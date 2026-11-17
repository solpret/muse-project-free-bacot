import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
feed=['0xBE141ED33EB3b95f6eF1416Fd36e250D0A52b2D3','0x04866CF5a12DeB5A7a8405b836B00366FbaAD6eA','0x49AD7CA933c3Eb28752B69e5fe0ada3FE13cCC9b','0xd4248743CbC45A21afDC3330090E6762069a9ABE','0x38728e1891A8993d6D071328389D84dC96D8eB15','0xFf8bDd6467213C227510Ba0de3D5E1d8159016b2','0x481BbbAe1A56F5bAfc68F2bdDB10c11ddBD90535','0xC85fd2C3bC372640Cf02cb938b9a1466Aa41403A','0x799f61Cf61BB3040cc1d59F3dd6C56d914892242','0x3832EA583BAf9C255E6E0D615cC8F9cf38Ad98c0','0x72Ded1D42261899d047d0724A17bd9905496Db08','0xECfC28d0806a73d0605dCf332c460EcfE0a621AA','0xC49edfFf50822a992F041D3F780cdB68dFa3972f','0x3EbC899b82559a1B126Cdf148A1d2518985730cA','0xD23d0003584cA99f1F6F45d677a62b01910f6907','0x2efa59D318A01B3e86f9dD4eba9baC9A5958c905','0x03b764Ff812F868320A76bCeC73Dd528C36CDD49','0x2Ce737d368afcC796779A9042Db66627Eea9E6B0','0x022e36ED4D0552AAf647D8891d2A79281ed11e65','0x62B2786076303B26b12B0990cffD72B86b58ccEc','0x4fea4ed6e70389245c41b2c9d85e8032e3c6ce31']
def chk(a):
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contracts/56/{a}",headers={"Accept":"application/json"})
        with urllib.request.urlopen(req,timeout=20) as r: j=json.load(r)
        std=j.get("stdJson",{}); src=json.dumps(std)
        names=[]
        for f in std.get("output",{}).get("abi",[]):
            if f.get("type")=="function": names.append(f.get("name",""))
        free=[n for n in names if "free" in n.lower()]
        mint=[n for n in names if "mint" in n.lower() or "claim" in n.lower()]
        return {"registry_bytes":"60b9262456de011f7d15a54cdd8c48baa8b022f" in src.lower(),"agent_word":("agentgate" in src.lower() or "agentid" in src.lower()),"free_fns":free,"mint_claim_fns":mint,"quote":("quote" in names),"n_abi":len(names)}
    except Exception as e:
        return {"error":str(e)[:150]}
out={}
with ThreadPoolExecutor(max_workers=10) as ex:
    for a,o in zip(feed, ex.map(chk, feed)):
        out[a]=o; print(a, json.dumps(o)[:300], flush=True)
json.dump(out, open("hot-leg-2026-11-05-0834-sourcify-abi.json","w"), indent=1)
print("DONE", len(out))
