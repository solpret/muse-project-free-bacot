#!/usr/bin/env python3
"""Verify ALL ACCESS 0xc3ce00677dad113f5d466d46c8c7b3a227855a5b (Boltbook Radar post, run 0301)."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import batch as _batch
from ankr import ankr_post
from Crypto.Hash import keccak

ADDR = "0xc3ce00677dad113f5d466d46c8c7b3a227855a5b"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v not in (None, "0x") else None
    except Exception: return None

def raw(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            out = _batch(calls, endpoint=ep, timeout=20)
            if not isinstance(out, list) or len(out) != len(calls): continue
            res = {}
            for item, key in zip(out, keys):
                res[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return res
        except Exception:
            continue
    return None

def raw_addr(addr, sig):
    for ep in EPS:
        try:
            r = _batch([("eth_call", [{"to": addr, "data": sel(sig)}, "latest"])], endpoint=ep, timeout=15)[0]
            if r and len(r) >= 66: return "0x" + r[-40:]
        except Exception: continue
    return None

def raw_str(addr, sig):
    for ep in EPS:
        try:
            r = _batch([("eth_call", [{"to": addr, "data": sel(sig)}, "latest"])], endpoint=ep, timeout=15)[0]
            if not r or r == "0x": return None
            b = bytes.fromhex(r[2:])
            # abi string: offset(32) + len(32) + data
            if len(b) >= 64:
                ln = int.from_bytes(b[32:64], "big")
                if 0 < ln <= len(b) - 64:
                    return b[64:64 + ln].decode("utf-8", "replace")
            return r
        except Exception: continue
    return None

views = ["totalSupply()", "totalMinted()", "MAX_SUPPLY()", "FREE_SUPPLY()",
         "freeClaimed()", "freeMinted()", "freeLeft()", "freeSupply()",
         "mintOpen()", "paused()", "price()", "quote(address,uint256)",
         "freeClaimed(address)", "freeMinted(address)", "balanceOf(address)",
         "spotsLeft()", "freeFor(address)"]
d = raw(ADDR, views)
print("VIEWS:", json.dumps(d), flush=True)
print("owner():", raw_addr(ADDR, "owner()"), flush=True)
print("agentRegistry():", raw_addr(ADDR, "agentRegistry()"), flush=True)
print("AGENT_ID():", raw_addr(ADDR, "AGENT_ID()"), flush=True)
print("name():", raw_str(ADDR, "name()"), flush=True)
print("symbol():", raw_str(ADDR, "symbol()"), flush=True)
print("tokenURI(0):", raw_str(ADDR, "tokenURI(uint256)") if False else "(skip: needs arg)", flush=True)

# Sourcify ABI
try:
    req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi",
                                 headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        sd = json.load(r)
    abi = sd.get("abi") or []
    fns = sorted({f.get("name") for f in abi if isinstance(f, dict) and f.get("type") == "function" and f.get("name")})
    print("SOURCIFY verified, fns:", fns, flush=True)
    print("SOURCIFY raw match:", sd.get("match") or sd.get("stdJson", {}).get("match") if isinstance(sd, dict) else None, flush=True)
except Exception as e:
    print("SOURCIFY error:", e, flush=True)

# First mint via Ankr getLogs (walkback in 1000-block chunks from current head)
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
head = None
for ep in EPS:
    try:
        head = int(_batch([("eth_blockNumber", [])], endpoint=ep, timeout=15)[0], 16); break
    except Exception: continue
print("HEAD:", head, flush=True)
found = None
to_blk = head
for i in range(12):
    frm = max(to_blk - 999, 0)
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to_blk),
                                          "pageSize": 1000, "decodeLogs": False,
                                          "address": ADDR, "topics": [TRANSFER, ZERO]}, timeout=30)
        logs = body.get("result", {}).get("logs", [])
    except Exception as e:
        print(f"walkback chunk {frm}-{to_blk} ERROR {e}", flush=True); logs = []
    print(f"walkback {frm}-{to_blk}: {len(logs)} mint logs", flush=True)
    if logs:
        first = min(logs, key=lambda l: int(l["blockNumber"], 16))
        found = int(first["blockNumber"], 16)
        print("FIRST MINT BLOCK:", found, "tx:", first.get("transactionHash"), flush=True)
        break
    to_blk = frm - 1
    if to_blk <= 0: break
if found is None:
    print("FIRST MINT: none found in last 12000 blocks", flush=True)
# block timestamp for first mint
if found:
    for ep in EPS:
        try:
            b = _batch([("eth_getBlockByNumber", [hex(found), False])], endpoint=ep, timeout=15)[0]
            ts = int(b["timestamp"], 16)
            from datetime import datetime, timezone, timedelta
            print("FIRST MINT TIME WIB:", datetime.fromtimestamp(ts, timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB"), flush=True)
            break
        except Exception as e:
            print("block ts fail", ep, e, flush=True)
json.dump({"views": d, "head": head, "first_mint_block": found},
          open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-09-0301-allaccess.json", "w"), indent=1)
print("DONE")
