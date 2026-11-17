import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
ADDR="0x1fab92b937572c79550aeee51cee77d3add20367"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def to_int(v):
    try: return int(v,16)
    except Exception: return None
def single(sig, args=None, ret_str=False):
    data=sel(sig)
    if args:
        for a in args:
            data+=enc_addr(a) if isinstance(a,str) and a.startswith("0x") else enc_u(a)
    for ep in EPS:
        try:
            res=batch([("eth_call",[{"to":ADDR,"data":data},"latest"])], endpoint=ep, timeout=8)
            if ret_str:
                return res[0]
            return to_int(res[0])
        except Exception:
            continue
    return None
def dec_str(hexdata):
    if not hexdata or hexdata=="0x": return None
    try:
        b=bytes.fromhex(hexdata[2:])
        off=int.from_bytes(b[32:64],"big"); ln=int.from_bytes(b[64+off-32:64+off] if False else b[32+off:64+off],"big") if False else None
        # standard ABI string: [0:32]=offset, [32:64]=length at offset, then data
        ln=int.from_bytes(b[32:64],"big")
        return b[64:64+ln].decode("utf-8","replace")
    except Exception as e:
        return f"<decode err {e}>"
out={}
out["name"]=dec_str(single("name()", ret_str=True))
out["symbol"]=dec_str(single("symbol()", ret_str=True))
out["contractURI"]=dec_str(single("contractURI()", ret_str=True))
for sig in ["totalSupply()","freeClaimed()","FREE_SUPPLY()","FREE_PER_WALLET()","MAX_SUPPLY()","PRICE()","mintOpen()"]:
    out[sig[:-2]]=single(sig)
out["AGENT_ID"]=single("AGENT_ID()", ret_str=True)
out["owner"]=single("owner()", ret_str=True)
out["quote_user1"]=single("quote(address,uint256)",[USER,1])
out["freeFor_user1"]=single("freeFor(address,uint256)",[USER,1])
out["freeLeft_user"]=single("freeLeft(address)",[USER])
out["freeUsed_user"]=single("freeUsed(address)",[USER])
out["mintedBy_user"]=single("mintedBy(address)",[USER])
out["balanceOf_user"]=single("balanceOf(address)",[USER])
try:
    b=batch([("eth_blockNumber",[])], endpoint=EPS[0], timeout=8)
    out["block"]=int(b[0],16)
except Exception as e:
    out["block"]=None
print(json.dumps(out,indent=1,default=str))
json.dump(out, open("hot-leg-2026-11-08-0719-1fab-read.json","w"), indent=1)
