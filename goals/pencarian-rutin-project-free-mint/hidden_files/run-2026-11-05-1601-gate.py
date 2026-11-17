#!/usr/bin/env python3
"""Run 1601 gate methods C/H/I/J/E for Smeltbots/Thronemind/Hashseers/Agent Frogs + WHALE probe. Read-only."""
import json, sys, urllib.request, base64
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed2.bnbchain.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: out = json.load(r)
            if "error" in out: return None
            v = out["result"]
            if not v or v == "0x": return None
            return v
        except Exception: continue
    return None
def call_int(to, sig, args=""):
    v = raw(to, sel(sig) + args)
    if v is None: return None
    try: return int(v, 16)
    except Exception: return v
def call_str(to, sig, args=""):
    v = raw(to, sel(sig) + args)
    if v is None: return None
    try:
        b = bytes.fromhex(v[2:])
        # abi string: offset(32) + len(32) + data
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode("utf-8", "replace")
    except Exception:
        return v
def get_json(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl"})
        with urllib.request.urlopen(req, timeout=15) as r: return json.load(r)
    except Exception as e:
        return {"error": str(e)[:100]}

TARGETS = {
 "Smeltbots": "0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e",
 "Thronemind": "0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90",
 "Hashseers": "0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688",
 "Agent Frogs": "0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31",
}
out = {}
for name, addr in TARGETS.items():
    d = {"address": addr}
    o = call_int(addr, "owner()")
    d["owner"] = ("0x" + format(o, "040x")[-40:]) if isinstance(o, int) else o
    d["contractURI"] = call_str(addr, "contractURI()")
    tu = call_str(addr, "tokenURI(uint256)", enc_uint(1))
    d["tokenURI_raw"] = (tu or "")[:300]
    if tu:
        try:
            if tu.startswith("data:application/json;base64,"):
                dec = json.loads(base64.b64decode(tu.split(",", 1)[1]).decode())
                d["tokenURI_decoded"] = dec
            else:
                d["tokenURI_decoded"] = tu[:200]
        except Exception as e:
            d["tokenURI_decoded"] = {"error": str(e)[:80]}
    meta = get_json(f"https://sourcify.dev/server/v2/contract/56/{addr}")
    d["sourcify_match"] = meta.get("match") if isinstance(meta, dict) else None
    d["sourcify_error"] = meta.get("error") if isinstance(meta, dict) and "error" in meta else None
    abi = meta.get("abi") if isinstance(meta, dict) else None
    if isinstance(abi, list):
        names = [f.get("name", "") for f in abi if isinstance(f, dict)]
        d["abi_site_fns"] = [n for n in names if any(k in n.lower() for k in ("site", "url", "domain", "website", "external", "link"))]
        d["abi_fn_count"] = len(names)
        d["abi_has_registry"] = any("REGISTRY" in n or "AGENT" in n for n in names)
    else:
        d["abi_site_fns"] = None
    print(name, json.dumps(d)[:1500], flush=True)
    out[name] = d

# WHALE probe
W = "0x8a3e3eea10e1fa7d6fa768550f8e572a15eb90d0"
w = {"address": W}
w["totalSupply"] = call_int(W, "totalSupply()")
w["freeMinted"] = call_int(W, "freeMinted()")
w["freeClaimed"] = call_int(W, "freeClaimed()")
w["FREE_SUPPLY"] = call_int(W, "FREE_SUPPLY()")
w["FREE_CAP"] = call_int(W, "FREE_CAP()")
w["MAX_SUPPLY"] = call_int(W, "MAX_SUPPLY()")
w["mintPrice"] = call_int(W, "mintPrice()")
w["PRICE"] = call_int(W, "PRICE()")
w["quote_user_1"] = call_int(W, "quote(address,uint256)", enc(USER) + enc_uint(1))
w["costOf_user_1"] = call_int(W, "costOf(address,uint256)", enc(USER) + enc_uint(1))
w["mintOpen"] = call_int(W, "mintOpen()")
w["paused"] = call_int(W, "paused()")
o = call_int(W, "owner()")
w["owner"] = ("0x" + format(o, "040x")[-40:]) if isinstance(o, int) else o
w["balanceOf_user"] = call_int(W, "balanceOf(address)", enc(USER))
w["mintedBy_user"] = call_int(W, "mintedBy(address)", enc(USER))
meta = get_json(f"https://sourcify.dev/server/v2/contract/56/{W}")
w["sourcify_match"] = meta.get("match") if isinstance(meta, dict) else None
def any_mint(lo, hi):
    params = {"blockchain": "bsc", "fromBlock": hex(lo), "toBlock": hex(hi),
              "pageSize": 1000, "decodeLogs": False, "topics": [TRANSFER, ZERO], "address": W}
    body = ankr_post("ankr_getLogs", params, timeout=30)
    logs = (body.get("result", {}) or {}).get("logs", []) if isinstance(body, dict) else []
    for lg in logs:
        if len(lg.get("topics", [])) == 4:
            return int(lg["blockNumber"], 16)
    return None
def block_ts(n):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                               "params": [hex(n), False]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r:
                return int(json.load(r)["result"]["timestamp"], 16)
        except Exception: continue
    return None
lo, hi = 131600000, 131792170
fm = None
if any_mint(lo, hi) is not None:
    while lo < hi:
        mid = (lo + hi) // 2
        if any_mint(lo, mid) is not None: hi = mid
        else: lo = mid + 1
    fm = lo
w["firstMintBlock"] = fm
w["firstMintTs"] = block_ts(fm) if fm else None
print("WHALE", json.dumps(w), flush=True)
out["WHALE"] = w
json.dump(out, open(f"{BASE}/run-2026-11-05-1601-gate.json", "w"), indent=1)
print("SAVED", flush=True)
