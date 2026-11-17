"""Route 5c track-C ERC-20 backlog shape-check, run 2026-11-05 1631. Read-only.
S1: mint fn + quote/cost fn + free-share view + registry ref/AgentGate.
S2: contract IS the token + no-arg free-mint fn + free views + registry ref/AgentGate.
All elements required. Records newly checked addresses in track-c-scan-checked.json.
"""
import json, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from eth_hash.auto import keccak

REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
REGISTRY_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
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

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def dec_uint(out):
    if not isinstance(out, str) or not out.startswith("0x") or len(out) < 66:
        return None
    try:
        return int(out[2:66], 16)
    except Exception:
        return None

def dec_str(out):
    if not isinstance(out, str) or not out.startswith("0x"):
        return None
    try:
        raw = bytes.fromhex(out[2:])
    except Exception:
        return None
    if len(raw) >= 64:
        try:
            ln = int.from_bytes(raw[32:64], "big")
            if 0 < ln <= len(raw) - 64:
                return raw[64:64 + ln].decode("utf-8", "replace")
        except Exception:
            pass
    if len(raw) == 32:
        return raw.rstrip(b"\x00").decode("utf-8", "replace") or None
    return None

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

FREE_SHARE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
                    "freeUsed", "freeAvailable", "freeSharePoolExhausted",
                    "freeSharesClaimed", "freeMinted", "freeRemaining"]
QUOTE_FNS = ["quote", "quoteFor", "quoteMint", "quoteMintFor", "cost", "costFor",
             "getCost", "price", "mintPrice", "feeFor"]
MINT_FNS = ["mint", "mintFree", "claimFreeShare", "claimShare", "mintShare"]
GATE_WORDS = ["agentid", "agentregistry", "agentgate", "hasagentid", "isagent"]

TODO = json.load(open("/tmp/todo5c.json"))
SCAN = json.load(open("onchain-scan-2026-11-05-1631.json"))
SCANMAP = {e["address"].lower(): e for e in SCAN["erc20_mint_contracts_list"]}

results = []
for addr in TODO:
    r = {"address": addr, "scan": SCANMAP.get(addr.lower(), {})}
    status, abi = sourcify_abi(addr)
    r["sourcify"] = status
    funcs = []
    if isinstance(abi, list):
        for item in abi:
            if item.get("type") == "function":
                funcs.append(item.get("name", ""))
    r["function_count"] = len(funcs)
    low = [f.lower() for f in funcs]
    r["has_mint_fn"] = any(f.lower() in ("mint", "mintfree", "claimfreeshare", "claimshare", "mintshare")
                           or "mint" in f.lower() for f in funcs)
    r["mint_fns"] = sorted(set(f for f in funcs if "mint" in f.lower()))
    r["quote_fns"] = sorted(set(f for f in funcs
                                if f.lower() in [q.lower() for q in QUOTE_FNS]
                                or f.lower().startswith("quote") or f.lower().startswith("cost")))
    r["free_share_views"] = sorted(set(f for f in funcs
                                       if f.lower() in [v.lower() for v in FREE_SHARE_VIEWS]))
    r["gate_fns"] = sorted(set(f for f in funcs
                               if any(g in f.lower() for g in GATE_WORDS)))
    # registry reference: ABI text contains registry address, or gate fns, or code bytes
    abi_text = json.dumps(abi).lower() if abi else ""
    r["registry_in_abi"] = REGISTRY.lower() in abi_text or "60b9262456de011f7d15a54cdd8c48baaa8b022f" in abi_text
    try:
        code = rpc_call("eth_getCode", [addr, "latest"])
        r["registry_bytes_direct"] = REGISTRY_BYTES in code[2:].lower() if isinstance(code, str) else None
        r["code_len"] = len(code) - 2 if isinstance(code, str) else None
    except Exception as e:
        r["registry_bytes_direct"] = None
        r["code_error"] = type(e).__name__
    r["agent_gate"] = bool(r["gate_fns"]) or bool(r.get("registry_in_abi")) or bool(r.get("registry_bytes_direct"))
    # S2 token check: name/symbol/decimals/totalSupply respond
    tok = {}
    for sig, key in (("name()", "name"), ("symbol()", "symbol"),
                     ("decimals()", "decimals"), ("totalSupply()", "totalSupply")):
        try:
            o = rpc_call("eth_call", [{"to": addr, "data": sel(sig)}, "latest"])
            tok[key] = dec_str(o) if key in ("name", "symbol") else dec_uint(o)
        except Exception:
            tok[key] = None
    r["token_views"] = tok
    r["is_token"] = all(tok.get(k) is not None for k in ("name", "symbol", "decimals", "totalSupply"))
    r["noarg_free_mint_fn"] = any(f in ("mintFree", "mintfree") for f in funcs)
    r["s1_pass"] = bool(r["has_mint_fn"] and r["quote_fns"] and r["free_share_views"] and r["agent_gate"])
    r["s2_pass"] = bool(r["is_token"] and r["noarg_free_mint_fn"] and r["free_share_views"] and r["agent_gate"])
    r["shape_pass"] = bool(r["s1_pass"] or r["s2_pass"])
    results.append(r)
    print(json.dumps(r, indent=1))
    time.sleep(1)

# record newly checked addresses
chk = json.load(open("track-c-scan-checked.json"))
n_new = 0
for r in results:
    key = r["address"].lower()
    if key not in chk["checked"]:
        chk["checked"][key] = {"source": "run-2026-11-05-1631-5c",
                               "shape_pass": r["shape_pass"],
                               "sourcify": r["sourcify"],
                               "mint_count_window": r["scan"].get("mint_count")}
        n_new += 1
json.dump(chk, open("track-c-scan-checked.json", "w"), indent=1)
print("checked file: added", n_new, "total now", len(chk["checked"]))

out = {"run": "2026-11-05-1631", "candidates_considered": 69,
       "already_checked_skipped": 67, "newly_shape_checked": len(results),
       "passes": [r["address"] for r in results if r["shape_pass"]],
       "results": results}
json.dump(out, open("run-2026-11-05-1631-trackc-shape.json", "w"), indent=1)
print("WROTE run-2026-11-05-1631-trackc-shape.json")
