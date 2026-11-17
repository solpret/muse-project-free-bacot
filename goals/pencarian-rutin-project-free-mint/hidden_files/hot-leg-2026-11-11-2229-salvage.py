#!/usr/bin/env python3
"""Hot-leg 2026-11-11 22:29 WIB — salvage: prio re-read via ONE batched
eth_call JSON-RPC request (legs34 hit its 200s budget before leg 4).
Read-only; writes only own run json."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-11-2229"
T0 = time.time()
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
U = enc_addr(USER)

CALLS = [
 ("Stampooor.freeMinted", "0x467696af8c2206B977B24081445104632dc1D459", "freeMinted()", ""),
 ("Stampooor.freeAvailable", "0x467696af8c2206B977B24081445104632dc1D459", "freeAvailable(address)", U),
 ("Stampooor.balanceOf", "0x467696af8c2206B977B24081445104632dc1D459", "balanceOf(address)", U),
 ("AgentPals.freeMinted", "0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", "freeMinted()", ""),
 ("MECHA.totalMinted", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", "totalMinted()", ""),
 ("MECHA.freeClaimed", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", "freeClaimed()", ""),
 ("MECHA.freeAvailable", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", "freeAvailable(address)", U),
 ("MECHA.balanceOf", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", "balanceOf(address)", U),
 ("BUCKET.totalSupply", "0x2b0d3b384C341020aed1d49907b5708C423bA6DA", "totalSupply()", ""),
 ("BUCKET.totalFreeCount", "0x2b0d3b384C341020aed1d49907b5708C423bA6DA", "totalFreeCount()", ""),
 ("BUCKET.freeAvailable", "0x2b0d3b384C341020aed1d49907b5708C423bA6DA", "freeAvailable(address)", U),
 ("BUCKET.balanceOf", "0x2b0d3b384C341020aed1d49907b5708C423bA6DA", "balanceOf(address)", U),
 ("MOONDRILL.totalSupply", "0x87b354E2014D2e418927A1105dD219A2e7b063b0", "totalSupply()", ""),
 ("MOONDRILL.firstFreeUsed", "0x87b354E2014D2e418927A1105dD219A2e7b063b0", "firstFreeUsed()", ""),
 ("MOONDRILL.freeMinted", "0x87b354E2014D2e418927A1105dD219A2e7b063b0", "freeMinted()", ""),
 ("MOONDRILL.balanceOf", "0x87b354E2014D2e418927A1105dD219A2e7b063b0", "balanceOf(address)", U),
 ("0x2e50.totalSupply", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3", "totalSupply()", ""),
 ("0x2e50.firstFreeUsed", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3", "firstFreeUsed()", ""),
 ("0x2e50.freeMinted", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3", "freeMinted()", ""),
 ("0x2e50.balanceOf", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3", "balanceOf(address)", U),
 ("CRTSAINTS.totalSupply", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F", "totalSupply()", ""),
 ("CRTSAINTS.firstFreeUsed", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F", "firstFreeUsed()", ""),
 ("CRTSAINTS.freeMinted", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F", "freeMinted()", ""),
 ("CRTSAINTS.balanceOf", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F", "balanceOf(address)", U),
 ("WFPASS.mintOpen", "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C", "mintOpen()", ""),
 ("WFPASS.freeMinted", "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C", "freeMinted()", ""),
 ("WFPASS.totalMinted", "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C", "totalMinted()", ""),
 ("ORIGAMIX.totalSupply", "0x43CAb600E87B0F96e7a310049774797FC3DF5756", "totalSupply()", ""),
 ("ORIGAMIX.firstFreeUsed", "0x43CAb600E87B0F96e7a310049774797FC3DF5756", "firstFreeUsed()", ""),
 ("ORIGAMIX.freeMinted", "0x43CAb600E87B0F96e7a310049774797FC3DF5756", "freeMinted()", ""),
 ("ORIGAMIX.balanceOf", "0x43CAb600E87B0F96e7a310049774797FC3DF5756", "balanceOf(address)", U),
 ("AGCR.freeMinted", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc", "freeMinted()", ""),
 ("AGCR.FREE_SUPPLY", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc", "FREE_SUPPLY()", ""),
 ("AGCR.balanceOf", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc", "balanceOf(address)", U),
 ("BINANCEAI.launched", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", "launched()", ""),
 ("BINANCEAI.claimable", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", "claimable(address)", U),
 ("S1-0x6C50.mintStart", "0x6C504A7B392b1D57845F57d2abb5C4d49211Aa7f", "mintStart()", ""),
 ("S1-0x6C50.totalMinted", "0x6C504A7B392b1D57845F57d2abb5C4d49211Aa7f", "totalMinted()", ""),
 ("S1-0x6C50.freeMinted", "0x6C504A7B392b1D57845F57d2abb5C4d49211Aa7f", "freeMinted()", ""),
 ("S1-0x6C50.freeAvailable", "0x6C504A7B392b1D57845F57d2abb5C4d49211Aa7f", "freeAvailable(address)", U),
]

batch = []
for i, (key, addr, sig, args) in enumerate(CALLS):
    batch.append({"jsonrpc": "2.0", "id": i, "method": "eth_call",
                  "params": [{"to": addr, "data": sel(sig) + args}, "latest"]})

def parse(raw):
    out = {}
    try:
        arr = json.loads(raw.decode(errors="replace"))
    except Exception:
        return None
    if not isinstance(arr, list):
        return None
    for item in arr:
        i = item.get("id")
        if i is None or i >= len(CALLS):
            continue
        key = CALLS[i][0]
        if "error" in item:
            out[key] = {"error": item["error"].get("message", str(item["error"]))[:80]}
            continue
        res = item.get("result")
        if res in (None, "0x"):
            out[key] = {"error": "empty-return"}
        elif len(res) >= 66:
            v = res[2:66]
            try:
                out[key] = int(v, 16)
            except Exception:
                out[key] = res
        else:
            out[key] = res
    return out

result = None
used_ep = None
for ep in ("https://bsc-dataseed.binance.org/", "https://bsc.nodereal.io/",
           "https://bsc-dataseed1.defibit.io/"):
    try:
        r = subprocess.run(["curl", "-s", "-m", "25", "-H", "Content-Type: application/json",
                            "-d", json.dumps(batch), ep],
                           capture_output=True, timeout=30)
        parsed = parse(r.stdout)
        if parsed and len(parsed) >= len(CALLS) // 2:
            result, used_ep = parsed, ep
            break
        elif parsed:
            result, used_ep = parsed, ep + " (partial)"
            break
    except Exception:
        continue

out = {"run": "free-mint-hot-leg 2026-11-11 22:29 WIB salvage-batch",
       "endpoint": used_ep, "n_calls": len(CALLS),
       "n_ok": sum(1 for v in (result or {}).values() if not isinstance(v, dict)),
       "results": result or {"error": "batch-failed-all-endpoints"},
       "elapsed_s": round(time.time() - T0, 1)}
json.dump(out, open(BASE + f"hot-leg-run-{TAG}-salvage.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
