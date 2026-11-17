import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
U=USER.lower().replace("0x","").rjust(64,"0")
def u1(n): return format(n,"064x")
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.defibit.io/","https://bsc.nodereal.io/"]
def call(to,data):
    for ep in EPS:
        try:
            r=subprocess.run(["curl","-s","-m","15","-H","Content-Type: application/json","-d",
                json.dumps({"jsonrpc":"2.0","id":0,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}),ep],
                capture_output=True,timeout=20)
            j=json.loads(r.stdout.decode(errors="replace"))
            if j.get("result") not in (None,"0x"): return j["result"]
            if "error" in j: return {"_err": j["error"].get("message","")[:120]}
        except Exception: continue
    return None
def dec_u(res):
    if not isinstance(res,str) or len(res)<66: return None
    try: return int(res[2:66],16)
    except Exception: return None
def dec_s(res):
    if not isinstance(res,str) or len(res)<130: return None
    try:
        ln=int(res[66:130],16)
        return bytes.fromhex(res[130:130+ln*2]).decode(errors="replace")
    except Exception: return None
W="0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C"
out={}
out["WFPASS_cost_user_1"]=dec_u(call(W, sel("cost(address,uint256)")+U+u1(1)))
out["WFPASS_cost_raw"]=str(call(W, sel("cost(address,uint256)")+U+u1(1)))[:200]
out["WFPASS_tokenURI_1"]=dec_s(call(W, sel("tokenURI(uint256)")+u1(1)))
out["WFPASS_tokenURI_1_raw"]=str(call(W, sel("tokenURI(uint256)")+u1(1)))[:300]
out["WFPASS_owner_raw"]=str(call(W, sel("owner()")))[:120]
# Sourcify metadata URLs for WFPASS + DRAGON + PIXIU
import urllib.request
for tag,A in [("WFPASS",W),("DRAGON","0xad0D8ac3D61fC8ab397B7136C69fcBf1281a4998"),("PIXIU","0x5777c2f59c65003DDebb018517B09f7ba0691202")]:
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{A}?fields=metadata",headers={"User-Agent":"Mozilla/5.0"})
        d=json.load(urllib.request.urlopen(req,timeout=15))
        md=d.get("metadata") or {}
        src=json.dumps(md)
        import re
        urls=sorted(set(re.findall(r'https?://[^\s"\'\\]+',src)))
        out[tag+"_sourcify_urls"]=urls[:20]
        out[tag+"_match"]=d.get("match")
    except Exception as e:
        out[tag+"_sourcify_urls"]="ERR "+str(e)[:100]
json.dump(out,open("hot-leg-2026-11-12-0554-gate.json","w"),indent=1)
print(json.dumps(out,indent=1)[:3000])
