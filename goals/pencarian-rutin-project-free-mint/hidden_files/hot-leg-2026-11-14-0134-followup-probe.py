#!/usr/bin/env python3
"""Hot-leg 0134 follow-up probe (2026-11-14 ~01:45 WIB): the 0134 run's legs 1-2
effectively skipped (Sourcify feed n=0, Boltbook EN+ZH fetch-failed — fetch
timeouts, not empty sources: manual re-check just now got Sourcify results
newest verifiedAt 2026-11-13T18:38:12Z and Boltbook EN 200 / 47,942 bytes;
Boltbook ZH still timing out). Shape-check the 3 newest Sourcify contracts +
any new Boltbook EN addresses. Strict timeouts; read-only except
hot-leg-seen.json additions + this output file."""
import json, re, subprocess, time
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}

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
out = {"run": "free-mint-hot-leg 2026-11-14 01:34 follow-up probe", "started_wib": now_wib()}
seen = json.load(open(f"{HF}/hot-leg-seen.json"))
seen_lower = {k.lower() for k in seen}

# Sourcify feed (fresh fetch)
feed_new = []
try:
    body = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=15)
    parsed = json.loads(body) if body else {}
    feed = parsed.get("results", []) if isinstance(parsed, dict) else parsed
    out["feed"] = {"n": len(feed), "newest_verifiedAt": feed[0].get("verifiedAt") if feed else None}
    for item in feed:
        addr = item.get("address", "")
        if addr and addr.lower() not in seen_lower and addr.lower() != REGISTRY.lower() \
                and addr.lower() not in EXCLUDED and addr not in feed_new:
            feed_new.append(addr)
except Exception as e:
    out["feed"] = {"error": str(e)}
out["feed_new"] = feed_new

# Boltbook EN only (ZH timed out on manual re-check)
bb_new = []
body = curl("https://boltbook.fun/?lang=en", timeout=15)
if body:
    addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", body)))
    out["boltbook_en"] = {"bytes": len(body), "n_addrs": len(addrs)}
    for a in addrs:
        if a.lower() not in seen_lower and a.lower() not in EXCLUDED and a not in bb_new:
            bb_new.append(a)
else:
    out["boltbook_en"] = {"error": "fetch-failed"}
out["boltbook_new"] = bb_new

# Probe shape-check (chunked, <=24 calls per batch)
PROBE = ["freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
         "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY", "agentRegistry",
         "AGENT_ID_REGISTRY", "AGENT_REGISTRY", "saleOpen", "mintOpen", "totalSupply"]
FREE_SET = {"freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
            "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY"}
targets = (feed_new + bb_new)[:12]
probe_calls, probe_keys = [], []
for a in targets:
    for fn in PROBE:
        probe_calls.append({"jsonrpc": "2.0", "id": len(probe_calls), "method": "eth_call",
                            "params": [{"to": a, "data": sel(fn + "()")}, "latest"]})
        probe_keys.append((a, fn))
probe_hits = {}
if probe_calls:
    for cid, r, err in rpc_chunked(probe_calls, timeout=20):
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

# ABI shape-check for any probe-possible-sale target
abi_shape = {}
for a in targets:
    if probe_status.get(a, {}).get("status") == "probe-possible-sale":
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

# Record newly seen contracts (additions only)
new_seen = {}
for a in feed_new:
    st = probe_status.get(a, {})
    new_seen[a] = {"first_seen_wib": now_wib(), "source": "sourcify-feed-followup-0134",
                   "status": st.get("status", "probe-not-run"),
                   "note": json.dumps(st.get("hits", []))[:400]}
for a in bb_new:
    st = probe_status.get(a, {})
    new_seen[a] = {"first_seen_wib": now_wib(), "source": "boltbook-en-followup-0134",
                   "status": st.get("status", "probe-not-run"),
                   "note": json.dumps(st.get("hits", []))[:400]}
if new_seen:
    seen.update(new_seen)
    json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)
out["seen_added"] = list(new_seen.keys())
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{HF}/hot-leg-2026-11-14-0134-followup-probe.json", "w"), indent=1)
print(json.dumps(out, indent=1))
