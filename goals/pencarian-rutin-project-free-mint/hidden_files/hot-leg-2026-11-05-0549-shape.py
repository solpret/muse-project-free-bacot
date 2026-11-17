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
feed=['0x8B05C4f3524A9Fa70746C25A6591baBE03D1BEcA','0x91E5E24F6E571Ef89659E6db04a0b3d42C319048','0x559Daa00edfF07B8ce17D32137b92Cb73872ebB9','0x1a24b126C909BdDdDC61C6cA6c5d359c33730f8B','0xF5b6e745B683406025dF27CF34E851668eB7acB5','0x3f161C1BAc7796B64dae3D4C6194651d9a847d5e','0x912077671da5c1046EB3eDe6c462F44cd9AB5d9F','0x52511b58190BccC46626c29438a9005b6556F0B1','0x2e2CECe9c29C968C90f6518cF9051DD3B406d396','0x5AFDa06d2DEa1318202C9DD31B35d83987327e5A','0xe150f80E440f6F3dA564B8b0c1B7455F714DeDaf','0x047AB0ED6c5Db7146f9079cab3B747C4b103bf6a','0x77Ea4071400f0a4d69Dd1E613a2BC544aA566ae6','0x56eBED63452Bb02B975ceE02949DA3C02466725b','0xBb4f824B3B87b03ea2c8907d0449BDf2d92a4Dd1','0xa150eD6b685cfbEb6C3d7dA3F89E1C34CAAd50F2','0xf361B3FD4161d81b40e0c0DDef005A6a9ae3eCe2','0x348455Be18b700caE8AA425BD84E456e47F16E8b','0x30C59a606feCb9AEdc73ab252E7Aba48E6d20353','0xF0BAd29eC68AF727b3E042B0b3bdcf414aFcA127']
def shape(a):
    o={}
    o['name']=dec_str(call(a,sel("name()"))); o['symbol']=dec_str(call(a,sel("symbol()")))
    o['decimals']=iv(call(a,sel("decimals()"))); o['totalSupply']=iv(call(a,sel("totalSupply()")))
    o['freeMinted']=iv(call(a,sel("freeMinted()"))); o['freeClaimed_total']=iv(call(a,sel("freeClaimed()")))
    o['FREE_SUPPLY']=iv(call(a,sel("FREE_SUPPLY()"))); o['FREE_SLOTS']=iv(call(a,sel("FREE_SLOTS()")))
    o['freeClaimed_user']=iv(call(a,sel("freeClaimed(address)")+u)); o['freeMinted_user']=iv(call(a,sel("freeMinted(address)")+u))
    o['quote_user1']=iv(call(a,sel("quote(address,uint256)")+u+one))
    o['agentRegistry']=call(a,sel("agentRegistry()")); o['registry']=call(a,sel("registry()"))
    return o
out={}
with ThreadPoolExecutor(max_workers=20) as ex:
    for a,o in zip(feed, ex.map(shape, feed)): out[a]=o; print("SHAPE",a,o,flush=True)
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-0549-sourcify-shape.json","w"),indent=1)
print("DONE")
