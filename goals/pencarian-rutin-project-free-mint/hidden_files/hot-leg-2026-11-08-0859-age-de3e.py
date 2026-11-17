import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
ADDR="0xde3e3e9e2f87f285f0f26ea54923a933b10df140"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
data=sel("freeClaimed()")
head=132309267
blk48=head-384000  # ~48h at 0.45s/block
out={"head_block":head,"block_48h_ago":blk48}
def to_int(v):
    try: return int(v,16)
    except Exception: return None
# try fast_rpc batch with explicit block
for ep in ["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.bnbchain.org/"]:
    try:
        res=batch([("eth_call",[{"to":ADDR,"data":data},hex(blk48)])], endpoint=ep, timeout=10)
        out[f"fast_rpc_{ep}"]=res[0] if res else None
        v=to_int(res[0]) if res and res[0] else None
        if v is not None:
            out["freeClaimed_48h_ago"]=v; out["method"]=f"fast_rpc {ep}"; break
    except Exception as e:
        out[f"fast_rpc_{ep}_err"]=str(e)[:120]
if "freeClaimed_48h_ago" not in out:
    # fallback: raw urllib eth_call
    for ep in ["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/"]:
        try:
            req=urllib.request.Request(ep, data=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":data},hex(blk48)]}).encode(), headers={"Content-Type":"application/json"})
            resp=json.loads(urllib.request.urlopen(req, timeout=10).read())
            if "result" in resp and resp["result"]:
                out["freeClaimed_48h_ago"]=to_int(resp["result"]); out["method"]=f"urllib {ep}"; break
            out[f"urllib_{ep}"]=str(resp)[:150]
        except Exception as e:
            out[f"urllib_{ep}_err"]=str(e)[:120]
v=out.get("freeClaimed_48h_ago")
if v==0: out["verdict"]="VERIFIED <=48h (freeClaimed was 0 at 48h-ago block)"
elif isinstance(v,int): out["verdict"]=f"AGE-EXCLUDED >48h (freeClaimed already {v} at 48h-ago block)"
else: out["verdict"]="UNVERIFIED - 48h-ago read failed on all endpoints"
json.dump(out, open("hot-leg-2026-11-08-0859-age-de3e.json","w"), indent=1)
print(json.dumps(out, indent=1))
