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
FEED=['0x387886b7e8b58C71b2C9d410B035c7453f958C9B', '0x08393dad165d90e7258501fE1dfb5F3498644011', '0x9FE55C0495603397065c0BEa491D4Bd0E8D57862', '0x3cEd94dE2311caF0B0B4A5dc5515F17ac3F0884B', '0xE2EEe4b6E667eF8246e648FCe06414DfCf1859B8', '0x3a70bB640acc84eEE4d841040c306774d2B4eBD9', '0x8936421923Fe2c5B14541BCBf0462777a4463Fc9', '0x6e4c313278A1243372CaD0613fA6A1746FC228e1', '0x1B4A399cfEE071896c4034daBc65b9A95C9cF6Ea', '0x04F597501eE998a967F1AB769718d1f946552e2A', '0xC24761BC4C145b86F6407ECCf9790a97Ed73B946', '0x00570d16C749a1c4a876B36B1F76c743C990f6Ea', '0xdc6821b7bA734DD7446941Ca51f6a8826C6874bE']
VIEWS=["name()","symbol()","decimals()","totalSupply()","freeMinted()","FREE_SLOTS()","FREE_SUPPLY()","FREE_AMOUNT()","freeSharesRemaining()","agentRegistry()"]
jobs=[]
for a in FEED:
    for fn in VIEWS: jobs.append((a,fn,None))
    jobs.append((a,"freeClaimed(address)",USER))
def run(item):
    a,fn,frm=item
    v=raw(a, sel(fn)+(enc(frm) if frm else ""))
    if fn in ("name()","symbol()"): return (a,fn,cstr(v))
    return (a,fn,cint(v))
out={}
with ThreadPoolExecutor(max_workers=12) as ex:
    for a,fn,v in ex.map(run,jobs): out.setdefault(a,{})[fn]=v
print(json.dumps(out,indent=1))
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-1250-sourcify-shape.json","w"),indent=1)
