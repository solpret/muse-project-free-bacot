#!/usr/bin/env python3
"""Leg 3 fast probe for the two new S1 contracts found in hot-leg run 0554."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-16-0554"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
CONTRACTS = ["0x1b8894391a3DcFe7e248C321103265AB52E273e0",
             "0xdb7A8fa53F96cf4744c21BB6c78a2272ec6566e5"]
t0 = time.time()
out = {"run": "hot-leg 0554 leg3", "contracts": {}}

def curl(url, timeout=15):
    try:
        r = subprocess.run(["curl", "-s", "-m", str(timeout), "-A", "Mozilla/5.0", url],
                           capture_output=True, timeout=timeout + 5)
        return r.stdout
    except Exception:
        return b""

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def build(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        else:
            d += enc_u(int(a))
    return d
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def post_rpc(ep, payload, timeout=60):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10)
    return json.loads(r.stdout)

# Views to probe (only those present in ABI)
PROBE = [("name", "name()", []), ("symbol", "symbol()", []),
         ("FREE_SUPPLY", "FREE_SUPPLY()", []), ("free_supply", "free_supply()", []),
         ("freeClaimed_total", "freeClaimed()", []),
         ("freeClaimed_user", "freeClaimed(address)", [USER]),
         ("quote1", "quote(address,uint256)", [USER, 1]),
         ("totalSupply", "totalSupply()", []),
         ("totalMinted", "totalMinted()", []),
         ("freeMinted", "freeMinted()", []),
         ("mintOpen", "mintOpen()", []), ("saleOpen", "saleOpen()", []),
         ("mintStart", "mintStart()", []), ("saleStart", "saleStart()", []),
         ("startTime", "startTime()", []), ("openedAt", "openedAt()", []),
         ("agentRegistry", "agentRegistry()", []),
         ("owner", "owner()", []), ("factory", "factory()", []),
         ("balanceOf_user", "balanceOf(address)", [USER])]

for a in CONTRACTS:
    rec = {"address": a}
    raw = curl(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi,metadata", 15)
    try:
        j = json.loads(raw.decode(errors="replace"))
    except Exception:
        j = {}
    abi = j.get("abi") or (j.get("stdJson") or {}).get("abi") or []
    names = set()
    for fn in abi:
        if isinstance(fn, dict) and fn.get("type") == "function":
            names.add((fn.get("name") or "").lower())
    rec["n_fns"] = len(names)
    rec["fns"] = sorted(names)
    # metadata: contract name / compiler / sources for linkage clues
    md = j.get("metadata") or {}
    if isinstance(md, dict):
        rec["contract_name"] = md.get("contractName") or (md.get("settings") or {}).get("compilationTarget")
    # choose probes present in ABI (name/symbol return strings; handle separately)
    calls, meta = [], []
    for key, sig, args in PROBE:
        fname = sig.split("(")[0].lower()
        if fname not in names:
            continue
        calls.append({"jsonrpc": "2.0", "id": len(calls) + 1, "method": "eth_call",
                      "params": [{"to": a, "data": build(sig, args)}, "latest"]})
        meta.append((key, sig))
    views = {}
    if calls:
        for ep in EPS:
            try:
                res = post_rpc(ep, calls, timeout=60)
                if not isinstance(res, list) or len(res) != len(calls):
                    continue
                for it, (key, sig) in zip(res, meta):
                    if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                        views[key] = None
                    else:
                        r = it["result"]
                        if key in ("name", "symbol"):
                            views[key] = r  # raw hex, decode later
                        else:
                            views[key] = to_int(r[:66]) if len(r) >= 66 else r
                break
            except Exception as e:
                print(a, "ep", ep, "exc", str(e)[:80], flush=True)
                continue
    rec["views"] = views
    # creation / deploy time: eth_getCode + first tx via BscScan? skip; use block of first mint later if needed
    out["contracts"][a] = rec
    print(a, json.dumps(rec, indent=1)[:2000], flush=True)

out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + f"hot-leg-{TAG}-leg3.json", "w"), indent=1)
print("ELAPSED", out["elapsed_s"])
