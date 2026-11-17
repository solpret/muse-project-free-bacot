#!/usr/bin/env python3
"""Verify-new for free-mint-search run 2026-11-13 01:01 WIB.
New contracts from legs: Agentx 0x64a5 (Boltbook, S1+early), 0x52B3 (feed,
free views+quote, no agent fn on ABI), 0xDBE8 (feed, REGISTRY+mintFree),
MORPHA 0xB40E (Boltbook claim report). Read-only; one batch POST per contract."""
import json, subprocess, time, concurrent.futures
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def dec_str(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        if len(b) < 64: return None
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception: return None
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def call(addr, sig, args=""):
    return sel(sig) + args
TARGETS = {
 "Agentx": ("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492", [
   ("totalMinted","totalMinted()"),("freeMinted","freeMinted()"),("FREE_CAP","FREE_CAP()"),
   ("MAX_SUPPLY","MAX_SUPPLY()"),("mintOpen","mintOpen()"),("mintOpensAt","mintOpensAt()"),
   ("price","price()"),("freeClaimed_user","freeClaimed(address)",enc_addr(USER)),
   ("balanceOf_user","balanceOf(address)",enc_addr(USER)),
   ("holdsAgentId_user","holdsAgentId(address)",enc_addr(USER)),
   ("mintsBy_user","mintsBy(address)",enc_addr(USER)),
   ("owner","owner()"),("name","name()"),("symbol","symbol()"),
   ("tokenURI_1","tokenURI(uint256)",enc_u(1)),("tokenURI_0","tokenURI(uint256)",enc_u(0)),
   ("nextTokenId","nextTokenId()"),
 ]),
 "C52B3": ("0x52B3442FE4AfDe958285fDc9c8d8D5283C9c36e1", [
   ("totalSupply","totalSupply()"),("FREE_SUPPLY","FREE_SUPPLY()"),("FREE_PER_WALLET","FREE_PER_WALLET()"),
   ("MAX_SUPPLY","MAX_SUPPLY()"),("PRICE","PRICE()"),("mintOpen","mintOpen()"),
   ("freeLeft","freeLeft()"),("freeUsed","freeUsed()"),
   ("freeClaimed_user","freeClaimed(address)",enc_addr(USER)),
   ("freeFor_user","freeFor(address)",enc_addr(USER)),
   ("balanceOf_user","balanceOf(address)",enc_addr(USER)),
   ("owner","owner()"),("name","name()"),("symbol","symbol()"),
   ("contractURI","contractURI()"),("externalUrl","externalUrl()"),
   ("tokenURI_1","tokenURI(uint256)",enc_u(1)),
   ("quote_1","quote(uint256)",enc_u(1)),
 ]),
 "DBE8": ("0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412", [
   ("minted","minted()"),("freeSold","freeSold()"),("paidSold","paidSold()"),
   ("FREE_SUPPLY","FREE_SUPPLY()"),("PAID_CAP","PAID_CAP()"),("START","START()"),
   ("FREE_END","FREE_END()"),("FREE_FEE","FREE_FEE()"),("PRICE","PRICE()"),
   ("phase","phase()"),("status","status()"),("freeOpen","freeOpen()"),("paidOpen","paidOpen()"),
   ("freeQuotaOf_user","freeQuotaOf(address)",enc_addr(USER)),
   ("quotaOf_user","quotaOf(address)",enc_addr(USER)),
   ("balanceOf_user","balanceOf(address)",enc_addr(USER)),
   ("owner","owner()"),("name","name()"),("symbol","symbol()"),
   ("tokenURI_1","tokenURI(uint256)",enc_u(1)),
 ]),
 "MORPHA": ("0xB40E4D3B33c5d70Ab31a1ddE3c240727691CB738", [
   ("totalSupply","totalSupply()"),("name","name()"),("symbol","symbol()"),
   ("balanceOf_user","balanceOf(address)",enc_addr(USER)),("owner","owner()"),
 ]),
}
def one(item):
    name,(addr,views)=item
    calls=[]; keys=[]
    for i,(key,sig,*rest) in enumerate(views):
        data = call(addr,sig,rest[0] if rest else "")
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res=post_rpc(ep,calls,timeout=25)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            out={}
            for it,key in zip(res,keys):
                if not isinstance(it,dict) or "error" in it: out[key]=None; continue
                rv=it.get("result")
                if key in ("name","symbol","contractURI","externalUrl") or key.startswith("tokenURI"):
                    out[key]=dec_str(rv) if rv else None
                else:
                    out[key]=to_int(rv)
            out["_addr"]=addr
            return name,out
        except Exception: continue
    return name,{"_addr":addr,"_error":"all-endpoints-failed"}
t0=time.time()
out={"started_wib":"2026-11-13 01:01 WIB","reads":{}}
try:
    res=post_rpc(EPS[0],{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=15)
    out["block"]=int(res.get("result"),16)
except Exception as e:
    out["block_error"]=str(e)[:100]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    for name,r in ex.map(one,TARGETS.items()):
        out["reads"][name]=r; print(name, json.dumps(r), flush=True)
out["elapsed_s"]=round(time.time()-t0,1)
json.dump(out,open(BASE+"run-2026-11-13-0101-verify-new.json","w"),indent=1)
print("ELAPSED",out["elapsed_s"],"BLOCK",out.get("block"))
