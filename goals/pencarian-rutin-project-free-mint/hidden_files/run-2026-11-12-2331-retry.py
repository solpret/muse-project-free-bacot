#!/usr/bin/env python3
"""Retry Sourcify shape-checks via curl (urllib IncompleteRead lesson, run 2301/CHICK 1401)."""
import json, subprocess
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
ADDRS = ["0x00598F428C8b4A2765E53d25BD865cE3596927c1","0x0504146B29416e8ec0262616c5520c20bFAB7fD8",
"0x0D83163CB11b7959aaAc7A65f8f62082653E8577","0x177B6B8761eF67520c42edEBD63CECe15A0c5829",
"0x199664F7508DfBEf4B16125543dc302609737799","0x1e311022fEe30A395291eA21e5f339D3016a0Ed4",
"0x43405D834868d14bfF44Fe492A5091F367b98e77","0x97695B7D962c4Dc97681985C16e98b4da985DD87",
"0x98a05953D68168Bf3216fF55750fd487f76486F0","0xF408Bfe87b62be13c633b6277903EFB8426538dF",
"0xcb15aE4d71fDE657B1c9AbD3fe6F6EfA5A3bB2FA","0xd14d63660b0c8cDDCa0e131A8C4B0B43B6b80Fa2",
"0xf9f931FFd3EF62dd616eA3eFe306A289512ab28F","0xfbb7d47c9df597eb92cff98b1bb97d3572bcab87",
"0x74e4320f1aea16b64b1ec7961572d2a8bddde247","0xbacde2210f535acecca04525b6ba83f8104682e8"]
def shape(addr):
    try:
        out = subprocess.run(["curl","-sL","--max-time","25",
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
            capture_output=True, text=True, timeout=30).stdout
        meta = json.loads(out)
        abi = meta.get("abi", [])
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {str(e)[:100]}"}
    fns = {}
    for e in abi:
        if e.get("type") == "function":
            fns.setdefault(e["name"], []).append(e)
    names = set(fns); lnames = {n.lower() for n in names}
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(lnames & {"quote","cost","getquote","mintcost","price","getprice","mintprice"})
    free_views = sorted(names & set(FREE_VIEWS))
    agent_ref = bool(lnames & {"agentid","agentregistry","registry","getagentid","agentgate","agentidregistry"})
    is_token = bool(names & {"name","symbol","decimals","totalSupply"})
    mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
    s1 = has_mint and has_quote and bool(free_views) and agent_ref
    s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
    is_nft = bool(names & {"tokenURI","ownerOf","safeTransferFrom"}) or "uri" in names
    free_mint_fn = bool(names & {"freeMint","mintFree","claimFree"}) or any(n.lower().startswith("freemint") for n in names)
    early_shape = is_nft and (agent_ref or free_mint_fn)
    return {"address": addr, "S1": s1, "S2": s2, "early_shape": early_shape,
            "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
            "agent_ref": agent_ref, "is_token": is_token, "is_nft": is_nft, "n_fns": len(abi)}
res = [shape(a) for a in ADDRS]
for r in res:
    print(r.get("address"), "| S1=", r.get("S1"), "S2=", r.get("S2"), "early=", r.get("early_shape"),
          "| mint=", r.get("has_mint"), "quote=", r.get("has_quote"), "free=", r.get("free_views"),
          "agent=", r.get("agent_ref"), "nft=", r.get("is_nft"), "n_fns=", r.get("n_fns"), "| err=", r.get("error"))
json.dump(res, open(BASE + "run-2026-11-12-2331-retry.json", "w"), indent=1)
