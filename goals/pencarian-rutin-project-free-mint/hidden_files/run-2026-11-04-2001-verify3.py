import json, urllib.request, base64
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
def dec_str(v):
    try:
        b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[32:64],'big'); raw=b[64:64+ln]
        if raw.startswith(b'data:application/json;base64,'):
            return base64.b64decode(raw.split(b',',1)[1]).decode()
        return raw.decode(errors='replace')
    except Exception as e: return f"ERR {e}"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0")
tests=[("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("freeMinted()",""),("mintOpen()",""),("quote(address,uint256)",u+"0000000000000000000000000000000000000000000000000000000000000001"),("mintedBy(address)",u),("freeUsed(address)",u),("balanceOf(address)",u)]
for name,addr in [("Ghostbot","0x0c654BEF00dAd6925F64B72151C4a504F1C00Bcd"),("Nodeneon","0xE54873f96A7a73FA1E39fe6C8B69aB178c87b3D6"),("Mindvolt","0x2f47305baEdC1B1F28461cD6b488404A908B1BEA"),("CzBinance","0xb04f19CD6440040be8E9B52c5aB6e14d37566C08")]:
    out={}
    for fn,arg in tests: out[fn]=iv(call(addr,sel(fn)+arg))
    o=call(addr,sel("owner()")); out["owner"]=hex(iv(o)) if o else None
    out["contractURI"]=dec_str(call(addr,sel("contractURI()"))) if call(addr,sel("contractURI()")) else None
    print(name,addr,out,flush=True)
