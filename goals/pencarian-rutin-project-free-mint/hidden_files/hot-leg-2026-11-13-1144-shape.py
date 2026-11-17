#!/usr/bin/env python3
"""Hot-leg 1144 follow-up: full S1/S2 shape-check (Sourcify ABI, ?fields=abi)
for the 2 probe-possible-sale contracts from the 1144 feed poll. First time a
hot-leg run produced probe-possible-sale (no precedent in 2026-11-13 runs).
Probe is coarse: it misses agentIdRegistry (Zero uses that name) and does not
check mint/quote functions, so a probe-possible verdict MUST be settled by ABI
before any lead verdict. Read-only except hot-leg-seen.json status update for
these 2 contracts + this output file. If shape passes, verify on-chain free
pool + user slot + age views; age-unverified -> watchlist-only, never a lead."""
import json, subprocess, time
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
TARGETS = ["0x9dE070e1a68789748799e36D9A52e976Cd371723",
           "0x36fE923C449F6163a601058626dEf6c83a8f23AE"]
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed"}
REGISTRY_FNS = {"agentRegistry", "agentIdRegistry", "AGENT_ID_REGISTRY"}
QUOTE_FNS = {"price", "quote", "cost", "getPrice", "mintPrice", "getQuote"}

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def curl(url, data=None, timeout=20):
    cmd = ["curl", "-sS", "-m", str(timeout), "-A", "Mozilla/5.0"]
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", data]
    cmd.append(url)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        return p.stdout if p.returncode == 0 and p.stdout else None
    except Exception:
        return None

def now_wib():
    return time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time() + 7 * 3600))

t0 = time.time()
out = {"run": "free-mint-hot-leg 2026-11-13 11:44 WIB shape follow-up",
       "started_wib": now_wib(), "targets": TARGETS}
results = {}

for addr in TARGETS:
    r = {"address": addr}
    body = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=20)
    if not body:
        r["abi"] = "fetch-failed"
        results[addr] = r
        continue
    try:
        meta = json.loads(body)
        abi = meta.get("abi", [])
    except Exception as e:
        r["abi"] = f"parse-failed: {e}"
        results[addr] = r
        continue
    fns = {}
    for item in abi:
        if item.get("type") == "function":
            fns.setdefault(item["name"], []).append(item)
    r["fn_count"] = len(fns)
    r["fn_names"] = sorted(fns.keys())
    # S1: mint + quote/cost + free view + registry/AgentGate
    has_mint = any(n in fns for n in ("mint", "mintFree", "claimFree", "mintAgent"))
    has_quote = any(n in fns for n in QUOTE_FNS)
    free_views = sorted(set(fns) & FREE_VIEWS)
    has_registry = bool(set(fns) & REGISTRY_FNS)
    has_gate = any("gate" in n.lower() or "agent" in n.lower() for n in fns)
    r["s1"] = {"has_mint": has_mint, "has_quote": has_quote,
               "free_views": free_views, "has_registry": has_registry,
               "has_agent_or_gate_fn": has_gate,
               "pass": bool(has_mint and has_quote and free_views and has_registry)}
    # S2: token fns + no-arg mintFree + free views + FREE_SLOTS/FREE_SUPPLY + registry
    token_fns = sorted(set(fns) & {"name", "symbol", "decimals", "totalSupply"})
    mintfree_noarg = any(len(it.get("inputs", [])) == 0
                         for it in fns.get("mintFree", []))
    free_consts = sorted(set(fns) & {"FREE_SLOTS", "FREE_SUPPLY", "FREE_AMOUNT", "FREE_CAP", "FREE_MAX"})
    r["s2"] = {"token_fns": token_fns, "mintFree_noarg": mintfree_noarg,
               "free_views": free_views, "free_consts": free_consts,
               "has_registry": has_registry,
               "pass": bool(len(token_fns) == 4 and mintfree_noarg and free_views
                            and free_consts and has_registry)}
    r["shape"] = "S1" if r["s1"]["pass"] else ("S2" if r["s2"]["pass"] else "not-sale-shape")
    results[addr] = r

# On-chain verify only for shape-passing contracts
shape_pass = [a for a, r in results.items() if r.get("shape") in ("S1", "S2")]
if shape_pass:
    calls, keys = [], []
    for addr in shape_pass:
        r = results[addr]
        views = []
        if r["shape"] == "S1":
            views = [("freeSharesRemaining", False), ("freeClaimed", False),
                     ("freeMinted", False), ("freeLeft", False),
                     ("freeAvailable", False), ("mintOpen", False), ("saleOpen", False),
                     ("freeClaimed", True), ("quote", True)]
            # quote(user,1): quote(address,uint256) selector differs; handled below
            views = views[:-1]
        else:
            views = [("freeMinted", False), ("FREE_SLOTS", False), ("FREE_SUPPLY", False),
                     ("freeClaimed", True), ("mintOpen", False)]
        for fn, uarg in views:
            if fn == "quote":
                continue
            data = sel(fn + ("(address)" if uarg else "()")) + (USER_PAD if uarg else "")
            calls.append({"jsonrpc": "2.0", "id": len(calls), "method": "eth_call",
                          "params": [{"to": addr, "data": data}, "latest"]})
            keys.append((addr, fn + ("_user" if uarg else "")))
        for fn in ("mintOpensAt", "mintStart", "openedAt", "freeStart", "launchTime"):
            calls.append({"jsonrpc": "2.0", "id": len(calls), "method": "eth_call",
                          "params": [{"to": addr, "data": sel(fn + "()")}, "latest"]})
            keys.append((addr, fn))
    # chunked <=24
    reads = {}
    for i in range(0, len(calls), 24):
        chunk = calls[i:i + 24]
        body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(chunk), timeout=30)
        if not body:
            continue
        try:
            resp = json.loads(body)
            items = resp if isinstance(resp, list) else [resp]
            by_id = {it.get("id"): it for it in items if isinstance(it, dict)}
            for c in chunk:
                it = by_id.get(c["id"], {})
                res = it.get("result")
                addr, fn = keys[c["id"]]
                v = None
                if res and res != "0x" and len(res) >= 66:
                    try:
                        v = int(res[-64:], 16)
                    except Exception:
                        v = None
                reads.setdefault(addr, {})[fn] = v
        except Exception:
            pass
    for addr in shape_pass:
        results[addr]["onchain"] = reads.get(addr, {})
        oc = reads.get(addr, {})
        pool = None
        for k in ("freeSharesRemaining", "freeLeft", "freeAvailable"):
            if oc.get(k) is not None:
                pool = oc[k]
                break
        if pool is None and oc.get("freeMinted") is not None and oc.get("FREE_SLOTS") is not None:
            pool = oc["FREE_SLOTS"] - oc["freeMinted"]
        if pool is None and oc.get("freeMinted") is not None and oc.get("FREE_SUPPLY") is not None:
            pool = oc["FREE_SUPPLY"] - oc["freeMinted"]
        results[addr]["free_pool_remaining"] = pool
        results[addr]["user_slot_open"] = (oc.get("freeClaimed_user") == 0)
        age_views = {k: oc.get(k) for k in ("mintOpensAt", "mintStart", "openedAt", "freeStart", "launchTime") if oc.get(k)}
        results[addr]["age_views"] = age_views
        results[addr]["age_verified"] = bool(age_views)
        results[addr]["verdict"] = ("shape-pass-age-unverified-watchlist-only"
                                    if not age_views else "shape-pass-age-view-present-needs-main-job")

out["results"] = results
out["shape_pass"] = shape_pass

# Update hot-leg-seen.json statuses for these 2 contracts
seen = json.load(open(f"{HF}/hot-leg-seen.json"))
for addr in TARGETS:
    r = results[addr]
    if addr in seen:
        seen[addr]["status"] = r.get("shape", r.get("abi", "unknown"))
        seen[addr]["shape_detail"] = json.dumps({k: r.get(k) for k in ("s1", "s2", "verdict", "free_pool_remaining", "user_slot_open")})[:600]
json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{HF}/hot-leg-2026-11-13-1144-shape.json", "w"), indent=1)
print(json.dumps(out, indent=1))
