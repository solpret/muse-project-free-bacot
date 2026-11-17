#!/usr/bin/env python3
"""REDO walk-back via binary search on historical supply (read-only).
Method 1 failed: eth_getLogs 2000-block chunks -> -32005 limit exceeded on every chunk
(recorded in run-2026-11-08-1531-walkback.json walkback_errors; the '0 mints' was NO successful read).
Binary search: supply(block) for totalMinted (402) / totalSupply (others); lo=132300000 anchor."""
import json, datetime, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
def rpc(m,p,timeout=12):
    last=None
    for ep in EPS:
        try: return _single(ep,m,p,timeout,retries=0)
        except Exception as e: last=e
    raise last
def sel(s): return "0x"+keccak(s.encode()).hex()[:8]
def u256(h):
    if not isinstance(h,str) or not h.startswith("0x") or len(h)<66: return None
    return int(h[-64:],16)
def wib(ts):
    return datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
CANDS=[
 ("402","0xd80D0095746999c93AE837B1DE1569d5814405dC","totalMinted()"),
 ("Macronyx","0x2E7Aa64BAc710082bb0E84F4BEb7C0cF668CfC29","totalSupply()"),
 ("Mindrift","0xD09052d690151702759481Bbcb0eB5Dbdc5f1eAA","totalSupply()"),
 ("Lucky Box","0xd08ef372B52C29255fEd7004f59bF41571451894","totalSupply()"),
]
LO=132300000
out={}
for name,addr,sig in CANDS:
    r={"supply_fn":sig,"anchor_lo":LO}
    def supply_at(b):
        return u256(rpc("eth_call",[{"to":addr,"data":sel(sig)},hex(b)],timeout=12))
    try:
        s_lo=supply_at(LO); r["supply_at_lo"]=s_lo
        print(f"{name}: supply@{LO}={s_lo}",flush=True)
    except Exception as e:
        r["anchor_error"]=str(e)[:120]; print(f"{name}: anchor ERROR {str(e)[:120]}",flush=True); out[addr]=r; continue
    if s_lo is None:
        r["note"]="supply view returns None at anchor (unparseable/revert) - first-mint UNVERIFIED by this method"
        print(f"{name}: anchor None - UNVERIFIED",flush=True); out[addr]=r; continue
    if s_lo>0:
        r["note"]=f"supply already >0 at {LO} - first mint BEFORE anchor (older than ~5h before window); age still needs lower bracket"
        print(f"{name}: supply>0 at anchor - first mint before {LO}",flush=True); out[addr]=r; continue
    # binary search first block with supply>0 in (LO, latest]
    latest=int(rpc("eth_blockNumber",[],timeout=12),16)
    lo,hi=LO,latest; calls=1
    while hi-lo>1:
        mid=(lo+hi)//2
        s=supply_at(mid); calls+=1
        if s is None: r.setdefault("search_none_blocks",[]).append(mid); hi=mid; continue
        if s>0: hi=mid
        else: lo=mid
    r["first_mint_block"]=hi; r["calls"]=calls
    try:
        blk=rpc("eth_getBlockByNumber",[hex(hi),False],timeout=10)
        ts=int(blk["timestamp"],16); r["first_mint_wib"]=wib(ts)
    except Exception as e: r["first_mint_ts_error"]=str(e)[:80]
    # fresh latest readings
    try: r["supply_latest"]=supply_at(latest)
    except Exception as e: r["supply_latest_error"]=str(e)[:80]
    print(f"{name}: first_mint_block={hi} {r.get('first_mint_wib','')} supply_latest={r.get('supply_latest')} calls={calls}",flush=True)
    out[addr]=r
json.dump(out,open("run-2026-11-08-1531-walkback2.json","w"),indent=1)
print("saved run-2026-11-08-1531-walkback2.json",flush=True)
