#!/usr/bin/env python3
"""Fresh reads for VISION + UFO age-exclusion decision, run 2026-11-13 0331.
Read-only; one JSON-RPC batch per contract."""
import json, subprocess
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def batch(addr, views):
    calls = []
    for i, (key, sig, *rest) in enumerate(views):
        data = sel(sig) + (rest[0] if rest else "")
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
    for ep in EPS:
        try:
            r = subprocess.run(["curl","-sL","--max-time","25","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(calls)], capture_output=True, text=True, timeout=30)
            res = json.loads(r.stdout)
            if isinstance(res, list) and len(res)==len(calls):
                out = {}
                for it,(key,_,*_) in zip(res, views):
                    out[key] = None if (isinstance(it,dict) and "error" in it) else to_int(it.get("result"))
                return out
        except Exception:
            continue
    return {"_error":"all-endpoints-failed"}
VISION = "0x5f76cab7b054e088563d5098e17bd0dc430e61ae"
v_views = [("totalShares","totalShares()"),("totalFreeShares","totalFreeShares()"),
           ("totalPaidShares","totalPaidShares()"),("MAX_SHARES","MAX_SHARES()"),
           ("totalSupply","totalSupply()"),("freeUsed_user","freeUsed(address)",enc_addr(USER)),
           ("sharesOf_user","sharesOf(address)",enc_addr(USER)),
           ("balanceOf_user","balanceOf(address)",enc_addr(USER))]
UFO = "0xE4059eA596392AcA14100af6CDC9481c330E2728"
u_views = [("FREE_SHARES","FREE_SHARES()"),("totalSupply","totalSupply()"),
           ("freeClaimed","freeClaimed()"),("endTime","endTime()"),("closed","closed()"),
           ("saleEnd","saleEnd()"),("expiresAt","expiresAt()"),("deadline","deadline()")]
out = {"vision": batch(VISION, v_views), "ufo": batch(UFO, u_views)}
try:
    r = subprocess.run(["curl","-sL","--max-time","15","-X","POST",EPS[0],"-H","Content-Type: application/json","-d", json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})], capture_output=True, text=True, timeout=20)
    out["block"] = int(json.loads(r.stdout).get("result"),16)
except Exception as e:
    out["block_error"] = str(e)[:100]
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-13-0331-vision-ufo.json","w"), indent=1)
