import json, subprocess
from Crypto.Hash import keccak
ADDR="0xCFB72b0E311796C478c6b74C1cd4592BbAa17aab"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def post(payload):
    r=subprocess.run(["curl","-sL","--max-time","12","-X","POST","https://bsc-dataseed1.bnbchain.org/","-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=20)
    return json.loads(r.stdout)
calls=[]; keys=[]
def add(key,sig,args=""):
    calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call","params":[{"to":ADDR,"data":sel(sig)+args},"latest"]}); keys.append(key)
add("freeMinted","freeMinted()"); add("FREE_SUPPLY","FREE_SUPPLY()"); add("totalMinted","totalMinted()")
add("totalSupply","totalSupply()"); add("mintOpen","mintOpen()"); add("soldOut","soldOut()")
add("mintEnd","mintEnd()"); add("mintStart","mintStart()"); add("PRICE","PRICE()")
add("FREE_PER_WALLET","FREE_PER_WALLET()"); add("MAX_PER_WALLET","MAX_PER_WALLET()")
add("MAX_SUPPLY","MAX_SUPPLY()"); add("paidMinted","paidMinted()")
add("freeAvailable_user","freeAvailable(address)",enc(USER)); add("freeUsed_user","freeUsed(address)",enc(USER))
add("mintedBy_user","mintedBy(address)",enc(USER)); add("balanceOf_user","balanceOf(address)",enc(USER))
add("owner","owner()"); add("TOKEN","TOKEN()"); add("PAYEE","PAYEE()")
add("quote_user1","quote(address,uint256)",enc(USER)+format(1,"064x"))
add("block","eth_blockNumber")
calls[-1]={"jsonrpc":"2.0","id":len(calls),"method":"eth_blockNumber","params":[]}
res=post(calls)
out={}
for item,key in zip(res,keys):
    if key=="block":
        out[key]=int(item["result"],16) if item.get("result") else None; continue
    if "error" in item: out[key]={"error":item["error"]}; continue
    raw=item.get("result","0x")
    if key=="quote_user1":
        hx=raw[2:]
        words=[int(hx[i:i+64],16) for i in range(0,min(len(hx),160),64)]
        s=None
        if len(hx)>=320:
            off=int(hx[256:320],16)
            ln=int(hx[off*2:off*2+64],16)
            s=bytes.fromhex(hx[off*2+64:off*2+64+ln*2]).decode(errors="replace")
        out[key]={"words":words,"msg":s,"raw":raw}
    else:
        out[key]=int(raw,16) if raw and raw!="0x" else None
print(json.dumps(out,indent=1))
json.dump(out,open("hot-leg-2026-11-09-0924-cfb7-probe.json","w"),indent=1)
