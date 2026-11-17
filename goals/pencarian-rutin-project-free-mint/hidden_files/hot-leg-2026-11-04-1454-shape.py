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
FEED=['0x860807b8dDBaacfB9785E7619fC7309f4519C160', '0xc020D036b56A8b224790093b19B7D51C6180c6a4', '0xF2e8f3B79eC513C065B4D239534Cf58040641700', '0xa821F0F6D70De954F770636b6f21Ba2E5bD3d3B6', '0x1eB1d4064cfD516ac08a8892Bc2f8BEaD4639993', '0x37408DB26D88F483ef0322AdC40E9B095A5aBD82', '0x75Bd37E0d9e210A9148fAB834745e5Cd001C0592', '0xB40CDD000D9d1f110D351DcA8207218d05bdd30C', '0xe13b1f772475e23673E46CEcF873D2A5A79D3bEA', '0xf522fb3E0DcFdA2EDd8a0C4F865eB1e8E51c0b09', '0xD315ba9F0e255A38aE04583cA9d580fBA93f98f3', '0x705b7Ee4DE02F0C60CA9653F07C3B35199Ad7f52', '0x7918184C5507b657B6e79B5FB2E9766c76C3e95F', '0x74De75657ED8314d532636C93b6A84Fe6A727777', '0xf6eeA67C12A64120d1816939cdeF03512cE46338', '0x4902A760943f7CcdFC26c8FeB91d0329BF9b0CCf', '0xF84eAe85c6a9e5358a5458cDa9150A45ce0EF9F3']
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
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-04-1454-shape.json","w"),indent=1)
print("SALE_SHAPE_HITS:")
for a,r in out.items():
    freeviews=[r.get(f) for f in ("freeClaimed()","freeMinted()","FREE_SLOTS()","FREE_SUPPLY()","freeSharesRemaining()","freeSharesClaimed()")]
    reg = r.get("agentRegistry") or r.get("registry")
    if any(v is not None for v in freeviews) or reg: print(" ",a,r)
