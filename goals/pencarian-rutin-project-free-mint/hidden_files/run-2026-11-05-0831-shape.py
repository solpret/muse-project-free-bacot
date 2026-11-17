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
feed=['0xBE141ED33EB3b95f6eF1416Fd36e250D0A52b2D3', '0x04866CF5a12DeB5A7a8405b836B00366FbaAD6eA', '0x49AD7CA933c3Eb28752B69e5fe0ada3FE13cCC9b', '0xd4248743CbC45A21afDC3330090E6762069a9ABE', '0x38728e1891A8993d6D071328389D84dC96D8eB15', '0xFf8bDd6467213C227510Ba0de3D5E1d8159016b2', '0x481BbbAe1A56F5bAfc68F2bdDB10c11ddBD90535', '0xC85fd2C3bC372640Cf02cb938b9a1466Aa41403A', '0x799f61Cf61BB3040cc1d59F3dd6C56d914892242', '0x3832EA583BAf9C255E6E0D615cC8F9cf38Ad98c0', '0x72Ded1D42261899d047d0724A17bd9905496Db08', '0xECfC28d0806a73d0605dCf332c460EcfE0a621AA', '0xC49edfFf50822a992F041D3F780cdB68dFa3972f', '0x3EbC899b82559a1B126Cdf148A1d2518985730cA', '0xD23d0003584cA99f1F6F45d677a62b01910f6907', '0x2efa59D318A01B3e86f9dD4eba9baC9A5958c905', '0x03b764Ff812F868320A76bCeC73Dd528C36CDD49', '0x2Ce737d368afcC796779A9042Db66627Eea9E6B0', '0x022e36ED4D0552AAf647D8891d2A79281ed11e65', '0x62B2786076303B26b12B0990cffD72B86b58ccEc']
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
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-0831-sourcify-shape.json","w"),indent=1)
