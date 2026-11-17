#!/usr/bin/env python3
"""Hot-leg run 2026-11-14 09:54 WIB: leg 1 Sourcify feed + leg 2 Boltbook EN/ZH
+ leg 3 shape-check genuinely-new contracts.
Read-only except: appends truly-new contracts to hot-leg-seen.json
(case-insensitive dedupe); writes run-2026-11-14-0954-feed.json + boltbook
html snapshots. No preview/mint. Agent-ref set includes 'agentIdRegistry'
(gap flagged in 0919 runlog: Sol scored agent_ref=false without it)."""
import json, re, subprocess, time, urllib.request

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
t0 = time.time()
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"}
AGENT_REFS = {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate",
              "AgentGate", "agentIdRegistry"}
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_lower = {k.lower(): k for k in seen}
out = {"started_wib": "2026-11-14T09:54+07:00", "feed": {}, "boltbook": {},
       "shapecheck": {}, "new_seen": []}

# --- Leg 1: Sourcify feed ---
try:
    req = urllib.request.Request(
        "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc",
        headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.loads(r.read().decode())
    results = payload.get("results", []) if isinstance(payload, dict) else payload
    addrs = [c.get("address") for c in results if isinstance(c, dict) and c.get("address")]
    newest = results[0].get("verifiedAt") if results else None
    genuinely_new = [a for a in addrs if a.lower() not in seen_lower
                     and a.lower() not in EXCLUDED]
    out["feed"] = {"total": len(addrs), "newest_verifiedAt": newest,
                   "addresses": addrs, "genuinely_new": genuinely_new}
except Exception as e:
    out["feed"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# --- Leg 2: Boltbook EN + ZH ---
def fetch_boltbook(url, fname):
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "60", "-A", "Mozilla/5.0",
                            "-o", BASE + fname, "-w", "%{http_code} %{size_download}", url],
                           capture_output=True, text=True, timeout=75)
        return r.stdout.strip()
    except Exception as e:
        return f"ERR {type(e).__name__}: {str(e)[:100]}"

bb_new = []
for label, url, fname in [
        ("en", "https://boltbook.fun/", "run-2026-11-14-0954-boltbook-en.html"),
        ("zh", "https://boltbook.fun/?lang=zh", "run-2026-11-14-0954-boltbook-zh.html")]:
    st = fetch_boltbook(url, fname)
    addrs = []
    try:
        html = open(BASE + fname, encoding="utf-8", errors="ignore").read()
        addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    except Exception as e:
        st += f" | read ERR {e}"
    new_addrs = [a for a in addrs if a.lower() not in seen_lower
                 and a.lower() not in EXCLUDED]
    bb_new.extend(new_addrs)
    out["boltbook"][label] = {"fetch": st, "addresses_total": len(addrs),
                              "new": new_addrs}

# --- Leg 3: shape-check genuinely-new contracts (feed + boltbook) ---
def shapecheck(addr):
    try:
        req = urllib.request.Request(
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
            headers={"User-Agent": "hot-leg/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            meta = json.loads(r.read().decode())
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & AGENT_REFS)
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) \
            and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token,
                "functions": sorted(names)}
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {str(e)[:120]}"}

targets = list(out["feed"].get("genuinely_new", []))
for a in bb_new:
    if a.lower() not in [t.lower() for t in targets]:
        targets.append(a)
for a in targets:
    out["shapecheck"][a] = shapecheck(a)


# --- Retry last run's shape-check-failed contracts ---
for RETRY_ADDR, RETRY_FIRST in [
        ("0x072f7c31cc65f13c2fd5a1571e70be2087d5b741", "2026-11-14T09:49:00+07:00"),
        ("0x19f4e3601264e9d01551c6de207c064a7ab601a8", "2026-11-14T09:44:00+07:00")]:
    key = "retry_" + RETRY_ADDR[2:6]
    out[key] = shapecheck(RETRY_ADDR)
    if "error" not in out[key]:
        sc = out[key]
        seen[RETRY_ADDR] = {"first_seen_wib": RETRY_FIRST,
            "note": (f"RETRY 0954: S1={sc.get('S1')} S2={sc.get('S2')} mint={sc.get('has_mint')} "
                     f"quote={sc.get('has_quote')} free={sc.get('free_views')} "
                     f"agent={sc.get('agent_ref')} token={sc.get('is_token')}"),
            "source": "boltbook-frontpage-retry-0954",
            "status": ("sale-shape-pass" if (sc.get("S1") or sc.get("S2"))
                       else "checked-not-sale-shape")}
        json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
        out["new_seen"].append(RETRY_ADDR + " (retry-resolved)")

# --- record newly seen ---
now_wib = "2026-11-14T09:54:00+07:00"
for a in targets:
    sc = out["shapecheck"].get(a, {})
    if a.lower() in seen_lower:
        continue
    seen[a] = {"first_seen_wib": now_wib,
               "note": (f"S1={sc.get('S1')} S2={sc.get('S2')} mint={sc.get('has_mint')} "
                        f"quote={sc.get('has_quote')} free={sc.get('free_views')} "
                        f"agent={sc.get('agent_ref')} token={sc.get('is_token')}"
                        if "error" not in sc else f"shape-check FAILED: {sc.get('error')}"),
               "source": "hot-leg 0954 sourcify-feed/boltbook",
               "status": ("shape-check-failed" if "error" in sc else
                          "sale-shape-pass" if (sc.get("S1") or sc.get("S2"))
                          else "checked-not-sale-shape")}
    seen_lower[a.lower()] = a
    out["new_seen"].append(a)
if out["new_seen"]:
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-14-0954-feed.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("DONE elapsed", out["elapsed_s"])
