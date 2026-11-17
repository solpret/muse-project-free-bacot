import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race, call_many
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
H = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; pad = USER[2:].rjust(64, '0')
block = int(race("eth_blockNumber", []), 16)
print("block", block, flush=True)
targets = {
 "Tri333": "0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f",
 "NBC": "0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf",
 "DinoAgent": "0xcE19D6A5FF15e088D4bf23614242927139084895",
 "ADCHAR": "0x6E8b05C2dD1C625D839f33f60B837d9AF25E6044",
 "InkKoi": "0xbd4B4e7189ae9356514664146b0eD683601200A9",
 "Draco": "0x2e1927798462397a88e3c1015Dc8168e798DF6D3",
 "PHNX": "0x28a4F0BbdC1bE886f9e5a290e6598A83F248B224",
}
views = [("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("FREE_CAP()",""),
 ("totalMinted()",""),("freeMinted()",""),("freeUsed()",""),("freeMintsLeft()",""),("freeMintsUsed()",""),
 ("mintOpen()",""),("nextTokenId()",""),
 ("freeClaimed(address)",pad),("freeCount(address)",pad),("freeTakenBy(address)",pad),
 ("freeUsed(address)",pad),("hasClaimed(address)",pad),("mintedBy(address)",pad),
 ("mintsOf(address)",pad),("balanceOf(address)",pad),
 ("isFreeMintAvailable(address)",pad),("currentPriceFor(address)",pad)]
calls=[]; meta=[]
for name,addr in targets.items():
    for sig,args in views:
        calls.append((addr,"0x"+sel(sig)+args)); meta.append((name,sig))
res=[]
for i in range(0,len(calls),80): res+=call_many(calls[i:i+80])
reread={}
for (name,sig),r in zip(meta,res):
    v=None
    if isinstance(r,str) and r.startswith("0x") and len(r)==66:
        try: v=int(r,16)
        except Exception: v=None
    reread.setdefault(name,{"address":targets[name]})[sig]=v
print(json.dumps(reread,indent=1),flush=True)
json.dump({"block":block,"reread":reread},open(f"{H}/hot-leg-2026-11-07-1924-reread.json","w"),indent=1)
print("DONE",block)
