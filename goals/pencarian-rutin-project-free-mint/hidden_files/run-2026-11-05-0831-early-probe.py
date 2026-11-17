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
res={}
C={"Pulsekeep":"0x65c89bD01A03B9B9B73eD29d3B3aF8D2eb034DFc","Tensortug":"0xDdD2b5501B32e0C58C7deB7401765d711553b702","PassAgentX":"0x08b1A979Dd997492EEcc010fe986eA2e2925e620","Bathybots":"0x9610195ac5304B697080ea1252C70613a098E388","RigOrb":"0x72D977237f7b3931A08434cEBD0D3814fE13539e"}
for n,a in C.items():
 res[n]={"totalSupply":call(a,"totalSupply()"),"totalMinted":call(a,"totalMinted()"),"freeMinted":call(a,"freeMinted()"),"freeClaimed":call(a,"freeClaimed()"),"FREE_CAP":call(a,"FREE_CAP()"),"FREE_SUPPLY":call(a,"FREE_SUPPLY()"),"claimedFree(user)":call(a,"claimedFree(address)",enc(USER)),"canFreeMint(user)":call(a,"canFreeMint(address)",enc(USER)),"balanceOf(user)":call(a,"balanceOf(address)",enc(USER)),"mintOpen":call(a,"mintOpen()")}
print(json.dumps(res,indent=1))
json.dump(res,open("run-2026-11-05-0831-early-probe.json","w"),indent=1)
