import json, urllib.request
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed.binance.org","https://bsc-dataseed2.bnbchain.org","https://bsc-dataseed3.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
MINT="0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN="0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=8) as r: out=json.load(r)
            if "error" in out: continue
            v=out["result"]
            if not v or v=="0x": return None
            return int(v,16)
        except Exception: continue
    return None
for sig in ["launched()","failed()","isRefundPhase()","totalShares()"]:
    print(sig, raw(MINT, sel(sig)))
print("tokenClaimed(user)", raw(MINT, sel("tokenClaimed(address)")+enc(USER)))
print("tokenBalance(user)", raw(TOKEN, sel("balanceOf(address)")+enc(USER)))
