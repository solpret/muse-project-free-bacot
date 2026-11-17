#!/usr/bin/env python3
"""KOMA round 2: exact ABI signatures + free pool / timing / user-slot views."""
import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR="0xef4882e029b8d58F81960c433D852a5b0A352965"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
def curl(url,timeout=25):
    try: return subprocess.run(["curl","-sL","--max-time",str(timeout),url],capture_output=True,text=True,timeout=timeout+5).stdout
    except Exception: return ""
def rpc(ep,payload,timeout=20):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return hex(n)[2:].rjust(64,"0")
def words(h):
    try:
        b=bytes.fromhex(h[2:]); return [int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
    except Exception: return None
mj=json.loads(curl(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi",25))
abi=mj.get("abi") or []
sigs={}
for f in abi:
    if f.get("type")=="function":
        ins=",".join(i.get("type","") for i in f.get("inputs",[]))
        sigs[f["name"]]=f["name"]+"("+ins+")"
for want in ("quoteFor","mint","freeClaimedByWallet","identityKeyOf","hasMinted","freePublicMinted","freeWhitelistMinted","MINT_START","OPEN_AT","saleDeadline","opened","TOTAL_SHARES","FREE_PUBLIC_SHARES","FREE_WHITELIST_SHARES","TOKENS_PER_SHARE","PAID_PRICE","paidMinted","totalMinted","idCollection","referralFreeOf"):
    print(want, "->", sigs.get(want))
out={"sigs":{k:sigs.get(k) for k in ("quoteFor","mint","freeClaimedByWallet","identityKeyOf","hasMinted")}}
VIEWS=[("MINT_START","MINT_START()"),("OPEN_AT","OPEN_AT()"),("saleDeadline","saleDeadline()"),
 ("opened","opened()"),("OPEN_COUNTED","OPEN_COUNTED()"),
 ("TOTAL_SHARES","TOTAL_SHARES()"),("FREE_PUBLIC_SHARES","FREE_PUBLIC_SHARES()"),
 ("FREE_WHITELIST_SHARES","FREE_WHITELIST_SHARES()"),("TOKENS_PER_SHARE","TOKENS_PER_SHARE()"),
 ("PAID_PRICE","PAID_PRICE()"),("PAID_SHARES","PAID_SHARES()"),
 ("freePublicMinted","freePublicMinted()"),("freeWhitelistMinted","freeWhitelistMinted()"),
 ("paidMinted","paidMinted()"),("totalMinted","totalMinted()"),
 ("freeClaimedByWallet_user","freeClaimedByWallet(address)",enc_addr(USER)),
 ("hasMinted_user","hasMinted(address)",enc_addr(USER)),
 ("identityKeyOf_user","identityKeyOf(address)",enc_addr(USER)),
 ("idCollection","idCollection()"),("pair","pair()"),
 ("quoteFor_user_1","quoteFor(address,uint256)",enc_addr(USER)+enc_u(1)),
 ("quoteFor_1","quoteFor(uint256)",enc_u(1)),
 ("referralFreeOf_user","referralFreeOf(address)",enc_addr(USER))]
calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":"0x"+sel(sig)+(rest[0] if rest else "")},"latest"]} for i,(k,sig,*rest) in enumerate(VIEWS)]
views={}
for ep in EPS:
    try:
        r=rpc(ep,calls)
        if isinstance(r,list) and len(r)==len(calls):
            for it,(k,sig,*rest) in zip(r,VIEWS):
                if isinstance(it,dict) and it.get("result") and it["result"]!="0x":
                    w=words(it["result"]); views[k]=w[0] if w and len(w)==1 else w
                else: views[k]=None
            break
    except Exception: continue
out["views"]=views
print(json.dumps(views,indent=1))
json.dump(out,open(BASE+"run-2026-11-13-1301-koma2.json","w"),indent=1)
