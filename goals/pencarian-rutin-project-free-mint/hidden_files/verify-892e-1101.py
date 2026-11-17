#!/usr/bin/env python3
"""Verify track-C S1 hit 0x892E438425b3A41BC75b25C22Fd878b3fa2e308d on-chain
(run 2026-11-07-1031, route 5a). Read-only eth_calls via fast_rpc.
User wallet: 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E (main wallet)."""
import json
import sys
import urllib.request

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single  # noqa: E402

ADDR = "0x892E438425b3A41BC75b25C22Fd878b3fa2e308d"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]


def rpc_call(method, params, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:  # noqa: BLE001
            last = e
    raise last


def keccak_selector(sig):
    from Crypto.Hash import keccak
    k = keccak.new(digest_bits=256)
    k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]


def call(fn_sig, args_hex=b"", timeout=10):
    data = keccak_selector(fn_sig) + args_hex.hex() if isinstance(args_hex, bytes) else keccak_selector(fn_sig) + args_hex
    return rpc_call("eth_call", [{"to": ADDR, "data": data}, "latest"], timeout)


def u256(x):
    return int(x, 16) if isinstance(x, str) else None


def addr_arg(a):
    return a[2:].lower().rjust(64, "0")


def u256_arg(n):
    return format(n, "064x")


def main():
    req = urllib.request.Request(
        f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi",
        headers={"User-Agent": "Mozilla/5.0"})
    abi = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())["abi"]
    fns = {}
    for it in abi:
        if it.get("type") == "function":
            sig = it["name"] + "(" + ",".join(i["type"] for i in it.get("inputs", [])) + ")"
            fns[it["name"]] = (sig, it)
    print("functions:")
    for name, (sig, it) in sorted(fns.items()):
        outs = ",".join(o["type"] for o in it.get("outputs", []))
        print(f"  {sig} -> {outs}")
    out = {}
    # no-arg views
    for name in ["AGENT_ID_REGISTRY", "AGENT_PRICE_PER_SHARE", "FREE_PER_AGENT",
                 "MAX_PER_TX", "MAX_PER_WALLET", "MAX_SHARES", "PRICE_PER_SHARE",
                 "TOKENS_PER_SHARE", "sharesSold", "totalSupply", "name", "symbol",
                 "decimals", "treasury"]:
        if name in fns:
            try:
                r = call(fns[name][0])
                out[name] = r
                print(f"{name} = {r}")
            except Exception as e:  # noqa: BLE001
                print(f"{name} ERROR: {e}")
                out[name] = f"ERROR:{e}"
    # user-scoped views
    for name in ["freeUsed", "isAgent", "mintedBy", "balanceOf"]:
        if name in fns:
            sig = fns[name][0]
            n_inputs = len(fns[name][1].get("inputs", []))
            try:
                if n_inputs == 1:
                    r = call(sig, addr_arg(USER))
                    print(f"{name}(user) = {r}")
                    out[name + "(user)"] = r
                else:
                    print(f"{name}: {n_inputs} inputs, skipped")
            except Exception as e:  # noqa: BLE001
                print(f"{name}(user) ERROR: {e}")
                out[name + "(user)"] = f"ERROR:{e}"
    # quote: try quote(address,uint256) then quote(uint256)
    if "quote" in fns:
        sig = fns["quote"][0]
        n_inputs = len(fns["quote"][1].get("inputs", []))
        print(f"quote sig: {sig} inputs={n_inputs}")
        try:
            if n_inputs == 2:
                r = call(sig, addr_arg(USER) + u256_arg(1))
            elif n_inputs == 1:
                r = call(sig, u256_arg(1))
            else:
                r = call(sig)
            print(f"quote(1 share) = {r}")
            out["quote(1)"] = r
        except Exception as e:  # noqa: BLE001
            print(f"quote ERROR: {e}")
            out["quote(1)"] = f"ERROR:{e}"
    json.dump(out, open("trackc-892e-verify-1101.json", "w"), indent=1)
    # interpret
    try:
        max_shares = u256(out.get("MAX_SHARES", ""))
        sold = u256(out.get("sharesSold", ""))
        free_per = u256(out.get("FREE_PER_AGENT", ""))
        print(f"INTERPRET: MAX_SHARES={max_shares} sharesSold={sold} "
              f"FREE_PER_AGENT={free_per}")
    except Exception as e:  # noqa: BLE001
        print(f"interpret error: {e}")


if __name__ == "__main__":
    main()
