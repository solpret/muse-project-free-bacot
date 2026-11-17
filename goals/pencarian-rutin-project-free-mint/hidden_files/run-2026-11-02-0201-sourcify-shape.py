#!/usr/bin/env python3
"""Hot-leg Sourcify shape-check (S1/S2), read-only. First run 2026-11-01 23:09 WIB."""
import json, sys, urllib.request, concurrent.futures
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
FEED = ["0xa233C45f881A6982647b63c61D7a5f9a3F90C5f4", "0x8E878C801b9F37cc0Cb6FF3C4597Af8FC057988b", "0xEbAdb5Be9692b0BF25E8A5F3351C35DdC58f195d", "0xB330e582f45c0243e5Eb1B56958b56273f26a9eB", "0xB44050254A25dAA8077C14BbB20d0a595e6CECE2", "0x74C2214fDCc10c303302592151c50965903aa7a9", "0x7f22e7cf2D2F85Ca6eb62Bf0B55f0B9229FF150F", "0x87a0db692B6815a756Ca3417574625735ED1399A", "0x011F1aeaF230A5E8dee20168654644DA4DE3C4B5", "0x16469C174cd827A5e21f4bf3eE3711f2bB42e275", "0xBB5CEb0a5e742B93FB96d1Ba22C4fD17Bb6798Ab", "0x38291fd400FDA30844B8D61133899a1966C6aa1B", "0x71fe29fD37F7f9AfC3F68e80339B12f3C42DDAbc", "0xAfa2Eb55F53bA5dC467bC3c2687d1bcE2ED2a779", "0xD94d7cc33262b40D19701fF58E97fa9602156F0E", "0x6125cB8F49bC5BEabfa3AceCEf4193d8F054d861", "0x3016C51322FE27e6029B649991df4A54061Ef7AB", "0x1F984f56249f991b24f960561844012c1c01B3cA", "0x1D645B30edbA8C8FBECaE9ECAeD6f323B65B3904", "0xc6929355F4b06506daeCeE0b53601a46B632B628", "0x55BA8f291cd8A520Db5634c009FE45e3C1456d17", "0x3DEF2fcC16E41F6A9fA88F9E47f6ADbD550f0A90", "0x0F90Fe32f079c2Fd943336F0f9658350c8D88D94", "0x6d8a561B3a8e9312b9E3475988122Dfa0EF47d84", "0x22801730D94A5853D0E8D6DFfa3E35a832D5adBe", "0xFA66b5395A49723263138ca3C501dc91EDE993e1", "0x7D6fFCb1D4716608C59407ef99Dc2D98adc3D946", "0x2DbAB55927F349c2fADD5a9598c6a54e646FB302", "0xD79D17E100D171F33538B885C1af3a3218890521", "0x32970cF194633E3dC6448112Bfb46Ec05B28E93D"]
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
def fetch(addr):
    for kind in ("v2abi",):
        url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"hot-leg/1.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                meta = json.loads(r.read().decode())
            abi = meta.get("abi", [])
            fns = {}
            for e in abi:
                if e.get("type") == "function":
                    fns.setdefault(e["name"], []).append(e)
            names = set(fns)
            has_mint = any(n.lower().startswith("mint") for n in names)
            has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
            free_views = sorted(names & set(FREE_VIEWS))
            agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
            s1 = has_mint and has_quote and bool(free_views) and agent_ref
            is_token = bool(names & {"name","symbol","decimals","totalSupply"})
            mintfree = "mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
            s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
            return {"address": addr, "match": kind, "functions": sorted(names),
                    "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                    "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token}
        except Exception as ex:
            last = f"{type(ex).__name__}: {str(ex)[:120]}"
    return {"address": addr, "match": None, "error": last}
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    out = list(ex.map(fetch, FEED))
for o in out:
    print(json.dumps(o))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0201-sourcify-shape.json","w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
