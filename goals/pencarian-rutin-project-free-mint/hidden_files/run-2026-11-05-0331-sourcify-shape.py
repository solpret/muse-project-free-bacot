import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,data):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=p,headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=8) as r: j=json.load(r)
            v=j.get("result"); return v if v and v!="0x" else None
        except Exception: continue
    return None
def iv(v):
    try: return int(v,16) if v else None
    except Exception: return None
def dec_str(v):
    try:
        b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[32:64],'big'); return b[64:64+ln].decode(errors='replace')
    except Exception: return None
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0"); one="0"*63+"1"
feed=['0x1c5C3fe70FA34dDfC91F4278A7FE3869AaC9E9Ee', '0xe76B6df12d5DB10d34Bb52901d39f8DaDa571f57', '0xb6551d6879b57048d3d13a6CAc03489EeA52E4b2']
def shape(a):
    o={}
    o['name']=dec_str(call(a,sel("name()"))); o['symbol']=dec_str(call(a,sel("symbol()")))
    o['decimals']=iv(call(a,sel("decimals()"))); o['totalSupply']=iv(call(a,sel("totalSupply()"))); o['totalMinted']=iv(call(a,sel("totalMinted()")))
    o['freeClaimed_total']=iv(call(a,sel("freeClaimed()"))); o['freeMinted']=iv(call(a,sel("freeMinted()")))
    o['FREE_SUPPLY']=iv(call(a,sel("FREE_SUPPLY()"))); o['FREE_SLOTS']=iv(call(a,sel("FREE_SLOTS()")))
    o['freeClaimed_user']=iv(call(a,sel("freeClaimed(address)")+u)); o['freeMinted_user']=iv(call(a,sel("freeMinted(address)")+u))
    o['quote_user1']=iv(call(a,sel("quote(address,uint256)")+u+one)); o['mintOpen']=iv(call(a,sel("mintOpen()")))
    o['agentRegistry']=call(a,sel("agentRegistry()")); o['registry']=call(a,sel("registry()"))
    return o
out={}
with ThreadPoolExecutor(max_workers=20) as ex:
    for a,o in zip(feed, ex.map(shape, feed)): out[a]=o; print("SHAPE",a,o,flush=True)
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-0331-sourcify-shape.json","w"),indent=1)
print("DONE")
