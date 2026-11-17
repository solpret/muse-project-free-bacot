#!/usr/bin/env python3
"""Hot-leg run 2026-11-09 07:09 WIB: shape-check 9 NEW Sourcify feed contracts.
Reuses classification logic from feed_shape_0001.py. Read-only."""
import json, time, urllib.request, urllib.error

FREE_SHARE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
                    "freeused", "freeavailable", "freesharepoolexhausted",
                    "freesharesclaimed", "freeminted", "freeremaining",
                    "free_slots", "free_supply", "free_amount"]
QUOTE_FNS = ["quote", "quotefor", "quotemint", "quotemintfor", "cost", "costfor",
             "getcost", "price", "mintprice", "feefor"]
GATE_WORDS = ["agentid", "agentregistry", "agentgate", "hasagentid", "isagent"]

NEW = [
 ("0xaFccf89418b021e1C1f9AF121608c0Cf35703a48", "2026-11-09T00:04:18Z"),
 ("0xC73758Cc9231E94413a12f31C39A80830BA21E33", "2026-11-09T00:04:08Z"),
 ("0xe00f6949f6ECCC0e37096dAc2bA41a94615E4b0a", "2026-11-09T00:03:48Z"),
 ("0x2c38Ff05B81D97B36ce285068741BB23d630F23F", "2026-11-09T00:03:32Z"),
 ("0x777D1731Eb2586ee470d88FEd03C82Df2dD697dd", "2026-11-09T00:03:02Z"),
 ("0x7368DB9f7E99e5Ee08CD7FdB5Ce1F8DCF0EA3d27", "2026-11-09T00:02:48Z"),
 ("0x7f57e301b9a12B507534f731340D1A789e932ae1", "2026-11-09T00:02:23Z"),
 ("0x1B8F7a46830Ca7d51db19eE1f678Bfa39Bec3dA4", "2026-11-09T00:02:12Z"),
 ("0x342b307387325D9476D276Ee096A3d8CdBFb70B6", "2026-11-09T00:02:00Z"),
]

def sourcify_abi(address, tries=3):
    url = f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"
    for i in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode())
                return ("verified", data.get("abi"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ("not_verified", None)
            time.sleep(3)
        except Exception:
            time.sleep(3)
    return ("error:retry-exhausted", None)

def classify(abi):
    funcs = []
    if isinstance(abi, list):
        for item in abi:
            if item.get("type") == "function":
                funcs.append(item.get("name", ""))
    mint_fns = [f for f in funcs if "mint" in f.lower()]
    quote_fns = [f for f in funcs if f.lower() in QUOTE_FNS or f.lower().startswith("quote") or f.lower().startswith("cost")]
    free_views = [f for f in funcs if f.lower() in FREE_SHARE_VIEWS]
    gate = [f for f in funcs if any(g in f.lower() for g in GATE_WORDS)]
    token_fns = [f for f in funcs if f.lower() in ("name", "symbol", "decimals", "totalsupply")]
    noarg_free = [f for f in funcs if f.lower() in ("mintfree", "claimfree")]
    s1 = bool(mint_fns) and bool(quote_fns) and bool(free_views) and bool(gate)
    s2 = len(token_fns) >= 3 and bool(noarg_free) and bool(free_views) and bool(gate)
    return {"functions": len(funcs), "mint_fns": mint_fns, "quote_fns": quote_fns,
            "free_views": free_views, "gate_fns": gate, "token_fns": token_fns,
            "S1": s1, "S2": s2}

out = []
for addr, vat in NEW:
    r = {"address": addr, "verifiedAt": vat}
    status, abi = sourcify_abi(addr)
    r["sourcify"] = status
    if abi is not None:
        r.update(classify(abi))
    else:
        r["S1"] = False; r["S2"] = False
    out.append(r)
    print(addr, vat, r["sourcify"], "S1=" + str(r.get("S1")), "S2=" + str(r.get("S2")),
          "mint=" + str(r.get("mint_fns")), "quote=" + str(r.get("quote_fns")),
          "free=" + str(r.get("free_views")), "gate=" + str(r.get("gate_fns")),
          "token=" + str(r.get("token_fns")))
json.dump(out, open("hot-leg-0709-shape.json", "w"), indent=1)
print("S1 pass:", [o["address"] for o in out if o.get("S1")])
print("S2 pass:", [o["address"] for o in out if o.get("S2")])
