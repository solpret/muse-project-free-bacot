import json, urllib.request
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed3.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,data):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=p,headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=8) as r: v=json.load(r)["result"]
            return v if v and v!="0x" else None
        except Exception: continue
    return None
def iv(v):
    try: return int(v,16) if v else None
    except Exception: return None
def sstr(v):
    try:
        if not v: return None
        b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[64:96],'big'); return b[96:96+ln].decode(errors='replace')
    except Exception: return None
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0")
for name,addr,tests in [
 ("F1","0xf1d1650dBfeB0FA8082481C8213ACCD59af3cF4A",[("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("mintOpen()",""),("quote(address,uint256)",u+"0000000000000000000000000000000000000000000000000000000000000001"),("mintedBy(address)",u),("freeUsed(address)",u),("balanceOf(address)",u),("owner()","")]),
 ("F2","0x2f47305baEdC1B1F28461cD6b488404A908B1BEA",[("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("mintOpen()",""),("quote(address,uint256)",u+"0000000000000000000000000000000000000000000000000000000000000001"),("mintedBy(address)",u),("freeUsed(address)",u),("balanceOf(address)",u),("owner()","")]),
 ("S824","0x824d1e5c1395ed7543854fCd9e4da6D3F358De16",[("isFreeOpen()",""),("freeSold()",""),("freeCap()",""),("FREE_TOKENS()",""),("startAt()",""),("token()",""),("agentRegistry()","")]),
 ("BCAE","0xbcaeE51683aEc7857d31098C97b582736E00c8f5",[("totalSupply()",""),("totalSpotsMinted()",""),("spotsLeft()",""),("mintedBy(address)",u),("quote(address,uint256)",u+"0000000000000000000000000000000000000000000000000000000000000001")]),
]:
    out={}
    for fn,arg in tests:
        out[fn]=iv(call(addr,sel(fn)+arg))
    out["name"]=sstr(call(addr,sel("name()"))); out["symbol"]=sstr(call(addr,sel("symbol()")))
    cu=call(addr,sel("contractURI()")); out["contractURI_raw"]=cu[:200] if cu else None
    print(name,addr,out,flush=True)
