#!/usr/bin/env python3
"""Fresh on-chain verification for Moonfang track-C lead (one-off, 2026-11-12).
Reads via eth_call with endpoint fallback + retries. Decodes word by word.
Usage: python3 moonfang-verify-0112.py
"""
import json, sys, time, urllib.request
from eth_hash.auto import keccak
from eth_abi import encode as abi_encode

SALE = "0x79b0CE8b39c3Ed230487172751612b4F631398Bc"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"  # baw agent wallet
ENDPOINTS = [
    "https://bsc-dataseed1.binance.org",
    "https://bsc-dataseed2.binance.org",
    "https://bsc-dataseed.bnbchain.org",
    "https://bsc-dataseed1.defibit.io",
    "https://rpc.ankr.com/bsc",
]

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def call_data(fn_sig, args=(), types=()):
    data = "0x" + sel(fn_sig)
    if args:
        data += abi_encode(types, args).hex()
    return data

def eth_call(to, data, endpoint, timeout=25):
    payload = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "eth_call",
        "params": [{"to": to, "data": data}, "latest"],
    }).encode()
    req = urllib.request.Request(endpoint, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)

def read(fn_sig, args=(), types=(), label=""):
    data = call_data(fn_sig, args, types)
    last_err = None
    for ep in ENDPOINTS:
        for attempt in range(2):
            try:
                res = eth_call(SALE, data, ep)
                if "error" in res:
                    last_err = res["error"]
                    continue
                raw = res["result"]
                if raw is None or raw == "0x":
                    return ("REVERT_OR_EMPTY", label)
                return (raw, label)
            except Exception as e:
                last_err = str(e)
                time.sleep(1)
    return ("UNVERIFIED:" + str(last_err)[:120], label)

def u256(raw):
    # decode first 32-byte word as uint256
    if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 66:
        return int(raw[2:66], 16)
    return raw

def boolean(raw):
    v = u256(raw)
    return bool(v) if isinstance(v, int) else raw

def addr(raw):
    if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 66:
        return "0x" + raw[-40:]
    return raw

def main():
    out = {}
    # Batch 1: totals first (per skill: total first, remaining can be stale)
    batch1 = [
        ("totalSupply()", (), (), u256),
        ("freeMinted()", (), (), u256),
        ("FREE_CAP()", (), (), u256),
        ("mintOpen()", (), (), boolean),
        ("priceOf(address,uint256)", (USER, 1), ("address", "uint256"), u256),
    ]
    for sig, args, types, dec in batch1:
        raw, _ = read(sig, args, types)
        out[sig] = dec(raw) if isinstance(raw, str) and raw.startswith("0x") else raw
        print(f"{sig}: {out[sig]}", flush=True)
        time.sleep(0.5)
    # Batch 2: user slot + params
    batch2 = [
        ("freeLeftFor(address)", (USER,), ("address",), u256),
        ("canMint(address)", (USER,), ("address",), boolean),
        ("mintedBy(address)", (USER,), ("address",), u256),
        ("MAX_PER_WALLET()", (), (), u256),
        ("token()", (), (), addr),
        ("REGISTRY()", (), (), addr),
    ]
    for sig, args, types, dec in batch2:
        raw, _ = read(sig, args, types)
        out[sig] = dec(raw) if isinstance(raw, str) and raw.startswith("0x") else raw
        print(f"{sig}: {out[sig]}", flush=True)
        time.sleep(0.5)
    # block number for freshness
    try:
        for ep in ENDPOINTS:
            try:
                payload = json.dumps({"jsonrpc": "2.0", "id": 1,
                                      "method": "eth_blockNumber", "params": []}).encode()
                req = urllib.request.Request(ep, data=payload,
                                             headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=20) as r:
                    bn = json.load(r)["result"]
                    print("blockNumber:", int(bn, 16), "via", ep, flush=True)
                    break
            except Exception:
                continue
    except Exception as e:
        print("blockNumber UNVERIFIED:", e)
    # mint calldata preview (programmatic): mint(uint256 qty, address referrer)
    qty = 1
    referrer = "0x0000000000000000000000000000000000000000"
    data = "0x" + sel("mint(uint256,address)") + abi_encode(["uint256", "address"], [qty, referrer]).hex()
    print("mint_calldata_qty1:", data, flush=True)
    print("value_wei (priceOf user,1):", out.get("priceOf(address,uint256)"), flush=True)
    json.dump(out, open("/tmp/moonfang_verify_out.json", "w"), indent=1, default=str)

if __name__ == "__main__":
    main()
