#!/usr/bin/env python3
"""RECOVERY (one-off, run 78): rebuild run77-paid.json from
run77-receipts-partial.json (raw receipts) using the EXACT derivation logic of
run77-receipts.py, after run78-receipts.py (sed bug: 'run77-paid.json' not
renamed) overwrote run77-paid.json with run-78 data. Also writes the run-78
paid map (currently sitting in run77-paid.json) to run78-paid.json.
Read-only w.r.t. chain; only restores local run files."""
import json
from pathlib import Path
from Crypto.Hash import keccak

HOME = Path.home()
def topic(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()
T_TRANSFER = topic("Transfer(address,address,uint256)")
T_SINGLE = topic("TransferSingle(address,address,address,uint256,uint256)")
T_BATCH = topic("TransferBatch(address,address,address,uint256[],uint256[])")
ZERO_PAD = "0x" + "0" * 64

tier = json.load(open(HOME / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = {"0x" + "0" * 24 + w[2:] for w in uniq}
print(f"tracked wallets={len(uniq)}")

def derive(partial_path):
    receipts = json.load(open(partial_path))
    paid = {}
    for h, r in receipts.items():
        if r is None:
            continue
        for lg in (r.get("logs") or []):
            topics = lg.get("topics") or []
            if not topics:
                continue
            if topics[0] == T_TRANSFER and len(topics) >= 3 and topics[1] == ZERO_PAD and topics[2] in tracked_padded:
                continue
            elif topics[0] in (T_SINGLE, T_BATCH) and len(topics) >= 4 and topics[2] == ZERO_PAD and topics[3] in tracked_padded:
                continue
            elif topics[0] == T_TRANSFER and len(topics) >= 3 and topics[2] in tracked_padded:
                tok = (lg.get("address") or "").lower()
                paid.setdefault(tok, set()).add("0x" + topics[2][-40:])
    return {k: sorted(v) for k, v in paid.items()}

# 1) run-78 map currently in run77-paid.json -> save as run78-paid.json
run78_paid = json.load(open(HOME / "workspace/narrative-pulse/scan-runs/run77-paid.json"))
json.dump(run78_paid, open(HOME / "workspace/narrative-pulse/scan-runs/run78-paid.json", "w"), indent=1)
print(f"run78-paid.json written: {len(run78_paid)} tokens, max {max(len(v) for v in run78_paid.values())} wallets")

# 2) rebuild run-77 map from raw receipts
run77_paid = derive(HOME / "workspace/narrative-pulse/scan-runs/run77-receipts-partial.json")
from collections import Counter
dist = Counter(len(v) for v in run77_paid.values())
print(f"rebuilt run77: {len(run77_paid)} tokens, distribution {dict(sorted(dist.items()))}")
for t in ["0x302941695afa1d83d648851b0898e39c63db7777","0x5eb157a3872c019f36989830a26e93ade0d97777","0x1a573d9c3baf15072773b2077d08176335a07777"]:
    print(f"  {t[:10]}: {len(run77_paid.get(t, []))} wallets")
s3029 = set(run77_paid.get("0x302941695afa1d83d648851b0898e39c63db7777", []))
s5eb1 = set(run77_paid.get("0x5eb157a3872c019f36989830a26e93ade0d97777", []))
s1a57 = set(run77_paid.get("0x1a573d9c3baf15072773b2077d08176335a07777", []))
print(f"  pairwise diffs: 3029-5eb1={len(s3029 ^ s5eb1)} 3029-1a57={len(s3029 ^ s1a57)} 5eb1-1a57={len(s5eb1 ^ s1a57)}")
# cross-check vs run77-token-verify MACHINE27 set
tv = json.load(open(HOME / "workspace/narrative-pulse/scan-runs/run77-token-verify.json"))
m27 = set(tv.get("machine27_window_totals", {}).get("machine27_set", [])) if "machine27_set" in tv.get("machine27_window_totals", {}) else None
print(f"  token-verify machine27_set stored: {m27 is not None}")
if m27:
    print(f"  diff rebuilt-3029 vs token-verify set: {len(s3029 ^ m27)}")
json.dump(run77_paid, open(HOME / "workspace/narrative-pulse/scan-runs/run77-paid.json", "w"), indent=1)
print("run77-paid.json RESTORED from raw receipts")
