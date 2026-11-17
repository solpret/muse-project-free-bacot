#!/usr/bin/env python3
"""Read-only run 130 receipts retry: re-fetch the 13 NULL receipts from the
main pass (fast_rpc batch/race failed on all endpoints at the time). Up to 3
attempts per hash with pauses. Re-parses mint logs + paid map and rewrites
run130-receipts.json / run130-paid.json / run130-receipts-partial.json.
No preview/mint/sign/login."""
import json, sys, time
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import fast_rpc

HOME = Path.home()
SR = HOME / "workspace/narrative-pulse/scan-runs"
def topic(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()
T_TRANSFER = topic("Transfer(address,address,uint256)")
T_SINGLE = topic("TransferSingle(address,address,address,uint256,uint256)")
T_BATCH = topic("TransferBatch(address,address,address,uint256[],uint256[])")
ZERO_PAD = "0x" + "0" * 64

parsed = json.load(open(SR / "run130-receipts.json"))
partial = json.load(open(SR / "run130-receipts-partial.json"))
tier = json.load(open(HOME / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = {"0x" + "0" * 24 + w[2:] for w in uniq}

nulls = [h for h, v in parsed.items() if v.get("status") == "receipt_null"]
print(f"null receipts to retry: {len(nulls)}", flush=True)
recovered, still_null = [], []
for h in nulls:
    r = None
    for attempt in (1, 2, 3):
        try:
            r = fast_rpc.race("eth_getTransactionReceipt", [h])
            if r is not None:
                break
        except Exception as e:
            print(f"  {h[:12]} attempt={attempt} ERROR {str(e)[:120]}", flush=True)
        time.sleep(8)
    if r is None:
        still_null.append(h)
        print(f"  {h[:12]} STILL NULL after 3 attempts", flush=True)
    else:
        recovered.append(h)
        partial[h] = r
        print(f"  {h[:12]} RECOVERED status={r.get('status')}", flush=True)
    time.sleep(4)
print(f"RECEIPTS RETRY DONE recovered={len(recovered)} still_null={len(still_null)}", flush=True)

# Re-parse ALL receipts (same logic as run130-receipts.py) so paid map is complete.
sent = json.load(open(SR / "run130-sent.json"))
cands = []
for w, r in sent["results"].items():
    if not r.get("ok"):
        continue
    for t in r["in_window"]:
        cands.append((w, t))
paid, new_parsed = {}, {}
for w, t in cands:
    r = partial.get(t["hash"])
    if r is None:
        new_parsed[t["hash"]] = {"wallet": w, "to": t["to"], "selector": t["input_prefix"],
                                 "value": t["value"], "time_wib": t["time_wib"], "status": "receipt_null"}
        continue
    logs = r.get("logs") or []
    mint_logs = []
    for lg in logs:
        topics = lg.get("topics") or []
        if not topics:
            continue
        if topics[0] == T_TRANSFER and len(topics) >= 3 and topics[1] == ZERO_PAD and topics[2] in tracked_padded:
            mint_logs.append({"contract": lg.get("address"), "to_topic": topics[2], "data": lg.get("data")})
        elif topics[0] in (T_SINGLE, T_BATCH) and len(topics) >= 4 and topics[2] == ZERO_PAD and topics[3] in tracked_padded:
            mint_logs.append({"contract": lg.get("address"), "to_topic": topics[3], "data": lg.get("data"), "batch": True})
        elif topics[0] == T_TRANSFER and len(topics) >= 3 and topics[2] in tracked_padded:
            tok = (lg.get("address") or "").lower()
            paid.setdefault(tok, set()).add("0x" + topics[2][-40:])
    new_parsed[t["hash"]] = {"wallet": w, "to": t["to"], "selector": t["input_prefix"],
                             "value": t["value"], "time_wib": t["time_wib"],
                             "receipt_status": r.get("status"), "n_logs": len(logs), "mint_logs": mint_logs}
json.dump(new_parsed, open(SR / "run130-receipts.json", "w"), indent=1)
json.dump(partial, open(SR / "run130-receipts-partial.json", "w"))
paid_out = {k: sorted(v) for k, v in paid.items()}
json.dump(paid_out, open(SR / "run130-paid.json", "w"), indent=1)
n_mint = sum(1 for v in new_parsed.values() if v.get("mint_logs"))
n_null = sum(1 for v in new_parsed.values() if v.get("status") == "receipt_null")
n_s1 = sum(1 for v in new_parsed.values() if v.get("receipt_status") == "0x1")
print(f"AFTER RETRY total={len(new_parsed)} with_mint_logs={n_mint} null={n_null} status1={n_s1} paid_tokens={len(paid_out)}", flush=True)
for h, v in new_parsed.items():
    if v.get("mint_logs"):
        print(f"MINT {h} wallet={v['wallet'][:10]} to={v['to']} sel={v['selector']} val={v['value']} time={v['time_wib']} logs={v['mint_logs']}", flush=True)
mx = max((len(v) for v in paid_out.values()), default=0)
print(f"PAID max_wallets_per_token={mx}", flush=True)
