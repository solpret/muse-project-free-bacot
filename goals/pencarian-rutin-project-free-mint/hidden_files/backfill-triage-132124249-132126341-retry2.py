#!/usr/bin/env python3
"""Second targeted retry for 0xE2b3... free path (correct selectors).
freeGranted() takes NO args; priceFor(address,uint256); mintedBy(address);
max_supply(); max_per_wallet(); name(); symbol(). Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0xE2b3D9043fccc76e6Ce13f84346735F1AA375b5a"
USER_NOPREFIX = "eb237f6f9fb4e826739f0954e9768914f28b2c2e"

def sel(sig):
    k = keccak.new(digest_bits=256)
    k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def call(data_hex, tries=5):
    last = None
    for i in range(tries):
        try:
            return race("eth_call", [{"to": ADDR, "data": data_hex}, "latest"])
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
            time.sleep(5)
    return f"ERROR {last}"

def u256(r):
    if isinstance(r, str) and r.startswith("0x") and len(r) >= 66:
        return int(r, 16)
    return f"revert-or-short: {str(r)[:200]}"

def string_call(data_hex):
    r = call(data_hex)
    if isinstance(r, str) and r.startswith("0x") and len(r) >= 130:
        try:
            ln = int(r[130:194], 16)
            return bytes.fromhex(r[194:194 + ln * 2]).decode("utf-8", "replace")
        except Exception as e:
            return f"decode-error: {e}"
    return f"revert-or-short: {str(r)[:200]}"

out = {
    "name": string_call(sel("name()")),
    "symbol": string_call(sel("symbol()")),
    "freeGranted_total": u256(call(sel("freeGranted()"))),
    "priceFor_user_1": u256(call(sel("priceFor(address,uint256)") + USER_NOPREFIX + "0" * 63 + "1")),
    "mintedBy_user": u256(call(sel("mintedBy(address)") + USER_NOPREFIX)),
    "max_supply": u256(call(sel("max_supply()"))),
    "max_per_wallet": u256(call(sel("max_per_wallet()"))),
    "totalMinted": u256(call(sel("totalMinted()"))),
    "price_paid": u256(call(sel("price_paid()"))),
}
print(json.dumps(out, indent=1))
json.dump(out, open(f"{BASE}/backfill-triage-132124249-132126341-retry2.json", "w"), indent=1)
