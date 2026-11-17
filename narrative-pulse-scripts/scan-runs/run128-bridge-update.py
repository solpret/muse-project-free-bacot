#!/usr/bin/env python3
"""Run 128 bridge update (read-only bookkeeping): write pointer-discovery result
for Dronefarm (last queued entry) into scan-bridge.json. Only this job writes the bridge.
No preview/mint/sign/login."""
import json
from pathlib import Path
from collections import Counter

BRIDGE = Path.home() / "workspace/goals/pencarian-rutin-project-free-mint/hidden_files/scan-bridge.json"
b = json.load(open(BRIDGE))
c = b.get("contracts", b)

updates = {
 "0x5063025fb6ab1859b91c312237a772ca21db44e6": {
   "website": None, "gate": "website_no_pointer_found",
   "note": "Run 128 pointer: contractURI base64 JSON decoded in full (name/description/seller_fee only, no external_url/website/URL); tokenURI #247 base64 JSON decoded in full (name/description/on-chain SVG image only, no URLs); Sourcify only generic docs/EIP URLs; ABI no site functions. Method: contractURI+tokenURI. Hint for routine job only, NOT a new lead by scan job (already reported as finding run 3)."},
}
for addr, u in updates.items():
    assert addr in c, f"missing bridge entry {addr}"
    assert c[addr].get("gate") is None, f"entry {addr} already has gate {c[addr].get('gate')}"
    c[addr].update(u)
    print(f"updated {addr[:10]} -> {u['gate']} website={u['website']}")

json.dump(b, open(BRIDGE, "w"), indent=1)
g = Counter(v.get("gate") for v in c.values())
print(f"bridge now: {len(c)} contracts, gates={dict(g)}")
print("bridge updated")
