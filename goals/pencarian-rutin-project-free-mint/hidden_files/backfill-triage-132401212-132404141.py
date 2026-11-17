#!/usr/bin/env python3
"""Backfill triage run 2026-11-08 ~21:0x WIB, window 132401212-132404141.
Read-only on-chain/state inputs; writes only backfill-triage-132401212-132404141.json.
First-seen (7 deduped): Sourcify ABI via curl, agentRegistry() EXACT check
(must equal 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F), free views + quote(user,1)
for agent-shaped contracts, first-block timestamp via fast_rpc (NOT Ankr -
Ankr returns fake 'now' timestamps), owner() vs same-owner-discards.json.
No preview/mint/sign/approve/swap.
"""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
REG_HEX = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

# address, first_block, mint_total_window, scan name/symbol
CONTRACTS = [
    ("0x669cb75f51b5D23F4B42fC1522b653d7B88e608d", 132401561, 33, "MiChan", "MICHAN"),
    ("0xFD63eB16714e1A1c45cF467243131D89Bb8e0B70", 132401609, 18, "Delveria Gear", "DLVG"),
    ("0x9421A58DFc41C4f5E7942B8B4777837d641106E3", 132401705, 4, None, None),
    ("0x54259f6001532c21893dae48B046627B72DfeC58", 132401907, 1, None, None),
    ("0xD61aF26aD1D8D9903436455e665d38167AcCCbEc", 132403589, 5, "Pressure", "PRESS"),
    ("0xEd934652815f98CB9FAcc6Ce0511f01A25694741", 132403768, 1, "Aiuki", "AIUKI"),
    ("0xb99a07A9aB24a07cDE78906E597d7fc056A07Ae6", 132403710, 1, "Brookwood Village Townhomes", "BVT"),
]

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a.lower()[2:]

def enc_uint(n):
    return format(int(n), "064x")

def enc_str(s):
    b = s.encode()
    out = enc_uint(32) + enc_uint(len(b))
    hx = b.hex()
    hx += "0" * ((64 - len(hx) % 64) % 64)
    return out + hx

def eth_call(to, data):
    try:
        r = race("eth_call", [{"to": to, "data": data}, "latest"])
        if isinstance(r, dict) and "error" in r:
            return {"error": str(r["error"])[:150]}
        return {"result": r}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:150]}"}

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

def dec_str(h):
    if not h or h == "0x" or len(h) < 130:
        return None
    try:
        ln = int(h[66:130], 16)
        return bytes.fromhex(h[130:130 + ln * 2]).decode("utf-8", "replace")
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
            data += enc_uint(a)
    r = eth_call(to, data)
    if "error" in r:
        return {"fn": sig, "error": r["error"]}
    h = r["result"]
    if decode == "uint":
        v = dec_uint(h)
    elif decode == "bool":
        v = dec_uint(h)
        v = None if v is None else bool(v)
    elif decode == "addr":
        v = dec_addr(h)
        v = v.lower() if v else None
    elif decode == "str":
        v = dec_str(h)
    else:
        v = h
    if v is None and h not in (None, "0x"):
        return {"fn": sig, "value": None, "raw": str(h)[:100], "note": "decode-null (revert?)"}
    return {"fn": sig, "value": v}

def fetch_abi_curl(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    last = None
    for _ in (1, 2):
        try:
            r = subprocess.run(["curl", "-s", "-m", "25", "-A",
                                "free-bacot-backfill-triage/1.0", url],
                               capture_output=True, text=True, timeout=40)
            if r.returncode != 0:
                last = f"curl rc={r.returncode} {r.stderr[:120]}"
                time.sleep(2)
                continue
            return json.loads(r.stdout), None
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
            time.sleep(2)
    return None, last

def block_ts(blk):
    try:
        b = race("eth_getBlockByNumber", [hex(blk), False])
        ts = int(b["timestamp"], 16)
        return ts, time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7 * 3600))
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"

def main():
    discards = json.load(open(f"{BASE}/same-owner-discards.json"))
    discard_owners = {r.get("owner", "").lower() for r in discards if isinstance(r, dict)}
    discard_contracts = {r.get("contract", "").lower() for r in discards if isinstance(r, dict)}
    results = []
    for addr, first_block, mint_total, scan_name, scan_symbol in CONTRACTS:
        o = {"address": addr, "first_block": first_block,
             "mint_total_window": mint_total,
             "scan_name": scan_name, "scan_symbol": scan_symbol}
        ts, ts_wib = block_ts(first_block)
        o["first_block_timestamp"] = ts
        o["first_block_wib"] = ts_wib
        data, err = fetch_abi_curl(addr)
        abi = None
        if data is not None:
            abi = data.get("abi")
            if abi is None and isinstance(data.get("stdJson"), dict):
                abi = data["stdJson"].get("abi")
        if abi is not None:
            o["sourcify"] = data.get("match") or "verified"
            fns = [e for e in abi if isinstance(e, dict) and e.get("type") == "function"]
            names = {f.get("name", "") for f in fns}
            o["abi_fn_count"] = len(fns)
            o["abi_fn_names"] = sorted(names)
        elif data is not None:
            o["sourcify"] = "not_verified"
            names = set()
        else:
            o["sourcify"] = f"transport-failed: {err}"
            names = set()
        # bytecode registry-bytes check (independent of Sourcify)
        try:
            code = race("eth_getCode", [addr, "latest"])
            if isinstance(code, str) and code.startswith("0x"):
                o["code_registry_bytes_hit"] = REG_HEX in code.lower()
                o["code_len"] = len(code)
            else:
                o["code_registry_bytes_hit"] = None
                o["code_error"] = str(code)[:200]
        except Exception as e:
            o["code_registry_bytes_hit"] = None
            o["code_error"] = f"{type(e).__name__}: {str(e)[:150]}"
        # agentRegistry() exact check when ABI has it or code has registry bytes
        agent_shaped = bool(o.get("code_registry_bytes_hit")) or ("agentRegistry" in names)
        if "agentRegistry" in names or o.get("code_registry_bytes_hit"):
            r = vcall(addr, "agentRegistry()", None, "addr")
            o["agentRegistry"] = r
            o["agentRegistry_exact_match"] = (r.get("value") == REGISTRY.lower())
            agent_shaped = bool(o["agentRegistry_exact_match"]) or bool(o.get("code_registry_bytes_hit"))
        o["agent_shaped"] = agent_shaped
        # generic views when ABI exists
        if names:
            for sig, dec in [("name()", "str"), ("symbol()", "str"),
                             ("totalSupply()", "uint"), ("MAX_SUPPLY()", "uint"),
                             ("mintOpen()", "bool"), ("price()", "uint"),
                             ("owner()", "addr")]:
                fn = sig.split("(")[0]
                if fn in names:
                    o[fn] = vcall(addr, sig, None, dec)
            # free views present in ABI
            for fn in ["freeLeft", "freeClaimed", "freeMinted", "freeSupply",
                       "FREE_SLOTS", "FREE_SUPPLY", "FREE_CAP", "freeSharesRemaining"]:
                if fn in names:
                    args = [USER] if fn == "freeClaimed" else None
                    o[fn] = vcall(addr, fn + ("(address)" if args else "()"), args, "uint")
            # agent token id + quote/free with token id
            tid = None
            if "agentTokenIdOf" in names:
                r = vcall(addr, "agentTokenIdOf(string)", [("str", "masgayut.ai")], "uint")
                o["agentTokenIdOf_masgayut.ai"] = r
                tid = r.get("value")
            if agent_shaped:
                for t in ([tid, 1] if tid else [1]):
                    if "freeOf" in names:
                        o[f"freeOf(user,{t})"] = vcall(addr, "freeOf(address,uint256)", [USER, t], "uint")
                    if "costOf" in names:
                        o[f"costOf(user,{t})"] = vcall(addr, "costOf(address,uint256)", [USER, t], "uint")
                    if "quote" in names:
                        o[f"quote(user,{t})"] = vcall(addr, "quote(address,uint256)", [USER, t], "uint")
                if "agentIds" in names:
                    o["agentIds"] = vcall(addr, "agentIds()", None, "addr")
                if "mintedBy" in names:
                    o["mintedBy(user)"] = vcall(addr, "mintedBy(address)", [USER], "uint")
                if "mintsLeft" in names:
                    o["mintsLeft(user)"] = vcall(addr, "mintsLeft(address)", [USER], "uint")
        else:
            # no ABI: best-effort owner() only
            o["owner"] = vcall(addr, "owner()", None, "addr")
        ov = None
        if isinstance(o.get("owner"), dict):
            ov = o["owner"].get("value")
        o["owner_in_discards"] = (ov.lower() in discard_owners) if ov else None
        o["contract_in_discards"] = addr.lower() in discard_contracts
        results.append(o)
        print(json.dumps(o, indent=1))
    out = {"run": "backfill 2026-11-08 ~21:0x WIB", "window": [132401212, 132404141],
           "first_seen_triage": results,
           "early_leads": [r for r in results if r.get("agent_shaped")],
           "same_owner_discards": [r for r in results if r.get("owner_in_discards")]}
    json.dump(out, open(f"{BASE}/backfill-triage-132401212-132404141.json", "w"), indent=1)
    print("WROTE backfill-triage-132401212-132404141.json")
    print("early_leads(agent-shaped):", len(out["early_leads"]),
          "same-owner discards:", len(out["same_owner_discards"]))

if __name__ == "__main__":
    main()
