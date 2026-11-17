"""Run 2026-11-05-1831 (subagent A): route 5c shape-check.
Reads run-2026-11-05-1831-trackc-todo.json (17 ERC-20), S1/S2 sale-shape test
via Sourcify ABI + registry-bytes. READ-ONLY except writing the results JSON
and updating track-c-scan-checked.json (allowed: this job owns that file).
Writes run-2026-11-05-1831-trackc-shape.json.
"""
import json, time, urllib.request, urllib.error
sys_path = __import__("sys")
sys_path.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]

def rpc_call(method, params, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:
            last = e
    raise last

def sourcify_abi(address, tries=4):
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
            time.sleep(4)
        except Exception:
            time.sleep(4)
    return ("error:retry-exhausted", None)

def sale_shape(abi, code_registry_hit):
    if not isinstance(abi, list):
        return {"S1": False, "S2": False, "reason": "no ABI"}
    fns = {i.get("name", ""): i for i in abi if i.get("type") == "function"}
    names = set(fns.keys())
    has_mint = any("mint" in n.lower() for n in names)
    quote_fns = [n for n in names if "quote" in n.lower() or "cost" in n.lower()]
    free_views = [n for n in names if "free" in n.lower() and not n.lower().startswith("freeze")]
    has_gate = ("agentRegistry" in names or "agentId" in names
                or code_registry_hit or any("agentgate" in n.lower() for n in names))
    s1 = bool(has_mint and quote_fns and free_views and has_gate)
    is_token = all(n in names for n in ("name", "symbol", "decimals", "totalSupply"))
    noarg_free = any(n in names for n in ("mintFree",)) or any(
        fns[n].get("inputs") == [] and "free" in n.lower() for n in names)
    s2 = bool(is_token and noarg_free and free_views and has_gate)
    return {"S1": s1, "S2": s2, "has_mint": has_mint, "quote_fns": quote_fns,
            "free_views": sorted(free_views)[:12], "has_gate": has_gate,
            "is_token": is_token, "noarg_free": noarg_free,
            "fn_count": len(fns)}

todo = json.load(open(HF + "run-2026-11-05-1831-trackc-todo.json"))
checked = json.load(open(HF + "track-c-scan-checked.json"))
checked_map = checked.get("checked", {})
out = {}
for e in todo:
    addr = e["address"]
    print(f"== 5c {addr} mints={e['mint_count']} ==", flush=True)
    status, abi = sourcify_abi(addr)
    try:
        code = rpc_call("eth_getCode", [addr, "latest"])
        reg = REG_BYTES in code[2:].lower() if isinstance(code, str) else None
    except Exception as ex:
        reg = "error:" + type(ex).__name__
    shape = sale_shape(abi, reg is True)
    fn_names = sorted({i.get("name", "") for i in abi if i.get("type") == "function"}) if isinstance(abi, list) else None
    out[addr] = {"mint_count_window": e["mint_count"], "minters": e.get("distinct_minters"),
                 "first_block": e.get("first_block"), "last_block": e.get("last_block"),
                 "sourcify": status, "registry_bytes": reg, "shape": shape,
                 "fn_names": fn_names}
    print(f"   sourcify={status} reg={reg} S1={shape.get('S1')} S2={shape.get('S2')}", flush=True)
    checked_map[addr] = {"source": "run-2026-11-05-1831-5c",
                         "status": "checked-sale-shape" if (shape.get("S1") or shape.get("S2")) else "checked-not-sale-shape",
                         "note": f"S1={shape.get('S1')} S2={shape.get('S2')} mint={shape.get('has_mint')} quote={shape.get('quote_fns')} free={shape.get('free_views')} agent={shape.get('has_gate')} token={shape.get('is_token')}"}
    time.sleep(1)

json.dump(out, open(HF + "run-2026-11-05-1831-trackc-shape.json", "w"), indent=1)
checked["checked"] = checked_map
json.dump(checked, open(HF + "track-c-scan-checked.json", "w"), indent=1)
print("WROTE run-2026-11-05-1831-trackc-shape.json + updated track-c-scan-checked.json")
