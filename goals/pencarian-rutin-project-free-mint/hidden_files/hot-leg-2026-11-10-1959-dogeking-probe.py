import json, subprocess
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP="https://bsc-dataseed.bnbchain.org/"
C="0xd73a0cdce58e07d8e2a38ee771cc3abc45b6fa45"
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x","").rjust(64,"0")
def enc_uint(n): return format(n,"064x")
calls={}
for fn in ["agentIds","token","FREE_SHARES","TOTAL_SHARES","FREE_TOKENS","POOL_TOKENS","SHARE_TOKENS","TOKEN_CAP","freeClaimed","isOpen","openedAt","saleStart","SALE_WINDOW","OPEN_SHARE"]:
    calls[fn]=sel(f"{fn}()")
calls["agentIdOf_user"]=sel("agentIdOf(address)")+enc_addr(USER)
calls["quote_1"]=sel("quote(uint256)")+enc_uint(1)
payload=json.dumps([{"jsonrpc":"2.0","id":i,"method":"eth_call","params":[{"to":C,"data":d},"latest"]} for i,d in enumerate(calls.values())])
p=subprocess.run(["curl","-s","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","--data",payload],capture_output=True,text=True)
try: resp=json.loads(p.stdout)
except Exception: resp=[]
if isinstance(resp,dict): resp=[resp]
keys=list(calls.keys())
out={}
for j,item in enumerate(resp):
    if j>=len(keys): break
    out[keys[j]]=item.get("result") if isinstance(item,dict) else None
def dec_addr(h):
    if not h or not isinstance(h,str) or len(h)<42: return None
    try: return "0x"+h[-40:]
    except Exception: return None
def dec_int(h):
    if not h or not isinstance(h,str) or not h.startswith("0x"): return None
    try: return int(h,16)
    except Exception: return None
res={}
for k,v in out.items():
    if k in ("agentIds","token"): res[k]=dec_addr(v)
    elif k=="agentIdOf_user":
        if v and isinstance(v,str) and v.startswith("0x") and len(v)>=130:
            b=bytes.fromhex(v[2:]); res[k]=(int.from_bytes(b[0:32],"big"), bool(int.from_bytes(b[32:64],"big")))
        else: res[k]=v
    elif k=="quote_1":
        if v and isinstance(v,str) and v.startswith("0x") and len(v)>=258:
            b=bytes.fromhex(v[2:]); res[k]=[int.from_bytes(b[i*32:(i+1)*32],"big") for i in range(4)]
        else: res[k]=v
    else: res[k]=dec_int(v)
p2=subprocess.run(["curl","-s","--max-time","15","-X","POST",EP,"-H","Content-Type: application/json","--data",'{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],capture_output=True,text=True)
try: res["_block"]=int(json.loads(p2.stdout)["result"],16)
except Exception: res["_block"]=None
json.dump(res, open("hot-leg-2026-11-10-1959-dogeking-probe.json","w"), indent=1, default=str)
for k,v in res.items(): print(k,"=",v)
