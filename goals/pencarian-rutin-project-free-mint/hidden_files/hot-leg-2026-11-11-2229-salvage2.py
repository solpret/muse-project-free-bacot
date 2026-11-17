#!/usr/bin/env python3
"""Hot-leg 2026-11-11 22:29 WIB — salvage v2: prio re-read via SMALL batched
eth_call requests (5 calls/batch; 40-call batch hit -32005 rate limit).
Read-only; writes only own run json."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-11-2229"
T0 = time.time()

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
U = enc_addr("0xeb237F6f9FB4e826739F0954e9768914F28b2c2E")

src = open(BASE + "hot-leg-2026-11-11-2229-salvage.py").read()
ns = {}
exec(src.split("batch = []")[0], ns)
CALLS = ns["CALLS"]

EPS = ("https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.defibit.io/",
       "https://bsc.nodereal.io/")
CHUNK = 5
results = {}
notes = []
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
        except Exception as e:
            continue
    if not done:
        for key, _, _, _ in chunk:
            results[key] = {"error": "all-endpoints-failed"}
        notes.append(f"chunk@{ci} failed all endpoints")
    time.sleep(0.5)
    print(f"chunk {ci}-{ci+len(chunk)-1} done, elapsed {time.time()-T0:.1f}s", flush=True)

out = {"run": "free-mint-hot-leg 2026-11-11 22:29 WIB salvage-batch-v2",
       "n_calls": len(CALLS),
       "n_ok": sum(1 for v in results.values() if not isinstance(v, dict)),
       "n_error": sum(1 for v in results.values() if isinstance(v, dict)),
       "notes": notes,
       "results": results,
       "elapsed_s": round(time.time() - T0, 1)}
json.dump(out, open(BASE + f"hot-leg-run-{TAG}-salvage2.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
