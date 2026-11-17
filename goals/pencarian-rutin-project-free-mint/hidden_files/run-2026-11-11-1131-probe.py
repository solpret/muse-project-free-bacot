#!/usr/bin/env python3
"""Probe run 1131: (1) new Boltbook addr 0xb3cf shape via Sourcify ABI;
(2) CAP7 fresh on-chain (free pool, user slot) + contractURI;
(3) 0x8653 early-shape NFT probe (name/totalSupply/free views) + first-mint
    attempt via public-RPC eth_getLogs small ranges; (4) Sourcify metadata
    URLs for CAP7 (method C). Read-only. Writes run-2026-11-11-1131-probe.json."""
import json, subprocess, time, urllib.request, re
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
out={}
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try:
        if v is None or v=="0x": return None
        return int(v,16)
    except Exception: return None
def post_rpc(ep,payload,timeout=25):
    r=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5)
    return json.loads(r.stdout)
def batch(addr,views):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig:
            data=sel(sig)+enc(USER); key=base+"_user"
        elif "(uint256)" in sig:
            data=sel(sig)+"00"*32; key=base+"_0"
        else:
            data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res=post_rpc(ep,calls,timeout=25)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            d={}
            for item,key in zip(res,keys):
                d[key]=None if (isinstance(item,dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item,dict) else None)
                if isinstance(item,dict) and "result" in item and item["result"] and len(item["result"])>66:
                    d[key+"_raw"]=item["result"][:500]
            return d
        except Exception as e:
            continue
    return None
def get(url,timeout=25):
    req=urllib.request.Request(url,headers={"User-Agent":"free-bacot/1.0"})
    with urllib.request.urlopen(req,timeout=timeout) as r: return r.read().decode(errors="replace")
def block():
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=25)
            return int(r["result"],16)
        except Exception: continue
    return None
out["block"]=block()
print("BLOCK",out["block"],flush=True)
# (1) new Boltbook addr shape
try:
    meta=json.loads(get("https://sourcify.dev/server/v2/contract/56/0xb3cf86fe905ad1d4c3a4eb55e01123e06e334c4c?fields=abi"))
    abi=meta.get("abi",[])
    names={e.get("name") for e in abi if e.get("type")=="function"}
    out["b3cf"]={"verified":True,"fn_count":len(names),
      "mint":sorted(n for n in names if n.lower().startswith("mint")),
      "quote":sorted(names & {"quote","cost","getQuote","mintCost","price","getPrice"}),
      "free":sorted(names & {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}),
      "agent":sorted(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"}),
      "nft":bool(names & {"tokenURI","ownerOf","safeTransferFrom"}) or "uri" in names,
      "token":bool(names & {"name","symbol","decimals","totalSupply"})}
except Exception as e:
    out["b3cf"]={"verified":False,"error":f"{type(e).__name__}: {str(e)[:150]}"}
print("B3CF",out["b3cf"],flush=True)
# (2) CAP7 fresh
CAP7="0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd"
cap7_views=["name()","symbol()","decimals()","totalSupply()","freeMinted()","freeClaimed()","freeClaimed(address)","FREE_SHARES()","sharesMinted()","paidMinted()","soldOut()","phase()","saleStart()","SALE_WINDOW()","PRICE()","costOf(uint256)","agentIdOf(address)","balanceOf(address)","contractURI()"]
out["cap7"]=batch(CAP7,cap7_views)
print("CAP7",out["cap7"],flush=True)
# (3) 0x8653 probe
A8653="0x8653B09bDaD22c99915910962167F132E514331F"
views8653=["name()","symbol()","totalSupply()","totalMinted()","freeMinted()","freeClaimed()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","balanceOf(address)","freeClaimed(address)","contractURI()"]
out["a8653"]=batch(A8653,views8653)
print("8653",out["a8653"],flush=True)
# first-mint attempt: eth_getLogs Transfer from zero, small ranges back from head
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
head=out["block"]
logs_ok=[]
if head:
    for span in (100, 500):
        frm=head-span
        payload={"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{"fromBlock":hex(frm),"toBlock":hex(head),"address":A8653,"topics":[TRANSFER,ZERO]}]}
        got=None
        for ep in EPS:
            try:
                res=post_rpc(ep,payload,timeout=25)
                if isinstance(res,dict) and "result" in res:
                    got=res["result"]; break
                else:
                    got={"error":str(res)[:150]}; break
            except Exception as e:
                got={"error":f"{type(e).__name__}: {str(e)[:120]}"}
        print(f"GETLOGS 8653 span={span} -> {str(got)[:200]}",flush=True)
        logs_ok.append({"span":span,"from":frm,"to":head,"result":got if not isinstance(got,list) else f"{len(got)} logs"})
        if isinstance(got,list) and got: break
out["a8653_getlogs"]=logs_ok
# (4) Sourcify metadata for CAP7 (method C)
try:
    meta=json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{CAP7}"))
    std=meta.get("stdJson",{}) or {}
    srcs=std.get("sources",{})
    urls=set()
    for s in srcs.values():
        for u in re.findall(r"https?://[^\s\"'<>]+", json.dumps(s)):
            urls.add(u)
    out["cap7_sourcify"]={"match":meta.get("match"),"verifiedAt":meta.get("verifiedAt"),
      "urls_in_sources":sorted(urls)[:20]}
except Exception as e:
    out["cap7_sourcify"]={"error":f"{type(e).__name__}: {str(e)[:150]}"}
print("CAP7-SOURCIFY",out["cap7_sourcify"],flush=True)
json.dump(out,open(BASE+"run-2026-11-11-1131-probe.json","w"),indent=1)
print("PROBE DONE",flush=True)
