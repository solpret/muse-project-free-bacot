#!/usr/bin/env python3
"""Fresh re-read NBC + DRACO — run 1831, 2026-11-07 ~18:47 WIB. Read-only.
Single-call batches with endpoint fallback (fast_rpc.batch reverts whole batch
if one call reverts). No preview, no mint."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
NBC = "0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf"
DRACO = "0x2e1927798462397a88e3c1015Dc8168e798DF6D3"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def call(addr, sig, arg=None):
    data = sel(sig) + (enc(arg) if arg else "")
    for ep in EPS:
        try:
            r = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=10)
            return to_int(r[0])
        except Exception:
            continue
    return None
t0 = time.time()
out = {"read_wib": "2026-11-07 ~18:47 WIB", "run": 1831}
# head
for ep in EPS:
    try:
        r = batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)
        out["head"] = int(r[0], 16)
        break
    except Exception:
        continue
nbc = {}
for v in ["freeTotal()", "freeUsed()", "mintedTotal()", "paidUsed()", "opensAt()", "closesAt()"]:
    nbc[v] = call(NBC, v)
nbc["freeTakenBy_user"] = call(NBC, "freeTakenBy(address)", USER)
nbc["balanceOf_user"] = call(NBC, "balanceOf(address)", USER)
out["nbc"] = nbc
print("NBC", json.dumps(nbc), flush=True)
draco = {}
for v in ["totalMints()", "totalSupply()", "mintOpen()"]:
    draco[v] = call(DRACO, v)
draco["isFreeMintAvailable_user"] = call(DRACO, "isFreeMintAvailable(address)", USER)
draco["currentPriceFor_user"] = call(DRACO, "currentPriceFor(address)", USER)
draco["mintsOf_user"] = call(DRACO, "mintsOf(address)", USER)
draco["balanceOf_user"] = call(DRACO, "balanceOf(address)", USER)
out["draco"] = draco
print("DRACO", json.dumps(draco), flush=True)
out["elapsed_s"] = round(time.time() - t0, 2)
json.dump(out, open(f"{BASE}/run-2026-11-07-1831-fresh-nbc-draco.json", "w"), indent=1)
print(f"FRESH NBC/DRACO DONE in {out['elapsed_s']}s head={out.get('head')}", flush=True)
