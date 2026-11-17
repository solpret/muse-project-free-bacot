#!/usr/bin/env python3
"""Run 127 bridge update (read-only bookkeeping): write pointer-discovery results
for the 5 backfill targets into scan-bridge.json. Only this job writes the bridge.
No preview/mint/sign/login."""
import json
from pathlib import Path

BRIDGE = Path.home() / "workspace/goals/pencarian-rutin-project-free-mint/hidden_files/scan-bridge.json"
b = json.load(open(BRIDGE))
c = b.get("contracts", b)

updates = {
 "0x508468bad31de925a533b88b17a233ec377c641d": {
   "website": None, "gate": "website_no_pointer_found",
   "note": "Run 127 pointer: contractURI + tokenURI #1328 base64 JSON decoded in full (name/description/on-chain SVG image only, no external_url/website/URL anywhere); Sourcify only generic docs/GitHub URLs; ABI no site functions. Method: contractURI+tokenURI."},
 "0x7ba27f90c7b509af1dfbda2a788fe4488ff3aab4": {
   "website": None, "gate": "website_no_pointer_found",
   "note": "Run 127 pointer: contractURI + tokenURI #1295 base64 JSON decoded in full (name/description/on-chain SVG image only, no external_url/website/URL anywhere); Sourcify only generic docs/GitHub URLs; ABI no site functions. Method: contractURI+tokenURI."},
 "0xf6ab7131b01f0a94e8860c284fc904d09ed0373b": {
   "website": None, "gate": "website_no_pointer_found",
   "note": "Run 127 pointer: contractURI + tokenURI #1678 base64 JSON decoded in full (name/description/on-chain SVG image only, no external_url/website/URL anywhere); Sourcify only generic docs/GitHub URLs; ABI no site functions. Method: contractURI+tokenURI."},
 "0xbf3488e453c68e9771c26d448e99d0ec5395135f": {
   "website": None, "gate": "website_no_pointer_found",
   "note": "Run 127 pointer: tokenURI #7812 base64 JSON decoded (name/description/on-chain SVG only, no external_url/website/URL); Sourcify only generic docs/GitHub URLs; ABI no site functions; contractURI read FAILED first pass AND retry (3 tries, fast_rpc race outage) - pointer incomplete, not proven absent. Method: tokenURI (+contractURI failed)."},
 "0x9da90fe302a987d979c21d7c3ae421cb0b2cf8b0": {
   "website": "https://orb.apeagent.online/", "gate": "website_verified_via_pointer",
   "note": "Run 127 pointer: tokenURI #2063 -> orb.apeagent.online metadata JSON with external_url https://orb.apeagent.online/; site root fetched HTTP 200, prints exact contract. contractURI read failed first pass + retry (race outage) - does not change verified outcome. Method: tokenURI. Hint for routine job only, NOT a new lead by scan job (already reported as finding run 3; already in Free Bacot snapshot as bridge-0x9da90fe3)."},
}
for addr, u in updates.items():
    assert addr in c, f"missing bridge entry {addr}"
    assert c[addr].get("gate") is None, f"entry {addr} already has gate {c[addr].get('gate')}"
    c[addr].update(u)
    print(f"updated {addr[:10]} -> {u['gate']} website={u['website']}")

json.dump(b, open(BRIDGE, "w"), indent=1)
from collections import Counter
g = Counter(v.get("gate") for v in c.values())
print(f"bridge now: {len(c)} contracts, gates={dict(g)}")
print("bridge updated")
