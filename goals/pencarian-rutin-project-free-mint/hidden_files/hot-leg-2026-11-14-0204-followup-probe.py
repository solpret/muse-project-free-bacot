#!/usr/bin/env python3
"""Hot-leg 0204 follow-up: probe the 4 feed-new contracts the main run's
12-target probe cap missed (probe_capped=3 by script accounting; actually 4
unprobed: 76E0, 8b5c, 4a2A, 0d29). Same 13 selectors, chunked <=24 calls.
Updates their hot-leg-seen.json status (written by this run) + writes a
follow-up JSON. Read-only otherwise."""
import json, subprocess, time
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TARGETS = ["0x76E0471d81D1D4027046b8d381E6a064CeC9c0e4",
           "0x8b5ca265B7FAf150839E9ab47D1354f245868c5e",
           "0x4a2A838eeCf26614C25886281FAF1b54683660bc",
           "0x0d29a23fe8C6AFAFD2237CbF812a5b1D7FE6ab44"]
PROBE = ["freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
         "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY", "agentRegistry",
         "AGENT_ID_REGISTRY", "AGENT_REGISTRY", "saleOpen", "mintOpen", "totalSupply"]
FREE_SET = {"freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
            "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY"}

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def curl(url, data=None, timeout=15):
    cmd = ["curl", "-sS", "-m", str(timeout), "-A", "Mozilla/5.0"]
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", data]
    cmd.append(url)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        return p.stdout if p.returncode == 0 and p.stdout else None
    except Exception:
        return None

def rpc_chunked(calls, timeout=20):
    out = []
    for i in range(0, len(calls), 24):
        chunk = calls[i:i + 24]
        body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(chunk), timeout=timeout)
        if not body:
            body = curl("https://bsc-dataseed1.defibit.io/", data=json.dumps(chunk), timeout=timeout)
        if not body:
            out += [(c["id"], None, "fetch-failed") for c in chunk]
            continue
        try:
            resp = json.loads(body)
            items = resp if isinstance(resp, list) else [resp]
            by_id = {it.get("id"): it for it in items if isinstance(it, dict)}
            for c in chunk:
                it = by_id.get(c["id"], {})
                out.append((c["id"], it.get("result"), it.get("error")))
        except Exception as e:
            out += [(c["id"], None, f"parse-failed: {e}") for c in chunk]
    return out

def now_wib():
    return time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time() + 7 * 3600))

t0 = time.time()
calls, keys = [], []
for a in TARGETS:
    for fn in PROBE:
        calls.append({"jsonrpc": "2.0", "id": len(calls), "method": "eth_call",
                      "params": [{"to": a, "data": sel(fn + "()")}, "latest"]})
        keys.append((a, fn))
hits = {}
for cid, r, err in rpc_chunked(calls, timeout=20):
    if r and isinstance(r, str) and len(r) >= 66 and not err:
        a, fn = keys[cid]
        hits.setdefault(a, []).append(fn)
status, abi_shape = {}, {}
for a in TARGETS:
    h = hits.get(a, [])
    free_hit = any(x in FREE_SET for x in h)
    agent_hit = any(x in ("agentRegistry", "AGENT_ID_REGISTRY", "AGENT_REGISTRY") for x in h)
    sale_hit = any(x in ("saleOpen", "mintOpen") for x in h)
    possible = bool(free_hit and (agent_hit or sale_hit))
    status[a] = {"hits": h, "free_hit": free_hit, "agent_hit": agent_hit,
                 "sale_hit": sale_hit,
                 "status": "probe-possible-sale" if possible else "probe-not-sale-shape"}
    if possible:
        try:
            mj = json.loads(curl(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", timeout=15) or "{}")
            abi = mj.get("abi") or []
            fns = [f.get("name") for f in abi if f.get("type") == "function"]
            has_mint = any(n in fns for n in ("mint", "mintFree", "claimFree", "claim"))
            has_quote = any(n in fns for n in ("quote", "price", "cost", "getQuote"))
            free_views = [n for n in fns if n in ("freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft", "freeAvailable", "freeFor", "freeUsed", "freeSharePoolExhausted", "freeSharesClaimed")]
            agent = any(n in fns for n in ("agentIdRegistry", "agentRegistry", "AGENT_ID_REGISTRY")) or "AgentGate" in json.dumps(abi)
            token = all(n in fns for n in ("name", "symbol", "decimals", "totalSupply"))
            abi_shape[a] = {"fns": len(fns), "mint": has_mint, "quote": has_quote,
                            "free_views": free_views, "agent": agent, "token_on_same": token,
                            "S1": bool(has_mint and has_quote and free_views and agent),
                            "S2": bool(token and "mintFree" in fns and free_views and agent)}
        except Exception as e:
            abi_shape[a] = {"error": str(e)[:120]}

seen = json.load(open(f"{HF}/hot-leg-seen.json"))
for a in TARGETS:
    if a in seen:
        seen[a]["status"] = status[a]["status"]
        seen[a]["note"] = json.dumps(status[a].get("hits", []))[:400] + " (followup probe 0204)"
json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)
out = {"run": "free-mint-hot-leg 2026-11-14 02:04 WIB followup-probe",
       "started_wib": now_wib(), "targets": TARGETS, "probe": status,
       "abi_shape": abi_shape, "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-14-0204-followup-probe.json", "w"), indent=1)
print(json.dumps(out, indent=1))
