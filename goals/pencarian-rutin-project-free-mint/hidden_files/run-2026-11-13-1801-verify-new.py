#!/usr/bin/env python3
"""Verify NEW leads run 1801: feed S1-positive 0x73f1, feed mint+free+agent 0x6DdE, Boltbook-new 0x97f3.
Chunked 8-call batches (dataseed batch bug lesson). Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def words(h):
    try:
        b = bytes.fromhex(h[2:]); return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
    except Exception: return None
def decode_str(h):
    try:
        b = bytes.fromhex(h[2:])
        if len(b) < 64: return None
        ln = int.from_bytes(b[32:64], "big")
        if 64 + ln <= len(b): return b[64:64+ln].decode("utf-8", "replace")
    except Exception: pass
    return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
VIEWS = [("name","name()"),("symbol","symbol()"),("totalSupply","totalSupply()"),
 ("totalMinted","totalMinted()"),("freeMinted","freeMinted()"),("freeClaimed","freeClaimed()"),
 ("freeRemaining","freeRemaining()"),("FREE_SUPPLY","FREE_SUPPLY()"),("FREE_CAP","FREE_CAP()"),
 ("MAX_SUPPLY","MAX_SUPPLY()"),("PRICE","PRICE()"),("saleStart","saleStart()"),
 ("saleEnd","saleEnd()"),("mintStart","mintStart()"),("mintOpensAt","mintOpensAt()"),
 ("mintOpen","mintOpen()"),("saleOpen","saleOpen()"),("isFreeOpen","isFreeOpen()"),
 ("agentIdRegistry","agentIdRegistry()"),("registry","registry()"),
 ("contractURI","contractURI()"),("tokenURI_1","tokenURI(uint256)",enc_u(1)),
 ("freeAvailable_user","freeAvailable(address)",enc_addr(USER)),
 ("freeMintedBy_user","freeMintedBy(address)",enc_addr(USER)),
 ("freeClaimed_user","freeClaimed(address)",enc_addr(USER)),
 ("quote_user_1","quote(address,uint256)",enc_addr(USER)+enc_u(1)),
 ("costOf_user_1","costOf(address,uint256)",enc_addr(USER)+enc_u(1)),
 ("balanceOf_user","balanceOf(address)",enc_addr(USER)),
 ("hasAgentId_user","hasAgentId(address)",enc_addr(USER)),
 ("owner","owner()")]
STRKEYS = ("name","symbol","contractURI","tokenURI_1")
def read(addr):
    allcalls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":sel(sig)+(rest[0] if rest else "")},"latest"]} for i,(key,sig,*rest) in enumerate(VIEWS)]
    out={"address":addr,"views":{},"errors":[]}
    CH=8
    for ci in range(0, len(allcalls), CH):
        chunk=allcalls[ci:ci+CH]; cv=VIEWS[ci:ci+CH]; done=False
        for ep in EPS:
            try:
                r=post(ep, chunk)
                if not isinstance(r, list) or len(r)!=len(chunk): continue
                for it,(key,sig,*rest) in zip(r, cv):
                    if not isinstance(it,dict) or "error" in it or not it.get("result") or it["result"]=="0x":
                        out["views"][key]=None; continue
                    if key in STRKEYS:
                        out["views"][key]=decode_str(it["result"])
                    else:
                        w=words(it["result"]); out["views"][key]=w[0] if w is not None and len(w)==1 else w
                out["endpoint"]=ep; done=True; break
            except Exception as e:
                out["errors"].append(str(e)[:80])
        if not done: out["errors"].append(f"chunk@{ci} all endpoints failed")
    return out
t0=time.time()
res={}
for name,addr in [("MossSignal","0xb2e5d82900b854d3cb8c6bb917426abadb687f68"),
                  ("AgentBubble","0x0d72970046c056db90888351b739246f468bff0b"),
                  ("Mihao","0xea4ef9da567f59ea7b5f5b7e08305f4e613bab73"),
                  ("CinderCrucible","0x73f1A09e49cA70F8ac6a2F8673Bf7f0f69219b23"),
                  ("Apex","0x6DdE73D48Ed92c9C60B77711d37fEc0B03ACBE18")]:
    res[name]=read(addr)
res["block"]=None
try:
    r=post(EPS[0], {"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}, timeout=15)
    res["block"]=int(r.get("result"),16)
except Exception as e:
    res["block_error"]=str(e)[:100]
res["elapsed_s"]=round(time.time()-t0,1)
json.dump(res, open(BASE+"run-2026-11-13-1801-verify-boltbook.json","w"), indent=1)
print(json.dumps({k:{kk:vv for kk,vv in v["views"].items() if vv is not None} for k,v in res.items() if isinstance(v,dict)}, indent=1)[:4000])
print("block:", res["block"], "elapsed:", res["elapsed_s"])
