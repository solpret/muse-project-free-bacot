#!/usr/bin/env python3
"""Retry transport-failed views from backfill triage 132404142-132407133.
Read-only; writes backfill-triage-132404142-132407133-retry.json.
Targets: SHACHO agentRegistry/owner/mintOpen/price/costOf + first-block ts;
NUMBI totalMinted/PAID_PRICE/TOKEN_PER_MINT/paused/walletStatus/mintedCount;
0x71144E code+owner; 0x63eC first-block ts. No preview/mint/sign.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
REG_HEX = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SHACHO = "0x26E009350Ef80cb542785d57c27c686a582bf605"
NUMBI = "0xeEdd6F512Fec64AD5A4aa64722ef6C5689937B50"
TID = 107187496765866644729837695198686237165740365523485558112864918211974996443404

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a.lower()[2:]

def enc_uint(n):
    return format(int(n), "064x")

def call(to, sig, args=None, decode="uint"):
    data = "0x" + sel(sig)
    for a in (args or []):
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            data += enc_addr(a)
        else:
            data += enc_uint(a)
    for attempt in (1, 2, 3):
        try:
            r = race("eth_call", [{"to": to, "data": data}, "latest"])
            if isinstance(r, dict) and "error" in r:
                return {"fn": sig, "error": str(r["error"])[:150]}
            h = r
            if decode == "uint":
                v = int(h, 16) if h and h != "0x" else None
            elif decode == "bool":
                v = int(h, 16) if h and h != "0x" else None
                v = None if v is None else bool(v)
            elif decode == "addr":
                v = ("0x" + h[-40:]).lower() if h and len(h) >= 66 else None
            else:
                v = h
            return {"fn": sig, "value": v}
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:120]}"
            time.sleep(3)
    return {"fn": sig, "error": last}

def block_ts(blk):
    for _ in (1, 2, 3):
        try:
            b = race("eth_getBlockByNumber", [hex(blk), False])
            ts = int(b["timestamp"], 16)
            return ts, time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7 * 3600))
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:120]}"
            time.sleep(3)
    return None, last

def main():
    out = {}
    # SHACHO
    s = {}
    s["agentRegistry"] = call(SHACHO, "agentRegistry()", None, "addr")
    s["agentRegistry_exact_match"] = s["agentRegistry"].get("value") == REGISTRY.lower()
    s["owner"] = call(SHACHO, "owner()", None, "addr")
    s["mintOpen"] = call(SHACHO, "mintOpen()", None, "bool")
    s["price"] = call(SHACHO, "price()", None, "uint")
    s["costOf(user,tid)"] = call(SHACHO, "costOf(address,uint256)", [USER, TID], "uint")
    s["costOf(user,1)"] = call(SHACHO, "costOf(address,uint256)", [USER, 1], "uint")
    s["freeOf(user,tid)"] = call(SHACHO, "freeOf(address,uint256)", [USER, TID], "uint")
    s["MAX_PER_WALLET"] = call(SHACHO, "MAX_PER_WALLET()", None, "uint")
    s["first_block_ts"] = block_ts(132406645)
    discards = json.load(open(f"{BASE}/same-owner-discards.json"))
    owners = {r.get("owner", "").lower() for r in discards if isinstance(r, dict)}
    s["owner_in_discards"] = (s["owner"].get("value") in owners) if s["owner"].get("value") else None
    out["SHACHO"] = s
    print("SHACHO:", json.dumps(s, indent=1))
    # NUMBI
    n = {}
    n["totalMinted"] = call(NUMBI, "totalMinted()", None, "uint")
    n["PAID_PRICE"] = call(NUMBI, "PAID_PRICE()", None, "uint")
    n["TOKEN_PER_MINT"] = call(NUMBI, "TOKEN_PER_MINT()", None, "uint")
    n["MAX_PER_WALLET"] = call(NUMBI, "MAX_PER_WALLET()", None, "uint")
    n["paused"] = call(NUMBI, "paused()", None, "bool")
    n["walletStatus(user)"] = call(NUMBI, "walletStatus(address)", [USER], "uint")
    n["mintedCount(user)"] = call(NUMBI, "mintedCount(address)", [USER], "uint")
    n["mintedCount(puzzleSigner?)"] = None
    out["NUMBI"] = n
    print("NUMBI:", json.dumps(n, indent=1))
    # 0x71144E ERC1155: code registry bytes + owner
    e = {}
    try:
        code = race("eth_getCode", ["0x71144EA489539EdbD58faB4D53b0ba5C2E446263", "latest"])
        e["code_registry_bytes_hit"] = REG_HEX in code.lower() if isinstance(code, str) else None
        e["code_len"] = len(code) if isinstance(code, str) else None
    except Exception as ex:
        e["code_error"] = f"{type(ex).__name__}: {str(ex)[:120]}"
    e["owner"] = call("0x71144EA489539EdbD58faB4D53b0ba5C2E446263", "owner()", None, "addr")
    e["owner_in_discards"] = (e["owner"].get("value") in owners) if e["owner"].get("value") else None
    out["ERC1155_0x71144E"] = e
    print("0x71144E:", json.dumps(e, indent=1))
    # 0x63eC first-block ts
    out["0x63eC_first_block_ts"] = block_ts(132404983)
    print("0x63eC ts:", out["0x63eC_first_block_ts"])
    json.dump(out, open(f"{BASE}/backfill-triage-132404142-132407133-retry.json", "w"), indent=1)
    print("WROTE backfill-triage-132404142-132407133-retry.json")

if __name__ == "__main__":
    main()
