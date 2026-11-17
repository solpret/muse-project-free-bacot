import json, urllib.request
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
def addr(v):
    try: return "0x"+v[-40:] if v else None
    except Exception: return None
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0"); one=(1).to_bytes(32,'big').hex()
tests=[("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("mintOpen()",""),("quote(address,uint256)",u+one),("freeLeft(address)",u),("freeUsed(address)",u),("mintedBy(address)",u),("balanceOf(address)",u)]
out={}
for name,a in [("6810","0x6810056D235c949f425b394dE590835096dd6AdC"),("2e93","0x2e93D00967fb9ac4961F3B23206F259100Cca638"),("NeuralAtlas","0xce6392af7fd84e5aa8a77ed6636c45bf756dab94")]:
    d={n: iv(call(a,sel(n)+arg)) for n,arg in tests}
    d["AGENT_ID()"]=addr(call(a,sel("AGENT_ID()")))
    d["PRICE()"]=iv(call(a,sel("PRICE()")))
    out[name]=d; print(name,d,flush=True)
# 150A Carded
a="0x150A46112fD3dfb7873d348eF15C8EC438854304"
d={}
for n,arg in [("freeUnlocked()",""),("freeClaims()",""),("freeClaimCap()",""),("sharesSold()",""),("shareCap()",""),("mintStart()",""),("quote(uint256)",one),("sharePrice()",""),("opened()","")]:
    d[n]=iv(call(a,sel(n)+arg))
d["registry()"]=addr(call(a,sel("registry()")))
d["freeTokensPerClaim()"]=iv(call(a,sel("freeTokensPerClaim()")))
out["150A"]=d; print("150A",d,flush=True)
json.dump(out,open("hot-leg-2026-11-04-1929-verify.json","w"),indent=1)
