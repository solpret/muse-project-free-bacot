#!/usr/bin/env python3
"""Verify new Sourcify contract 0x36D9...bc8d (feed 1631, S1 shape via ABI).
Read-only batch eth_call; writes run-2026-11-13-1631-verify-new36d9.json."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x36D9A4392E3d9ff05B6929C82D536367E9c1bc8d"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
VIEWS = [("name","name()"),("symbol","symbol()"),("totalSupply","totalSupply()"),
 ("totalMinted","totalMinted()"),("freeMinted","freeMinted()"),("freeRemaining","freeRemaining()"),
 ("paidMinted","paidMinted()"),("FREE_SUPPLY","FREE_SUPPLY()"),("FREE_PER_WALLET","FREE_PER_WALLET()"),
 ("MAX_SUPPLY","MAX_SUPPLY()"),("MAX_PER_WALLET","MAX_PER_WALLET()"),("PRICE","PRICE()"),
 ("cost","cost()"),("saleStart","saleStart()"),("saleEnd","saleEnd()"),("SALE_END","SALE_END()"),
 ("saleOpen","saleOpen()"),("mintOpen","mintOpen()"),("isFreeOpen","isFreeOpen()"),
 ("isPaidOpen","isPaidOpen()"),("saleClosed","saleClosed()"),("FREE_MODE","FREE_MODE()"),
 ("agentIdRegistry","agentIdRegistry()"),("contractURI","contractURI()"),
 ("tokenURI_1","tokenURI(uint256)",enc_u(1)),
 ("freeAvailable_user","freeAvailable(address)",enc_addr(USER)),
 ("freeMintedBy_user","freeMintedBy(address)",enc_addr(USER)),
 ("quote_user_1","quote(address,uint256)",enc_addr(USER)+enc_u(1)),
 ("costOf_user_1","costOf(address,uint256)",enc_addr(USER)+enc_u(1)),
 ("balanceOf_user","balanceOf(address)",enc_addr(USER)),
 ("hasAgentId_user","hasAgentId(address)",enc_addr(USER)),
 ("remainingQuota_user","remainingQuota(address)",enc_addr(USER)),
 ("canMintFor_user","canMintFor(address,uint256,uint8)",enc_addr(USER)+enc_u(1)+enc_u(0)),
 ("owner","owner()")]
def words(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
    except Exception:
        return None
def decode_str(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        if len(b) < 64: return None
        off = int.from_bytes(b[0:32], "big"); ln = int.from_bytes(b[32:64], "big")
        if off + 32 + ln <= len(b) and ln < 10000:
            return b[64:64+ln].decode("utf-8", "replace")
        return b.decode("utf-8", "replace")
    except Exception:
        return None
t0=time.time()
allcalls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":sel(sig)+(rest[0] if rest else "")},"latest"]} for i,(key,sig,*rest) in enumerate(VIEWS)]
out={"address":ADDR,"views":{},"endpoint":None}
CH=8
for ci in range(0,len(allcalls),CH):
    chunk=allcalls[ci:ci+CH]; chunk_views=VIEWS[ci:ci+CH]; done=False
    for ep in EPS:
        try:
            r=post_rpc(ep,chunk)
            if not isinstance(r,list) or len(r)!=len(chunk): continue
            for it,(key,sig,*rest) in zip(r,chunk_views):
                if not isinstance(it,dict) or "error" in it or not it.get("result") or it["result"]=="0x":
                    out["views"][key]=None; continue
                if key in ("name","symbol","contractURI","tokenURI_1"):
                    out["views"][key]=decode_str(it["result"])
                else:
                    w=words(it["result"])
                    out["views"][key]=w[0] if w is not None and len(w)==1 else w
            out["endpoint"]=ep; done=True; break
        except Exception as e:
            out.setdefault("errors",[]).append(str(e)[:80])
    if not done:
        for key,sig,*rest in chunk_views: out["views"].setdefault(key,None)
try:
    r=post_rpc(EPS[0],{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=15)
    out["block"]=int(r.get("result"),16)
except Exception as e:
    out["block_error"]=str(e)[:100]
out["elapsed_s"]=round(time.time()-t0,1)
print(json.dumps(out,indent=1))
json.dump(out,open(BASE+"run-2026-11-13-1631-verify-new36d9.json","w"),indent=1)
