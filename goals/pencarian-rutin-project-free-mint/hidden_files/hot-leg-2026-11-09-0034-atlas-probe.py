import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
ADDR="0x5cfebb581e5c95303eb546f280f430573bb3c59e"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def call(sig, args=None, ep=None):
    data=sel(sig)
    if args:
        for a in args:
            data+= enc_addr(a) if isinstance(a,str) and a.startswith("0x") else enc_u(a)
    eps=[ep] if ep else EPS
    for e in eps:
        try:
            res=batch([("eth_call",[{"to":ADDR,"data":data},"latest"])], endpoint=e, timeout=8)
            return res[0]
        except Exception:
            continue
    return None
def u(v):
    try: return int(v,16)
    except Exception: return None
def s_decode(v):
    try:
        b=bytes.fromhex(v[2:])
        off=int.from_bytes(b[32:64],"big"); ln=int.from_bytes(b[64:96],"big")
        return b[96:96+ln].decode("utf-8","replace")
    except Exception as ex:
        return f"DECODE-ERR {ex} raw={str(v)[:120]}"
out={}
for sig in ["freeMinted()","FREE_SUPPLY()","freeRemaining()","totalMinted()","MAX_SUPPLY()","START_BLOCK()","currentEpoch()","lastMintAt()","AGENT_ID()"]:
    out[sig]=u(call(sig))
out["quote_user"]=u(call("quote(address)",[USER]))
out["mintedBy_user"]=u(call("mintedBy(address)",[USER]))
out["balanceOf_user"]=u(call("balanceOf(address)",[USER]))
out["hasAgentId_user"]=u(call("hasAgentId(address)",[USER]))
out["name"]=s_decode(call("name()"))
out["symbol"]=s_decode(call("symbol()"))
out["contractURI"]=s_decode(call("contractURI()"))
out["status_user"]=u(call("status(address)",[USER]))
try:
    b=batch([("eth_blockNumber",[])], endpoint=EPS[0], timeout=8)
    out["block"]=int(b[0],16)
except Exception as e:
    out["block_error"]=str(e)
print(json.dumps(out,indent=1))
json.dump(out, open("hot-leg-2026-11-09-0034-atlas-probe.json","w"), indent=1)
