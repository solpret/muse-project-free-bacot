import json, sys, urllib.request, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def u(a): return a[2:].lower().rjust(64,"0")
def call(to,sig,args=""):
    try:
        r=race("eth_call",[{"to":to,"data":sel(sig)+args},"latest"],timeout=10)
        if not r or r=="0x": return None
        return int(r,16)
    except Exception as e:
        return None
VIEWS=["totalSupply()","totalMinted()","freeMinted()","freeClaimed()","FREE_CAP()","FREE_SUPPLY()","MAX_SUPPLY()","freeMintOpen()","mintOpen()","canFreeMint(address)","canClaimFree(address)","claimedFree(address)","balanceOf(address)","AGENT_REGISTRY()","agentRegistry()"]
TARGETS={
 "HOOTCAST":"0xbFccd7dE6eF1B3D81632412600a933CD6De14B77",
 "Agent Eggs Companion":"0xA625f5Ca282B29E8346179bDbB493939c37b2ac1",
 "AgentLumen":"0xC34A47BC9A2002c9aba58AFC17242F3818cD4Bce",
 "Agent Creatures":"0xF7245511A890a42F911c776824c665E2da3cedb3",
}
out={}
for name,addr in TARGETS.items():
    res={}
    for v in VIEWS:
        arg=u(USER) if "address" in v else ""
        res[v]=call(addr,v,arg)
    out[name]={"address":addr, **res}
    print(name, {k:val for k,val in res.items() if val is not None}, flush=True)
try:
    req=urllib.request.Request("https://sourcify.dev/server/v2/contract/56/0xbFccd7dE6eF1B3D81632412600a933CD6De14B77?fields=abi", headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=25) as r: ab=json.load(r).get("abi",[])
    names=sorted({f.get("name") for f in ab if isinstance(f,dict) and f.get("name")})
    print("HOOTCAST ABI:", names, flush=True)
    print("HOOTCAST agent-ish:", [n for n in names if "agent" in n.lower() or "registry" in n.lower() or "gate" in n.lower()], flush=True)
    out["HOOTCAST"]["abi_names"]=names
except Exception as e:
    print("HOOTCAST ABI ERR", type(e).__name__, e, flush=True)
for name,blk in [("HOOTCAST",131876453),("Agent Eggs Companion",131876077),("AgentLumen",131876176),("Agent Creatures",131877138)]:
    try:
        b=race("eth_getBlockByNumber",[hex(blk),False],timeout=10)
        ts=int(b["timestamp"],16)
        wib=datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
        print(name,"first_block",blk,"->",wib,"WIB", flush=True)
        out[name]["first_mint_wib"]=wib
    except Exception as e:
        print(name,"block ts ERR",type(e).__name__,e, flush=True)
json.dump(out, open("triage-firstseen-2026-11-06-0301-verify.json","w"), indent=1)
print("DONE", flush=True)
