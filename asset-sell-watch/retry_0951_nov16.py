#!/usr/bin/env python3
"""Retry balance+pair reads for entries that failed RPC in run 0951, using fallback endpoints."""
import json, urllib.request
from eth_abi import encode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
ENDPOINTS = ["https://bsc-dataseed1.defibit.io/", "https://bsc-dataseed1.ninicoin.io/",
             "https://bsc-dataseed.bnbchain.org/", "https://rpc.ankr.com/bsc"]

def sel(sig): return keccak(text=sig).hex()[:8]

def rpc(url, calls):
    batch = [{"jsonrpc": "2.0", "id": i+1, "method": m, "params": p} for i, (m, p) in enumerate(calls)]
    req = urllib.request.Request(url, data=json.dumps(batch).encode(), headers={"Content-Type": "application/json"})
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=20).read())
    except Exception as e:
        return [None]*len(calls), str(e)
    out = []
    for r in res:
        if isinstance(r, dict) and (r.get("error") or not r.get("result")): out.append(None)
        elif isinstance(r, dict): out.append(r["result"])
        else: out.append(None)
    return out, None

def call_multi(to, data):
    for url in ENDPOINTS:
        r, _ = rpc(url, [("eth_call", [{"to": to, "data": data}, "latest"])])
        if r[0]: return r[0], url
    return None, None

def u256(h):
    try: return int(h, 16) if h else 0
    except Exception: return 0

data = json.load(open("pending-swaps.json"))
prev = json.load(open("pending_check_0951_nov16_stdout.json"))
failed = {e["symbol"] for e in prev["entries"] if e["status"] == "rpc_failed_balance"}
out = {}
for e in data["entries"]:
    if e["symbol"] not in failed: continue
    tok = e["token"]
    bal_h, url = call_multi(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
    item = {"symbol": e["symbol"], "token": tok, "rpc_url": url}
    if bal_h is None:
        item["status"] = "rpc_failed_balance"; out[e["symbol"]] = item; continue
    bal = u256(bal_h); dec = 18
    item["balance_raw"] = str(bal); item["balance_human"] = bal / 1e18
    if bal == 0:
        item["status"] = "empty"; out[e["symbol"]] = item; continue
    pair_h, url2 = call_multi(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address","address"], [tok, WBNB]).hex())
    pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
    item["pair_wbnb"] = pair
    item["status"] = "no_pair" if not pair else "pair_exists"
    if pair:
        res_h, _ = call_multi(pair, "0x" + sel("getReserves()"))
        if res_h:
            from eth_abi import decode
            try:
                r0, r1, _ = decode(["uint112","uint112","uint32"], bytes.fromhex(res_h[2:]))
                item["reserves"] = [str(r0), str(r1)]
                item["status"] = "pair_empty" if (r0==0 or r1==0) else "pair_live"
            except Exception as ex: item["reserves_error"] = str(ex)
    out[e["symbol"]] = item
print(json.dumps(out, indent=1, ensure_ascii=False))
