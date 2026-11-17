import json, sys, datetime
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
    except Exception:
        return None
VIEWS=["totalSupply()","totalMinted()","freeMinted()","freeClaimed()","FREE_CAP()","FREE_SUPPLY()","MAX_SUPPLY()","freeMintOpen()","mintOpen()","canFreeMint(address)","canClaimFree(address)","claimedFree(address)","balanceOf(address)","AGENT_REGISTRY()","agentRegistry()","registry()"]
TARGETS={
 "HATCHIEggy":"0xF2a6D1A5Da92d611cf8eC614548D4d6E83BEB6D8",
 "Titan Wolf Agent":"0xf6972e6263Aa411F4E5c4E8d25edbae6DDF68b52",
 "Storm Nomad Agent":"0x74D09dca3326afAE7d078e29F004e2ECF53c740f",
}
FIRST={"MILLION":131883591,"Nova Pylon":131882604,"Ethereal Zebra Agent":131882745,"Loom Vellum":131883110,"Void Rat Agent":131883444,"Pearl Mesa":131883586,"Zenith Arch":131884092,"Cyber Scribe":131884137}
out={}
for name,addr in TARGETS.items():
    res={}
    for v in VIEWS:
        arg=u(USER) if "address" in v else ""
        res[v]=call(addr,v,arg)
    out[name]={"address":addr, **res}
    print(name, {k:val for k,val in res.items() if val is not None}, flush=True)
    try:
        b=race("eth_getBlockByNumber",[hex(FIRST[name]),False],timeout=10)
        ts=int(b["timestamp"],16)
        wib=datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
        print(name,"first_block",FIRST[name],"->",wib,"WIB", flush=True)
        out[name]["first_mint_wib"]=wib
    except Exception as e:
        print(name,"block ts ERR",type(e).__name__,e, flush=True)
json.dump(out, open("triage-firstseen-2026-11-06-0401-verify.json","w"), indent=1)
print("DONE", flush=True)
