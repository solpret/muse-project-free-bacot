#!/usr/bin/env python3
"""Run 0931: verify scan first-seen agent-shaped candidates + 5c shape-check. Read-only."""
import json, sys, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(to,data):
    for ep in EPS:
        try:
            v=_single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0)
            return v
        except Exception: pass
    return None
def iv(v):
    try: return int(v,16) if v else None
    except Exception: return None
CANDS={"SynthMinds":"0x36E655717BA3fB01268b6069a88Cc5D4a982EA15","Shroomlets":"0xD0624b7cED1B822BCa6359302c375D8EF700a7fe","Aerogent":"0xa91D6303E5538c0c71Af0Df8CEF62875a2600bFE"}
VIEWS=["totalSupply()","freeClaimed()","FREE_SUPPLY()","freeLeft()","mintOpen()","freeMinted()"]
out={}
for n,a in CANDS.items():
    d={v: iv(call(a,sel(v))) for v in VIEWS}
    d["mintedBy_user"]=iv(call(a,sel("mintedBy(address)")+enc(USER)))
    d["freeUsed_user"]=iv(call(a,sel("freeUsed(address)")+enc(USER)))
    d["balance_user"]=iv(call(a,sel("balanceOf(address)")+enc(USER)))
    o=call(a,sel("owner()")); d["owner"]="0x"+o[-40:] if o and len(o)>=42 else o
    out[n]=d; print(n,d,flush=True)
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
# pre-window: 2000 blocks immediately before scan window start 131354347 -> 131352347-131354346
for n,a in CANDS.items():
    try:
        body=ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":hex(131352347),"toBlock":hex(131354346),"address":a,"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO]}, timeout=30)
        res=body.get("result",body) if isinstance(body,dict) else body
        logs=res.get("logs",[]) if isinstance(res,dict) else []
        out[n]["prewindow_131352347_131354346_mints"]=len(logs)
        print(n,"prewindow mints",len(logs),flush=True)
    except Exception as e:
        out[n]["prewindow_error"]=str(e)[:160]; print(n,"prewindow ERROR",str(e)[:160],flush=True)
# 5c shape-check top20 todo
todo=json.load(open(BASE+"run-2026-11-03-0931-trackc-5c-todo.json"))
shapes=[]
for e in todo:
    a=e["address"]
    r=subprocess.run(["curl","-sL","--max-time","20",f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"],capture_output=True,text=True).stdout
    try: abi=json.loads(r).get("abi",[]) if r.startswith("{") else []
    except Exception: abi=[]
    fns=sorted({f.get("name") for f in abi if f.get("type")=="function"})
    txt=json.dumps(abi).lower()
    has_mint=any(f in fns for f in ["mint","mintFree","mintCard"])
    has_quote=any(f in fns for f in ["quote","cost","getQuote","quoteCost"])
    has_free=any(f in fns for f in ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted"])
    agent=("60b9262456de011f7d15a54cdd8c48baaa8b022f" in txt) or any(f in fns for f in ["agentGate","agentId","agentRegistry","isAgent","AGENT_ID","hasAgentId"])
    istoken=any(f in fns for f in ["decimals","totalSupply"]) and not any(f in fns for f in ["ownerOf","tokenURI"])
    s1=has_mint and has_quote and has_free and agent
    s2=istoken and ("mintFree" in fns) and has_free and agent
    rec={"address":a,"mint_count":e["mint_count"],"S1":s1,"S2":s2,"verified":bool(abi),"has_mint":has_mint,"has_quote":has_quote,"has_free":has_free,"agent":agent,"fns":fns}
    shapes.append(rec); print(a, e["mint_count"], "S1",s1,"S2",s2,"ver",bool(abi),"mint",has_mint,"quote",has_quote,"free",has_free,"agent",agent, flush=True)
json.dump({"candidates":out,"trackc_5c":shapes}, open(BASE+"run-2026-11-03-0931-scan-verify.json","w"), indent=1)
