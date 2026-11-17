#!/usr/bin/env python3
"""Run 1201 retry: re-shape-check the 10 error addresses from legs via curl (handles IncompleteRead better)."""
import json, subprocess
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
def get(url):
    out = subprocess.run(["curl","-sL","--max-time","25",url], capture_output=True, text=True, timeout=30)
    if out.returncode != 0 or not out.stdout.strip():
        raise RuntimeError(f"curl rc={out.returncode} empty")
    return out.stdout
def shape(addr):
    try:
        meta = json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"))
        abi = meta.get("abi", [])
    except Exception as e:
        return {"address": addr, "status": "still-error", "error": f"{type(e).__name__}: {str(e)[:100]}"}
    fns = {}
    for e in abi:
        if e.get("type") == "function":
            fns.setdefault(e["name"], []).append(e)
    names = set(fns); lnames = {n.lower() for n in names}
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(lnames & {"quote","cost","getquote","mintcost","price","getprice","mintprice"})
    free_views = sorted(names & set(FREE_VIEWS))
    agent_ref = bool(lnames & {"agentid","agentregistry","registry","getagentid","agentgate","agentidregistry"})
    is_token = bool(names & {"name","symbol","decimals","totalSupply"}) and "transfer" in names
    mintfree = "mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
    s1 = has_mint and has_quote and bool(free_views) and agent_ref
    s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
    is_nft = bool(names & {"tokenURI","ownerOf","safeTransferFrom"}) or "uri" in names
    free_mint_fn = bool(names & {"freeMint","mintFree","claimFree"}) or any(n.lower().startswith("freemint") for n in names)
    early_shape = is_nft and (agent_ref or free_mint_fn)
    return {"address": addr, "status": "verified-now", "S1": s1, "S2": s2, "early_shape": early_shape, "n_fns": len(abi), "free_views": free_views, "agent_ref": agent_ref}
addrs = ["0x03878fD227126F459Cf7C2eC91029d01bCd1962E","0x24881Fea36d6e87df34f4fEAfE7B521d1093c163","0x2cb8F6854BB37C9FF53D791161B65bfB6515370B","0xF9f642F747372b70e7473AB359C3C68F44f5605C","0xa09fC014acDCe23315AD9956F681fBEb8C8a8F02","0xa668BdC7324A3bB09D0Ad723dBC0082E8F18eEd7","0xa707b958148a96812ceb592dfbadf739d6e7ba78","0xd0305cFb027D0e07d2fD58244dF92313aed4b384","0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045","0xdaf73524e83b92c141579b76198386d5702effe5"]
res = [shape(a) for a in addrs]
out = {"run": "2026-11-12 12:01 WIB", "retried": len(addrs),
       "now_verified": [r for r in res if r["status"]=="verified-now"],
       "still_error": [r for r in res if r["status"]!="verified-now"]}
json.dump(out, open(BASE+"run-2026-11-12-1201-retry-legs.json","w"), indent=1)
print(json.dumps(out, indent=1))
