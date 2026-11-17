#!/usr/bin/env python3
"""Run 2026-11-06 0609 WIB: shape-check the 6 Sourcify feed contracts new vs hot-leg-seen.
Reuses classify()/sourcify_abi() from feed_shape_0001.py. Read-only except hot-leg-seen.json
update for the checked addresses (same format as the hot leg)."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from feed_shape_0001 import sourcify_abi, classify

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0631"
NEW = ["0x2bE9Ac09dD0C1d05398C3BA77996D04046bE2f28",
       "0xE8Ec42bDce6898c962A60971F428029265335aa4",
       "0x9ab27027172F9bc438872d01dEF7eD934ea6786a",
       "0x2A984f0062E81F258F6d2D5f84D1715a57195294",
       "0x3FB5A51F90609CF37A97c9bB508594214A9026ea",
       "0x734bFBce7E9c3AD98249E710dcD8fE9CFdCA326D",
       "0x2FD93F9EbA69Ee7C46a18c469F816B0E4c22e12c"]
feed = json.load(open(f"{BASE}/run-2026-11-06-0631-sourcify-feed.json"))
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
    hl[addr] = {"first_seen_wib": "2026-11-06T06:35:00+07:00",
                "note": f"S1={r.get('S1')} S2={r.get('S2')} mint={r.get('mint_fns')} quote={r.get('quote_fns')} free={r.get('free_views')} agent={r.get('gate_fns')} token={r.get('token_fns')} err=",
                "source": "sourcify-feed",
                "status": "checked-not-sale-shape" if not (r.get("S1") or r.get("S2")) else "SALE-SHAPE-PASS-NEEDS-VERIFY"}
json.dump(out, open(f"{BASE}/run-{TS}-sourcify-shape.json", "w"), indent=1)
json.dump(hl, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
print("hot-leg-seen total now:", len(hl))
