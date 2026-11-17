#!/usr/bin/env python3
import json, sys, time, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from Crypto.Hash import keccak
from ankr import ankr_post
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(to,data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0)
        except Exception as e: err=str(e)[:100]
    return "ERR:"+err
def iv(v):
    try: return int(v,16)
    except Exception: return None
def txt(v):
    try:
        b=bytes.fromhex(v[2:])
        # string ABI: offset, len, data
        ln=int.from_bytes(b[32:64],"big")
        return b[64:64+ln].decode(errors="ignore")
    except Exception: return None
TARGETS={
 "0x0982BEbB146caa4d48b6BaB61c0c455168317Cc5":None,
 "0x19cde1dA74F8f84bfeb48C2EfCb211583C976501":None,
 "0x08F20733f4480BBAF01aC09A9A9bac1c82B72c16":None,
 "0x83080b4a5e1aCAB6e18064C39599ACa56EB2290a":None,
 "0x1B57835b37D66A382F8B1fbF03D06DfBDcc3b724":None,
 "0xB8e692872507C41B091026676b83f66753cC5B85":None,
 "0x44871b006E4c97B11585191ff17A68130c4df7E5":None,
 "0x9831577F7Ee2257e9B0b5C9809eD53B00e6975b8":None,
}
def blk():
    for ep in EPS:
        try: return int(_single(ep,"eth_blockNumber",[],8,retries=0),16)
        except Exception: pass
head=blk(); print("head",head)
out={"head":head}
for C in TARGETS:
    r={}
    r["name"]=txt(call(C,sel("name()")))
    r["symbol"]=txt(call(C,sel("symbol()")))
    r["totalSupply"]=iv(call(C,sel("totalSupply()")))
    r["freeClaimed"]=iv(call(C,sel("freeClaimed()")))
    r["FREE_SUPPLY"]=iv(call(C,sel("FREE_SUPPLY()")))
    r["mintedBy"]=iv(call(C,sel("mintedBy(address)")+enc(USER)))
    r["freeUsed"]=iv(call(C,sel("freeUsed(address)")+enc(USER)))
    r["balance"]=iv(call(C,sel("balanceOf(address)")+enc(USER)))
    r["quote"]=call(C,sel("quote(address,uint256)")+enc(USER)+"01".rjust(64,"0"))
    r["AGENT_ID"]=call(C,sel("AGENT_ID()"))
    r["owner"]=call(C,sel("owner()"))
    print(C, r)
    # first mint walk from 130000000
    logs=[]; tok=None; pages=0; err=None
    while True:
        params={"blockchain":"bsc","fromBlock":hex(130000000),"toBlock":hex(head),"pageSize":1000,"decodeLogs":False,"topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef","0x"+"00"*32],"address":C}
        if tok: params["pageToken"]=tok
        try: body=ankr_post("ankr_getLogs",params,timeout=30)
        except Exception as e: err=str(e)[:200]; break
        res=body.get("result",{}) if isinstance(body,dict) else {}
        got=[l for l in res.get("logs",[]) if l.get("address","").lower()==C.lower()]
        logs.extend(got); tok=res.get("nextPageToken"); pages+=1
        if not tok or pages>=10: break
        time.sleep(1)
    fm={"count":len(logs),"err":err,"pages":pages}
    if logs:
        blks=sorted(int(l["blockNumber"],16) for l in logs)
        minters=set(l.get("topics",[])[2] for l in logs if len(l.get("topics",[]))>=3)
        fm.update({"first_block":blks[0],"last_block":blks[-1],"distinct_minters":len(minters)})
        for ep in EPS:
            try:
                b=_single(ep,"eth_getBlockByNumber",[hex(blks[0]),False],8,retries=0); ts=int(b["timestamp"],16)
                fm["first_wib"]=datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB"); break
            except Exception: pass
    r["first"]=fm; print(" first",fm)
    out[C]=r
json.dump(out, open(BASE+"run-2026-11-02-1901-sourcify-verify.json","w"), indent=1)
