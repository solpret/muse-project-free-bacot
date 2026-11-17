#!/usr/bin/env python3
"""hot-leg 2026-11-09 19:04 (scheduled) re-read: same 31 items as 19:05 run
(block 132581501 baseline). Read-only. Writes hot-leg-2026-11-09-1904-reread.json
+ prints diffs. Also one-off MOTOR free-lane check (agentFreeUsed vs
AGENT_FREE_CAP) from the Boltbook ZH post claiming the free lane closed
~19:07 WIB; MOTOR is snapshot status minted-by-user, user slot already used."""
import json, subprocess
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc.nodereal.io/"
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_uint(n): return format(n, "064x")
NOARG = ["totalSupply","totalMinted","totalMints","freeMinted","freeClaimed",
 "freeMintedTotal","freeLeft","freeUsed","FREE_CAP","FREE_SUPPLY","FREE_SHARES",
 "FREE_QUOTA","FREE_PER_WALLET","remainingFree","MAX_SUPPLY","MAX_FREE",
 "sharesMinted","sold","phase","launched","soldOut","closed","finalized",
 "mintOpen","mintActive","totalSkunksMinted","freeSkunksClaimed",
 "freeSkunksRemaining","freeWindowOpen",
 "agentFreeUsed","AGENT_FREE_CAP","paidMinted"]
ADDRARG = ["balanceOf","mintedBy","freeClaimed","freeLeft","freeUsed","freeCount",
 "freeMinted","mintedCount","freeAvailable","hasMinted","quotaOf","freeTakenBy",
 "priceFor","freeClaimedBy","freeUsedByWallet"]
ADDRUINT = ["quote","freeFor"]
def calldata(field):
    if field in ("address","_batch_fail"): return None
    if field.endswith("_user1"):
        fn = field[:-6]
        if fn in ADDRUINT: return sel(f"{fn}(address,uint256)") + enc_addr(USER) + enc_uint(1)
        return None
    if field.endswith("_user"):
        fn = field[:-5]
        if fn in ADDRARG: return sel(f"{fn}(address)") + enc_addr(USER)
        return None
    if field in NOARG: return sel(f"{field}()")
    return None
def run_batch(calls):
    payload = json.dumps([{"jsonrpc":"2.0","id":i,"method":"eth_call","params":[{"to":to,"data":data},"latest"]} for i,(to,data) in enumerate(calls)])
    p = subprocess.run(["curl","-s","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","--data",payload],capture_output=True,text=True)
    try: return json.loads(p.stdout)
    except Exception: return {"_curl_error": p.stdout[:200]+p.stderr[:200]}
def decode(r):
    if not isinstance(r,str) or not r.startswith("0x"): return None
    try: return int(r,16)
    except Exception: return None
def main():
    prev = json.load(open(BASE+"hot-leg-2026-11-09-1905-reread.json"))
    items = prev["items"]
    motor = {"address": "0x86F83E98437A1DcF0e4A62828f68C1D53B3c7AB5",
             "agentFreeUsed": None, "AGENT_FREE_CAP": None, "totalSupply": None,
             "paidMinted": None, "freeUsedByWallet_user": None}
    jobs=[]
    for name,entry in items.items():
        for field in entry:
            if field=="address": continue
            d=calldata(field)
            jobs.append((name,field,entry["address"],d))
    for field in motor:
        if field=="address": continue
        jobs.append(("MOTOR",field,motor["address"],calldata(field)))
    results={}
    real=[j for j in jobs if j[3] is not None]
    for i in range(0,len(real),25):
        chunk=real[i:i+25]
        resp=run_batch([(to,data) for (_,_,to,data) in chunk])
        if isinstance(resp,dict) and "_curl_error" in resp:
            for (n,f,t,d) in chunk: results[(n,f)]=None
            continue
        if isinstance(resp,dict): resp=[resp]
        for j,item in enumerate(resp):
            n,f,t,d=chunk[j]
            results[(n,f)]=decode(item["result"]) if isinstance(item,dict) and "result" in item else None
    for (n,f,t,d) in jobs:
        if d is None: results[(n,f)]=None
    out={"block":None,"items":{}}
    p=subprocess.run(["curl","-s","--max-time","15","-X","POST",EP,"-H","Content-Type: application/json","--data",json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})],capture_output=True,text=True)
    try: out["block"]=int(json.loads(p.stdout)["result"],16)
    except Exception: out["block"]=None
    for name,entry in items.items():
        row={"address":entry["address"]}
        for field in entry:
            if field=="address": continue
            row[field]=results.get((name,field))
        out["items"][name]=row
    diffs=[]
    for name,row in out["items"].items():
        base=prev["items"].get(name,{})
        for field,val in row.items():
            if field=="address": continue
            old=base.get(field)
            if old is None and val is None: continue
            if old!=val: diffs.append({"item":name,"field":field,"old":old,"new":val})
    out["diffs_vs_1905"]=diffs
    out["MOTOR"]={f:results.get(("MOTOR",f)) for f in motor if f!="address"}
    out["MOTOR"]["address"]=motor["address"]
    json.dump(out,open(BASE+"hot-leg-2026-11-09-1904-reread.json","w"),indent=1)
    print("block:",out["block"],"calls:",len(real))
    print("DIFFS:",json.dumps(diffs,indent=1))
    print("MOTOR:",json.dumps(out["MOTOR"]))
    print("NULLS:",json.dumps({f"{n}.{f}":v for (n,f),v in results.items() if v is None}))
if __name__=="__main__":
    main()
