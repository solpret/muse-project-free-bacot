"""Follow-up run 2026-11-05-1731 (subagent A, routes 4+5c): STRICT verification of the
13 first-seen NFT contracts + route 5c shape-check (2 ERC-20) + Sourcify-feed
sale-shape cross-check for feed items NEW vs hot-leg-seen + the 2 feed/scan overlaps.
READ-ONLY. Writes run-2026-11-05-1731-scan-followup.json in cwd."""
import json, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32

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

def block_time(blk):
    try:
        b = rpc_call("eth_getBlockByNumber", [hex(blk), False])
        ts = int(b["timestamp"], 16)
        return time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7 * 3600))
    except Exception as e:
        return f"error:{type(e).__name__}"

def probe_views(addr):
    out = {}
    UP = USER[2:].lower().rjust(64, "0")
    for sig in ["freeRemaining()", "freeLeft()", "freeClaimed()", "freeMinted()",
                "FREE_SUPPLY()", "freeSupply()", "totalMinted()", "maxSupply()",
                "mintOpen()", "totalSupply()", "freePerWallet()", "FREE_PER_WALLET()",
                "FREE_CAP()", "freeAllocation()"]:
        try:
            o = rpc_call("eth_call", [{"to": addr, "data": sel(sig)}, "latest"])
            out[sig] = dec_uint(o)
        except Exception:
            out[sig] = "error:" + type(Exception).__name__
    for sig in ["balanceOf(address)", "mintedBy(address)", "freeMintedBy(address)",
                "freeClaimed(address)", "freeFor(address)", "canFreeMint(address)"]:
        try:
            o = rpc_call("eth_call", [{"to": addr, "data": sel(sig) + UP}, "latest"])
            out[sig] = dec_uint(o)
        except Exception:
            out[sig] = "error:" + type(Exception).__name__
    return out

def earlier_mints(addr, frm=131790000, to=131799644):
    f = frm
    while f <= to:
        cto = min(f + 1999, to)
        params = {"blockchain": "bsc", "fromBlock": hex(f), "toBlock": hex(cto),
                  "pageSize": 1000, "decodeLogs": False,
                  "topics": [TRANSFER, ZERO_TOPIC], "address": addr}
        try:
            body = ankr_post("ankr_getLogs", params, timeout=30)
            logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
        except Exception as e:
            return {"error": f"{f}-{cto}: {type(e).__name__}:{str(e)[:120]}"}
        if logs:
            b = int(logs[0]["blockNumber"], 16)
            return {"earliest_mint_block": b, "earliest_mint_tx": logs[0].get("transactionHash"),
                    "mints_in_chunk": len(logs), "chunk": f"{f}-{cto}"}
        f = cto + 1
        time.sleep(1.5)
    return {"earliest_mint_block": None, "mints_before_window": 0}

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
    is_token = all(x in names for x in ("name", "symbol", "decimals", "totalSupply"))
    noarg_free = any(n in names for n in ("mintFree",)) or any(
        fns[n].get("inputs") == [] and "free" in n.lower() for n in names)
    s2 = bool(is_token and noarg_free and free_views and has_gate)
    return {"S1": s1, "S2": s2, "has_mint": has_mint, "quote_fns": quote_fns,
            "free_views": sorted(free_views)[:12], "has_gate": has_gate,
            "is_token": is_token, "noarg_free": noarg_free,
            "fn_count": len(fns)}

first = json.load(open(HF + "run-2026-11-05-1731-scan-firstseen-raw.json"))
out = {"first_seen_strict": {}, "trackc_5c": {}, "feed_sale_shape": {}}

for c in first:
    addr = c["address"]
    print(f"== {addr} {c['name']} ==", flush=True)
    rec = {"name": c["name"], "symbol": c["symbol"], "kind": c["kind"],
           "window_mints": c["mint_count"], "window_minters": c["distinct_minters"],
           "window_first_block": c["first_block"], "window_last_block": c["last_block"],
           "scan_registry_hit": c["registry_bytes_hit"], "scan_sourcify": c["sourcify"]}
    status, abi = sourcify_abi(addr)
    rec["sourcify_retry"] = status
    if isinstance(abi, list):
        fns = [i.get("name", "") for i in abi if i.get("type") == "function"]
        rec["abi_free_funcs"] = sorted({n for n in fns if "free" in n.lower() and not n.lower().startswith("freeze")})
        rec["abi_mint_funcs"] = sorted({n for n in fns if "mint" in n.lower()})
        rec["abi_fn_count"] = len(fns)
        rec["abi_has_agentRegistry"] = "agentRegistry" in fns
    try:
        code = rpc_call("eth_getCode", [addr, "latest"])
        rec["registry_bytes_direct"] = REG_BYTES in code[2:].lower() if isinstance(code, str) else None
    except Exception as e:
        rec["registry_bytes_direct"] = "error:" + type(e).__name__
    rec["free_views"] = probe_views(addr)
    rec["earlier_mints_131790000_131799644"] = earlier_mints(addr)
    rec["window_first_block_time"] = block_time(c["first_block"])
    em = rec["earlier_mints_131790000_131799644"].get("earliest_mint_block")
    if em:
        rec["earliest_mint_block_time"] = block_time(em)
    out["first_seen_strict"][addr] = rec
    time.sleep(1)

todo = json.load(open(HF + "run-2026-11-05-1731-trackc-todo.json"))
for e in todo:
    addr = e["address"]
    print(f"== 5c {addr} ==", flush=True)
    status, abi = sourcify_abi(addr)
    try:
        code = rpc_call("eth_getCode", [addr, "latest"])
        reg = REG_BYTES in code[2:].lower() if isinstance(code, str) else None
    except Exception:
        reg = "error"
    shape = sale_shape(abi, reg is True)
    out["trackc_5c"][addr] = {"mint_count_window": e["mint_count"], "minters": e["distinct_minters"],
                              "first_block": e["first_block"], "last_block": e["last_block"],
                              "sourcify": status, "registry_bytes": reg, "shape": shape}
    time.sleep(1)

feed = json.load(open(HF + "run-2026-11-05-1731-sourcify-feed.json"))
try:
    hot = json.load(open(HF + "hot-leg-seen.json"))
    hot_addrs = {k.lower() for k in hot.keys()} if isinstance(hot, dict) else set()
except Exception:
    hot_addrs = set()
    out["feed_sale_shape_note"] = "hot-leg-seen.json unreadable; checked all 20 feed items"
scan = json.load(open(HF + "onchain-scan-2026-11-05-1731.json"))
scan_addrs = {c["address"].lower() for c in scan["contracts"]} | \
             {x["address"].lower() for x in scan["erc20_mint_contracts_list"]}
targets = []
for it in feed.get("results", []):
    a = (it.get("address") or "").lower()
    if a and (a not in hot_addrs or a in scan_addrs):
        targets.append(it)
out["feed_targets_count"] = len(targets)
out["feed_targets_note"] = "feed items NEW vs hot-leg-seen OR present in this scan window"
for it in targets:
    addr = it.get("address")
    print(f"== feed {addr} ==", flush=True)
    status, abi = sourcify_abi(addr, tries=3)
    try:
        code = rpc_call("eth_getCode", [addr, "latest"])
        reg = REG_BYTES in code[2:].lower() if isinstance(code, str) else None
    except Exception:
        reg = "error"
    shape = sale_shape(abi, reg is True)
    out["feed_sale_shape"][addr] = {"verifiedAt": it.get("verifiedAt"), "match": it.get("match"),
                                    "in_scan_window": addr.lower() in scan_addrs,
                                    "in_hot_leg_seen": addr.lower() in hot_addrs,
                                    "sourcify": status, "registry_bytes": reg, "shape": shape}
    time.sleep(1)

json.dump(out, open(HF + "run-2026-11-05-1731-scan-followup.json", "w"), indent=1)
print("WROTE run-2026-11-05-1731-scan-followup.json")
