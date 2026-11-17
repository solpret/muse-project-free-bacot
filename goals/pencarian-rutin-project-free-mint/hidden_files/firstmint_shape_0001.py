#!/usr/bin/env python3
"""First-mint + agent-shape checks, run 0001 (2026-11-06 00:01 WIB). Read-only.
- Ankr getLogs address-filtered, pageSize 1, earliest Transfer-from-zero.
- Sourcify ABI: agent-shape (registry/AgentGate/free-mint fns) + free-view names.
- eth_getCode registry-bytes hit.
A failed read is None / error, never zero."""
import json, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post

EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
REGISTRY_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FROM_BLOCK = 131060000

TARGETS = {
    "Night Shift": "0x427aed3f7427b48e45f5e648105aa1b77724cf14",
    "Cuprihive": "0x1e9460475825a3218cd36b8d35a0698d6939aaec",
    "Skyagent": "0x83decf8076d04d59da771da6bb298132164be55b",
    "Rookling": "0xe76a5bf585f9378b065d48f1a49d90ecf71ebeba",
    "Flyingsquirrelai": "0x9e14822255f2f287f5ef233e4cf8580481dcf75e",
    "PRICKLY": "0x4e557ae3824ae3e837aa4a8da2a45a04501beaee",
    "unicorn.exe": "0x965286f9662a6dACeFf9bD3C4D58ABaBDD9C87A5",
    "Blend In": "0x9ca2c07b67cd97109f40378ae90c815feb878b1f",
    "Buzzkill": "0x4854ce8e3ec3a1acb0dd4eae3f547e5a214c2a0d",
}

def rpc_call(method, params, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:
            last = e
    raise last

def block_ts(blocknum):
    try:
        b = rpc_call("eth_getBlockByNumber", [hex(blocknum), False], 10)
        return int(b["timestamp"], 16)
    except Exception as e:
        return f"error:{str(e)[:80]}"

def first_mint_ankr(addr, head):
    params = {"blockchain": "bsc", "fromBlock": hex(FROM_BLOCK), "toBlock": hex(head),
              "address": addr, "pageSize": 1, "decodeLogs": False,
              "topics": [TRANSFER, ZERO_TOPIC]}
    try:
        body = ankr_post("ankr_getLogs", params, timeout=30)
    except Exception as e:
        return {"error": f"ankr:{str(e)[:120]}"}
    logs = body.get("logs", []) if isinstance(body, dict) else []
    if not logs:
        return {"first_mint": None, "note": "no Transfer-from-zero logs in range (address filter may be unsupported or no mints)"}
    first = logs[0]
    fb = int(first["blockNumber"], 16)
    # confirm nothing earlier: query [FROM_BLOCK, fb-1]
    params2 = dict(params); params2["toBlock"] = hex(fb - 1)
    try:
        body2 = ankr_post("ankr_getLogs", params2, timeout=30)
        earlier = body2.get("logs", []) if isinstance(body2, dict) else []
    except Exception as e:
        earlier = f"error:{str(e)[:80]}"
    return {"first_block": fb, "first_tx": first.get("transactionHash"),
            "earlier_in_range": (len(earlier) if isinstance(earlier, list) else earlier)}

def sourcify_abi(address, tries=3):
    url = f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"
    for i in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode())
                return ("verified", data.get("abi"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ("not_verified", None)
            time.sleep(3)
        except Exception:
            time.sleep(3)
    return ("error:retry-exhausted", None)

def code_registry_hit(addr):
    try:
        code = rpc_call("eth_getCode", [addr, "latest"], 10)
        if isinstance(code, str):
            return REGISTRY_BYTES in code.lower()
        return None
    except Exception as e:
        return f"error:{str(e)[:80]}"

def main():
    head = int(rpc_call("eth_blockNumber", [], 10), 16)
    print("head:", head)
    out = {}
    for label, addr in TARGETS.items():
        r = {"address": addr}
        r["registry_bytes"] = code_registry_hit(addr)
        status, abi = sourcify_abi(addr)
        r["sourcify"] = status
        if isinstance(abi, list):
            funcs = [it.get("name", "") for it in abi if it.get("type") == "function"]
            low = [f.lower() for f in funcs]
            r["functions"] = len(funcs)
            r["agent_gate_fns"] = [f for f in funcs if any(g in f.lower() for g in ("agentid", "agentregistry", "agentgate", "hasagentid", "isagent"))]
            r["mint_fns"] = [f for f in funcs if "mint" in f.lower()]
            r["free_views"] = [f for f in funcs if any(g in f.lower() for g in ("free",))]
            r["quote_fns"] = [f for f in funcs if f.lower().startswith(("quote", "cost", "price"))]
            r["agent_shaped"] = bool(r["agent_gate_fns"]) and bool(r["mint_fns"])
        fm = first_mint_ankr(addr, head)
        r["first_mint"] = fm
        if isinstance(fm.get("first_block"), int):
            ts = block_ts(fm["first_block"])
            r["first_mint_ts"] = ts
            if isinstance(ts, int):
                r["first_mint_wib"] = time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7 * 3600))
        out[label] = r
        print(label, "| registry_bytes:", r["registry_bytes"], "| sourcify:", status,
              "| agent_shaped:", r.get("agent_shaped"), "| first:", fm.get("first_block"),
              r.get("first_mint_wib", ""))
    json.dump(out, open("firstmint-shape-2026-11-06-0001.json", "w"), indent=1)
    print("wrote firstmint-shape-2026-11-06-0001.json")

if __name__ == "__main__":
    main()
