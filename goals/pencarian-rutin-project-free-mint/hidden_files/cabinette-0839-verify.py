import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
ADDR="0xa8543350e5accacc780c9613bfa2fb9b52d3858e"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def to_int(v):
    try: return int(v,16)
    except Exception: return None
def call(sig, args=None, ep=None):
    data=sel(sig)
    if args:
        for a in args:
            data+= enc_addr(a) if isinstance(a,str) and a.startswith("0x") else enc_u(a)
    eps=[ep] if ep else EPS
    for e in eps:
        try:
            r=batch([("eth_call",[{"to":ADDR,"data":data},"latest"])], endpoint=e, timeout=8)
            return to_int(r[0])
        except Exception: pass
    return None
def call_str(sig):
    data=sel(sig)
    for e in EPS:
        try:
            r=batch([("eth_call",[{"to":ADDR,"data":data},"latest"])], endpoint=e, timeout=8)
            raw=r[0]
            if not raw or raw=="0x": return None
            b=bytes.fromhex(raw[2:])
            if len(b)<64: return None
            off=int.from_bytes(b[0:32],"big"); ln=int.from_bytes(b[off:off+32],"big")
            return b[off+32:off+32+ln].decode(errors="ignore")
        except Exception: pass
    return None
try:
    b=batch([("eth_blockNumber",[])], endpoint=EPS[0], timeout=8)
    block=int(b[0],16)
except Exception as e:
    block=None
out={"address":ADDR,"block":block}
out["name"]=call_str("name()")
out["symbol"]=call_str("symbol()")
for sig in ["totalSupply()","freeClaimed()","FREE_SUPPLY()","FREE_CAP()","FREE_PER_WALLET()","MAX_SUPPLY()","mintOpen()","owner()"]:
    out[sig[:-2]]=call(sig)
for sig,args in [("freeLeft(address)",[USER]),("freeUsed(address)",[USER]),("mintedBy(address)",[USER]),("balanceOf(address)",[USER]),("freeClaimed(address)",[USER]),("freeFor(address,uint256)",[USER,1]),("quote(address,uint256)",[USER,1]),("priceFor(address)",[USER])]:
    key=sig.split("(")[0]+"_user"
    out[key]=call(sig,args)
json.dump(out, open("cabinette-0839-verify.json","w"), indent=1)
print(json.dumps(out, indent=1))
