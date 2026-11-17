import json, urllib.request
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
H = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; pad = USER[2:].rjust(64, '0')
targets = {
 "Tri333": ("0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f", [("freeMinted()",None),("FREE_CAP()",None),("freeCount(address)","user"),("balanceOf(address)","user"),("mintOpen()",None)]),
 "NBC": ("0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf", [("freeMinted()",None),("freeUsed()",None),("totalSupply()",None),("freeTakenBy(address)","user"),("balanceOf(address)","user"),("mintOpen()",None)]),
 "DinoAgent": ("0xcE19D6A5FF15e088D4bf23614242927139084895", [("freeMinted()",None),("FREE_SUPPLY()",None),("freeClaimed(address)","user"),("balanceOf(address)","user")]),
 "ADCHAR": ("0x6E8b05C2dD1C625D839f33f60B837d9AF25E6044", [("nextTokenId()",None),("hasClaimed(address)","user")]),
 "InkKoi": ("0xbd4B4e7189ae9356514664146b0eD683601200A9", [("freeMinted()",None),("FREE_SUPPLY()",None),("freeClaimed(address)","user"),("totalSupply()",None),("balanceOf(address)","user")]),
 "Draco": ("0x2e1927798462397a88e3c1015Dc8168e798DF6D3", [("isFreeMintAvailable(address)","user"),("currentPriceFor(address)","user"),("mintsOf(address)","user"),("balanceOf(address)","user"),("totalMints()",None),("mintOpen()",None)]),
 "PHNX": ("0x28a4F0BbdC1bE886f9e5a290e6598A83F248B224", [("freeMintsLeft()",None),("freeMintsUsed()",None),("isFreeMintAvailable(address)","user"),("currentPriceFor(address)","user"),("mintsOf(address)","user"),("balanceOf(address)","user"),("totalMints()",None)]),
}
reqs=[]; meta=[]
i=0
for name,(addr,views) in targets.items():
    for sig,arg in views:
        data="0x"+sel(sig)+(pad if arg=="user" else "")
        reqs.append({"jsonrpc":"2.0","id":i,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        meta.append((name,sig)); i+=1
body=json.dumps(reqs).encode()
req=urllib.request.Request("https://bsc-dataseed.binance.org/",data=body,headers={"Content-Type":"application/json"})
with urllib.request.urlopen(req,timeout=30) as r:
    resp=json.load(r)
out={}
for (name,sig),item in zip(meta,resp):
    v=None
    if isinstance(item,dict) and "result" in item and isinstance(item["result"],str) and len(item["result"])==66:
        try: v=int(item["result"],16)
        except Exception: v=None
    elif isinstance(item,dict) and "error" in item:
        v="REVERT:"+str(item["error"].get("message",""))[:50]
    out.setdefault(name,{})[sig]=v
print(json.dumps(out,indent=1))
json.dump({"block":132200917,"reread":out},open(f"{H}/hot-leg-2026-11-07-1924-reread.json","w"),indent=1)
print("DONE")
