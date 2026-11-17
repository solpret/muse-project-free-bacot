#!/usr/bin/env python3
"""Hot-leg 1034 follow-up: probe the 8 feed contracts capped out of the main
run's 12-contract probe cap (probe_capped=9, minus 1 Boltbook EOA already
resolved via eth_getCode=0x). Chunked <=24 calls. Also spot-checks one
zero-hit contract from the main probe with a direct single eth_call, per the
1024 lesson (never trust an all-zero batch without a spot-check).
Updates hot-leg-seen.json entries for the 8 contracts with real probe results.
Read-only on-chain except the seen-file update + this run's output file."""
import json, subprocess, time
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"

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

def rpc_chunked(calls, timeout=30):
    out = []
    for i in range(0, len(calls), 24):
        chunk = calls[i:i + 24]
        body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(chunk), timeout=timeout)
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
out = {"run": "free-mint-hot-leg 2026-11-13 10:34 WIB follow-up probe (capped 8)",
       "started_wib": time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time() + 7 * 3600))}

CAPPED = ["0x08D33Ca12D5bC01EF3f147699D10682a8aB24909",
          "0x19ea0Eb1Cc5963FaCbaf7F0eC8374074a0B93951",
          "0xf8E39535AFC5220FB06936E5c27177F7462e70fe",
          "0x8e3e150E4b9a31F168D2a988248688F33D75Bf05",
          "0x4060BD3879a29bC4a37D2D01e76aA5087D0ce4a8",
          "0x8E503620B758a03cD6DEF55532bd1C423E21364b",
          "0x6e19398EC6492b8820c99d52fb5FA131867171f0",
          "0x79E4EFB1e26f8BAB6Dc30F1f0dEE528C7Dd94964"]
PROBE = ["freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
         "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY", "agentRegistry",
         "AGENT_ID_REGISTRY", "saleOpen", "mintOpen", "totalSupply"]
FREE_SET = {"freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
            "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY"}

calls, keys = [], []
for a in CAPPED:
    for fn in PROBE:
        calls.append({"jsonrpc": "2.0", "id": len(calls), "method": "eth_call",
                      "params": [{"to": a, "data": sel(fn + "()")}, "latest"]})
        keys.append((a, fn))
hits = {}
for cid, r, err in rpc_chunked(calls, timeout=30):
    if r and isinstance(r, str) and len(r) >= 66 and not err:
        a, fn = keys[cid]
        hits.setdefault(a, []).append(fn)
status = {}
for a in CAPPED:
    h = hits.get(a, [])
    free_hit = any(x in FREE_SET for x in h)
    agent_hit = any(x in ("agentRegistry", "AGENT_ID_REGISTRY") for x in h)
    sale_hit = any(x in ("saleOpen", "mintOpen") for x in h)
    possible = bool(free_hit and (agent_hit or sale_hit))
    status[a] = {"hits": h, "free_hit": free_hit, "agent_hit": agent_hit,
                 "sale_hit": sale_hit,
                 "status": "probe-possible-sale" if possible else "probe-not-sale-shape"}
out["probe"] = status

# Spot-check: one zero-hit contract from the main probe, direct single calls.
SPOT = "0xe8310fB999A81203e2573B0337235FDA15c9fe45"
spot_calls = [
    {"jsonrpc": "2.0", "id": 0, "method": "eth_getCode", "params": [SPOT, "latest"]},
    {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
     "params": [{"to": SPOT, "data": sel("totalSupply()")}, "latest"]},
    {"jsonrpc": "2.0", "id": 2, "method": "eth_call",
     "params": [{"to": SPOT, "data": sel("freeClaimed()")}, "latest"]},
]
spot = {}
for cid, r, err in rpc_chunked(spot_calls, timeout=30):
    spot[cid] = {"result": (r[:66] if r else None), "error": err}
out["spot_check"] = {"contract": SPOT, "calls": spot,
                     "verdict": "zero-hits-real" if spot.get(1, {}).get("result") in (None, "0x")
                     and spot.get(0, {}).get("result") not in (None, "0x", "0x0") else "needs-review"}

# Update seen entries for the 8 capped contracts with real probe results.
seen = json.load(open(f"{HF}/hot-leg-seen.json"))
for a in CAPPED:
    st = status[a]
    seen[a] = {"first_seen_wib": seen.get(a, {}).get("first_seen_wib", out["started_wib"]),
               "source": "sourcify-feed",
               "status": st["status"],
               "note": json.dumps(st["hits"])[:400]}
json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)
out["seen_updated"] = CAPPED
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{HF}/hot-leg-2026-11-13-1034-probe-followup.json", "w"), indent=1)
print(json.dumps(out, indent=1))
