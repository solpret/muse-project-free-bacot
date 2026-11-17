#!/usr/bin/env python3
"""Hot-leg 2344 leg4: snapshot re-read via direct dataseed eth_call (fallback dataseed2/publicnode).
V/ITEMS extracted from the 1129 script. Diff vs 2249 reread (+2319 for null baseline)."""
import json, re, sys, time, subprocess, concurrent.futures, os
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-2354"
PREV_TAG = "hot-leg-2026-11-08-1129"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc.publicnode.com/"]
t0 = time.time()
log = {"run": "free-mint-hot-leg 2026-11-08 23:44:38 WIB leg4"}

seen = json.load(open(BASE + "hot-leg-seen.json"))
src = open(BASE + PREV_TAG + ".py").read()
def extract(var):
    m = re.search(re.escape(var) + r"\s*=\s*(\{.*?^\})", src, re.S | re.M)
    return eval(m.group(1))
V = extract("V"); ITEMS = extract("ITEMS")

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def rpc_call(method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    for ep in EPS:
        try:
            out = subprocess.run(["curl", "-sL", "--max-time", "15", "-X", "POST", ep,
                                  "-H", "Content-Type: application/json", "-d", payload],
                                 capture_output=True, text=True, timeout=20).stdout
            r = json.loads(out).get("result")
            if r is not None:
                return r
        except Exception:
            continue
    return None

def single(addr, sig, arg=""):
    data = sel(sig)
    if arg == "USER": data += enc_addr(USER)
    elif arg == "USER1": data += enc_addr(USER) + format(1, "064x")
    r = rpc_call("eth_call", [{"to": addr, "data": data}, "latest"])
    return to_int(r)

blk = to_int(rpc_call("eth_blockNumber", []))
if blk is None:
    log["leg4_block_error"] = "eth_blockNumber failed on all endpoints"

def do_item(name):
    addr, keys = ITEMS[name]
    out = {"address": addr}
    for k in keys:
        sig, arg = V[k]
        out[k] = single(addr, sig, arg)
    return name, out

items = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for name, out in ex.map(do_item, ITEMS):
        items[name] = out
reread = {"block": blk, "items": items}
json.dump(reread, open(BASE + TAG + "-reread.json", "w"), indent=1)
log["leg4"] = {"block": blk, "n": len(items)}
prev = json.load(open(BASE + "hot-leg-2026-11-08-2344-reread.json"))
prev2 = json.load(open(BASE + "hot-leg-2026-11-08-2319-reread.json"))
log["leg4_diff_prev_file"] = "hot-leg-2026-11-08-2344-reread.json (+2319 for null baseline)"
diffs = []
recoveries = []
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
                pass  # fresh null = read failure artifact, not a state change
            else:
                diffs.append({"item": name, "field": k, "old": ov, "new": v})
log["leg4_diff_vs_prev"] = diffs
log["leg4_recoveries_null_to_value"] = recoveries

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
bridge = json.load(open(BASE + "scan-bridge.json"))
snap = json.load(open(BASE + "onchain-snapshot.json"))
snap_addrs = set()
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict):
        for f in ("address", "sale", "token"):
            if v.get(f): snap_addrs.add(v[f].lower())
bcontracts = bridge.get("contracts", {})
log["bridge"] = {"n_contracts": len(bcontracts),
    "mtime": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(os.path.getmtime(BASE + "scan-bridge.json"))),
    "in_snapshot": len([a for a in bcontracts if a.lower() in snap_addrs]),
    "same_owner_discarded": len([a for a, v in bcontracts.items() if v.get("same_owner_discarded")]),
    "note": "read-only; bridge diff checked separately."}
log["elapsed_sec"] = round(time.time() - t0, 1)
json.dump(log, open(BASE + TAG + "-leg4.log", "w"), indent=1)
print(json.dumps(log, indent=1))
print("ELAPSED", round(time.time() - t0, 1))
