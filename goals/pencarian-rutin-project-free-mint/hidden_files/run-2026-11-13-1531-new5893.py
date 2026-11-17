#!/usr/bin/env python3
"""Verify new Sourcify S1-positive contract 0x5893199322A5300775912ebD236d8f1fEFC700Db
(feed verifiedAt 2026-11-13T08:31:09Z). Read-only: ABI fn list + batch eth_call
views + tokenURI/contractURI decode. Writes run-2026-11-13-1531-new5893.json."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0x5893199322A5300775912ebD236d8f1fEFC700Db"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENT_ID = 107187496765866644729837695198686237165740365523485558112864918211974996443404
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def curl(url, timeout=25):
    try:
        return subprocess.run(["curl","-sL","--max-time",str(timeout),url],
            capture_output=True, text=True, timeout=timeout+5).stdout
    except Exception:
        return ""
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout+5).stdout
    return json.loads(out)
def words(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        return [int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
    except Exception:
        return None
def decode_str(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        if len(b) < 64: return None
        off = int.from_bytes(b[0:32],"big"); ln = int.from_bytes(b[off:off+32],"big")
        return b[off+32:off+32+ln].decode("utf-8", "replace")
    except Exception:
        return None
VIEWS = [
 ("name","name()"),("symbol","symbol()"),("decimals","decimals()"),
 ("totalSupply","totalSupply()"),("totalMinted","totalMinted()"),
 ("freeMinted","freeMinted()"),("freeRemaining","freeRemaining()"),
 ("FREE_SUPPLY","FREE_SUPPLY()"),("FREE_PER_WALLET","FREE_PER_WALLET()"),
 ("FREE_CAP","FREE_CAP()"),("MAX_SUPPLY","MAX_SUPPLY()"),
 ("saleStart","saleStart()"),("saleEnd","saleEnd()"),("mintStart","mintStart()"),
 ("mintOpensAt","mintOpensAt()"),("saleOpen","saleOpen()"),("mintOpen","mintOpen()"),
 ("isFreeOpen","isFreeOpen()"),("freeMode","FREE_MODE()"),
 ("agentIdRegistry","agentIdRegistry()"),("registry","registry()"),
 ("agentRegistry","agentRegistry()"),("owner","owner()"),
 ("freeAvailable_user","freeAvailable(address)",enc_addr(USER)),
 ("freeClaimed_user","freeClaimed(address)",enc_addr(USER)),
 ("freeMintedBy_user","freeMintedBy(address)",enc_addr(USER)),
 ("quote_user_1","quote(address,uint256)",enc_addr(USER)+enc_u(1)),
 ("costOf_user_1","costOf(address,uint256)",enc_addr(USER)+enc_u(1)),
 ("balanceOf_user","balanceOf(address)",enc_addr(USER)),
 ("holdsAgentId_user","holdsAgentId(address)",enc_addr(USER)),
 ("price","price()"),("PRICE","PRICE()"),("mintPrice","mintPrice()"),
 ("tokenURI_0","tokenURI(uint256)",enc_u(0)),
 ("tokenURI_1","tokenURI(uint256)",enc_u(1)),
 ("contractURI","contractURI()"),
 ("uri_0","uri(uint256)",enc_u(0)),
 ("supports721","supportsInterface(bytes4)","80ac58cd"),
 ("supports1155","supportsInterface(bytes4)","d9b67a26"),
]
def main():
    t0=time.time()
    out={"address":ADDR,"started_wib":"2026-11-13T15:31+07:00"}
    try:
        meta=curl(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi",20)
        mj=json.loads(meta)
        abi=mj.get("abi") or (mj.get("stdJson",{}).get("output",{}).get("abi")) or []
        fns=[f.get("name") for f in abi if f.get("type")=="function"]
        out["sourcify_fns"]=sorted(set(fns))
        out["sourcify_n_fns"]=len(fns)
        out["sourcify_name"]=mj.get("name") or (mj.get("stdJson",{}).get("name"))
        src=json.dumps(mj).lower()
        out["registry_bytes_in_source"]="0x60b9262456de011f7d15a54cdd8c48baaa8b022f" in src
    except Exception as e:
        out["sourcify_error"]=str(e)[:200]
    calls=[]
    for i,(key,sig,*rest) in enumerate(VIEWS):
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call",
                      "params":[{"to":ADDR,"data":sel(sig)+(rest[0] if rest else "")},"latest"]})
    res={}
    try:
        r=post_rpc(EPS[0],{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=15)
        out["block"]=int(r.get("result"),16)
    except Exception as e:
        out["block_error"]=str(e)[:100]
    done=False
    for ep in EPS:
        try:
            r=post_rpc(ep,calls)
            if not isinstance(r,list) or len(r)!=len(calls): continue
            for it,(key,sig,*rest) in zip(r,VIEWS):
                if not isinstance(it,dict) or "error" in it or not it.get("result") or it["result"]=="0x":
                    res[key]=None; continue
                raw=it["result"]
                if key in ("name","symbol","tokenURI_0","tokenURI_1","contractURI","uri_0"):
                    res[key]=decode_str(raw)
                else:
                    w=words(raw)
                    res[key]=w[0] if w is not None and len(w)==1 else w
            out["endpoint"]=ep; done=True; break
        except Exception as e:
            out.setdefault("errors",[]).append(str(e)[:80])
    out["views"]=res; out["elapsed_s"]=round(time.time()-t0,1)
    print(json.dumps(out,indent=1))
    json.dump(out,open(BASE+"run-2026-11-13-1531-new5893.json","w"),indent=1)
if __name__=="__main__":
    main()
