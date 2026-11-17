import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR="0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
VIEWS=["totalSupply()","totalMinted()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","freeRemaining()","mintOpen()","isFreeOpen()","saleStart()","saleEnd()","balanceOf(address)","freeAvailable(address)","freeMintedBy(address)"]
def post_one(ep,payload,timeout=15):
    r=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5)
    return json.loads(r.stdout)
def race(payload,timeout=15):
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs={ex.submit(post_one,ep,payload,timeout):ep for ep in EPS}
        for f in as_completed(futs):
            try:
                res=f.result()
                if isinstance(res,list) and len(res)==len(payload): return res
            except Exception: continue
    return None
calls=[];keys=[]
for i,sig in enumerate(VIEWS):
    base=sig.split("(")[0]
    if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
    else: data=sel(sig); key=base
    calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]}); keys.append(key)
blk=race([{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}],timeout=10)
out={"block": int(blk[0]["result"],16) if blk else None}
res=race(calls,timeout=20)
if res is None: out["views"]=None
else:
    out["views"]={k:(None if (isinstance(it,dict) and "error" in it) else (int(it["result"],16) if isinstance(it,dict) and it.get("result") not in (None,"0x") else None)) for it,k in zip(res,keys)}
    out["summary"]={k:v for k,v in out["views"].items() if v is not None}
print(json.dumps(out,indent=1))
json.dump(out,open("hot-leg-2026-11-12-1834-runic-retry.json","w"),indent=1)
