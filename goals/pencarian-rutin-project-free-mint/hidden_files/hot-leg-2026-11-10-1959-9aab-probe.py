import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP="https://bsc.nodereal.io/"
C="0x9aab6e84096A780F9400CdD4E230FaA41B4545f2"
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x","").rjust(64,"0")
def enc_uint(n): return format(n,"064x")
calls={}
def noarg(fn): calls[fn]=sel(f"{fn}()")
def addrarg(fn): calls[fn+"_user"]=sel(f"{fn}(address)")+enc_addr(USER)
def addruint(fn,n=1): calls[fn+"_user1"]=sel(f"{fn}(address,uint256)")+enc_addr(USER)+enc_uint(n)
for fn in ["name","symbol","totalSupply","totalMinted","freeMinted","freeRemaining","freeAllocationRemaining",
           "FREE_SUPPLY","FREE_PER_WALLET","MAX_SUPPLY","maxSupply","mintOpen","saleOpen","isFreeOpen","isPaidOpen",
           "saleClosed","saleStart","saleEnd","freeEnd","PRICE","mintPrice","cost","paidMinted","paidSupply",
           "remainingSupply","contractURI","owner","PAYEE","agentIdRegistry","AGENT_ID_REGISTRY"]:
    noarg(fn)
for fn in ["balanceOf","mintedBy","freeMintedBy","freeAvailable","freeRemainingFor","canFreeMint","hasAgentId","remainingQuota"]:
    addrarg(fn)
addruint("quote",1)
addruint("costOf",1)
payload=json.dumps([{"jsonrpc":"2.0","id":i,"method":"eth_call","params":[{"to":C,"data":d},"latest"]} for i,d in enumerate(calls.values())])
p=subprocess.run(["curl","-s","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","--data",payload],capture_output=True,text=True)
try: resp=json.loads(p.stdout)
except Exception: resp=[]
if isinstance(resp,dict): resp=[resp]
out={}
keys=list(calls.keys())
for j,item in enumerate(resp):
    if j>=len(keys): break
    k=keys[j]
    r=item.get("result") if isinstance(item,dict) else None
    out[k]=r
# block number
p2=subprocess.run(["curl","-s","--max-time","15","-X","POST",EP,"-H","Content-Type: application/json","--data",'{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],capture_output=True,text=True)
try: out["_block"]=int(json.loads(p2.stdout)["result"],16)
except Exception: out["_block"]=None
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
for k,v in out.items():
    if k in ("name","symbol","contractURI"):
        res[k]=dec_str(v)
    elif k=="_block":
        res[k]=v
    else:
        res[k]=dec_int(v)
json.dump(res, open(BASE+"hot-leg-2026-11-10-1959-9aab-probe.json","w"), indent=1)
for k,v in res.items(): print(k,"=",v)
