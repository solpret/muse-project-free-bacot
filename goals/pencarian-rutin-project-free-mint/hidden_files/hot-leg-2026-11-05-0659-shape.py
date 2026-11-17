import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
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
def dec_str(v):
    try:
        b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[32:64],'big'); return b[64:64+ln].decode(errors='replace')
    except Exception: return None
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0"); one="0"*63+"1"
feed=['0x59F2C83890a8F0b5501a41F02c1B5D2fC754f20F','0x062fc2cd02485386e34249fe3d769f41A7FF2994','0x2431bA1a56d1134cB5D0ffd0b6f357e79E8c3D52','0x08b1A979Dd997492EEcc010fe986eA2e2925e620','0xEc1C5898dA3f8ffC5d147a27d5C7D63DCC9F268d','0xB838d6AD5eF89a2DEe2C1b89Cb5Eda48B6af0F75','0xcB76bFD6AB414F7d998240B859C05F0152F9DB46','0x94abFD344aec55177E049041d42D44c4890763e8','0xC7855a313987D2F64450504c72181E4CF3137148','0xc66944EbD784F28c09fd0819d4fD5e5f69B4A22d','0xF95156D447595562e0c94F8EDCC4B5f57D147A07','0x424b240Fa7379dc72974Df401A375b0A33BB6477','0x37B7f53d320d36E37c1dd8FD53311B9c32f93565','0xcbE18caA6d2A8BEaC563972d7457E8Afbb0E7C4a','0x4f5c604d96D164289925075A9AAeDF847F9f3aaE','0x9610195ac5304B697080ea1252C70613a098E388','0x65d591267eBd42a28b53c4004EA1A9769E545233','0xfCa100D8F9dE83F79d72fac1f3AfCd8c9cE2c669','0x0dDeE36a1ac1ba28F5F6B92379b8f5989181df76','0x9cc08ff6c63c938e0d48A9DFC647460DF7b419Bd']
def shape(a):
    o={}
    o['name']=dec_str(call(a,sel("name()"))); o['symbol']=dec_str(call(a,sel("symbol()")))
    o['decimals']=iv(call(a,sel("decimals()"))); o['totalSupply']=iv(call(a,sel("totalSupply()")))
    o['freeMinted']=iv(call(a,sel("freeMinted()"))); o['freeClaimed_total']=iv(call(a,sel("freeClaimed()")))
    o['FREE_SUPPLY']=iv(call(a,sel("FREE_SUPPLY()"))); o['FREE_SLOTS']=iv(call(a,sel("FREE_SLOTS()")))
    o['freeClaimed_user']=iv(call(a,sel("freeClaimed(address)")+u)); o['freeMinted_user']=iv(call(a,sel("freeMinted(address)")+u))
    o['quote_user1']=iv(call(a,sel("quote(address,uint256)")+u+one))
    o['agentRegistry']=call(a,sel("agentRegistry()")); o['registry']=call(a,sel("registry()"))
    o['freeSharesRemaining']=iv(call(a,sel("freeSharesRemaining()"))); o['freeAvailable']=iv(call(a,sel("freeAvailable()")))
    return o
out={}
with ThreadPoolExecutor(max_workers=20) as ex:
    for a,o in zip(feed, ex.map(shape, feed)): out[a]=o; print("SHAPE",a,o,flush=True)
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-0659-sourcify-shape.json","w"),indent=1)
# retry reread failures
retry={}
retry['NIULAI_phase']=iv(call("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF",sel("phase()")))
retry['DROID_totalMinted']=iv(call("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",sel("totalMinted()")))
retry['IMARS_freeMinted']=iv(call("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",sel("freeMinted()")))
print("RETRY",retry)
json.dump(retry,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-0659-retry.json","w"),indent=1)
print("DONE")
