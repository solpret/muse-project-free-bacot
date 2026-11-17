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
            with urllib.request.urlopen(req,timeout=6) as r: j=json.load(r)
            if "error" in j: return None
            v=j.get("result"); return v if v and v!="0x" else None
        except Exception: continue
    return None
def iv(v):
    try: return int(v,16) if v else None
    except Exception: return None
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0"); one="0"*63+"1"
tests=[("name()",""),("symbol()",""),("decimals()",""),("totalSupply()",""),("FREE_SUPPLY()",""),("FREE_SLOTS()",""),("FREE_AMOUNT()",""),("freeMinted()",""),("freeClaimed(address)",u),("freeClaimed()",""),("freeLeft(address)",u),("freeSharesRemaining()",""),("freeSharesClaimed()",""),("freeUsed(address)",u),("freeAvailable(address)",u),("freeSharePoolExhausted()",""),("freeFor(address)",u),("quote(address,uint256)",u+one),("registry()",""),("agentRegistry()",""),("mintFree()","")]
addrs=["0xF8B51600358000E24898ECDed278b29D60f7FE2e","0x77432c7b16D9CdBaDBf067EE46eC2a89CFA36e70","0x0737A4FE71A12F20eaA93CDAbc2940dE7f4c79e6","0x7379D4FF4f8F984A026E8dea5B7BaA07F4Eb6E7f","0xe024075315F65c824072B2fF71431c84Eb5a77e7","0x01C627368bf5DD2a97bD862230dE8Da45C6c22E1","0x38374172106745D0794BD064BC9a9334Ae1F7305","0x782d5B27b9C3eB98F9fDBF71C57A7D801e4F7Ccd","0xa16d097A3aeDEb84ef1676f82449D41f64b0C033","0x42400E4170D1aF2c3839986f97eCDaE1E7e77499","0x1cbDE5E272a622f622D43575A71635Cc00d8001f","0x759C09378dBFf2d6AAC0261Ad1f92f9d230669f5","0x9e8aeF3af62534393970a4a8dEF3D480a32ED92d","0x80591929257eC242489dd757393DDBeE51A2B882","0xf1940eAf5d1CA7e99352B7f30d60a1d7ba514eaA","0xf2F0Ef26724F22fd1b64b9D6379172000215d6ea","0x2961C8d23AA415F3F4D72E67e5faf31507Ef5690","0x675e14eb6Da66080846Ca385191f090B7565c8b6","0x1Ad7c607500dE19642a0E9E9bfD8C4D13FD27777","0x195fC0EF58e66Ca107be08d4EdBb4607514A0879"]
def shape(a):
    out={}
    for name,arg in tests:
        v=call(a,sel(name)+arg)
        if v is not None:
            if name in ("name()","symbol()"):
                try:
                    hx=v[130:]; out[name]=bytes.fromhex(hx).rstrip(b'\x00').decode('utf-8','ignore')[:40]
                except Exception: out[name]=v[:66]
            elif name in ("registry()","agentRegistry()"): out[name]="0x"+v[-40:]
            else: out[name]=iv(v)
    return out
out={}
with ThreadPoolExecutor(max_workers=15) as ex:
    for a,o in zip(addrs, ex.map(shape,addrs)):
        out[a]=o; print("SHAPE",a,o,flush=True)
json.dump(out,open("hot-leg-2026-11-04-2249-shape.json","w"),indent=1)
print("DONE")
