import json, urllib.request
from Crypto.Hash import keccak
ADDR="0xAeA1433dBD9e7edE0914d996C2Dad692E6e01e09"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def encu(n): return ("%064x"%n)
def call(to,data):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=6) as r: out=json.load(r)
            if "error" in out: continue
            return out.get("result")
        except Exception: continue
    return "RPC-FAIL"
def u(sig,args=""):
    v=call(ADDR,sel(sig)+args)
    if v in (None,"0x","RPC-FAIL"): return v
    try: return int(v,16)
    except Exception: return v
def s(sig,args=""):
    v=call(ADDR,sel(sig)+args)
    if v in (None,"0x","RPC-FAIL"): return v
    try:
        h=v[2:]
        off=int(h[:64],16)*2; ln=int(h[off:off+64],16)
        return bytes.fromhex(h[off+64:off+64+ln*2]).decode(errors="replace")
    except Exception: return v
out={}
out["name"]=s("name()"); out["symbol"]=s("symbol()")
out["totalSupply"]=u("totalSupply()"); out["totalMinted"]=u("totalMinted()")
out["MAX_SUPPLY"]=u("MAX_SUPPLY()"); out["ERA_SIZE"]=u("ERA_SIZE()"); out["era"]=u("era()")
out["price"]=u("price()"); out["MAX_PRICE"]=u("MAX_PRICE()")
out["mintCost_user_1"]=u("mintCost(address,uint256)",enc(USER)+encu(1))
out["freeUsed_user"]=u("freeUsed(address)",enc(USER))
out["mintOpen"]=u("mintOpen()"); out["mintMode"]=u("mintMode()")
out["requireAgentId"]=u("requireAgentId()"); out["hasAgentId_user"]=u("hasAgentId(address)",enc(USER))
out["agentId"]=call(ADDR,sel("agentId()"))
out["publicRemaining"]=u("publicRemaining()"); out["reserve"]=u("reserve()"); out["reserveMinted"]=u("reserveMinted()")
out["cracked"]=u("cracked()"); out["maxPerWallet"]=u("maxPerWallet()")
out["mintedBy_user"]=u("mintedBy(address)",enc(USER)); out["balanceOf_user"]=u("balanceOf(address)",enc(USER))
out["SITE"]=s("SITE()"); out["contractURI"]=s("contractURI()")
st=call(ADDR,sel("stats()"))
out["stats_raw"]=st
wi=call(ADDR,sel("walletInfo(address)")+enc(USER))
out["walletInfo_raw"]=wi
out["owner"]=call(ADDR,sel("owner()"))
print(json.dumps(out,indent=1))
json.dump(out,open("run-2026-11-06-0833-aea1-state.json","w"),indent=1)
