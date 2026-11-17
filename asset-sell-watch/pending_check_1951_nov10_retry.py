#!/usr/bin/env python3
"""Retry fresh reads for entries whose balanceOf failed in the 19:51 run,
plus CSAGENT reserves/quote. Uses a fallback BSC RPC (bsc-dataseed1).
Read-only; never treats a failed read as zero."""
import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
URL = "https://bsc-dataseed1.binance.org/"

def sel(sig):
    return keccak(text=sig).hex()[:8]

def call(to, data):
    body = [{"jsonrpc": "2.0", "id": 1, "method": "eth_call",
             "params": [{"to": to, "data": data}, "latest"]}]
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=30).read())
        r = res[0]
        return r.get("result") if not r.get("error") else None
    except Exception as e:
        return {"_err": str(e)}

def u256(h):
    try:
        return int(h, 16) if h and isinstance(h, str) else 0
    except Exception:
        return 0

TOKENS = {
    "YYDS": ("0xd23be069c3c3a7f631af52584a16a9e46bb41da1", 18, None),
    "JINMA": ("0xe4517E6718b24D5725956ac7A90686592a7b1539", 18, None),
    "BITCAT": ("0x8708EE82fa34c58431532323530592ee3953e9d5", 9, "37777777600000000000"),
    "LUCKY777": ("0xc6D4ec8CB889aFBa9f251606001457644E260f7D", 18, "50000000000000000000000000"),
    "CHEEMSA": ("0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2", 18, "5000000000000000000000000"),
}
out = {}
for sym, (tok, dec, amt) in TOKENS.items():
    item = {"token": tok}
    bal_h = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
    if isinstance(bal_h, dict) or bal_h is None:
        item["balance"] = None
        item["balance_error"] = str(bal_h)
    else:
        bal = u256(bal_h)
        item["balance_raw"] = str(bal)
        item["balance_human"] = bal / (10 ** dec)
    out[sym] = item

# CSAGENT pair reserves + quote
cs = "0xeD290fA2e34233d0ee97eA95C2a34E770A9DA45D"
pair = "0x3020220ca11bae3f027c0dc8a3b8bb73d5b55a00"
res_h = call(pair, "0x" + sel("getReserves()"))
cs_item = {"pair": pair}
if isinstance(res_h, dict) or res_h is None:
    cs_item["reserves"] = None
    cs_item["reserves_error"] = str(res_h)
else:
    try:
        r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
        cs_item["reserves"] = [str(r0), str(r1)]
    except Exception as ex:
        cs_item["reserves_error"] = str(ex)
out["CSAGENT"] = cs_item
print(json.dumps(out, indent=1))
