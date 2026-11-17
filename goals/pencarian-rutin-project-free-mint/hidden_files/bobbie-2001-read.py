import json, urllib.request
from Crypto.Hash import keccak
RPC="https://bsc-dataseed.binance.org"
ADDR="0x3BF121dC4c5a1Ba567F3eE801d0e447601726207"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def call(data):
    body=json.dumps({"jsonrpc":"2.0","method":"eth_call","params":[{"to":ADDR,"data":data},"latest"],"id":1}).encode()
    req=urllib.request.Request(RPC,data=body,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=30) as r:
        return json.load(r)
def uint(fn):
    try:
        res=call(sel(fn))
        if "result" in res and res["result"] and res["result"]!="0x":
            return int(res["result"],16)
        return ("ERR",res.get("error"))
    except Exception as e:
        return ("EXC",str(e))
for fn in ["totalSupply()","totalMinted()","freeAllocated()","FREE_SUPPLY()","mintStartsAt()","mintEndsAt()","mintOpen()"]:
    print(fn, uint(fn))
# block number for timestamp context
body=json.dumps({"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":2}).encode()
req=urllib.request.Request(RPC,data=body,headers={"Content-Type":"application/json"})
with urllib.request.urlopen(req,timeout=30) as r:
    print("block",int(json.load(r)["result"],16))
