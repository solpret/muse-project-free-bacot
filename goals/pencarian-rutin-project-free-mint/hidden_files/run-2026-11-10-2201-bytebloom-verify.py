import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
BB="0x74bbDAD7c027C56bE30A7fEaC6F7371B95f1c32B"
TX="0x4ad8c90a91a0704fc08c2fd20cf13ca3a38f850e41a9651a617cd024097c5007"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(addr,sig,args=""):
    data=sel(sig)+args
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]},timeout=25)
            res=r.get("result")
            if res not in (None,"0x"): return res
        except Exception: continue
    return None
def words(h):
    if h is None: return None
    b=bytes.fromhex(h[2:])
    return [int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
res={}
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getTransactionReceipt","params":[TX]},timeout=25)
        if r.get("result"): res["receipt"]=r["result"]; break
    except Exception: continue
rc=res.get("receipt") or {}
print("receipt status:", rc.get("status"), "block:", int(rc.get("blockNumber","0x0"),16) if rc.get("blockNumber") else None, "gasUsed:", int(rc.get("gasUsed","0x0"),16) if rc.get("gasUsed") else None)
print("ownerOf(508):", (lambda w: "0x"+w[-1].to_bytes(32,'big')[-20:].hex() if w else None)(words(call(BB,"ownerOf(uint256)",format(508,"064x")))))
print("balanceOf(user):", (lambda w: w[0] if w else None)(words(call(BB,"balanceOf(address)",enc(USER)))))
print("agentFreeByWallet(user):", (lambda w: w[0] if w else None)(words(call(BB,"agentFreeByWallet(address)",enc(USER)))))
print("agentFreeUsed:", (lambda w: w[0] if w else None)(words(call(BB,"agentFreeUsed()"))))
print("totalSupply:", (lambda w: w[0] if w else None)(words(call(BB,"totalSupply()"))))
print("tokenURI(508) raw:", call(BB,"tokenURI(uint256)",format(508,"064x"))[:200] if call(BB,"tokenURI(uint256)",format(508,"064x")) else None)
json.dump(res, open("run-2026-11-10-2201-bytebloom-receipt.json","w"), indent=1)
print("VERIFY DONE")
