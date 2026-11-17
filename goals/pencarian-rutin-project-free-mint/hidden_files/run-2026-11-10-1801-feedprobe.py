#!/usr/bin/env python3
"""Feed shape-check run 1801 via on-chain selector probing (Sourcify ABI endpoint
returns minimal metadata only this run — 209B, no abi — so ABI-based shape test is
impossible; probe selectors directly via eth_call batches). Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
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
VIEWS=["totalSupply()","totalMinted()","name()","symbol()","decimals()","mintOpen()","mintPrice()","price()",
 "freeMinted()","freeClaimed()","freeSharesRemaining()","freeLeft()","freeSupply()","freeAllocation()",
 "agentId()","agentRegistry()","REGISTRY()","registry()","balanceOf(address)","freeClaimed(address)",
 "freeMintedBy(address)","canClaimFree(address)","mintStart()","START_TIME()","tokensPerShare()","MAX_SUPPLY()"]
def probe(addr):
    calls,keys=[],[]
    for i,sig in enumerate(VIEWS):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(key)
    # costOf(user,1)
    calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call","params":[{"to":addr,"data":sel("costOf(address,uint256)")+enc(USER)+"0"*63+"1"},"latest"]})
    keys.append("costOf_user_1")
    for ep in EPS:
        try:
            res=post_rpc(ep,calls,timeout=25)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            outd={}
            for item,key in zip(res,keys):
                outd[key]=None if (isinstance(item,dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item,dict) else None)
            return outd
        except Exception: continue
    return None
feed=json.load(open(f"{BASE}/run-2026-11-10-1801-feed.json"))
items=feed.get('results', feed if isinstance(feed,list) else [])
out={}
for it in items:
    a=it.get('address') or it.get('contractAddress')
    if a=='0xf1b9D0b2Fac297AAD0A9eA858Dea805A49a0140a':
        out[a]={"note":"known feed-f1b9 bukan sale-shape"}; print(a,"known"); continue
    d=probe(a) or {}
    # decode name/symbol strings separately (they return bytes; to_int gives None for long strings)
    out[a]=d
    exists=[k for k,v in d.items() if v is not None]
    print(a,"| exists:",exists,flush=True)
    time.sleep(0.2)
json.dump(out,open(f"{BASE}/run-2026-11-10-1801-feedprobe.json","w"),indent=1)
print("FEEDPROBE DONE",len(out))
