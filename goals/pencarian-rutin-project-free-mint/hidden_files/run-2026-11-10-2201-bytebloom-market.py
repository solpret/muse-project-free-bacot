import json, subprocess
from Crypto.Hash import keccak
MKT="0x8c1c800fc3079e9dea13a9c5f4c20d0e5e2f2675"
BB="0x74bbDAD7c027C56bE30A7fEaC6F7371B95f1c32B"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(addr,sig,args=""):
    data=sel(sig)+args
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]},timeout=25)
            res=r.get("result")
            if res not in (None,"0x"): return res
        except Exception: continue
    return None
def words(h):
    if h is None: return None
    b=bytes.fromhex(h[2:])
    return [int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
def wi(h):
    w=words(h); return w[0] if w and len(w)==1 else w
print("NFT():", (lambda w: "0x"+w[-1].to_bytes(32,'big')[-20:].hex() if w else None)(words(call(MKT,"NFT()"))))
print("FEE_BPS:", wi(call(MKT,"FEE_BPS()")))
print("listedCount:", wi(call(MKT,"listedCount()")))
print("sales:", wi(call(MKT,"sales()")))
print("volume(wei):", wi(call(MKT,"volume()")))
lc = wi(call(MKT,"listedCount()"))
if lc:
    page = words(call(MKT,"listingsPage(uint256,uint256)",format(0,"064x")+format(min(lc,20),"064x")))
    print("listingsPage(0,%d):"%min(lc,20), page)
    # listingsPage returns array of tokenIds presumably; check first few listings
    if page:
        for tid in page[:5]:
            lst = words(call(MKT,"listings(uint256)",format(tid,"064x")))
            print(f"listings({tid}):", lst, "price BNB:", (lst[1]/1e18 if lst and len(lst)>1 else None))
print("listings(508):", words(call(MKT,"listings(uint256)",format(508,"064x"))))
print("isValid(508):", wi(call(MKT,"isValid(uint256)",format(508,"064x"))))
