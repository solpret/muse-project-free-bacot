#!/usr/bin/env python3
"""Run 0131 scan triage. Read-only."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def iv(v): return int(v,16) if v else None
scan=json.load(open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-scan-2026-11-02-0201.json'))
seen=json.load(open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-scan-seen.json'))
seen_addrs=set(seen.get("contracts",{}).keys())
snap=json.load(open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json'))
known=set()
for v in snap["contracts"].values(): known.add(v["address"].lower())
for v in snap["track_c"].values():
    for k in ("sale","token","address"):
        if v.get(k): known.add(v[k].lower())
EXCLUDED_NAMES={"piggy agent","worldygg","blob miner","pulse.ai","fluffies","nonce genesis","hashstone","laser agents","pixel","agent nakamigos","ghost agents","ka agents","onchain crystals","flaggies","agent pandas","ascension","colo","quogent","niche society","halcyx"}
REG="0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
cands=[]
for c in scan["contracts"]:
    a=c["address"].lower()
    if a in seen_addrs or a in known or a==REG: continue
    if c.get("sourcify")!="verified" or not c.get("free_shaped") or not c.get("registry_bytes_hit"): continue
    if (c.get("name") or "").lower() in EXCLUDED_NAMES: continue
    cands.append(c)
print("triage candidates (verified+free+registry, first-seen):", len(cands))
out=[]
for c in cands:
    A=c["address"]; r={"address":A,"name":c.get("name"),"symbol":c.get("symbol"),"window_mints":c["mint_count"],"window_minters":c["distinct_minters"],"window_first_block":c["first_block"]}
    r["totalSupply"]=iv(call(A, sel("totalSupply()"))); r["totalMinted"]=iv(call(A, sel("totalMinted()")))
    r["freeClaimed"]=iv(call(A, sel("freeClaimed()"))); r["FREE_SUPPLY"]=iv(call(A, sel("FREE_SUPPLY()")))
    r["AGENT_ID"]=call(A, sel("AGENT_ID()")); r["agentIdRegistry"]=call(A, sel("agentIdRegistry()"))
    tot=r["totalSupply"] if r["totalSupply"] is not None else r["totalMinted"]
    r["total_for_compare"]=tot
    r["verdict"]="FIRST-MINTS-VERIFIED" if (tot is not None and tot<=c["mint_count"]+5) else ("continuation" if tot is not None else "total-unreadable")
    out.append(r); print(json.dumps(r))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0201-scan-triage.json","w"), indent=1)
# update seen file: append ALL scan contracts (not just triaged) per body: append newly seen contracts
new=0
for c in scan["contracts"]:
    a=c["address"].lower()
    if a not in seen["contracts"]:
        seen["contracts"][a]={"first_seen_block":c["first_block"],"source":"scan-2026-11-02-0201"}; new+=1
json.dump(seen, open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-scan-seen.json','w'), indent=1)
print("seen appended:", new, "total seen contracts now:", len(seen["contracts"]))
