#!/usr/bin/env python3
"""Hot-leg 1014: Sourcify feed poll + Boltbook EN/ZH + single direct
JSON-RPC batch (bsc-dataseed) re-read of priority watchlist/track-C +
pending binanceai claim + AgentMuse. Read-only except hot-leg-seen.json
(new contracts only) and run output files. Strict timeouts."""
import json, re, subprocess, time
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}

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
out = {"run": "free-mint-hot-leg 2026-11-13 10:14 WIB", "started_wib": now_wib()}

# --- Leg 1: Sourcify feed ---
seen = json.load(open(f"{HF}/hot-leg-seen.json"))
feed_new = []
try:
    body = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=20)
    feed = json.loads(body) if body else []
    out["feed"] = {"n": len(feed),
                   "newest_verifiedAt": feed[0].get("verifiedAt") if feed else None,
                   "oldest_verifiedAt": feed[-1].get("verifiedAt") if feed else None}
    for item in feed:
        addr = item.get("address", "")
        if addr.lower() not in {k.lower() for k in seen} and addr.lower() != REGISTRY.lower() and addr.lower() not in EXCLUDED:
            feed_new.append(addr)
except Exception as e:
    out["feed"] = {"error": str(e)}
out["feed_new"] = feed_new

# --- Leg 2: Boltbook EN+ZH ---
bb = {}
for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
    body = curl(url, timeout=20)
    if body:
        bb[lang] = {"bytes": len(body), "addrs": sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", body)))}
    else:
        bb[lang] = {"error": "fetch-failed"}
out["boltbook"] = bb
bb_new = []
seen_lower = {k.lower() for k in seen}
for lang in ("en", "zh"):
    for a in bb.get(lang, {}).get("addrs", []):
        if a.lower() not in seen_lower and a.lower() not in EXCLUDED and a not in bb_new:
            bb_new.append(a)
out["boltbook_new"] = bb_new

# --- Shape-check feed-new + boltbook-new via Sourcify ABI ---
def shapecheck(addr):
    body = curl(f"https://sourcify.dev/server/v2/contracts/56/{addr}", timeout=20)
    if not body:
        return {"status": "shape-check-failed", "reason": "sourcify-fetch-failed"}
    try:
        abi = json.loads(body)["stdJson"]["output"]["abi"]
    except Exception:
        return {"status": "shape-check-failed", "reason": "no-abi-in-sourcify"}
    fns = {e.get("name") for e in abi if e.get("type") == "function"}
    mint = any(n in fns for n in ("mint", "mintFree", "claimFree", "mintWithAgentId"))
    quote = any(n in fns for n in ("quote", "cost", "getQuote", "price"))
    free = [n for n in fns if n.startswith("free")]
    agent = any(n in fns for n in ("agentId", "registry", "AGENT_ID_REGISTRY", "agentRegistry", "agentGate")) or REGISTRY.lower() in json.dumps(abi).lower()
    token = all(n in fns for n in ("name", "symbol", "decimals", "totalSupply"))
    s1 = bool(mint and quote and free and agent)
    s2 = bool(token and ("mintFree" in fns or "claimFree" in fns) and free and agent)
    return {"S1": s1, "S2": s2, "mint": mint, "quote": quote, "free": free,
            "agent": agent, "token": token,
            "status": "sale-shape" if (s1 or s2) else "not-sale-shape"}

sc = {}
for a in feed_new + bb_new:
    sc[a] = shapecheck(a)
out["shapecheck"] = sc

# --- Leg 3/4: single direct batch re-read + eth_getCode for boltbook-new ---
PLAN = [
 ("OBFG", "0x5314071bba19943f58347ba5dec423e5032a6818",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("saleOpen", False), ("freeAvailable", True)]),
 ("JNTM", "0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b",
  [("freeClaimed", False), ("FREE_LOTS_CAP", False), ("opened", False), ("mintStart", False), ("freeLeft", False), ("paidMinted", False)]),
 ("Agentx", "0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
  [("freeMinted", False), ("FREE_CAP", False), ("freeClaimed", True), ("mintOpen", False)]),
 ("BC1B", "0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053",
  [("freeCount", False), ("FREE_CAP", False)]),
 ("Pickgrid", "0x7f541bcc33abed0e64455565da723e949c6f76f0",
  [("freeMinted", False)]),
 ("MECHA", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
  [("freeClaimed", False)]),
 ("NOTV", "0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01",
  [("totalMinted", False), ("freeStart", False)]),
 ("AgentMuse", "0x779fa133848d23052B7345F63B3b2E5309cd13ed",
  [("freeClaimed", False), ("FREE_SHARES", False), ("openedAt", False), ("bookedOf", True)]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", False), ("claimable", True)]),
]
reqs, keys = [], []
for name, addr, views in PLAN:
    for fn, uarg in views:
        data = sel(fn + ("(address)" if uarg else "()")) + (USER_PAD if uarg else "")
        reqs.append({"jsonrpc": "2.0", "id": len(reqs), "method": "eth_call",
                     "params": [{"to": addr, "data": data}, "latest"]})
        keys.append((name, fn + ("_user" if uarg else "")))
code_keys = []
for a in bb_new:
    reqs.append({"jsonrpc": "2.0", "id": len(reqs), "method": "eth_getCode",
                 "params": [a, "latest"]})
    code_keys.append(a)
reads, codes = {}, {}
body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(reqs), timeout=30)
if body:
    try:
        resp = json.loads(body)
        items = resp if isinstance(resp, list) else [resp]
        for item in items:
            i = item.get("id")
            if i is None:
                continue
            r = item.get("result")
            if i < len(keys):
                name, fn = keys[i]
                v = None
                if r and r != "0x" and len(r) >= 66:
                    try:
                        v = int(r[-64:], 16)
                    except Exception:
                        v = None
                reads.setdefault(name, {})[fn] = v
            else:
                codes[code_keys[i - len(keys)]] = ("0x" if r in (None, "0x") else "contract")
    except Exception as e:
        out["batch_error"] = f"parse-failed: {e}"
else:
    out["batch_error"] = "dataseed-batch-fetch-failed"
out["reads"] = reads
out["reads_ok"] = sum(1 for n in reads if any(v is not None for v in reads[n].values()))
out["eth_getCode"] = codes

# --- Bridge leg (read-only) ---
try:
    b = json.load(open(f"{HF}/scan-bridge.json"))
    c = b.get("contracts", {})
    out["bridge"] = {"n": len(c),
                     "not_in_snapshot": sum(1 for v in c.values() if not v.get("in_freebacot_snapshot")),
                     "same_owner_discarded": sum(1 for v in c.values() if v.get("same_owner_discarded"))}
except Exception as e:
    out["bridge"] = {"error": str(e)}

# --- Update hot-leg-seen.json with newly seen contracts (only additions) ---
new_seen = {}
for a in feed_new:
    new_seen[a] = {"first_seen_wib": now_wib(), "source": "sourcify-feed",
                   "status": sc.get(a, {}).get("status", "shape-check-failed"),
                   "note": json.dumps(sc.get(a, {}))[:400]}
for a in bb_new:
    code = codes.get(a, "unknown")
    st = sc.get(a, {})
    new_seen[a] = {"first_seen_wib": now_wib(), "source": "boltbook",
                   "status": "checked-not-contract" if code == "0x" else st.get("status", "shape-check-failed"),
                   "note": f"eth_getCode={code}; shape={json.dumps(st)[:300]}"}
if new_seen:
    seen.update(new_seen)
    json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)
out["seen_added"] = list(new_seen.keys())
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-13-1014.json", "w"), indent=1)
print(json.dumps(out, indent=1))
