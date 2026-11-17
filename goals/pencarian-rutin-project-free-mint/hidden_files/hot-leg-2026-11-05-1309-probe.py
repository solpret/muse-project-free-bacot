import json, urllib.request
from Crypto.Hash import keccak
RPCS=["https://bsc.publicnode.com","https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:50]}
            return out["result"]
        except Exception: continue
    return {"error":"rpc-fail"}
def cint(v):
    if isinstance(v,dict): return v
    try: return int(v,16) if v and v!="0x" else 0
    except Exception: return v
def cstr(v):
    if isinstance(v,dict) or not v or v=="0x": return v
    try:
        h=v[2:]; ln=int(h[64:128],16); return bytes.fromhex(h[128:128+ln*2]).decode(errors="replace")
    except Exception: return v
def abi_of(a):
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",headers={"User-Agent":"curl"})
        with urllib.request.urlopen(req,timeout=15) as r: d=json.load(r)
        return d.get("abi") or d.get("stdJson",{}).get("abi") or []
    except Exception as e:
        return {"error":str(e)[:80]}
out={}
# ECHI + SHAG: WEBSITE/TWITTER constants + quote + spots
for a in ["0x5AC18bF9Ac3782F68aaC0523f0a1c576fe05aba6","0xbF097aef8287E089fBC55b3ae65Ee2265cD26BD5"]:
    o={}
    for fn in ["WEBSITE()","TWITTER()","PRICE()","totalSpotsMinted()","spotsLeft()","totalSupply()","mintOpen()"]:
        v=raw(a, sel(fn))
        o[fn]=cstr(v) if fn in ("WEBSITE()","TWITTER()") else cint(v)
    qd=sel("quote(address,uint256)")+enc(USER)+"0000000000000000000000000000000000000000000000000000000000000001"
    o["quote(user,1)"]=cint(raw(a,qd))
    ag=raw(a, sel("AGENT_REGISTRY()"))
    o["AGENT_REGISTRY()"]=ag
    out[a]=o
# Tumblebots + Smeltbots: full ABI grep for registry + agent refs; probe free views
for a in ["0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17","0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e"]:
    abi=abi_of(a)
    o={}
    if isinstance(abi,dict): o["abi_error"]=abi
    else:
        fns=sorted({f.get("name") for f in abi if f.get("type")=="function" and f.get("name")})
        o["_abi_functions"]=fns
        o["_abi_json_has_registry"]=REG in json.dumps(abi).lower()
        o["_abi_agent_names"]=[f for f in fns if "agent" in f.lower() or "registry" in f.lower() or "gate" in f.lower()]
    for fn,frm in [("canFreeMint(address)",USER),("claimedFree(address)",USER),("freeMinted()",None),("FREE_CAP()",None),("PRICE()",None),("totalSupply()",None),("paidMinted()",None)]:
        v=raw(a, sel(fn)+(enc(frm) if frm else ""))
        o[fn]=cint(v)
    qd=sel("quote(address,uint256)")+enc(USER)+"0000000000000000000000000000000000000000000000000000000000000001"
    o["quote(user,1)"]=cint(raw(a,qd))
    out[a]=o
# Boltbook addresses: AGCC + LOOTPASS shape probe (ABI fns + key views)
for a in ["0x6288DFe86f22B53eD86886aE2D78941de7483743","0x7ae571216492715f7f6f0a6640ecae4f15d1444b"]:
    abi=abi_of(a)
    o={}
    if isinstance(abi,dict): o["abi_error"]=abi
    else:
        fns=sorted({f.get("name") for f in abi if f.get("type")=="function" and f.get("name")})
        o["_abi_functions"]=fns
        o["_abi_json_has_registry"]=REG in json.dumps(abi).lower()
    for fn,frm in [("name()",None),("symbol()",None),("totalSupply()",None),("freeMinted()",None),("FREE_SLOTS()",None),("FREE_SUPPLY()",None),("freeLeft(address)",USER),("freeClaimed(address)",USER),("mintedBy(address)",USER),("mintOpen()",None),("agentRegistry()",None),("AGENT_REGISTRY()",None)]:
        v=raw(a, sel(fn)+(enc(frm) if frm else ""))
        o[fn]=cstr(v) if fn in ("name()","symbol()") else cint(v)
    qd=sel("quote(address,uint256)")+enc(USER)+"0000000000000000000000000000000000000000000000000000000000000001"
    o["quote(user,1)"]=cint(raw(a,qd))
    out[a]=o
print(json.dumps(out,indent=1))
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-1309-probe.json","w"),indent=1)
