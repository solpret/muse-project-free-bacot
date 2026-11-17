import json, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=8) as r: out=json.load(r)
            if "error" in out: continue
            v=out["result"]
            if not v or v=="0x": return None
            return int(v,16)
        except Exception: continue
    return None
def block():
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=8) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None
LEADS={
 "Silent Hydra Agent":"0x56C7776351BaDf99D33A602026aAAD7Afc5E4dF4",
 "Cipher Wraith Agent":"0x50e9958a50B239f96fC64b9e1A06A3850D24063a",
 "Umbra Lynx Agent":"0x1062c963F5F11A5A55831B7e818E55b052B59947",
}
out={"block":block(),"leads":{}}
for name,addr in LEADS.items():
    d={}
    for sig in ["totalMinted()","totalSupply()","spotsLeft()","MAX_SUPPLY()","PRICE()","balanceOf(address)"]:
        args=enc(USER) if "address" in sig else ""
        d[sig]=raw(addr, sel(sig)+args)
    d["mintedBy_user"]=raw(addr, sel("mintedBy(address)")+enc(USER))
    out["leads"][name]=d
    print(name, d)
json.dump(out, open(f"{BASE}/run-2026-11-06-0731-early-probe.json","w"), indent=1)
