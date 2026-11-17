#!/usr/bin/env python3
"""Age-rule candidates run 2026-11-07 0531 WIB (on-chain leg, read-only).
Method mirrors run 0201: first-seen block in onchain-scan-seen.json (or the
snapshot's firstSeenBlock) as an age LOWER bound (first mint <= first seen,
so >48h is guaranteed for these). Block rate 0.45 s/block measured live in
earlier runs; 48h = 384,000 blocks. Threshold = live head - 384000.
Live-status snapshot entries only (status startswith early-lead / strong-lead /
candidate, plus watchlist-launched flagged separately); sold-out and
minted-by-user excluded. This leg deletes nothing; parent decides.
Writes run-2026-11-07-0531-age-candidates.json only.
"""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
head = int(race("eth_blockNumber", []), 16)
TH = head - 384000
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
seen_c = seen.get("contracts", {})
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))

def live_status(s):
    if not s:
        return False
    return (s.startswith("early-lead") or s.startswith("strong-lead")
            or s.startswith("candidate"))

cands = []
for name, v in snap.get("contracts", {}).items():
    st = v.get("status") or ""
    if not live_status(st):
        continue
    addr = (v.get("address") or "").lower()
    fs = v.get("firstSeenBlock") or seen_c.get(addr) or seen_c.get(v.get("address", ""))
    if isinstance(fs, int) and fs < TH:
        cands.append({"name": name, "address": v.get("address"),
                      "first_seen_block": fs, "status": st})
cands.sort(key=lambda r: r["first_seen_block"])
out = {"run": "2026-11-07-0531", "live_head": head, "threshold_block": TH,
       "method": "first-seen block as age lower bound; 48h = 384000 blocks at 0.45 s/block; live-status (early/strong-lead/candidate) snapshot entries only; sold-out and minted-by-user excluded; parent deletes at finalization, this leg deletes nothing",
       "count": len(cands), "candidates": cands}
json.dump(out, open(f"{BASE}/run-2026-11-07-0531-age-candidates.json", "w"), indent=1)
print(f"AGE head={head} threshold={TH} candidates={len(cands)}")
for c in cands:
    print(" ", c["name"], c["address"], "first_seen", c["first_seen_block"], c["status"])
# Reference: watchlist-launched ONLYAI first-seen (not counted as candidate)
onlyai = snap["contracts"].get("ONLYAI-Crystals", {})
print("ONLYAI watchlist-launched firstSeenBlock:", onlyai.get("firstSeenBlock"),
      "seen-file:", seen_c.get("0x156482ad3f0eebd8e3f70d494ebd1da3f738f5ba"))
