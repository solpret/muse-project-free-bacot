import json, sys, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
A="0x74bDA11E34EB02121104Ff38471D91Fe1C37F81A"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/"]
VIEWS=["mintOpensAt()","FREE_POOL()","CLAIM_WINDOW()","claimDeadline()","PAID_PRICE()","MYTHIC_PRICE()","PAID_POOL()","claimAmountOf(address)","claimed(address)","freeMinted(address)","freeUsed(address)","mintFree()","pair()","token()","factory()","poolSeeded()","selloutTime()","randomRemaining()","totalClaimedPaid()","paidMinted()","mythicMinted()"]
def one(ep, sig):
    if "(address)" in sig: data=sel(sig)+enc(USER)
    else: data=sel(sig)
    try:
        r=batch([("eth_call",[{"to":A,"data":data},"latest"])], endpoint=ep, timeout=10)
        return r[0]
    except Exception as e:
        return f"ERR:{str(e)[:80]}"
out={}
for sig in VIEWS:
    vals=[one(ep,sig) for ep in EPS]
    v=next((x for x in vals if not str(x).startswith("ERR")), vals[0])
    try: iv=int(v,16) if isinstance(v,str) and v.startswith("0x") else v
    except Exception: iv=v
    print(sig,"->",v,"=",iv,flush=True); out[sig]=v
# ABI inputs for registry/freeUsed/mintFree/claim
r=subprocess.run(["curl","-s","-m","30",f"https://sourcify.dev/server/v2/contract/56/{A}?fields=abi"],capture_output=True,text=True,timeout=40)
try:
    d=json.loads(r.stdout); abi=d.get("stdJson",{}).get("output",{}).get("abi") or d.get("abi")
    for x in abi:
        if x.get("type")=="function" and x.get("name") in ("registry","freeUsed","freeMinted","mintFree","claim","claimAmountOf","claimed","mintPaid","mintMythic"):
            print("ABI:", x.get("name"), [i.get("type") for i in x.get("inputs",[])], "->", [o.get("type") for o in x.get("outputs",[])], "stateMutability:", x.get("stateMutability"), flush=True)
    out["_abi_ok"]=True
except Exception as e:
    print("ABI fetch err:", e); out["_abi_ok"]=False
json.dump(out, open("run-2026-11-07-0831-oni2.json","w"), indent=1)
