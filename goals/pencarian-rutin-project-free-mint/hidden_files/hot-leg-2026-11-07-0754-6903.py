import json, urllib.request, time
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed.binance.org","https://bsc-dataseed1.defibit.io"]
C="0x69037Db8C6f237eCd9aB4B364D65C6dD05825dCb"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def rpc(method,params,timeout=5):
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    for rpc in RPCS:
        for _ in range(2):
            try:
                req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
                with urllib.request.urlopen(req,timeout=timeout) as r: o=json.load(r)
                if "error" in o: return None
                return o.get("result")
            except Exception: time.sleep(0.2)
    return None
def call(data):
    v=rpc("eth_call",[{"to":C,"data":data},"latest"])
    return v
def dec_str(v):
    if not v or v=="0x": return None
    b=bytes.fromhex(v[2:])
    if len(b)<64: return None
    ln=int.from_bytes(b[32:64],"big")
    return b[64:64+ln].decode("utf-8","replace")
def dec_uint(v):
    if not v or v=="0x": return None
    try: return int(v,16)
    except Exception: return v
def dec_addr(v):
    if not v or len(v)<42: return v
    return "0x"+v[-40:]
def dec_bool(v):
    if not v: return None
    return int(v,16)!=0
UP="0x"+"0"*24+USER[2:].lower()
reads=[
 ("name()","str"),("symbol()","str"),("DESCRIPTION()","str"),("WEBSITE()","str"),("X_URL()","str"),
 ("AGENT_ID()","uint"),("MAX_SUPPLY()","uint"),("MAX_PER_WALLET()","uint"),
 ("PRICE_LOW()","uint"),("PRICE_HIGH()","uint"),("TREASURY()","addr"),
 ("mintOpen()","bool"),("totalSupply()","uint"),("owner()","addr"),
 ("contractURI()","str"),("logo()","str"),("artFrozen()","bool"),("artChunks()","uint"),
]
out={}
for sig,typ in reads:
    v=call(sel(sig))
    dec={"str":dec_str,"uint":dec_uint,"addr":dec_addr,"bool":dec_bool}[typ](v)
    out[sig]=dec; print(sig,repr(dec))
for sig,typ in [("costFor(address,uint256)","uint"),("freeMinter(address)","bool"),("mintedBy(address)","uint"),("balanceOf(address)","uint")]:
    data=sel(sig)+UP[2:]
    if "uint256" in sig: data+=format(1,"064x")
    v=call(data)
    dec={"uint":dec_uint,"bool":dec_bool}[typ](v)
    out[sig+"_user"]=dec; print(sig,"(user,1)" if "uint256" in sig else "(user)",repr(dec))
blk=rpc("eth_blockNumber",[])
print("block",int(blk,16) if blk else None)
json.dump(out,open("hot-leg-2026-11-07-0754-6903.json","w"),indent=1)
