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
VIEWS=["name()","symbol()","totalSupply()","totalMinted()","MAX_SUPPLY()","FREE_SUPPLY()","freeClaimed(address)","freeFor(address)","freeLeft()","freeUsed()","freeMinted()","mintOpen()","owner()","agentId()","AGENT_ID()","agentRegistry()","REGISTRY()","PRICE()","mintPrice()"]
def one(ep, sig):
    if "(address)" in sig: data=sel(sig)+enc(USER)
    else: data=sel(sig)
    try:
        r=batch([("eth_call",[{"to":A,"data":data},"latest"])], endpoint=ep, timeout=10)
        return r[0]
    except Exception as e:
        return f"ERR:{e}"
out={}
for sig in VIEWS:
    vals=[one(ep,sig) for ep in EPS]
    # take first non-error
    v=next((x for x in vals if not str(x).startswith("ERR")), vals[0])
    print(sig,"->",v,flush=True); out[sig]=v
# decode name/symbol
def dec_str(h):
    try:
        b=bytes.fromhex(h[2:])
        if len(b)>=128:
            ln=int.from_bytes(b[64:96],'big'); return b[96:96+ln].decode(errors='replace')
    except Exception: return None
    return None
for k in ("name()","symbol()"):
    if isinstance(out.get(k),str) and out[k].startswith("0x"):
        print(k,"decoded:",dec_str(out[k]))
        out[k+"_decoded"]=dec_str(out[k])
# quote(address,uint256) and quote(uint256) separately
for sig,args in [("quote(address,uint256)",enc(USER)+"0"*63+"1"),("quote(uint256)","0"*63+"1")]:
    data=sel(sig)+args
    vals=[]
    for ep in EPS:
        try: vals.append(batch([("eth_call",[{"to":A,"data":data},"latest"])], endpoint=ep, timeout=10)[0])
        except Exception as e: vals.append(f"ERR:{e}")
    v=next((x for x in vals if not str(x).startswith("ERR")), vals[0])
    print(sig,"->",v,flush=True); out[sig]=v
r=subprocess.run(["curl","-s","-m","30",f"https://sourcify.dev/server/v2/contract/56/{A}?fields=abi"],capture_output=True,text=True,timeout=40)
d=json.loads(r.stdout); abi=d.get("stdJson",{}).get("output",{}).get("abi") or d.get("abi")
names=sorted(set(x.get("name") for x in abi if x.get("type")=="function"))
print("FN NAMES:", names); out["_abi_fns"]=names; out["_match"]=d.get("match")
json.dump(out, open("run-2026-11-07-0831-feed-hit.json","w"), indent=1)
