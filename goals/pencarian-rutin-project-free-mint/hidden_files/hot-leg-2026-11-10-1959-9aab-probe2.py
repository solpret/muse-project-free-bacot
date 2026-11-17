import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc.nodereal.io/","https://bsc-dataseed.bnbchain.org/"]
C="0x9aab6e84096A780F9400CdD4E230FaA41B4545f2"
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x","").rjust(64,"0")
def enc_uint(n): return format(n,"064x")
calls=[]
def noarg(fn): calls.append((fn, sel(f"{fn}()")))
def addrarg(fn): calls.append((fn+"_user", sel(f"{fn}(address)")+enc_addr(USER)))
def addruint(fn,n=1): calls.append((fn+"_user1", sel(f"{fn}(address,uint256)")+enc_addr(USER)+enc_uint(n)))
for fn in ["name","symbol","totalSupply","totalMinted","freeMinted","freeRemaining","freeAllocationRemaining",
           "FREE_SUPPLY","FREE_PER_WALLET","MAX_SUPPLY","maxSupply","mintOpen","saleOpen","isFreeOpen","isPaidOpen",
           "saleClosed","saleStart","saleEnd","freeEnd","PRICE","mintPrice","cost","paidMinted","paidSupply",
           "remainingSupply","contractURI","owner","PAYEE","agentIdRegistry","AGENT_ID_REGISTRY"]:
    noarg(fn)
for fn in ["balanceOf","mintedBy","freeMintedBy","freeAvailable","freeRemainingFor","canFreeMint","hasAgentId","remainingQuota"]:
    addrarg(fn)
addruint("quote",1); addruint("costOf",1)
def run_batch(ep, chunk):
    payload=json.dumps([{"jsonrpc":"2.0","id":i,"method":"eth_call","params":[{"to":C,"data":d},"latest"]} for i,(_,d) in enumerate(chunk)])
    p=subprocess.run(["curl","-s","--max-time","30","-X","POST",ep,"-H","Content-Type: application/json","--data",payload],capture_output=True,text=True)
    try:
        r=json.loads(p.stdout)
        return r if isinstance(r,list) else [r]
    except Exception:
        return []
results={}; failed=[]
for i in range(0,len(calls),25):
    chunk=calls[i:i+25]
    resp=run_batch(EPS[0], chunk)
    ok = len(resp)==len(chunk) and all(isinstance(x,dict) and "result" in x for x in resp)
    if not ok:
        resp2=run_batch(EPS[1], chunk)
        ok2 = len(resp2)==len(chunk) and all(isinstance(x,dict) and "result" in x for x in resp2)
        resp = resp2 if ok2 else resp
    for j,item in enumerate(resp):
        k=chunk[j][0]
        if isinstance(item,dict) and "result" in item: results[k]=item["result"]
        else: results[k]=None; failed.append(k)
def dec_str(h):
    if not h or not isinstance(h,str) or not h.startswith("0x"): return None
    try:
        b=bytes.fromhex(h[2:])
        if len(b)<64: return None
        ln=int.from_bytes(b[32:64],"big")
        return b[64:64+ln].decode("utf-8","replace")
    except Exception: return None
def dec_int(h):
    if not h or not isinstance(h,str) or not h.startswith("0x"): return None
    try: return int(h,16)
    except Exception: return None
res={}
for k,v in results.items():
    if k in ("name","symbol","contractURI"): res[k]=dec_str(v)
    else: res[k]=dec_int(v)
# quote returns tuple; decode raw separately
q=results.get("quote_user1")
if q and isinstance(q,str) and q.startswith("0x"):
    try:
        b=bytes.fromhex(q[2:])
        res["quote_tuple"]=[int.from_bytes(b[i*32:(i+1)*32],"big") for i in range(5)] if len(b)>=160 else q
    except Exception: res["quote_tuple"]=q
p2=subprocess.run(["curl","-s","--max-time","15","-X","POST",EPS[0],"-H","Content-Type: application/json","--data",'{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],capture_output=True,text=True)
try: res["_block"]=int(json.loads(p2.stdout)["result"],16)
except Exception: res["_block"]=None
res["_failed"]=failed
json.dump(res, open(BASE+"hot-leg-2026-11-10-1959-9aab-probe.json","w"), indent=1)
for k,v in res.items(): print(k,"=",v)
