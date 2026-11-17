import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
U=USER.lower().replace("0x","").rjust(64,"0")
def u1(n): return format(n,"064x")
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.defibit.io/","https://bsc.nodereal.io/"]
def batch(calls):
    # calls: list of (key,to,data)
    payload=[{"jsonrpc":"2.0","id":i,"method":"eth_call","params":[{"to":to,"data":data},"latest"]} for i,(k,to,data) in enumerate(calls)]
    for ep in EPS:
        try:
            r=subprocess.run(["curl","-s","-m","25","-H","Content-Type: application/json","-d",json.dumps(payload),ep],capture_output=True,timeout=30)
            arr=json.loads(r.stdout.decode(errors="replace"))
            if isinstance(arr,list) and arr and all("result" in it or "error" in it for it in arr):
                res={}
                for it in arr:
                    i=it.get("id")
                    if i is None or i>=len(calls): continue
                    res[calls[i][0]]=it.get("result") if "result" in it else None
                return res
        except Exception: continue
    return {k:None for k,_,_ in calls}
def dec_u(res):
    if not res or len(res)<66: return None
    try: return int(res[2:66],16)
    except Exception: return None
def dec_s(res):
    if not res or len(res)<130: return None
    try:
        ln=int(res[66:130],16)
        return bytes.fromhex(res[130:130+ln*2]).decode(errors="replace")
    except Exception: return None
def dec_b(res):
    v=dec_u(res); return None if v is None else v!=0
def dec_addr(res):
    if not res or len(res)<66: return None
    return "0x"+res[26:66]
W="0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C"
A1="0xad0D8ac3D61fC8ab397B7136C69fcBf1281a4998"
A2="0x5777c2f59c65003DDebb018517B09f7ba0691202"
calls=[]
def add(key,to,sig,args=""):
    calls.append((key,to,sel(sig)+args))
for pfx,A in [("W",W),("A1",A1),("A2",A2)]:
    add(pfx+".cost_user_1",A,"cost(address,uint256)",U+u1(1))
    add(pfx+".freeClaimed_user",A,"freeClaimed(address)",U)
    add(pfx+".freeAvailable_user",A,"freeAvailable(address)",U)
    add(pfx+".mintedBy_user",A,"mintedBy(address)",U)
    add(pfx+".freeMinted",A,"freeMinted()")
    add(pfx+".freeClaimed_tot",A,"freeClaimed()")
    add(pfx+".FREE_SUPPLY",A,"FREE_SUPPLY()")
    add(pfx+".MAX_SUPPLY",A,"MAX_SUPPLY()")
    add(pfx+".totalSupply",A,"totalSupply()")
    add(pfx+".mintOpen",A,"mintOpen()")
    add(pfx+".price",A,"price()")
    add(pfx+".name",A,"name()")
    add(pfx+".symbol",A,"symbol()")
    add(pfx+".AGENT_ID",A,"AGENT_ID()")
    add(pfx+".owner",A,"owner()")
    add(pfx+".contractURI",A,"contractURI()")
raw=batch(calls)
out={}
for pfx in ("W","A1","A2"):
    out[pfx]={
      "cost_user_1":dec_u(raw.get(pfx+".cost_user_1")),
      "freeClaimed_user":dec_u(raw.get(pfx+".freeClaimed_user")),
      "freeAvailable_user":dec_u(raw.get(pfx+".freeAvailable_user")),
      "mintedBy_user":dec_u(raw.get(pfx+".mintedBy_user")),
      "freeMinted":dec_u(raw.get(pfx+".freeMinted")),
      "freeClaimed_tot":dec_u(raw.get(pfx+".freeClaimed_tot")),
      "FREE_SUPPLY":dec_u(raw.get(pfx+".FREE_SUPPLY")),
      "MAX_SUPPLY":dec_u(raw.get(pfx+".MAX_SUPPLY")),
      "totalSupply":dec_u(raw.get(pfx+".totalSupply")),
      "mintOpen":dec_b(raw.get(pfx+".mintOpen")),
      "price":dec_u(raw.get(pfx+".price")),
      "name":dec_s(raw.get(pfx+".name")),
      "symbol":dec_s(raw.get(pfx+".symbol")),
      "AGENT_ID":dec_u(raw.get(pfx+".AGENT_ID")),
      "owner":dec_addr(raw.get(pfx+".owner")),
      "contractURI":dec_s(raw.get(pfx+".contractURI")),
    }
# block number
for ep in EPS:
    try:
        r=subprocess.run(["curl","-s","-m","10","-H","Content-Type: application/json","-d",json.dumps({"jsonrpc":"2.0","id":0,"method":"eth_blockNumber","params":[]}),ep],capture_output=True,timeout=15)
        j=json.loads(r.stdout.decode(errors="replace"))
        if j.get("result"): out["block"]=int(j["result"],16); break
    except Exception: continue
json.dump(out,open("hot-leg-2026-11-12-0554-verify-new.json","w"),indent=1)
print(json.dumps(out,indent=1))
