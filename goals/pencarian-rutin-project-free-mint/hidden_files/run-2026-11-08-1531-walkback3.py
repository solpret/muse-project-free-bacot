#!/usr/bin/env python3
"""REDO walk-back via Ankr ankr_getLogs with ADDRESS filter (read-only).
Method 1 (dataseed eth_getLogs) failed: -32005 limit exceeded on all chunks.
Method 2 (historical eth_call binary search) failed: missing trie node (pruned dataseeds).
Method 3: ankr get_logs(address, topics=[Transfer, zero]) in 2000-block chunks, 132340000 -> fb-1.
Includes Hoopsy as control (expect many pre-window mints -> validates method)."""
import json, datetime, sys, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import get_logs
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def wib(ts):
    return datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
CANDS=[
 ("402","0xd80D0095746999c93AE837B1DE1569d5814405dC",132361002),
 ("Macronyx","0x2E7Aa64BAc710082bb0E84F4BEb7C0cF668CfC29",132361132),
 ("Mindrift","0xD09052d690151702759481Bbcb0eB5Dbdc5f1eAA",132361900),
 ("Lucky Box","0xd08ef372B52C29255fEd7004f59bF41571451894",132361734),
 ("CONTROL-Hoopsy","0xE1a438A132659Fea25AFD7712Ed7F203e62cC420",132361319),
]
out={}
for name,addr,fb in CANDS:
    earliest=None; tot=0; errs=[]; calls=0
    frm=132340000
    while frm<fb:
        to=min(frm+1999,fb-1)
        try:
            body=get_logs(addr,frm,to,topics=[TRANSFER,ZERO]); calls+=1
            logs=(body.get("result",{}) or {}).get("logs",[]) if isinstance(body,dict) else []
            for lg in logs:
                b=int(lg.get("blockNumber","0x0"),16); tot+=1
                if earliest is None or b<earliest: earliest=b
        except Exception as e:
            errs.append(f"{frm}-{to}: {str(e)[:100]}")
        frm=to+1
        time.sleep(0.3)
    r={"first_block_in_window":fb,"mints_before_window":tot,"earliest_mint_block":earliest,"ankr_calls":calls,"errors":errs}
    if earliest:
        try:
            blk=None
            for ep in EPS:
                try: blk=_single(ep,"eth_getBlockByNumber",[hex(earliest),False],8,retries=0); break
                except Exception: continue
            r["earliest_mint_wib"]=wib(int(blk["timestamp"],16))
        except Exception as e: r["earliest_mint_ts_error"]=str(e)[:80]
    print(f"{name} {addr[:10]} mints_before={tot} earliest={earliest} {r.get('earliest_mint_wib','')} calls={calls} errors={len(errs)}",flush=True)
    out[addr]=r
json.dump(out,open("run-2026-11-08-1531-walkback3.json","w"),indent=1)
print("saved run-2026-11-08-1531-walkback3.json",flush=True)
