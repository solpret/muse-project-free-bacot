import json, urllib.request, urllib.error, time
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
H = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; pad = USER[2:].rjust(64, '0')
targets = {
 "Tri333": ("0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f", [("freeMinted()",None),("FREE_CAP()",None),("freeCount(address)","user")]),
 "NBC": ("0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf", [("freeMinted()",None),("freeTakenBy(address)","user"),("balanceOf(address)","user")]),
 "DinoAgent": ("0xcE19D6A5FF15e088D4bf23614242927139084895", [("freeMinted()",None),("freeClaimed(address)","user")]),
 "ADCHAR": ("0x6E8b05C2dD1C625D839f33f60B837d9AF25E6044", [("nextTokenId()",None),("hasClaimed(address)","user")]),
 "InkKoi": ("0xbd4B4e7189ae9356514664146b0eD683601200A9", [("freeMinted()",None),("freeClaimed(address)","user")]),
 "Draco": ("0x2e1927798462397a88e3c1015Dc8168e798DF6D3", [("isFreeMintAvailable(address)","user"),("totalMints()",None)]),
 "PHNX": ("0x28a4F0BbdC1bE886f9e5a290e6598A83F248B224", [("freeMintsLeft()",None),("isFreeMintAvailable(address)","user")]),
}
def one(addr, data):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}).encode()
    for attempt in range(3):
        try:
            req = urllib.request.Request("https://bsc-dataseed.binance.org/", data=body, headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                d = json.load(r)
            if "result" in d and isinstance(d["result"], str) and len(d["result"]) == 66:
                return int(d["result"], 16)
            if "error" in d:
                return "REVERT:" + str(d["error"].get("message",""))[:50]
            return "UNREAD:" + str(d)[:60]
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(4); continue
            return "HTTP%d" % e.code
        except Exception as e:
            time.sleep(2)
    return "FAIL"
out = {}
for name,(addr,views) in targets.items():
    out[name] = {}
    for sig,arg in views:
        data = "0x"+sel(sig)+(pad if arg=="user" else "")
        out[name][sig] = one(addr, data)
        time.sleep(1)
    json.dump({"block":132200917,"reread":out}, open(f"{H}/hot-leg-2026-11-07-1924-reread.json","w"), indent=1)
    print(name, out[name], flush=True)
print("DONE")
