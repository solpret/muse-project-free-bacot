#!/usr/bin/env python3
"""Hot-leg 2026-11-11 22:59 WIB — LEG-4-ONLY salvage2.
Parent run killed by service restart after feed fetch; salvage run hit the
280s timeout after legs 1+2 (Sourcify ABI endpoint stalled: all 18 new +
3 retry shape-checks failed, recorded in seen; Boltbook EN 0B + ZH 0B).
This script runs ONLY leg 4 (47-call prio re-read, 5-call batches) + bridge
read-only, then writes the combined run JSON + prints it.
Legs 1+2 facts are reconstructed from saved state (see out dict)."""
import json, subprocess, time
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-11-2259"
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

# ---- CALLS: parsed literally from the 2259 script (same prio list as 2244) ----
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
U = enc_addr(USER)

src = open(BASE + "hot-leg-2026-11-11-2259.py").read()
start = src.index("CALLS = [")
end = src.index("]", src.index('"RIGFORGE.freeClaimed"')) + 1
CALLS = eval(src[start + len("CALLS = "):end])
assert len(CALLS) == 47, len(CALLS)

feed = json.load(open(BASE + f"hot-leg-{TAG}-feed.json"))
meta = feed["meta"]
out = {"run": "free-mint-hot-leg 2026-11-11 22:59 WIB (salvage: legs1+2 done, leg4 here)",
       "started_wib": now_wib,
       "leg1_feed": {"returned": len(feed["addrs"]),
                     "verified_range": (min(meta.values()), max(meta.values())) if meta else None,
                     "ok": True, "source": "saved-feed-salvage"},
       "leg1_new": 18,
       "leg1_shape": "all-18-new shape-check-failed (ABI unfetchable: Sourcify ABI endpoint timeout, re-verified manually 23:12 WIB HTTP 000); 3 retries also failed; recorded in hot-leg-seen.json, retry next run",
       "leg1_s1_pass": [], "leg1_s2_pass": [],
       "leg1_retry": ["0xffb755653b9638beeb23d8a451b9ddcf003b7777",
                      "0x0EafFB8F2A3aAFBB7Fb60e5Fa902286E09Ca0f01",
                      "0x83aC0c3E0cdFBcdEAA58278FAc504B1fbF2Ff08F"],
       "seen_count": 11940,
       "legs12_elapsed_s": "salvage run hit 280s timeout after legs 1+2 (Sourcify stall)",
       "leg2_boltbook": {"en_bytes": 0, "zh_bytes": 0,
                         "note": "EN 0B (4th consecutive failure); ZH 0B this run (was 42907B in 2244); 0 addrs, 0 new"},
       "seen_count_after_bb": 11940}

EPS = ("https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.defibit.io/",
       "https://bsc.nodereal.io/")
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
            r = subprocess.run(["curl", "-s", "-m", "20", "-H", "Content-Type: application/json",
                                "-d", json.dumps(batch), ep],
                               capture_output=True, timeout=25)
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
    time.sleep(0.4)

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
