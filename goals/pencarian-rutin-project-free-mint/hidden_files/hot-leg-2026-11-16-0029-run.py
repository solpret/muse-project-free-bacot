#!/usr/bin/env python3
"""Hot-leg run 2026-11-16 00:29 WIB: legs 1-3 (Sourcify feed, Boltbook, shape-check) + bridge.
Read-only except hot-leg-seen.json additions and run json. No preview/mint."""
import json, re, subprocess, time, urllib.request
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
t0 = time.time()
def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")
def curl(url, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url],
                         capture_output=True, text=True, timeout=timeout+10).stdout
    return out

seen = json.load(open(BASE + "hot-leg-seen.json"))
snap = json.load(open(BASE + "onchain-snapshot.json"))
snap_addrs = set()
for k in ("contracts", "track_c", "pending_claims"):
    v = snap.get(k)
    if isinstance(v, dict):
        for name, it in v.items():
            if isinstance(it, dict):
                for kk in ("address", "sale", "token", "contract", "mint"):
                    if it.get(kk) and isinstance(it[kk], str) and it[kk].startswith("0x"):
                        snap_addrs.add(it[kk].lower())
            elif isinstance(it, str) and it.startswith("0x"):
                snap_addrs.add(it.lower())
bridge = json.load(open(BASE + "scan-bridge.json"))
bcontracts = bridge.get("contracts", {}) if isinstance(bridge, dict) else {}
if isinstance(bcontracts, dict):
    bridge_addrs = list(bcontracts.keys())
    b_disc = sum(1 for v in bcontracts.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
else:
    bridge_addrs = []
    for c in bcontracts:
        if isinstance(c, dict):
            a = c.get("address") or c.get("contract")
            if a: bridge_addrs.append(a)
        elif isinstance(c, str): bridge_addrs.append(c)
    b_disc = sum(1 for c in bcontracts if isinstance(c, dict) and c.get("same_owner_discarded"))
b_not_in_snap = [a for a in bridge_addrs if a.lower() not in snap_addrs]
b_in_snap = [a for a in bridge_addrs if a.lower() in snap_addrs]

# Leg 1: Sourcify feed
feed = {"error": None, "total": 0, "new": [], "top": None, "top_verifiedAt": None}
try:
    raw = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 60)
    d = json.loads(raw)
    items = d.get("results", d if isinstance(d, list) else [])
    feed["total"] = len(items)
    if items:
        feed["top"] = items[0].get("address")
        feed["top_verifiedAt"] = items[0].get("verifiedAt") or items[0].get("creationMatch", {})
    for it in items:
        a = it.get("address")
        if a and a not in seen and a.lower() not in ("0x60b9262456de011f7d15a54cdd8c48baa8b022f",):
            feed["new"].append(a)
except Exception as e:
    feed["error"] = str(e)[:200]

# Leg 2: Boltbook EN + ZH
def boltbook(lang):
    out = {"bytes": 0, "full_address_contracts": 0, "new": [], "error": None}
    try:
        url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
        txt = get(url, 60)
        out["bytes"] = len(txt)
        addrs = re.findall(r"0x[0-9a-fA-F]{40}", txt)
        uniq = sorted(set(addrs), key=lambda x: x.lower())
        out["full_address_contracts"] = len(uniq)
        out["new"] = [a for a in uniq if a not in seen]
    except Exception as e:
        out["error"] = str(e)[:200]
    return out
bb_en = boltbook("en")
bb_zh = boltbook("zh")

# Leg 3: shape-check new contracts (feed + boltbook) via Sourcify source
REG = "0x60b9262456de011f7d15a54cdd8c48baa8b022f".lower()
targets = []
for a in feed["new"] + bb_en["new"] + bb_zh["new"]:
    if a not in targets and a.lower() not in ("0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
        "0x8b47354e7b76b1970a0d06365c8244a810d37493"):
        targets.append(a)
shape = []
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeSupply"]
for a in targets:
    rec = {"address": a, "S1": False, "S2": False, "reason": ""}
    try:
        d = json.loads(curl(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", 60))
        src = json.dumps(d)
        low = src.lower()
        has_mint = bool(re.search(r"\bmint\w*\s*\(", low))
        has_quote = any(k in low for k in ["quote", "costfor", "pricefor", "getprice"])
        has_free = any(k.lower() in low for k in FREE_VIEWS)
        has_agent = REG in low or "agentgate" in low or "agentid" in low or "agentregistry" in low
        is_token = all(k in low for k in ["\"name\"", "\"symbol\"", "\"decimals\"", "\"totalsupply\""]) or ("name()" in low and "symbol()" in low and "decimals()" in low)
        has_mintfree = "mintfree" in low
        rec["detail"] = {"mint": has_mint, "quote": has_quote, "free_view": has_free,
                         "agent_ref": has_agent, "is_token": is_token, "mintFree": has_mintfree}
        if has_mint and has_quote and has_free and has_agent:
            rec["S1"] = True; rec["reason"] = "S1 shape"
        elif is_token and has_mintfree and has_free and has_agent:
            rec["S2"] = True; rec["reason"] = "S2 shape"
        else:
            rec["reason"] = "not agent sale shape: " + ",".join(
                k for k, v in rec["detail"].items() if not v) or "unknown"
    except Exception as e:
        rec["reason"] = "source fetch error: " + str(e)[:120]
    shape.append(rec)

hits = [s for s in shape if s["S1"] or s["S2"]]
added = []
for a in targets:
    if a not in seen:
        seen[a] = {"first_seen": "2026-11-16T00:29+07:00", "run": "hot-leg-0029"}
        added.append(a)
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out = {"run": "free-mint-hot-leg 2026-11-16T00:29+07:00", "started_wib": "2026-11-16T00:29+07:00",
       "sourcify_feed": feed, "boltbook_en": bb_en, "boltbook_zh": bb_zh,
       "shape_check": shape, "shape_hits": hits,
       "bridge": {"contracts": len(bridge_addrs), "same_owner_discarded": b_disc,
                  "not_in_snapshot": len(b_not_in_snap), "not_in_snapshot_list": b_not_in_snap,
                  "in_snapshot": b_in_snap},
       "seen_added": added, "seen_n": len(seen), "elapsed_s": round(time.time()-t0, 1)}
json.dump(out, open(BASE + "run-hot-leg-2026-11-16-0029.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:4000])
