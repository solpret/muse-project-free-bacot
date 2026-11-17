#!/usr/bin/env python3
"""Hot-leg run 2026-11-14 09:19 WIB: leg 1 Sourcify feed + leg 2 Boltbook EN/ZH.
Read-only except: appends newly-seen contracts to hot-leg-seen.json;
writes run-2026-11-14-0919-feed.json + boltbook html snapshots. No preview/mint."""
import json, re, subprocess, time, urllib.request, concurrent.futures

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
t0 = time.time()
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}

seen = json.load(open(BASE + "hot-leg-seen.json"))
out = {"started_wib": "2026-11-14T09:19+07:00", "feed": {}, "boltbook": {}, "new_seen": []}

# --- Leg 1: Sourcify feed ---
try:
    req = urllib.request.Request(
        "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc",
        headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        feed = json.loads(r.read().decode())
    addrs = []
    for c in feed:
        a = c.get("address") or (c.get("contract") or {}).get("address")
        if a: addrs.append(a)
    newest = feed[0].get("verifiedAt") if feed else None
    genuinely_new = [a for a in addrs if a not in seen and a.lower() not in EXCLUDED]
    out["feed"] = {"total": len(addrs), "newest_verifiedAt": newest,
                   "genuinely_new": genuinely_new,
                   "note": "All 20 already in hot-leg-seen.json" if not genuinely_new else f"{len(genuinely_new)} new"}
except Exception as e:
    out["feed"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# shape-check genuinely new feed contracts only
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
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
                "is_token": is_token, "functions": sorted(names)[:80]}
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {str(e)[:120]}"}

shapes = []
for a in out["feed"].get("genuinely_new", []):
    shapes.append(shapecheck(a))
out["feed"]["shapes"] = shapes

# --- Leg 2: Boltbook EN + ZH ---
def fetch_boltbook(lang_url, fname):
    try:
        r = subprocess.run(["curl","-sL","--max-time","60","-A","Mozilla/5.0","-o",BASE+fname, "-w","%{http_code} %{size_download}", lang_url],
                           capture_output=True, text=True, timeout=75)
        return r.stdout.strip()
    except Exception as e:
        return f"ERR {type(e).__name__}: {str(e)[:100]}"

bb = {}
for label, url, fname in [
        ("en", "https://boltbook.fun/", "run-2026-11-14-0919-boltbook-en.html"),
        ("zh", "https://boltbook.fun/?lang=zh", "run-2026-11-14-0919-boltbook-zh.html")]:
    st = fetch_boltbook(url, fname)
    addrs = []
    try:
        html = open(BASE+fname, encoding="utf-8", errors="ignore").read()
        addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    except Exception as e:
        st += f" | read ERR {e}"
    new_addrs = [a for a in addrs if a not in seen and a.lower() not in EXCLUDED]
    bb[label] = {"fetch": st, "addresses_total": len(addrs), "new": new_addrs}
out["boltbook"] = bb

# --- record newly seen (feed + boltbook) ---
now_wib = "2026-11-14T09:19:00+07:00"
for a in out["feed"].get("genuinely_new", []):
    seen[a] = {"first_seen": now_wib, "source": "hot-leg 0919 sourcify-feed"}
    out["new_seen"].append(a)
for label in ("en","zh"):
    for a in bb[label]["new"]:
        if a not in seen:
            seen[a] = {"first_seen": now_wib, "source": f"hot-leg 0919 boltbook-{label}"}
            out["new_seen"].append(a)
if out["new_seen"]:
    json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
out["elapsed_s"] = round(time.time()-t0, 1)
json.dump(out, open(BASE+"run-2026-11-14-0919-feed.json","w"), indent=1)
print(json.dumps(out, indent=1))
print("DONE elapsed", out["elapsed_s"])
