import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RONIN="0xF62FA2ee1490708D51DeF7212493D5c7878Fa110"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def _post_one(ep,payload,timeout=12):
    r=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5)
    return json.loads(r.stdout)
def post_race(payload,timeout=12):
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs={ex.submit(_post_one,ep,payload,timeout):ep for ep in EPS}
        for fut in as_completed(futs):
            try:
                res=fut.result()
                if isinstance(res,list) and len(res)==len(payload): return res
            except Exception: continue
    return None
sigs=["FREE_CAP()","FREE_SUPPLY()","freeMinted()","totalMinted()","mintOpensAt()","mintOpen()","contractURI()","MAX_PER_WALLET()","freeClaimed(address)","tokenURI(uint256)"]
calls=[];keys=[]
for i,sig in enumerate(sigs):
    if sig=="tokenURI(uint256)":
        data=sel(sig)+"0"*63+"1"; key="tokenURI_1"
    elif "(address)" in sig:
        data=sel(sig)+enc(USER); key=sig.split("(")[0]+"_user"
    else:
        data=sel(sig); key=sig.split("(")[0]
    calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":RONIN,"data":data},"latest"]}); keys.append(key)
res=post_race(calls,timeout=12)
out={}
if res:
    for it,key in zip(res,keys):
        if isinstance(it,dict) and "error" in it: out[key]={"error":str(it["error"])[:80]}
        else:
            raw=it.get("result") if isinstance(it,dict) else None
            out[key]={"raw":str(raw)[:200],"int":to_int(raw) if raw else None}
print(json.dumps(out,indent=1))
# block number
blk=post_race([{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}],timeout=10)
print("block:", blk[0]["result"] if blk else None)
json.dump(out,open(BASE+"hot-leg-2026-11-12-1544-ronin-supplement.json","w"),indent=1)
