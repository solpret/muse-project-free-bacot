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
feed=['0x52Ea279BF4013Dc3eeA7Cd5A639E7b517E500f4E','0x4368D7047d3DE03D088460A7AfF437f017e3B22F','0x83648dD42722Fb24Bf04c887EBB023C1849c1D71','0xC8f664A922DCC33ebB7858958599454F8369d45F','0xf7fF99bd6bd739A27e3511E96c7ABB8ffF460267','0xd1D90f968bCbbdEa49520Fde5b71bBeb9555738b','0x273fc2C7705B23eb129E35aC8Da26348E6Fc4980','0xCA0D24D4Aee7a9855ea33e27fbAA2f8545013aD2','0x32CD875BC8289EC648d53AeB4Ba1688e7e79a0D2','0x4Bb7f2d9fdE2E6ff48337e6ad2E6e837e0e67777','0x6F066D0604f0cB8A9b32dFc525Ec25D1a1671eB2','0x22ad1E0B9aDC23C2FB8c2aBBAf3E5Fee22BB6f73','0x8b9403566c811C8844f8b8cF9Bf61ee38463D612','0x6B7619c7F3ca816D6E5C00fa6c79D99caCa9Ef01','0x3B843b46CDFa173e947E1d662629933af1D94231','0xb4AC39E5040D4CC8E1f58fc8Ba8743A41cC09Def','0x6F8815CD3c1B0895814A2d4911492e4FF5a5Ef86','0xa422fbf16E0e2f81A38f74B1be8b770B97575529','0xBC3C55a7b69C7c75b44bfEF11302E9f64bD3Cf0d','0xDF4B0b420F0684E654931Bc37b2f230dF8e81704']
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
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-0301-sourcify-shape.json","w"),indent=1)
print("DONE")
