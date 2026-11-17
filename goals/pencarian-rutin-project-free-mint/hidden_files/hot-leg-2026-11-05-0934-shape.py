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
feed=['0x62EC413381B74387b57F1E2734cdd2E5b96a57B7','0x320eaFF5D69Af30696FbDb179f70EFe9C511361c','0xcdbdB027BBcbEc8217859f4f244A0629Fa27Ddb2','0xF136482BE355d431BA02D657a50691621C78d9B0','0x5DDC00FE4A43FAA59d22cD9DF291dAA53fdbf172','0xa650d6d58C91aE9a2674dfC60D99ed24D97Bd571','0x12167D06c9CecC0b5EAFD166892CFbf8240fd971','0xE9bF181aEDb61c320787cd707a36aB0C6524aA6b','0x37336d3E8faE51ddA4Ce0f213c72631A87119ED4','0xc3e4029b0cfdcaFaF91fC0e33ff0deC597736207','0xe24F690b14DDc81e4B41B7BF1dE10c06A3f5b348','0xA1f2FB3B5D1a3B94e7d4efd795154862DbC1055c']
def shape(a):
    o={}
    o['name']=dec_str(call(a,sel("name()"))); o['symbol']=dec_str(call(a,sel("symbol()")))
    o['decimals']=iv(call(a,sel("decimals()"))); o['totalSupply']=iv(call(a,sel("totalSupply()")))
    o['freeMinted']=iv(call(a,sel("freeMinted()"))); o['freeClaimed_total']=iv(call(a,sel("freeClaimed()")))
    o['FREE_SUPPLY']=iv(call(a,sel("FREE_SUPPLY()"))); o['FREE_SLOTS']=iv(call(a,sel("FREE_SLOTS()"))); o['FREE_AMOUNT']=iv(call(a,sel("FREE_AMOUNT()")))
    o['freeClaimed_user']=iv(call(a,sel("freeClaimed(address)")+u)); o['freeMinted_user']=iv(call(a,sel("freeMinted(address)")+u))
    o['quote_user1']=iv(call(a,sel("quote(address,uint256)")+u+one))
    o['agentRegistry']=call(a,sel("agentRegistry()")); o['registry']=call(a,sel("registry()"))
    o['freeSharesRemaining']=iv(call(a,sel("freeSharesRemaining()"))); o['freeAvailable']=iv(call(a,sel("freeAvailable()")))
    return o
out={}
with ThreadPoolExecutor(max_workers=20) as ex:
    for a,o in zip(feed, ex.map(shape, feed)): out[a]=o; print("SHAPE",a,o,flush=True)
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-0934-sourcify-shape.json","w"),indent=1)
print("DONE")
