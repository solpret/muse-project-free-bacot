#!/usr/bin/env python3
"""Hot-leg 0134 follow-up probe #2 (2026-11-14 ~01:45 WIB): the follow-up probe's
own feed/Boltbook fetches timed out (egress ~15s vs 15s script timeout), but a
direct shell fetch at ~01:44 WIB DID return the feed (5 newest verified
2026-11-13T18:29-18:38Z) — so legs 1-2 stalled on transport, not on empty
sources. Probe-shape-check those 5 feed addresses + any new Boltbook EN
addresses now; record in hot-leg-seen.json + follow-up JSON. Read-only on-chain
except seen additions. Strict timeouts; one pass only."""
import json, re, subprocess, time
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FEED5 = ["0xB2996E757E08c75d433Da42c95Ae03a1d5948A06",
         "0x88b4c8Dc1d0FE3CC1201609A5ECeAB9dF4cDc6cd",
         "0x99950CdDF74A7ba71ee7B27e7f14fF96cF913522",
         "0xc6B9F8a3b35a19CbD7F929f28a5bD0583c104644",
         "0x966F61323008C00c56Ec60d2b55b2Cc59B996827"]

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

def rpc_chunked(calls, timeout=25):
    out = []
    for i in range(0, len(calls), 24):
        chunk = calls[i:i + 24]
        body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(chunk), timeout=timeout)
        used_fb = False
        if not body:
            body = curl("https://bsc-dataseed1.defibit.io/", data=json.dumps(chunk), timeout=timeout)
            used_fb = True
        if not body:
            out += [(c["id"], None, "fetch-failed") for c in chunk]
            continue
        try:
            resp = json.loads(body)
            items = resp if isinstance(resp, list) else [resp]
            by_id = {it.get("id"): it for it in items if isinstance(it, dict)}
            if not used_fb and all(not by_id.get(c["id"], {}).get("result") for c in chunk):
                body2 = curl("https://bsc-dataseed1.defibit.io/", data=json.dumps(chunk), timeout=timeout)
                if body2:
                    try:
                        r2 = json.loads(body2)
                        i2 = r2 if isinstance(r2, list) else [r2]
                        b2 = {it.get("id"): it for it in i2 if isinstance(it, dict)}
                        if any(b2.get(c["id"], {}).get("result") for c in chunk):
                            by_id = b2
                    except Exception:
                        pass
            for c in chunk:
                it = by_id.get(c["id"], {})
                out.append((c["id"], it.get("result"), it.get("error")))
        except Exception as e:
            out += [(c["id"], None, f"parse-failed: {e}") for c in chunk]
    return out

def now_wib():
    return time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time() + 7 * 3600))

t0 = time.time()
out = {"run": "free-mint-hot-leg 2026-11-14 01:34 follow-up probe #2", "started_wib": now_wib()}
seen = json.load(open(f"{HF}/hot-leg-seen.json"))
seen_lower = {k.lower() for k in seen}

# Boltbook EN (best effort, 20s)
bb_new = []
body = curl("https://boltbook.fun/?lang=en", timeout=20)
if body:
    addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", body)))
    out["boltbook_en"] = {"bytes": len(body), "n_addrs": len(addrs)}
    for a in addrs:
        if a.lower() not in seen_lower and a.lower() not in EXCLUDED and a not in bb_new \
                and a not in FEED5:
            bb_new.append(a)
else:
    out["boltbook_en"] = {"error": "fetch-failed"}
out["boltbook_new"] = bb_new

targets = [a for a in FEED5 if a.lower() not in seen_lower] + bb_new
out["targets"] = targets
PROBE = ["freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
         "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY", "agentRegistry",
         "AGENT_ID_REGISTRY", "AGENT_REGISTRY", "saleOpen", "mintOpen", "totalSupply"]
FREE_SET = {"freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
            "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY"}
probe_calls, probe_keys = [], []
for a in targets:
    for fn in PROBE:
        probe_calls.append({"jsonrpc": "2.0", "id": len(probe_calls), "method": "eth_call",
                            "params": [{"to": a, "data": sel(fn + "()")}, "latest"]})
        probe_keys.append((a, fn))
probe_hits = {}
if probe_calls:
    for cid, r, err in rpc_chunked(probe_calls, timeout=25):
        if r and isinstance(r, str) and len(r) >= 66 and not err:
            a, fn = probe_keys[cid]
            probe_hits.setdefault(a, []).append(fn)
probe_status = {}
for a in targets:
    hits = probe_hits.get(a, [])
    free_hit = any(h in FREE_SET for h in hits)
    agent_hit = any(h in ("agentRegistry", "AGENT_ID_REGISTRY", "AGENT_REGISTRY") for h in hits)
    sale_hit = any(h in ("saleOpen", "mintOpen") for h in hits)
    probe_status[a] = {"hits": hits, "free_hit": free_hit, "agent_hit": agent_hit,
                       "sale_hit": sale_hit,
                       "status": "probe-possible-sale" if (free_hit and (agent_hit or sale_hit))
                                 else "probe-not-sale-shape"}
out["probe"] = probe_status

abi_shape = {}
for a in targets:
    if probe_status.get(a, {}).get("status") == "probe-possible-sale":
        try:
            mj = json.loads(curl(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", timeout=20) or "{}")
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

new_seen = {}
for a in targets:
    st = probe_status.get(a, {})
    src = "sourcify-feed-followup2-0134" if a in FEED5 else "boltbook-en-followup2-0134"
    new_seen[a] = {"first_seen_wib": now_wib(), "source": src,
                   "status": st.get("status", "probe-not-run"),
                   "note": json.dumps(st.get("hits", []))[:400]}
if new_seen:
    seen.update(new_seen)
    json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)
out["seen_added"] = list(new_seen.keys())
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{HF}/hot-leg-2026-11-14-0134-followup-probe2.json", "w"), indent=1)
print(json.dumps(out, indent=1))
