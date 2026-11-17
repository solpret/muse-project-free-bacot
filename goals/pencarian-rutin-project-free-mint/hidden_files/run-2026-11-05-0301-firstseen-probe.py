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
            with urllib.request.urlopen(req,timeout=10) as r: j=json.load(r)
            v=j.get("result"); return v if v and v!="0x" else None
        except Exception: continue
    return None
def iv(v):
    try: return int(v,16) if v else None
    except Exception: return None
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0"); one="0"*63+"1"
def probe(a):
    o={}
    o['agentIds']=call(a,sel("agentIds()"))
    o['price']=iv(call(a,sel("price()")))
    o['costOf_user1']=iv(call(a,sel("costOf(address,uint256)")+u+one))
    o['totalSupply']=iv(call(a,sel("totalSupply()")))
    o['MAX_SUPPLY']=iv(call(a,sel("MAX_SUPPLY()")))
    o['mintOpen']=iv(call(a,sel("mintOpen()")))
    o['mintedBy_user']=iv(call(a,sel("mintedBy(address)")+u))
    o['mintsLeft_user']=iv(call(a,sel("mintsLeft(address)")+u))
    o['FREE_SUPPLY']=iv(call(a,sel("FREE_SUPPLY()")))
    o['TOKENS_PER_FREE_MINT']=iv(call(a,sel("TOKENS_PER_FREE_MINT()")))
    o['mintedPerWallet_user']=iv(call(a,sel("mintedPerWallet(address)")+u))
    o['freeMintedPerWallet_user']=iv(call(a,sel("freeMintedPerWallet(address)")+u))
    return o
targets=['0x82Cf5049146D8656d1d4877546110C29B4a1c71a','0x5AD666A89De917b4EabFB20De881A6776169d39c','0x273fc2C7705B23eb129E35aC8Da26348E6Fc4980','0x9578F8a40228f44f31A9E4bc179E1112f7fA4157']
out={}
with ThreadPoolExecutor(max_workers=4) as ex:
    for a,o in zip(targets, ex.map(probe, targets)): out[a]=o; print("PROBE",a,o,flush=True)
json.dump(out,open("run-2026-11-05-0301-firstseen-probe.json","w"),indent=1)
print("DONE")
