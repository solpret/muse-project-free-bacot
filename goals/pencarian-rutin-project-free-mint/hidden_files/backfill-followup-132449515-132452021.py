#!/usr/bin/env python3
"""UNIT-BOT follow-up, backfill run 2026-11-09 ~02:46 WIB.
Read-only. Triage utama GAGAL total (fast_rpc semua endpoint timeout +
Sourcify curl rc=28). Scan sendiri mencatat: registry_bytes_hit=false,
sourcify=error RemoteDisconnected, free_shaped=[], mint_funcs=[].
Follow-up retry: Sourcify ABI via curl (3x), eth_getCode registry-bytes
(4x fast_rpc), first-block timestamp (4x + curl dataseed fallback),
owner() (4x), lalu agentRegistry()/free views bila ABI tersedia.
Tulis backfill-followup-132449515-132452021.json. No preview/mint/sign.
"""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0xD800eFB5F2F44B6aFB0CDe553E885390a7D38156"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
REG_HEX = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FIRST_BLOCK = 132451566

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

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    last = None
    for _ in range(3):
        try:
            r = subprocess.run(["curl", "-s", "-m", "25", "-A",
                                "free-bacot-backfill-triage/1.0", url],
                               capture_output=True, text=True, timeout=40)
            if r.returncode != 0:
                last = f"curl rc={r.returncode} {r.stderr[:120]}"
                time.sleep(3)
                continue
            return json.loads(r.stdout), None
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
            time.sleep(3)
    return None, last

def block_ts(blk):
    last = None
    for i in range(4):
        try:
            b = race("eth_getBlockByNumber", [hex(blk), False])
            ts = int(b["timestamp"], 16)
            return {"block": blk, "timestamp": ts,
                    "wib": time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7 * 3600))}
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:120]}"
            time.sleep(4)
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
    out = {"address": ADDR, "name": "UNIT-BOT", "first_block": FIRST_BLOCK}
    out["first_block_ts"] = block_ts(FIRST_BLOCK)
    data, err = fetch_abi(ADDR)
    abi = None
    names = set()
    if data is not None:
        abi = data.get("abi")
        if abi is None and isinstance(data.get("stdJson"), dict):
            abi = data["stdJson"].get("abi")
    if abi is not None:
        out["sourcify"] = data.get("match") or "verified"
        fns = [e for e in abi if isinstance(e, dict) and e.get("type") == "function"]
        names = {f.get("name", "") for f in fns}
        out["abi_fn_count"] = len(fns)
        out["abi_fn_names"] = sorted(names)
    elif data is not None:
        out["sourcify"] = "not_verified"
    else:
        out["sourcify"] = f"transport-failed: {err}"
    # registry bytes via eth_getCode, retried
    code = None
    last = None
    for i in range(4):
        try:
            code = race("eth_getCode", [ADDR, "latest"])
            break
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:120]}"
            time.sleep(4)
    if isinstance(code, str) and code.startswith("0x"):
        out["code_registry_bytes_hit"] = REG_HEX in code.lower()
        out["code_len"] = len(code)
    else:
        out["code_registry_bytes_hit"] = None
        out["code_error"] = last or str(code)[:200]
    if "agentRegistry" in names or out.get("code_registry_bytes_hit"):
        r = call("agentRegistry()", None, "addr")
        out["agentRegistry"] = r
        out["agentRegistry_exact_match"] = (r.get("value") == REGISTRY.lower()) if r.get("value") else False
    out["agent_shaped"] = bool(out.get("agentRegistry_exact_match")) or bool(out.get("code_registry_bytes_hit"))
    out["owner"] = call("owner()", None, "addr")
    if names:
        for sig, kind in [("name()", "str"), ("symbol()", "str"), ("totalSupply()", "uint"),
                          ("MAX_SUPPLY()", "uint"), ("mintOpen()", "bool"),
                          ("totalMinted()", "uint"), ("price()", "uint"), ("mintPrice()", "uint")]:
            if sig.split("(")[0] in names:
                out[sig.split("(")[0]] = call(sig, None, kind)
    discards = json.load(open(f"{BASE}/same-owner-discards.json"))
    discard_owners = {r.get("owner", "").lower() for r in discards if isinstance(r, dict)}
    ov = out.get("owner", {}).get("value") if isinstance(out.get("owner"), dict) else None
    out["owner_in_discards"] = (ov.lower() in discard_owners) if ov else None
    json.dump(out, open(f"{BASE}/backfill-followup-132449515-132452021.json", "w"), indent=1)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
