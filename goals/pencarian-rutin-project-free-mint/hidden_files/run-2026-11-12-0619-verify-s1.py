#!/usr/bin/env python3
"""Hot-leg 0619: verify the two new S1 contracts from the Sourcify feed.
Read-only; writes run-2026-11-12-0619-verify-s1.json. No preview/mint."""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def post_rpc(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def raw_batch(addr,views):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        elif "(uint256)" in sig: data=sel(sig)+"00"*31+"01"; key=base+"_1"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res=post_rpc(ep,calls,timeout=25)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {key:(None if (isinstance(it,dict) and "error" in it) else (it.get("result") if isinstance(it,dict) else None)) for it,key in zip(res,keys)}
        except Exception: continue
    return None
def get_block():
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=25)
            return int(r["result"],16)
        except Exception: continue
    return None
def get_abi(addr):
    req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",headers={"User-Agent":"free-bacot/1.0"})
    with urllib.request.urlopen(req,timeout=25) as r:
        return json.loads(r.read().decode())["abi"]
TARGETS=["0xEC234269297614ED73Db83103325cff68A40aE10","0x4556f4Eda3Ed29946f544e03E2Ec2b236d81129f"]
VIEWS=["name()","symbol()","totalSupply()","totalMinted()","freeMinted()","freeClaimed()","FREE_SUPPLY()","FREE_SLOTS()","freePoolSize()","freeLeft()","freeSharesRemaining()","mintOpen()","saleStart()","mintStart()","mintOpenedAt()","owner()","contractURI()","tokenURI(uint256)","AGENT_ID()","agentIdRegistry()","quote(address,uint256)","cost(address,uint256)","freeAvailable(address)","freeClaimed(address)","mintedBy(address)","freeMintedBy(address)","balanceOf(address)"]
out={"block":get_block(),"started_wib":"2026-11-12 06:19 WIB","verify":{}}
print("BLOCK",out["block"],flush=True)
for addr in TARGETS:
    t=time.time()
    try:
        abi=get_abi(addr)
        fns=sorted({e["name"] for e in abi if e.get("type")=="function"})
    except Exception as e:
        fns=[]; print(addr,"ABI FAIL",e,flush=True)
    views=[v for v in VIEWS if v.split("(")[0] in fns]
    got=raw_batch(addr,views)
    d={"address":addr,"abi_fns":fns}
    if got is None:
        d["_batch_fail"]=True
    else:
        for k,v in got.items():
            if k in ("name","symbol","contractURI","tokenURI_1","owner"):
                d[k]=v  # raw hex; decode below
            else:
                d[k]=to_int(v)
    # decode string/bytes returns
    def dec_str(h):
        try:
            if not h or h=="0x": return None
            b=bytes.fromhex(h[2:])
            if len(b)>=64:
                ln=int.from_bytes(b[32:64],"big")
                return b[64:64+ln].decode(errors="replace") or None
            return None
        except Exception: return None
    for k in ("name","symbol","contractURI","tokenURI_1"):
        if d.get(k): d[k+"_decoded"]=dec_str(d[k])
    out["verify"][addr]=d
    print(addr, {k:v for k,v in d.items() if v is not None and k!="abi_fns"}, f"({time.time()-t:.1f}s)", flush=True)
json.dump(out,open(BASE+"run-2026-11-12-0619-verify-s1.json","w"),indent=1)
print("VERIFY-S1 DONE")
