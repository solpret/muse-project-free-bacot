#!/usr/bin/env python3
"""Run 132 targeted NULL-receipt retry (read-only): fetch ONLY the 2 NULL hashes
from run132-receipts.json via fast_rpc (batch, race fallback), then re-derive
run132-receipts.json + run132-paid.json on the SAME 46-candidate non-approve
basis as the main pass. DO NOT re-parse approvals (run 130/131 lesson: including
approve txs inflates the null count). No preview/mint/sign/login."""
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

parsed = json.load(open(SR / "run132-receipts.json"))
partial = json.load(open(SR / "run132-receipts-partial.json"))
nulls = [h for h, v in parsed.items() if v.get("status") == "receipt_null"]
print(f"nulls to retry: {len(nulls)}", flush=True)
recovered = {}
for h in nulls:
    r = None
    try:
        res = fast_rpc.batch([("eth_getTransactionReceipt", [h])])
        r = res[0] if isinstance(res, list) and res else None
    except Exception as e:
        print(f"  batch {h[:12]} ERROR {e}; race fallback", flush=True)
    if r is None:
        try:
            r = fast_rpc.race("eth_getTransactionReceipt", [h])
        except Exception as e:
            print(f"  race {h[:12]} ERROR {e}", flush=True)
    if r is None:
        print(f"  {h[:12]} STILL NULL", flush=True)
    else:
        recovered[h] = r
        print(f"  {h[:12]} recovered status={r.get('status')} logs={len(r.get('logs') or [])}", flush=True)
    time.sleep(2.0)

if not recovered:
    print("RETRY DONE: 0 recovered, nulls stay residual for run 133", flush=True)
    raise SystemExit(0)

# Merge into partial (raw receipts) and re-derive parsed + paid on the 46-candidate basis.
partial.update(recovered)
json.dump(partial, open(SR / "run132-receipts-partial.json", "w"))

sent = json.load(open(SR / "run132-sent.json"))
tier = json.load(open(HOME / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = {"0x" + "0" * 24 + w[2:] for w in uniq}
APPROVE = "0x095ea7b3"

cands, seen = [], set()
for w, r in sent["results"].items():
    if not r.get("ok"):
        continue
    for t in r["in_window"]:
        if t["hash"] in seen:
            continue
        seen.add(t["hash"])
        if t["input_prefix"] == APPROVE:
            continue
        cands.append((w, t))
assert len(cands) == len(parsed), f"basis mismatch: cands={len(cands)} parsed={len(parsed)}"

new_parsed, paid = {}, {}
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
json.dump(new_parsed, open(SR / "run132-receipts.json", "w"), indent=1)
paid_out = {k: sorted(v) for k, v in paid.items()}
json.dump(paid_out, open(SR / "run132-paid.json", "w"), indent=1)
n_mint = sum(1 for v in new_parsed.values() if v.get("mint_logs"))
n_null = sum(1 for v in new_parsed.values() if v.get("status") == "receipt_null")
n_s1 = sum(1 for v in new_parsed.values() if v.get("receipt_status") == "0x1")
n_s0 = sum(1 for v in new_parsed.values() if v.get("receipt_status") == "0x0")
print(f"RETRY-RE-DERIVED total={len(new_parsed)} with_mint_logs={n_mint} null={n_null} status1={n_s1} status0={n_s0} paid_tokens={len(paid_out)}", flush=True)
print(f"RETRY DONE recovered={len(recovered)}/{len(nulls)}", flush=True)
