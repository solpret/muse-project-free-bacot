#!/usr/bin/env python3
"""One-off triage for the first parallel backfill run (131915549-131921548).

Shape-checks the 16 first-seen contracts from the three chunk JSONs:
Sourcify ABI (curl), registry bytes in bytecode, free/mint function names.
Prints a compact verdict per contract so the parent can decide which (if
any) need full leg verification (quote, first-mint time, owner).
Read-only; writes nothing.
"""
import json
import subprocess
import sys
import urllib.request

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed3.bnbchain.org/"]
REGISTRY_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"


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
        return (f"error:{type(e).__name__}", None)


def main():
    addrs = []
    for f in ["backfill-131915549-131917548.json",
              "backfill-131917549-131919548.json",
              "backfill-131919549-131921548.json"]:
        r = json.load(open(f"{BASE}/{f}"))
        for c in r["first_seen"]:
            addrs.append((c["address"], c["mint_count"], c["first_block"],
                          c.get("name"), c.get("symbol")))
    print(f"TRIAGE {len(addrs)} first-seen")
    for addr, mints, first_block, name, symbol in addrs:
        code = None
        try:
            code = rpc_call("eth_getCode", [addr, "latest"], timeout=5)
        except Exception as e:  # noqa: BLE001
            code = f"ERR:{e}"
        registry_hit = None
        if isinstance(code, str) and len(code) > 2:
            registry_hit = REGISTRY_BYTES in code[2:].lower()
        status, abi = sourcify_abi(addr)
        free_funcs, mint_funcs = [], []
        if isinstance(abi, list):
            for item in abi:
                if item.get("type") != "function":
                    continue
                nm = item.get("name", "")
                if "free" in nm.lower() and not nm.lower().startswith("freeze"):
                    free_funcs.append(nm)
                if "mint" in nm.lower():
                    mint_funcs.append(nm)
        # first-mint timestamp (best-effort)
        ts = None
        try:
            blk = rpc_call("eth_getBlockByNumber",
                           [hex(first_block), False], timeout=8)
            ts = int(blk["timestamp"], 16) if blk else None
        except Exception:  # noqa: BLE001
            pass
        print(f"{addr} mints={mints} first_block={first_block} ts={ts} "
              f"name={name} symbol={symbol} registry={registry_hit} "
              f"sourcify={status} free={sorted(set(free_funcs))[:10]} "
              f"mint={sorted(set(mint_funcs))[:10]}", flush=True)


if __name__ == "__main__":
    main()
