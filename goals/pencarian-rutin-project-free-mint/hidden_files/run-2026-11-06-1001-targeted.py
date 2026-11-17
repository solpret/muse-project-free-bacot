import json, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def raw(to,data,timeout=6):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=timeout) as r: out=json.load(r)
            if "error" in out: continue
            v=out["result"]
            if not v or v=="0x": return None
            try: return int(v,16)
            except Exception: return v
        except Exception: continue
    return None
def call(to,sig,args=""): return raw(to,sel(sig)+args)
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_uint(n): return format(n,"064x")
T={
 "Cipher Mind":("0x3226B724d9F81c4E09E6E07b75532e01e6f5c7B7",["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","mintedBy(address)","balanceOf(address)","spotsLeft()","MAX_SUPPLY()","PRICE()","quote(address,uint256)"]),
 "Cyber Lynx Agent":("0x5189EAEB67d2A799CD9094AEc4Af6eb76C6E073b",["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","mintedBy(address)","balanceOf(address)","spotsLeft()","MAX_SUPPLY()","PRICE()","quote(address,uint256)"]),
 "Storm Sprite Agent":("0xB7E18A0C3c593b256eCb1C57DDa9BFbc2141bf38",["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","mintedBy(address)","balanceOf(address)","spotsLeft()","MAX_SUPPLY()","PRICE()","quote(address,uint256)"]),
 "Void Jaguar Agent":("0xd79fa409EDaC394614c721195eECe440f016e188",["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","mintedBy(address)","balanceOf(address)","spotsLeft()","MAX_SUPPLY()","PRICE()","quote(address,uint256)"]),
}
out={}
for name,(addr,views) in T.items():
    d={"address":addr}
    for sig in views:
        key=sig.split("(")[0]
        if "address" in sig and "uint256" in sig: v=call(addr,sig,enc(USER)+enc_uint(1)); key+="_user_1"
        elif "address" in sig: v=call(addr,sig,enc(USER)); key+="_user"
        else: v=call(addr,sig)
        d[key]=v
    out[name]=d; print(name,d,flush=True)
json.dump(out,open(f"{BASE}/run-2026-11-06-1001-reread-targeted.json","w"),indent=1)
print("TARGETED DONE")
