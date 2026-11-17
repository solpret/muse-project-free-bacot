import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
def sel(s):
    return "0x"+keccak.new(digest_bits=256, data=s.encode()).hexdigest()[:8]
A="0x25f3efb465685692ef3ddc47ed040baf216b5d38"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/"]
fns=["name()","symbol()","totalSupply()","MAX_SUPPLY()","FREE_SUPPLY()","freePodsRemaining()","freeClaimed(address)","freeFor(address)","freeLeft()","freeUsed()","mintOpen()","owner()","agentId()","AGENT_ID()","agentRegistry()","REGISTRY()","quote(address,uint256)","quote(uint256)"]
calls=[]
for f in fns:
    if "(address" in f:
        data=sel(f)+"000000000000000000000000"+USER[2:].lower()
    elif "(uint256" in f:
        data=sel(f)+"0000000000000000000000000000000000000000000000000000000000000001"
    elif f.startswith("quote(address"):
        data=sel(f)+"000000000000000000000000"+USER[2:].lower()+"0000000000000000000000000000000000000000000000000000000000000001"
    else:
        data=sel(f)
    calls.append(("eth_call",[{"to":A,"data":data},"latest"]))
res=batch(calls, timeout=20)
out={}
for f,r in zip(fns,res):
    out[f]=r
    print(f, "->", r, flush=True)
# Sourcify ABI
try:
    req=urllib.request.Request(f"https://sourcify.dev/server/v2/contracts/56/{A}", headers={"User-Agent":"curl/8"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        d=json.load(resp)
    abi=d.get("stdJson",{}).get("output",{}).get("abi") or d.get("abi")
    if abi:
        names=[x.get("name") for x in abi if x.get("type")=="function"]
        print("SOURCIFY match:", d.get("match"), "fns:", len(names))
        print("FN NAMES:", sorted(set(names)))
        out["_sourcify_match"]=d.get("match"); out["_abi_fns"]=sorted(set(names))
    else:
        print("SOURCIFY no abi, match:", d.get("match"))
        out["_sourcify_match"]=d.get("match")
except Exception as e:
    print("SOURCIFY ERROR:", e)
    out["_sourcify_error"]=str(e)
json.dump(out, open("run-2026-11-07-0831-peapod.json","w"), indent=1)
