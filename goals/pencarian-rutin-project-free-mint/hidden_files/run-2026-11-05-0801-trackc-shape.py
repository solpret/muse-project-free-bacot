import json, urllib.request
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc.publicnode.com"]
def sel(s):
 k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,data):
 p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
 for ep in EPS:
  try:
   req=urllib.request.Request(ep,data=p,headers={"Content-Type":"application/json"},method="POST")
   with urllib.request.urlopen(req,timeout=10) as r: j=json.load(r)
   v=j.get("result"); return v if v and v!="0x" else None
  except Exception: continue
 return None
def iv(v):
 try: return int(v,16) if v else None
 except Exception: return None
def dec(v):
 try:
  b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[32:64],'big'); return b[64:64+ln].decode(errors='replace')
 except Exception: return None
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0"); one="0"*63+"1"
a="0x8E6f8B636Df9A5F15fAAACD803a4AAE43cF97B0e"
o={'name':dec(call(a,sel("name()"))),'symbol':dec(call(a,sel("symbol()"))),'decimals':iv(call(a,sel("decimals()"))),'totalSupply':iv(call(a,sel("totalSupply()"))),'freeMinted':iv(call(a,sel("freeMinted()"))),'freeClaimed_total':iv(call(a,sel("freeClaimed()"))),'FREE_SUPPLY':iv(call(a,sel("FREE_SUPPLY()"))),'FREE_SLOTS':iv(call(a,sel("FREE_SLOTS()"))),'freeClaimed_user':iv(call(a,sel("freeClaimed(address)")+u)),'quote_user1':iv(call(a,sel("quote(address,uint256)")+u+one)),'agentRegistry':call(a,sel("agentRegistry()")),'registry':call(a,sel("registry()")),'freeSharesRemaining':iv(call(a,sel("freeSharesRemaining()"))),'freeAvailable':iv(call(a,sel("freeAvailable()")))}
print(json.dumps(o,indent=1))
json.dump({a:o},open("run-2026-11-05-0801-trackc-shape.json","w"),indent=1)
