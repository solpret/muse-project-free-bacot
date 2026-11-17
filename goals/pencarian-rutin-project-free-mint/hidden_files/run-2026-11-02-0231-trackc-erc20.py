#!/usr/bin/env python3
"""Run 0131 route 5c ERC-20 backlog shape-check. Read-only except checked-file update."""
import json, urllib.request, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def get(url):
    req=urllib.request.Request(url, headers={"User-Agent":"free-mint-search/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)
FREE_VIEWS={"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeShares","freeCount"}
scan=json.load(open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-scan-2026-11-02-0231.json'))
chk=json.load(open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/track-c-scan-checked.json'))
checked=set(a.lower() for a in chk.get("checked",[]))
snap=json.load(open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json'))
known=set()
for v in snap["track_c"].values():
    for k in ("sale","token","address"):
        if v.get(k): known.add(v[k].lower())
cand=[x for x in scan["erc20_mint_contracts_list"] if x["mint_count"]>=10 and x["address"].lower() not in checked and x["address"].lower() not in known]
cand.sort(key=lambda x: -x["mint_count"])
todo=cand[:20]
print("todo:", len(todo), "remaining dropped as sampling limit:", len(cand)-len(todo))
out=[]
for x in todo:
    A=x["address"]; entry={"address":A,"mint_count":x["mint_count"],"distinct_minters":x["distinct_minters"]}
    try:
        d=get(f"https://sourcify.dev/server/v2/contract/56/{A}?fields=abi")
        fns=[e["name"] for e in d.get("abi",[]) if e.get("type")=="function"]
        entry["sourcify"]="verified"; entry["functions"]=fns
        has_mint=any(f in fns for f in ("mint","mintFree","claimFree"))
        has_quote=any(f in fns for f in ("quote","costFor","quoteFor"))
        free=[f for f in fns if f in FREE_VIEWS]
        agent=any(("registry" in f.lower() or "gate" in f.lower()) for f in fns)
        is_token=all(f in fns for f in ("name","symbol","decimals","totalSupply"))
        entry.update({"has_mint":has_mint,"has_quote":has_quote,"free_views":free,"agent_ref_name":agent,"is_token":is_token})
        entry["S1"]=bool(has_mint and has_quote and free and agent)
        entry["S2"]=bool(is_token and ("mintFree" in fns) and free and agent)
        entry["S2_variant"]=bool(is_token and ("claimFree" in fns) and free and agent)
        # identity-delegation follow-up for near passes (RuninAI lesson): claimFree/mint + free, identity() present, no name agent ref
        if not entry["S1"] and not entry["S2"] and has_mint and free and "identity" in fns:
            ident=call(A, sel("identity()"))
            entry["identity"]=ident
            if ident:
                ia="0x"+ident[-40:]; entry["identity_addr"]=ia
                entry["identity_REGISTRY"]=call(ia, sel("REGISTRY()"))
    except Exception as e:
        entry["sourcify"]="unverified-or-error"; entry["error"]=f"{type(e).__name__}: {str(e)[:120]}"
        entry["S1"]=False; entry["S2"]=False
    out.append(entry); print(json.dumps(entry)[:700])
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0231-trackc-erc20.json","w"), indent=1)
chk["checked"]=sorted(checked | {x["address"].lower() for x in todo})
json.dump(chk, open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/track-c-scan-checked.json','w'), indent=1)
print("checked total now:", len(chk["checked"]))
