#!/usr/bin/env python3
"""Second-pass ABI probe for free-mint-search run 2026-11-14 02:01 WIB.
The v2/contract endpoint without ?fields=abi returns match metadata only, so
pass 1 reported fns=0. This pass fetches ?fields=abi for the same 15 feed
contracts and classifies mint/free/quote/agentgate functions. Read-only."""
import json, subprocess, time, re
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDRS = [
 "0xfB70c26dE2AA5fB02Fa2342EaDe5c32Fbf875E8E",
 "0x8b7aB23DCB21A1209b821Da1d53f93E12b667C95",
 "0x9025871F606Dc6dAc15aE331DB83ff5Cd83557A7",
 "0x027FFe566B1F3f9Bb3Ddbd835DD01d0b62Af9DB7",
 "0x3811e5Fc190589764d2653A5E6fC16B4080Fc4DE",
 "0x9a266cceA08d3E8628224Cb68bc240fEd47b1E76",
 "0x0FA947aE540F35b782e4eF35B43fAD5284DEc3d1",
 "0x5e8A8a4A3ebFde53afcb50722F82359E3586D0bd",
 "0xfF172b79d040faefA1Bf34B47151edc87130246E",
 "0x76E0471d81D1D4027046b8d381E6a064CeC9c0e4",
 "0x8b5ca265B7FAf150839E9ab47D1354f245868c5e",
 "0x4a2A838eeCf26614C25886281FAF1b54683660bc",
 "0x0d29a23fe8C6AFAFD2237CbF812a5b1D7FE6ab44",
 "0x2f0980Ad16A96f7287087E242259736ab59e6531",
 "0x912DcAfaF5114A888D60f58B3A5141c67Cc5FAD5",
]
t0 = time.time()
FREE_PAT = re.compile(r"free|FREE")
MINT_PAT = re.compile(r"mint|claim", re.I)
QUOTE_PAT = re.compile(r"quote|cost|price", re.I)
results = {}
for a in ADDRS:
    row = {"address": a}
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "30",
                            f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"],
                           capture_output=True, text=True, timeout=35)
        d = json.loads(r.stdout)
        abi = d.get("abi") or []
        fns = [x.get("name", "") for x in abi if isinstance(x, dict) and x.get("type") == "function"]
        row["verified"] = True
        row["fn_count"] = len(fns)
        row["fns"] = fns
        row["has_mint"] = any(MINT_PAT.search(f) for f in fns)
        row["has_free_view"] = any(FREE_PAT.search(f) for f in fns)
        row["has_quote"] = any(QUOTE_PAT.search(f) for f in fns)
        row["has_agentgate"] = any("agent" in f.lower() or "gate" in f.lower() for f in fns)
        row["has_registry_getter"] = any(f in ("agentRegistry", "registry", "agentIdRegistry", "AGENT_ID") for f in fns)
        row["is_erc721_1155"] = any(f in ("totalSupply", "tokenURI", "ownerOf", "balanceOf") for f in fns)
        row["is_erc20"] = any(f in ("decimals", "totalSupply", "transfer") for f in fns) and "name" in fns and "symbol" in fns
    except Exception as e:
        row["verified"] = False
        row["error"] = str(e)[:150]
        row["fns"] = []
    results[a] = row
    print(a, "verified" if row.get("verified") else "NOT_VERIFIED",
          "fns", row.get("fn_count"), "mint", row.get("has_mint"),
          "free", row.get("has_free_view"), "quote", row.get("has_quote"),
          "agentgate", row.get("has_agentgate"), "regGetter", row.get("has_registry_getter"),
          "721/1155", row.get("is_erc721_1155"), "ERC20", row.get("is_erc20"),
          "FN:", ",".join(row.get("fns", [])[:12]), flush=True)
json.dump({"run": "2026-11-14-0201", "elapsed_s": round(time.time() - t0, 1),
           "results": results},
          open(BASE + "run-2026-11-14-0201-probe-feed-abi.json", "w"), indent=1)
print("DONE elapsed", round(time.time() - t0, 1))
