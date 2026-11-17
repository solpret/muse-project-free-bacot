import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR="0x28a4F0BbdC1bE886f9e5a290e6598A83F248B224"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc.publicnode.com/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def to_int(v):
    try: return int(v,16)
    except Exception: return None
def call(sig, args, ep):
    data=sel(sig)
    for a in args:
        data += enc(a) if isinstance(a,str) and a.startswith("0x") else enc_u(a)
    r=batch([("eth_call",[{"to":ADDR,"data":data},"latest"])], endpoint=ep, timeout=8)
    return r[0]
def call_str(sig, ep):
    data=sel(sig)
    r=batch([("eth_call",[{"to":ADDR,"data":data},"latest"])], endpoint=ep, timeout=8)
    raw=r[0]
    if not raw or raw=="0x": return None
    try:
        b=bytes.fromhex(raw[2:])
        off=int.from_bytes(b[32:64],"big"); ln=int.from_bytes(b[64:96],"big")
        return b[96:96+ln].decode()
    except Exception: return raw
VIEWS=[("name()",[]),("symbol()",[]),("freeMintsLeft()",[]),("freeMintLimit()",[]),("freeMintsUsed()",[]),("isFreeMintAvailable(address)",[USER]),("mintsOf(address)",[USER]),("mintOpen()",[]),("totalMints()",[]),("totalSupply()",[]),("currentPriceFor(address)",[USER]),("price()",[]),("currentStage()",[]),("currentTokensPerMint()",[]),("agentRegistry()",[]),("owner()",[]),("MAX_CAP()",[]),("balanceOf(address)",[USER])]
out={"address":ADDR,"started_wib":"2026-11-07 18:14 WIB"}
try:
    b=batch([("eth_blockNumber",[])], endpoint=EPS[0], timeout=8)
    out["block"]=int(b[0],16)
except Exception as e:
    out["block"]=None; print("BLOCK-FAIL",e,flush=True)
print("BLOCK",out["block"],flush=True)
for sig,args in VIEWS:
    val=None; used=None
    for ep in EPS:
        try:
            if sig in ("name()","symbol()"):
                val=call_str(sig, ep)
            else:
                raw=call(sig,args,ep); val=to_int(raw)
                if sig in ("agentRegistry()","owner()"):
                    val="0x"+format(val,"040x") if val is not None else None
            used=ep; break
        except Exception as e:
            continue
    key=sig.split("(")[0]+("_user" if args else "")
    out[key]=val
    print(f"{key}={val} [{used}]",flush=True)
json.dump(out,open(f"{BASE}/hot-leg-2026-11-07-1814-verify-28a4.json","w"),indent=1)
