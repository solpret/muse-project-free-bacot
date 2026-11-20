#!/usr/bin/env python3
"""Retry pass for free-mint-search run 2026-11-18 16:31 WIB.
Re-reads ONLY the calls whose first-pass value was None (transport
failure, curl rc=28), using fast_rpc.batch_race (raced across healthy
endpoints) in 5-call chunks, 8 workers. Contract-revert 'err:' values
from pass 1 are kept as-is. Writes run-2026-11-18-1631-reread-retry.json
(merged reads) + a retry summary into run-2026-11-18-1631.json.
Read-only."""
import ast, json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from eth_hash.auto import keccak
import fast_rpc

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def encode(sig, arg):
    data = "0x" + sel(sig)
    if arg == "user":
        data += enc_addr(USER)
    elif arg == "one":
        data += "%064x" % 1
    elif arg == "user1":
        data += enc_addr(USER) + "%064x" % 1
    return data

src = open(f"{HF}/run-2026-11-18-1631.py").read()
tree = ast.parse(src)
plan = bsccat_addr = bsccat_views = pepe_addr = pepe_views = None
for node in tree.body:
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name):
                if t.id == "PLAN":
                    plan = ast.literal_eval(node.value)
                elif t.id == "BSCCAT_ADDR":
                    bsccat_addr = ast.literal_eval(node.value)
                elif t.id == "BSCCAT_VIEWS":
                    bsccat_views = ast.literal_eval(node.value)
                elif t.id == "PEPE_MINT":
                    pepe_addr = ast.literal_eval(node.value)
                elif t.id == "PEPE_VIEWS":
                    pepe_views = ast.literal_eval(node.value)
assert plan and bsccat_addr and pepe_addr

calls, meta = [], []
for name, addr, views in plan:
    for label, sig, arg in views:
        calls.append((addr, encode(sig, arg)))
        meta.append((name, addr, label))
for label, sig, arg in bsccat_views:
    calls.append((bsccat_addr, encode(sig, arg)))
    meta.append(("bsccat", bsccat_addr, label))
for label, sig, arg in pepe_views:
    calls.append((pepe_addr, encode(sig, arg)))
    meta.append(("pepe", pepe_addr, label))

rr = json.load(open(f"{HF}/run-2026-11-18-1631-reread.json"))
def old_val(name, label):
    if name == "bsccat":
        return rr["bsccat"]["views"].get(label)
    if name == "pepe":
        return rr["pepe"].get(label)
    return rr["reads"].get(name, {}).get("views", {}).get(label)

todo = [(i, c, m) for i, (c, m) in enumerate(zip(calls, meta)) if old_val(m[0], m[2]) is None]
print(f"retry: {len(todo)} None-valued calls of {len(calls)}", flush=True)

def one_chunk(chunk):
    idxs, cc = [t[0] for t in chunk], [t[1] for t in chunk]
    try:
        res = fast_rpc.batch_race(cc, timeout=10)
        vals = []
        for r in res:
            try:
                vals.append(int(r, 16))
            except Exception:
                vals.append(r)
        return idxs, vals, None
    except Exception:
        # per-call race fallback (handles a reverting view inside chunk)
        vals = []
        for to, data in cc:
            try:
                r = fast_rpc.race("eth_call", [{"to": to, "data": data}, "latest"], timeout=10)
                vals.append(int(r, 16))
            except Exception as e:
                vals.append(None)
        return idxs, vals, "fallback-per-call"

import concurrent.futures as cf
chunks = [todo[i:i + 5] for i in range(0, len(todo), 5)]
recovered = 0
results = {}
errors = []
with cf.ThreadPoolExecutor(max_workers=8) as ex:
    for idxs, vals, err in ex.map(one_chunk, chunks):
        for j, v in zip(idxs, vals):
            results[j] = v
            if v is not None:
                recovered += 1
        if err:
            errors.append(err)
        print(f"chunk done, recovered so far {recovered}/{len(todo)}", flush=True)

# merge into reread copy
for j, v in results.items():
    name, addr, label = meta[j]
    if v is None:
        continue
    if name == "bsccat":
        rr["bsccat"]["views"][label] = v
    elif name == "pepe":
        rr["pepe"][label] = v
    else:
        rr["reads"].setdefault(name, {"address": addr, "views": {}})["views"][label] = v
rr["retry"] = {"recovered": recovered, "of": len(todo),
               "elapsed_s": round(time.time() - T0, 1)}
json.dump(rr, open(f"{HF}/run-2026-11-18-1631-reread-retry.json", "w"), indent=1)
out = json.load(open(f"{HF}/run-2026-11-18-1631.json"))
out["retry"] = rr["retry"]
json.dump(out, open(f"{HF}/run-2026-11-18-1631.json", "w"), indent=1)
print(f"RETRY DONE recovered={recovered}/{len(todo)} elapsed={round(time.time()-T0,1)}s", flush=True)
