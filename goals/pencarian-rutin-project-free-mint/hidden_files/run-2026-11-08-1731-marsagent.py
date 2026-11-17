#!/usr/bin/env python3
"""One-off read-only check MarsAgent 0x2231FdAe405c33dc4993f8C577c453802FF1AcE9
(hot-leg 17:19 reported mintOpen 1->0; NOT in snapshot — record status for parent merge).
Read-only; writes run-2026-11-08-1731-marsagent.json only."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return '0x' + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, '0')
USER = '0xeb237F6f9FB4e826739F0954e9768914F28b2c2E'
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
ADDR = '0x2231FdAe405c33dc4993f8C577c453802FF1AcE9'
def single(data):
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": ADDR, "data": data}, "latest"]},
                           timeout=8, retries=0)
            if not isinstance(out, dict): continue
            if out.get("error"): return None
            r = out.get("result")
            if r is None or r == "0x": return None
            return int(r, 16)
        except Exception:
            continue
    return None
out = {"address": ADDR, "name": "MarsAgent", "note": "hot-leg 17:19 reported mintOpen 1->0 (MINT DITUTUP, not sold out); gate-failed track-C lead 2026-11-07; user does not hold; NOT in snapshot — for parent merge only"}
for v in ['mintOpen()', 'totalSupply()', 'totalMinted()', 'freeClaimed()', 'freeMinted()',
          'FREE_SUPPLY()', 'FREE_SHARES()', 'MAX_SUPPLY()', 'balanceOf(address)',
          'freeClaimed(address)']:
    data = sel(v) + enc(USER) if '(address)' in v else sel(v)
    out[v.split('(')[0] + ('_user' if '(address)' in v else '')] = single(data)
    print(v, '=', out[v.split('(')[0] + ('_user' if '(address)' in v else '')], flush=True)
json.dump(out, open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-08-1731-marsagent.json', 'w'), indent=1)
print("WROTE marsagent")
