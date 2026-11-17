import json, sys, urllib.request, ast
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-05-1501"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
# keys passed as comma-separated argv[1]; out file argv[2]
keys=sys.argv[1].split(",")
outf=sys.argv[2]
cands=json.load(open(f"{BASE}/run-{TS}-age-candidates.json"))
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=12) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:60]}
            v=out["result"]
            if not v or v=="0x": return None
            try: return int(v,16)
            except Exception: return v
        except Exception: continue
    return {"error":"rpc-fail"}
def block():
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None
res={"block":block()}
for k in keys:
    a=cands[k]["address"]; d={}
    for fn in ["totalSupply()","totalMinted()","freeMinted()","freeClaimed()","FREE_SUPPLY()","FREE_CAP()","MAX_SUPPLY()"]:
        d[fn]=raw(a,sel(fn))
    d["balanceOf(user)"]=raw(a,sel("balanceOf(address)")+enc(USER))
    res[k]=d
    print(k, d, flush=True)
    json.dump(res, open(f"{BASE}/{outf}","w"), indent=1)
print("DONE block", res["block"], flush=True)
