#!/usr/bin/env python3
"""Fix-up for run130 receipts-retry re-parse bug: the retry script re-parsed
ALL 211 in-window txs (including 69 approve txs that were never fetched),
inflating nulls 13 -> 81. Re-derive the parsed/paid files on the correct
142 non-approve candidate basis, using the current partial file (which holds
the 1 recovered receipt). No new network calls."""
import json, sys
from pathlib import Path
from Crypto.Hash import keccak

HOME = Path.home()
SR = HOME / "workspace/narrative-pulse/scan-runs"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def topic(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()
APPROVE = sel("approve(address,uint256)")
T_TRANSFER = topic("Transfer(address,address,uint256)")
T_SINGLE = topic("TransferSingle(address,address,address,uint256,uint256)")
T_BATCH = topic("TransferBatch(address,address,address,uint256[],uint256[])")
ZERO_PAD = "0x" + "0" * 64

sent = json.load(open(SR / "run130-sent.json"))
partial = json.load(open(SR / "run130-receipts-partial.json"))
tier = json.load(open(HOME / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = {"0x" + "0" * 24 + w[2:] for w in uniq}

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
print(f"candidates={len(cands)} (non-approve, deduped)", flush=True)
parsed, paid = {}, {}
for w, t in cands:
    r = partial.get(t["hash"])
    if r is None:
        parsed[t["hash"]] = {"wallet": w, "to": t["to"], "selector": t["input_prefix"],
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
    parsed[t["hash"]] = {"wallet": w, "to": t["to"], "selector": t["input_prefix"],
                         "value": t["value"], "time_wib": t["time_wib"],
                         "receipt_status": r.get("status"), "n_logs": len(logs), "mint_logs": mint_logs}
json.dump(parsed, open(SR / "run130-receipts.json", "w"), indent=1)
paid_out = {k: sorted(v) for k, v in paid.items()}
json.dump(paid_out, open(SR / "run130-paid.json", "w"), indent=1)
n_mint = sum(1 for v in parsed.values() if v.get("mint_logs"))
n_null = sum(1 for v in parsed.values() if v.get("status") == "receipt_null")
n_s1 = sum(1 for v in parsed.values() if v.get("receipt_status") == "0x1")
print(f"FIXED total={len(parsed)} with_mint_logs={n_mint} null={n_null} status1={n_s1} paid_tokens={len(paid_out)}", flush=True)
for h, v in parsed.items():
    if v.get("mint_logs"):
        print(f"MINT {h} {v}", flush=True)
    if v.get("status") == "receipt_null":
        print(f"NULL {h} wallet={v['wallet'][:10]} sel={v['selector']} time={v['time_wib']}", flush=True)
mx = max((len(v) for v in paid_out.values()), default=0)
print(f"PAID max_wallets_per_token={mx}", flush=True)
