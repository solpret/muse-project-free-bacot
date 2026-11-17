#!/usr/bin/env python3
"""Triage first-seen of parallel backfill run 132094118-132096338 (2026-11-07 ~06:30 WIB).
Read-only; writes one JSON triage file.
Per contract: Sourcify ABI (curl), registry bytes in bytecode, agentRegistry()
exact match, name/symbol, owner(), free/price views + quote(user,1),
first-mint timestamp + age, owner vs same-owner-discards.json.
"""
import json, subprocess, sys, time
from datetime import datetime, timezone, timedelta

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
REG_BYTES = REGISTRY[2:].lower()
EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed3.bnbchain.org/"]
WIB = timezone(timedelta(hours=7))

def rpc_call(method, params, timeout=8):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:
            last = e
    raise last

def sel(sig):
    from eth_hash.auto import keccak
    return "0x" + keccak(sig.encode()).hex()[:8]

def call(addr, data, timeout=7):
    try:
        return rpc_call("eth_call", [{"to": addr, "data": data}, "latest"], timeout)
    except Exception as e:
        return {"_error": str(e)[:120]}

def dec_uint(out):
    if not isinstance(out, str) or not out.startswith("0x") or len(out) < 66:
        return None
    try:
        return int(out[2:66], 16)
    except Exception:
        return None

def dec_addr(out):
    if not isinstance(out, str) or len(out) < 66:
        return None
    return "0x" + out[26:66]

def dec_str(out):
    if not isinstance(out, str) or not out.startswith("0x") or len(out) < 130:
        return None
    try:
        b = bytes.fromhex(out[2:])
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96+ln].decode(errors="replace")
    except Exception:
        return None

def sourcify_abi(address):
    try:
        p = subprocess.run(["curl", "-s", "-m", "20",
            f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"],
            capture_output=True, text=True, timeout=25)
        if p.returncode != 0 or not p.stdout.strip():
            return ("curl_error", None)
        d = json.loads(p.stdout)
        if d.get("match") is None and d.get("abi") is None:
            return ("not_verified", None)
        return ("verified", d.get("abi"))
    except Exception as e:
        return (f"error:{type(e).__name__}", None)

def first_mint_ts(block):
    try:
        b = rpc_call("eth_getBlockByNumber", [hex(block), False], timeout=8)
        ts = int(b["timestamp"], 16)
        return ts, datetime.fromtimestamp(ts, WIB).strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        return None, f"error:{str(e)[:80]}"

def triage_one(c, discards):
    addr = c["address"]
    out = dict(c)
    code = None
    try:
        code = rpc_call("eth_getCode", [addr, "latest"], timeout=5)
    except Exception as e:
        code = f"ERR:{e}"
    out["registry_bytes_in_code"] = (REG_BYTES in code[2:].lower()) if isinstance(code, str) and len(code) > 2 else None
    status, abi = sourcify_abi(addr)
    out["sourcify"] = status
    fns = []
    if isinstance(abi, list):
        fns = [i.get("name") for i in abi if i.get("type") == "function"]
    out["abi_functions"] = fns
    low = [f.lower() for f in fns]
    out["name"] = dec_str(call(addr, sel("name()"))) if "name" in low else None
    out["symbol"] = dec_str(call(addr, sel("symbol()"))) if "symbol" in low else None
    out["agentRegistry"] = dec_addr(call(addr, sel("agentRegistry()"))) if "agentregistry" in low else None
    out["registry_match"] = (out["agentRegistry"] or "").lower() == REGISTRY.lower() if out["agentRegistry"] else False
    out["owner"] = dec_addr(call(addr, sel("owner()"))) if "owner" in low else None
    out["totalSupply"] = dec_uint(call(addr, sel("totalSupply()"))) if "totalsupply" in low else None
    out["maxSupply"] = dec_uint(call(addr, sel("maxSupply()"))) if "maxsupply" in low else None
    free = {}
    for fn, data in [
        ("PRICE", sel("PRICE()") if "price" in low else None),
        ("price", sel("price()") if "price" in low else None),
        ("FREE_SUPPLY", sel("FREE_SUPPLY()") if "free_supply" in low else None),
        ("freeSupply", sel("freeSupply()") if "freesupply" in low else None),
        ("freeMinted", sel("freeMinted()") if "freeminted" in low else None),
        ("FREE_SLOTS", sel("FREE_SLOTS()") if "free_slots" in low else None),
        ("freeLeft", sel("freeLeft()") if "freeleft" in low else None),
        ("freeClaimed(user)", sel("freeClaimed(address)") + USER[2:].lower().rjust(64, "0") if "freeclaimed" in low else None),
        ("freeFor(user)", sel("freeFor(address)") + USER[2:].lower().rjust(64, "0") if "freefor" in low else None),
        ("quote(user,1)", sel("quote(address,uint256)") + USER[2:].lower().rjust(64, "0") + "1".rjust(64, "0") if "quote" in low else None),
    ]:
        if data:
            v = call(addr, data)
            free[fn] = dec_uint(v) if not isinstance(v, dict) else v
    out["free_views"] = free
    ts, wib = first_mint_ts(c["first_block"])
    out["first_mint_ts"] = ts
    out["first_mint_wib"] = wib
    out["age_hours"] = round((time.time() - ts) / 3600, 2) if ts else None
    out["owner_in_discards"] = (out["owner"] or "").lower() in {d.lower() for d in discards} if out["owner"] else False
    out["agent_shaped"] = bool(out["registry_match"] or out["registry_bytes_in_code"])
    out["age_ok_48h"] = out["age_hours"] is not None and out["age_hours"] <= 48
    if out["agent_shaped"] and out["age_ok_48h"]:
        out["verdict"] = "AGENT-SHAPED — needs free-path check (quote/free views)"
    elif out["agent_shaped"]:
        out["verdict"] = "agent-shaped but age >48h — not early lead"
    else:
        out["verdict"] = "not-agent-shaped"
    return out

def main():
    first_seen = []
    for f in ["backfill-132094118-132096117.json", "backfill-132096118-132096338.json"]:
        d = json.load(open(f"{BASE}/{f}"))
        first_seen += d.get("first_seen", [])
    # dedupe across chunks, keep earliest first_block
    ded = {}
    for c in first_seen:
        a = c["address"]
        if a not in ded or c["first_block"] < ded[a]["first_block"]:
            ded[a] = c
    first_seen = sorted(ded.values(), key=lambda c: c["first_block"])
    discards = json.load(open(f"{BASE}/same-owner-discards.json"))
    if isinstance(discards, list) and discards and isinstance(discards[0], dict):
        discards = [d.get("owner") for d in discards if d.get("owner")]
    else:
        discards = discards.get("owners", discards.get("discards", [])) if isinstance(discards, dict) else discards
    print(f"TRIAGE {len(first_seen)} first-seen (deduped)")
    res = [triage_one(c, discards) for c in first_seen]
    for r in res:
        print(json.dumps({k: r.get(k) for k in
            ["address", "kind", "mint_count", "first_block", "first_mint_wib",
             "age_hours", "name", "symbol", "sourcify", "registry_match",
             "registry_bytes_in_code", "agentRegistry", "owner", "owner_in_discards",
             "totalSupply", "maxSupply", "free_views", "verdict"]}, indent=1, ensure_ascii=False))
    triage = {"run": "backfill-132094118-132096338",
              "checked_wib": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S"),
              "first_seen_triage": res}
    out_path = f"{BASE}/backfill-triage-132094118-132096338.json"
    json.dump(triage, open(out_path, "w"), indent=1, ensure_ascii=False)
    print("WROTE", out_path)

if __name__ == "__main__":
    main()
