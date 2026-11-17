import json, urllib.request
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
A="0x7561C414A7a6Ff44Fc81e9BFC2eda8F57C3EC61e"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=15) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:120]}
            return out["result"]
        except Exception: continue
    return {"error":"rpc-fail"}
def cint(v):
    if isinstance(v,dict) or not v or v=="0x": return v
    try: return int(v,16)
    except Exception: return v
def cstr(v):
    if isinstance(v,dict) or not v or v=="0x": return v
    try:
        h=v[2:]; ln=int(h[64:128],16); return bytes.fromhex(h[128:128+ln*2]).decode(errors="replace")
    except Exception: return v
def block():
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None
res={"block":block(),"address":A}
for fn in ["name()","symbol()","totalSupply()","totalMinted()","freeMinted()","freeClaimed()","MAX_SUPPLY()","FREE_SUPPLY()","mintOpen()","paused()","owner()"]:
    v=raw(A,sel(fn)); res[fn]=cstr(v) if fn in ("name()","symbol()") else cint(v)
for fn in ["balanceOf(address)","mintedBy(address)","freeClaimed(address)","freeUsed(address)","claimedFree(address)"]:
    v=raw(A,sel(fn)+enc(USER)); res[fn+"(user)"]=cint(v)
for fn in ["quote(address,uint256)"]:
    v=raw(A,sel(fn)+enc(USER)+"0000000000000000000000000000000000000000000000000000000000000001"); res[fn+"(user,1)"]=cint(v)
# contractURI / tokenURI(0) raw (may be long)
for fn in ["contractURI()"]:
    v=raw(A,sel(fn)); res[fn]=v if isinstance(v,dict) else (v[:600] if v else v)
# Sourcify ABI function list
try:
    req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{A}?fields=abi",headers={"User-Agent":"curl"})
    with urllib.request.urlopen(req,timeout=20) as r: d=json.load(r)
    abi=d.get("abi") or []
    res["abi_functions"]=sorted({f.get("name") for f in abi if f.get("type")=="function" and f.get("name")})
    res["sourcify_match"]=d.get("match") or d.get("stdJson",{}).get("match")
except Exception as e:
    res["sourcify_error"]=str(e)[:120]
print(json.dumps(res,indent=1))
json.dump(res,open(f"{BASE}/run-2026-11-05-1431-agentpanda.json","w"),indent=1)
