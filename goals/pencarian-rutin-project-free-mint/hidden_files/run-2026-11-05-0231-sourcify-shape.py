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
feed=['0x056c0222cE93E415fe5E7974577715E722E439C9','0x025D5A1eD084636770FAD86229ac97D2f25f9244','0x8402Febcd6fFE2043eD36f7107712BB9a2FDE0fc','0x1619452C940230aaa10676e9f10bf204fB797777','0x3aa0c21ca50e47ca210289C14263e50D5f063b74','0xA588dF8311255069c05604c2e7C7465ECDCc4c88','0x3342Da62BD986B306A1D9da2c4395Cd300420582','0x78Fb44801E01Fd8e290568EDA975C79848fbdC64','0xF8CF986488DD675043021d8340DEE809A71AE1A7','0x857169CdE48cf9fD8874E26a43FbbcA838Fc56a1','0x5cFbe7a6968D7ACDA9cd127370fc0017DB19b486','0xdDBE18962479a683aEC5a78eB775340Ab51a9c1b','0x5AD666A89De917b4EabFB20De881A6776169d39c','0xb0Eb05D28c02CabfB42f26715153B4dB84CeEC38','0x13876666D7dbF30c4c63dbEBF370234E9417bd09','0xC4251a0e2ed024E5070a72692D535ddD3cb85aEF','0x69c2BA04381934AB3cD30Fd7Ffc00dfa41f989f1','0x981Ff66639414c41C80c9D89D39748e0840c7777','0x48CCcb8426aFC610212d9Ab376C36FE3E1E071Db','0x50cF1C98C46Cf78F04f2F61161EAdA02944fBc02']
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
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-0231-sourcify-shape.json","w"),indent=1)
print("DONE")
