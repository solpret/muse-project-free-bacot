import json, urllib.request, time
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,sig,dl):
    data=sel(sig)
    for rpc in RPCS:
        if time.time()>dl: return "deadline"
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=5) as r: out=json.load(r)
            if "error" in out: continue
            v=out["result"]
            if not v or v=="0x": return None
            return int(v,16)
        except Exception: continue
    return None
ADDR="0x8269Ea1629644219a88dbB053D34E8e877596B00"
dl=time.time()+40
res={}
for sig in ["sharesMinted()","freeMinted()","paidShares()","soldOut()","freeSharesRemaining()","totalSupply()","freeSharesClaimed(address)"]:
    if sig.startswith("freeSharesClaimed"):
        # needs arg; skip via generic call with user addr
        data=sel(sig)+"eb237f6f9fb4e826739f0954e9768914f28b2c2e".rjust(64,"0")
        v=None
        for rpc in RPCS:
            try:
                body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]}).encode()
                req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
                with urllib.request.urlopen(req,timeout=5) as r: out=json.load(r)
                if "error" in out: continue
                vv=out["result"]
                v=None if not vv or vv=="0x" else int(vv,16)
                break
            except Exception: continue
        res[sig]=v
    else:
        res[sig]=call(ADDR,sig,dl)
print(json.dumps(res,indent=1))
json.dump({"block_note":"block ~131947085","pacture":res},open("run-2026-11-06-1144-pacture.json","w"),indent=1)
