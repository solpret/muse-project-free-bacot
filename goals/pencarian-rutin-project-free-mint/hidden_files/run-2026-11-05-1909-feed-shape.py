"""Run 2026-11-05-1909 (subagent A, routes 4+5c): Sourcify-feed cross-check.
Shape-check the 15 feed-new contracts (S1/S2 sale shape + NFT agent-shape
indicators from ABI). READ-ONLY. Writes run-2026-11-05-1909-sourcify-shape.json.
"""
import json, time, urllib.request, urllib.error, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
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

feed = json.load(open(HF + "run-2026-11-05-1909-sourcify-feed.json"))
if isinstance(feed, dict): feed = feed.get("results", [])
hot = json.load(open(HF + "hot-leg-seen.json"))
hot_addrs = set()
if isinstance(hot, dict):
    for k, v in hot.items():
        hot_addrs.add(str(k).lower())
        if isinstance(v, dict):
            hot_addrs.update(str(x).lower() for x in v.keys())
        elif isinstance(v, list):
            hot_addrs.update(str(x).lower() for x in v)
out = {"feed_new_shape": {}, "feed_already_hotleg": []}
for it in feed:
    addr = it["address"]
    if addr.lower() in hot_addrs:
        out["feed_already_hotleg"].append(addr)
        continue
    print(f"== feed {addr} {it['verifiedAt']} ==", flush=True)
    status, abi = sourcify_abi(addr)
    try:
        code = rpc_call("eth_getCode", [addr, "latest"])
        reg = REG_BYTES in code[2:].lower() if isinstance(code, str) else None
    except Exception as e:
        reg = "error:" + type(e).__name__
    shape = sale_shape(abi, reg is True)
    fn_names = sorted({i.get("name", "") for i in abi if i.get("type") == "function"}) if isinstance(abi, list) else None
    out["feed_new_shape"][addr] = {
        "verifiedAt": it["verifiedAt"], "sourcify": status,
        "registry_bytes": reg, "shape": shape,
        "fn_names": fn_names,
    }
    print(f"   sourcify={status} reg={reg} S1={shape.get('S1')} S2={shape.get('S2')} fns={shape.get('fn_count')}", flush=True)
    time.sleep(1)

json.dump(out, open(HF + "run-2026-11-05-1909-sourcify-shape.json", "w"), indent=1)
print("WROTE run-2026-11-05-1909-sourcify-shape.json")
