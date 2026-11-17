import json, urllib.request
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR="0xce18531F9F639ca2351CA15FB2032D925b917472"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
VIEWS=["totalSupply()","totalMinted()","freeMinted()","paidMinted()","FREE_CAP()","MAX_SUPPLY()","mintOpen()","mintOpenTime()","isFree()","AGENT_ID()","owner()","freeClaimed(address)","isAgent(address)","balanceOf(address)"]
def batch(addr, views):
    calls=[]; keys=[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig:
            data=sel(sig)+enc(USER); key=base+"_user"
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
        except Exception: continue
    return None
r=batch(ADDR, VIEWS)
print(json.dumps(r, indent=1))
for k in ["AGENT_ID","owner"]:
    v=r.get(k) if r else None
    print(k, hex(v) if isinstance(v,int) else v)
# head block
for ep in EPS:
    try:
        req=urllib.request.Request(ep, data=json.dumps([{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}]).encode(), headers={"Content-Type":"application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp: out=json.load(resp)
        print("head", int(out[0]["result"],16)); break
    except Exception: continue
json.dump({"addr":ADDR,"views":r}, open("run-2026-11-08-1631-oddlode-verify.json","w"), indent=1)
