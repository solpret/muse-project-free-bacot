#!/usr/bin/env python3
"""Hot-leg 0109 follow-up: probe shape-check the 11 salvage feed contracts
(recorded 01:08 as shape-check-pending, never probed; 0109 main run only
probed FROST since feed_new was empty). Chunked <=24 calls. Updates
hot-leg-seen.json statuses only for these 11."""
import json, subprocess, time
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TARGETS = [
 "0x660258a6608Abb3B1E865384612F1abc15c06c48",
 "0xA324dd980F04b5b93aC6945CE3F925d3c1D76aa5",
 "0x4f5A250f42CC82CcC4B272e7b16eB3eFEc4b24B3",
 "0x7D0004acfD131De1751D74c1aC237ae51bB32045",
 "0xB061fbA11cba355aC267cB9F99083ede96d66C48",
 "0xFCEde15610Ebd5ff76b58604db437aB45A3f3dDe",
 "0x2293579445a7f4092c3faEc414abe75D0530566B",
 "0xc7642BA97fB6af41c84C5A838FD7Bc99731a68B6",
 "0x46b659e2fc2B8dD0C6FCB7dD444C9aD39575c136",
 "0x219f6e5a1DF0a891350aB085827eFc1F4e634b73",
 "0xDBA7769bba18549911D6f942e8767fDc944a1E83",
]
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

t0 = time.time()
out = {"run": "free-mint-hot-leg 2026-11-14 01:09 WIB followup-probe",
       "started_wib": time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time() + 7 * 3600))}
PROBE = ["freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
         "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY", "agentRegistry",
         "AGENT_ID_REGISTRY", "AGENT_REGISTRY", "saleOpen", "mintOpen", "totalSupply"]
FREE_SET = {"freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
            "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY"}
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
status = {}
for a in TARGETS:
    h = hits.get(a, [])
    free_hit = any(x in FREE_SET for x in h)
    agent_hit = any(x in ("agentRegistry", "AGENT_ID_REGISTRY", "AGENT_REGISTRY") for x in h)
    sale_hit = any(x in ("saleOpen", "mintOpen") for x in h)
    possible = bool(free_hit and (agent_hit or sale_hit))
    status[a] = {"hits": h, "free_hit": free_hit, "agent_hit": agent_hit,
                 "sale_hit": sale_hit,
                 "status": "probe-possible-sale" if possible else "probe-not-sale-shape"}
out["probe"] = status
# ABI shape-check for any probe-possible
abi_shape = {}
for a in TARGETS:
    if status[a]["status"] == "probe-possible-sale":
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
out["abi_shape"] = abi_shape
# Update seen statuses
seen = json.load(open(f"{HF}/hot-leg-seen.json"))
for a in TARGETS:
    st = status[a]
    ab = abi_shape.get(a, {})
    note = f"probe hits={st['hits']}; free={st['free_hit']} agent={st['agent_hit']} sale={st['sale_hit']}"
    if ab:
        note += f"; ABI S1={ab.get('S1')} S2={ab.get('S2')} fns={ab.get('fns')}"
    seen[a] = {"first_seen_wib": seen[a].get("first_seen_wib", out["started_wib"]),
               "source": "sourcify-feed",
               "status": ("probe-possible-sale-abi-" + ("S1" if ab.get("S1") else "S2" if ab.get("S2") else "no-sale-shape")
                          if st["status"] == "probe-possible-sale" else "checked-not-sale-shape"),
               "note": note[:600]}
json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-14-0109-followup-probe.json", "w"), indent=1)
print(json.dumps(out, indent=1))
