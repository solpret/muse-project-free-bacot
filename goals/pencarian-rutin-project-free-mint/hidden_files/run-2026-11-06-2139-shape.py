#!/usr/bin/env python3
"""Hot-leg run 2139: Leg 1 Sourcify shape-check for 19 new feed contracts.
Concurrent ABI fetch; S1/S2 classification per body. Read-only; writes
run-2026-11-06-2139-sourcify-shape.json. Target fast."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2139"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
REG_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "freeminted", "freeremaining"]
GATE_WORDS = ["agentid", "agentregistry", "agentgate", "hasagentid", "isagent"]
QUOTE_FNS = ["quote", "quotefor", "quotemint", "cost", "costfor", "getcost",
             "price", "mintprice", "feefor"]

ADDRS = [
 "0x5b5037553E3DaCDE2b7f7a18735cebc7D13538cE",
 "0xD3178991D5Ee676a2e2d67bb286582bB973e73C3",
 "0x365C153a2148038411ade7c6923CE0A3b2C66B26",
 "0x50edeBD16d86f931CA37617ca0906595961b8C8c",
 "0xAe343d6B6A20f528DF32d2617c622c49fD0892E9",
 "0x6aC1131e0eD37f139f4917018950093cB611A3D0",
 "0x845Ca5298D099E87113ACb9d6385d5adc3edd765",
 "0x0966A4c9C8B82D2da4d4812AFee4f33D24ae4518",
 "0xE7a080311c891643A297eA674DA1AF9e22642F19",
 "0x24CD4aa07C38A17395895d791D1675AE4F03f100",
 "0x298E445775E27134b90b08CDe5Addece6005d3eC",
 "0xc587e18919A3e101F4d576db7A4Bec5b363b814F",
 "0xf4C6bc66a3aA936A4DAf7BF10454193325Ef5714",
 "0x02D8dAD9a863f57C1F06E1bea1f2f32252F3F2C9",
 "0x7fe03C055588bd5018825175D791103c5CBEd8be",
 "0xBfeD79C1AB445fdf8afec956fb1c75e11a77f3aB",
 "0xBfE2790CBE0Cf0363607633c1A9Ae6A1304e2Bd5",
 "0x91c139A516515a51Ad8d745B833eD8de53BA634C",
 "0x9e2738B3DD3773c6c71cA24Fbc92660B501C0B6b",
]

def fetch_abi(addr):
    for fields in ("abi", "metadata"):
        try:
            r = subprocess.run(["curl", "-s", "--max-time", "15",
                f"https://sourcify.dev/server/v2/contract/56/{addr}?fields={fields}"],
                capture_output=True, text=True, timeout=20)
            d = json.loads(r.stdout)
            abi = d.get("abi")
            if abi is None and isinstance(d.get("metadata"), dict):
                abi = d["metadata"].get("output", {}).get("abi")
            if isinstance(abi, list):
                return ("verified", abi)
            if d.get("match") or d.get("stdJson"):
                return ("verified-no-abi", None)
        except Exception:
            continue
    return ("fetch-failed", None)

def classify(addr):
    st, abi = fetch_abi(addr)
    r = {"address": addr, "sourcify": st}
    if not isinstance(abi, list):
        r["verdict"] = "abi-unavailable"
        return r
    fns = [f.get("name", "") for f in abi if isinstance(f, dict) and f.get("type") == "function"]
    low = [f.lower() for f in fns]
    norm = [f.replace("_", "") for f in low]
    has_mint = any("mint" in f for f in low)
    has_quote = any(any(q in f for q in QUOTE_FNS) for f in low)
    free_views = [f for f in low if any(w in f.replace("_", "") for w in FREE_VIEWS)]
    gate = [f for f in norm if any(g in f for g in GATE_WORDS)]
    registry_in_abi = REG.lower() in json.dumps(abi).lower()
    is_nft = any(f in low for f in ("ownerof", "tokenuri"))
    is_token = all(f in low for f in ("name", "symbol", "decimals", "totalsupply"))
    mint_free_noarg = any(f.get("name") == "mintFree" and len(f.get("inputs", [])) == 0
                          for f in abi if isinstance(f, dict))
    free_slots = any("free_slots" in f or "free_supply" in f or "freeslots" in f.replace("_", "")
                     or "freesupply" in f.replace("_", "") for f in low)
    free_claimed_views = any(f in low for f in ("freeclaimed", "freeminted"))
    s1 = has_mint and has_quote and bool(free_views) and (bool(gate) or registry_in_abi)
    s2 = is_token and mint_free_noarg and free_claimed_views and free_slots and (bool(gate) or registry_in_abi)
    r.update({"fns": len(fns), "mint_fns": [f for f in fns if "mint" in f.lower()],
              "quote_fns": [f for f in fns if any(q in f.lower() for q in QUOTE_FNS)],
              "free_views": free_views, "gate_fns": gate,
              "registry_in_abi": registry_in_abi, "is_nft": is_nft,
              "is_token": is_token, "mintFree_noarg": mint_free_noarg,
              "S1": s1, "S2": s2,
              "verdict": ("S1-PASS" if s1 else "S2-PASS" if s2 else "not-sale-shape")})
    return r

t0 = time.time()
with ThreadPoolExecutor(max_workers=8) as ex:
    results = list(ex.map(classify, ADDRS))
out = {r["address"]: r for r in results}
json.dump(out, open(f"{BASE}/run-{TS}-sourcify-shape.json", "w"), indent=1)
for r in results:
    print(r["address"], r["verdict"], "sourcify=" + r["sourcify"],
          "mint=" + str(r.get("mint_fns")), "quote=" + str(r.get("quote_fns")),
          "free=" + str(r.get("free_views")), "gate=" + str(r.get("gate_fns")),
          "nft=" + str(r.get("is_nft")), "token=" + str(r.get("is_token")))
print("ELAPSED", round(time.time() - t0, 1))
