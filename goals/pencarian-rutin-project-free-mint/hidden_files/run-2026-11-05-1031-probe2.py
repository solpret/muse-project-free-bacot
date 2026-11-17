import json, urllib.request
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed.bnbchain.org","https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
OUT="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-1031-probe2.json"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def encu(n): return format(n,"064x")
def raw(to,data):
    for rpc in RPCS:
        body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
        try:
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=20) as r: out=json.load(r)
            if "error" in out: return {"error":out["error"]}
            v=out["result"]
            if not v or v=="0x": return None
            try: return int(v,16)
            except Exception: return v
        except Exception as e: last=e; continue
    return {"error":str(last)}
def call(to,sig,args=""): return raw(to,sel(sig)+args)
def block():
    for rpc in RPCS:
        body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
        try:
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=20) as r: return int(json.load(r)["result"],16)
        except Exception: continue
res={"block":block()}
for name,addr in [("Saturnode","0x6124b3ae64adA7b73581CcD01fEF89e583E8742c"),("Pumpkinfarm","0x77E38295603a06654a6ED3Ed0849e6AA50749963"),("PixelLaptop","0x273fc2c7705b23eb129e35ac8da26348e6fc4980")]:
    res[name]={"totalSupply":call(addr,"totalSupply()"),"freeClaimed":call(addr,"freeClaimed()"),"FREE_SUPPLY":call(addr,"FREE_SUPPLY()"),"MAX_SUPPLY":call(addr,"MAX_SUPPLY()"),"mintOpen":call(addr,"mintOpen()"),"mintedBy_user":call(addr,"mintedBy(address)",enc(USER)),"balanceOf_user":call(addr,"balanceOf(address)",enc(USER)),"quote_user_1":call(addr,"quote(address,uint256)",enc(USER)+encu(1))}
print(json.dumps(res,indent=1))
with open(OUT,"w") as f: json.dump(res,f,indent=1)
