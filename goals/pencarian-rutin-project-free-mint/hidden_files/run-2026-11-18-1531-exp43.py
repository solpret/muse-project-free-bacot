#!/usr/bin/env python3
"""Fresh FIND exp43 read run 1531 (phase ends 16:00 WIB). Read-only, chunked <=5."""
import json, subprocess, time
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RPC = "https://bsc-dataseed.binance.org/"
def sel(sig): return keccak(sig.encode())[:4].hex()
def post(payload, timeout=25):
    r = subprocess.run(["curl","-s","-L","--max-time",str(timeout),RPC,"-H","Content-Type: application/json","-d",json.dumps(payload)], capture_output=True, timeout=timeout+5)
    return json.loads(r.stdout.decode())
def batch(addr, views, chunk=5):
    out={}
    for i in range(0, len(views), chunk):
        part=views[i:i+chunk]
        calls=[]
        for j,(label,sig,arg) in enumerate(part):
            data="0x"+sel(sig)
            if isinstance(arg,int): data+="%064x"%arg
            calls.append({"jsonrpc":"2.0","id":j+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        resp=post(calls)
        by={it["id"]:it for it in resp if isinstance(it,dict)} if isinstance(resp,list) else {}
        for j,(label,sig,arg) in enumerate(part):
            it=by.get(j+1,{})
            if "result" in it and it["result"] not in (None,"0x"):
                try: out[label]=int(it["result"],16)
                except Exception: out[label]=it["result"]
            elif "error" in it: out[label]="revert"
            else: out[label]=None
        print(f"  chunk {i//chunk+1} OK", flush=True)
    return out
ADDR="0x4158B701EaA30E8FaDBaA526F70780A38318c1C4"
VIEWS=[("currentExperiment","currentExperiment()",None),
 ("participantsOf_43","participantsOf(uint256)",43),
 ("specimensInExperiment_43","specimensInExperiment(uint256)",43),
 ("experimentStart_43","experimentStart(uint256)",43),
 ("experimentEnd_43","experimentEnd(uint256)",43)]
views=batch(ADDR,VIEWS,chunk=5)
print("views:",views)
blk=post([{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}])
block=int(blk[0]["result"],16) if isinstance(blk,list) else None
json.dump({"address":ADDR,"views":views,"block":block,"read_wib":"2026-11-18 ~15:31 WIB"},
          open(f"{HF}/run-2026-11-18-1531-exp43.json","w"), indent=1)
print("block:",block,"saved run-2026-11-18-1531-exp43.json")
