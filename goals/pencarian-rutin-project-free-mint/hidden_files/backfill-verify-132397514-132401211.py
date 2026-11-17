#!/usr/bin/env python3
"""Backfill triage verification run 2026-11-08 20:31 WIB, window 132397514-132401211.
Read-only eth_call verification (no preview/mint/sign). Uses public BSC dataseeds
(NOT Ankr for block timestamps - Ankr returns fake 'now' timestamps).
Template: agentIds()/freeLeft()/freeOf(address,uint256)/costOf(address,uint256)/
mintWithAgentTokenId - 5 contracts share identical 41-fn ABI (exact_match).
"""
import json, urllib.request, time, sys
from eth_hash.auto import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
RPCS = [
    "https://bsc-dataseed.binance.org",
    "https://bsc-dataseed1.bnbchain.org",
    "https://bsc-dataseed2.bnbchain.org",
    "https://bsc-dataseed1.defibit.io",
    "https://1rpc.io/bnb",
]
CONTRACTS = {
    "C1": ("0xaC3f9A33c653FB3CA49056cFA5eDf19101DeBf97", 132398338, 95),
    "C2": ("0x169F9cfC148ba462Bb0073466939e8Eae32C0be5", 132398433, 48),
    "C3": ("0xf4BaCF30fB8F69373F63D99C657F53DD7774Af1D", 132398918, 30),
    "C4": ("0xef4Fa905b107A431FcaEB50F1183B712dc3eb9D6", 132398383, 42),
    "C5": ("0x6a90E032D50C6FF44608167f7a8634c77ACAeE34", 132398414, 30),
    "C6": ("0xf4dC5600D2546E1e52b8cA81169D3Cec53264b68", 132397626, 7),
}

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a.lower()[2:]

def enc_uint(n):
    return format(n, "064x")

def enc_str(s):
    b = s.encode()
    out = enc_uint(32) + enc_uint(len(b))
    hx = b.hex()
    hx += "0" * ((64 - len(hx) % 64) % 64)
    return out + hx

def call(to, data):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": to, "data": data}, "latest"]}).encode()
    last_err = None
    for url in RPCS:
        try:
            req = urllib.request.Request(url, data=payload,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                j = json.load(r)
            if "error" in j:
                return {"error": j["error"]}
            return {"result": j["result"]}
        except Exception as e:
            last_err = str(e)
    return {"error": last_err}

def get_block_ts(num):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                          "params": [hex(num), False]}).encode()
    for url in RPCS:
        try:
            req = urllib.request.Request(url, data=payload,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                j = json.load(r)
            b = j.get("result")
            if b and b.get("timestamp"):
                return int(b["timestamp"], 16)
        except Exception:
            pass
    return None

def dec_addr(h):
    if not h or h == "0x" or len(h) < 66:
        return None
    return "0x" + h[-40:]

def dec_uint(h):
    if not h or h == "0x":
        return None
    try:
        return int(h, 16)
    except Exception:
        return None

def dec_bool(h):
    v = dec_uint(h)
    return None if v is None else bool(v)

def dec_str(h):
    if not h or h == "0x" or len(h) < 130:
        return None
    try:
        ln = int(h[66:130], 16)
        raw = bytes.fromhex(h[130:130 + ln * 2])
        return raw.decode("utf-8", "replace")
    except Exception:
        return None

def vcall(to, sig, args=None, decode="uint"):
    data = "0x" + sel(sig)
    for a in (args or []):
        if isinstance(a, tuple) and a[0] == "str":
            data += enc_str(a[1])
        elif isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            data += enc_addr(a)
        else:
            data += enc_uint(int(a))
    r = call(to, data)
    if "error" in r:
        return {"fn": sig, "error": str(r["error"])[:120]}
    h = r["result"]
    if decode == "uint":
        v = dec_uint(h)
    elif decode == "bool":
        v = dec_bool(h)
    elif decode == "addr":
        v = dec_addr(h)
        v = v.lower() if v else None
    elif decode == "str":
        v = dec_str(h)
    else:
        v = h
    if v is None and h not in (None, "0x"):
        return {"fn": sig, "value": None, "raw": h[:100], "note": "decode-null (revert?)"}
    return {"fn": sig, "value": v}

def main():
    results = {}
    # agent token id of the user's agent name (pure fn on template)
    tid = None
    r = vcall(CONTRACTS["C1"][0], "agentTokenIdOf(string)", [("str", "masgayut.ai")], "uint")
    tid = r.get("value")
    results["agentTokenIdOf_masgayut.ai_on_C1"] = r
    for key, (addr, first_block, mint_total) in CONTRACTS.items():
        o = {"address": addr, "first_block": first_block, "mint_total_window": mint_total}
        if key == "C6":
            # not_verified: best-effort generic views
            for sig, dec in [("name()", "str"), ("symbol()", "str"),
                             ("totalSupply()", "uint"), ("owner()", "addr")]:
                o[sig.split("(")[0]] = vcall(addr, sig, None, dec)
            o["sourcify"] = "not_verified"
        else:
            for sig, dec, args in [
                ("name()", "str", None), ("symbol()", "str", None),
                ("agentIds()", "addr", None),
                ("MAX_SUPPLY()", "uint", None), ("totalSupply()", "uint", None),
                ("mintOpen()", "bool", None), ("price()", "uint", None),
                ("MAX_PER_WALLET()", "uint", None),
                ("freeLeft()", "uint", None), ("bogo()", "bool", None),
                ("mintedBy(address)", "uint", [USER]),
                ("mintsLeft(address)", "uint", [USER]),
                ("owner()", "addr", None), ("treasury()", "addr", None),
            ]:
                o[sig.split("(")[0]] = vcall(addr, sig, args, dec)
            # free path for user: freeOf/costOf with tokenId from agentTokenIdOf, and with 1
            for t in ([tid, 1] if tid else [1]):
                o["freeOf(user,%s)" % t] = vcall(addr, "freeOf(address,uint256)", [USER, t], "uint")
                o["costOf(user,%s)" % t] = vcall(addr, "costOf(address,uint256)", [USER, t], "uint")
            o["sourcify"] = "exact_match"
        ts = get_block_ts(first_block)
        o["first_block_ts"] = ts
        if ts:
            o["first_mint_wib"] = time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7 * 3600))
        results[key] = o
    # owner vs same-owner discards
    disc = json.load(open("same-owner-discards.json"))
    disc_owners = {d.get("owner", "").lower() for d in disc if isinstance(d, dict)}
    disc_contracts = {d.get("contract", "").lower() for d in disc if isinstance(d, dict)}
    for key, o in results.items():
        if key.startswith("agentToken"):
            continue
        ov = o.get("owner", {})
        ov = ov.get("value") if isinstance(ov, dict) else None
        o["owner_in_discards"] = (ov.lower() in disc_owners) if ov else None
        o["contract_in_discards"] = o["address"].lower() in disc_contracts
    print(json.dumps(results, indent=1))

if __name__ == "__main__":
    main()
