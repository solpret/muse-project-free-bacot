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
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0")
for name,addr in [("Ringgent","0xf1d1650dBfeB0FA8082481C8213ACCD59af3cF4A"),("Mindvolt","0x2f47305baEdC1B1F28461cD6b488404A908B1BEA"),("Ghostbot","0x0c654BEF00dAd6925F64B72151C4a504F1C00Bcd"),("Nodeneon","0xE54873f96A7a73FA1E39fe6C8B69aB178c87b3D6")]:
    ts=int(iv(call(addr,sel("totalSupply()"))) or 0); fc=int(iv(call(addr,sel("freeClaimed()"))) or 0); fs=int(iv(call(addr,sel("FREE_SUPPLY()"))) or 0)
    print(name, "totalSupply",ts,"freeClaimed",fc,"FREE_SUPPLY",fs,"pct",round(100*fc/fs,1) if fs else None,"mintOpen",iv(call(addr,sel("mintOpen()"))),"quote",iv(call(addr,sel("quote(address,uint256)")+u+"0000000000000000000000000000000000000000000000000000000000000001")),"mintedBy",iv(call(addr,sel("mintedBy(address)")+u)),"balance",iv(call(addr,sel("balanceOf(address)")+u)),flush=True)
S="0x824d1e5c1395ed7543854fCd9e4da6D3F358De16"
print("S824 freeSold",iv(call(S,sel("freeSold()"))),"freeCap",iv(call(S,sel("freeCap()"))),"isFreeOpen",iv(call(S,sel("isFreeOpen()"))),"totalSold",iv(call(S,sel("totalSold()"))),flush=True)
