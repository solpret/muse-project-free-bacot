import json, subprocess
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def batch(addr, views):
    calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":(sel(sig)+enc(USER) if "(address)" in sig else sel(sig))},"latest"]} for i,sig in enumerate(views)]
    for ep in EPS:
        try:
            r=subprocess.run(["curl","-sL","--max-time","25","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(calls)],capture_output=True,text=True,timeout=30)
            res=json.loads(r.stdout)
            if isinstance(res,list) and len(res)==len(calls):
                return {views[i].split("(")[0]+("_user" if "(address)" in views[i] else ""): (None if "error" in res[i] else to_int(res[i].get("result"))) for i in range(len(views))}
        except Exception: continue
    return None
def block():
    for ep in EPS:
        try:
            r=subprocess.run(["curl","-sL","--max-time","25","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})],capture_output=True,text=True,timeout=30)
            return int(json.loads(r.stdout)["result"],16)
        except Exception: continue
    return None
out={"block":block()}
out["CAP7"]=batch("0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd",
 ["freeMinted()","sharesMinted()","paidMinted()","soldOut()","phase()","FREE_SHARES()","freeClaimed(address)","balanceOf(address)","costOf(uint256)"])
print("CAP7",out["CAP7"],flush=True)
out["SHINE"]=batch("0xDDc2352d1ceC10b42e05A297232f5328902C6c2C",
 ["launch()","launchBlock()","freeClaimed()","sharesSold()","remainingShares()","freeClaimed(address)","mintCost(uint256)"])
print("SHINE",out["SHINE"],flush=True)
json.dump(out,open("run-2026-11-11-1401-prio.json","w"),indent=1)
print("PRIO DONE block",out["block"],flush=True)
