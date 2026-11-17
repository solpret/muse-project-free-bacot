#!/usr/bin/env python3
"""Hot-leg 2026-11-08 00:14 WIB re-read (read-only, single-call, concurrent).
Compares against hot-leg-2026-11-08-0009-reread.json (+retry)."""
import json, sys, time, concurrent.futures
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
U = enc_addr(USER)

def call(to, data):
    for ep in EPS:
        try:
            v = _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
            if v is None: return None
            return int(v, 16)
        except Exception:
            continue
    return None

ITEMS = {
 "HUNT PASS": ("0x885128Cf234c768F1353e2C1432D55873C6b67dD", [("totalMinted","totalMinted()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),("freeMinted","freeMinted()",""),("balanceOf_user","balanceOf(address)",U),("mintedBy_user","mintedBy(address)",U)]),
 "HOG ORBIT": ("0x7bc0b487febcbb1caa781148bf05a8cd72d02ec5", [("freeLeft","freeLeft()",""),("totalSupply","totalSupply()",""),("balanceOf_user","balanceOf(address)",U),("freeOf_user","freeOf(address,uint256)",U+enc_uint(1)),("costOf_user","costOf(address,uint256)",U+enc_uint(1)),("mintsLeft_user","mintsLeft(address)",U),("mintedBy_user","mintedBy(address)",U)]),
 "Tri333": ("0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f", [("freeMinted","freeMinted()",""),("FREE_CAP","FREE_CAP()",""),("freeCount_user","freeCount(address)",U),("mintOpen","mintOpen()",""),("balanceOf_user","balanceOf(address)",U)]),
 "WAR3": ("0x1Aa9797cC762b838388566Daa45A56b1709F4Bbe", [("freeMinted","freeMinted()",""),("totalSupply","totalSupply()",""),("balanceOf_user","balanceOf(address)",U)]),
 "DinoAgent": ("0xcE19D6A5FF15e088D4bf23614242927139084895", [("freeMinted","freeMinted()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),("freeClaimed_user","freeClaimed(address)",U)]),
 "fab7-variant": ("0xfab7dd20e8816e10227C1222bd4Bd446FecF1B72", [("freeMinted","freeMinted()",""),("FREE_SHARES","FREE_SHARES()",""),("totalMinted","totalMinted()",""),("finalized","finalized()","")]),
 "AURISLE": ("0xC52a979C20C5a43e5Be4Ffa6d1A4DD50069D5E2D", [("freeMinted","freeMinted()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),("freeClaimed_user","freeClaimed(address)",U)]),
 "CipherAgent": ("0x158b5e25015758a94703A27c152889451E5d52E5", [("totalMints","totalMints()",""),("mintOpen","mintOpen()",""),("balanceOf_user","balanceOf(address)",U)]),
 "MarsAgent": ("0x2231FdAe405c33dc4993f8C577c453802FF1AcE9", [("totalMints","totalMints()",""),("mintOpen","mintOpen()",""),("balanceOf_user","balanceOf(address)",U)]),
 "OnlyAI": ("0x156482ad3f0eebd8e3f70d494ebd1da3f738f5ba", [("totalSupply","totalSupply()",""),("balanceOf_user","balanceOf(address)",U)]),
 "Ink Koi": ("0xbd4B4e7189ae9356514664146b0eD683601200A9", [("freeMinted","freeMinted()",""),("freeClaimed_user","freeClaimed(address)",U)]),
 "LOCKSMITH": ("0x05e8738290be6639fD0f7236ebF444E5466D3164", [("totalMinted","totalMinted()",""),("freeMintedTotal","freeMintedTotal()",""),("FREE_CAP","FREE_CAP()",""),("mintActive","mintActive()","")]),
 "Gloops": ("0x183CBb52B3C7BCB2433d50dE0Add99B59f4DE4fE", [("totalMinted","totalMinted()",""),("mintOpen","mintOpen()","")]),
 "Saturnagent": ("0xef870a9b4a529373fb2e174b59ca7a66eb018074", [("freeClaimed","freeClaimed()",""),("quote_user1","quote(address,uint256)",U+enc_uint(1))]),
 "Lumenhold": ("0x9701980b0afd825134390ee46fb3bd675a2f356f", [("freeClaimed","freeClaimed()",""),("quote_user1","quote(address,uint256)",U+enc_uint(1))]),
 "AgentBook": ("0xEECaCBE6eAC6D6F2a38e8daA9049C7AA08aD43b0", [("FREE_QUOTA","FREE_QUOTA()",""),("remainingFree","remainingFree()","")]),
 "Night Bandits Club": ("0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf", [("freeUsed","freeUsed()",""),("freeTakenBy_user","freeTakenBy(address)",U)]),
}
def block():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
    return None

jobs = []
for name,(addr,views) in ITEMS.items():
    for key,sig,arg in views:
        jobs.append((name,addr,key,sel(sig)+arg))
t0=time.time()
out={}
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
    futs={ex.submit(call,addr,data):(name,key) for name,addr,key,data in jobs}
    for f in concurrent.futures.as_completed(futs):
        name,key=futs[f]
        try: v=f.result()
        except Exception: v=None
        out.setdefault(name,{})[key]=v
res={"block":block(),"items":{n:dict([("address",ITEMS[n][0])]+list(v.items())) for n,v in out.items()},"started_wib":"2026-11-08 00:14 WIB","duration_sec":round(time.time()-t0,1)}
print(json.dumps(res,indent=1))
json.dump(res,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-08-0014-reread.json","w"),indent=1)
