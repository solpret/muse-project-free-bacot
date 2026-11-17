#!/usr/bin/env python3
"""Hot-leg re-read run 2026-11-14 13:19 WIB. Focus set only (near-threshold items
from run 1301 + new Boltbook address). Read-only; writes run-2026-11-14-1319-hotleg-reread.json.
No preview/mint. Reuses ITEMS defs from run-2026-11-14-1301-reread.py."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
t0 = time.time()
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
def post_rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)
# load ITEMS from 1301 script (defs only, up to 'def chunked')
lines = open(BASE + "run-2026-11-14-1301-reread.py").read().splitlines()
cut = next(i for i, l in enumerate(lines) if l.startswith("def chunked"))
ns = {}
exec("\n".join(lines[:cut]), ns)
ITEMS1301 = ns["ITEMS"]
FOCUS = ["WANGCAI", "YUANBAO", "REOPIR", "CPASS", "ORBIT", "LumenFindings", "DragonAgents", "B77D", "RaceAgents"]
ITEMS = {n: ITEMS1301[n] for n in FOCUS if n in ITEMS1301}
ITEMS["Boltbook-0xcbc0"] = ("0xcbc0a4535c520ce308ac490d4975816e038953d4", [
    ("totalSupply", "totalSupply()", []), ("freeClaimed", "freeClaimed()", []),
    ("freeMinted", "freeMinted()", []), ("FREE_SUPPLY", "FREE_SUPPLY()", []),
    ("FREE_SLOTS", "FREE_SLOTS()", []), ("freeRemaining", "freeRemaining()", []),
    ("name", "name()", []), ("symbol", "symbol()", [])])
def read_chunk(chunk):
    calls, meta = [], []
    for name, (addr, views) in chunk:
        for key, sig, args in views:
            calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                          "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
            meta.append((name, key))
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=60)
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
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=60)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16)
        except Exception: continue
    return None
items = list(ITEMS.items())
reads, ok = {}, 0
for i in range(0, len(items), 3):
    ch = items[i:i+3]
    r, ep = read_chunk(ch)
    names = [n for n, _ in ch]
    if r is None:
        print(f"chunk FAIL {names}", flush=True)
        for n in names: reads[n] = {"address": ITEMS[n][0], "views": None}
        continue
    ok += sum(1 for n in names if r.get(n) is not None)
    for n in names: reads[n] = {"address": ITEMS[n][0], "views": r.get(n)}
    print(f"chunk OK via {ep} ({time.time()-t0:.0f}s) {names}", flush=True)
    time.sleep(3)
blk = block_number()
out = {"started_wib": "2026-11-14T13:19+07:00", "reads": reads, "reads_ok": ok,
       "reads_total": len(ITEMS), "block": blk, "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "run-2026-11-14-1319-hotleg-reread.json", "w"), indent=1)
print("DONE reads_ok", ok, "/", len(ITEMS), "block", blk, "elapsed", round(time.time() - t0, 1))
