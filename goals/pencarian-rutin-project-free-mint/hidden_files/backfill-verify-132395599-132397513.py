#!/usr/bin/env python3
"""Backfill triage verification run 2026-11-08 20:01 WIB, window 132395599-132397513.
Read-only eth_call verification (no preview/mint/sign). Uses public BSC dataseeds
(NOT Ankr for block timestamps - Ankr returns fake 'now' timestamps).
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

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a.lower()[2:]

def enc_uint(n):
    return format(n, "064x")

def call(to, data, tag=""):
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
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            data += enc_addr(a)
        else:
            data += enc_uint(int(a))
    r = call(to, data, sig)
    if "error" in r:
        return {"fn": sig, "error": r["error"]}
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
    return {"fn": sig, "value": v, "raw": h}

def check(contract, specs):
    out = {"address": contract}
    for sig, dec in specs:
        if sig.startswith("mintCost"):
            args = [1]
        elif "(address)" in sig:
            args = [USER]
        else:
            args = None
        out[sig.split("(")[0]] = vcall(contract, sig, args, dec)
    return out

def main():
    results = {}
    # Gloop
    results["Gloop"] = check("0x183CBb52B3C7BCB2433d50dE0Add99B59f4DE4fE", [
        ("AGENT_REGISTRY()", "addr"), ("totalMinted()", "uint"),
        ("TOTAL_SUPPLY()", "uint"), ("mintOpen()", "bool"),
        ("MINT_START()", "uint"), ("difficultyBits()", "uint"),
        ("owner()", "addr"), ("hasMinted(address)", "bool"),
    ])
    # Beast16
    results["Beast16"] = check("0xaCeF3B62B958ED7F49dFc73885609b4d270B9bD0", [
        ("AGENT_ID()", "addr"), ("MAX_SUPPLY()", "uint"), ("PRICE()", "uint"),
        ("currentPrice()", "uint"), ("totalMinted()", "uint"),
        ("mintOpen()", "bool"), ("OPEN_TIME()", "uint"),
        ("freeUsed(address)", "bool"), ("mintedBy(address)", "uint"),
        ("holdsAgentId(address)", "bool"), ("soldOut()", "bool"),
        ("owner()", "addr"),
    ])
    # 402
    results["402"] = check("0xd80D0095746999c93AE837B1DE1569d5814405dC", [
        ("agentIdRegistry()", "addr"), ("FREE_CAP()", "uint"),
        ("FREE_PER_WALLET()", "uint"), ("freeMinted()", "uint"),
        ("freeCount(address)", "uint"), ("PRICE()", "uint"),
        ("MAX_SUPPLY()", "uint"), ("totalMinted()", "uint"),
        ("paidMintedCount()", "uint"), ("mintOpen()", "bool"),
        ("owner()", "addr"),
    ])
    # AAEF (1 mint, agentRegistry in ABI) - mintCost signature? check ABI first
    abi = json.load(open("sourcify-AAEF5BB8.json")).get("abi") or []
    fns = {}
    for e in abi:
        if e.get("type") == "function":
            fns.setdefault(e["name"], []).append(
                "(" + ",".join(i["type"] for i in e.get("inputs", [])) + ")")
    print("AAEF fn signatures:", json.dumps(fns, indent=1), file=sys.stderr)
    specs = [("agentRegistry()", "addr"), ("name()", "str"), ("symbol()", "str"),
             ("MAX_SUPPLY()", "uint"), ("totalSupply()", "uint"),
             ("totalMinted()", "uint"), ("mintActive()", "bool"),
             ("owner()", "addr")]
    if "mintCost" in fns:
        for s in fns["mintCost"]:
            if s == "(uint256)":
                specs.append(("mintCost(uint256)", "uint"))
    if "freeUsed" in fns:
        for s in fns["freeUsed"]:
            if s == "(address)":
                specs.append(("freeUsed(address)", "bool"))
    if "price" in fns:
        for s in fns["price"]:
            if s == "()":
                specs.append(("price()", "uint"))
    results["AAEF"] = check("0xAAEF5BB8A7363B5997F17149d554640DC35f306d", specs)
    # first-mint block timestamps (dataseed, not Ankr)
    for name, blk in [("Gloop", 132395620), ("Beast16", 132395601),
                      ("402", 132395729), ("AAEF", 132396078)]:
        ts = get_block_ts(blk)
        results[name]["first_block_ts"] = ts
        if ts:
            results[name]["first_block_wib"] = time.strftime(
                "%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7 * 3600))
    # owner vs same-owner discards
    disc = json.load(open("same-owner-discards.json"))
    disc_owners = {d.get("owner", "").lower() for d in disc if isinstance(d, dict)}
    disc_contracts = {d.get("contract", "").lower() for d in disc if isinstance(d, dict)}
    for name, r in results.items():
        o = r.get("owner", {})
        ov = o.get("value") if isinstance(o, dict) else None
        r["owner_in_discards"] = (ov.lower() in disc_owners) if ov else None
        r["contract_in_discards"] = r["address"].lower() in disc_contracts
    print(json.dumps(results, indent=1))

if __name__ == "__main__":
    main()
