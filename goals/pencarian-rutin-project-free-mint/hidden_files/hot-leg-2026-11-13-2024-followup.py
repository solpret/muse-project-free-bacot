#!/usr/bin/env python3
"""Hot-leg 2024 followup: leg-3 fast verification of the 2 probe-possible-sale
new contracts from the Sourcify feed + the 1 feed contract the probe cap
missed (0x0ebF...). Read-only. Chunked <=24 calls. Also fetch Sourcify
metadata (contractName, verifiedAt) for each."""
import json, subprocess, time
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
C43F = "0xc43f7Ab11728FC884662B35AD974ff703cb4221d"
B4BB = "0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f"
EBFB = "0x0ebFb6655062B10811Dc3Fa725731193E77CE46A"

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
out = {"run": "hot-leg 2026-11-13 20:24 followup leg-3", "started_wib": time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time() + 7 * 3600))}

# Probe the missed contract first (same 13 selectors as main run)
PROBE = ["freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
         "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY", "agentRegistry",
         "AGENT_ID_REGISTRY", "AGENT_REGISTRY", "saleOpen", "mintOpen", "totalSupply"]
calls, keys = [], []
for fn in PROBE:
    calls.append({"jsonrpc": "2.0", "id": len(calls), "method": "eth_call",
                  "params": [{"to": EBFB, "data": sel(fn + "()")}, "latest"]})
    keys.append((EBFB, fn))
probe_hits = []
for cid, r, err in rpc_chunked(calls):
    if r and len(r) >= 66 and not err:
        probe_hits.append(keys[cid][1])
out["ebfb_probe_hits"] = probe_hits
out["ebfb_probe_status"] = "probe-possible-sale" if any(h in ("freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft", "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY") for h in probe_hits) and any(h in ("agentRegistry", "AGENT_ID_REGISTRY", "AGENT_REGISTRY", "saleOpen", "mintOpen") for h in probe_hits) else "probe-not-sale-shape"

# Leg-3 views for the two probe-possible contracts
VIEWS = [("freeMinted", False), ("freeLeft", False), ("freeSharesRemaining", False),
         ("FREE_SLOTS", False), ("FREE_SUPPLY", False), ("FREE_CAP", False),
         ("FREE_MAX", False), ("mintOpen", False), ("saleOpen", False),
         ("saleStart", False), ("mintStart", False), ("freeStart", False),
         ("launched", False), ("totalSupply", False),
         ("freeClaimed", True), ("freeAvailable", True)]
calls, keys = [], []
for addr in (C43F, B4BB):
    for fn, uarg in VIEWS:
        data = sel(fn + ("(address)" if uarg else "()")) + (USER_PAD if uarg else "")
        calls.append({"jsonrpc": "2.0", "id": len(calls), "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append((addr, fn + ("_user" if uarg else "")))
    # quote(address,uint256) with qty 1
    data = sel("quote(address,uint256)") + USER_PAD + "1".rjust(64, "0")
    calls.append({"jsonrpc": "2.0", "id": len(calls), "method": "eth_call",
                  "params": [{"to": addr, "data": data}, "latest"]})
    keys.append((addr, "quote_user_1"))
    # contractURI()
    calls.append({"jsonrpc": "2.0", "id": len(calls), "method": "eth_call",
                  "params": [{"to": addr, "data": sel("contractURI()")}, "latest"]})
    keys.append((addr, "contractURI_raw"))
reads = {}
for cid, r, err in rpc_chunked(calls):
    addr, fn = keys[cid]
    v = None
    if fn == "contractURI_raw":
        reads.setdefault(addr, {})[fn] = r
    elif r and r != "0x" and len(r) >= 66:
        try:
            v = int(r[-64:], 16)
        except Exception:
            v = None
        reads.setdefault(addr, {})[fn] = v
    else:
        reads.setdefault(addr, {})[fn] = None
out["reads"] = reads

# Sourcify metadata: contract name + verifiedAt
meta = {}
for addr in (C43F, B4BB, EBFB):
    try:
        mj = json.loads(curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=stdJson", timeout=20) or "{}")
        meta[addr] = {"name": mj.get("name"), "verifiedAt": mj.get("verifiedAt"),
                      "creationMatch": mj.get("creationMatch")}
    except Exception as e:
        meta[addr] = {"error": str(e)[:120]}
out["sourcify_meta"] = meta
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{HF}/hot-leg-2026-11-13-2024-followup.json", "w"), indent=1)
print(json.dumps(out, indent=1))
