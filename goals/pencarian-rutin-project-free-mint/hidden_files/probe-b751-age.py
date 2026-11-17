import json, subprocess, sys
from Crypto.Hash import keccak
ADDR="0xB7517e3B31107695F2f8837fAFC76999b956C871"
EP="https://bsc-dataseed.binance.org/"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def batch(calls, ep=EP):
    out=subprocess.run(["curl","-sL","--max-time","30","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(calls)],capture_output=True,text=True,timeout=40).stdout
    return json.loads(out)
blocks=[133485229,133456429,133427629,133398829,133415629,133410000,133420000]
data=sel("totalSupply()")
calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":data},hex(b)]} for i,b in enumerate(blocks)]
r=batch(calls)
for b,it in zip(blocks,r):
    v=it.get("result")
    print(b, "->", int(v,16) if v and v!="0x" else v, it.get("error",""))
# tokenURI(1) for metadata/external_url (method I)
def enc_u(n): return format(n,"064x")
calls=[{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":sel("tokenURI(uint256)")+enc_u(1)},"latest"]},
       {"jsonrpc":"2.0","id":2,"method":"eth_call","params":[{"to":ADDR,"data":sel("tokenURI(uint256)")+enc_u(9901)},"latest"]}]
r=batch(calls)
for it in r:
    v=it.get("result")
    print("tokenURI ->", v[:200] if v else it)
