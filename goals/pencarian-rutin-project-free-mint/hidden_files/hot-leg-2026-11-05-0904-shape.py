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
feed=['0xBB416Cc2ae23d29337B0339aABbe5E3EB7493225','0x4F350e7e09cC94AD3152C57d10EFe42FBb0E9579','0x5a51EFAC975154e87C263574837d58D33450810C','0xd99648101d280c63EeF2DF101ebfC55a0893136A','0x8D4A7A96DB3981702583fc6c47CC2b2fcef9b61c','0x6F83aF88150B986fd0010cEA5f88E4282e5bf659','0x168c0D4569632E9c8692F447Fb0F1CFf57c000fA','0x8aE3997D826461d619fa01fbDf247a25677B81bA','0x8a59c7355314b0ae15b8BAaF3E0688cc1B9897A3','0xCb8637E4B6154979f9dA60e39b238d2C67aCb0bF','0x9791d92B63a566AC578e6070ee1F8546C8b2153B','0x86956Bc830EB62110820Ae79164BeF61c7E31936','0x76551A300Ddb2D8a4957e568c4cf5Ec8CFdB66db','0xDDF07685E55Eb368403E1570A491aE36Bc5e2890','0xB0eC18848E9fC9Fc672EA6aAd7576508aB2e5D31','0xa55eaC62D1Fe8C3754E3f713692F5650d040CaD6']
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
    o['mintedBy_user']=iv(call(a,sel("mintedBy(address)")+u)); o['freeUsed_user']=iv(call(a,sel("freeUsed(address)")+u))
    return o
out={}
with ThreadPoolExecutor(max_workers=20) as ex:
    for a,o in zip(feed, ex.map(shape, feed)): out[a]=o; print("SHAPE",a,o,flush=True)
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-0904-sourcify-shape.json","w"),indent=1)
# Sourcify ABI registry-byte check (fast, parallel)
def abi_check(a):
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contracts/56/{a}",headers={"Accept":"application/json"})
        with urllib.request.urlopen(req,timeout=15) as r: j=json.load(r)
        std=j.get("stdJson",{}); src=json.dumps(std)
        reg="60b9262456de011f7d15a54cdd8c48baa8b022f" in src.lower()
        ag="agentgate" in src.lower() or "agentid" in src.lower()
        names=[]
        try:
            for f in std.get("output",{}).get("abi",[]): names.append(f.get("name",""))
        except Exception: pass
        return {"registry_bytes":reg,"agent_word":ag,"abi_names_sample":names[:40],"has_abi":bool(names)}
    except Exception as e:
        return {"error":str(e)[:120]}
abi={}
with ThreadPoolExecutor(max_workers=10) as ex:
    for a,o in zip(feed, ex.map(abi_check, feed)): abi[a]=o; print("ABI",a,o,flush=True)
json.dump(abi,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-0904-sourcify-abi.json","w"),indent=1)
print("DONE")
