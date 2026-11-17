import json, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RPCS=["https://bsc.publicnode.com","https://bsc-dataseed1.bnbchain.org"]
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
            if "error" in out: return {"error":str(out["error"])[:60]}
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
    except Exception as e: return {"error":str(e)[:80]}
FREE=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed"]
out={}
# Boltbook new addresses: shape-check
for a in ['0x8F0528cE5Ff7B55e22315754d8aE412d4D33952d','0x97F03175E2EDAB6feDd722241367439abF66F37A','0x98C92Aad727608744DD681126046c07701D73705','0xE02dF9e4e622DeBDD43d8312fC4933528b173774','0xaa05bb33a462e396867e9244055303a55f796666']:
    abi=abi_of(a)
    fns=sorted({f.get("name") for f in abi if isinstance(abi,list) and f.get("type")=="function" and f.get("name")}) if isinstance(abi,list) else []
    e={"abi_functions":fns}
    if isinstance(abi,dict): e["abi_error"]=abi
    has_mint=any(n.startswith("mint") for n in fns); has_quote="quote" in fns
    free=[f for f in fns if any(x in f for x in FREE)]
    agent=("agentRegistry" in fns or "AGENT_REGISTRY" in fns or "registry" in fns or (isinstance(abi,list) and REG in json.dumps(abi).lower()))
    is_token=("name" in fns and "symbol" in fns and "decimals" in fns and "totalSupply" in fns)
    e.update({"S1":has_mint and has_quote and bool(free) and agent,"S2":is_token and "mintFree" in fns and ("freeClaimed" in fns or "freeMinted" in fns) and ("FREE_SLOTS" in fns or "FREE_SUPPLY" in fns) and agent,"mint":has_mint,"quote":has_quote,"free":free,"agent":agent,"token":is_token})
    for fn in ["name()","symbol()","totalSupply()"]:
        v=raw(a,sel(fn)); e[fn]=cstr(v) if fn in ("name()","symbol()") else cint(v)
    out[a]=e; print("BB",a,e.get("S1"),e.get("S2"),e.get("name()"),e.get("symbol()"),e.get("free"),e.get("agent"),e["abi_functions"][:20])
# Spot-sale family names + PRICE/spotsLeft/WEBSITE/TWITTER
for a in ['0xDA40501eE9eA0718ee21dd036048450A4deA5Faa','0xc18a7caDb5ce5753941b7B5D427Ccde9e09c6249','0x5AC18bF9Ac3782F68aaC0523f0a1c576fe05aba6','0xbF097aef8287E089fBC55b3ae65Ee2265cD26BD5']:
    e={}
    for fn in ["name()","symbol()","totalSupply()","PRICE()","spotsLeft()","totalSpotsMinted()","WEBSITE()","TWITTER()"]:
        v=raw(a,sel(fn)); e[fn]=cstr(v) if fn in ("name()","symbol()","WEBSITE()","TWITTER()") else cint(v)
    out[a]=e; print("SPOT",a,e)
json.dump(out,open(f"{BASE}/hot-leg-2026-11-05-1324-boltbook-shape.json","w"),indent=1)
print(json.dumps(out,indent=1))
