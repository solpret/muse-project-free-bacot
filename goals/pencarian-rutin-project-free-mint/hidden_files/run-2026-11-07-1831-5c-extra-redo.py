#!/usr/bin/env python3
"""Run 1831 parent redo: correct Sourcify endpoint /v2/contract/56/{addr}?fields=abi.
5c-extra for 9 ERC20 + metadata URL check (method C) for DinoAgent/Tri333.
Read-only except own output."""
import json, urllib.request
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeMint","isFreeMintAvailable"]

def fetch(addr, fields="abi"):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields={fields}"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.loads(resp.read().decode())

out = {}
erc20 = ["0x5D28C44bAd17d75D2207C4A042b73AF5297971C2","0x62926C83729fB7d54b211C2dd9D5A9116be38a87",
"0x68Cf8Eb34F99d8c86F9E5518B9b5Cea45b1Bb889","0x2760e5D359EB84512207A91C02E2eC29fd30a1b2",
"0x71E8639b242FFaf9e2a5ab0247FaacD17E25eE4E","0x54Ff11c7a6850a442E0029Bd454ef000e5131191",
"0x28a4F0BbdC1bE886f9e5a290e6598A83F248B224","0xD89651A8B8B79C7F65543Dd428837b98D63ba60E",
"0x597bE001b48891620Da1440CdfA82D08297dfB45"]
res = []
for a in erc20:
    try:
        d = fetch(a)
        abi = d.get("abi", [])
        names = [f.get("name","") for f in abi if isinstance(f, dict)]
        has_mint = any(n in ("mint","mintFree","mintPaid") for n in names)
        has_quote = any(("rice" in n) or ("quote" in n.lower()) or n in ("currentPriceFor","price") for n in names)
        has_free = [n for n in names if n in FREE_VIEWS]
        src_text = json.dumps(d.get("stdJson",{}).get("sources",{}))
        has_reg = REG.lower() in src_text.lower() or any(
            n in ("agentRegistry","AGENT_ID_REGISTRY","agentIdRegistry","AGENT_ID") for n in names)
        is_token = all(n in names for n in ("name","symbol","decimals","totalSupply"))
        res.append({"address": a, "verified": True, "match": d.get("match"),
                    "S1": bool(has_mint and has_quote and has_free and has_reg),
                    "S2": bool(is_token and "mintFree" in names and has_free and has_reg),
                    "detail": {"mint": has_mint, "quote": has_quote, "free_views": has_free,
                               "registry": has_reg, "is_token": is_token, "abi_fns": len(names)}})
    except Exception as ex:
        res.append({"address": a, "verified": False, "error": str(ex)[:150]})
out["track_c_5c_extra_redo"] = res
# Method (C) Sourcify metadata for DinoAgent + Tri333: look for URLs in sources/metadata
for label, addr in [("DinoAgent","0xcE19D6A5FF15e088D4bf23614242927139084895"),
                    ("Tri333","0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f")]:
    try:
        d = fetch(addr, fields="abi,metadata")
        blob = json.dumps(d)
        import re
        urls = sorted(set(re.findall(r"https?://[A-Za-z0-9\-._~:/?#@!$&'()*+,;=%]+", blob)))
        out[label+"_sourcify"] = {"verified": True, "match": d.get("match"),
                                  "urls_in_metadata": [u for u in urls if "sourcify" not in u][:10]}
    except Exception as ex:
        out[label+"_sourcify"] = {"verified": False, "error": str(ex)[:150]}
json.dump(out, open(f"{BASE}/run-2026-11-07-1831-5c-extra-redo.json","w"), indent=1)
print(json.dumps(out, indent=1))
