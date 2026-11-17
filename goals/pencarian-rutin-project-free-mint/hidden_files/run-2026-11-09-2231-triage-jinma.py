#!/usr/bin/env python3
"""Triage JINMA sale 0x8553e7033C06fC69B7508d58507b75242cF86EC4 (new via Boltbook post j8nsVLKZbbhH).
Read-only; never previews/mints. Writes run-2026-11-09-2231-triage-jinma.json."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
SALE="0x8553e7033C06fC69B7508d58507b75242cF86EC4"
TOKEN="0xe4517e6718b24d5725956ac7a90686592a7b1539"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try:
        if v is None or v=="0x": return None
        return int(v,16)
    except Exception: return None
def post_rpc(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def raw_batch(addr,views):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig:
            data=sel(sig)+enc(USER); key=base+"_user"
        elif "(uint256,address)" in sig:
            data=sel(sig)+"0"*64+"0"*24+USER[2:].lower(); key=base+"_user"
        else:
            data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res=post_rpc(ep,calls,timeout=25)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {key: to_int(item.get("result")) for item,key in zip(res,keys)}
        except Exception: continue
    return {key: None for key in keys}
def fetch_abi(addr):
    req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata",headers={"User-Agent":"curl/8"})
    try:
        with urllib.request.urlopen(req,timeout=20) as r: d=json.load(r)
        return d
    except Exception as e: return {"_error":str(e)}
out={"sale":SALE,"token":TOKEN,"user":USER}
sale_abi=fetch_abi(SALE)
out["sale_sourcify"]= {"match": sale_abi.get("match"), "verifiedAt": sale_abi.get("verifiedAt"), "error": sale_abi.get("_error")}
abi=sale_abi.get("abi")
fns=[]
if isinstance(abi,list):
    fns=sorted({f.get("name") for f in abi if f.get("type")=="function" and f.get("name")})
out["sale_fns"]=fns
src=json.dumps(abi).lower() if isinstance(abi,list) else ""
out["sale_agent_ref"]= ("60b9262456de011f7d15a54cdd8c48baaa8b022f" in src or "agentid" in src or "agentgate" in src or "agentregistry" in src)
out["sale_metadata_urls"]= []
try:
    md=json.loads(sale_abi.get("metadata","") or "{}")
    out["sale_metadata_urls"]= [md.get("settings",{}).get("compilationTarget",{}), md.get("sources",{})]
except Exception: pass
views=["totalShares()","FREE_SHARES()","freeSharesRemaining()","publicFreeRemaining()","totalPaidShares()","saleClockStart()","TOKENS_PER_SHARE()","PRICE_PER_SHARE()","token()","owner()","hasAgentId(address)","freeSharesClaimed(address)","paidQuotaOf(address)","mintPrice()","quote(uint256)","costOf(uint256,address)","freeOf(uint256,address)","saleStart()","startTime()","mintStart()","launchTime()","MAX_SHARES()","isOpen()","saleOpen()"]
out["sale_reads"]=raw_batch(SALE,views)
tok_abi=fetch_abi(TOKEN)
out["token_sourcify"]= {"match": tok_abi.get("match"), "verifiedAt": tok_abi.get("verifiedAt"), "error": tok_abi.get("_error")}
tabi=tok_abi.get("abi")
out["token_fns"]= sorted({f.get("name") for f in tabi if f.get("type")=="function" and f.get("name")}) if isinstance(tabi,list) else []
out["token_reads"]=raw_batch(TOKEN,["name()","symbol()","decimals()","totalSupply()","owner()","launched()","transferLocked()","isTransferLocked()","paused()","balanceOf(address)"])
# code length + registry bytes
def code_len(addr):
    for ep in EPS:
        try:
            r=post_rpc(ep,[{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]}],timeout=25)
            c=r[0].get("result","0x")
            return (len(c)-2)//2, ("60b9262456de011f7d15a54cdd8c48baaa8b022f" in c.lower())
        except Exception: continue
    return None,None
out["sale_code_len"],out["sale_registry_bytes"]=code_len(SALE)
out["token_code_len"],out["token_registry_bytes"]=code_len(TOKEN)
# owner vs discards
try:
    disc=json.load(open(f"{BASE}/same-owner-discards.json"))
    owners=set()
    def walk(o):
        if isinstance(o,dict):
            for k,v in o.items():
                if k.lower() in ("owner","owners","deployer") and isinstance(v,str): owners.add(v.lower())
                walk(v)
        elif isinstance(o,list):
            for v in o: walk(v)
    walk(disc)
    out["discard_owners_count"]=len(owners)
    own=out["sale_reads"].get("owner")
    out["sale_owner_hex"]= hex(own) if isinstance(own,int) else own
    out["owner_in_discards"]= (("0x%040x"%own).lower() in owners) if isinstance(own,int) else None
except Exception as e:
    out["discards_error"]=str(e)
# head block
try:
    r=post_rpc(EPS[0],[{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}],timeout=25)
    out["head_block"]=int(r[0]["result"],16)
except Exception as e: out["head_error"]=str(e)
json.dump(out,open(f"{BASE}/run-2026-11-09-2231-triage-jinma.json","w"),indent=1)
print(json.dumps(out,indent=1))
