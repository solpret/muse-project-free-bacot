#!/usr/bin/env python3
"""Fresh ONLYAI Crystals check, run 0331: totalSupply + free views + user slot.
Read-only eth_call via bsc-dataseed. A revert/empty = view absent, never zero."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ONLYAI = "0x156482ad3f0eebd8e3f70d494ebd1da3f738f5ba"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def call(data, label):
    for ep in EPS:
        try:
            r = _single(ep, "eth_call", [{"to": ONLYAI, "data": data}, "latest"], 10, retries=0)
            return r
        except Exception as e:
            last = e
    return f"ERROR:{last}"

def u256(hexstr):
    if not isinstance(hexstr, str) or not hexstr.startswith("0x") or hexstr == "0x":
        return None
    try:
        return int(hexstr, 16)
    except Exception:
        return None

def main():
    out = {"contract": ONLYAI, "user": USER}
    # no-arg views
    for sig in ["totalSupply()", "MAX_SUPPLY()", "FREE_SUPPLY()", "freeSupply()",
                "freeMinted()", "freeClaimed()", "freeLeft()", "totalMinted()",
                "totalPaid()", "name()", "symbol()"]:
        r = call(sel(sig), sig)
        out[sig] = {"raw": r, "value": u256(r) if sig not in ("name()", "symbol()") else r}
        print(f"{sig}: {r} -> {out[sig]['value']}")
    # address-arg views
    padded = "0" * 24 + USER[2:].lower()
    for sig in ["freeClaimed(address)", "freeMintedBy(address)", "hasFreeMint(address)",
                "freeFor(address)", "balanceOf(address)"]:
        r = call(sel(sig) + padded, sig)
        out[sig] = {"raw": r, "value": u256(r)}
        print(f"{sig}(user): {r} -> {out[sig]['value']}")
    # quote(address,uint256) for 1
    data = sel("quote(address,uint256)") + padded + "0" * 63 + "1"
    r = call(data, "quote")
    out["quote(address,1)"] = {"raw": r, "value": u256(r)}
    print(f"quote(user,1): {r} -> {out['quote(address,1)']['value']}")
    json.dump(out, open("run-2026-11-07-0331-onlyai-check.json", "w"), indent=1)
    print("written run-2026-11-07-0331-onlyai-check.json")

if __name__ == "__main__":
    main()
