#!/usr/bin/env python3
"""Route 5c shape-check for run 2026-11-07-1031: 4 new ERC-20 backlog
candidates (mint_count>=10, not in track-c-scan-checked.json union).
Same S1/S2 test as route 5a (incl. registry-bytes check). Read-only."""
import json
import sys
import urllib.request
import urllib.error

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single  # noqa: E402

REGISTRY_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/"]
FREE_SHARE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
                    "freeused", "freeavailable", "freesharepoolexhausted",
                    "freesharesclaimed", "freeminted", "freeslots", "freesupply"]
QUOTE_FNS = ["quote", "cost", "price", "getprice", "mintprice", "mintcost"]
CANDIDATES = [
    ("0xAC258FC0c9F0B45AAB391eA462F4ff2df589fEcc", 30, 3, 132133086),
    ("0x039BBc2cAA3eF358890336EB47ebBfca7EaF751b", 19, 12, 132132549),
    ("0xC55967cC0A829eAcB1764A46b7eCC784B0fDeE39", 16, 7, 132132472),
    ("0x62266654ac9BBb8D24e8573a78aCf3a083902ffA", 15, 6, 132132631),
]


def sourcify_abi(address):
    url = f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return ("verified", json.loads(resp.read().decode()).get("abi"))
    except urllib.error.HTTPError as e:
        return ("not_verified" if e.code == 404 else f"http_{e.code}", None)
    except Exception as e:  # noqa: BLE001
        return (f"error:{type(e).__name__}", None)


def rpc_call(method, params, timeout=8):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:  # noqa: BLE001
            last = e
    raise last


def main():
    results = []
    for addr, mc, minters, first in CANDIDATES:
        status, abi = sourcify_abi(addr)
        names = []
        if isinstance(abi, list):
            names = [it.get("name", "") for it in abi if it.get("type") == "function"]
        lower = [n.lower() for n in names]
        has_mint = any("mint" in n for n in lower)
        has_quote = any(any(q in n for q in QUOTE_FNS) for n in lower)
        free_views = [n for n in names if n.lower() in FREE_SHARE_VIEWS]
        gate_names = [n for n in names
                      if "agentregistry" in n.lower() or "agentgate" in n.lower()
                      or "agentid" in n.lower() or n.lower() == "agent_id_registry"]
        reg_bytes = False
        try:
            code = rpc_call("eth_getCode", [addr, "latest"])
            if isinstance(code, str) and len(code) > 2:
                reg_bytes = REGISTRY_BYTES in code[2:].lower()
        except Exception as e:  # noqa: BLE001
            reg_bytes = f"error:{e}"
        registry_ref = bool(gate_names) or reg_bytes is True
        s1 = has_mint and has_quote and bool(free_views) and registry_ref
        token_fns = {"name", "symbol", "decimals", "totalsupply"}
        has_token = token_fns <= set(lower)
        noarg_free_mint = False
        if isinstance(abi, list):
            for f in abi:
                if f.get("type") == "function" and f.get("name", "").lower() in (
                        "mintfree", "freemint", "claimfree", "mintfreeshare"):
                    if len(f.get("inputs", [])) == 0:
                        noarg_free_mint = True
        s2 = has_token and noarg_free_mint and bool(free_views) and registry_ref
        rec = {"address": addr, "mint_count": mc, "distinct_minters": minters,
               "first_block": first, "sourcify": status, "has_mint": has_mint,
               "has_quote": has_quote, "free_views": free_views,
               "gate_names": gate_names, "registry_bytes": reg_bytes,
               "S1": s1, "S2": s2}
        results.append(rec)
        print(f"{addr} mints={mc} sourcify={status} mint={has_mint} quote={has_quote} "
              f"free={free_views} gate={gate_names} reg_bytes={reg_bytes} S1={s1} S2={s2}",
              flush=True)
    json.dump(results, open("trackc-5c-1031.json", "w"), indent=1)
    print(f"5c HITS: {sum(1 for r in results if r['S1'] or r['S2'])} of {len(results)}")


if __name__ == "__main__":
    main()
