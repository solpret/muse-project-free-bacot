#!/usr/bin/env python3
"""Re-probe correction for hot-leg 1024: the 132-call probe batch silently
returned zero hits for all 11 contracts, but a direct check shows
0xfb8771... responds to totalSupply() + name(). Re-probe in small chunks
(2 contracts x 12 selectors) so a batch failure is visible, and correct
hot-leg-seen.json statuses. Never marks probe-failed as not-sale-shape."""
import json, subprocess, time
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
PROBE = ["freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
         "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY", "agentRegistry",
         "AGENT_ID_REGISTRY", "saleOpen", "mintOpen", "totalSupply"]
FREE_SET = {"freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
            "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY"}

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def curl_batch(reqs, timeout=30):
    try:
        p = subprocess.run(["curl", "-sS", "-m", str(timeout), "-A", "Mozilla/5.0",
                            "-H", "Content-Type: application/json", "-d", json.dumps(reqs),
                            "https://bsc-dataseed.binance.org/"],
                           capture_output=True, text=True, timeout=timeout + 5)
        return p.stdout if p.returncode == 0 and p.stdout else None
    except Exception:
        return None

t0 = time.time()
run = json.load(open(f"{HF}/hot-leg-run-2026-11-13-1024.json"))
targets = run["feed_new"]
seen = json.load(open(f"{HF}/hot-leg-seen.json"))

out = {"run": "free-mint-hot-leg 2026-11-13 10:24 WIB probe-correction",
       "started_wib": time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time() + 7 * 3600)),
       "targets": targets, "chunks": []}
probe_status = {}
for ci in range(0, len(targets), 2):
    chunk = targets[ci:ci + 2]
    reqs, keys = [], []
    for a in chunk:
        for fn in PROBE:
            reqs.append({"jsonrpc": "2.0", "id": len(reqs), "method": "eth_call",
                         "params": [{"to": a, "data": sel(fn + "()")}, "latest"]})
            keys.append((a, fn))
    body = curl_batch(reqs)
    chunk_rec = {"contracts": chunk, "batch_items": len(reqs)}
    if not body:
        chunk_rec["error"] = "fetch-failed"
        out["chunks"].append(chunk_rec)
        for a in chunk:
            probe_status[a] = {"hits": [], "status": "probe-failed",
                               "note": "chunk fetch failed; NOT not-sale-shape"}
        continue
    try:
        resp = json.loads(body)
        items = resp if isinstance(resp, list) else [resp]
    except Exception as e:
        chunk_rec["error"] = f"parse-failed: {e}"
        out["chunks"].append(chunk_rec)
        for a in chunk:
            probe_status[a] = {"hits": [], "status": "probe-failed",
                               "note": "chunk parse failed; NOT not-sale-shape"}
        continue
    chunk_rec["returned_items"] = len(items)
    hits = {}
    for item in items:
        i = item.get("id")
        if i is None or i >= len(keys):
            continue
        r = item.get("result")
        if r and isinstance(r, str) and len(r) >= 66 and not item.get("error"):
            a, fn = keys[i]
            hits.setdefault(a, []).append(fn)
    chunk_rec["hits"] = hits
    out["chunks"].append(chunk_rec)
    for a in chunk:
        h = hits.get(a, [])
        free_hit = any(x in FREE_SET for x in h)
        agent_hit = any(x in ("agentRegistry", "AGENT_ID_REGISTRY") for x in h)
        sale_hit = any(x in ("saleOpen", "mintOpen") for x in h)
        possible = bool(free_hit and (agent_hit or sale_hit))
        probe_status[a] = {"hits": h, "free_hit": free_hit, "agent_hit": agent_hit,
                           "sale_hit": sale_hit,
                           "status": "probe-possible-sale" if possible else "probe-not-sale-shape"}
out["probe"] = probe_status

# Correct hot-leg-seen.json for these 11 contracts
corrected = []
for a in targets:
    st = probe_status.get(a, {})
    if a in seen:
        seen[a]["status"] = st.get("status", "probe-failed")
        seen[a]["note"] = ("CORRECTED re-probe (chunked): " + json.dumps(st.get("hits", []))[:300])
        corrected.append(a)
if corrected:
    json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)
out["seen_corrected"] = corrected
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{HF}/hot-leg-2026-11-13-1024-probe-correction.json", "w"), indent=1)
print(json.dumps(out, indent=1))
