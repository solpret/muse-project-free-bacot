#!/usr/bin/env python3
"""Sourcify shape-check run 1531: 18 addresses newly verified since 07:40:52Z (top run 1431).
Read-only. Fetches ABI via sourcify metadata, checks agent-shape (A) + sale-shape S1/S2 (C).
"""
import json, subprocess, concurrent.futures
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDRS = [
 "0x144763c5B4571efba0B0112c518900b884DBeF98","0x0C9242825016a1BDc148A48A3e6cc131eD3319AF",
 "0xaD80Daa0e8fD52Eaa57e6050334A3503F7f4a6bF","0xD63020c0b7E4a6138A16dccEda750ce369e1FD40",
 "0x53Cac593BBFd8cA9Bf1dD62556Df4707ECdE7777","0x9dC652B41142B7237CB7D33398236f5BdFFdfF71",
 "0x18E077729B83a7112b8091902809F7aBdef9957A","0x022d67729D0D5C9806C09614F1a78BEf28475Cee",
 "0x230b7BD7F72dC1236baB161F71D3Eb0Dd9b06889","0xa376d14dc0A6524e5d346ad9c5B628982DE0511C",
 "0x69164D8756d755eed154432ac4FFb673113a58E6","0x87C5d481A3219a7516A22606211F3D14DA467352",
 "0x7E41906a8d4Ed5Ef4146c920B6fc8f4B80859CDe","0x5e8bF4492ea0466e32D94a181C04d61f45eA7777",
 "0xF8f64ca920edcA1684C775C8B19ED04e77c94fB0","0x0889b3a797677f17d952eeE08F1120F6e5ed34F0",
 "0x5e4C1a1fAc1b77E0017bCf9686b66b039d76aA9F","0x8334C7d0e8aF217EEA5251A0A181e628971535e1",
]
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
 "freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
AGENT_FNS = {"agentId","agentRegistry","agentIdRegistry","holdsAgentId","registry",
 "getAgentId","agentGate","AgentGate","AGENT_ID_REGISTRY","hasAgentId","AGENT_ID"}
QUOTE_FNS = {"quote","cost","getQuote","mintCost","price","getPrice"}
def one(addr):
    try:
        r = subprocess.run(["curl","-s","-L","--max-time","30",
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
            capture_output=True, timeout=35)
        meta = json.loads(r.stdout.decode())
        abi = meta.get("abi") or []
        names = {e["name"] for e in abi if e.get("type")=="function"}
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & QUOTE_FNS)
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & AGENT_FNS)
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and bool(names & {"mintFree"}) and bool(free_views) and agent_ref
        agent_shaped = agent_ref or has_mint and bool(free_views)
        return {"address": addr, "verified": bool(abi), "verifiedAt": meta.get("verifiedAt"),
                "n_fns": len(names), "has_mint": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token,
                "S1": s1, "S2": s2, "agent_shaped": agent_shaped,
                "fns": sorted(names)[:60]}
    except Exception as e:
        return {"address": addr, "verified": False, "error": f"{type(e).__name__}: {str(e)[:120]}"}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    res = list(ex.map(one, ADDRS))
for r in res:
    print(r["address"], "| verified:", r.get("verified"), "| n_fns:", r.get("n_fns"),
          "| mint:", r.get("has_mint"), "| quote:", r.get("has_quote"),
          "| free:", r.get("free_views"), "| agent:", r.get("agent_ref"),
          "| S1:", r.get("S1"), "| S2:", r.get("S2"), "|", r.get("error",""))
json.dump(res, open(f"{HF}/run-2026-11-18-1531-feed-shape.json","w"), indent=1)
print("hits S1/S2/agent-shaped:", [r["address"] for r in res if r.get("S1") or r.get("S2") or r.get("agent_shaped")])
print("saved run-2026-11-18-1531-feed-shape.json")
