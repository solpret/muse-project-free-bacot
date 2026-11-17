#!/usr/bin/env python3
"""hot-leg run 2026-11-15 ~05:34 WIB — leg (4) re-read only, chunked (0529-style).
Reuses ITEMS focus set from hot-leg-2026-11-15-0529-run.py (AST-extracted),
3 contracts per batch via curl with per-endpoint retry, 2s sleep between chunks.
Adds SPOT-MOG (gate-blocked track-C lead) + SPOT-PIXELFROGS (gate-blocked).
Compares vs 0529 reread (block 133624269); None reads are failures, never changes.
Read-only on-chain; writes only run-2026-11-15-0534-reread.json."""
import ast, json, subprocess, sys, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-15-0534"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
t0 = time.time()

src = open(BASE + "hot-leg-2026-11-15-0529-run.py").read()
tree = ast.parse(src)
class _FixNames(ast.NodeTransformer):
    def visit_Name(self, node):
        if node.id == "U":
            return ast.copy_location(ast.List(elts=[ast.Constant(value=USER)], ctx=ast.Load()), node)
        if node.id == "USER":
            return ast.copy_location(ast.Constant(value=USER), node)
        return node
tree = _FixNames().visit(tree)
ast.fix_missing_locations(tree)
ITEMS = None
for node in tree.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ITEMS":
        ITEMS = ast.literal_eval(node.value)
        break
assert ITEMS, "ITEMS not found"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a, str) and a.startswith("0x") and len(a) == 42 else enc_u(int(a))
    return d
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
def post_rpc(ep, payload, timeout=150):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(r)
def chunked(items, n=3):
    items = list(items.items())
    for i in range(0, len(items), n):
        yield items[i:i+n]
def read_chunk(chunk):
    calls, meta = [], []
    for name, (addr, views) in chunk:
        for key, sig, args in views:
            calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                          "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
            meta.append((name, key))
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=150)
            if not isinstance(res, list) or len(res) != len(calls):
                print("  chunk ep", ep, "bad shape", type(res), str(res)[:120], flush=True); continue
            o = {}
            for it, (name, key) in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    o.setdefault(name, {})[key] = None
                else:
                    rr = it["result"]
                    o.setdefault(name, {})[key] = to_int(rr[:66]) if len(rr) >= 66 else rr
            return o, ep
        except Exception as e:
            print("  chunk ep", ep, "exc", str(e)[:100], flush=True); continue
    return None, None
def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=30)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16)
        except Exception: continue
    return None

EXTRA = {
 "SPOT-MOG": ("0x238D982aC300b75AFb5f21E759DB1d575Bb5c0DE", [
    ("freeMinted", "freeMinted()", []), ("FREE_SLOTS", "FREE_SLOTS()", []),
    ("freeUsedByWallet_user", "freeUsedByWallet(address)", [USER]),
    ("FREE_AMOUNT", "FREE_AMOUNT()", []), ("startedAt", "startedAt()", [])]),
 "SPOT-PIXELFROGS": ("0x454054e55FA2D7Ba37df7F3ceA269696f19037dF", [
    ("totalSupply", "totalSupply()", []), ("freeMinted", "freeMinted()", []),
    ("freeLeft", "freeLeft()", []), ("mintStart", "mintStart()", [])]),
}
ALL = dict(ITEMS)
ALL.update(EXTRA)

reads, ok = {}, 0
for ci, ch in enumerate(chunked(ALL, 3)):
    r, ep = read_chunk(ch)
    names = [n for n, _ in ch]
    if r is None:
        print(f"chunk {ci+1} FAIL {names}", flush=True)
        for n in names: reads[n] = {"address": ALL[n][0], "views": None}
        continue
    ok += sum(1 for n in names if r.get(n) is not None)
    for n in names: reads[n] = {"address": ALL[n][0], "views": r.get(n)}
    print(f"chunk {ci+1} OK via {ep} ({time.time()-t0:.0f}s) {names}", flush=True)
    time.sleep(2)
blk = block_number()
out = {"run": TAG, "block": blk, "reads": reads, "reads_ok": ok,
       "reads_total": len(ALL), "elapsed_s": round(time.time() - t0, 1)}
prev = json.load(open(BASE + "run-2026-11-15-0529-reread.json"))
changes, read_failures = [], []
pa, pb = prev.get("reads", {}), reads
for name in sorted(set(pa) | set(pb)):
    va = (pa.get(name) or {}).get("views") or {}
    vb = (pb.get(name) or {}).get("views") or {}
    for k in sorted(set(va) | set(vb)):
        if va.get(k) is None and vb.get(k) is None:
            continue
        if vb.get(k) is None:
            read_failures.append({"contract": name, "view": k, "prev": va.get(k)})
        elif va.get(k) != vb.get(k):
            changes.append({"contract": name, "view": k, "prev": va.get(k), "now": vb.get(k)})
out["changes_vs_0529"] = changes
out["read_failures_vs_0529"] = read_failures
out["prev_block"] = prev.get("block")
json.dump(out, open(BASE + "run-" + TAG + "-reread.json", "w"), indent=1)
print(json.dumps({"block": blk, "reads_ok": ok, "total": len(ALL),
                  "elapsed_s": out["elapsed_s"], "n_changes": len(changes),
                  "changes": changes, "n_read_failures": len(read_failures)}, indent=1))
