import json, urllib.request, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR="0x34aE861Fbeb2aaA6071248F8a27AcE5f30aA7bBf"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try:
        return int(v,16) if v and v!="0x" else None
    except Exception: return None
VIEWS=["agentId()","token()","usdt()","freeAvailable()","freeMinted()","MAX_FREE()","MAX_SHARES()","sharesMinted()","paidShares()","soldOut()","closed()","deployedAt()","windDownAt()","PRICE()","TOKENS_PER_SHARE()","quote(address,uint256)","quote(uint256)","freeClaimed(address)","hasAgentId(address)","claimedShares(address)","mintedBy(address)","hasMinted(address)"]
def call(addr, views):
    calls=[]; keys=[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address" in sig:
            data=sel(sig)+enc(USER); key=base+"_user"
        elif "(uint256)" in sig:
            data=sel(sig)+"0"*63+"1"; key=base+"_1"
        elif "(address,uint256)" in sig:
            data=sel(sig)+enc(USER)+"0"*63+"1"; key=base+"_user1"
        else:
            data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            req=urllib.request.Request(ep, data=json.dumps(calls).encode(), headers={"Content-Type":"application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=15) as r: out=json.load(r)
            if not isinstance(out,list) or len(out)!=len(calls): continue
            res={}
            for item,key in zip(out,keys):
                res[key]=to_int(item.get("result")) if isinstance(item,dict) and "result" in item else None
            return res
        except Exception as e:
            continue
    return None
r=call(ADDR, VIEWS)
print(json.dumps(r, indent=1))
# address-typed views return ints; print as hex for agentId/token/usdt
for k in ["agentId","token","usdt"]:
    v=r.get(k) if r else None
    print(k, hex(v) if isinstance(v,int) else v)
# head block
for ep in EPS:
    try:
        req=urllib.request.Request(ep, data=json.dumps([{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}]).encode(), headers={"Content-Type":"application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp: out=json.load(resp)
        print("head", int(out[0]["result"],16), "via", ep); break
    except Exception: continue
json.dump({"addr":ADDR,"views":r,"wib":"2026-11-08 ~17:0x"}, open("run-2026-11-08-1631-34ae-verify.json","w"), indent=1)
