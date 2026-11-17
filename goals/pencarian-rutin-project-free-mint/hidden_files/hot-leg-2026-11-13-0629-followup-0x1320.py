#!/usr/bin/env python3
"""Follow-up 0629: verify new S1 0x1320... (feed 06:30 WIB)."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG="2026-11-13-0629"
T0=time.time(); USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
A="0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b"
out={"contract":A}
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def _post_one(ep,payload,timeout=12):
    r=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5)
    return json.loads(r.stdout)
def race(payload,timeout=12):
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs={ex.submit(_post_one,ep,payload,timeout):ep for ep in EPS}
        for fut in as_completed(futs):
            try:
                res=fut.result()
                if isinstance(res,list) and len(res)==len(payload): return res
            except Exception: continue
    return None
def curl(url,timeout=10):
    try:
        r=subprocess.run(["curl","-sL","-m",str(timeout),"-A","Mozilla/5.0",url],capture_output=True,timeout=timeout+5)
        return r.stdout
    except Exception: return b""
# ABI first (names exact)
abi_j=None
try: abi_j=json.loads(curl(f"https://sourcify.dev/server/v2/contract/56/{A}?fields=abi",10).decode(errors="replace"))
except Exception: pass
abi=abi_j.get("abi") if isinstance(abi_j,dict) else None
names=[]
if abi:
    names=[(f.get("name") or "") for f in abi if isinstance(f,dict)]
out["abi_names"]=names
out["abi_n"]=len(names)
json.dump(abi_j,open(BASE+f"hot-leg-{TAG}-followup-0x1320-abi.json","w"),indent=1)
# views: exact names from ABI where possible
VIEWS=["freeLotsCap()","FREE_LOTS_CAP()","freeTokensPerLot()","FREE_TOKENS_PER_LOT()","freeLotsClaimed()","freeClaimed(address)","freeClaimedByAgent(address)","claimFree()","quote(address,uint256)","contractURI()","name()","symbol()","token()","saleToken()","agentRegistry()","freeLeft()","freeClaimed()","totalMinted()","mintStart()","mintOpen()","balanceOf(address)"]
calls=[];keys=[]
for i,sig in enumerate(VIEWS):
    base=sig.split("(")[0]
    if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
    elif sig=="quote(address,uint256)": data=sel(sig)+enc(USER)+format(1,"064x"); key="quote_user_1"
    else: data=sel(sig); key=base
    calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":A,"data":data},"latest"]}); keys.append(key)
res=race(calls,timeout=12)
views={}
if res:
    for it,key,sig in zip(res,keys,VIEWS):
        if isinstance(it,dict) and "error" in it: views[key]=None
        elif isinstance(it,dict) and it.get("result"):
            raw=it["result"]
            if key in ("name","symbol","contractURI"):
                try:
                    b=bytes.fromhex(raw[2:]); off=int.from_bytes(b[:32],"big"); ln=int.from_bytes(b[32:64],"big")
                    views[key]=b[64:64+ln].decode(errors="replace") if off==32 else b[32:].decode(errors="replace").strip("\x00")
                except Exception: views[key]=raw[:80]
            elif key=="quote_user_1":
                try:
                    b=bytes.fromhex(raw[2:]); words=[int.from_bytes(b[i:i+32],"big") for i in range(0,min(len(b),160),32)]
                    tail=None
                    if len(words)>=5 and words[4]<len(b):
                        off=words[4]; ln=int.from_bytes(b[off:off+32],"big"); tail=b[off+32:off+32+ln].decode(errors="replace")
                    views[key]={"words":words,"tail":tail}
                except Exception as e: views[key]={"err":str(e)[:80]}
            else: views[key]=to_int(raw)
out["views"]=views
out["summary"]={k:v for k,v in views.items() if v is not None}
# method A: contract-address web search via browser.search equivalent? use curl to bscscan? just record Sourcify metadata urls
meta=None
try: meta=json.loads(curl(f"https://sourcify.dev/server/v2/contract/56/{A}",10).decode(errors="replace"))
except Exception: pass
out["sourcify_meta_keys"]=list(meta.keys()) if isinstance(meta,dict) else None
if isinstance(meta,dict):
    out["sourcify_meta"]=str(meta)[:1500]
out["elapsed_s"]=round(time.time()-T0,1)
json.dump(out,open(BASE+f"hot-leg-{TAG}-followup-0x1320.json","w"),indent=1)
print(json.dumps(out,indent=1))
