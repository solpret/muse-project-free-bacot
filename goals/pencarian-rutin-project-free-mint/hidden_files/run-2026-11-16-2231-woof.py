import json, subprocess
from Crypto.Hash import keccak
ADDR="0xBb9bA68C8E99651450F099C431eb530a71C712bE"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP="https://bsc-dataseed.binance.org/"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def rpc(method, params, timeout=60):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params})
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",EP,"-H","Content-Type: application/json","-d",p],capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(out)
def call(sig, args=[]):
    d=sel(sig)
    for a in args:
        if isinstance(a,str) and a.startswith("0x") and len(a)==42: d+=enc_addr(a)
        else: d+=format(int(a),"064x")
    r=rpc("eth_call",[{"to":ADDR,"data":d},"latest"])
    return r.get("result")
def dec_int(h):
    try: return int(h,16) if h and h!="0x" else None
    except Exception: return None
def dec_str(h):
    try:
        if not h or h=="0x": return None
        b=bytes.fromhex(h[2:])
        off=int.from_bytes(b[32:64],"big"); ln=int.from_bytes(b[64+off-32:64+off],"big") if False else int.from_bytes(b[off+32:off+64],"big")
        return b[off+64:off+64+ln].decode()
    except Exception as e: return f"<str-err {e}>"
views={}
for name,sig,args,typ in [
 ("name","name()",[],"str"),("symbol","symbol()",[],"str"),
 ("totalSupply","totalSupply()",[],"int"),("totalMinted","totalMinted()",[],"int"),
 ("freeMinted","freeMinted()",[],"int"),("MAX_SUPPLY","MAX_SUPPLY()",[],"int"),
 ("FREE_SUPPLY","FREE_SUPPLY()",[],"int"),("mintOpen","mintOpen()",[],"int"),
 ("mintPrice","mintPrice()",[],"int"),("freeMintedBy_user","freeMintedBy(address)",[USER],"int"),
 ("mintedBy_user","mintedBy(address)",[USER],"int"),
 ("balanceOf_user","balanceOf(address)",[USER],"int"),
 ("owner","owner()",[],"addr"),("agentId","agentId()",[],"addr"),
 ("agentRegistry","agentRegistry()",[],"addr"),
 ("priceFor_user_1","priceFor(address,uint256)",[USER,1],"int"),
 ("freeRemainingFor_user","freeRemainingFor(address)",[USER],"int"),
]:
    try:
        r=call(sig,args)
        if typ=="str": v=dec_str(r)
        elif typ=="addr": v=("0x"+r[-40:]) if r and len(r)>=42 else r
        else: v=dec_int(r)
        views[name]=v
    except Exception as e:
        views[name]=f"ERR {e}"
    print(name, "=", views[name], flush=True)
code=rpc("eth_getCode",[ADDR,"latest"]).get("result","")
print("code_len:", (len(code)-2)//2 if code else 0, "registry_bytes:", "60b9262456de011f7d15a54cdd8c48baaa8b022f" in (code or "").lower(), flush=True)
head=int(rpc("eth_blockNumber",[]).get("result","0x0"),16)
print("head:", head, flush=True)
json.dump({"address":ADDR,"views":views,"code_len":(len(code)-2)//2 if code else 0,"registry_bytes":"60b9262456de011f7d15a54cdd8c48baaa8b022f" in (code or "").lower(),"head":head}, open("run-2026-11-16-2231-woof.json","w"), indent=1)
