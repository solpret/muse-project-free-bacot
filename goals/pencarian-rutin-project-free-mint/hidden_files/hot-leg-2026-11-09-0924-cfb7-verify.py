import json, subprocess, time
from Crypto.Hash import keccak
TX="0x3b195924a58ba72c4a94bbf76be3a4b068fc3863c4b6fa1f35827c6f5bf6ed78"
ADDR="0xCFB72b0E311796C478c6b74C1cd4592BbAa17aab"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
POSTAGE="0x6C310EABEdFD4eEd6148bf2C07241FB45a52FB42"
def post(payload, ep="https://bsc-dataseed1.bnbchain.org/"):
    r=subprocess.run(["curl","-sL","--max-time","12","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=20)
    return json.loads(r.stdout)
rc=None
for i in range(12):
    rc=post({"jsonrpc":"2.0","id":1,"method":"eth_getTransactionReceipt","params":[TX]})
    if rc.get("result"): break
    time.sleep(10)
print("receipt:", json.dumps(rc.get("result"), indent=1) if rc.get("result") else "NOT FOUND after retries")
if rc.get("result"):
    r=rc["result"]
    blk=int(r["blockNumber"],16)
    print("status:",int(r["status"],16),"block:",blk,"gasUsed:",int(r["gasUsed"],16))
    def sel(s):
        k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
    def enc(a): return a[2:].lower().rjust(64,"0")
    calls=[]; keys=[]
    def add(key,sig,to,args=""):
        calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call","params":[{"to":to,"data":sel(sig)+args},"latest"]}); keys.append(key)
    add("freeMinted","freeMinted()",ADDR); add("totalMinted","totalMinted()",ADDR)
    add("balanceOf_user","balanceOf(address)",ADDR,enc(USER)); add("freeUsed_user","freeUsed(address)",ADDR,enc(USER))
    add("mintedBy_user","mintedBy(address)",ADDR,enc(USER))
    add("postage_balance","balanceOf(address)",POSTAGE,enc(USER))
    add("ownedIds","ownedIds(address,uint256,uint256)",ADDR,enc(USER)+format(0,"064x")+format(10,"064x"))
    res=post(calls)
    out={}
    for item,key in zip(res,keys):
        raw=item.get("result","0x")
        if key=="ownedIds":
            hx=raw[2:]; off=int(hx[64:128],16); ln=int(hx[off*2:off*2+64],16)
            out[key]=[int(hx[off*2+64+i*64:off*2+128+i*64],16) for i in range(ln)]
        else:
            out[key]=int(raw,16) if raw and raw!="0x" else None
    print(json.dumps(out,indent=1))
    json.dump({"tx":TX,"receipt":r,"post":out},open("hot-leg-2026-11-09-0924-cfb7-verify.json","w"),indent=1)
