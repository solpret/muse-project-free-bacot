#!/usr/bin/env python3
"""Triage run 2301: S1 hit 0x5a52fe87, A888S2 0x1c963acf, 0x8b059e61. Read-only."""
import json, urllib.request, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def post_rpc(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def to_int(v):
    try:
        if v is None or v=="0x": return None
        return int(v,16)
    except Exception: return None
def batch(addr,views):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig:
            data=sel(sig)+enc(USER); key=base+"_user"
        else:
            data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(key)
    for ep in RPCS:
        try:
            res=post_rpc(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {k:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,k in zip(res,keys)}
        except Exception: continue
    return None
def abi(addr):
    url=f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req=urllib.request.Request(url,headers={"User-Agent":"curl/8"})
    try:
        with urllib.request.urlopen(req,timeout=20) as r: d=json.load(r)
        return d
    except Exception as e: return {"_error":str(e)}
def block():
    for ep in RPCS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})
            return int(r["result"],16)
        except Exception: continue
    return None
out={"block":block()}
# --- S1 hit ---
A="0x5a52fe87c7F498653C596D856F1354E0a2895a07"
d=abi(A); ab=d.get("abi") if isinstance(d,dict) else None
fns=[]
if isinstance(ab,list):
    for f in ab:
        if f.get("type")=="function":
            ins=",".join(i.get("type","") for i in f.get("inputs",[]))
            fns.append(f"{f.get('name')}({ins})")
print("S1-HIT fns:", fns)
out["s1_hit"]={"address":A,"fns":fns,"verifiedAt":d.get("verifiedAt") if isinstance(d,dict) else None}
VIEWS=["totalSupply()","freeSharesRemaining()","freeSharesClaimed(address)","freeClaimed(address)",
 "freeSharesClaimed()","freeClaimed()","totalShares()","FREE_SHARES()","TOKENS_PER_SHARE()",
 "PRICE_PER_SHARE()","saleOpen()","mintOpen()","launched()","hasAgentId(address)",
 "balanceOf(address)","agentRegistry()","AGENT_ID_REGISTRY()","owner()","name()","symbol()"]
r=batch(A,VIEWS); out["s1_hit"]["views"]=r
print("S1-HIT views:", json.dumps(r))
# quote(user,1) needs exact quote fn name; try common ones
for q in ["quote(address,uint256)","quote(uint256)","getQuote(address,uint256)","cost(address,uint256)","priceFor(address,uint256)"]:
    try:
        data=sel(q)+enc(USER)+"0000000000000000000000000000000000000000000000000000000000000001"
        for ep in RPCS:
            try:
                res=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":A,"data":data},"latest"]})
                if isinstance(res,dict) and "result" in res and res["result"] not in (None,"0x"):
                    print("QUOTE",q,"->",res["result"], to_int(res["result"]))
                    out["s1_hit"].setdefault("quotes",{})[q]=res["result"]
                    break
            except Exception: continue
    except Exception as e: print("quote err",q,e)
# --- A888S2 ---
B="0x1c963acf3743a2b2a3ee8359100e9cbeca82d424"
d2=abi(B); ab2=d2.get("abi") if isinstance(d2,dict) else None
fns2=[]
if isinstance(ab2,list):
    for f in ab2:
        if f.get("type")=="function":
            ins=",".join(i.get("type","") for i in f.get("inputs",[]))
            fns2.append(f"{f.get('name')}({ins})")
print("A888S2 fns:", fns2)
out["a888s2"]={"address":B,"fns":fns2,"verifiedAt":d2.get("verifiedAt") if isinstance(d2,dict) else None}
V2=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()",
 "mintOpen()","balanceOf(address)","freeClaimed(address)","freeMintedBy(address)","mintPrice()",
 "priceFor(address,uint256)","agentRegistry()","hasAgentId(address)","owner()","name()","symbol()",
 "saleStart()","START_TIME()","startTime()","mintStart()","freeSupply()","freeLeft()"]
r2=batch(B,V2); out["a888s2"]["views"]=r2
print("A888S2 views:", json.dumps(r2))
# --- 0x8b05 ---
C="0x8b059e611E5f16b4659f81698CDbcB3dcfcDFDF1"
d3=abi(C); ab3=d3.get("abi") if isinstance(d3,dict) else None
fns3=[]
if isinstance(ab3,list):
    for f in ab3:
        if f.get("type")=="function":
            ins=",".join(i.get("type","") for i in f.get("inputs",[]))
            fns3.append(f"{f.get('name')}({ins})")
print("8B05 fns:", fns3)
out["c8b05"]={"address":C,"fns":fns3,"verifiedAt":d3.get("verifiedAt") if isinstance(d3,dict) else None}
r3=batch(C,V2); out["c8b05"]["views"]=r3
print("8B05 views:", json.dumps(r3))
json.dump(out,open(f"{BASE}/run-2026-11-09-2301-triage-new.json","w"),indent=1)
print("TRIAGE DONE block", out["block"])
