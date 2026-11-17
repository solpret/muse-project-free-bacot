#!/usr/bin/env python3
"""Hot-leg 0954 leg-3: verify the 3 S1 sale-shape contracts first seen 09:36 WIB
(ba5c, bac6, ec26) — on-chain state, user slot, first-mint launch age. Read-only."""
import json, sys, time, urllib.request
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-0954"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
WIB = timezone(timedelta(hours=7))
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed.binance.org",
        "https://bsc-dataseed1.defibit.io"]
CONTRACTS = {
    "ba5c": "0xba5cde0ceea8704b8944deb51228ca59a7bd9cf0",
    "bac6": "0xbac6b6de36a54b2815c02ad3cc5e6551e306aa90",
    "ec26": "0xec266bdd979b19d8a2f1266ef0610b4791dbd24b",
}
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0"*24 + a[2:].lower()
def enc_u(n): return format(n, "064x")
def rpc_call(method, params, timeout=5):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    for rpc in RPCS:
        for _ in range(2):
            try:
                req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    o = json.load(r)
                if "error" in o: return None
                return o.get("result")
            except Exception:
                time.sleep(0.2)
    return "err:URLError"
def call(to, data):
    v = rpc_call("eth_call", [{"to": to, "data": data}, "latest"])
    if v is None or v == "0x" or (isinstance(v, str) and v.startswith("err:")): return v
    try: return int(v, 16)
    except Exception: return v
def call_str(to, data):
    v = rpc_call("eth_call", [{"to": to, "data": data}, "latest"])
    if not v or v == "0x" or (isinstance(v, str) and v.startswith("err:")): return v
    try:
        b = bytes.fromhex(v[2:])
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception: return v
def block_ts(n):
    req = urllib.request.Request("https://bsc-dataseed1.bnbchain.org",
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                         "params": [hex(n), False]}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        b = json.load(r)
    ts = int(b["result"]["timestamp"], 16)
    return ts, datetime.fromtimestamp(ts, WIB).isoformat(timespec="seconds")

out = {"run": TS, "t0_wib": datetime.now(WIB).isoformat(timespec="seconds")}
for tag, addr in CONTRACTS.items():
    d = json.load(open(f"{BASE}/hot-leg-0954-abi-{tag}.json"))
    abi = d.get("abi") or []
    sigs = {}
    for f in abi:
        if f.get("type") == "function":
            ins = ",".join(i.get("type", "") for i in f.get("inputs", []))
            sigs[f["name"]] = f"{f['name']}({ins})"
    out[tag] = {"address": addr, "match": d.get("match"), "sigs": sigs}
    print(tag, addr, "match", d.get("match"), flush=True)
    for name, s in sorted(sigs.items()):
        print("   ", s, flush=True)

# ---- on-chain reads ----
def read_erc20_share(tag, addr):
    r = {}
    r["name"] = call_str(addr, sel("name()"))
    r["symbol"] = call_str(addr, sel("symbol()"))
    r["decimals"] = call(addr, sel("decimals()"))
    r["totalSupply"] = call(addr, sel("totalSupply()"))
    r["sharesSold"] = call(addr, sel("sharesSold()"))
    r["MAX_SHARES"] = call(addr, sel("MAX_SHARES()"))
    r["FREE_PER_AGENT"] = call(addr, sel("FREE_PER_AGENT()"))
    r["MAX_PER_WALLET"] = call(addr, sel("MAX_PER_WALLET()"))
    r["MAX_PER_TX"] = call(addr, sel("MAX_PER_TX()"))
    r["PRICE_PER_SHARE"] = call(addr, sel("PRICE_PER_SHARE()"))
    r["TOKENS_PER_SHARE"] = call(addr, sel("TOKENS_PER_SHARE()"))
    r["AGENT_ID_REGISTRY"] = call(addr, sel("AGENT_ID_REGISTRY()"))
    r["treasury"] = call(addr, sel("treasury()"))
    r["freeUsed_user"] = call(addr, sel("freeUsed(address)") + enc_addr(USER))
    r["isAgent_user"] = call(addr, sel("isAgent(address)") + enc_addr(USER))
    r["quote_user_1"] = call(addr, sel("quote(address,uint256)") + enc_addr(USER) + enc_u(1))
    r["mintedBy_user"] = call(addr, sel("mintedBy(address)") + enc_addr(USER))
    r["balanceOf_user"] = call(addr, sel("balanceOf(address)") + enc_addr(USER))
    return r
def read_nft(tag, addr):
    r = {}
    r["name"] = call_str(addr, sel("name()"))
    r["symbol"] = call_str(addr, sel("symbol()"))
    r["totalMinted"] = call(addr, sel("totalMinted()"))
    r["freeMinted"] = call(addr, sel("freeMinted()"))
    r["paidMinted"] = call(addr, sel("paidMinted()"))
    r["FREE_SUPPLY"] = call(addr, sel("FREE_SUPPLY()"))
    r["PAID_SUPPLY"] = call(addr, sel("PAID_SUPPLY()"))
    r["MAX_SUPPLY"] = call(addr, sel("MAX_SUPPLY()"))
    r["MAX_PER_WALLET"] = call(addr, sel("MAX_PER_WALLET()"))
    r["price"] = call(addr, sel("price()"))
    r["paused"] = call(addr, sel("paused()"))
    r["owner"] = call(addr, sel("owner()"))
    r["AGENT_REGISTRY"] = call(addr, sel("AGENT_REGISTRY()"))
    r["mintedBy_user"] = call(addr, sel("mintedBy(address)") + enc_addr(USER))
    r["balanceOf_user"] = call(addr, sel("balanceOf(address)") + enc_addr(USER))
    r["tokenURI_0"] = call(addr, sel("tokenURI(uint256)") + enc_u(0))
    return r
out["ba5c"]["chain"] = read_erc20_share("ba5c", CONTRACTS["ba5c"])
out["ec26"]["chain"] = read_erc20_share("ec26", CONTRACTS["ec26"])
out["bac6"]["chain"] = read_nft("bac6", CONTRACTS["bac6"])
for tag in ("ba5c", "ec26", "bac6"):
    print(tag, json.dumps(out[tag]["chain"]), flush=True)

# ---- first mint via Ankr getLogs: Transfer from zero address ----
T0 = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "0"*64
for tag, addr in CONTRACTS.items():
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "address": [addr],
            "fromBlock": hex(132090000), "toBlock": "latest",
            "topics": [T0, ZERO], "pageSize": 1000, "decodeLogs": False})
        logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
        ls = sorted(logs, key=lambda l: int(l.get("blockNumber", "0x0"), 16))
        info = {"n_transfer_from_zero": len(ls)}
        if ls:
            first = ls[0]
            fb = int(first["blockNumber"], 16)
            ts, dt = block_ts(fb)
            info["first"] = {"block": fb, "tx": first.get("transactionHash"), "ts": ts, "wib": dt,
                             "age_min": round((datetime.now(WIB) - datetime.fromtimestamp(ts, WIB)).total_seconds()/60, 1)}
            info["last_block"] = int(ls[-1]["blockNumber"], 16)
        out[tag]["first_mint"] = info
        print(tag, "first-mint:", info, flush=True)
    except Exception as e:
        out[tag]["first_mint"] = {"error": f"{type(e).__name__}: {e}"}
        print(tag, "first-mint ERR:", e, flush=True)

out["duration_note"] = "leg-3 only"
json.dump(out, open(f"{BASE}/hot-leg-{TS}-leg3.json", "w"), indent=1)
print("LEG3 DONE", flush=True)
