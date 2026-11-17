import json, urllib.request
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed.bnbchain.org","https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
 k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def raw(to,data):
 last=None
 for rpc in RPCS:
  body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
  try:
   req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
   with urllib.request.urlopen(req,timeout=20) as r: out=json.load(r)
   break
  except Exception as e: last=e; continue
 else: return {"error":str(last)}
 if "error" in out: return {"error":out["error"]}
 return out["result"]
def dec_str(v):
 try:
  if not v or v=="0x": return None
  b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[32:64],'big'); return b[64:64+ln].decode(errors='replace')
 except Exception as e: return f"decode-err:{e}"
def call(to,sig,args=""):
 v=raw(to,sel(sig)+args)
 if isinstance(v,dict): return v
 if v is None or v=="0x": return None
 try: return int(v,16)
 except Exception: return v
C={"SPOTS-A":"0x49150574b740c5a75FaC272446f9cBB7c27b02C2","SPOTS-B":"0x86CA531ffB29A0B7bc17A5f3973F7B431a9263A4","SPOTS-C":"0x12167D06c9CecC0b5EAFD166892CFbf8240fd971",
   "Pumpkinfarm":"0x77E38295603a06654a6ED3Ed0849e6AA50749963","Astrogent":"0x483cef46ec23d5656896526408221074597b6ed6"}
res={}
for n,a in C.items():
 d={}
 d["name"]=dec_str(raw(a,sel("name()"))) if n.startswith("SPOTS") else None
 d["symbol"]=dec_str(raw(a,sel("symbol()"))) if n.startswith("SPOTS") else None
 d["totalSupply"]=call(a,"totalSupply()")
 d["totalSpotsMinted"]=call(a,"totalSpotsMinted()")
 d["spotsLeft"]=call(a,"spotsLeft()")
 d["MAX_SPOTS"]=call(a,"MAX_SPOTS()")
 d["PRICE"]=call(a,"PRICE()")
 d["PER_SPOT"]=call(a,"PER_SPOT()")
 d["mintedBy(user)"]=call(a,"mintedBy(address)",enc(USER))
 d["balanceOf(user)"]=call(a,"balanceOf(address)",enc(USER))
 d["quote(user,1)"]=call(a,"quote(address,uint256)",enc(USER)+enc_u(1))
 d["WEBSITE"]=dec_str(raw(a,sel("WEBSITE()")))
 d["TWITTER"]=dec_str(raw(a,sel("TWITTER()")))
 d["AGENT_REGISTRY"]=call(a,"AGENT_REGISTRY()")
 # pumpkin/astro specifics
 if n in ("Pumpkinfarm","Astrogent"):
  d["freeClaimed"]=call(a,"freeClaimed()"); d["FREE_SUPPLY"]=call(a,"FREE_SUPPLY()"); d["MAX_SUPPLY"]=call(a,"MAX_SUPPLY()"); d["mintOpen"]=call(a,"mintOpen()")
 res[n]=d
 print(n, json.dumps(d), flush=True)
json.dump(res,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-1001-spots-probe.json","w"),indent=1)
