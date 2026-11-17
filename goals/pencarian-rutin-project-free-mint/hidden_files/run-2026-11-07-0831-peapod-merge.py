import json, sys, time, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/"]
def read(addr, views):
    out={}
    for sig in views:
        if "(address)" in sig: data=sel(sig)+enc(USER)
        elif "(uint256)" in sig: data=sel(sig)+"0"*63+"1"
        elif sig.startswith("quote(address"):
            data=sel(sig)+enc(USER)+"0"*63+"1"
        else: data=sel(sig)
        val=None
        for ep in EPS:
            try:
                r=batch([("eth_call",[{"to":addr,"data":data},"latest"])], endpoint=ep, timeout=12)
                val=r[0]; break
            except Exception as e:
                val=f"ERR:{str(e)[:90]}"
                time.sleep(1)
        try: iv=int(val,16) if isinstance(val,str) and val.startswith("0x") else val
        except Exception: iv=val
        print(addr[:10], sig, "->", val, "=", iv, flush=True)
        out[sig]=(val,iv)
    return out
PP="0x25f3efb465685692ef3ddc47ed040baf216b5d38"
MB="0x348455be18b700cae8aa425bd84e456e47f16e8b"
res={}
print("=== PEA FUN POD ===")
res["peapod"]=read(PP,["name()","symbol()","totalSupply()","totalMinted()","MAX_SUPPLY()","FREE_SUPPLY()","freePodsRemaining()","freeClaimed(address)","freeFor(address)","freeLeft()","freeUsed()","freeMinted()","mintOpen()","owner()","agentId()","AGENT_ID()","agentRegistry()","REGISTRY()","quote(address,uint256)","quote(uint256)","PRICE()"])
print("=== MERGEBORN ===")
res["mergeborn"]=read(MB,["totalSupply()","totalMinted()","MAX_SUPPLY()","FREE_SUPPLY()","freeClaimed()","freeMinted()","freeLeft()","freeClaimed(address)","mintOpen()","owner()"])
# Sourcify ABI for peapod
for label,addr in [("peapod",PP)]:
    try:
        r=subprocess.run(["curl","-s","-m","30",f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],capture_output=True,text=True,timeout=40)
        d=json.loads(r.stdout); abi=d.get("stdJson",{}).get("output",{}).get("abi") or d.get("abi")
        names=sorted(set(x.get("name") for x in abi if x.get("type")=="function"))
        print(label,"SOURCIFY",d.get("match"),"fns",len(names),names,flush=True)
        res[label+"_abi"]={"match":d.get("match"),"fns":names}
    except Exception as e:
        print(label,"ABI ERR",e,flush=True); res[label+"_abi"]={"error":str(e)}
json.dump(res, open("run-2026-11-07-0831-peapod-merge.json","w"), indent=1, default=str)
