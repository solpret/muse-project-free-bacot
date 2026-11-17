import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def to_int(v):
    try:
        if v is None or v=="0x": return None
        return int(v,16)
    except Exception: return None
def batch(addr, views):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            res=post(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {k:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,k in zip(res,keys)}
        except Exception: continue
    return None
def call_str(addr, sig):
    # string-returning view (name/symbol) - raw hex
    for ep in EPS:
        try:
            res=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":sel(sig)},"latest"]})
            r=res.get("result")
            if r and r!="0x": return r
        except Exception: continue
    return None
def dec_str(h):
    if not h: return None
    try:
        b=bytes.fromhex(h[2:])
        off=int.from_bytes(b[32:64],"big"); ln=int.from_bytes(b[64+off-32:64+off],"big") if False else None
        # standard ABI string: [0:32]=offset, [32:64]=len at offset
        ln=int.from_bytes(b[32:64],"big")
        return b[64:64+ln].decode(errors="ignore")
    except Exception: return h[:80]
VIEWS=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","FREE_PER_WALLET()","MAX_SUPPLY()","mintOpen()","isFreeOpen()","balanceOf(address)","freeMintedBy(address)","freeClaimed(address)","owner()","agentIdRegistry()","agentRegistry()","contractURI()","saleStart()","mintStart()","START_TIME()","freeSharesRemaining()","FREE_SHARES()","opened()","freeMinted(address)"]
targets={
 "Dropnix":"0xb95531eb859c556b7c9521a99b7b67ba12519564",
 "STALL":"0xe3de7fd0d12cff4a46d8bf702ab593b6f921b308",
 "Rayglide":"0xc4035e850f64d61adce8ecd774f1200d655e5f00",
 "11-11-sale":"0x64767b1a39441e72046c2162065a2896e154b341",
 "11-11-token":"0x398Fa8a4d9e6FE658E3ECD2F4B5CDC8F3562C522",
 "HashKitty":"0xa0abff126a2c219b6d097a1e2ec4cd54ca17feea",
}
out={}
for name,addr in targets.items():
    t=time.time()
    got=batch(addr,VIEWS)
    nm=dec_str(call_str(addr,"name()")); sy=dec_str(call_str(addr,"symbol()"))
    code=None
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]})
            code=r.get("result"); break
        except Exception: continue
    reg = code and ("60b9262456de011f7d15a54cdd8c48baaa8b022f" in code.lower())
    out[name]={"address":addr,"name":nm,"symbol":sy,"views":got,"registry_bytes_in_code":bool(reg),"code_len":len(code)-2 if code else None,"secs":round(time.time()-t,1)}
    print(name, nm, sy, "regBytes:", bool(reg), "codeLen:", len(code)-2 if code else None, json.dumps(got), flush=True)
json.dump(out, open("run-2026-11-10-1901-triage-new.json","w"), indent=1)
print("DONE")
