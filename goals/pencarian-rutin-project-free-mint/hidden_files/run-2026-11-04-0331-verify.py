import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(to,data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0),None
        except Exception as e: err=str(e)[:160]
    return None,err
def si(v):
    try:
        if v and len(v)<=130: return int(v,16)
    except Exception: pass
    return None
items={"Agentyyds":"0x8463abFC06173BdCaEDe96c4331C30A958789629","Cosmopilot":"0x3e68AbD88885979188b97b19e8986552F10265D2","Pilotphoenix":"0xc1A54df271a455E236169F8Ff65b084eBfB00E15"}
tests=[("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("freeMinted()",""),("freeLeft()",""),("mintOpen()",""),("mintedBy(address)",enc(USER)),("freeUsed(address)",enc(USER)),("balanceOf(address)",enc(USER)),("MAX_SUPPLY()",""),("owner()",""),("AGENT_ID()",""),("agentIdRegistry()","")]
out={"block":None}
for ep in EPS:
    try: out["block"]=int(_single(ep,"eth_blockNumber",[],8,retries=0),16); break
    except Exception: pass
for n,a in items.items():
    out[n]={}
    for name,arg in tests:
        v,e=call(a,sel(name)+arg); out[n][name]={"int":si(v),"error":e if v is None else None}
    for name,arg in [("quote(address,uint256)",enc(USER)+"01".rjust(64,"0")),("freeFor(address,uint256)",enc(USER)+"01".rjust(64,"0"))]:
        v,e=call(a,sel(name)+arg); out[n][name]={"int":si(v),"error":e if v is None else None}
json.dump(out,open("run-2026-11-04-0331-verify.json","w"),indent=1)
for n in items: print(n, json.dumps(out[n]))
print("block",out["block"])
