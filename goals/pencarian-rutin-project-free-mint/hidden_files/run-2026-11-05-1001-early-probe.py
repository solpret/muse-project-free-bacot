import json, urllib.request
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed.bnbchain.org","https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
 k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(to,sig,args=""):
 data=sel(sig)+args; last=None
 for rpc in RPCS:
  body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
  try:
   req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
   with urllib.request.urlopen(req,timeout=20) as r: out=json.load(r)
   break
  except Exception as e: last=e; continue
 else: return {"error":str(last)}
 if "error" in out: return {"error":out["error"]}
 v=out["result"]
 if not v or v=="0x": return None
 try: return int(v,16)
 except Exception: return v
def blk():
 for rpc in RPCS:
  body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
  try:
   req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
   with urllib.request.urlopen(req,timeout=20) as r: return int(json.load(r)["result"],16)
  except Exception: continue
C={
 "SAOBNFT":"0xeA45d5dCC55700183b87016Dd38d17f6f1a6ed8b",
 "V12":"0x11df7fD6bf179d7173184c82E2917b62905E773c",
 "DuskWyrm":"0xF592a1917cb4fDf5D9ad666b6426Da2F8585D0d4",
 "DYOR":"0x86956Bc830EB62110820Ae79164BeF61c7E31936",
 "PixelLaptop":"0x273fc2c7705b23eb129e35ac8da26348e6fc4980",
}
res={"block":blk()}
for n,a in C.items():
 res[n]={"totalSupply":call(a,"totalSupply()"),"totalMinted":call(a,"totalMinted()"),
 "freeMinted":call(a,"freeMinted()"),"freeClaimed":call(a,"freeClaimed()"),
 "FREE_SUPPLY":call(a,"FREE_SUPPLY()"),"MAX_SUPPLY":call(a,"MAX_SUPPLY()"),
 "agentRegistry":call(a,"agentRegistry()"),"mintOpen":call(a,"mintOpen()"),
 "balanceOf(user)":call(a,"balanceOf(address)",enc(USER)),
 "freeClaimed(user)":call(a,"freeClaimed(address)",enc(USER)),
 "mintedBy(user)":call(a,"mintedBy(address)",enc(USER)),
 "owner":call(a,"owner()")}
print(json.dumps(res,indent=1))
json.dump(res,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-1001-early-probe.json","w"),indent=1)
