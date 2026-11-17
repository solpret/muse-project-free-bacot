#!/usr/bin/env python3
"""Hot-leg 0954 leg-3 v2: parallel on-chain reads for ba5c/bac6/ec26 + first-mint via Ankr.
Read-only. Single primary RPC, ThreadPoolExecutor, no sequential retry storms."""
import json, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-0954"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
WIB = timezone(timedelta(hours=7))
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed.binance.org"]
CONTRACTS = {
    "ba5c": "0xba5cde0ceea8704b8944deb51228ca59a7bd9cf0",
    "bac6": "0xbac6b6de36a54b2815c02ad3cc5e6551e306aa90",
    "ec26": "0xec266bdd979b19d8a2f1266ef0610b4791dbd24b",
}
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0"*24 + a[2:].lower()
def enc_u(n): return format(n, "064x")
def rpc_once(rpc, method, params, timeout=8):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)
def call(to, data):
    for rpc in RPCS:
        try:
            o = rpc_once(rpc, "eth_call", [{"to": to, "data": data}, "latest"])
            if "error" in o or o.get("result") is None: continue
            v = o["result"]
            if v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return "err:RPC"
def call_str(to, data):
    for rpc in RPCS:
        try:
            o = rpc_once(rpc, "eth_call", [{"to": to, "data": data}, "latest"])
            if "error" in o or not o.get("result") or o["result"] == "0x": continue
            b = bytes.fromhex(o["result"][2:])
            ln = int.from_bytes(b[32:64], "big")
            return b[64:64+ln].decode(errors="replace")
        except Exception:
            continue
    return "err:RPC"
def block_ts(n):
    o = rpc_once(RPCS[0], "eth_getBlockByNumber", [hex(n), False], 10)
    ts = int(o["result"]["timestamp"], 16)
    return ts, datetime.fromtimestamp(ts, WIB).isoformat(timespec="seconds")

TASKS = {}
def add(tag, key, fn): TASKS[(tag, key)] = fn
for tag in ("ba5c", "ec26"):
    a = CONTRACTS[tag]
    add(tag, "name", lambda a=a: call_str(a, sel("name()")))
    add(tag, "symbol", lambda a=a: call_str(a, sel("symbol()")))
    add(tag, "decimals", lambda a=a: call(a, sel("decimals()")))
    add(tag, "totalSupply", lambda a=a: call(a, sel("totalSupply()")))
    add(tag, "sharesSold", lambda a=a: call(a, sel("sharesSold()")))
    add(tag, "MAX_SHARES", lambda a=a: call(a, sel("MAX_SHARES()")))
    add(tag, "FREE_PER_AGENT", lambda a=a: call(a, sel("FREE_PER_AGENT()")))
    add(tag, "MAX_PER_WALLET", lambda a=a: call(a, sel("MAX_PER_WALLET()")))
    add(tag, "PRICE_PER_SHARE", lambda a=a: call(a, sel("PRICE_PER_SHARE()")))
    add(tag, "TOKENS_PER_SHARE", lambda a=a: call(a, sel("TOKENS_PER_SHARE()")))
    add(tag, "AGENT_ID_REGISTRY", lambda a=a: call(a, sel("AGENT_ID_REGISTRY()")))
    add(tag, "freeUsed_user", lambda a=a: call(a, sel("freeUsed(address)") + enc_addr(USER)))
    add(tag, "isAgent_user", lambda a=a: call(a, sel("isAgent(address)") + enc_addr(USER)))
    add(tag, "quote_user_1", lambda a=a: call(a, sel("quote(address,uint256)") + enc_addr(USER) + enc_u(1)))
    add(tag, "mintedBy_user", lambda a=a: call(a, sel("mintedBy(address)") + enc_addr(USER)))
    add(tag, "balanceOf_user", lambda a=a: call(a, sel("balanceOf(address)") + enc_addr(USER)))
a = CONTRACTS["bac6"]
for key, sig in [("name","name()"),("symbol","symbol()"),("totalMinted","totalMinted()"),
                 ("freeMinted","freeMinted()"),("paidMinted","paidMinted()"),
                 ("FREE_SUPPLY","FREE_SUPPLY()"),("PAID_SUPPLY","PAID_SUPPLY()"),
                 ("MAX_SUPPLY","MAX_SUPPLY()"),("MAX_PER_WALLET","MAX_PER_WALLET()"),
                 ("price","price()"),("paused","paused()"),("owner","owner()"),
                 ("AGENT_REGISTRY","AGENT_REGISTRY()")]:
    add("bac6", key, (lambda s=sig, a=a: call(a, sel(s))))
add("bac6", "mintedBy_user", lambda: call(a, sel("mintedBy(address)") + enc_addr(USER)))
add("bac6", "balanceOf_user", lambda: call(a, sel("balanceOf(address)") + enc_addr(USER)))

out = {"run": TS, "t0_wib": datetime.now(WIB).isoformat(timespec="seconds")}
res = {tag: {"address": CONTRACTS[tag]} for tag in CONTRACTS}
t0 = time.time()
with ThreadPoolExecutor(max_workers=16) as ex:
    futs = {ex.submit(fn): k for k, fn in TASKS.items()}
    for f in as_completed(futs):
        tag, key = futs[f]
        try: res[tag][key] = f.result()
        except Exception as e: res[tag][key] = f"err:{type(e).__name__}"
out["chain"] = res
print("chain reads done in", round(time.time()-t0, 1), "s", flush=True)
for tag in CONTRACTS: print(tag, json.dumps(res[tag]), flush=True)

# ---- first mint via Ankr getLogs (parallel) ----
T0 = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "0"*64
def first_mint(tag):
    addr = CONTRACTS[tag]
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "address": [addr],
            "fromBlock": hex(132090000), "toBlock": "latest",
            "topics": [T0, ZERO], "pageSize": 1000, "decodeLogs": False})
        logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
        ls = sorted(logs, key=lambda l: int(l.get("blockNumber", "0x0"), 16))
        info = {"n_transfer_from_zero": len(ls)}
        if ls:
            first = ls[0]; fb = int(first["blockNumber"], 16)
            ts, dt = block_ts(fb)
            info["first"] = {"block": fb, "tx": first.get("transactionHash"), "ts": ts, "wib": dt,
                             "age_min": round((datetime.now(WIB) - datetime.fromtimestamp(ts, WIB)).total_seconds()/60, 1)}
            info["last_block"] = int(ls[-1]["blockNumber"], 16)
        return tag, info
    except Exception as e:
        return tag, {"error": f"{type(e).__name__}: {e}"}
t0 = time.time()
with ThreadPoolExecutor(max_workers=3) as ex:
    for tag, info in ex.map(first_mint, list(CONTRACTS)):
        out.setdefault("first_mint", {})[tag] = info
        print(tag, "first-mint:", info, flush=True)
print("ankr done in", round(time.time()-t0, 1), "s", flush=True)
json.dump(out, open(f"{BASE}/hot-leg-{TS}-leg3.json", "w"), indent=1)
print("LEG3 DONE", flush=True)
