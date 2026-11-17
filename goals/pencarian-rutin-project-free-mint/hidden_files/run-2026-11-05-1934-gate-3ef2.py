"""Gate methods (I)+(J) + Boltbook shape-check for run 1934. Read-only."""
import json, urllib.request, base64, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR="0x3ef2A97Abf2E43182eACAe323B82d2CAC2132C6A"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def rpc(m,p,t=10):
    for ep in EPS:
        try: return _single(ep,m,p,t,retries=0)
        except Exception: continue
    return None
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,data):
    v=rpc("eth_call",[{"to":to,"data":data},"latest"])
    return v
# (I) tokenURI(1)
d=sel("tokenURI(uint256)")+format(1,"064x")
v=call(ADDR,d)
print("tokenURI(1) raw:", (v or "")[:400])
if v and v!="0x":
    try:
        b=bytes.fromhex(v[2:]); off=int.from_bytes(b[32:64],"big"); ln=int.from_bytes(b[64:96],"big")
        s=b[96:96+ln].decode(errors="ignore")
        print("tokenURI(1) decoded:", s[:800])
        if s.startswith("data:application/json;base64,"):
            print("tokenURI json:", base64.b64decode(s.split(",",1)[1]).decode(errors="ignore")[:800])
    except Exception as e: print("tokenURI decode err:", e)
# (J) ABI grep
meta=json.load(open(HF+"run-2026-11-05-1924-meta-0x3ef2A97A.json"))
abi=meta["metadata"]["output"]["abi"]
fns=[i.get("name","") for i in abi if i.get("type")=="function"]
print("ABI fns:", sorted(fns))
print("site-like fns:", [n for n in fns if any(k in n.lower() for k in ("website","site","url","domain","external","twitter","link"))])
print("has contractURI:", "contractURI" in fns, "| has tokenURI:", "tokenURI" in fns)
# (D) same-family pattern fetch
for url in ("https://agentglyph.pages.dev/","https://agentglyph.vercel.app/","https://agentglyph.surge.sh/"):
    try:
        req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            body=r.read().decode(errors="ignore")
            print(url, "HTTP", r.status, "len", len(body), "prints-contract:", "0x3ef2A97Abf2E43182eACAe323B82d2CAC2132C6A" in body or "0x3ef2a97abf2e43182eacae323b82d2cac2132c6a" in body.lower())
    except Exception as e:
        print(url, "ERR", type(e).__name__, str(e)[:100])
