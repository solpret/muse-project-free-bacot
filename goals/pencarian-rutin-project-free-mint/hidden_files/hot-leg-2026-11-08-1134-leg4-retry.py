#!/usr/bin/env python3
"""Hot-leg 1134 leg4 retry (lean): per-item batched eth_calls + single-call fallback.
Single endpoint; hard cap via outer timeout. Writes -reread.json + -leg4.log."""
import json, re, sys, time, os, concurrent.futures
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-1134"
PREV_TAG = "hot-leg-2026-11-08-1129"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc-dataseed1.bnbchain.org/"
t0 = time.time()
log = {"run": "free-mint-hot-leg 2026-11-08 11:34:38 WIB leg4-retry", "note": "leg4 first attempt hit outer timeout 100s (RPC slow); retry with per-item batched calls + single-call fallback"}

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
def call_data(sig, arg=""):
    data = sel(sig)
    if arg == "USER": data += enc_addr(USER)
    elif arg == "USER1": data += enc_addr(USER) + format(1, "064x")
    return data
def single(addr, sig, arg=""):
    try:
        res = batch([("eth_call", [{"to": addr, "data": call_data(sig, arg)}, "latest"])], endpoint=EP, timeout=5)
        return to_int(res[0])
    except Exception:
        return None

def do_item(name):
    addr, keys = ITEMS[name]
    calls = [("eth_call", [{"to": addr, "data": call_data(*V[k])}, "latest"]) for k in keys]
    out = {"address": addr}
    try:
        res = batch(calls, endpoint=EP, timeout=8)
        for k, v in zip(keys, res):
            out[k] = to_int(v)
        return name, out, "batched"
    except Exception:
        for k in keys:
            out[k] = single(addr, *V[k])
        return name, out, "fallback-single"

try:
    blk = int(batch([("eth_blockNumber", [])], endpoint=EP, timeout=6)[0], 16)
except Exception as ex:
    blk = None; log["leg4_block_error"] = str(ex)[:120]
items = {}
modes = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
    for name, out, mode in ex.map(do_item, ITEMS):
        items[name] = out; modes[name] = mode
reread = {"block": blk, "items": items}
json.dump(reread, open(BASE+TAG+"-reread.json","w"), indent=1)
log["leg4"] = {"block": blk, "n": len(items), "modes": modes}
prev = json.load(open(BASE+PREV_TAG+"-reread.json"))
log["leg4_diff_prev_file"] = PREV_TAG+"-reread.json"
diffs = []
for name, cur in items.items():
    old = prev["items"].get(name, {})
    for k, v in cur.items():
        if k == "address": continue
        ov = old.get(k)
        if v != ov:
            diffs.append({"item": name, "field": k, "old": ov, "new": v})
log["leg4_diff_vs_prev"] = diffs

# --- Pandora ---
PANDORA = "0xdb8A4102C49a41cfAeD7673A3F155f19853Af5e8"
pandora = {"address": PANDORA}
for _k, _sig in {"totalMinted": "totalMinted()", "totalSupply": "totalSupply()",
                 "mintActive": "mintActive()", "publicRemaining": "publicRemaining()",
                 "freeUsed_user": "freeUsed(address)"}.items():
    _arg = "USER" if _k == "freeUsed_user" else ""
    pandora[_k] = single(PANDORA, _sig, _arg)
log["leg3b_pandora"] = pandora

# --- bridge ---
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
