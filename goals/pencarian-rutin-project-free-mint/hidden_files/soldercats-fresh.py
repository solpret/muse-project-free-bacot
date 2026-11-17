import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SALE="0x3D972EBbF7488f21b95250B867e2406c723C9DDC"
EP="https://bsc.nodereal.io/"
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a.lower().replace("0x","").rjust(64,"0")
calls=[("mintStart","mintStart()"),("mintOpen","mintOpen()"),("agentFreeUsed","agentFreeUsed()"),
("AGENT_FREE_CAP","AGENT_FREE_CAP()"),("agentFreeByWallet_user","agentFreeByWallet(address)"),
("freeLeft","freeLeft()"),("walletInfo_user","walletInfo(address)"),("TOKEN","TOKEN()"),
("totalSupply","totalSupply()"),("balanceOf_user","balanceOf(address)"),("PRICE","PRICE()"),
("MAX_SUPPLY","MAX_SUPPLY()"),("paidMinted","paidMinted()"),("REGISTRY","REGISTRY()"),
("mintEnd","mintEnd()"),("status","status()")]
jobs=[]
for name,sig in calls:
    data=sel(sig)+enc(USER) if sig.endswith("(address)") else sel(sig)
    jobs.append((name,data))
payload=json.dumps([{"jsonrpc":"2.0","id":i,"method":"eth_call","params":[{"to":SALE,"data":d},"latest"]} for i,(n,d) in enumerate(jobs)])
p=subprocess.run(["curl","-s","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","--data",payload],capture_output=True,text=True)
resps=json.loads(p.stdout)
out={}
for (name,_),r in zip(jobs,resps):
    raw=r.get("result") if isinstance(r,dict) else None
    out[name]=raw
    print(name,"=",raw, r.get("error","") if isinstance(r,dict) else "")
json.dump(out, open(BASE+"soldercats-fresh-0834.json","w"), indent=1)
# block
p2=subprocess.run(["curl","-s","--max-time","15","-X","POST",EP,"-H","Content-Type: application/json","--data",'{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],capture_output=True,text=True)
print("block:", json.loads(p2.stdout).get("result"))
