import json, subprocess, sys
from Crypto.Hash import keccak
ADDR="0xB7517e3B31107695F2f8837fAFC76999b956C871"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def build(sig,args=None):
    d=sel(sig)
    for a in (args or []):
        d+= a[2:].lower().rjust(64,"0") if isinstance(a,str) and a.startswith("0x") else format(int(a),"064x")
    return d
VIEWS=[("name","name()",None),("symbol","symbol()",None),("totalSupply","totalSupply()",None),
("freeMinted","freeMinted()",None),("freeClaimed","freeClaimed()",None),
("FREE_SUPPLY","FREE_SUPPLY()",None),("FREE_SLOTS","FREE_SLOTS()",None),
("FREE_MAX","FREE_MAX()",None),("FREE_CAP","FREE_CAP()",None),("FREE_POOL","FREE_POOL()",None),
("freeRemaining","freeRemaining()",None),("freeSharesRemaining","freeSharesRemaining()",None),
("freeLeft","freeLeft()",None),("freeAvailable","freeAvailable()",None),
("mintOpen","mintOpen()",None),("saleActive","saleActive()",None),
("totalMinted","totalMinted()",None),("MAX_SUPPLY","MAX_SUPPLY()",None),
("owner","owner()",None),("agentRegistry","agentRegistry()",None),
("freeClaimed_user","freeClaimed(address)",[USER]),("mintedBy_user","mintedBy(address)",[USER]),
("balanceOf_user","balanceOf(address)",[USER]),("hasAgentId_user","hasAgentId(address)",[USER]),
("decimals","decimals()",None),("contractURI","contractURI()",None)]
calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":build(s,a)},"latest"]} for i,(_,s,a) in enumerate(VIEWS)]
calls.append({"jsonrpc":"2.0","id":99,"method":"eth_blockNumber","params":[]})
res=None; used=None
for ep in EPS:
    try:
        out=subprocess.run(["curl","-sL","--max-time","25","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(calls)],capture_output=True,text=True,timeout=35).stdout
        r=json.loads(out)
        if isinstance(r,list) and len(r)==len(calls): res=r; used=ep; break
    except Exception: continue
if res is None: print("BATCH FAILED all endpoints"); sys.exit(1)
print("via",used)
def dec_int(r):
    if not r or r=="0x": return None
    try: return int(r[:66],16)
    except Exception: return r
def dec_str(r):
    if not r or r=="0x": return None
    try:
        b=bytes.fromhex(r[2:]); ln=int.from_bytes(b[32:64],"big"); return b[64:64+ln].decode(errors="replace")
    except Exception: return r[:100]
for (name,sig,args),it in zip(VIEWS,res[:-1]):
    r=it.get("result") if isinstance(it,dict) else None
    if r is None or "error" in it or r=="0x": print(name,"-> (no return)"); continue
    if name in ("name","symbol","contractURI"): print(name,"->",dec_str(r))
    elif name=="owner": print(name,"->","0x"+r[-40:])
    else: print(name,"->",dec_int(r))
print("block:", int(res[-1]["result"],16))
json.dump({n:(it.get("result") if isinstance(it,dict) else None) for (n,_,_),it in zip(VIEWS,res[:-1])}, open("probe-b751-result.json","w"), indent=1)
