#!/usr/bin/env python3
"""Run 102 null-receipt recovery (read-only): 9 NULL receipts from run102-receipts.py,
all 0xad94ee77 PCS buys/sells. Re-fetch via fast_rpc race, merge into partial,
re-parse those 9 into run102-receipts.json and rebuild run102-paid.json."""
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

parsed = json.load(open(SR / "run102-receipts.json"))
partial = json.load(open(SR / "run102-receipts-partial.json"))
nulls = [h for h, v in parsed.items() if v.get("status") == "receipt_null"]
print(f"nulls to recover: {len(nulls)}", flush=True)
recovered = {}
for h in nulls:
    r = None
    for attempt in range(3):
        try:
            r = fast_rpc.race("eth_getTransactionReceipt", [h])
            if r is not None:
                break
        except Exception as e:
            print(f"  {h[:12]} attempt {attempt+1} ERROR {e}", flush=True)
        time.sleep(5)
    if r is None:
        print(f"  {h[:12]} STILL NULL after 3 attempts", flush=True)
        continue
    recovered[h] = r
    partial[h] = r
    print(f"  {h[:12]} recovered status={r.get('status')} block={int(r.get('blockNumber'),16) if r.get('blockNumber') else None} logs={len(r.get('logs') or [])}", flush=True)
json.dump(partial, open(SR / "run102-receipts-partial.json", "w"))
json.dump(recovered, open(SR / "run102-null-receipts.json", "w"), indent=1)

# rebuild tracked set + paid map from ALL raw receipts (same logic as run102-receipts.py)
tier = json.load(open(HOME / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = {"0x" + "0" * 24 + w[2:] for w in uniq}
paid = {}
for h, v in parsed.items():
    if v.get("status") == "receipt_null" and h not in recovered:
        continue
    r = partial.get(h)
    if not r:
        continue
    for lg in r.get("logs") or []:
        topics = lg.get("topics") or []
        if not topics:
            continue
        if topics[0] == T_TRANSFER and len(topics) >= 3 and topics[1] == ZERO_PAD and topics[2] in tracked_padded:
            continue  # mint, not paid
        elif topics[0] in (T_SINGLE, T_BATCH) and len(topics) >= 4 and topics[2] == ZERO_PAD and topics[3] in tracked_padded:
            continue
        elif topics[0] == T_TRANSFER and len(topics) >= 3 and topics[2] in tracked_padded:
            tok = (lg.get("address") or "").lower()
            paid.setdefault(tok, set()).add("0x" + topics[2][-40:])
# re-parse recovered entries
for h, r in recovered.items():
    v = parsed[h]
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
    parsed[h] = {"wallet": v["wallet"], "to": v["to"], "selector": v["selector"],
                 "value": v["value"], "time_wib": v["time_wib"],
                 "receipt_status": r.get("status"), "n_logs": len(logs), "mint_logs": mint_logs}
    if mint_logs:
        print(f"MINT in recovered {h} logs={mint_logs}", flush=True)
json.dump(parsed, open(SR / "run102-receipts.json", "w"), indent=1)
paid_out = {k: sorted(v) for k, v in paid.items()}
json.dump(paid_out, open(SR / "run102-paid.json", "w"), indent=1)
n_mint = sum(1 for v in parsed.values() if v.get("mint_logs"))
n_null = sum(1 for v in parsed.values() if v.get("status") == "receipt_null")
print(f"NULL RECOVERY DONE recovered={len(recovered)}/{len(nulls)} remaining_null={n_null} total_mint_pattern={n_mint} paid_tokens={len(paid_out)}", flush=True)
