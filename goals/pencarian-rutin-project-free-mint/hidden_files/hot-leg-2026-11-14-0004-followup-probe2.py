#!/usr/bin/env python3
"""Hot-leg 0004 follow-up probe: re-probe FROST + the 2 feed-new contracts that
were capped out of the main probe (probe_capped=1). Main probe returned 0 hits
for ALL 12 targets while the re-read leg (same RPC) read fine - suspect the
probe chunks hit the early-run RPC stall. If any target is probe-possible-sale,
run the Sourcify ABI shape-check. Read-only; updates hot-leg-seen.json notes
only for the 2 capped contracts."""
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
TARGETS = ['0x07009D16E55133d98Ab2EFeC92E66ea4D962a7cc', '0x1C571782E610De334B2BB8A4E4E98a54841cd5ee', '0xb04D25fd8B2c7Ec4B66EeFB37C0ebb1634E7cA6E', '0xfe9161e4F3Ed2F4EA0EB886230f45cd5061C9183', '0x05ba4F231fc0839542687E26cA88ab5310775CA8', '0x7d0d52e7c47b9f22A007E9004fe990CAbD8424a7', '0x61e51D80b00EbD6Dbd2ea2b552f2eb42D9eC8201', '0xD0e45EE7930cfb8B9F9A77547C095B1fBEF63Ca3', '0x9d310f80B18e4982b57408E173254861eDd8e778', '0x34e368CEdE40b19F4867b4f9b7108311ACf53B3D', '0xf2a57c71d83D94B11Ab21F2B2e09d529E5B2402A']
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
    status[a] = {"hits": h, "free_hit": free_hit, "agent_hit": agent_hit,
                 "sale_hit": sale_hit,
                 "status": "probe-possible-sale" if (free_hit and (agent_hit or sale_hit)) else "probe-not-sale-shape"}
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
out = {"run": "free-mint-hot-leg 2026-11-14 00:04 follow-up probe 2 (remaining 11 feed-new)",
       "probe": status, "abi_shape": abi_shape,
       "elapsed_s": round(time.time() - t0, 1)}
# Update seen notes for the 2 capped contracts (status only, first_seen kept)
seen = json.load(open(f"{HF}/hot-leg-seen.json"))
for a in TARGETS:
    if a in seen:
        seen[a]["status"] = status[a]["status"]
        seen[a]["note"] = json.dumps(status[a].get("hits", []))[:400] + " (follow-up probe2 0004)"
json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)
json.dump(out, open(f"{HF}/hot-leg-2026-11-14-0004-followup-probe2.json", "w"), indent=1)
print(json.dumps(out, indent=1))
