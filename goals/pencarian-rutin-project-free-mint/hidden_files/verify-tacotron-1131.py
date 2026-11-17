#!/usr/bin/env python3
"""Tacotron 0x05debe44... verify run 1131. Read-only, bounded ~90s."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
C = "0x05debe4445232205ae7e79d02cb5de5aa0641eff"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
t0 = time.time()
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def call(to, data, timeout=8):
    for ep in EPS:
        if time.time() - t0 > 85: return "deadline"
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], timeout, retries=0)
        except Exception: continue
    return None
def cint(to, sig, args=""):
    v = call(to, sel(sig) + args)
    if v in (None, "deadline"): return v
    try: return int(v, 16)
    except Exception: return v
def cstr(to, sig):
    v = call(to, sel(sig))
    if v in (None, "deadline") or not isinstance(v, str) or len(v) < 130: return v
    try:
        ln = int(v[66:130], 16)
        return bytes.fromhex(v[130:130+ln*2]).decode("utf-8", "replace")
    except Exception: return v
out = {"contract": C, "block": None}
try:
    out["block"] = int(_single(EPS[0], "eth_blockNumber", [], 8, retries=0), 16)
except Exception as e:
    out["block_err"] = str(e)[:80]
# Sourcify metadata
try:
    req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{C}",
                                 headers={"User-Agent": "free-bacot/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r: meta = json.load(r)
    out["sourcify"] = {"verified": True, "match": meta.get("stdJson", {}).get("match") or meta.get("match"),
                       "verifiedAt": (meta.get("creationMatch") or {}).get("verifiedAt") or (meta.get("stdJson") or {}).get("verifiedAt"),
                       "creationMatch": meta.get("creationMatch", {}).get("match") if isinstance(meta.get("creationMatch"), dict) else None}
    abi = meta.get("abi") or (meta.get("stdJson") or {}).get("abi") or []
    if not abi:
        req2 = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{C}?fields=abi",
                                      headers={"User-Agent": "free-bacot/1.0"})
        with urllib.request.urlopen(req2, timeout=20) as r2: abi = json.load(r2).get("abi", [])
    out["abi_functions"] = sorted({e["name"] for e in abi if e.get("type") == "function"})
    # quote signature
    for e in abi:
        if e.get("type") == "function" and e.get("name") == "quote":
            out["quote_abi"] = e
        if e.get("type") == "function" and e.get("name") == "contractURI":
            out["has_contractURI"] = True
    json.dump(abi, open(BASE + "abi-tacotron-1131.json", "w"))
except Exception as e:
    out["sourcify"] = {"verified": False, "error": f"{type(e).__name__}: {str(e)[:120]}"}
U = enc_addr(USER)
out["name"] = cstr(C, "name()")
out["symbol"] = cstr(C, "symbol()")
out["contractURI"] = cstr(C, "contractURI()")
out["freeClaimed()"] = cint(C, "freeClaimed()")
out["totalSupply()"] = cint(C, "totalSupply()")
out["FREE_SUPPLY()"] = cint(C, "FREE_SUPPLY()")
out["MAX_SUPPLY()"] = cint(C, "MAX_SUPPLY()")
out["mintOpen()"] = cint(C, "mintOpen()")
out["freeLeft(user)"] = cint(C, "freeLeft(address)", U)
out["freeFor(user)"] = cint(C, "freeFor(address)", U)
out["freeClaimed(user)"] = cint(C, "freeClaimed(address)", U)
out["freeUsed(user)"] = cint(C, "freeUsed(address)", U)
out["mintedBy(user)"] = cint(C, "mintedBy(address)", U)
out["balanceOf(user)"] = cint(C, "balanceOf(address)", U)
out["owner()"] = None
ov = cint(C, "owner()")
out["owner()"] = ("0x" + format(ov, "040x")) if isinstance(ov, int) and ov else ov
# quote(user,1): returns tuple? read raw
qv = call(C, sel("quote(address,uint256)") + U + format(1, "064x"))
out["quote(user,1)_raw"] = qv
if isinstance(qv, str) and len(qv) >= 130:
    try:
        out["quote(user,1)_tuple"] = [int(qv[2:66], 16), int(qv[66:130], 16)]
    except Exception:
        pass
# first-mint confirmation: any mint before block 131000000?
try:
    r = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(130000000),
                  "toBlock": hex(131000000), "address": C,
                  "topics": [TRANSFER, ZERO], "pageSize": 5, "decodeLogs": False}, timeout=30)
    logs = r.get("result", {}).get("logs", [])
    out["pre_131000000_mint_logs"] = len(logs)
    out["pre_131000000_earliest"] = int(logs[0]["blockNumber"], 16) if logs else None
except Exception as e:
    out["pre_131000000_error"] = f"{type(e).__name__}: {str(e)[:120]}"
out["duration_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "verify-tacotron-1131.json", "w"), indent=1)
print(json.dumps(out, indent=1))
