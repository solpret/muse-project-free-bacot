import json, urllib.request, subprocess
from Crypto.Hash import keccak
ADDR="0x08Df7970BB2C632908e3df036d0439420D9cE858"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def get(url, timeout=25):
    req=urllib.request.Request(url, headers={"User-Agent":"free-bacot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r: return r.read().decode(errors="replace")
try:
    meta=json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi"))
    abi=meta.get("abi",[])
    names={e["name"] for e in abi if e.get("type")=="function"}
    print("SOURCIFY verified, fns:", len(names))
    print("names:", sorted(names))
except Exception as e:
    print("SOURCIFY FAIL:", type(e).__name__, str(e)[:200])
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
views=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","name()","symbol()","balanceOf(address)","freeClaimed(address)","freeMinted(address)","mintedBy(address)","owner()","agentRegistry()","contractURI()"]
calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":(sel(sig)+enc(USER) if "(address)" in sig else sel(sig))},"latest"]} for i,sig in enumerate(views)]
for ep in ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]:
    try:
        r=subprocess.run(["curl","-sL","--max-time","25","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(calls)],capture_output=True,text=True,timeout=30)
        res=json.loads(r.stdout)
        if isinstance(res,list) and len(res)==len(calls):
            for sig,item in zip(views,res):
                v=item.get("result") if isinstance(item,dict) and "error" not in item else None
                if v and v!="0x":
                    try: print(sig, "->", int(v,16) if len(v)<=66 and all(c in "0123456789abcdefx" for c in v) else v[:120])
                    except Exception: print(sig, "->", v[:120])
            break
    except Exception as e:
        print("RPC fail", ep, e); continue
json.dump({"addr":ADDR}, open("run-2026-11-11-1301-probe-08df.json","w"))
