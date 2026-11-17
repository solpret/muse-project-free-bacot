import json, urllib.request
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed.bnbchain.org","https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
 k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
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
C={"PCAT":"0x9b9e0a4358449eebf4437877a9b36e26c24ce703","KOAI":"0x6dFE0D2E3Ab6f2bD5F3875557eb0e5c5Fe4B05c7","ACOS":"0x3aeda314ec05bc22e3c26a543e16df2b8cc8fe69","MoonCat":"0x045425004b622733ced4139e930c622187ea6c73","Saturnode":"0x6124b3ae64ada7b73581ccd01fef89e583e8742c","Sidecoo":"0x409Cfe3747f1ac20f267B50BCbB6a4E9406DA3a8"}
res={}
for n,a in C.items():
 res[n]={"totalSupply":call(a,"totalSupply()"),"totalMinted":call(a,"totalMinted()"),
 "freeClaimed":call(a,"freeClaimed()"),"freeMinted":call(a,"freeMinted()"),
 "FREE_SUPPLY":call(a,"FREE_SUPPLY()"),"MAX_SUPPLY":call(a,"MAX_SUPPLY()"),
 "mintOpen":call(a,"mintOpen()"),"agentRegistry":call(a,"agentRegistry()"),
 "balanceOf(user)":call(a,"balanceOf(address)",enc(USER)),
 "mintedBy(user)":call(a,"mintedBy(address)",enc(USER)),
 "freeClaimed(user)":call(a,"freeClaimed(address)",enc(USER)),
 "quote(user,1)":call(a,"quote(address,uint256)",enc(USER)+enc_u(1))}
 print(n, json.dumps(res[n]), flush=True)
json.dump(res,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-1101-boltbook-probe.json","w"),indent=1)
