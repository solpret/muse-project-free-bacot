#!/usr/bin/env python3
"""Targeted slot + gate reads run 2031. Read-only."""
import json, urllib.request, base64
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc-dataseed.binance.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TC="0xc5624B61beE1971E6Aa3AB5f403236Ab32C2B6cd"   # TIME CARDS
AG="0x7BcC29c5405286b4Dd8b5b23FE7097F9EE65e4e5"   # Agentic
BH="0x2CCb3fA957E69AbD46A6651CC1444EF2Ea9bd591"   # BAHUANG3
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def rpc(method,params,timeout=20):
    for u in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
            req=urllib.request.Request(u,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=timeout) as r: out=json.load(r)
            if "error" in out: continue
            return out["result"]
        except Exception: continue
    return None
def call(addr,sig,args="",raw=False):
    v=rpc("eth_call",[{"to":addr,"data":sel(sig)+args},"latest"])
    if v is None or v=="0x": return None
    if raw: return v
    try: return int(v,16)
    except Exception: return v
blk=rpc("eth_blockNumber",[])
out={"block":int(blk,16) if blk else None}
out["TIME_CARDS"]={"claimedFree_user":call(TC,"claimedFree(address)",enc(USER)),
  "balanceOf_user":call(TC,"balanceOf(address)",enc(USER)),
  "freeMinted":call(TC,"freeMinted()"),"FREE_SUPPLY":call(TC,"FREE_SUPPLY()"),
  "totalSupply":call(TC,"totalSupply()"),"freeStart":call(TC,"freeStart()"),
  "contractURI_raw":call(TC,"contractURI()",raw=True),
  "tokenURI1_raw":call(TC,"tokenURI(uint256)","0"*63+"1",raw=True)}
out["Agentic"]={"hasFreeMinted_user":call(AG,"hasFreeMinted(address)",enc(USER)),
  "freeClaimed_user":call(AG,"freeClaimed(address)",enc(USER)),
  "balanceOf_user":call(AG,"balanceOf(address)",enc(USER)),
  "freeMinted":call(AG,"freeMinted()"),"freeClaimed":call(AG,"freeClaimed()"),
  "FREE_SUPPLY":call(AG,"FREE_SUPPLY()"),"totalMinted":call(AG,"totalMinted()"),
  "contractURI_raw":call(AG,"contractURI()",raw=True)}
out["BAHUANG3"]={"freeAllowance_user":call(BH,"freeAllowance(address)",enc(USER)),
  "balanceOf_user":call(BH,"balanceOf(address)",enc(USER)),
  "freeMinted":call(BH,"freeMinted()"),"FREE_CAP":call(BH,"FREE_CAP()"),
  "totalMinted":call(BH,"totalMinted()"),"mintStart":call(BH,"mintStart()")}
print(json.dumps(out,indent=1)[:4000])
json.dump(out,open("run-2026-11-09-2031-targeted.json","w"),indent=1)
# Sourcify metadata for TIME CARDS (method C)
try:
    req=urllib.request.Request("https://sourcify.dev/server/v2/contract/56/"+TC+"?fields=stdJson",headers={"User-Agent":"curl/8"})
    with urllib.request.urlopen(req,timeout=25) as r: meta=json.load(r)
    s=json.dumps(meta)
    print("TIME_CARDS sourcify stdJson has URL-ish:", [w for w in re.findall(r'https?://[a-zA-Z0-9./_-]+',s)][:10] if (re:=__import__('re')) else [])
    json.dump(meta,open("run-2026-11-09-2031-timecards-sourcify.json","w"))
except Exception as e:
    print("TIME_CARDS sourcify fetch fail:",repr(e))
