#!/usr/bin/env python3
"""Retry for hot-leg run 2026-11-14 22:49 WIB: re-read leg was degraded
(27/147 reads OK) because ABI fetches failed in a burst and suffixed view
labels (commitEnd_1, priceFor_user, ...) were not mapped to functions.
Sequential ABI fetch with retries + label-suffix parsing, then batch eth_call
for the still-null views only. Merges into run-2026-11-14-2249-reread.json and
hot-leg-run-2026-11-14-2249.json. Read-only on-chain; no preview/mint/sign.
"""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-14-2249"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
t0 = time.time()
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]

def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "free-mint-hot-leg/2249-retry"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def post_rpc(ep, payload, timeout=120):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(r)

def to_int(v):
    try:
        return int(v, 16) if v and v != "0x" else None
    except Exception:
        return None

def parse_label(label):
    """'commitEnd_1' -> ('commitEnd', [1]); 'priceFor_user' -> ('priceFor', [USER]);
    'snippetsOf_1_user' -> ('snippetsOf', [1, USER]); plain -> (label, [])."""
    parts = label.split("_")
    if len(parts) == 1:
        return label, []
    args = []
    for tok in parts[1:]:
        if tok == "user":
            args.append(USER)
        elif tok.isdigit():
            args.append(int(tok))
        else:
            return label, []
    return parts[0], args

reread = json.load(open(BASE + "run-" + TAG + "-reread.json"))
reads = reread["reads"]
prev = json.load(open(BASE + "run-2026-11-14-2244-reread.json"))
prev_reads = prev.get("reads", {})

# contracts with at least one null view
todo = []
for name, d in reads.items():
    nulls = [k for k, v in (d.get("views") or {}).items() if v is None]
    if nulls:
        todo.append((name, d["address"], nulls))
print(f"retry items: {len(todo)}", flush=True)

calls, meta = [], []
abi_fail = []
for name, addr, labels in todo:
    abi = None
    for attempt in range(3):
        try:
            m = json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
                               timeout=25).decode())
            abi = {e["name"]: e for e in m.get("abi", []) if e.get("type") == "function"}
            break
        except Exception as e:
            if attempt == 2:
                abi_fail.append((name, str(e)[:80]))
            time.sleep(1.5)
    time.sleep(0.3)
    if not abi:
        print(f"  {name}: ABI fetch failed", flush=True)
        continue
    for label in labels:
        fn_name, pargs = parse_label(label)
        fn = abi.get(fn_name)
        if not fn:
            print(f"  {name}: fn {fn_name} not in ABI (label {label})", flush=True)
            continue
        inputs = fn.get("inputs", [])
        if len(inputs) != len(pargs):
            print(f"  {name}: {fn_name} arity {len(inputs)} != parsed {len(pargs)}", flush=True)
            continue
        sig = fn_name + "(" + ",".join(i.get("type", "") for i in inputs) + ")"
        data = sel(sig)
        ok = True
        for (inp, arg) in zip(inputs, pargs):
            t = inp.get("type", "")
            if t == "address" and isinstance(arg, str):
                data += arg[2:].lower().rjust(64, "0")
            elif (t.startswith("uint") or t.startswith("int")) and isinstance(arg, int):
                data += format(arg, "064x")
            else:
                ok = False
        if not ok:
            print(f"  {name}: {fn_name} arg-type mismatch", flush=True)
            continue
        calls.append({"jsonrpc": "2.0", "id": len(calls) + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        meta.append((name, label))

print(f"retry calls built: {len(calls)}", flush=True)
ok_n = 0
CH = 60
for ci in range(0, len(calls), CH):
    chunk = calls[ci:ci + CH]
    chunk_meta = meta[ci:ci + CH]
    got = None
    for ep in EPS:
        try:
            res = post_rpc(ep, chunk, timeout=120)
            if isinstance(res, list) and len(res) == len(chunk):
                got = res
                break
        except Exception:
            continue
    if got is None:
        print(f"retry chunk {ci//CH + 1} FAIL", flush=True)
        continue
    for it, (name, label) in zip(got, chunk_meta):
        if isinstance(it, dict) and "error" not in it and it.get("result") not in (None, "0x"):
            r = it["result"]
            reads[name]["views"][label] = to_int(r[:66]) if len(r) >= 66 else r
            ok_n += 1
        else:
            reads[name]["views"][label] = None
    print(f"retry chunk {ci//CH + 1} ok ({time.time()-t0:.0f}s)", flush=True)
    time.sleep(1)

blk = reread.get("block")
for ep in EPS:
    try:
        r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=60)
        if isinstance(r, dict) and r.get("result"):
            blk = int(r["result"], 16)
            break
    except Exception:
        continue

still_null = sum(1 for d in reads.values() for v in (d.get("views") or {}).values() if v is None)
tot = sum(len(d.get("views") or {}) for d in reads.values())
reread["reads"] = reads
reread["block"] = blk
reread["retry_ok"] = ok_n
reread["retry_abi_fail"] = abi_fail
reread["elapsed_s"] = round(reread.get("elapsed_s", 0) + (time.time() - t0), 1)
json.dump(reread, open(BASE + "run-" + TAG + "-reread.json", "w"), indent=1)

changes = []
for name, cur in reads.items():
    pv = (prev_reads.get(name) or {}).get("views") or {}
    cv = cur.get("views") or {}
    for k, v in cv.items():
        if pv.get(k) != v:
            changes.append({"contract": name, "view": k, "prev": pv.get(k), "now": v})

out = json.load(open(BASE + "hot-leg-run-" + TAG + ".json"))
out["reread"]["reads_ok"] = tot - still_null
out["reread"]["reads_total"] = tot
out["reread"]["block"] = blk
out["reread_changes_vs_2244"] = changes
out["reread_retry"] = {"calls_ok": ok_n, "still_null": still_null,
                       "abi_fail": abi_fail, "elapsed_s": round(time.time() - t0, 1)}
out["elapsed_s"] = round(out.get("elapsed_s", 0) + (time.time() - t0), 1)
json.dump(out, open(BASE + "hot-leg-run-" + TAG + ".json", "w"), indent=1)
print(json.dumps({"retry_ok": ok_n, "still_null": still_null, "total_views": tot,
                  "block": blk, "changes": changes, "abi_fail": abi_fail}, indent=1))
