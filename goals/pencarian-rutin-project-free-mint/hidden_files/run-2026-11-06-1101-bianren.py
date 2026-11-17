#!/usr/bin/env python3
"""Focused Bianren first-mint: backward chunked Ankr getLogs, NO stop on
no-hit chunks; stop when logs >= totalMinted (16) or 400 chunks (past 48h)."""
import json, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR="0xd24A02198e12B35faDE9DD8334Fb7f6333CD05eF"
ZERO="0x"+"00"*32
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
def logs(frm,to):
    b=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(to),"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO],"address":ADDR},timeout=30)
    return [int(l["blockNumber"],16) for l in (b.get("result",{}).get("logs",[]) if isinstance(b,dict) else [])]
def ts(blk):
    import urllib.request
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(blk),False]}).encode()
    for rpc in ["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com"]:
        try:
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=8) as r: t=int(json.load(r)["result"]["timestamp"],16)
            return datetime.datetime.fromtimestamp(t,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception: continue
    return None
head=131945028
total=[]; to_b=head; chunks=0
while len(total)<16 and chunks<400:
    frm=max(0,to_b-999)
    try: ls=logs(frm,to_b)
    except Exception as e:
        print("chunk error",frm,repr(e),flush=True); break
    chunks+=1
    total+=ls
    if chunks%20==0: print("chunks",chunks,"logs",len(total),"earliest",min(total) if total else None,flush=True)
    to_b=frm-1
print("BIANREN chunks",chunks,"logs",len(total),"earliest",min(total) if total else None, ts(min(total)) if total else None,flush=True)
json.dump({"chunks":chunks,"logs":len(total),"earliest_block":min(total) if total else None,"earliest_wib":ts(min(total)) if total else None,"all_blocks":sorted(total)},open(f"{BASE}/run-2026-11-06-1101-bianren.json","w"),indent=1)
