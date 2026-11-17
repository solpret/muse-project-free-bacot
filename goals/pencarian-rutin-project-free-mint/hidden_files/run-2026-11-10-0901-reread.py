#!/usr/bin/env python3
"""Re-read run 2026-11-10 09:01 WIB — curl transport (25s/call) because
fast_rpc caps at RACE_TIMEOUT 8s and dataseed latency is ~10-25s since
~03:03 WIB (run 0431: total re-read failure via fast_rpc).
Read-only; never writes snapshot/state/watermark. Writes run-2026-11-10-0901-reread.json.
"""
import json, sys, time, os, subprocess
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-0901"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            outd = {}
            for item, key in zip(res, keys):
                outd[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return outd
        except Exception:
            continue
    return None

LEAN = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
        "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
        "freeClaimed(address)"]
TC_VIEWS = ["totalSupply()", "freeMinted()", "freeSharesRemaining()",
            "balanceOf(address)", "freeClaimed(address)"]

out_path = f"{BASE}/run-{TS}-reread.json"
out = {"block": None, "reread": {}, "track_c": {}, "started_wib": "2026-11-10 09:01 WIB"}

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

out["block"] = get_block()
print("BLOCK", out["block"], flush=True)

# RESUME (same-TS): if a partial 1001 run file exists (batch split or killed
# run), keep its successful reads and retry only transport-level batch
# failures. Batches: run with MAX_CONTRACTS=N to cap the contracts phase,
# or SKIP_CONTRACTS=1 to run only the track_c phase.
MAX_CONTRACTS = int(os.environ.get("MAX_CONTRACTS", "0") or 0)
SKIP_CONTRACTS = os.environ.get("SKIP_CONTRACTS", "") == "1"
if os.path.exists(out_path):
    try:
        prev = json.load(open(out_path))
        if isinstance(prev, dict) and str(prev.get("started_wib", "")).startswith("2026-11-10 09:01"):
            kept_r, kept_t = prev.get("reread", {}), prev.get("track_c", {})
            for k in [k for k, v in list(kept_r.items()) if not isinstance(v, dict)]:
                del kept_r[k]
            # NOTE 0001 resume: keep all-None reread entries — they are complete
            # reads (views legitimately revert on those contracts), not failures.
            # Only _batch_fail entries are dropped and retried.
            dropped = [k for k, v in kept_r.items() if isinstance(v, dict) and v.get("_batch_fail")]
            for k in dropped: del kept_r[k]
            dropped_t = [k for k, v in kept_t.items() if isinstance(v, dict) and v.get("_batch_fail")]
            for k in dropped_t: del kept_t[k]
            out["reread"], out["track_c"] = kept_r, kept_t
            if not out["block"]:
                out["block"] = prev.get("block")
            print(f"RESUMED partial: reread={len(out['reread'])} track_c={len(out['track_c'])} dropped_batch_fail={len(dropped)+len(dropped_t)} block={out['block']}", flush=True)
    except Exception as e:
        print("RESUME FAILED", e, flush=True)

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
contracts = snap.get("contracts", {})
track_c = snap.get("track_c", {})

def save():
    tmp = out_path + ".tmp"
    with open(tmp, "w") as f: json.dump(out, f, indent=1)
    os.replace(tmp, out_path)

LOW = ("sold-out", "age-excluded", "minted-by-user", "excluded", "promotion-discarded",
       "same-owner-discarded", "paid-only")
def prio(name):
    st = str(contracts[name].get("status") or "")
    return 1 if any(x in st for x in LOW) else 0

todo = [(k, v.get("address")) for k, v in contracts.items()
        if v.get("address") and k not in out["reread"]]
todo.sort(key=lambda it: prio(it[0]))
if MAX_CONTRACTS > 0:
    todo = todo[:MAX_CONTRACTS]
print(f"TODO contracts: {len(todo)} (have {len(out['reread'])}) MAX_CONTRACTS={MAX_CONTRACTS} SKIP={SKIP_CONTRACTS}", flush=True)

def read_lean(item):
    name, addr = item
    t = time.time()
    got = raw_batch(addr, LEAN)
    d = {"address": addr}
    if got is None:
        for k in ["totalSupply", "totalMinted", "freeClaimed", "freeMinted",
                  "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "balanceOf_user",
                  "freeClaimed_user"]:
            d[k] = None
        d["_batch_fail"] = True
    else:
        d.update(got)
    print(f"LEAN {name} totalSupply={d.get('totalSupply')} freeClaimed={d.get('freeClaimed')} bal={d.get('balanceOf_user')} ({time.time()-t:.1f}s)", flush=True)
    return name, d

done = [0]
if not SKIP_CONTRACTS:
    with ThreadPoolExecutor(max_workers=8) as ex:
        for name, d in ex.map(read_lean, todo):
            out["reread"][name] = d
            done[0] += 1
            if done[0] % 20 == 0:
                save()
    save()
    print(f"CONTRACTS DONE total={len(out['reread'])} in {time.time()-T0:.1f}s", flush=True)
else:
    print(f"CONTRACTS SKIPPED (SKIP_CONTRACTS=1) total={len(out['reread'])}", flush=True)

def read_tc(item):
    name, addr = item
    t = time.time()
    got = raw_batch(addr, TC_VIEWS)
    d = {"address": addr}
    if got is None:
        for k in ["totalSupply", "freeMinted", "freeSharesRemaining",
                  "balanceOf_user", "freeClaimed_user"]:
            d[k] = None
        d["_batch_fail"] = True
    else:
        d.update(got)
    print(f"TC {name} totalSupply={d.get('totalSupply')} freeMinted={d.get('freeMinted')} ({time.time()-t:.1f}s)", flush=True)
    return name, d

tc_items = []
for k, v in track_c.items():
    if k in out["track_c"]: continue
    if not isinstance(v, dict): continue
    a = v.get("address") or v.get("sale") or v.get("token")
    if a and isinstance(a, str) and a.startswith("0x"):
        tc_items.append((k, a))
print(f"TODO track_c: {len(tc_items)} (have {len(out['track_c'])}) SKIP_TRACKC={os.environ.get('SKIP_TRACKC','')}", flush=True)
if os.environ.get("SKIP_TRACKC", "") == "1":
    print("TRACK_C SKIPPED (SKIP_TRACKC=1)", flush=True)
else:
    with ThreadPoolExecutor(max_workers=8) as ex:
        for name, d in ex.map(read_tc, tc_items):
            out["track_c"][name] = d
            done[0] += 1
            if done[0] % 20 == 0:
                save()
    save()
print(f"REREAD DONE in {time.time()-T0:.1f}s reread={len(out['reread'])} track_c={len(out['track_c'])}", flush=True)
