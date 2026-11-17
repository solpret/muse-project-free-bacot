#!/usr/bin/env python3
"""Golden Agents follow-up, backfill run 2026-11-09 ~02:01 WIB.
Read-only. Triage utama gagal membaca AGENT_ID_REGISTRY() dkk karena
endpoint fast_rpc timeout (bukan revert): baca ulang nilai-nilai kunci
dengan retry: AGENT_ID_REGISTRY() (harus persis
0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F), mintActive(), publicMinted(),
MAX_PER_WALLET(), PUBLIC_MAX(), TEAM_RESERVE(), reservedMinted(),
mintedBy(user), balanceOf(user). Tulis
backfill-followup-132442705-132446387.json. No preview/mint/sign.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0x4233C62919CC03168a361C547117c1553C375bfC"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a.lower()[2:]

def enc_uint(n):
    return format(int(n), "064x")

def eth_call(to, data, tries=3):
    last = None
    for i in range(tries):
        try:
            r = race("eth_call", [{"to": to, "data": data}, "latest"])
            if isinstance(r, dict) and "error" in r:
                return {"error": str(r["error"])[:150]}
            return {"result": r}
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:120]}"
            time.sleep(3)
    return {"error": last}

def dec(h, kind):
    if not h or h == "0x":
        return None
    try:
        if kind == "addr":
            return "0x" + h[-40:] if len(h) >= 66 else None
        if kind == "bool":
            return bool(int(h, 16))
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
        return {"fn": sig, "value": None, "raw": str(r["result"])[:80], "note": "decode-null (revert?)"}
    return {"fn": sig, "value": v}

def main():
    out = {"address": ADDR, "name": "Golden Agents"}
    out["AGENT_ID_REGISTRY"] = call("AGENT_ID_REGISTRY()", None, "addr")
    v = out["AGENT_ID_REGISTRY"].get("value")
    out["registry_exact_match"] = (v.lower() == REGISTRY.lower()) if v else None
    out["mintActive"] = call("mintActive()", None, "bool")
    out["publicMinted"] = call("publicMinted()", None, "uint")
    out["MAX_PER_WALLET"] = call("MAX_PER_WALLET()", None, "uint")
    out["PUBLIC_MAX"] = call("PUBLIC_MAX()", None, "uint")
    out["TEAM_RESERVE"] = call("TEAM_RESERVE()", None, "uint")
    out["reservedMinted"] = call("reservedMinted()", None, "uint")
    out["mintedBy(user)"] = call("mintedBy(address)", [USER], "uint")
    out["balanceOf(user)"] = call("balanceOf(address)", [USER], "uint")
    out["totalSupply"] = call("totalSupply()", None, "uint")
    out["MAX_SUPPLY"] = call("MAX_SUPPLY()", None, "uint")
    json.dump(out, open(f"{BASE}/backfill-followup-132442705-132446387.json", "w"), indent=1)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
