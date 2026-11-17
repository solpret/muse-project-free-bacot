#!/usr/bin/env python3
"""Retry via urllib across dataseeds (run 2026-11-16 02:51 WIB). Read-only."""
import json, urllib.request, urllib.error
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
ENDPOINTS = [
    "https://bsc-dataseed.binance.org/",
    "https://bsc-dataseed1.bnbchain.org/",
    "https://bsc-dataseed2.bnbchain.org/",
    "https://bsc-dataseed3.bnbchain.org/",
    "https://bsc-dataseed4.bnbchain.org/",
    "https://bsc-dataseed-public.bnbchain.org/",
    "https://bsc-rpc.publicnode.com/",
    "https://bsc-dataseed1.defibit.io/",
]

def sel(sig):
    return keccak(text=sig).hex()[:8]

def rpc(method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    last_err = None
    for url in ENDPOINTS:
        try:
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            r = json.loads(urllib.request.urlopen(req, timeout=20).read())
            if isinstance(r, dict) and r.get("result") is not None:
                return r["result"], url
            last_err = f"{url}: {r.get('error')}"
        except Exception as e:
            last_err = f"{url}: {e}"
    return None, last_err

def call(to, data):
    return rpc("eth_call", [{"to": to, "data": data}, "latest"])

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

TOK = {
 "BNBbaby": "0xd0079025a9bb66a7a1de991de2e4326faba35729",
 "WW3": "0xf62628D99B28535ee593Ab5D6dFE7D914f5edca0",
 "LUCKY777": "0xc6D4ec8CB889aFBa9f251606001457644E260f7D",
 "YYDS": "0xd23be069c3c3a7f631af52584a16a9e46bb41da1",
 "币安加油": "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f",
 "JINMA": "0xe4517E6718b24D5725956ac7A90686592a7b1539",
 "CHEEMSA": "0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2",
}
RECORDED_PAIR = {
 "币安加油": "0xc939e2b49eea548c4539e45b4e355c2b2aa464d6",
 "JINMA": "0xaa91fd1b1fc70888f5df17784720b752472e99da",
 "LUCKY777": "0x81afde1cddf0d277580b8e524361e0a7ea2983c6",
 "YYDS": "0xd15c928b7b777cac7d613fe840c6ec3de8e4edda",
}
out = {}
gp, gp_src = rpc("eth_gasPrice", [])
out["gasPrice"] = gp; out["gasPrice_src"] = gp_src
if gp:
    print(f"GAS: {u256(gp)/1e9:.4f} gwei via {gp_src} | 300k est {u256(gp)*300000/1e18:.8f} BNB | 2x {u256(gp)*600000/1e18:.8f} BNB")
else:
    print("GAS FAILED:", gp_src)

for sym, tok in TOK.items():
    b, src = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
    out[f"bal:{sym}"] = b
    print(f"BAL {sym}: {u256(b)/1e18 if b else b} (via {src})")

for sym in ["币安加油", "JINMA", "LUCKY777", "YYDS"]:
    p, src = call(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [TOK[sym], WBNB]).hex())
    out[f"pair:{sym}"] = p
    print(f"PAIR {sym}: {p} recorded={RECORDED_PAIR[sym]} (via {src})")

for sym, pair in RECORDED_PAIR.items():
    r, src = call(pair, "0x" + sel("getReserves()"))
    out[f"reserves:{sym}"] = r
    if r and r.startswith("0x"):
        try:
            r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(r[2:]))
            print(f"RESERVES {sym} ({pair}): {r0} / {r1}")
        except Exception as e:
            print(f"RESERVES {sym} decode err: {e} raw={r}")
    else:
        print(f"RESERVES {sym}: {r} (via {src})")

q, src = call(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [177600000000000, [TOK["YYDS"], WBNB]]).hex())
out["quote:YYDS"] = q
if q and q.startswith("0x"):
    try:
        outs = decode(["uint256[]"], bytes.fromhex(q[2:]))[0]
        print(f"QUOTE YYDS: {outs[1]/1e18:.10f} BNB raw={outs[1]}")
    except Exception as e:
        print("QUOTE YYDS decode err:", e, q)
else:
    print("QUOTE YYDS:", q, "via", src)

for fn in ["tradingOpen()", "launched()"]:
    v, src = call(TOK["CHEEMSA"], "0x" + sel(fn))
    out[f"cheemsa:{fn}"] = v
    print(f"CHEEMSA {fn}: {v} (via {src})")

json.dump(out, open("/home/hatch/workspace/asset-sell-watch/pending_check_retry_0251_nov16_stdout.json", "w"), indent=1)
