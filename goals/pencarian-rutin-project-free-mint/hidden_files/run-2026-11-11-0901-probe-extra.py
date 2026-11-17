#!/usr/bin/env python3
"""Supplementary probe run 0901: 3 upcoming (first-mint watch) + AgentPals/GangDotFun + retry 2 timed-out feed ABIs. Read-only."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def batch(addr, views):
    calls=[]; keys=[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            r=post(ep,calls,timeout=25)
            if isinstance(r,list) and len(r)==len(calls):
                return {k:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,k in zip(r,keys)}
        except Exception: continue
    return None
def block():
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=25)
            return int(r["result"],16)
        except Exception: continue
    return None
out={"block":block()}
VIEWS=["totalSupply()","totalMinted()","freeMinted()","mintOpen()","mintStart()","balanceOf(address)"]
for name,addr in [("Stampooor Stamp Packs","0x467696af8c2206B977B24081445104632dc1D459"),
                  ("Rulz Share","0x08E3e40829718913fb627c818Cb334B1E3d5B699"),
                  ("Mimint Share","0x0BF38aFe23070C79f693DBDA4ce1866Ff11C4bF7"),
                  ("AgentPals","0xD265a929D0E50bD5ee4675e4E97F38D8380802E2"),
                  ("GangDotFun","0x0a2a07ef09dd7d83e2312476f0588abaa3e34ce3")]:
    out[name]=batch(addr,VIEWS)
    print(name,json.dumps(out[name]),flush=True)
# retry 2 timed-out feed ABIs
for addr in ["0x7Eb92041aa3037e39baA88154F279e3D9F85c593","0x4e11a16f9CB98bCdd4fb003FFbb64bf83E5515C3"]:
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",headers={"User-Agent":"free-bacot/1.0"})
        with urllib.request.urlopen(req,timeout=20) as r: meta=json.loads(r.read().decode())
        abi=meta.get("abi",[])
        fns=sorted(set(e["name"] for e in abi if e.get("type")=="function"))
        is_nft=bool(set(fns)&{"tokenURI","ownerOf","safeTransferFrom"}) or "uri" in fns
        agent_ref=bool(set(fns)&{"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        has_mint=any(n.lower().startswith("mint") for n in fns)
        print("RETRY-ABI",addr,"fns=",len(fns),"nft=",is_nft,"agent=",agent_ref,"mint=",has_mint,flush=True)
        out["retry_"+addr]={"fn_count":len(fns),"is_nft":is_nft,"agent_ref":agent_ref,"has_mint":has_mint,"fns":fns}
    except Exception as ex:
        print("RETRY-ABI FAIL",addr,repr(ex),flush=True)
        out["retry_"+addr]={"error":repr(ex)}
json.dump(out,open("run-2026-11-11-0901-probe-extra.json","w"),indent=1)
print("DONE block",out["block"],flush=True)
