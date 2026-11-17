import sys, json, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
def rpc(m,p,timeout=10):
    last=None
    for ep in EPS:
        try: return _single(ep,m,p,timeout,retries=0)
        except Exception as e: last=e
    raise last
def keccak_sel(sig):
    from Crypto.Hash import keccak
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def call(addr,sig,args=""):
    try: return rpc("eth_call",[{"to":addr,"data":keccak_sel(sig)+args},"latest"])
    except Exception as e: return f"ERR:{e}"
def di(h):
    try:
        if isinstance(h,str) and h.startswith("0x") and len(h)>=66: return int(h[2:66],16)
    except Exception: pass
    return None
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
uarg="0"*24+USER[2:].lower()
BOB="0x3BF121dC4c5a1Ba567F3eE801d0e447601726207"
AGP="0x71f86082C3b32601f865c63980a9B686e887EAB1"
print("BOBBIE freeUsed(user):",di(call(BOB,"freeUsed(address)",uarg)),flush=True)
print("BOBBIE quote(user,1,false):",di(call(BOB,"quote(address,uint256,bool)",uarg+"0"*63+"1"+"0"*63+"0")),flush=True)
print("BOBBIE quote(user,1,true):",di(call(BOB,"quote(address,uint256,bool)",uarg+"0"*63+"1"+"0"*63+"1")),flush=True)
print("BOBBIE mintEndsAt:",di(call(BOB,"mintEndsAt()")),"mintStartsAt:",di(call(BOB,"mintStartsAt()")),flush=True)
print("BOBBIE totalMinted now:",di(call(BOB,"totalMinted()")),"freeAllocated:",di(call(BOB,"freeAllocated()")),flush=True)
print("AGENTPAD totalMinted now:",di(call(AGP,"totalMinted()")),"mintOpen:",di(call(AGP,"mintOpen()")),flush=True)
r=subprocess.run(["curl","-sS","--max-time","25",f"https://sourcify.dev/server/v2/contract/56/{AGP}?fields=abi"],capture_output=True,text=True,timeout=40)
abi=json.loads(r.stdout).get("abi",[])
for f in abi:
    if f.get("type")=="function" and f.get("name") in ("mintFree","claimFree","mintPaid","claimableBy","freeMintedBy","nextFreeAt"):
        print("AGP ABI:",f.get("name"),"payable" if f.get("stateMutability")=="payable" else f.get("stateMutability"),"inputs:",[(i.get("type"),i.get("name")) for i in f.get("inputs",[])],"outputs:",[(o.get("type")) for o in f.get("outputs",[])],flush=True)
r2=subprocess.run(["curl","-sS","--max-time","25",f"https://sourcify.dev/server/v2/contract/56/{BOB}?fields=abi"],capture_output=True,text=True,timeout=40)
abi2=json.loads(r2.stdout).get("abi",[])
for f in abi2:
    if f.get("type")=="function" and f.get("name") in ("mint","quote","freeUsed","freeAllocated","settleMint"):
        print("BOB ABI:",f.get("name"),f.get("stateMutability"),"inputs:",[(i.get("type"),i.get("name")) for i in f.get("inputs",[])],flush=True)
