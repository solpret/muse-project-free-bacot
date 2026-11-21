#!/usr/bin/env python3
"""hot-leg 2026-11-21 15:24 WIB leg4 re-read + BAISHOU (new Boltbook ZH) on-chain read. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc.nodereal.io/", "https://bsc-rpc.publicnode.com"]
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
NOARG = ["totalSupply","totalMinted","freeMinted","freeClaimed","freeLeft","freeUsed",
 "FREE_SUPPLY","FREE_QUOTA","FREE_SHARES","mintOpen","mintActive","mintStartTime",
 "launched","failed","isRefundPhase","totalShares"]
ADDRARG = ["balanceOf","freeClaimed","freeClaimedBy","freeClaimedByWallet"]
def calldata(field):
    if field.endswith("_user"):
        fn = field[:-5]
        if fn in ADDRARG: return sel(f"{fn}(address)") + enc_addr(USER)
        return None
    if field in NOARG: return sel(f"{field}()")
    return None
def run_batch(calls):
    payload = json.dumps([{"jsonrpc":"2.0","id":i,"method":"eth_call","params":[{"to":to,"data":data},"latest"]} for i,(to,data) in enumerate(calls)])
    for ep in EPS:
        p = subprocess.run(["curl","-s","--max-time","25","-X","POST",ep,"-H","Content-Type: application/json","--data",payload],capture_output=True,text=True)
        try:
            r = json.loads(p.stdout)
            if isinstance(r, list) and r: return r
            if isinstance(r, dict) and "result" in r: return [r]
        except Exception:
            continue
    return None
def decode(r):
    if not isinstance(r,str) or not r.startswith("0x"): return None
    try: return int(r,16)
    except Exception: return None
ITEMS = {
 "Prosperity Turtle Agents": ("0x1F37Bd89349B6d14a6eF8353504C8E0DFf609C6f", ["totalSupply","totalMinted","freeClaimed","freeClaimed_user","balanceOf_user"]),
 "Guardian Lion Agents": ("0xdddB9129c40561B0b697D2a2Fc22429f04C181d6", ["totalSupply","totalMinted","freeClaimed","freeClaimed_user","balanceOf_user"]),
 "ONI": ("0x74BDA11E34EB02121104Ff38471D91Fe1C37F81A", ["totalSupply","totalMinted","freeMinted","freeClaimed","freeClaimed_user","balanceOf_user"]),
 "AgentMintPass": ("0xfcadfb7cc85b6ea540d64e4f4b9f162e630f55c0", ["totalSupply","totalMinted","freeClaimed","freeClaimed_user"]),
 "AGATE-Pass": ("0x5b63bd45e61a2e6540548c3509b598b6384206c5", ["totalSupply","totalMinted","freeClaimed","freeClaimed_user"]),
 "AgentDrop": ("0x1dd8740ffca0be3caac3b4a3eb41fdff506e38a9", ["totalSupply","totalMinted","freeClaimed","freeClaimed_user"]),
 "AgentForge Hero": ("0xA65944F2093e6dcFD1d1a7a4f6744f924068f878", ["totalSupply","totalMinted","freeClaimed","freeClaimed_user"]),
 "Coffee Agents": ("0xc1fAd916153d1b91d6ba9a2253450A6eB2f48245", ["totalSupply","totalMinted","mintActive","mintStartTime","FREE_QUOTA","freeClaimed_user"]),
 "AgentBadge-ABDG": ("0x126AF9585953004cbB9c5a0B37FC5616DD5F3B43", ["totalSupply","totalMinted","freeClaimed","freeClaimed_user"]),
 "Pocket Ai": ("0xf9D00B7a2992de00EBc5F9f04BAf95d44C542102", ["totalSupply","totalMinted","freeClaimed","freeClaimed_user"]),
 "DeepShard": ("0xC463960af285b7EDA0909D362Ae31783597C2076", ["totalSupply","totalMinted","freeClaimed","freeClaimed_user"]),
 "binanceai.fun mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", ["launched","failed","isRefundPhase","tokenClaimed_user","refundClaimed_user","totalShares"]),
 "BAISHOU": ("0xE69708358EC640C0bc86980893a4Afd01Aff6F9B", ["totalSupply","freeClaimed","freeMinted","freeLeft","FREE_SUPPLY","freeClaimed_user","balanceOf_user"]),
}
def main():
    jobs=[]
    for name,(addr,fields) in ITEMS.items():
        for f in fields:
            d=calldata(f)
            jobs.append((name,f,addr,d))
    results={}
    real=[j for j in jobs if j[3] is not None]
    for i in range(0,len(real),25):
        chunk=real[i:i+25]
        resp=run_batch([(t,d) for (_,_,t,d) in chunk])
        if resp is None:
            for (n,f,t,d) in chunk: results[(n,f)]="RPC-FAIL"
            continue
        for j,item in enumerate(resp):
            n,f,t,d=chunk[j]
            results[(n,f)]=decode(item.get("result")) if isinstance(item,dict) else None
    for (n,f,t,d) in jobs:
        if d is None: results[(n,f)]="NO-CALLDATA"
    block=None
    p=subprocess.run(["curl","-s","--max-time","15","-X","POST",EPS[0],"-H","Content-Type: application/json","--data",json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})],capture_output=True,text=True)
    try: block=int(json.loads(p.stdout)["result"],16)
    except Exception: block=None
    out={"block":block,"items":{}}
    for name,(addr,fields) in ITEMS.items():
        out["items"][name]={"address":addr}
        for f in fields: out["items"][name][f]=results.get((name,f))
    print(json.dumps(out,indent=1))
    json.dump(out,open(BASE+"hot-leg-1524-leg4.json","w"),indent=1)
if __name__=="__main__":
    main()
