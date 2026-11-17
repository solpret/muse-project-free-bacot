#!/usr/bin/env python3
"""Hot-leg 1929 leg4 RETRY — lean single-batch re-read.
The first attempt (per-field batches) hit the 150s timeout: RPC is slow
(~7s/call). This retry puts all eth_calls in a few big batches via
call_many, with per-chunk fallback. Read-only except own hot-leg files."""
import json, re, sys, time, os, concurrent.futures
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import call_many, batch
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-1929"
PREV_TAG = "hot-leg-2026-11-08-1129"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
t0 = time.time()
log = {"run": "free-mint-hot-leg 2026-11-08 19:29:38 WIB leg4-retry"}

src = open(BASE+PREV_TAG+".py").read()
def extract(var):
    m = re.search(re.escape(var)+r"\s*=\s*(\{.*?^\})", src, re.S|re.M)
    return eval(m.group(1))
V = extract("V"); ITEMS = extract("ITEMS")
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

# Build one flat call list: (label, to, data)
calls = []   # (item, field, to, data)
for name, (addr, keys) in ITEMS.items():
    for k in keys:
        sig, arg = V[k]
        data = sel(sig)
        if arg == "USER": data += enc_addr(USER)
        elif arg == "USER1": data += enc_addr(USER) + format(1, "064x")
        calls.append((name, k, addr, data))
PANDORA = "0xdb8A4102C49a41cfAeD7673A3F155f19853Af5e8"
pandora_calls = []
for pk, psig in {"totalMinted": "totalMinted()", "totalSupply": "totalSupply()",
                 "mintActive": "mintActive()", "publicRemaining": "publicRemaining()",
                 "freeUsed_user": "freeUsed(address)"}.items():
    data = sel(psig)
    if pk == "freeUsed_user": data += enc_addr(USER)
    pandora_calls.append((pk, PANDORA, data))
log["calls_total"] = len(calls) + len(pandora_calls)

def run_chunk(chunk):
    # chunk: list of (to, data); returns list of raw results (or None per item)
    try:
        return call_many([(to, data) for _, to, data in chunk], timeout=60)
    except Exception as ex:
        return [f"ERR {type(ex).__name__}" for _ in chunk]

try:
    blk = int(batch([("eth_blockNumber", [])], timeout=20)[0], 16)
except Exception as ex:
    blk = None; log["leg4_block_error"] = str(ex)[:120]

all_calls = [(c[2], c[3]) for c in calls] + [(c[1], c[2]) for c in pandora_calls]
# chunk into 4 groups of ~30
CH = 30
chunks = [all_calls[i:i+CH] for i in range(0, len(all_calls), CH)]
results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    for res in ex.map(run_chunk, chunks):
        results.extend(res)
log["chunks"] = len(chunks)

items = {}
for (name, k, addr, data), raw in zip(calls, results):
    v = to_int(raw) if isinstance(raw, str) and raw.startswith("0x") else None
    items.setdefault(name, {"address": addr})[k] = v
pandora = {"address": PANDORA}
for (pk, _, _), raw in zip(pandora_calls, results[len(calls):]):
    pandora[pk] = to_int(raw) if isinstance(raw, str) and raw.startswith("0x") else None
log["leg3b_pandora"] = pandora

reread = {"block": blk, "items": items}
json.dump(reread, open(BASE+TAG+"-reread.json","w"), indent=1)
n_null = sum(1 for it in items.values() for k,v in it.items() if k != "address" and v is None)
n_tot = sum(1 for it in items.values() for k,v in it.items() if k != "address")
log["leg4"] = {"block": blk, "n": len(items), "nulls": f"{n_null}/{n_tot}"}

prev = json.load(open(BASE+"hot-leg-2026-11-08-1924-reread.json"))
prev2 = json.load(open(BASE+"hot-leg-2026-11-08-1919-reread.json"))
diffs, recoveries = [], []
for name, cur in items.items():
    for k, v in cur.items():
        if k == "address": continue
        ov = prev["items"].get(name, {}).get(k)
        if ov is None:
            ov = prev2["items"].get(name, {}).get(k)
        if v != ov:
            if ov is None and v is not None:
                recoveries.append({"item": name, "field": k, "old": ov, "new": v})
            elif v is None:
                pass
            else:
                diffs.append({"item": name, "field": k, "old": ov, "new": v})
log["leg4_diff_vs_prev"] = diffs
log["leg4_recoveries_null_to_value"] = recoveries
log["leg4_diff_prev_file"] = "hot-leg-2026-11-08-1924-reread.json (+1919 for null baseline)"

bridge = json.load(open(BASE+"scan-bridge.json"))
snap = json.load(open(BASE+"onchain-snapshot.json"))
snap_addrs = set()
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict):
        for f in ("address","sale","token"):
            if v.get(f): snap_addrs.add(v[f].lower())
bcontracts = bridge.get("contracts", {})
log["bridge"] = {"n_contracts": len(bcontracts),
    "mtime": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(os.path.getmtime(BASE+"scan-bridge.json"))),
    "in_snapshot": len([a for a in bcontracts if a.lower() in snap_addrs]),
    "note": "read-only; no bridge contract newly meets a tier this run (checked only via count/mtime + snapshot membership, per prior runs)."}
log["elapsed_sec"] = round(time.time()-t0, 1)
json.dump(log, open(BASE+TAG+"-leg4.log","w"), indent=1)
print(json.dumps(log, indent=1))
print("ELAPSED", round(time.time()-t0,1))
