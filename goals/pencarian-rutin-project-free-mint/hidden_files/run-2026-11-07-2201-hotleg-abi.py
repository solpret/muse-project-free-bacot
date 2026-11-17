#!/usr/bin/env python3
"""Run 2201: (1) ABI fetch (?fields=abi) for the 2 hot-leg S1 contracts for
function lists + site-function grep (method J) + metadata URLs (method C);
(2) retry the 11 abi-unavailable contracts from the 2201 Sourcify feed.
Read-only except own output files.
"""
import json, time, urllib.request, urllib.error

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "isfreemintavailable", "freeminted",
              "free_slots", "free_supply", "freeslots", "freesupply"]
QUOTE_WORDS = ["quote", "cost", "price", "getprice", "mintprice", "mintcost"]

def get_json(url, timeout=30, tries=2):
    last = None
    for _ in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": "free-bacot/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode()), None
        except urllib.error.HTTPError as e:
            return None, f"HTTP{e.code}"
        except Exception as e:
            last = f"{type(e).__name__}:{e}"
            time.sleep(2)
    return None, last

def shape(abi):
    fns = [e for e in abi if isinstance(e, dict) and e.get("type") == "function"]
    names = [f.get("name", "").lower() for f in fns]
    name_set = set(names)
    raw = json.dumps(abi).lower()
    mint = [n for n in names if n.startswith("mint") or n in ("claim", "claimfree")]
    quote = [n for n in names if any(w in n for w in QUOTE_WORDS)]
    freev = [n for n in names if n in FREE_VIEWS]
    has_reg = REGISTRY in raw or "agentregistry" in name_set or "agentgate" in name_set
    is_token = all(x in name_set for x in ("name", "symbol", "decimals", "totalsupply"))
    noarg_free = any(f.get("name", "").lower() in ("mintfree", "claimfree")
                     and len(f.get("inputs", [])) == 0 for f in fns)
    s1 = bool(mint) and bool(quote) and bool(freev) and has_reg
    s2 = is_token and noarg_free and bool(freev) and has_reg
    site_fns = [f.get("name") for f in fns
                if any(w in f.get("name", "").lower() for w in ("website", "siteurl", "domain", "external", "uri", "url"))]
    return {"fns": len(fns), "functions": sorted(name_set), "mint": mint[:6],
            "quote": quote[:6], "free_views": freev[:8], "registry": has_reg,
            "is_token": is_token, "noarg_free": noarg_free, "S1": s1, "S2": s2,
            "site_fns": site_fns,
            "agent_mint_shape": bool(mint) and bool(freev) and has_reg}

out = {}
for addr in ["0xa46D33862124Da90385cEb58acba63718729DEe0",
             "0x2df7435f5bce0577bee213e13da68313c74d7d0b"]:
    d, err = get_json(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi")
    if d and d.get("abi") is not None:
        out[addr] = {"match": d.get("match"), "verifiedAt": d.get("verifiedAt"),
                     **shape(d["abi"])}
    else:
        # fall back: full record for metadata URLs
        full, err2 = get_json(f"https://sourcify.dev/server/v2/contract/56/{addr}")
        meta = {}
        if full:
            meta = {"match": full.get("match"), "verifiedAt": full.get("verifiedAt"),
                    "top_keys": list(full.keys()),
                    "stdJson_keys": list((full.get("stdJson") or {}).keys())[:10],
                    "metadata_keys": list((full.get("metadata") or {}).keys())}
        out[addr] = {"abi_error": err, "full_error": err2, "metadata": meta}
    print(addr, json.dumps(out[addr])[:500], flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-07-2201-hotleg-abi.json", "w"), indent=1)

# retry abi-unavailable feed contracts
retry = ["0x007A27aB17597D1FD23Cf5C48dE55340560b763F",
         "0xFDd21Bad4Fe203BE41dc3c00f91EafED7706daF5",
         "0x3bfA1E7B4FF086Cb4744A038173E1e36D3AAA3d1",
         "0xD5A60C03Cf50Fc95d5393CA31F388A3986BF2900",
         "0xD826883c65Bd3B760Ee1B0720C8C31CC2B177777",
         "0x9293756219863F27Daa1363C7BB92C3b3874Ac2b",
         "0x97D6115e60a6EE8bC5Ce7ab35558254900D72a61",
         "0x61f70EF7cb25Fc8D0E977064cf346947A439353d",
         "0x50D8f4103b0e78CD5b3FE41B7f36F5116Be17777",
         "0x39D66D947BdB4140cf5b7c1bAEe638B962c70FD5",
         "0x8D3DFdB8ae1A748d83266A47987Fd804a4ff2a98",
         "0xF72dCf2BC47dBB5dEA0F4650808e7b90922447ff"]
rout = {"retried": [], "hits": []}
for addr in retry:
    d, err = get_json(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi")
    if d and d.get("abi") is not None:
        s = shape(d["abi"])
        s["address"] = addr
        s["verifiedAt"] = d.get("verifiedAt")
        rout["retried"].append(s)
        if s["S1"] or s["S2"] or s["agent_mint_shape"]:
            rout["hits"].append(s)
    else:
        rout["retried"].append({"address": addr, "error": err, "shape": "abi-unavailable-retry"})
    print(addr, "retry:", json.dumps(rout["retried"][-1])[:300], flush=True)
json.dump(rout, open(f"{BASE}/run-2026-11-07-2201-sourcify-retry.json", "w"), indent=1)
print("done", flush=True)
