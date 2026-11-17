#!/usr/bin/env python3
"""Retry of leg-4 reread for hot-leg run 2026-11-15-1009.
The 60-call batch failed on all 4 RPC endpoints (reads_ok 0/213); the main
job's 1001 run proved 3-contract chunks with curl timeout 150s work.
One bounded retry with the proven method; if this fails, the leg is skipped.
Overwrites run-2026-11-15-1009-reread.json with real values and updates
hot-leg-run-2026-11-15-1009.json reread + changes sections.
"""
import json, re, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-15-1009"
MAIN_REREAD_TAG = "2026-11-15-1001"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
NOW = time.strftime("%Y-%m-%dT%H:%M+07:00", time.gmtime(time.time() + 7 * 3600))
t0 = time.time()
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a, str) and a.startswith("0x") and len(a) == 42 else enc_u(int(a))
    return d
def post_rpc(ep, payload, timeout=150):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)

src = open(BASE + "run-" + MAIN_REREAD_TAG + "-reread.py").read()
m = re.search(r"ITEMS = \{.*?\n\}\n", src, re.S)
ns = {"USER": USER, "U": [USER]}
exec(m.group(0), ns)
ITEMS = ns["ITEMS"]

def read_chunk(chunk):
    calls, meta = [], []
    for name, (addr, views) in chunk:
        for key, sig, args in views:
            calls.append({"jsonrpc": "2.0", "id": len(calls) + 1, "method": "eth_call",
                          "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
            meta.append((name, key))
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=150)
            if not isinstance(res, list) or len(res) != len(calls):
                print("  chunk ep", ep, "bad shape", str(res)[:120], flush=True); continue
            out = {}
            for it, (name, key) in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    out.setdefault(name, {})[key] = None
                else:
                    r = it["result"]
                    out.setdefault(name, {})[key] = to_int(r[:66]) if len(r) >= 66 else r
            return out, ep
        except Exception as e:
            print("  chunk ep", ep, "exc", str(e)[:100], flush=True); continue
    return None, None

def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=150)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16)
        except Exception: continue
    return None

items = list(ITEMS.items())
reads, ok = {}, 0
total_calls = sum(len(v) for _, v in items)
chunks = [items[i:i + 3] for i in range(0, len(items), 3)]
for ci, ch in enumerate(chunks):
    r, ep = read_chunk(ch)
    names = [n for n, _ in ch]
    if r is None:
        print(f"chunk {ci+1}/{len(chunks)} FAIL {names}", flush=True)
        for n in names: reads[n] = {"address": ITEMS[n][0], "views": None}
        continue
    ok += sum(1 for n in names if r.get(n) is not None)
    for n in names: reads[n] = {"address": ITEMS[n][0], "views": r.get(n)}
    print(f"chunk {ci+1}/{len(chunks)} OK via {ep} ({time.time()-t0:.0f}s) {names}", flush=True)
    time.sleep(5)
blk = block_number()
reread = {"started_wib": NOW, "reads": reads, "reads_ok": ok,
          "reads_total": len(ITEMS), "block": blk, "elapsed_s": round(time.time() - t0, 1),
          "retry_of_failed_60call_batch": True}
json.dump(reread, open(BASE + "run-" + TAG + "-reread.json", "w"), indent=1)

prev_main = json.load(open(BASE + "run-" + MAIN_REREAD_TAG + "-reread.json"))
prev_reads = prev_main.get("reads", {})
changes = []
for name, cur in reads.items():
    pv = (prev_reads.get(name) or {}).get("views") or {}
    cv = (cur or {}).get("views") or {}
    for k, v in cv.items():
        if pv.get(k) != v:
            changes.append({"contract": name, "view": k, "prev": pv.get(k), "now": v})
run = json.load(open(BASE + "hot-leg-run-" + TAG + ".json"))
run["reread"] = {"reads_ok": ok, "reads_total": len(ITEMS), "block": blk,
                 "elapsed_s": reread["elapsed_s"], "method": "retry-3-contract-chunks"}
run["reread_changes_vs_" + MAIN_REREAD_TAG] = changes
run["reread_prev_block"] = prev_main.get("block")
run["reread_first_attempt_failed"] = {"reads_ok": 0, "reads_total": 213,
                                      "note": "60-call batches failed on all 4 RPC endpoints; retried with 3-contract chunks"}
run["elapsed_s"] = round(run.get("elapsed_s", 0) + (time.time() - t0), 1)
json.dump(run, open(BASE + "hot-leg-run-" + TAG + ".json", "w"), indent=1)
print("DONE reads_ok", ok, "/", len(ITEMS), "calls", total_calls, "block", blk,
      "changes", len(changes), "elapsed", round(time.time() - t0, 1))
print(json.dumps(changes, indent=1))
