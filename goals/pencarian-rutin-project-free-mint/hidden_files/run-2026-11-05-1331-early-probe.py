import json, urllib.request
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc.publicnode.com"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
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
EARLY={
 "Agent Miner":"0x8670e99062ead2cE5402754aeDE769602FDf38b8",
 "Thronemind":"0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90",
 "Hashseers":"0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688",
 "Layerloom":"0x1B72ceC52A74537b06F713FCebA0e491f53679aE",
 "Cachejack":"0x18042D2E0bFd11fc2cc8ee1E59a6601e530C3dF5",
}
res={"block":block()}
for name,addr in EARLY.items():
    d={}
    for fn in ["totalSupply()","freeMinted()","paidMinted()","claimedFree(address)","canFreeMint(address)","balanceOf(address)"]:
        arg=enc(USER) if "address" in fn else ""
        v=raw(addr, sel(fn)+arg)
        d[fn]=cint(v)
    res[name]=d
    print(name,d)
# new Sourcify agenticspace-template contract
NEW="0x0C764987b263356104C65397c0232b6105D18E6D"
d={}
for fn in ["name()","symbol()","totalSpotsMinted()","spotsLeft()","totalSupply()"]:
    v=raw(NEW, sel(fn)); d[fn]=cstr(v) if fn in ("name()","symbol()") else cint(v)
qd=sel("quote(address,uint256)")+enc(USER)+"0000000000000000000000000000000000000000000000000000000000000001"
d["quote(user,1)"]=cint(raw(NEW,qd))
for fn in ["WEBSITE()","TWITTER()"]:
    v=raw(NEW, sel(fn)); d[fn]=cstr(v)
res["NewSourcify-0C76"]=d
print("NewSourcify-0C76",d)
json.dump(res,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-1331-early-probe.json","w"),indent=1)
