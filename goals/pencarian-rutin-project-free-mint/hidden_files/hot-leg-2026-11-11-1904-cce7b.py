#!/usr/bin/env python3
import json, urllib.request, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc.nodereal.io/","https://bsc-dataseed.binance.org/","https://bsc.publicnode.com"]
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x","").rjust(64,"0")
def enc_u(n): return "%064x"%n
def call(addr,sig,args="",timeout=15):
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":sel(sig)+args},"latest"]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=timeout) as r: j=json.loads(r.read().decode())
            if "error" in j: return {"error":str(j["error"])[:120]}
            raw=j["result"]
            if raw in (None,"0x"): return {"error":"empty-return"}
            return raw
        except Exception: continue
    return {"error":"all-endpoints-failed"}
def dec(raw):
    if isinstance(raw,dict): return raw
    try: return int(raw[2:66],16)
    except Exception: return raw
def dec_str(raw):
    if isinstance(raw,dict): return raw
    try:
        h=raw[2:]; off=int(h[:64],16)*2; ln=int(h[64:128],16)
        return bytes.fromhex(h[off+64:off+64+ln*2]).decode(errors="replace")
    except Exception: return raw
C="0xcce7e755D343912AA0dBBc617FEA9bb193Efb32a"; U=enc_addr(USER)
res={}
for name,sig,args,fn in [
 ("FREE_CAP","FREE_CAP()","",dec),("MAX_SUPPLY","MAX_SUPPLY()","",dec),
 ("MAX_PER_WALLET","MAX_PER_WALLET()","",dec),("mintOpensAt","mintOpensAt()","",dec),
 ("price","price()","",dec),("totalMinted","totalMinted()","",dec),
 ("nextTokenId","nextTokenId()","",dec),("mintsBy_user","mintsBy(address)",U,dec),
 ("agentIdRegistry","agentIdRegistry()","",dec_str),("owner","owner()","",dec_str),
 ("holdsAgentId_user","holdsAgentId(address)",U,dec),
 ("tokenURI_1","tokenURI(uint256)",enc_u(1),dec_str),
 ("tokenURI_111","tokenURI(uint256)",enc_u(111),dec_str),
]:
    raw=call(C,sig,args); res[name]=fn(raw) if not isinstance(raw,dict) else raw
print(json.dumps(res,indent=1,default=str))
# website retry for Stampooor
for url in ["https://stampooor.com/","https://stampooor.com/packs/"]:
    r=subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code} %{size_download}","-m","15",url],capture_output=True,timeout=20)
    print("CURL",url,r.stdout.decode(),r.stderr.decode()[:100])
json.dump(res,open(BASE+"hot-leg-2026-11-11-1904-cce7b.json","w"),indent=1,default=str)
