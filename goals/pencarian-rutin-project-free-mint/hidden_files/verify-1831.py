#!/usr/bin/env python3
"""Minimal on-chain verify for run 1831 genuinely-new addresses:
- BUNNY token 0x5D28C44bAd17d75D2207C4A042b73AF5297971C2 (from HOPKIN post)
- Vorn Agent 0x978c968a371f6adf98abe32915fae09111d11293 (dieuxuan50 author page)
Sourcify v2 status + eth_call name/symbol/totalSupply + eth_getCode + Ankr recent mints.
Read-only; writes verify-1831.json next to this script."""
import sys, json, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import race, _single
from ankr import ankr_post

ADDRS = {
    "BUNNY": "0x5D28C44bAd17d75D2207C4A042b73AF5297971C2",
    "VornAgent": "0x978c968a371f6adf98abe32915fae09111d11293",
}
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

def sourcify(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}"
    req = urllib.request.Request(url, headers={"User-Agent": "curl"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.load(r)
            st = d.get("stdJson", {}) or {}
            return {"http": r.status, "match": d.get("match"), "matchType": (st.get("matchType") if isinstance(st, dict) else None),
                    "creationMatch": d.get("creationMatch"), "runtimeMatch": d.get("runtimeMatch"),
                    "name": d.get("name"), "stdJsonKeys": list(st.keys())[:5] if isinstance(st, dict) else None}
    except urllib.error.HTTPError as e:
        return {"http": e.code, "match": None}
    except Exception as e:
        return {"http": None, "error": type(e).__name__, "msg": str(e)[:150]}

def call(addr, data):
    try:
        r = _single("https://bsc-dataseed1.bnbchain.org/", "eth_call", [{"to": addr, "data": data}, "latest"], 15, retries=0)
        return r
    except Exception as e:
        return f"ERR {type(e).__name__}: {str(e)[:120]}"

def decode_str(hexdata):
    try:
        b = bytes.fromhex(hexdata[2:])
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96+ln].decode("utf-8", "replace")
    except Exception:
        return None

out = {}
head_n = int(race("eth_blockNumber", [], timeout=10), 16)
out["head"] = head_n
for label, addr in ADDRS.items():
    e = {"address": addr}
    e["sourcify"] = sourcify(addr)
    e["code"] = call(addr, None) if False else None
    try:
        code = _single("https://bsc-dataseed1.bnbchain.org/", "eth_getCode", [addr, "latest"], 15, retries=0)
        e["code_len"] = (len(code) - 2) // 2 if code.startswith("0x") else None
        e["has_code"] = e["code_len"] not in (None, 0)
    except Exception as ex:
        e["code_err"] = str(ex)[:120]
    ts = call(addr, "0x18160ddd")
    e["totalSupply_raw"] = ts
    try:
        e["totalSupply"] = int(ts, 16)
    except Exception:
        e["totalSupply"] = None
    nm = call(addr, "0x06fdde03")
    e["name"] = decode_str(nm) if isinstance(nm, str) and nm.startswith("0x") and len(nm) > 130 else nm
    sy = call(addr, "0x95d89b41")
    e["symbol"] = decode_str(sy) if isinstance(sy, str) and sy.startswith("0x") and len(sy) > 130 else sy
    # agent-shape hints: try agentRegistry() 0x... selector? use Sourcify ABI if available
    e["agent_shape"] = "not-checked-abi"
    try:
        url = f"https://sourcify.dev/server/v2/contract/56/{addr}"
        req = urllib.request.Request(url, headers={"User-Agent": "curl"})
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.load(r)
            abi = (d.get("stdJson", {}) or {}).get("abi") or d.get("abi") or []
            fns = [f.get("name") for f in abi if isinstance(f, dict) and f.get("type") == "function"]
            e["abi_functions"] = len(fns)
            e["functions_sample"] = fns[:80]
            reg = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F".lower()
            e["registry_ref_in_abi"] = any("agent" in (f or "").lower() for f in fns)
            e["has_free_fn"] = [f for f in fns if f and ("free" in f.lower() or "claim" in f.lower())]
            e["has_agent_fn"] = [f for f in fns if f and "agent" in f.lower()]
    except Exception as ex:
        e["abi_err"] = f"{type(ex).__name__}: {str(ex)[:120]}"
    for window in (20000, 100000):
        try:
            params = {"blockchain": "bsc", "fromBlock": hex(head_n - window), "toBlock": hex(head_n),
                      "address": [addr], "topics": [TRANSFER, ZERO], "pageSize": 5, "descOrder": True}
            body = ankr_post("ankr_getLogs", params, timeout=30)
            logs = (body.get("result", {}) or {}).get("logs", []) or []
            e[f"mints_last_{window}"] = len(logs)
            e[f"mints_last_{window}_blocks"] = [int(l["blockNumber"], 16) for l in logs]
        except Exception as ex:
            e[f"mints_last_{window}_err"] = f"{type(ex).__name__}: {str(ex)[:150]}"
    out[label] = e
    print(label, json.dumps(e, indent=1)[:1500], flush=True)

with open("verify-1831.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("WROTE verify-1831.json")
