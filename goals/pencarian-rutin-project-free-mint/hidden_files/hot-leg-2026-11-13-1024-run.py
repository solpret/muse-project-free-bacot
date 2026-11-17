#!/usr/bin/env python3
"""Hot-leg 1024 (2026-11-13): Sourcify feed poll (parse {"results": [...]}) +
Boltbook EN/ZH + single direct JSON-RPC batch (bsc-dataseed) re-read of
priority watchlist/track-C + pending binanceai claim + AgentMuse, plus
on-chain selector PROBE shape-check for feed/boltbook-new contracts
(Sourcify ABI route broken since 1014 run: plural 404, singular metadata-only).
Read-only except hot-leg-seen.json (new contracts only) and run output files.
Strict timeouts; skip stalled legs, never wait."""
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
out = {"run": "free-mint-hot-leg 2026-11-13 10:24 WIB", "started_wib": now_wib()}

seen = json.load(open(f"{HF}/hot-leg-seen.json"))
seen_lower = {k.lower() for k in seen}
reported = {}
try:
    reported = json.load(open(f"{HF}/hot-leg-reported.json"))
except Exception:
    pass

# --- Leg 1: Sourcify feed (object with "results" key) ---
feed_new = []
try:
    body = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=20)
    parsed = json.loads(body) if body else {}
    feed = parsed.get("results", []) if isinstance(parsed, dict) else parsed
    out["feed"] = {"n": len(feed),
                   "newest_verifiedAt": feed[0].get("verifiedAt") if feed else None,
                   "oldest_verifiedAt": feed[-1].get("verifiedAt") if feed else None}
    for item in feed:
        addr = item.get("address", "")
        if addr and addr.lower() not in seen_lower and addr.lower() != REGISTRY.lower() \
                and addr.lower() not in EXCLUDED and addr not in feed_new:
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
for lang in ("en", "zh"):
    for a in bb.get(lang, {}).get("addrs", []):
        if a.lower() not in seen_lower and a.lower() not in EXCLUDED and a not in bb_new:
            bb_new.append(a)
out["boltbook_new"] = bb_new

# --- Probe shape-check (on-chain selectors; Sourcify ABI broken) ---
PROBE = ["freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
         "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY", "agentRegistry",
         "AGENT_ID_REGISTRY", "saleOpen", "mintOpen", "totalSupply"]
FREE_SET = {"freeSharesRemaining", "freeClaimed", "freeMinted", "freeLeft",
            "freeAvailable", "FREE_SLOTS", "FREE_SUPPLY"}
probe_targets = (feed_new + bb_new)[:12]  # cap: keep batch manageable
probe_calls, probe_keys = [], []
for a in probe_targets:
    for fn in PROBE:
        probe_calls.append({"jsonrpc": "2.0", "id": len(probe_calls),
                            "method": "eth_call",
                            "params": [{"to": a, "data": sel(fn + "()")}, "latest"]})
        probe_keys.append((a, fn))
probe_hits = {}
if probe_calls:
    body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(probe_calls), timeout=45)
    if body:
        try:
            resp = json.loads(body)
            items = resp if isinstance(resp, list) else [resp]
            for item in items:
                i = item.get("id")
                if i is None or i >= len(probe_keys):
                    continue
                r = item.get("result")
                if r and isinstance(r, str) and len(r) >= 66 and not item.get("error"):
                    a, fn = probe_keys[i]
                    probe_hits.setdefault(a, []).append(fn)
        except Exception as e:
            out["probe_error"] = f"parse-failed: {e}"
    else:
        out["probe_error"] = "dataseed-probe-fetch-failed"
probe_status = {}
for a in probe_targets:
    hits = probe_hits.get(a, [])
    free_hit = any(h in FREE_SET for h in hits)
    agent_hit = any(h in ("agentRegistry", "AGENT_ID_REGISTRY") for h in hits)
    sale_hit = any(h in ("saleOpen", "mintOpen") for h in hits)
    possible = bool(free_hit and (agent_hit or sale_hit))
    probe_status[a] = {"hits": hits, "free_hit": free_hit, "agent_hit": agent_hit,
                       "sale_hit": sale_hit,
                       "status": "probe-possible-sale" if possible else "probe-not-sale-shape"}
out["probe"] = probe_status
out["probe_capped"] = len(feed_new + bb_new) - len(probe_targets)

# --- Leg 3/4: single direct batch re-read (known-good views) + eth_getCode ---
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
body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(reqs), timeout=45)
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

# --- Derived change flags vs 1014 run (for reporting decision) ---
prev = {"Agentx": {"freeMinted": 675, "FREE_CAP": 1111},
        "OBFG": {"freeMinted": 643, "FREE_SUPPLY": 1230},
        "JNTM": {"freeClaimed": 374},
        "BC1B": {"freeCount": 462},
        "Pickgrid": {"freeMinted": 216},
        "MECHA": {"freeClaimed": 1909},
        "NOTV": {"totalMinted": 0},
        "AgentMuse": {"freeClaimed": 244},
        "binanceai-mint": {"launched": 0}}
flags = {}
ax = reads.get("Agentx", {})
if ax.get("freeMinted") is not None and ax.get("FREE_CAP"):
    pct = ax["freeMinted"] / ax["FREE_CAP"] * 100
    flags["Agentx_pct"] = round(pct, 1)
    flags["Agentx_strong_lead"] = bool(pct > 70 and ax.get("freeClaimed_user") == 0
                                       and ax.get("mintOpen") == 1)
ob = reads.get("OBFG", {})
if ob.get("freeMinted") is not None and ob.get("FREE_SUPPLY"):
    flags["OBFG_pct"] = round(ob["freeMinted"] / ob["FREE_SUPPLY"] * 100, 1)
    flags["OBFG_soldout"] = bool(ob["freeMinted"] >= ob["FREE_SUPPLY"])
    flags["OBFG_slot_lost"] = bool(ob.get("freeAvailable_user") == 0)
flags["binanceai_opened"] = bool(reads.get("binanceai-mint", {}).get("launched") == 1)
flags["NOTV_opened"] = bool((reads.get("NOTV", {}).get("totalMinted") or 0) > 0)
flags["JNTM_opened"] = bool(reads.get("JNTM", {}).get("opened") == 1)
out["flags"] = flags

# --- Update hot-leg-seen.json with newly seen contracts (only additions) ---
new_seen = {}
for a in feed_new:
    st = probe_status.get(a, {})
    new_seen[a] = {"first_seen_wib": now_wib(), "source": "sourcify-feed",
                   "status": st.get("status", "probe-not-run"),
                   "note": json.dumps(st.get("hits", []))[:400]}
for a in bb_new:
    code = codes.get(a, "unknown")
    st = probe_status.get(a, {})
    new_seen[a] = {"first_seen_wib": now_wib(), "source": "boltbook",
                   "status": "checked-not-contract" if code == "0x" else st.get("status", "probe-not-run"),
                   "note": f"eth_getCode={code}; probe_hits={json.dumps(st.get('hits', []))[:300]}"}
if new_seen:
    seen.update(new_seen)
    json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)
out["seen_added"] = list(new_seen.keys())
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-13-1024.json", "w"), indent=1)
print(json.dumps(out, indent=1))
