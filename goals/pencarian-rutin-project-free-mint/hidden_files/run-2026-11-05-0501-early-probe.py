import sys, json, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0")
def call(to, data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],6,retries=0)
        except Exception: continue
    return None
def num(h):
    try: return int(h,16) if h and h!="0x" else None
    except Exception: return None
SELS={"totalSupply()":"0x18160ddd","totalMinted()":"0x817e08b7","mintOpen()":"0x146ab2b2","mintedBy(address)":"0x1e8c2c42","balanceOf(address)":"0x70a08231","freeClaimed()":"0x2b8e55e4","FREE_SUPPLY()":"0x0e9a6c5f","freeMinted(address)":"0x9f2f6d5a","freeSupply()":"0x6b1a9b0e"}
ITEMS={
 "Sly Hours":"0x0000000000000000000000000000000000000000",  # placeholder replaced below
}
# addresses from snapshot keys
snap=json.load(open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json'))
want=["Sly Hours-F19A","Lotl Lagoon-57Dc","Bamboo Mafia-fc4E","Upside Down-BE59","Desert Drip-Bf59","FIN-TECH-4DeD","Eight Arms Deep-644a","Night Shift-3034","Mud Money-7C89","Honeycomb Bureau-4c80","LunaBirds"]
out={"block":None}
try: out["block"]=_single(EPS[0],"eth_blockNumber",[],6,retries=0); out["block"]=int(out["block"],16)
except Exception as e: out["block"]="ERR "+str(e)
for k in want:
    v=snap["contracts"].get(k,{})
    addr=v.get("address")
    if not addr: out[k]={"error":"no address in snapshot"}; continue
    r={}
    for name,sel in SELS.items():
        data=sel+(u if "(address)" in name else "")
        r[name]=num(call(addr,data))
    r["prev_totalSupply"]=v.get("totalSupply")
    out[k]=r; print("PROBE",k,addr,r,flush=True)
json.dump(out,open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-0501-early-probe.json','w'),indent=1)
print("DONE")
