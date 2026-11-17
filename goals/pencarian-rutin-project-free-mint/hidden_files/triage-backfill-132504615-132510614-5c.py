#!/usr/bin/env python3
"""Track-C 5c shape-check for the parallel backfill run 132504615-132510614.

Takes ERC20 contracts with mint_count>=10 from the three chunk JSONs,
dedupes by address (max mint_count kept), skips already-checked, shape-
checks up to 20 new ones (Sourcify ABI sale-shape S1/S2 + registry bytes),
prints verdicts, and records newly checked addresses in
track-c-scan-checked.json (same format as the existing file).
Read-only except appending the checked list.
"""
import json
import sys
import subprocess
import urllib.request

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
REGISTRY_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ("freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "freeminted", "freeslots", "freesupply")


def rpc_call(method, params, timeout=8):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:  # noqa: BLE001
            last = e
    raise last


def sourcify_abi(address):
    url = f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return ("verified", data.get("abi"))
    except urllib.error.HTTPError as e:
        return ("not_verified" if e.code == 404 else f"http_{e.code}", None)
    except Exception as e:  # noqa: BLE001
        # curl fallback (urllib IncompleteRead/RemoteDisconnected seen before)
        try:
            import subprocess
            r = subprocess.run(["curl", "-s", "-m", "20", "-A", "Mozilla/5.0", url],
                               capture_output=True, text=True, timeout=30)
            data = json.loads(r.stdout)
            if isinstance(data.get("abi"), list):
                return ("verified", data.get("abi"))
            return ("no-abi", None)
        except Exception:
            return (f"error:{type(e).__name__}", None)


def main():
    checked_path = f"{BASE}/track-c-scan-checked.json"
    checked = json.load(open(checked_path))
    if isinstance(checked, dict):
        # dual structure: sub-dict "checked" + top-level address keys
        sub = checked.get("checked", {})
        checked_set = {k.lower() for k in sub}
        checked_set |= {k.lower() for k in checked if k.startswith("0x")}
        fmt = "dict"
    else:
        checked_set = {str(x).lower() for x in checked}
        fmt = "list"

    best = {}
    for f in ["backfill-132504615-132506614.json",
              "backfill-132506615-132508614.json",
              "backfill-132508615-132510614.json"]:
        r = json.load(open(f"{BASE}/{f}"))
        for e in r["erc20_mint_contracts_list"]:
            if e["mint_count"] < 10:
                continue
            key = e["address"].lower()
            if key not in best or e["mint_count"] > best[key]["mint_count"]:
                best[key] = e
    cands = sorted(best.values(), key=lambda e: -e["mint_count"])
    new = [e for e in cands if e["address"].lower() not in checked_set][:20]
    print(f"5c: {len(cands)} unique >=10, {len(new)} new to check (cap 20)")
    hits = []
    for e in new:
        addr = e["address"]
        status, abi = sourcify_abi(addr)
        fns = []
        if isinstance(abi, list):
            fns = [x.get("name", "") for x in abi if x.get("type") == "function"]
        lower = [f.lower() for f in fns]
        has_mint = any("mint" in f for f in lower)
        has_quote = any(f in ("quote", "cost", "costof", "getcost", "price",
                              "mintcost", "mintprice") for f in lower)
        free_views = [f for f in lower if f in FREE_VIEWS]
        is_token = all(x in lower for x in ("name", "symbol", "decimals",
                                            "totalsupply"))
        no_arg_free = False
        if isinstance(abi, list):
            for x in abi:
                if x.get("type") == "function" and x.get("name", "").lower() in (
                        "mintfree", "freemint", "claimfree"):
                    if not x.get("inputs"):
                        no_arg_free = True
        code = None
        try:
            code = rpc_call("eth_getCode", [addr, "latest"], timeout=5)
        except Exception:  # noqa: BLE001
            pass
        registry_hit = (REGISTRY_BYTES in code[2:].lower()
                        if isinstance(code, str) and len(code) > 2 else None)
        s1 = has_mint and has_quote and bool(free_views) and bool(registry_hit)
        s2 = (is_token and no_arg_free and bool(free_views)
              and bool(registry_hit))
        verdict = "S1-HIT" if s1 else ("S2-HIT" if s2 else "no-shape")
        if s1 or s2:
            hits.append(addr)
        print(f"{addr} mints={e['mint_count']} minters={e['distinct_minters']} "
              f"sourcify={status} registry={registry_hit} mint={has_mint} "
              f"quote={has_quote} free_views={free_views} token={is_token} "
              f"no_arg_free={no_arg_free} -> {verdict}", flush=True)
    print(f"5c DONE: {len(new)} checked, {len(hits)} sale-shape hits: {hits}")
    # Record newly checked addresses as top-level keys (recent-run format).
    if fmt == "dict":
        for e in new:
            checked[e["address"]] = e["first_block"]
    else:
        checked.extend(e["address"] for e in new)
    with open(checked_path, "w") as f:
        json.dump(checked, f, indent=1)
    print(f"recorded {len(new)} addresses in track-c-scan-checked.json "
          f"(total now {len(checked)})")


if __name__ == "__main__":
    main()
