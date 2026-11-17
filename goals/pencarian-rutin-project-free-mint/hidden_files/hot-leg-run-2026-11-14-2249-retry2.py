#!/usr/bin/env python3
"""Recovery 2 for hot-leg run 2026-11-14 22:49 WIB: full re-read of the focus
set using the 2244 label set (incl. suffixed labels like commitEnd_1,
priceFor_user) with sequential ABI fetch + small (20-call) RPC chunks.
Overwrites run-2026-11-14-2249-reread.json views and recomputes the diff vs
2244. Read-only on-chain; no preview/mint/sign.
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
    req = urllib.request.Request(url, headers={"User-Agent": "free-mint-hot-leg/2249-rec2"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def post_rpc(ep, payload, timeout=90):
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

prev = json.load(open(BASE + "run-2026-11-14-2244-reread.json"))
prev_reads = prev.get("reads", {})
items = [(n, d["address"], list((d.get("views") or {}).keys()))
         for n, d in prev_reads.items() if d.get("address")]
print(f"items: {len(items)}, target views: {sum(len(l) for _,_,l in items)}", flush=True)

calls, meta = [], []
skipped = []
for name, addr, labels in items:
    abi = None
    for attempt in range(3):
        try:
            m = json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
                               timeout=25).decode())
            abi = {e["name"]: e for e in m.get("abi", []) if e.get("type") == "function"}
            break
        except Exception as e:
            if attempt == 2:
                skipped.append((name, "abi:" + str(e)[:60]))
            time.sleep(1.5)
    time.sleep(0.25)
    if not abi:
        print(f"  {name}: ABI fetch FAILED", flush=True)
        continue
    for label in labels:
        fn_name, pargs = parse_label(label)
        fn = abi.get(fn_name)
        if not fn:
            skipped.append((name, f"nofn:{label}"))
            continue
        inputs = fn.get("inputs", [])
        if len(inputs) != len(pargs):
            skipped.append((name, f"arity:{label}"))
            continue
        sig = fn_name + "(" + ",".join(i.get("type", "") for i in inputs) + ")"
        data = sel(sig)
        ok = True
        for inp, arg in zip(inputs, pargs):
            t = inp.get("type", "")
            if t == "address" and isinstance(arg, str):
                data += arg[2:].lower().rjust(64, "0")
            elif (t.startswith("uint") or t.startswith("int")) and isinstance(arg, int):
                data += format(arg, "064x")
            else:
                ok = False
        if not ok:
            skipped.append((name, f"argtype:{label}"))
            continue
        calls.append({"jsonrpc": "2.0", "id": len(calls) + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        meta.append((name, label))
print(f"calls built: {len(calls)}, skipped: {len(skipped)}", flush=True)
for s in skipped:
    print("  skip:", s, flush=True)

reads = {}
ok_n = 0
CH = 20
for ci in range(0, len(calls), CH):
    chunk = calls[ci:ci + CH]
    cm = meta[ci:ci + CH]
    got = None
    used = None
    for ep in EPS:
        try:
            res = post_rpc(ep, chunk, timeout=90)
            if isinstance(res, list) and len(res) == len(chunk):
                got, used = res, ep
                break
        except Exception as e:
            print(f"  chunk {ci//CH+1} ep {ep} exc {str(e)[:60]}", flush=True)
            continue
    if got is None:
        print(f"chunk {ci//CH+1} FAIL all endpoints", flush=True)
        for name, label in cm:
            reads.setdefault(name, {})[label] = None
        continue
    n_ok = 0
    for it, (name, label) in zip(got, cm):
        if isinstance(it, dict) and "error" not in it and it.get("result") not in (None, "0x"):
            r = it["result"]
            reads.setdefault(name, {})[label] = to_int(r[:66]) if len(r) >= 66 else r
            ok_n += 1
            n_ok += 1
        else:
            reads.setdefault(name, {})[label] = None
    print(f"chunk {ci//CH+1} ok via {used} ({time.time()-t0:.0f}s) {n_ok}/{len(chunk)}", flush=True)
    time.sleep(1)

blk = None
for ep in EPS:
    try:
        r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=60)
        if isinstance(r, dict) and r.get("result"):
            blk = int(r["result"], 16)
            break
    except Exception:
        continue

full = {}
for name, addr, labels in items:
    full[name] = {"address": addr, "views": reads.get(name, {})}
tot = sum(len(d["views"]) for d in full.values())
null_n = sum(1 for d in full.values() for v in d["views"].values() if v is None)
reread = {"started_wib": time.strftime("%Y-%m-%dT%H:%M+07:00", time.gmtime(time.time()+7*3600)),
          "reads": full, "reads_ok": tot - null_n, "reads_total": tot,
          "block": blk, "elapsed_s": round(time.time() - t0, 1),
          "recovery": 2, "skipped": skipped}
json.dump(reread, open(BASE + "run-" + TAG + "-reread.json", "w"), indent=1)

changes = []
for name, cur in full.items():
    pv = (prev_reads.get(name) or {}).get("views") or {}
    cv = cur.get("views") or {}
    for k, v in cv.items():
        if pv.get(k) != v:
            changes.append({"contract": name, "view": k, "prev": pv.get(k), "now": v})
real = [c for c in changes if c["now"] is not None]

out = json.load(open(BASE + "hot-leg-run-" + TAG + ".json"))
out["reread"] = {"reads_ok": tot - null_n, "reads_total": tot, "block": blk,
                 "elapsed_s": reread["elapsed_s"]}
out["reread_changes_vs_2244"] = changes
out["reread_recovery2"] = {"calls_ok": ok_n, "still_null": null_n, "skipped": skipped,
                           "elapsed_s": round(time.time() - t0, 1)}
out["elapsed_s"] = round(out.get("elapsed_s", 0) + (time.time() - t0), 1)
json.dump(out, open(BASE + "hot-leg-run-" + TAG + ".json", "w"), indent=1)
print(json.dumps({"calls_ok": ok_n, "total_views": tot, "still_null": null_n,
                  "block": blk, "changes_total": len(changes), "real_changes": real}, indent=1))
