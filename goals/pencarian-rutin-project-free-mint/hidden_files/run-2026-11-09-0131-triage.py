#!/usr/bin/env python3
"""Triage run 2026-11-09 01:31 WIB - 4 first-seen contracts from scan window.
Read-only. Golden Agents 0x4233..., GEODES 0x06c7..., BONK AGENT 0x6546...,
AGENT TERMINAL 0x169F... (known same-owner discard candidate)."""
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
OUT = f"{BASE}/run-2026-11-09-0131-triage.json"

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

def call_addr(addr, sig):
    data = sel(sig)
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]},
                           timeout=25, retries=0)
            r = out.get("result") if isinstance(out, dict) else None
            if r and r != "0x":
                return "0x" + r[-40:]
            return None
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

def first_mint(addr, first_block, max_back=20000):
    """Walk back in 1000-block chunks (Ankr) from first_block-1 for earlier mints."""
    frm = first_block
    searched_to = first_block - 1
    while first_block - frm < max_back and frm > 0:
        to = frm - 1
        frm = max(0, to - 999)
        try:
            logs, _ = scan.ankr_logs(frm, to, [scan.TRANSFER, scan.ZERO_TOPIC])
        except Exception as e:
            return {"error": str(e), "searched_from": frm, "searched_to": to}
        mine = [l for l in logs if l.get("address", "").lower() == addr.lower()]
        if mine:
            blk = min(int(l["blockNumber"], 16) for l in mine)
            return {"first_block": blk, "first_block_ts": block_ts(blk),
                    "mints_in_chunk": len(mine), "searched_from": frm, "searched_to": to,
                    "earlier_than_window": True}
        print(f"  walkback {frm}-{to}: 0 mints for {addr[:10]}", flush=True)
    return {"first_block": first_block, "first_block_ts": block_ts(first_block),
            "searched_from": frm, "searched_to": searched_to,
            "earlier_than_window": False,
            "note": f"no earlier mint in {max_back} blocks back from first_block"}

TARGETS = [
    ("Golden Agents", "0x4233C62919CC03168a361C547117c1553C375bfC", 132445024, 6),
    ("GEODES", "0x06c7f79B54859a7a6320A0f01fd73981B50F08A1", 132444276, 1),
    ("BONK AGENT Collector Card", "0x6546b3e4D638e576464Aa7349B5151F9d3a11ccd", 132444244, 25),
    ("AGENT TERMINAL", "0x169F9cfC148ba462Bb0073466939e8Eae32C0be5", 132444907, 1),
]

res = {"started": time.strftime("%Y-%m-%d %H:%M WIB")}
discards = json.load(open(f"{BASE}/same-owner-discards.json")) if __import__("os").path.exists(f"{BASE}/same-owner-discards.json") else {}
discard_owners = set()
if isinstance(discards, dict):
    for v in discards.values():
        if isinstance(v, dict) and v.get("owner"):
            discard_owners.add(v["owner"].lower())
print("discard owners known:", len(discard_owners), flush=True)

for name, addr, first_block, window_mints in TARGETS:
    d = {"address": addr, "window_first_block": first_block, "window_mints": window_mints}
    d["name"] = call_str(addr, "name()")
    d["symbol"] = call_str(addr, "symbol()")
    for v in ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
              "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
              "freeClaimed(address)", "mintedBy(address)", "price()", "canMint(address)",
              "freeLeft()", "mintedByAgent(address)"]:
        sig = v
        if "(address)" in sig:
            d[sig.split("(")[0] + "_user"] = call(addr, sig, "user")
        else:
            d[sig.split("(")[0]] = call(addr, sig)
    # quote(user,1) + quote(1) + priceOf(user,1) + costOf(user,1)
    for sig, key, args in [("quote(address,uint256)", "quote_user_1", "user1"),
                           ("quote(uint256)", "quote_1", "1"),
                           ("priceOf(address,uint256)", "priceOf_user_1", "user1"),
                           ("costOf(address,uint256)", "costOf_user_1", "user1"),
                           ("freeOf(address,uint256)", "freeOf_user_1", "user1")]:
        data = sel(sig)
        if args == "user1":
            data += enc(USER) + enc_u(1)
        else:
            data += enc_u(1)
        val = None
        for ep in EPS:
            try:
                out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                    "params": [{"to": addr, "data": data}, "latest"]},
                               timeout=25, retries=0)
                val = to_int(out.get("result")) if isinstance(out, dict) else None
                break
            except Exception:
                continue
        d[key] = val
    d["owner"] = call_addr(addr, "owner()")
    d["owner_in_discards"] = (d["owner"] or "").lower() in discard_owners if d.get("owner") else None
    for regfn in ["agentRegistry()", "REGISTRY()", "AGENT_REGISTRY()", "agentIdRegistry()"]:
        d[regfn] = call_addr(addr, regfn)
    sc = sourcify(addr)
    d["sourcify_error"] = sc.get("_error") if isinstance(sc, dict) else None
    abi = None
    try:
        abi = sc.get("stdJson", {}).get("output", {}).get("abi") or sc.get("abi")
    except Exception:
        pass
    if abi:
        fns = [f.get("name") for f in abi if f.get("type") == "function"]
        d["abi_fns"] = fns
        d["agent_shape"] = {
            "mint": any("mint" in f.lower() for f in fns),
            "free_views": [f for f in fns if "free" in f.lower()],
            "agent": any("agent" in f.lower() or "registry" in f.lower() for f in fns),
            "quote": any("quote" in f.lower() or "cost" in f.lower() or "price" in f.lower() for f in fns)}
        d["registry_bytes"] = REGISTRY[2:].lower() in json.dumps(sc).lower()
        # contractURI / tokenURI external link check (method H/I)
        d["contractURI"] = call_str(addr, "contractURI()")
    else:
        d["abi_fns"] = None
    print(name, json.dumps(d, default=str), flush=True)
    print(f"{name} first-mint walkback...", flush=True)
    d["first_mint"] = first_mint(addr, first_block)
    print(f"{name} FIRST", json.dumps(d["first_mint"], default=str), flush=True)
    res[name] = d

with open(OUT, "w") as f:
    json.dump(res, f, indent=1, default=str)
print("TRIAGE DONE", OUT, flush=True)
