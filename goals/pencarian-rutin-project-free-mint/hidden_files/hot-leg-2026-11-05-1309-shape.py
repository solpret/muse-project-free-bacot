import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
RPCS=["https://bsc.publicnode.com","https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:60]}
            return out["result"]
        except Exception: continue
    return {"error":"rpc-fail"}
def cint(v):
    if isinstance(v,dict): return v
    try: return int(v,16) if v and v!="0x" else 0
    except Exception: return v
def cstr(v):
    if isinstance(v,dict) or not v or v=="0x": return v
    try:
        h=v[2:]; ln=int(h[64:128],16); return bytes.fromhex(h[128:128+ln*2]).decode(errors="replace")
    except Exception: return v
FEED=['0x5AC18bF9Ac3782F68aaC0523f0a1c576fe05aba6','0x778e0a368972bA86aAAbE3fAa05B944581A295d9','0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17','0x24B326f43Ac5776E5c701048fbd9993D81905e61','0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e','0xf1d76659837c5796f8E25f4b5d2d8E692E49BD8A','0x080300c762ab742b76A551c09E55460a7D531BAf','0x6CdcE83aa952233B3CF2436BF6D0F6DB1Ea12cCe','0xe7CABBD4901f7C3C8e44bc0e32fEC52922A7F971','0x41956f5E88bF747Ff4d9f7D21E63c87847FF312F','0xbF097aef8287E089fBC55b3ae65Ee2265cD26BD5']
VIEWS=["name()","symbol()","decimals()","totalSupply()","freeMinted()","FREE_SLOTS()","FREE_SUPPLY()","FREE_AMOUNT()","freeSharesRemaining()","freeClaimed(address)","freeFor(address)","freeLeft(address)","freeAvailable(address)","agentRegistry()","registry()","mintFree()"]
jobs=[]
for a in FEED:
    for fn in VIEWS:
        jobs.append((a,fn,USER if "(address)" in fn else None))
def run(item):
    a,fn,frm=item
    v=raw(a, sel(fn)+(enc(frm) if frm else ""))
    if fn in ("name()","symbol()"): return (a,fn,cstr(v))
    return (a,fn,cint(v))
out={}
with ThreadPoolExecutor(max_workers=12) as ex:
    for a,fn,v in ex.map(run,jobs): out.setdefault(a,{})[fn]=v
for a in FEED:
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",headers={"User-Agent":"curl"})
        with urllib.request.urlopen(req,timeout=15) as r: d=json.load(r)
        abi=d.get("abi") or d.get("stdJson",{}).get("abi") or []
        fns=sorted({f.get("name") for f in abi if f.get("type")=="function" and f.get("name")})
        out[a]["_abi_functions"]=fns
    except Exception as e:
        out[a]["_abi_functions"]={"error":str(e)[:80]}
# WAGA pool re-check (track-C lead gate-blocked run 13:04)
WAGA="0x06a6f51D30556f4262e38485C09556fE81e6A984"
w={}
for fn,frm in [("totalMints()",None),("freeLeft(address)",USER),("mintedBy(address)",USER),("mintOpen()",None)]:
    v=raw(WAGA, sel(fn)+(enc(frm) if frm else ""))
    w[fn]=cint(v)
# quote(user,1): quote(address,uint256)
qd=sel("quote(address,uint256)")+enc(USER)+"0000000000000000000000000000000000000000000000000000000000000001"
w["quote(user,1)"]=cint(raw(WAGA,qd))
out["_waga_recheck"]=w
print(json.dumps(out,indent=1))
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-1309-sourcify-shape.json","w"),indent=1)
