#!/usr/bin/env python3
"""Read-only: created addresses of run-69 deployment txs (to==None in sent pass).
Batch via fast_rpc; saves run70-deployments.json {created_address: [tx_hash, status]}.
No preview/mint/sign/login."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import fast_rpc
HOME = Path.home()
sent = json.load(open(HOME / "workspace/narrative-pulse/scan-runs/run70-sent.json"))
dep = []
for w, r in sent["results"].items():
    if not r.get("ok"):
        continue
    for t in r["in_window"]:
        if t.get("to") is None:
            dep.append((w, t["hash"]))
print(f"deployment txs: {len(dep)}", flush=True)
out = {}
for j in range(0, len(dep), 6):
    chunk = dep[j:j+6]
    try:
        res = fast_rpc.batch([("eth_getTransactionReceipt", [h]) for _, h in chunk])
    except Exception as e:
        print(f"batch {j} ERROR {e}; race fallback", flush=True)
        res = []
        for _, h in chunk:
            try:
                res.append(fast_rpc.race("eth_getTransactionReceipt", [h]))
            except Exception as e2:
                res.append(None)
                print(f"  race {h[:12]} ERROR {e2}", flush=True)
    for (w, h), rc in zip(chunk, res):
        if rc is None:
            print(f"  NULL receipt {h} wallet {w[:10]}", flush=True)
            continue
        ca = (rc.get("contractAddress") or "").lower()
        out[ca] = [h, rc.get("status")]
    time.sleep(4.0)
json.dump(out, open(HOME / "workspace/narrative-pulse/scan-runs/run70-deployments.json", "w"), indent=1)
print("created addresses:", sorted(out.keys()))
