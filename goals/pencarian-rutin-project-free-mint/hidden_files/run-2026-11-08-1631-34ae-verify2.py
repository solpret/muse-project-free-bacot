import json, urllib.request
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SALE="0x34aE861Fbeb2aaA6071248F8a27AcE5f30aA7bBf"
TOKEN="0x37266a6d1310bb1579c3721061b5366168602560"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def batch(addr, specs):
    calls=[]; keys=[]
    for i,(sig,arg) in enumerate(specs):
        if arg=="user": data=sel(sig)+enc(USER)
        elif arg=="one": data=sel(sig)+"0"*63+"1"
        else: data=sel(sig)
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(sig.split("(")[0]+("_user" if arg=="user" else ""))
    for ep in EPS:
        try:
            req=urllib.request.Request(ep, data=json.dumps(calls).encode(), headers={"Content-Type":"application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=15) as r: out=json.load(r)
            if not isinstance(out,list): continue
            res={}
            for item,key in zip(out,keys):
                res[key]=to_int(item.get("result")) if isinstance(item,dict) and "result" in item else None
            return res
        except Exception: continue
    return None
r1=batch(SALE,[("freeAvailable(address)","user"),("claimable(address)","user"),("freeClaimed(address)","user"),("freeMinted()",""),("sharesMinted()",""),("MAX_FREE()",""),("MAX_SHARES()","")])
print("SALE:", json.dumps(r1, indent=1))
r2=batch(TOKEN,[("name()",""),("symbol()",""),("decimals()",""),("totalSupply()",""),("balanceOf(address)","user")])
print("TOKEN raw:", json.dumps(r2, indent=1))
# decode string returns
def dec_str(hexv):
    if hexv is None: return None
    b=bytes.fromhex(hexv[2:])
    try:
        ln=int.from_bytes(b[64:96],'big')
        return b[96:96+ln].decode()
    except Exception: return hexv
# re-read name/symbol as raw
def raw(addr, sig):
    for ep in EPS:
        try:
            body=[{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":sel(sig)},"latest"]}]
            req=urllib.request.Request(ep, data=json.dumps(body).encode(), headers={"Content-Type":"application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=15) as r: out=json.load(r)
            return out[0].get("result")
        except Exception: continue
    return None
print("token name:", dec_str(raw(TOKEN,"name()")))
print("token symbol:", dec_str(raw(TOKEN,"symbol()")))
json.dump({"sale":r1,"token_views":r2,"token_name":dec_str(raw(TOKEN,"name()")),"token_symbol":dec_str(raw(TOKEN,"symbol()"))}, open("run-2026-11-08-1631-34ae-verify2.json","w"), indent=1)
