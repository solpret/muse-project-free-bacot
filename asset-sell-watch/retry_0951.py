#!/usr/bin/env python3
"""Targeted retry for missing reads in run 0951, via alternate endpoint."""
import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
ENDPOINT = "https://bsc-dataseed1.binance.org/"

def sel(sig): return keccak(text=sig).hex()[:8]
def rpc(calls, url=ENDPOINT):
    batch = [{"jsonrpc":"2.0","id":i+1,"method":m,"params":p} for i,(m,p) in enumerate(calls)]
    req = urllib.request.Request(url, data=json.dumps(batch).encode(), headers={"Content-Type":"application/json"})
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=30).read())
    except Exception as e:
        return [None]*len(calls), str(e)
    out=[]
    for r in res:
        if isinstance(r, dict) and (r.get("error") or not r.get("result")): out.append(None)
        elif isinstance(r, dict): out.append(r["result"])
        else: out.append(None)
    return out, None
def call(to, data, url=ENDPOINT):
    r,_ = rpc([("eth_call",[{"to":to,"data":data},"latest"])], url)
    return r[0]
def u256(h):
    try: return int(h,16) if h else 0
    except Exception: return 0

out = {}
gp,_ = rpc([("eth_gasPrice",[])])
out["gas_price_wei"] = u256(gp[0]) if gp[0] else None
out["gas_price_gwei"] = out["gas_price_wei"]/1e9 if out["gas_price_wei"] else None

def pair_of(tok):
    h = call(FACTORY, "0x"+sel("getPair(address,address)")+encode(["address","address"],[tok,WBNB]).hex())
    return ("0x"+h[-40:]) if h and u256(h) else None

def reserves(pair):
    rh = call(pair, "0x"+sel("getReserves()"))
    if not rh: return None
    r0,r1,_ = decode(["uint112","uint112","uint32"], bytes.fromhex(rh[2:]))
    return [str(r0), str(r1)]

# 币安加油 balance + pair
tok = "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f"
bh = call(tok, "0x"+sel("balanceOf(address)")+encode(["address"],[W]).hex())
out["bi_an_jia_you_balance_raw"] = str(u256(bh)) if bh else None
p = pair_of(tok); out["bi_an_jia_you_pair"] = p
if p: out["bi_an_jia_you_reserves"] = reserves(p)
# YYDS pair + reserves + quote
tok2 = "0xd23be069c3c3a7f631af52584a16a9e46bb41da1"
p2 = pair_of(tok2); out["yyds_pair"] = p2
if p2:
    out["yyds_reserves"] = reserves(p2)
    qh = call(ROUTER, "0x"+sel("getAmountsOut(uint256,address[])")+encode(["uint256","address[]"],[177600000000000,[tok2,WBNB]]).hex())
    if qh:
        outs = decode(["uint256[]"], bytes.fromhex(qh[2:]))[0]
        out["yyds_quote_bnb"] = outs[1]/1e18 if len(outs)==2 else None
# KAGENT pair + reserves + launched
tok3 = "0xb34105002B19EF0ce43B59011fE848df5c8B174f"
p3 = pair_of(tok3); out["kagent_pair"] = p3
if p3: out["kagent_reserves"] = reserves(p3)
lh = call(tok3, "0x"+sel("launched()"))
out["kagent_launched_raw"] = lh
if lh:
    try: out["kagent_launched"] = decode(["bool"], bytes.fromhex(lh[2:]))[0]
    except Exception: out["kagent_launched"] = None
print(json.dumps(out, indent=1))
