#!/usr/bin/env python3
"""Hot-leg 2026-11-11 23:19 WIB — LEG-4-ONLY salvage.
Parent run killed after ~400s overrun: leg 1 Sourcify feed returned 0 addrs
(feed fetch failed), leg 2 Boltbook EN 0B + ZH 0B (both failed, EN 4th
consecutive failure), leg 4 stalled on slow RPC (~5-6s/call, 3-endpoint
retries). This salvage runs ONLY leg 4 prio re-read with tighter bounds:
2 endpoints, curl -m 12, chunk 5. Sold-out items (AgentPals 300/300,
NAOMI 777/777, S1-0x6C50 100/100) are NOT re-read this run — sold out
cannot reverse; noted, not treated as change.
Writes hot-leg-run-2026-11-11-2319.json + prints it."""
import json, subprocess, time
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-11-2319"
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
U = enc_addr(USER)

CALLS = [
 ("Stampooor.freeMinted", "0x467696af8c2206B977B24081445104632dc1D459", "freeMinted()", ""),
 ("Stampooor.freeAvailable", "0x467696af8c2206B977B24081445104632dc1D459", "freeAvailable(address)", U),
 ("Stampooor.balanceOf", "0x467696af8c2206B977B24081445104632dc1D459", "balanceOf(address)", U),
 ("AGCR.freeMinted", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc", "freeMinted()", ""),
 ("AGCR.FREE_SUPPLY", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc", "FREE_SUPPLY()", ""),
 ("AGCR.balanceOf", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc", "balanceOf(address)", U),
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
 ("BINANCEAI.launched", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", "launched()", ""),
 ("BINANCEAI.claimable", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", "claimable(address)", U),
 ("RIGFORGE.freeSharesLeft", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", "freeSharesLeft()", ""),
 ("RIGFORGE.openedAt", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", "openedAt()", ""),
 ("RIGFORGE.freeClaimed", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", "freeClaimed()", ""),
]

out = {"run": "free-mint-hot-leg 2026-11-11 23:19 WIB (salvage leg4-only)",
       "started_wib": now_wib,
       "leg1_feed": {"returned": 0, "ok": False,
                     "note": "Sourcify feed fetch failed this run (0 addrs); no new contracts seen; retry next run"},
       "leg1_new": [], "leg1_shape": {}, "leg1_s1_pass": [], "leg1_s2_pass": [],
       "leg1_retry": "skipped (parent killed; 0xffb75565/0x0EafFB8F/0x83aC0c3E retry next run)",
       "leg2_boltbook": {"en_bytes": 0, "zh_bytes": 0,
                         "note": "EN 0B (4th consecutive failure); ZH 0B this run (was 42907B in 2244); 0 addrs, 0 new; retry next run"},
       "skipped_reread_soldout": ["AgentPals 300/300", "NAOMI 777/777", "S1-0x6C50 100/100"]}

EPS = ("https://bsc-dataseed.binance.org/", "https://bsc.nodereal.io/")
block = None
for ep in EPS:
    try:
        r = subprocess.run(["curl", "-s", "-m", "10", "-H", "Content-Type: application/json",
                            "-d", json.dumps({"jsonrpc": "2.0", "id": 0, "method": "eth_blockNumber", "params": []}), ep],
                           capture_output=True, timeout=15)
        j = json.loads(r.stdout.decode(errors="replace"))
        if j.get("result"):
            block = int(j["result"], 16)
            out["block"] = block
            out["block_endpoint"] = ep
            break
    except Exception:
        continue

results = {}
notes = []
CHUNK = 5
for ci in range(0, len(CALLS), CHUNK):
    chunk = CALLS[ci:ci + CHUNK]
    batch = [{"jsonrpc": "2.0", "id": i, "method": "eth_call",
              "params": [{"to": addr, "data": sel(sig) + args}, "latest"]}
             for i, (key, addr, sig, args) in enumerate(chunk)]
    done = False
    for ep in EPS:
        try:
            r = subprocess.run(["curl", "-s", "-m", "12", "-H", "Content-Type: application/json",
                                "-d", json.dumps(batch), ep],
                               capture_output=True, timeout=15)
            arr = json.loads(r.stdout.decode(errors="replace"))
            if isinstance(arr, list) and arr and all("result" in it or "error" in it for it in arr):
                for item in arr:
                    i = item.get("id")
                    if i is None or i >= len(chunk):
                        continue
                    key = chunk[i][0]
                    if "error" in item:
                        results[key] = {"error": str(item["error"])[:80]}
                    else:
                        res = item.get("result")
                        if res in (None, "0x"):
                            results[key] = {"error": "empty-return"}
                        elif len(res) >= 66:
                            try:
                                results[key] = int(res[2:66], 16)
                            except Exception:
                                results[key] = res
                        else:
                            results[key] = res
                done = True
                break
        except Exception:
            continue
    if not done:
        for key, _, _, _ in chunk:
            results[key] = {"error": "all-endpoints-failed"}
        notes.append(f"chunk@{ci} failed all endpoints")
    time.sleep(0.3)

out["leg4_reread"] = {"n_calls": len(CALLS),
                      "n_ok": sum(1 for v in results.values() if not isinstance(v, dict)),
                      "n_error": sum(1 for v in results.values() if isinstance(v, dict)),
                      "notes": notes, "results": results}

try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    contracts = bridge.get("contracts", {})
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for sec in ("contracts", "track_c"):
        for v in snap.get(sec, {}).values():
            if isinstance(v, dict) and v.get("address"):
                snap_addrs.add(v["address"].lower())
    not_in = [a for a in contracts if a.lower() not in snap_addrs]
    disc = [a for a, v in contracts.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
    out["bridge"] = {"total": len(contracts), "not_in_snapshot": len(not_in),
                     "same_owner_discarded": len(disc), "not_in_list": not_in}
except Exception as e:
    out["bridge"] = {"error": str(e)[:120]}

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-run-{TAG}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
