#!/usr/bin/env python3
import json, sys, time, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def blk():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
def first_mints(C, head, frm=130900000):
    logs=[]; tok=None; pages=0; err=None
    while True:
        params={"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(head),"pageSize":1000,"decodeLogs":False,
                "topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef","0x"+"00"*32],"address":C}
        if tok: params["pageToken"]=tok
        try: body=ankr_post("ankr_getLogs", params, timeout=30)
        except Exception as e: err=str(e)[:200]; break
        res=body.get("result",{}) if isinstance(body,dict) else {}
        got=[l for l in res.get("logs",[]) if l.get("address","").lower()==C.lower()]
        logs.extend(got); tok=res.get("nextPageToken"); pages+=1
        if not tok or pages>=10: break
        time.sleep(1)
    out={"count":len(logs),"err":err,"pages":pages}
    if logs:
        blks=sorted(int(l["blockNumber"],16) for l in logs)
        minters=set(l.get("topics",[])[2] for l in logs if len(l.get("topics",[]))>=3)
        out.update({"first_block":blks[0],"last_block":blks[-1],"distinct_minters":len(minters)})
        for ep in EPS:
            try:
                b=_single(ep,"eth_getBlockByNumber",[hex(blks[0]),False],8,retries=0); ts=int(b["timestamp"],16)
                out["first_ts"]=ts; out["first_wib"]=datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB"); break
            except Exception: pass
    return out
head=blk(); print("head", head)
out={"head": head}
for tag,C in [("4fc3","0x4fc39B2c1620f2561d01232f87E25581CFD72A51"),("C9c0De","0xC9c0De69ea301cA9479149554bf325aE3342584B"),("E4cA7A","0xE4cA7AaA82253717C0d897C10d58D59821631509"),("46c181","0x46c1815082ccf1273e3c07548ef2004046Bb7Fc0"),("b2d236","0xb2d236EC0473792eC6727e5bf41084Df3eA0137F"),("bd297c","0xbd297cb5158F4DcA02C336A59556FDBfa6609A70"),("D8F2d1","0xD8F2d1f5158135232f69Fe0605A406A51d86Ce6B")]:
    r=first_mints(C, head); out[tag]=r; print(tag, json.dumps(r))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0731-firstmints2.json","w"), indent=1)
