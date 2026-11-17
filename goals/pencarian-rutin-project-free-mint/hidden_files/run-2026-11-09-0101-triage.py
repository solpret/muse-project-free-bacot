#!/usr/bin/env python3
"""Triage run 2026-11-09 01:01 WIB — new Boltbook items + Pokechain sellout verify.
Read-only. Gryphlume 0x8ea465abd41aec8b6f1bd80a7c6c37d3ae85529c (NFT),
YAOQIAN sale 0x75148608e41C4f3A325F4DBC040B2B60CDc772d6 (track C),
Backdoor Pass 0x9c6a008f73a1d1941f4763b88c6ee8c8e4ef8b0a (NFT),
Pokechain 0x4EF929aF00cB93993c3D01834C4DA79200d31e32 (sellout verify).
"""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import _post as _fr_post
import onchain_nft_scan as scan
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
OUT = f"{BASE}/run-2026-11-09-0101-triage.json"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def call(addr, sig, arg=None):
    """arg: None | 'user' | int"""
    data = sel(sig)
    if arg == "user": data += enc(USER)
    elif isinstance(arg, int): data += enc_u(arg)
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]},
                           timeout=25, retries=0)
            if isinstance(out, dict) and "error" in out: return None
            return to_int(out.get("result")) if isinstance(out, dict) else None
        except Exception:
            continue
    return None

def call_str(addr, sig):
    data = sel(sig)
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]},
                           timeout=25, retries=0)
            r = out.get("result") if isinstance(out, dict) else None
            if not r or r == "0x": return None
            b = bytes.fromhex(r[2:])
            # abi string: offset(32) + len(32) + data
            if len(b) >= 64:
                ln = int.from_bytes(b[32:64], "big")
                return b[64:64+ln].decode("utf-8", "replace")
            return None
        except Exception:
            continue
    return None

def sourcify(addr):
    url = f"https://sourcify.dev/server/v2/contracts/56/{addr}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except Exception as e:
        return {"_error": str(e)}

def block_ts(blk):
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                "params": [hex(blk), False]}, timeout=25, retries=0)
            ts = out.get("result", {}).get("timestamp")
            return int(ts, 16) if ts else None
        except Exception:
            continue
    return None

def first_mint(addr, head, max_back=30000):
    """Walk back in 1000-block chunks (Ankr) for first Transfer-from-zero."""
    frm = head
    while head - frm < max_back and frm > 0:
        to = frm
        frm = max(0, to - 999)
        try:
            logs, _ = scan.ankr_logs(frm, to, [scan.TRANSFER, scan.ZERO_TOPIC])
        except Exception as e:
            return {"error": str(e), "searched_from": frm, "searched_to": to}
        mine = [l for l in logs if l.get("address", "").lower() == addr.lower()]
        if mine:
            blk = min(int(l["blockNumber"], 16) for l in mine)
            return {"first_block": blk, "first_block_ts": block_ts(blk),
                    "mints_in_chunk": len(mine), "searched_from": frm, "searched_to": to}
        print(f"  walkback {frm}-{to}: 0 mints for {addr[:10]}", flush=True)
    return {"first_block": None, "searched_from": max(0, head - max_back), "searched_to": head}

head = int(_fr_post(EPS[0], {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber",
                             "params": []}, timeout=20, retries=0)["result"], 16)
print("HEAD", head, flush=True)
res = {"head": head, "started": time.strftime("%Y-%m-%d %H:%M WIB")}

# --- Gryphlume ---
G = "0x8ea465abd41aec8b6f1bd80a7c6c37d3ae85529c"
g = {"address": G}
for v in ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
          "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
          "freeClaimed(address)", "mintedBy(address)", "price()", "priceOf(address,uint256)"]:
    sig = v
    arg = None
    if "(address)" in sig and "uint256" in sig:
        # priceOf(address,uint256): encode user + 1
        data = sel(sig) + enc(USER) + enc_u(1)
        g["priceOf_user_1"] = None
        for ep in EPS:
            try:
                out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                    "params": [{"to": G, "data": data}, "latest"]},
                               timeout=25, retries=0)
                g["priceOf_user_1"] = to_int(out.get("result")) if isinstance(out, dict) else None
                break
            except Exception:
                continue
        continue
    if "(address)" in sig:
        arg = "user"
        key = sig.split("(")[0] + "_user"
    else:
        key = sig.split("(")[0]
    g[key] = call(G, sig, arg)
g["name"] = call_str(G, "name()")
g["symbol"] = call_str(G, "symbol()")
g["canMint_user"] = call(G, "canMint(address)", "user")
g["agentGate"] = call(G, "agentGate()")
g["REGISTRY"] = None
# REGISTRY() returns address (32-byte)
for ep in EPS:
    try:
        out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                            "params": [{"to": G, "data": sel("REGISTRY()")}, "latest"]},
                       timeout=25, retries=0)
        r = out.get("result")
        if r and r != "0x":
            g["REGISTRY"] = "0x" + r[-40:]
        break
    except Exception:
        continue
sc = sourcify(G)
g["sourcify_status"] = sc.get("stdJson", {}).get("status") if isinstance(sc, dict) else None
g["sourcify_verifiedAt"] = sc.get("creationMatch", {}) if isinstance(sc, dict) else None
g["sourcify_error"] = sc.get("_error") if isinstance(sc, dict) else None
print("GRYPHLUME", json.dumps(g, default=str), flush=True)
print("Gryphlume first-mint walkback...", flush=True)
g["first_mint"] = first_mint(G, head)
print("GRYPHLUME FIRST", json.dumps(g["first_mint"], default=str), flush=True)
res["Gryphlume"] = g

# --- YAOQIAN sale (track C S1 shape) ---
Y = "0x75148608e41C4f3A325F4DBC040B2B60CDc772d6"
y = {"address": Y}
for v in ["totalSupply()", "freeClaimed()", "freeMinted()", "freeSharesRemaining()",
          "sharesMinted()", "paidShares()", "maxShares()", "MAX_SHARES()",
          "sold()", "deadline()", "phase()", "mintOpen()", "balanceOf(address)",
          "freeClaimed(address)"]:
    sig = v
    if "(address)" in sig:
        y[sig.split("(")[0] + "_user"] = call(Y, sig, "user")
    else:
        y[sig.split("(")[0]] = call(Y, sig)
# quote(user,1) and quote(1): quote(uint256) + quote(address,uint256)
for sig, arg in [("quote(uint256)", 1), ("quote(address,uint256)", None)]:
    if arg is None:
        data = sel(sig) + enc(USER) + enc_u(1)
        key = "quote_user_1"
    else:
        data = sel(sig) + enc_u(1)
        key = "quote_1"
    val = None
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": Y, "data": data}, "latest"]},
                           timeout=25, retries=0)
            val = to_int(out.get("result")) if isinstance(out, dict) else None
            break
        except Exception:
            continue
    y[key] = val
y["name"] = call_str(Y, "name()")
y["symbol"] = call_str(Y, "symbol()")
sc = sourcify(Y)
y["sourcify_error"] = sc.get("_error") if isinstance(sc, dict) else None
abi = None
try:
    abi = sc.get("stdJson", {}).get("output", {}).get("abi") or sc.get("abi")
except Exception:
    pass
if abi:
    fns = [f.get("name") for f in abi if f.get("type") == "function"]
    y["abi_fns"] = fns
    y["shape_S1"] = {"mint": any("mint" in f.lower() for f in fns),
                     "quote": any("quote" in f.lower() or "cost" in f.lower() or "price" in f.lower() for f in fns),
                     "free_views": [f for f in fns if "free" in f.lower()],
                     "agent": any("agent" in f.lower() or "registry" in f.lower() for f in fns)}
    src = json.dumps(sc)
    y["registry_bytes"] = REGISTRY[2:].lower() in src.lower()
else:
    y["abi_fns"] = None
print("YAOQIAN", json.dumps(y, default=str), flush=True)
res["YAOQIAN"] = y

# --- Backdoor Pass ---
B = "0x9c6a008f73a1d1941f4763b88c6ee8c8e4ef8b0a"
b = {"address": B}
for v in ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
          "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
          "freeClaimed(address)", "mintedBy(address)", "price()"]:
    sig = v
    if "(address)" in sig:
        b[sig.split("(")[0] + "_user"] = call(B, sig, "user")
    else:
        b[sig.split("(")[0]] = call(B, sig)
b["name"] = call_str(B, "name()")
b["symbol"] = call_str(B, "symbol()")
b["canMint_user"] = call(B, "canMint(address)", "user")
sc = sourcify(B)
b["sourcify_error"] = sc.get("_error") if isinstance(sc, dict) else None
try:
    abi = sc.get("stdJson", {}).get("output", {}).get("abi") or sc.get("abi")
except Exception:
    abi = None
if abi:
    fns = [f.get("name") for f in abi if f.get("type") == "function"]
    b["abi_fns"] = fns
    b["agent_shape"] = {"mint": any("mint" in f.lower() for f in fns),
                        "free_views": [f for f in fns if "free" in f.lower()],
                        "agent": any("agent" in f.lower() or "registry" in f.lower() for f in fns)}
    b["registry_bytes"] = REGISTRY[2:].lower() in json.dumps(sc).lower()
else:
    b["abi_fns"] = None
print("BACKDOOR", json.dumps(b, default=str), flush=True)
print("Backdoor first-mint walkback...", flush=True)
b["first_mint"] = first_mint(B, head)
print("BACKDOOR FIRST", json.dumps(b["first_mint"], default=str), flush=True)
res["BackdoorPass"] = b

# --- Pokechain sellout verify ---
P = "0x4EF929aF00cB93993c3D01834C4DA79200d31e32"
p = {"address": P,
     "totalSupply": call(P, "totalSupply()"),
     "totalMinted": call(P, "totalMinted()"),
     "MAX_SUPPLY": call(P, "MAX_SUPPLY()")}
print("POKECHAIN", json.dumps(p), flush=True)
res["Pokechain"] = p

with open(OUT, "w") as f:
    json.dump(res, f, indent=1, default=str)
print("TRIAGE DONE", OUT, flush=True)
