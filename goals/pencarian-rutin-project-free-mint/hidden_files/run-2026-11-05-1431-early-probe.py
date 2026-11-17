import json, urllib.request
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc.publicnode.com"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data,frm=None):
    tx={"to":to,"data":data}
    if frm: tx["from"]=frm
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[tx,"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=15) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:100]}
            return out["result"]
        except Exception: continue
    return {"error":"rpc-fail"}
def cint(v):
    if isinstance(v,dict) or not v or v=="0x": return v
    try: return int(v,16)
    except Exception: return v
def cstr(v):
    if isinstance(v,dict) or not v or v=="0x": return v
    try:
        h=v[2:]; ln=int(h[64:128],16); return bytes.fromhex(h[128:128+ln*2]).decode(errors="replace")
    except Exception: return v
def block():
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None
# Early leads run 1301 (Thronemind/Hashseers/Layerloom/Cachejack/Agent Miner)
# + run 1331 (Smeltbots/Tumblebots) — second / first re-read respectively.
EARLY={
 "Thronemind":"0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90",
 "Hashseers":"0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688",
 "Layerloom":"0x1B72ceC52A74537b06F713FCebA0e491f53679aE",
 "Cachejack":"0x18042D2E0bFd11fc2cc8ee1E59a6601e530C3dF5",
 "Agent Miner":"0x8670e99062ead2cE5402754aeDE769602FDf38b8",
 "Smeltbots":"0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e",
  "Tumblebots":"0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17",
 "Neurolucha":"0x56eBED63452Bb02B975ceE02949DA3C02466725b",
 "Roguefall":"0x5fe03829a2f94a8bA3906459258b1305F0e68934",
 "Agent Goats":"0x0E9E0a3B46dC0d36A1Ab64f553Dd8A0693E6aAa6",
 "Agent Owls":"0x50B4bD215c409C975c940d5CF23B56D8F3ecfd3b",
 "Hirelings-A":"0xff61A6e13776B0823E18d960b3f9ee2C78685601",
 "Hirelings-B":"0xcbE18caA6d2A8BEaC563972d7457E8Afbb0E7C4a",
 "Forklings":"0xD7B3FD33e0b465B0e374906F60567D317b758FD8",
 "Auspibots":"0x3E56Ace6760ba03F3Ff669C51bcCa662bB96f955",
}
res={"block":block()}
for name,addr in EARLY.items():
    d={}
    for fn in ["totalSupply()","freeMinted()","paidMinted()","claimedFree(address)","canFreeMint(address)","balanceOf(address)","FREE_CAP()","FREE_SUPPLY()","MAX_SUPPLY()","mintedBy(address)","freeClaimed()"]:
        arg=enc(USER) if "address" in fn else ""
        v=raw(addr, sel(fn)+arg)
        d[fn]=cint(v)
    res[name]=d
    print(name,d)
# STAR / PACT / MEOW / WAGA (hot-leg reread set, main-run coverage)
STAR="0x7d390e37ed41a359f276d8764ca15432704b99b7"
res["STAR"]={"totalSupply()":cint(raw(STAR,sel("totalSupply()"))),"balanceOf(user)":cint(raw(STAR,sel("balanceOf(address)")+enc(USER)))}
PACT="0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9"
res["PACT"]={"sharesMinted()":cint(raw(PACT,sel("sharesMinted()"))),"freeMinted()":cint(raw(PACT,sel("freeMinted()"))),"paidShares()":cint(raw(PACT,sel("paidShares()"))),"freeClaimed(user)":cint(raw(PACT,sel("freeClaimed(address)")+enc(USER)))}
M="0x7a38395ad7317594a8eb6c658f3f073a693dfaab"
res["MEOW"]={"totalSupply()":cint(raw(M,sel("totalSupply()"))),"balanceOf(user)":cint(raw(M,sel("balanceOf(address)")+enc(USER)))}
WAGA="0x06a6f51D30556f4262e38485C09556fE81e6A984"
res["WAGA"]={"totalMints()":cint(raw(WAGA,sel("totalMints()"))),"freeLeft(user)":cint(raw(WAGA,sel("freeLeft(address)")+enc(USER))),"mintedBy(user)":cint(raw(WAGA,sel("mintedBy(address)")+enc(USER))),"mintOpen()":cint(raw(WAGA,sel("mintOpen()"))),"quote(user,1)":cint(raw(WAGA,sel("quote(address,uint256)")+enc(USER)+"0000000000000000000000000000000000000000000000000000000000000001"))}
print("WAGA",res["WAGA"])
json.dump(res,open(f"{BASE}/run-2026-11-05-1431-early-probe.json","w"),indent=1)
