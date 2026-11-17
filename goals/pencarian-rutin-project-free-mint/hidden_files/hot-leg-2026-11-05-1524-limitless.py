import json, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-05-1524"
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:80]}
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
def abi_of(a):
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",headers={"User-Agent":"curl"})
        with urllib.request.urlopen(req,timeout=15) as r: d=json.load(r)
        return d.get("abi") or d.get("stdJson",{}).get("abi") or []
    except Exception as e: return {"error":str(e)[:100]}
A="0xc7aA008c2369FF00322c49D526F33529bB692a86"
abi=abi_of(A)
FREE=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed"]
if isinstance(abi,dict):
    print("ABI ERR", abi); res={"abi_error":abi}
else:
    fns=sorted({f.get("name") for f in abi if f.get("type")=="function" and f.get("name")})
    has_mint=any(n.startswith("mint") for n in fns)
    has_quote="quote" in fns
    free=[f for f in fns if any(x in f for x in FREE)]
    agent=("agentRegistry" in fns or "AGENT_REGISTRY" in fns or "registry" in fns or REG in json.dumps(abi).lower())
    is_token=("name" in fns and "symbol" in fns and "decimals" in fns and "totalSupply" in fns)
    has_mintfree="mintFree" in fns
    s1=has_mint and has_quote and bool(free) and agent
    s2=is_token and has_mintfree and ("freeClaimed" in fns or "freeMinted" in fns) and ("FREE_SLOTS" in fns or "FREE_SUPPLY" in fns) and agent
    nft_agent=has_mint and bool(free) and agent
    print("LIMITLESS fns:",fns)
    print("S1",s1,"S2",s2,"nft_agent",nft_agent,"mint",has_mint,"quote",has_quote,"free",free,"agent",agent,"token",is_token)
    res={"S1":s1,"S2":s2,"nft_agent_shape":nft_agent,"mint":has_mint,"quote":has_quote,"free":free,"agent":agent,"token":is_token,"fns":fns}
    # on-chain reads (generic NFT free-mint shape)
    reads={}
    for fn in ["name()","symbol()","totalSupply()","freeMinted()","freeClaimed()","FREE_SUPPLY()","FREE_CAP()","MAX_SUPPLY()","maxSupply()","contractURI()","owner()"]:
        v=raw(A,sel(fn)); reads[fn]=cstr(v) if fn in ("name()","symbol()","contractURI()","owner()") else cint(v)
    reads["balanceOf(user)"]=cint(raw(A,sel("balanceOf(address)")+enc(USER)))
    for fn in ["mintedBy(address)","freeUsed(address)","claimedFree(address)","freeClaimed(address)","freeMinted(address)"]:
        v=raw(A,sel(fn)+enc(USER)); reads[fn+"(user)"]=cint(v)
    print(json.dumps(reads,indent=1))
    res["onchain"]=reads
json.dump(res,open(f"{BASE}/hot-leg-{TS}-limitless.json","w"),indent=1)
print("saved limitless check")
