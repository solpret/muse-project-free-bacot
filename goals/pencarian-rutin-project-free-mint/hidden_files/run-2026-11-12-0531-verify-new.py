#!/usr/bin/env python3
"""Verify early leads fresh for run 0131: MECHA (run-2101 early), BUCKET /
MOONDRILL / 0x2e50 (hot-leg 2114 early), CRTSAINTS (hot-leg 2049 early).
Read-only; writes run-2026-11-12-0531-verify-new.json. No preview/mint."""
import json, subprocess, time
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
def get_block():
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=25)
            return int(r["result"],16)
        except Exception: continue
    return None
VIEWS=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()",
       "mintOpen()","balanceOf(address)","freeClaimed(address)","freeUsed(address)","freeUsedBy(address)",
       "mintedBy(address)","freeMintedBy(address)","mintStart()","mintOpenedAt()","freePoolSize()",
       "totalFreeCount()","freeLeft()","firstFreeUsed()","paidMinted()","isAgent(address)","freeAvailable(address)",
       "freePerWallet()","PRICE()","price()","saleStart()","saleEnd()","AGENT_ID_REGISTRY()","agentIdRegistry()","mintOpenSat()"]
TARGETS={
 "MECHA":"0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
 "BUCKET":"0x2b0d3b384C341020aed1d49907b5708C423bA6DA",
 "MOONDRILL":"0x87b354E2014D2e418927A1105dD219A2e7b063b0",
 "0x2e50":"0x2e508C6510d9550131932f0D6Fe691DCe38E66E3",
 "CRTSAINTS":"0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F",
 "NAOMI":"0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9",
 "AGCR":"0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc",
 "WFPASS":"0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C",
 "S1-6C50":"0x6C504A7B392b1D57845F57d2abb5C4d49211Aa7f",
 "S1-0895":"0x0895398c932E602152B8F27723C2F5bf1413A87d",
 "BB-7c71":"0x7c71b7158b9b3122f35570d6b737ea4a2db8e205",
 "SEVEN":"0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96",
 "Binance Life Cards":"0x4367b86F889014e6fD57fE812B86A581b913C645",
 "Stampooor":"0x467696af8c2206B977B24081445104632dc1D459",
 "Lucky Catch":"0xD405C90079c594DA2456F5b37B4158A12f1382e5",
 "AgentPals":"0xD265a929D0E50bD5ee4675e4E97F38D8380802E2",
 "0x79b0":"0x79b0CE8b39c3Ed230487172751612b4F631398Bc",
 "Eco":"0xd31b168F7b6f3dB39BEd89433124595aaa91cfF3",
 "Pickgrid":"0x7f541bcc33abed0e64455565da723e949c6f76f0",
 "SUDOSAINTS":"0x869d330bb48e7ab32da16745ef9a36a69d34f12f",
 "SOLACE":"0x0759c26e1fbe339a7e4282f29b719f56e72f9a1b",
}
out={"block":get_block(),"started_wib":"2026-11-12 05:31 WIB","verify":{}}
print("BLOCK",out["block"],flush=True)
for name,addr in TARGETS.items():
    t=time.time(); got=raw_batch(addr,VIEWS)
    d={"address":addr}
    if got is None:
        d["_batch_fail"]=True
    else:
        d.update(got)
    out["verify"][name]=d
    print(name, {k:v for k,v in d.items() if v is not None}, f"({time.time()-t:.1f}s)", flush=True)
json.dump(out,open(BASE+"run-2026-11-12-0531-verify-new.json","w"),indent=1)
print("VERIFY DONE")
