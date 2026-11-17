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
feed=['0x5fe03829a2f94a8bA3906459258b1305F0e68934', '0xFfa2D0C21daF3417c0724767cDCB085a8DE5A99e', '0x3E56Ace6760ba03F3Ff669C51bcCa662bB96f955', '0x7aC17874Fc6a8ABDF37dC70F5061506c4f2dCe61', '0xdD4bf766eeC8E6ee9D19aA2658D281F800242368', '0xF7a19b8e8347fBE90C37C4CA4D9F456025cb1a90', '0x3895D6446621e734CEAf78b129C54Db2fBE9987F', '0x7E1603964C8A1a734e56aF7e6FcE2B97B143F8Dc', '0xaf4F8471f0BCfC34a5A0Dc6a00A5A5c7062d12fe', '0xb19a9bf73E1ACbAED3A9ae8c9c284a67f403F817', '0xD7B3FD33e0b465B0e374906F60567D317b758FD8', '0x1d27767895c9Ac9B7C4bed5632f2bd311F0b48DC', '0xe25977C41F072855A6418F222A0980C3952b91b9', '0xD16579bc0D5627A1570C04541CD3ac36B7470314', '0xD165FB8c4e3d75aC27f79Df6006534998F164c76', '0x6261ffb6D2970e61cD2920EFE2e800618d6b280e', '0xa94CDBC4F0De88981859bBd12029cA521b9E9109', '0x4EDedFA45341E35F17E4B58105bb876CCD3d6Fa9', '0x62312cC9C17B15BCceF11b92aEcC695adadeD6A1', '0x7Af8A160c127354D58Bf85E9652526d5a3413f03']
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
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-0624-sourcify-shape.json","w"),indent=1)
print("DONE")
