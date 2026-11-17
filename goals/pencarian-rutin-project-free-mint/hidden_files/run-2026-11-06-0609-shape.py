#!/usr/bin/env python3
"""Run 2026-11-06 0609 WIB: shape-check the 6 Sourcify feed contracts new vs hot-leg-seen.
Reuses classify()/sourcify_abi() from feed_shape_0001.py. Read-only except hot-leg-seen.json
update for the checked addresses (same format as the hot leg)."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from feed_shape_0001 import sourcify_abi, classify

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0609"
NEW = ["0xd79f5E4A3A8Ad8576bbb389e6AD77Bf2c97A4302",
       "0xb24849ae2C80448FcdE247ad018072D0f2472DeF",
       "0xa0F5D8FEA57653598607Eac425980187EEafa313",
       "0xf82812c9B513D51d8866F9F0e73a7c4401A0b229",
       "0x5011Ed8BEDE185b2433629dF171B56A48124B6EA",
       "0x3eA9551da8ca70C4598a26FA28B1Dc48De4FAf35"]
feed = json.load(open(f"{BASE}/run-2026-11-06-0609-sourcify-feed.json"))
vat = {it["address"].lower(): it.get("verifiedAt") for it in feed["results"]}
hl = json.load(open(f"{BASE}/hot-leg-seen.json"))
out = []
for addr in NEW:
    status, abi = sourcify_abi(addr)
    r = {"address": addr, "verifiedAt": vat.get(addr.lower()), "sourcify": status}
    if abi is not None:
        r.update(classify(abi))
    else:
        r["S1"] = False; r["S2"] = False
    out.append(r)
    print(addr, status, "S1=", r.get("S1"), "S2=", r.get("S2"),
          "mint=", r.get("mint_fns"), "quote=", r.get("quote_fns"),
          "free=", r.get("free_views"), "agent=", r.get("gate_fns"), "token=", r.get("token_fns"), flush=True)
    hl[addr] = {"first_seen_wib": "2026-11-06T06:15:00+07:00",
                "note": f"S1={r.get('S1')} S2={r.get('S2')} mint={r.get('mint_fns')} quote={r.get('quote_fns')} free={r.get('free_views')} agent={r.get('gate_fns')} token={r.get('token_fns')} err=",
                "source": "sourcify-feed",
                "status": "checked-not-sale-shape" if not (r.get("S1") or r.get("S2")) else "SALE-SHAPE-PASS-NEEDS-VERIFY"}
json.dump(out, open(f"{BASE}/run-{TS}-sourcify-shape.json", "w"), indent=1)
json.dump(hl, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
print("hot-leg-seen total now:", len(hl))
