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
 "MILLION":"0xD36B54fbd4c9fA99731b52907713c9e1983aD8a4",
 "Nova Pylon":"0x61b1668af9A34Cfde0B4e8565ef3C28aACC3DC2E",
 "Ethereal Zebra Agent":"0x4B2469E26451C0813E95D2Fbd9683b50E1811035",
 "Loom Vellum":"0xbC81a0909eB530D7809f9a5B4518999cf20292a3",
 "Void Rat Agent":"0xf4FA74D20A445cBd0a2559890b8eb129BefB8eea",
 "Pearl Mesa":"0x638Ca21ADE5EA01AD15CF6193cbc2B1206B307D1",
 "Zenith Arch":"0xABD3f4F0c611f6548445F1c5Fe5fbc636EeE3773",
 "Cyber Scribe":"0x96922BC3f136967b55Dab654250F90112C92C0Dc",
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
json.dump(out, open("triage-firstseen-2026-11-06-0331-verify.json","w"), indent=1)
print("DONE", flush=True)
