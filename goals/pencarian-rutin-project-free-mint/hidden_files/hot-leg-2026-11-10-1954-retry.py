#!/usr/bin/env python3
"""One retry of leg-4 failed fields via bsc-dataseed (read-only). Merges
successful re-reads into hot-leg-2026-11-10-1954-reread.json, recomputes
diffs vs 1944 baseline. Nulls stay baseline."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc-dataseed.binance.org/"
T0 = time.time()
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x","").rjust(64,"0")
def enc_uint(n): return format(n,"064x")
NOARG = ["totalSupply","totalMinted","totalMints","freeMinted","freeClaimed",
 "freeMintedTotal","freeLeft","freeUsed","FREE_CAP","FREE_SUPPLY","FREE_SHARES",
 "FREE_QUOTA","FREE_PER_WALLET","remainingFree","MAX_SUPPLY","MAX_FREE",
 "sharesMinted","sold","phase","launched","soldOut","closed","finalized",
 "mintOpen","mintActive","totalSkunksMinted","freeSkunksClaimed",
 "freeSkunksRemaining","freeRemaining","mintCount","MAX_MINTS","opened",
 "openedAt","saleActive","soldShares","publicMinted","launchTime","totalShares",
 "totalFreeShares","mintingOpen","TOTAL_SHARES","MAX_FREE_SHARES","SALE_START",
 "isSaleEnded","remaining","mintEnd","mintStart","SALE_END","startTime",
 "freeWindowOpen","agentFreeUsed","AGENT_FREE_CAP","paidMinted"]
ADDRARG = ["balanceOf","mintedBy","freeClaimed","freeLeft","freeUsed","freeCount",
 "freeMinted","mintedCount","freeAvailable","hasMinted","quotaOf","freeTakenBy",
 "priceFor","freeClaimedBy","freeUsedByWallet","hasFreeMinted","freeAllowance",
 "maxShares","remainingShares"]
ADDRUINT = ["quote","freeFor"]
def calldata(field):
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
def decode(r):
    if not isinstance(r,str) or not r.startswith("0x"): return None
    try: return int(r,16)
    except Exception: return None
reread = json.load(open(BASE+"hot-leg-2026-11-10-1954-reread.json"))
leg4 = json.load(open(BASE+"hot-leg-run-2026-11-10-1954-leg4.json"))
failed = [(f["item"], f["field"]) for f in leg4["leg4"]["read_failed"]]
jobs=[]
for name, field in failed:
    addr = reread["items"][name]["address"]
    data = calldata(field)
    if data: jobs.append((name, field, addr, data))
print("retry jobs:", len(jobs))
ok=0; still=[]
for i in range(0, len(jobs), 25):
    chunk = jobs[i:i+25]
    payload = json.dumps([{"jsonrpc":"2.0","id":j,"method":"eth_call",
        "params":[{"to":to,"data":data},"latest"]} for j,(n,f,to,data) in enumerate(chunk)])
    p = subprocess.run(["curl","-s","--max-time","30","-X","POST",EP,
        "-H","Content-Type: application/json","--data",payload], capture_output=True, text=True)
    try: resp = json.loads(p.stdout)
    except Exception: resp = None
    if isinstance(resp, dict): resp=[resp]
    if not resp:
        still += [(n,f) for n,f,_,_ in chunk]; continue
    for j, item in enumerate(resp):
        name, field, to, data = chunk[j]
        v = decode(item.get("result")) if isinstance(item, dict) else None
        if v is None: still.append((name,field))
        else:
            reread["items"][name][field]=v; ok+=1
print("recovered:", ok, "still failed:", len(still), "duration:", round(time.time()-T0,1))
prev = json.load(open(BASE+"hot-leg-2026-11-10-1944-reread.json"))
diffs=[]
for name, row in reread["items"].items():
    base = prev["items"].get(name,{})
    for field, val in row.items():
        if field=="address": continue
        old = base.get(field)
        if old is None and val is None: continue
        if old != val: diffs.append({"item":name,"field":field,"old":old,"new":val})
reread["diffs_vs_1944"]=diffs
reread["read_failed"]=[{"item":n,"field":f} for n,f in still]
reread["retry"]={"endpoint":EP,"recovered":ok,"still_failed":len(still),"duration_sec":round(time.time()-T0,1)}
json.dump(reread, open(BASE+"hot-leg-2026-11-10-1954-reread.json","w"), indent=1)
print("DIFFS:", json.dumps(diffs, indent=1))
