#!/usr/bin/env python3
"""Age bracket run 1801: totalSupply() at historical blocks (eth_call block param)
to bracket first mint — Ankr getLogs is down (401), so no Transfer-log search.
Blocks: Nov 8 00:00 ~132237000, Nov 9 00:00 ~132429000, Nov 9 12:00 ~132525000,
Nov 10 00:00 ~132621000, Nov 10 08:00 ~132669000, Nov 10 12:00 ~132693000.
Read-only."""
import json, subprocess
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def post_rpc(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def ts_at(addr, block):
    data=sel("totalSupply()")
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},hex(block)]},timeout=25)
            res=r.get("result")
            if res and res!="0x": return int(res,16)
            if res=="0x": return 0
        except Exception: continue
    return None
TARGETS={
 "ACORE":"0xf4bacf30fb8f69373f63d99c657f53dd7774af1d",
 "NIGHTFORGE":"0x22f43ba09fd4beb9417d4484c60370354b220186",
}
BLOCKS=[(132237000,"Nov8 00:00"),(132429000,"Nov9 00:00"),(132525000,"Nov9 12:00"),(132621000,"Nov10 00:00"),(132669000,"Nov10 08:00"),(132693000,"Nov10 12:00")]
out={}
for name,addr in TARGETS.items():
    row={}
    for b,label in BLOCKS:
        row[label]=ts_at(addr,b)
        print(name,label,b,"->",row[label],flush=True)
    out[name]=row
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-10-1801-agebracket.json","w"),indent=1)
print("AGEBRACKET DONE")
