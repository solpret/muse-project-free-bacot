#!/usr/bin/env python3
"""Hot-leg 0109: leg3 SUOHA fresh verify + age probe; Agent Grove / MORPHA / DEWATA / KAGENT checks."""
import json, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_uint(n): return format(n,"064x")
def raw(to,data,block="latest"):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},block]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=6) as r: out=json.load(r)
            if "error" in out: continue
            v=out["result"]
            if not v or v=="0x": return None
            try: return int(v,16)
            except Exception: return v
        except Exception: continue
    return None
def call(to,sig,args="",block="latest"): return raw(to,sel(sig)+args,block)
def blocknum():
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=6) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None
blk=blocknum()
out={"block":blk}
SUOHA="0x58055F6535b6bF7B33123521A905C61afbd99406"
s={}
for fn in ["cardsSold()","freeCardsRemaining()","FREE_CAP()","TOTAL_SHARES()","paused()","currentPrice()","TOKENS_PER_SHARE()","freeGiven()","totalShares()"]:
    s[fn]=call(SUOHA,fn)
s["quote_user_1"]=call(SUOHA,"quote(address,uint256)",enc(USER)+enc_uint(1))
s["quote_user_2"]=call(SUOHA,"quote(address,uint256)",enc(USER)+enc_uint(2))
s["freeClaimed_user"]=call(SUOHA,"freeClaimed(address)",enc(USER))
s["quotaLeft_user"]=call(SUOHA,"quotaLeft(address)",enc(USER))
s["token"]=raw(SUOHA,sel("token()"))
out["SUOHA"]=s
# age probe: cardsSold at 48h boundary block ~131805100 (2026-11-04 ~01:09 WIB)
for b in [131805100, 131830000, 131850000, 131858000]:
    out[f"SUOHA_cardsSold_block_{b}"]=call(SUOHA,"cardsSold()",block=hex(b))
GROVE="0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c"
g={}
for fn in ["freeMinted()","freeOpen()","totalSupply()","FREE_SUPPLY()","MAX_SUPPLY()","freeClaimed(address)"]:
    g[fn]=call(GROVE,fn,enc(USER) if "address" in fn else "")
out["AgentGrove"]=g
MORPHA="0xb40e4d3b33c5d70ab31a1dde3c240727691cb738"
out["MORPHA_totalSupply"]=call(MORPHA,"totalSupply()")
out["MORPHA_mintOpen"]=call(MORPHA,"mintOpen()")
DEWATA="0x13628D733A26b942213BA1b3C61471925D4a2165"
out["DEWATA_totalMinted"]=call(DEWATA,"totalMinted()")
out["DEWATA_totalSupply"]=call(DEWATA,"totalSupply()")
KAG="0xb34105002B19EF0ce43B59011fE848df5c8B174f"
out["KAGENT_freeClaimed"]=call(KAG,"freeClaimed()")
out["KAGENT_balanceOf_user"]=call(KAG,"balanceOf(address)",enc(USER))
json.dump(out,open(f"{BASE}/hot-leg-2026-11-06-0109-verify.json","w"),indent=1)
print(json.dumps(out,indent=1))
