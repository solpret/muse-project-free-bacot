#!/usr/bin/env python3
"""Retry free-path verification for 0xE2b3... (first-seen backfill 132124249-132126341).
RPC transport failed during triage (all fast_rpc endpoints failed on eth_call).
Read-only; writes backfill-triage-132124249-132126341-retry.json."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0xE2b3D9043fccc76e6Ce13f84346735F1AA375b5a"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_NOPREFIX = USER[2:].lower()

def sel(sig):
    k = keccak.new(digest_bits=256)
    k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def call(data_hex, tries=3):
    last = None
    for i in range(tries):
        try:
            return race("eth_call", [{"to": ADDR, "data": data_hex}, "latest"])
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
            time.sleep(3)
    return f"ERROR {last}"

def u256(r):
    if isinstance(r, str) and r.startswith("0x") and len(r) >= 66:
        return int(r, 16)
    return f"revert-or-short: {str(r)[:160]}"

def string_call(data_hex):
    r = call(data_hex)
    if isinstance(r, str) and r.startswith("0x") and len(r) >= 130:
        try:
            ln = int(r[130:194], 16)
            raw = bytes.fromhex(r[194:194 + ln * 2])
            return raw.decode("utf-8", "replace")
        except Exception as e:
            return f"decode-error: {e} raw={str(r)[:160]}"
    return f"revert-or-short: {str(r)[:160]}"

out = {}
out["name"] = string_call(sel("name()"))
out["symbol"] = string_call(sel("symbol()"))
out["free_quota"] = u256(call(sel("free_quota()")))
out["freeGranted_user"] = u256(call(sel("freeGranted(address)") + USER_NOPREFIX))
out["max_per_wallet"] = u256(call(sel("max_per_wallet()")))
out["max_supply"] = u256(call(sel("max_supply()")))
out["totalMinted"] = u256(call(sel("totalMinted()")))
out["mintedBy_user"] = u256(call(sel("mintedBy(address)") + USER_NOPREFIX))
out["priceFor_user_1"] = u256(call(sel("priceFor(address,uint256)") + USER_NOPREFIX + "0" * 63 + "1"))
out["price_paid"] = u256(call(sel("price_paid()")))
out["agentRegistry"] = call(sel("agentRegistry()"))
if isinstance(out["agentRegistry"], str) and out["agentRegistry"].startswith("0x") and len(out["agentRegistry"]) >= 66:
    out["agentRegistry"] = "0x" + out["agentRegistry"][-40:]
out["owner"] = call("0x8da5cb5b")
if isinstance(out["owner"], str) and out["owner"].startswith("0x") and len(out["owner"]) >= 66:
    out["owner"] = "0x" + out["owner"][-40:]
# mint() signature from ABI: check inputs via sourcify ABI
import subprocess
try:
    r = subprocess.run(["curl", "-s", "-m", "25", "-A", "free-bacot-backfill-triage/1.0",
                        f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi"],
                       capture_output=True, text=True, timeout=40)
    abi = json.loads(r.stdout).get("abi", [])
    mint = [e for e in abi if e.get("type") == "function" and e.get("name") == "mint"]
    out["mint_fn"] = mint
    pf = [e for e in abi if e.get("type") == "function" and e.get("name") == "priceFor"]
    out["priceFor_fn"] = pf
    fg = [e for e in abi if e.get("type") == "function" and e.get("name") == "freeGranted"]
    out["freeGranted_fn"] = fg
    fq = [e for e in abi if e.get("type") == "function" and e.get("name") == "free_quota"]
    out["free_quota_fn"] = fq
except Exception as e:
    out["abi_fetch_error"] = f"{type(e).__name__}: {e}"

print(json.dumps(out, indent=1))
json.dump(out, open(f"{BASE}/backfill-triage-132124249-132126341-retry.json", "w"), indent=1)
