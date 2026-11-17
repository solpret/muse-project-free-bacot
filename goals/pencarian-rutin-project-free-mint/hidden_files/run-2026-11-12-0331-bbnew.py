#!/usr/bin/env python3
"""Shape-check + on-chain verify Boltbook-new 0xfa07e35e (run 0331).
Read-only; writes run-2026-11-12-0331-bbnew.json."""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR="0xfa07e35e9fb5bd3dc030e61c1709b9dfe3525da5"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def get(url,timeout=25):
    req=urllib.request.Request(url,headers={"User-Agent":"free-bacot/1.0"})
    with urllib.request.urlopen(req,timeout=timeout) as r: return r.read().decode(errors="replace")
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
out={"address":ADDR}
# Sourcify ABI
try:
    meta=json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi"))
    abi=meta.get("abi",[])
    fns={}
    for e in abi:
        if e.get("type")=="function": fns.setdefault(e["name"],[]).append(e)
    names=set(fns)
    out["sourcify"]={"verified":True,"fn_count":len(names),
      "names":sorted(names)[:80]}
    FREE={"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
    ln={n.lower() for n in names}
    has_mint=any(n.lower().startswith("mint") for n in names)
    has_quote=bool(ln & {"quote","cost","getquote","mintcost","price","getprice","mintprice"})
    free_views=sorted(names & FREE)
    agent_ref=bool(ln & {"agentid","agentregistry","registry","getagentid","agentgate","agentidregistry"})
    is_token=bool(names & {"name","symbol","decimals","totalSupply"})
    mintfree="mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
    s1=has_mint and has_quote and bool(free_views) and agent_ref
    s2=is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
    is_nft=bool(names & {"tokenURI","ownerOf","safeTransferFrom"}) or "uri" in names
    out["shape"]={"S1":s1,"S2":s2,"early_shape":bool(is_nft and (agent_ref or bool(names & {"freeMint","mintFree","claimFree","mint"}))),
      "has_mint":has_mint,"has_quote":has_quote,"free_views":free_views,"agent_ref":agent_ref,"is_token":is_token,"is_nft":is_nft}
except Exception as e:
    out["sourcify"]={"verified":False,"error":f"{type(e).__name__}: {str(e)[:150]}"}
    out["shape"]={"error":"no ABI"}
# on-chain reads
def post_rpc(ep,payload,timeout=25):
    o=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(o)
def raw_batch(addr,views):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res=post_rpc(ep,calls,timeout=25)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {key:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,key in zip(res,keys)}
        except Exception: continue
    return None
VIEWS=["name()","symbol()","totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","balanceOf(address)","freeClaimed(address)","mintStart()","mintOpenedAt()","owner()"]
got=raw_batch(ADDR,VIEWS)
out["onchain"]=got
# name/symbol are strings - read raw
def eth_call(to,data):
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]},timeout=25)
            if "result" in r: return r["result"]
        except Exception: continue
    return None
def dec_str(raw):
    try:
        b=bytes.fromhex(raw[2:])
        off=int.from_bytes(b[32:64],"big"); ln=int.from_bytes(b[64+off-32:64+off],"big") if False else None
        # standard ABI string: [0:32]=offset, [32:64]=len, [64:]=data
        ln=int.from_bytes(b[32:64],"big")
        return b[64:64+ln].decode(errors="replace")
    except Exception as e: return f"<decode fail {e}>"
out["name_raw"]=dec_str(eth_call(ADDR,sel("name()"))) if eth_call(ADDR,sel("name()")) else None
out["symbol_raw"]=dec_str(eth_call(ADDR,sel("symbol()"))) if eth_call(ADDR,sel("symbol()")) else None
print(json.dumps(out,indent=1))
json.dump(out,open(BASE+"run-2026-11-12-0331-bbnew.json","w"),indent=1)
