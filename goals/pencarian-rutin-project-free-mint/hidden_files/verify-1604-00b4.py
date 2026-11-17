import json, subprocess
from Crypto.Hash import keccak
C="0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP="https://bsc.nodereal.io/"
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x","").rjust(64,"0")
def enc_uint(n): return format(n,"064x")
calls={
 "name()":sel("name()"), "symbol()":sel("symbol()"), "decimals()":sel("decimals()"),
 "registry()":sel("registry()"), "factory()":sel("factory()"),
 "FREE_SHARES()":sel("FREE_SHARES()"), "totalFreeMinted()":sel("totalFreeMinted()"),
 "FREE_TOKENS_PER_SHARE()":sel("FREE_TOKENS_PER_SHARE()"),
 "TOKENS_PER_SHARE()":sel("TOKENS_PER_SHARE()"), "FREE_PER_ID()":sel("FREE_PER_ID()"),
 "mintStart()":sel("mintStart()"), "currentState()":sel("currentState()"),
 "finalized()":sel("finalized()"), "refunding()":sel("refunding()"),
 "totalMinted()":sel("totalMinted()"), "totalSupply()":sel("totalSupply()"),
 "mintDeadline()":sel("mintDeadline()"), "PRICE()":sel("PRICE()"),
 "freeClaimedByWallet_user":sel("freeClaimedByWallet(address)")+enc_addr(USER),
 "quote_1":sel("quote(uint256)")+enc_uint(1),
 "balanceOf_user":sel("balanceOf(address)")+enc_addr(USER),
 "mintedByWallet_user":sel("mintedByWallet(address)")+enc_addr(USER),
}
payload=json.dumps([{"jsonrpc":"2.0","id":i,"method":"eth_call","params":[{"to":C,"data":d},"latest"]} for i,d in enumerate(calls.values())])
p=subprocess.run(["curl","-s","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","--data",payload],capture_output=True,text=True)
resp=json.loads(p.stdout)
keys=list(calls.keys())
out={}
for i,it in enumerate(resp):
    k=keys[i]; r=it.get("result")
    if not r or r=="0x": out[k]=None; continue
    h=r[2:]
    if k in ("name()","symbol()"):
        try:
            off=int(h[0:64],16); ln=int(h[64:128],16)
            out[k]=bytes.fromhex(h[128:128+ln*2]).decode()
        except Exception as e: out[k]=f"decode-err {e} raw={r[:80]}"
    elif k=="quote_1":
        out[k]=[int(h[j:j+64],16) for j in range(0,256,64)]
    elif k in ("registry()","factory()"):
        out[k]="0x"+h[24:64]
    elif k in ("freeClaimedByWallet_user","finalized()","refunding()"):
        out[k]=bool(int(h[0:64],16))
    else:
        out[k]=int(h[0:64],16)
import datetime
ms=out.get("mintStart()")
if isinstance(ms,int) and ms>0:
    out["mintStart_WIB"]=datetime.datetime.fromtimestamp(ms,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
    out["mintStart_age_min"]=round((datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).timestamp()-ms)/60,1)
md=out.get("mintDeadline()")
if isinstance(md,int) and md>0:
    out["mintDeadline_WIB"]=datetime.datetime.fromtimestamp(md,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
print(json.dumps(out,indent=1))
json.dump(out,open("verify-1604-00b4.json","w"),indent=1)
