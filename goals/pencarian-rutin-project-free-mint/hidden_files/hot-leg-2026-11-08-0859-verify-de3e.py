import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
ADDR="0xde3e3e9e2f87f285f0f26ea54923a933b10df140"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def to_int(v):
    try: return int(v,16)
    except Exception: return None
def single(sig, args=None, ret="int"):
    data=sel(sig)
    if args:
        for a in args:
            data += enc_addr(a) if isinstance(a,str) and a.startswith("0x") else enc_u(a)
    for ep in EPS:
        try:
            res=batch([("eth_call",[{"to":ADDR,"data":data},"latest"])], endpoint=ep, timeout=8)
            r=res[0]
            if ret=="raw": return r
            return to_int(r)
        except Exception:
            continue
    return None
def single_str(sig):
    data=sel(sig)
    for ep in EPS:
        try:
            res=batch([("eth_call",[{"to":ADDR,"data":data},"latest"])], endpoint=ep, timeout=8)
            r=res[0]
            if r and len(r)>130:
                ln=int(r[66:130],16)
                s=bytes.fromhex(r[130:130+ln*2]).decode(errors="replace")
                return s
            return r
        except Exception:
            continue
    return None
out={}
out["freeClaimed"]=single("freeClaimed()")
out["FREE_SUPPLY"]=single("FREE_SUPPLY()")
out["FREE_PER_WALLET"]=single("FREE_PER_WALLET()")
out["totalSupply"]=single("totalSupply()")
out["MAX_SUPPLY"]=single("MAX_SUPPLY()")
out["PRICE"]=single("PRICE()")
out["mintOpen"]=single("mintOpen()")
out["freeLeft_user"]=single("freeLeft(address)",[USER])
out["freeUsed_user"]=single("freeUsed(address)",[USER])
out["mintedBy_user"]=single("mintedBy(address)",[USER])
out["balanceOf_user"]=single("balanceOf(address)",[USER])
out["quote_user1"]=single("quote(address,uint256)",[USER,1])
out["freeFor_user1"]=single("freeFor(address,uint256)",[USER,1])
out["name"]=single_str("name()")
out["symbol"]=single_str("symbol()")
out["AGENT_ID_raw"]=single("AGENT_ID()",ret="raw")
out["owner_raw"]=single("owner()",ret="raw")
out["contractURI"]=single_str("contractURI()")
try:
    b=batch([("eth_blockNumber",[])], endpoint=EPS[0], timeout=8)
    out["block"]=int(b[0],16)
except Exception as e:
    out["block_error"]=str(e)
json.dump(out, open("hot-leg-2026-11-08-0859-verify-de3e.json","w"), indent=1)
print(json.dumps(out, indent=1))
