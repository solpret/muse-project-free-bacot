import json, subprocess
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR="0xd31b168F7b6f3dB39BEd89433124595aaa91cfF3"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def post(ep,payload):
    o=subprocess.run(["curl","-sL","--max-time","25","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=30).stdout
    return json.loads(o)
def call(data):
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]})
            if "result" in r: return r["result"]
        except Exception: continue
    return None
def u(sig):
    d=sel(sig); r=call(d)
    if r is None: return None
    try: return int(r,16)
    except Exception: return r
def uaddr(sig):
    d=sel(sig)+enc(USER); r=call(d)
    if r is None: return None
    try: return int(r,16)
    except Exception: return r
def s(sig):
    r=call(sel(sig))
    if r is None: return None
    try:
        b=bytes.fromhex(r[2:])
        # dynamic string: offset(32)+len(32)+data
        ln=int.from_bytes(b[32:64],"big"); return b[64:64+ln].decode(errors="replace")
    except Exception: return r
def tok_uri(tid):
    d=sel("tokenURI(uint256)")+str(tid).rjust(64,"0")
    r=call(d)
    if r is None: return None
    try:
        b=bytes.fromhex(r[2:]); ln=int.from_bytes(b[32:64],"big"); return b[64:64+ln].decode(errors="replace")
    except Exception: return r
out={}
for f in ["name()","symbol()","totalMinted()","freeMinted()","FREE_WALLETS()","freeWalletsLeft()","freeWalletCount()","MAX_SUPPLY()","mintOpen()","mintOpensAt()","price()","nextTokenId()","agentIdRegistry()"]:
    out[f]= s(f) if f in ("name()","symbol()") else u(f)
out["balanceOf(user)"]=uaddr("balanceOf(address)")
out["freeCountBy(user)"]=uaddr("freeCountBy(address)")
out["mintsBy(user)"]=uaddr("mintsBy(address)")
out["holdsAgentId(user)"]=uaddr("holdsAgentId(address)")
out["tokenURI(1)"]=tok_uri(1)
blk=None
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}); blk=int(r["result"],16); break
    except Exception: continue
out["block"]=blk
print(json.dumps(out,indent=1))
