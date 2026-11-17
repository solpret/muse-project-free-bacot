import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a.lower().replace("0x","").rjust(64,"0")
def enc_uint(n): return format(n,"064x")
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.defibit.io/","https://bsc.nodereal.io/"]
def call(to,data):
    for ep in EPS:
        try:
            r=subprocess.run(["curl","-s","-m","15","-H","Content-Type: application/json","-d",
                json.dumps({"jsonrpc":"2.0","id":0,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}),ep],
                capture_output=True,timeout=20)
            j=json.loads(r.stdout.decode(errors="replace"))
            if j.get("result") not in (None,"0x"): return j["result"]
        except Exception: continue
    return None
def u(res):
    if res is None: return None
    try: return int(res[2:66],16)
    except Exception: return None
def s(res):
    # decode string return (offset,len,data)
    if res is None or len(res)<130: return None
    try:
        ln=int(res[66:130],16)
        return bytes.fromhex(res[130:130+ln*2]).decode(errors="replace")
    except Exception: return None
def b(res):
    if res is None: return None
    try: return int(res[2:66],16)!=0
    except Exception: return None
U=enc(USER)
out={}
# WFPASS quote + slot
W="0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C"
out["WFPASS"]={
 "cost_user_1": u(call(W, sel("cost(address,uint256)")+U+enc_uint(1))),
 "freeClaimed_user": u(call(W, sel("freeClaimed(address)")+U)),
 "freeAvailable_user": u(call(W, sel("freeAvailable(address)")+U)),
 "mintedBy_user": u(call(W, sel("mintedBy(address)")+U)),
 "freeMinted": u(call(W, sel("freeMinted()"))),
 "FREE_SUPPLY": u(call(W, sel("FREE_SUPPLY()"))),
 "mintOpen": b(call(W, sel("mintOpen()"))),
 "price": u(call(W, sel("price()"))),
 "name": s(call(W, sel("name()"))),
 "contractURI": s(call(W, sel("contractURI()"))),
}
# New S1 contracts (0x5777 ABI known; 0xad0D assumed same shape - verify via same calls)
for tag,A in [("ad0D","0xad0D8ac3D61fC8ab397B7136C69fcBf1281a4998"),("5777","0x5777c2f59c65003DDebb018517B09f7ba0691202")]:
    out[tag]={
     "name": s(call(A, sel("name()"))),
     "symbol": s(call(A, sel("symbol()"))),
     "freeClaimed": u(call(A, sel("freeClaimed()"))),
     "FREE_SUPPLY": u(call(A, sel("FREE_SUPPLY()"))),
     "MAX_SUPPLY": u(call(A, sel("MAX_SUPPLY()"))),
     "totalSupply": u(call(A, sel("totalSupply()"))),
     "mintOpen": b(call(A, sel("mintOpen()"))),
     "price": u(call(A, sel("price()"))),
     "cost_user_1": u(call(A, sel("cost(address,uint256)")+U+enc_uint(1))),
     "mintedBy_user": u(call(A, sel("mintedBy(address)")+U)),
     "AGENT_ID": u(call(A, sel("AGENT_ID()"))),
     "owner": None,
     "contractURI": s(call(A, sel("contractURI()"))),
    }
    r=call(A, sel("owner()"))
    out[tag]["owner"]="0x"+r[26:66] if r and len(r)>=66 else None
    time.sleep(0.2)
json.dump(out, open("hot-leg-2026-11-12-0554-verify-new.json","w"), indent=1)
print(json.dumps(out,indent=1))
