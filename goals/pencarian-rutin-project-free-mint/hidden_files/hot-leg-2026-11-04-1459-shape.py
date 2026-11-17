import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed3.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,data):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=p,headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=6) as r: v=json.load(r)["result"]
            return v if v and v!="0x" else None
        except Exception: continue
    return None
def iv(v):
    try: return int(v,16) if v else None
    except Exception: return None
def sv(v):
    try:
        if not v or len(v)<130: return None
        ln=int(v[66:130],16); return bytes.fromhex(v[130:130+ln*2]).decode(errors="replace")
    except Exception: return None
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0")
FEED=['0x510fb80d3eb9a9BB278c58339e72E159c4e673B0','0x2b5867fd2F342b295C71e8D8f382E9Ae69276287','0xfE4afec0604fd0dDB73673846f119CDae78fbc19','0xf7851c6F4dAbA06dAFB3296e879D5941633552EF','0xD7Cc46ADA7b230FbF133d8Ff1068481406033331','0x8bfF603BfBB79dB20972aa8cbe6294f192348d89']
def probe(a):
    out={"name":sv(call(a,sel("name()"))),"symbol":sv(call(a,sel("symbol()"))),"decimals":iv(call(a,sel("decimals()"))),"totalSupply":iv(call(a,sel("totalSupply()")))}
    for f in ["freeClaimed()","freeMinted()","FREE_SLOTS()","FREE_SUPPLY()","freeSharesRemaining()","freeSharesClaimed()","freeClaimed(address)","freeUsed(address)","mintedBy(address)","balanceOf(address)"]:
        arg=u if f.endswith("(address)") else ""
        out[f]=iv(call(a,sel(f)+arg))
    out["agentRegistry"]=call(a,sel("agentRegistry()")); out["registry"]=call(a,sel("registry()")); out["contractURI"]=sv(call(a,sel("contractURI()")))
    return out
with ThreadPoolExecutor(max_workers=20) as ex: res=list(ex.map(probe,FEED))
out=dict(zip(FEED,res))
for a,r in out.items(): print(a, r)
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-04-1459-shape.json","w"),indent=1)
print("SALE_SHAPE_HITS:")
for a,r in out.items():
    freeviews=[r.get(f) for f in ("freeClaimed()","freeMinted()","FREE_SLOTS()","FREE_SUPPLY()","freeSharesRemaining()","freeSharesClaimed()")]
    reg = r.get("agentRegistry") or r.get("registry")
    if any(v is not None for v in freeviews) or reg: print(" ",a,r)
