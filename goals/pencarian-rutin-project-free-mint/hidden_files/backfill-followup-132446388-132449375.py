#!/usr/bin/env python3
"""Meow Cards follow-up, backfill run 2026-11-09 ~02:31 WIB.
Read-only. Triage utama: agent-shaped (agentRegistry persis 0x60B926...),
Sourcify exact_match, name Meow Cards / MEOWC, totalSupply 2, MAX_SUPPLY 10000,
priceOf(user,1,1)=0,00035 BNB, TAPI first_block timestamp GAGAL (semua endpoint
fast_rpc timeout) dan firstFreeUsed(user) belum dibaca.
Follow-up baca ulang dengan retry: firstFreeUsed(user), PRICE_TIER_1/2,
remaining(), MAX_PER_WALLET(), mintedByWallet(user), balanceOf(user),
isAgent(user,1), refPriceOf(1), totalCards(), nextTokenId(), tokenURI(1),
first-block timestamp (retry fast_rpc, fallback curl dataseed langsung).
Tulis backfill-followup-132446388-132449375.json. No preview/mint/sign.
"""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0xb8164afefc53910D7A74cEcE15A60a9e0C86089e"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
FIRST_BLOCK = 132446691

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a.lower()[2:]

def enc_uint(n):
    return format(int(n), "064x")

def eth_call(to, data, tries=4):
    last = None
    for i in range(tries):
        try:
            r = race("eth_call", [{"to": to, "data": data}, "latest"])
            if isinstance(r, dict) and "error" in r:
                return {"error": str(r["error"])[:150]}
            return {"result": r}
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:120]}"
            time.sleep(4)
    return {"error": last}

def dec(h, kind):
    if not h or h == "0x":
        return None
    try:
        if kind == "addr":
            return "0x" + h[-40:] if len(h) >= 66 else None
        if kind == "bool":
            return bool(int(h, 16))
        if kind == "str":
            ln = int(h[66:130], 16)
            return bytes.fromhex(h[130:130 + ln * 2]).decode("utf-8", "replace")
        return int(h, 16)
    except Exception:
        return None

def call(sig, args=None, kind="uint"):
    data = "0x" + sel(sig)
    for a in (args or []):
        data += enc_addr(a) if (isinstance(a, str) and a.startswith("0x") and len(a) == 42) else enc_uint(a)
    r = eth_call(ADDR, data)
    if "error" in r:
        return {"fn": sig, "error": r["error"]}
    v = dec(r["result"], kind)
    if v is None and r["result"] not in (None, "0x"):
        return {"fn": sig, "value": None, "raw": str(r["result"])[:120], "note": "decode-null (revert?)"}
    return {"fn": sig, "value": v}

def block_ts(blk):
    for i in range(4):
        try:
            b = race("eth_getBlockByNumber", [hex(blk), False])
            ts = int(b["timestamp"], 16)
            return {"block": blk, "timestamp": ts,
                    "wib": time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7 * 3600))}
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:120]}"
            time.sleep(4)
    # fallback: curl dataseed langsung
    try:
        r = subprocess.run(["curl", "-s", "-m", "20", "-X", "POST",
                            "https://bsc-dataseed.binance.org/",
                            "-H", "Content-Type: application/json",
                            "-d", json.dumps({"jsonrpc": "2.0", "method": "eth_getBlockByNumber",
                                              "params": [hex(blk), False], "id": 1})],
                           capture_output=True, text=True, timeout=30)
        d = json.loads(r.stdout)
        ts = int(d["result"]["timestamp"], 16)
        return {"block": blk, "timestamp": ts, "via": "curl-dataseed",
                "wib": time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7 * 3600))}
    except Exception as e:
        return {"block": blk, "error": f"{last} | curl fallback: {type(e).__name__}: {str(e)[:120]}"}

def main():
    out = {"address": ADDR, "name": "Meow Cards"}
    out["first_block"] = block_ts(FIRST_BLOCK)
    out["firstFreeUsed(user)"] = call("firstFreeUsed(address)", [USER], "bool")
    out["PRICE_TIER_1"] = call("PRICE_TIER_1()", None, "uint")
    out["PRICE_TIER_2"] = call("PRICE_TIER_2()", None, "uint")
    out["remaining"] = call("remaining()", None, "uint")
    out["MAX_PER_WALLET"] = call("MAX_PER_WALLET()", None, "uint")
    out["mintedByWallet(user)"] = call("mintedByWallet(address)", [USER], "uint")
    out["balanceOf(user)"] = call("balanceOf(address)", [USER], "uint")
    out["isAgent(user,1)"] = call("isAgent(address,uint256)", [USER, 1], "bool")
    out["refPriceOf(1)"] = call("refPriceOf(uint256)", [1], "uint")
    out["priceOf(user,1,1)"] = call("priceOf(address,uint256,uint256)", [USER, 1, 1], "uint")
    out["priceOf(user,0,1)"] = call("priceOf(address,uint256,uint256)", [USER, 0, 1], "uint")
    out["totalCards"] = call("totalCards()", None, "uint")
    out["nextTokenId"] = call("nextTokenId()", None, "uint")
    out["totalSupply"] = call("totalSupply()", None, "uint")
    out["totalMinted"] = call("totalMinted()", None, "uint")
    out["tokenURI(1)"] = call("tokenURI(uint256)", [1], "str")
    out["tokenURI(2)"] = call("tokenURI(uint256)", [2], "str")
    json.dump(out, open(f"{BASE}/backfill-followup-132446388-132449375.json", "w"), indent=1)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
