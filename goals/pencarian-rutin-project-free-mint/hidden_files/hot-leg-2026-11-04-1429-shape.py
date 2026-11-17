import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
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
FEED=["0x8d33a3BD349d77E3e7684F0B1D5FeE611D5B644f","0xf58d3e2dFb6567d48f7eE952c051f44EC149Cc81","0x22B73414073B97BC048C9C9DEeA92e37809543Ff","0x0A6378b96166823c87f3A0C705Ef15bb2DD16552","0x9124D6c0f30db2eAB1933A2b21dB02C826e74B18","0xB4C4aE9C78Fe59Ab7bD56837159B0E45A2d6e9eE","0x4Acf79D1DEc7452232FdaDABf6025c9cC2735D34","0x3c9B60A2d1c422e15ce3F8c36568745Ca7061703","0x2f60D3c58dABf1386BC1F28e0851069F93FA15BE","0xFdA0727547a865FD46872554F584534C3BD9FC4d","0xCAce241Ff692Bca2173EC7D9863267be260523F1","0xA700E8Dd334451Cbe1304C8ADfCE7f67798A3bb1","0xB1BCF66c430Cd08092581C4b4c63EcFe178da7bf","0xB5d21D20162D10c5F0d23e3519091643F58f8F79","0x7a5547773bb3005C1DB70702bb9b3B51C93E71fe","0xE65D92b5A3BFf82d2D0682F852AE752065f910f6","0xf1713DC58fD88f786F99812dE5B73C256294Df9F","0x7d14Cc496855baC1D789DdB459EFd619eE606908","0x416a426Dd1a653A123D200af22f3458c1eba3E41","0xDBa25A08F8829F0EDfa3cbe019a8CeE6d6172cff"]
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
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-04-1429-shape.json","w"),indent=1)
print("SALE_SHAPE_HITS:")
for a,r in out.items():
    freeviews=[r.get(f) for f in ("freeClaimed()","freeMinted()","FREE_SLOTS()","FREE_SUPPLY()","freeSharesRemaining()","freeSharesClaimed()")]
    reg = r.get("agentRegistry") or r.get("registry")
    if any(v is not None for v in freeviews) or reg: print(" ",a,r)
