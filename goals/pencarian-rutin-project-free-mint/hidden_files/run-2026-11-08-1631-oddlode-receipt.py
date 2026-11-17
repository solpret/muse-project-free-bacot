import json, urllib.request, time
from Crypto.Hash import keccak
TX="0xf515f49ce73580ec7f6cf541b1170e6122380f5de45e58e53e47eaf3b8beeb1a"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR="0xce18531F9F639ca2351CA15FB2032D925b917472"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def post(ep, payload):
    req=urllib.request.Request(ep, data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r: return json.load(r)
receipt=None
for attempt in range(12):
    for ep in EPS:
        try:
            out=post(ep, [{"jsonrpc":"2.0","id":1,"method":"eth_getTransactionReceipt","params":[TX]}])
            if out and out[0].get("result"):
                receipt=out[0]["result"]; break
        except Exception: continue
    if receipt: break
    time.sleep(5)
print("receipt:", json.dumps(receipt, indent=1) if receipt else "NOT MINED after ~60s")
if receipt:
    print("status:", receipt.get("status"), "block:", int(receipt.get("blockNumber"),16), "gasUsed:", int(receipt.get("gasUsed"),16))
    # post-mint reads
    def sel(s):
        k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
    def enc(a): return a[2:].lower().rjust(64,"0")
    def to_int(v):
        try: return int(v,16) if v and v!="0x" else None
        except Exception: return None
    views=["totalSupply()","freeMinted()","freeClaimed(address)","balanceOf(address)","ownerOf(uint256)"]
    # tokenId from Transfer log topic[3]
    token_id=None
    for lg in receipt.get("logs",[]):
        topics=lg.get("topics",[])
        if len(topics)==4 and topics[0].lower()=="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef":
            token_id=int(topics[3],16)
    print("minted tokenId (from Transfer log):", token_id)
    calls=[]; keys=[]
    for i,sig in enumerate(views):
        if sig=="ownerOf(uint256)" and token_id is None:
            continue
        if "(address)" in sig: data=sel(sig)+enc(USER); key=sig.split("(")[0]+"_user"
        elif "(uint256)" in sig: data=sel(sig)+hex(token_id)[2:].rjust(64,"0"); key="ownerOf_token"
        else: data=sel(sig); key=sig.split("(")[0]
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            out=post(ep, calls)
            if isinstance(out,list) and len(out)==len(calls):
                res={}
                for item,key in zip(out,keys):
                    res[key]=to_int(item.get("result")) if isinstance(item,dict) and "result" in item else None
                print("post-mint reads:", json.dumps(res, indent=1))
                if res.get("ownerOf_token") is not None:
                    print("ownerOf(token):", hex(res["ownerOf_token"]))
                json.dump({"tx":TX,"receipt":receipt,"tokenId":token_id,"reads":res}, open("run-2026-11-08-1631-oddlode-receipt.json","w"), indent=1)
                break
        except Exception as e:
            print("read err", e); continue
