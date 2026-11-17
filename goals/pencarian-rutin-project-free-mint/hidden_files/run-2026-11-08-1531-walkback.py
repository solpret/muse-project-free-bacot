#!/usr/bin/env python3
"""Walk-back first-mint check for 4 agent-shaped non-discarded candidates (read-only).
eth_getLogs with address filter, chunked, from 132340000 to first_block-1.
Plus extra probes: 402 FREE_CAP/FREE_PER_WALLET/freeCount(user); Lucky Box freeFor/freeLeft(user)."""
import json, datetime
import sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak
EPS = ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
def rpc(m,p,timeout=10):
    last=None
    for ep in EPS:
        try: return _single(ep,m,p,timeout,retries=0)
        except Exception as e: last=e
    raise last
def sel(sig): return "0x"+keccak(sig.encode()).hex()[:8]
def call(addr,data):
    return rpc("eth_call",[{"to":addr,"data":data},"latest"])
def u256(h):
    if not isinstance(h,str) or not h.startswith("0x") or len(h)<66: return None
    return int(h[-64:],16)
def enc_addr(a): return "0x"+"00"*12+a[2:].lower()
def wib(ts):
    return datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
CANDS=[
 ("402","0xd80D0095746999c93AE837B1DE1569d5814405dC",132361002),
 ("Macronyx","0x2E7Aa64BAc710082bb0E84F4BEb7C0cF668CfC29",132361132),
 ("Mindrift","0xD09052d690151702759481Bbcb0eB5Dbdc5f1eAA",132361900),
 ("Lucky Box","0xd08ef372B52C29255fEd7004f59bF41571451894",132361734),
]
out={}
for name,addr,fb in CANDS:
    r={"first_block_in_window":fb}
    earliest=None; total_before=0
    frm=132340000
    while frm<fb:
        to=min(frm+1999,fb-1)
        try:
            logs=rpc("eth_getLogs",[{"fromBlock":hex(frm),"toBlock":hex(to),"address":addr,"topics":[TRANSFER,ZERO]}],timeout=15)
            for lg in (logs or []):
                b=int(lg.get("blockNumber","0x0"),16)
                total_before+=1
                if earliest is None or b<earliest: earliest=b
        except Exception as e:
            r.setdefault("walkback_errors",[]).append(f"{frm}-{to}: {str(e)[:100]}")
        frm=to+1
    r["mints_before_window"]=total_before
    r["earliest_mint_block"]=earliest
    if earliest:
        try:
            blk=rpc("eth_getBlockByNumber",[hex(earliest),False],timeout=8)
            ts=int(blk["timestamp"],16); r["earliest_mint_wib"]=wib(ts)
        except Exception as e: r["earliest_mint_ts_error"]=str(e)[:80]
    print(f"{name} {addr} mints_before_window={total_before} earliest={earliest} {r.get('earliest_mint_wib','')}",flush=True)
    out[addr]=r
# extra probes for 402
a402="0xd80D0095746999c93AE837B1DE1569d5814405dC"
for nm,sig in [("FREE_CAP","FREE_CAP()"),("FREE_PER_WALLET","FREE_PER_WALLET()"),("freeCount_total","freeCount()")]:
    try:
        v=u256(call(a402,sel(sig))); out[a402][nm]=v; print("402",nm,v,flush=True)
    except Exception as e: out[a402][nm+"_error"]=str(e)[:80]; print("402",nm,"ERROR",str(e)[:80],flush=True)
for nm,sig in [("freeCount_user","freeCount(address)"),("canFreeMint_user","canFreeMint(address)")]:
    try:
        v=u256(call(a402,sel(sig)+enc_addr(USER)[2:])); out[a402][nm]=v; print("402",nm,v,flush=True)
    except Exception as e: out[a402][nm+"_error"]=str(e)[:80]; print("402",nm,"ERROR",str(e)[:80],flush=True)
# extra probes for Lucky Box (free views take address)
alb="0xd08ef372B52C29255fEd7004f59bF41571451894"
for nm,sig in [("freeFor_user","freeFor(address)"),("freeLeft_user","freeLeft(address)"),("freeUsed_user2","freeUsed(address)")]:
    try:
        v=u256(call(alb,sel(sig)+enc_addr(USER)[2:])); out[alb][nm]=v; print("LuckyBox",nm,v,flush=True)
    except Exception as e: out[alb][nm+"_error"]=str(e)[:80]; print("LuckyBox",nm,"ERROR",str(e)[:80],flush=True)
for nm,sig in [("freeLeft_noarg","freeLeft()"),("freeFor_noarg","freeFor()")]:
    try:
        v=u256(call(alb,sel(sig))); out[alb][nm]=v; print("LuckyBox",nm,v,flush=True)
    except Exception as e: out[alb][nm+"_error"]=str(e)[:80]; print("LuckyBox",nm,"ERROR",str(e)[:80],flush=True)
json.dump(out,open("run-2026-11-08-1531-walkback.json","w"),indent=1)
print("saved run-2026-11-08-1531-walkback.json",flush=True)
