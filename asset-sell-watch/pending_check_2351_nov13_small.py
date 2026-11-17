#!/usr/bin/env python3
"""Attempt 4 — small sequential batches, dataseed1 primary, dataseed2/4 fallback."""
import json, time, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
def sel(sig): return keccak(text=sig).hex()[:8]
URLS = ["https://bsc-dataseed1.binance.org/", "https://bsc-dataseed2.binance.org/",
        "https://bsc-dataseed4.binance.org/", "https://bsc-dataseed3.binance.org/"]

def post(url, payload, timeout=20):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())

def batch(calls, tries=3):
    """calls: list of (method, params). Returns list of results (None on failure)."""
    out = [None]*len(calls)
    for start in range(0, len(calls), 6):
        chunk = calls[start:start+6]
        payload = [{"jsonrpc":"2.0","id":i+1,"method":m,"params":p} for i,(m,p) in enumerate(chunk)]
        got = None
        for attempt in range(tries):
            for url in URLS:
                try:
                    res = post(url, payload)
                    if isinstance(res, list):
                        got = res; break
                except Exception:
                    continue
            if got is not None: break
            time.sleep(2)
        if got:
            by_id = {r.get("id"): r.get("result") for r in got if isinstance(r, dict) and not r.get("error")}
            for i in range(len(chunk)):
                out[start+i] = by_id.get(i+1)
    return out

def u256(h):
    try: return int(h, 16) if h else 0
    except Exception: return 0

with open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json") as f:
    ENTRIES = json.load(f)["entries"]
KNOWN_PAIR = {"YYDS":"0xD15c928B7b777CaC7d613FE840C6eC3dE8e4EdDA",
 "币安加油":"0xc939e2b49eea548c4539e45b4e355c2b2aa464d6",
 "JINMA":"0xaa91fd1b1fc70888f5df17784720b752472e99da",
 "LUCKY777":"0x81afde1cddf0d277580b8e524361e0a7ea2983c6"}

calls = [("eth_gasPrice", [])]
for e in ENTRIES:
    calls.append(("eth_call", [{"to": e["token"], "data": "0x"+sel("balanceOf(address)")+encode(["address"],[W]).hex()}, "latest"]))
for e in ENTRIES:
    calls.append(("eth_call", [{"to": FACTORY, "data": "0x"+sel("getPair(address,address)")+encode(["address","address"],[e["token"],WBNB]).hex()}, "latest"]))
res = batch(calls)
gas = u256(res[0]) if res and res[0] else None
gas_est = gas*300000/1e18 if gas else None
n = len(ENTRIES)
out = {"run":"pending-coin-swap-watch 2026-11-13 23:51 WIB (attempt 2 (retry), small batches dataseed)",
 "wallet":W, "gas_price_gwei": gas/1e9 if gas else None, "gas_est_300k_bnb": gas_est,
 "gas_2x_threshold_bnb": 2*gas_est if gas_est else None, "entries":[]}
items=[]
for i,e in enumerate(ENTRIES):
    item={"symbol":e["symbol"],"token":e["token"]}
    bal_h=res[1+i]
    if bal_h is None:
        item["status"]="rpc_failed_balance"; items.append(item); continue
    bal=u256(bal_h)
    item["balance_raw"]=str(bal); item["balance_human"]=bal/10**e.get("decimals",18)
    if bal==0:
        item["status"]="empty"; items.append(item); continue
    pair_h=res[1+n+i]
    pair=("0x"+pair_h[-40:]) if pair_h and u256(pair_h) else None
    if not pair: pair=KNOWN_PAIR.get(e["symbol"])
    item["pair_wbnb"]=pair
    if not pair:
        item["status"]="no_pair"; items.append(item); continue
    items.append(item)
need_res=[it for it in items if it.get("pair_wbnb") and it.get("status") is None]
if need_res:
    rcalls=[("eth_call",[{"to":it["pair_wbnb"],"data":"0x"+sel("getReserves()")},"latest"]) for it in need_res]
    rres=batch(rcalls)
    for it,rh in zip(need_res,rres):
        if rh:
            try:
                r0,r1,_=decode(["uint112","uint112","uint32"],bytes.fromhex(rh[2:]))
                it["reserves"]=[str(r0),str(r1)]
                if r0==0 or r1==0: it["status"]="pair_empty"
            except Exception as ex: it["reserves_error"]=str(ex)
        else: it["status"]="rpc_failed_reserves"
need_q=[it for it in items if it.get("status") is None and it.get("reserves")]
if need_q:
    qcalls=[]
    for it in need_q:
        e=next(x for x in ENTRIES if x["symbol"]==it["symbol"])
        amt=int(e["amount_to_sell_raw"]) if e.get("amount_to_sell_raw") else int(it["balance_raw"])
        it["sell_amount_raw"]=str(amt)
        qcalls.append(("eth_call",[{"to":ROUTER,"data":"0x"+sel("getAmountsOut(uint256,address[])")+encode(["uint256","address[]"],[amt,[e["token"],WBNB]]).hex()},"latest"]))
    qres=batch(qcalls)
    for it,qh in zip(need_q,qres):
        if qh:
            try:
                outs=decode(["uint256[]"],bytes.fromhex(qh[2:]))[0]
                it["quote_bnb"]=outs[1]/1e18 if len(outs)==2 else None
            except Exception as ex: it["quote_error"]=str(ex)
        if it.get("quote_bnb") is not None:
            it["quote_ge_2x_gas"]=(gas_est is not None and it["quote_bnb"]>=2*gas_est)
            it["status"]="executable_candidate" if it["quote_ge_2x_gas"] else "quote_dust"
        else: it["status"]="no_quote"
out["entries"]=items
# sale-state probes (best effort, single calls)
def try_call(addr, sig):
    try:
        r=post(URLS[0], {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":"0x"+sel(sig)},"latest"]}, timeout=20)
        return u256(r.get("result")) if isinstance(r,dict) else None
    except Exception: return None
out["sale_state_checks"]={
 "CHEEMSA_tradingOpen": try_call("0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2","tradingOpen()"),
 "LUCKY777_launched": try_call("0x3849159784aa47Fe76117103904204D9f5D153E7","launched()"),
 "JINMA_launched": try_call("0x8553e7033C06fC69B7508d58507b75242cF86EC4","launched()"),
 "PACTURE_launched": try_call("0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9","launched()"),
}
print(json.dumps(out, indent=1))
