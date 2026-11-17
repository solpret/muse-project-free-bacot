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
feed=['0xD68995d343016f0Bb62e8787F0f03AAAEd118d8a','0xCfb9beF5F7B748aC72311F057f3a888BC73334D9','0x88886f0fD371dfF856291bAdcEd45922bC888888','0x26131Eb28A342cDF75FAFa9EfFd3cE20C6CA518a','0x6fdE01375Dee314C56193e177512767f88545232','0x8AC96df1D3Dbd7c99A54CB4e50599cE129015E50','0xE07150DD3A870fF0115Fc4e3c80529f92e294D89','0x63dea5aCdbE1F27c968907D08610A5f0A0284bA6']
def shape(a):
    o={}
    o['name']=dec_str(call(a,sel("name()"))); o['symbol']=dec_str(call(a,sel("symbol()")))
    o['decimals']=iv(call(a,sel("decimals()"))); o['totalSupply']=iv(call(a,sel("totalSupply()")))
    for n,arg in [("freeSharesRemaining()",""),("freeClaimed()",""),("freeMinted()",""),("FREE_SLOTS()",""),("FREE_SUPPLY()",""),("freeSharesClaimed(address)",u),("freeClaimed(address)",u),("freeAvailable(address)",u),("quote(address,uint256)",u+one),("mintOpen()",""),("launched()","")]:
        o[n]=iv(call(a,sel(n)+arg))
    o['agentRegistry']=call(a,sel("agentRegistry()")); o['registry']=call(a,sel("registry()"))
    return o
out={}
with ThreadPoolExecutor(max_workers=8) as ex:
    for a,o in zip(feed, ex.map(shape, feed)): out[a]=o; print("SHAPE",a,o,flush=True)
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-0231-trackc-shape.json","w"),indent=1)
print("DONE")
