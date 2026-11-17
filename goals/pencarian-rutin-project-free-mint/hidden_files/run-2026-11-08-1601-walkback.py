#!/usr/bin/env python3
"""Walk-back + extra probes for the 2 genuinely-new candidates (read-only)."""
import sys, time, json, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from ankr import ankr_post
from fast_rpc import _single
from eth_hash.auto import keccak
EPS = ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
def rpc(m,p,t=8):
    last=None
    for ep in EPS:
        try: return _single(ep,m,p,t,retries=0)
        except Exception as e: last=e
    raise last
def sel(s): return "0x"+keccak(s.encode()).hex()[:8]
def call(a,data,t=8): return rpc("eth_call",[{"to":a,"data":data},"latest"],t)
def u256(h):
    if isinstance(h,str) and h.startswith("0x") and len(h)>=66: return int(h[-64:],16)
    return None
def enc_addr(a): return "0x"+"00"*12+a[2:].lower()
TARGETS={
 "0xB1f4f9c3Bb8533064fFec75dFab1Be88833b3a32": 132369105,
 "0x2ACc978c344F7A8a9b4FE6B1D57E753712Fb35B2": 132368619,
}
out={}
for addr,fblk in TARGETS.items():
    r={"first_block":fblk}
    # walk-back: Transfer mints (from zero) for this address, 132320000..fblk-1 in 10k chunks
    total=0; earliest=None
    frm=132320000
    while frm < fblk:
        to=min(frm+9999, fblk-1)
        try:
            res=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(to),"address":addr,"topics":[TRANSFER,ZERO],"pageSize":1000},timeout=55)
            logs=res.get("result",{}).get("logs",[]) if isinstance(res,dict) else []
            total+=len(logs)
            for lg in logs:
                b=int(lg.get("blockNumber","0x0"),16)
                earliest=b if earliest is None else min(earliest,b)
            print(f"  walkback {addr[:10]} {frm}-{to}: {len(logs)} logs",flush=True)
        except Exception as e:
            r.setdefault("walkback_errors",[]).append(f"{frm}-{to}: {e}")
            print(f"  walkback {addr[:10]} {frm}-{to}: ERROR {e}",flush=True)
        frm=to+1
    r["walkback_mints_before_first_block"]=total
    r["walkback_earliest_block"]=earliest
    if earliest:
        blk=rpc("eth_getBlockByNumber",[hex(earliest),False],timeout=8)
        ts=int(blk["timestamp"],16)
        r["walkback_earliest_wib"]=datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
    print(f"== {addr} walkback total={total} earliest={earliest}",flush=True)
    # extra probes
    probes={}
    for name,sig in [("mintStart","mintStart()"),("claimedFree_user","claimedFree(address)"),("paidMinted","paidMinted()"),("currentPrice","currentPrice()"),("spotsLeft","spotsLeft()"),("nextTokenId","nextTokenId()"),("MAX_PER_WALLET","MAX_PER_WALLET()"),("isAgent_user","isAgent(address)")]:
        try:
            data=sel(sig)
            if "(address)" in sig: data+=enc_addr(USER)[2:]
            v=u256(call(addr,data))
            probes[name]=v
            print(f"  {name}: {v}",flush=True)
        except Exception as e:
            probes[name+"_error"]=str(e)[:80]
            print(f"  {name}: ERROR {str(e)[:80]}",flush=True)
    r["probes"]=probes
    # mintStart -> WIB
    ms=probes.get("mintStart")
    if isinstance(ms,int) and ms>0:
        r["mintStart_wib"]=datetime.datetime.fromtimestamp(ms,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
    out[addr]=r
json.dump(out,open("run-2026-11-08-1601-walkback.json","w"),indent=1)
print("saved run-2026-11-08-1601-walkback.json",flush=True)
