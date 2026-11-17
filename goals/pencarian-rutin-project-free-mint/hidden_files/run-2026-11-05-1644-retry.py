import json, urllib.request
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc.publicnode.com"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=6) as r: out=json.load(r)
            if "error" in out: continue
            v=out["result"]
            if not v or v=="0x": return None
            try: return int(v,16)
            except Exception: return v
        except Exception: continue
    return "RPC-FAIL"
def call(to,sig,args=""): return raw(to,sel(sig)+args)
def block():
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=6) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return "RPC-FAIL"
out={"block":block()}
out["SENBAZURU"]={"freeClaimed":call("0xb21583A08581278BcF925351a99C61A4562C62f0","freeClaimed()"),"paidSold":call("0xb21583A08581278BcF925351a99C61A4562C62f0","paidSold()"),"hasFreeShare_user":call("0xb21583A08581278BcF925351a99C61A4562C62f0","hasFreeShare(address)",enc(USER))}
out["ASOC"]={"freeUsed":call("0x43cEef9313CB8c4ca3757bA841C44DF40A223205","freeUsed()"),"paidSold":call("0x43cEef9313CB8c4ca3757bA841C44DF40A223205","paidSold()")}
out["AFROG"]={"freeClaimed":call("0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31","freeClaimed()"),"FREE_SUPPLY":call("0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31","FREE_SUPPLY()"),"totalSupply":call("0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31","totalSupply()")}
out["StarAgent"]={"totalSupply":call("0x7d390e37Ed41A359f276D8764ca15432704B99b7","totalSupply()")}
out["Driftnauts"]={"totalSupply":call("0x6a926234D3767F2EEb3DB12c1B4C9e2912C5589b","totalSupply()"),"freeMinted":call("0x6a926234D3767F2EEb3DB12c1B4C9e2912C5589b","freeMinted()")}
out["AgentMiner_quote"]={"quote_user_1":call("0x8670e99062ead2cE5402754aeDE769602FDf38b8","quote(address,uint256)",enc(USER)+"0000000000000000000000000000000000000000000000000000000000000001")}
out["LuckyBox_quote"]={"quote_user_1":call("0xd08ef372B52C29255fEd7004f59bF41571451894","quote(address,uint256)",enc(USER)+"0000000000000000000000000000000000000000000000000000000000000001")}
print(json.dumps(out,indent=1))
json.dump(out,open("run-2026-11-05-1644-retry.json","w"),indent=1)
