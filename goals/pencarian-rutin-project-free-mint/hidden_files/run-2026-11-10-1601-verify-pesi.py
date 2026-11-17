import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SALE="0xe82BAc76C904d49AA6a240f236AFe1D1eD5F4baD"
TOKEN="0x9AEFce1FC6aEb5A5E4051f5fA9fd9D54C4dA6EF5"
EPS=["https://bsc-dataseed.binance.org/","https://bsc.nodereal.io/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a):
    if isinstance(a,int): return hex(a)[2:].rjust(64,"0")
    return a[2:].lower().rjust(64,"0")
def call(addr,sig,arg=None):
    data=sel(sig)+(enc(arg) if arg is not None else "")
    payload={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}
    for ep in EPS:
        try:
            out=subprocess.run(["curl","-sL","--max-time","20","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=25).stdout
            r=json.loads(out)
            if "error" in r: continue
            v=r.get("result")
            if v is None or v=="0x": return None
            return v
        except Exception: continue
    return None
def vint(addr,sig,arg=None):
    v=call(addr,sig,arg)
    return int(v,16) if v else None
def vaddr(addr,sig):
    v=call(addr,sig)
    return "0x"+v[-40:] if v else None
def vstr(addr,sig):
    v=call(addr,sig)
    if not v: return None
    try:
        ln=int(v[66:130],16)
        return bytes.fromhex(v[130:130+ln*2]).decode()
    except Exception: return v
out={}
out["registry"]=vaddr(SALE,"registry()")
out["token"]=vaddr(SALE,"token()")
out["tokensPerShare"]=vint(SALE,"tokensPerShare()")
out["freeCap"]=vint(SALE,"freeCap()")
out["freeClaimed"]=vint(SALE,"freeClaimed()")
out["freeRemaining"]=vint(SALE,"freeRemaining()")
out["freeShares"]=vint(SALE,"freeShares()")
out["priceOf1"]=vint(SALE,"priceOf(uint256)",1)
out["sharePrice"]=vint(SALE,"sharePrice()")
out["paidCap"]=vint(SALE,"paidCap()")
out["paidShares"]=vint(SALE,"paidShares()")
out["paidRemaining"]=vint(SALE,"paidRemaining()")
out["pair"]=vaddr(SALE,"pair()")
out["deadline"]=vint(SALE,"deadline()")
out["lpTrigger"]=vint(SALE,"lpTrigger()")
out["lpCreated"]=vint(SALE,"lpCreated()")
out["paused"]=vint(SALE,"paused()")
out["owner"]=vaddr(SALE,"owner()")
out["feeBps"]=vint(SALE,"feeBps()")
out["token_name"]=vstr(TOKEN,"name()")
out["token_symbol"]=vstr(TOKEN,"symbol()")
out["token_decimals"]=vint(TOKEN,"decimals()")
out["token_totalSupply"]=vint(TOKEN,"totalSupply()")
out["token_maxSupply"]=vint(TOKEN,"maxSupply()")
out["token_balance_user"]=vint(TOKEN,"balanceOf(address)",USER)
for ep in EPS:
    try:
        o=subprocess.run(["curl","-sL","--max-time","20","-X","POST",ep,"-H","Content-Type: application/json","-d",'{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],capture_output=True,text=True,timeout=25).stdout
        out["block"]=int(json.loads(o)["result"],16); out["block_ep"]=ep; break
    except Exception: continue
print(json.dumps(out,indent=1))
json.dump(out,open("run-2026-11-10-1601-verify-pesi.json","w"),indent=1)
