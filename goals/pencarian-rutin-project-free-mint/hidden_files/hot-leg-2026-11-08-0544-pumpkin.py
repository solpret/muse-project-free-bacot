import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
ADDR="0x77e38295603a06654a6ed3ed0849e6aa50749963"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def to_int(v):
    try: return int(v,16)
    except Exception: return None
def call(addr,sig,args=None,raw=False):
    data=sel(sig)
    if args:
        for a in args:
            data+= enc_addr(a) if isinstance(a,str) and a.startswith("0x") else enc_u(a)
    for ep in EPS:
        try:
            res=batch([("eth_call",[{"to":addr,"data":data},"latest"])],endpoint=ep,timeout=8)
            return res[0]
        except Exception as e:
            last=str(e)
    return f"ERR:{last}"
def dec_str(hexv):
    try:
        b=bytes.fromhex(hexv[2:])
        off=int.from_bytes(b[32:64],"big"); ln=int.from_bytes(b[64:96],"big")
        return b[96:96+ln].decode()
    except Exception as e:
        return f"ERR:{e}"
out={}
for sig in ["name()","symbol()","totalSupply()","MAX_SUPPLY()","FREE_SUPPLY()","FREE_PER_WALLET()","MAX_PER_WALLET()","freeClaimed()","mintOpen()","PRICE()","AGENT_ID()","owner()","contractURI()"]:
    v=call(ADDR,sig)
    if sig in ("name()","symbol()","contractURI()"):
        out[sig]=dec_str(v) if isinstance(v,str) and v.startswith("0x") else v
    elif sig=="AGENT_ID()" or sig=="owner()":
        out[sig]=("0x"+v[-40:]) if isinstance(v,str) and v.startswith("0x") and len(v)>=42 else v
    elif sig=="mintOpen()":
        out[sig]=to_int(v)
    else:
        out[sig]=to_int(v)
for sig,args,key in [("freeLeft(address)",[USER],"freeLeft_user"),
                     ("freeUsed(address)",[USER],"freeUsed_user"),
                     ("freeFor(address,uint256)",[USER,1],"freeFor_user1"),
                     ("quote(address,uint256)",[USER,1],"quote_user1"),
                     ("balanceOf(address)",[USER],"balanceOf_user"),
                     ("mintedBy(address)",[USER],"mintedBy_user")]:
    out[key]=to_int(call(ADDR,sig,args))
try:
    b=batch([("eth_blockNumber",[])],endpoint=EPS[0],timeout=8)
    out["block"]=int(b[0],16)
except Exception as e:
    out["block"]=f"ERR:{e}"
print(json.dumps(out,indent=1))
json.dump(out,open("hot-leg-2026-11-08-0544-pumpkin.json","w"),indent=1)
