#!/usr/bin/env python3
"""Hot-leg run 2026-11-07 04:09 WIB. Legs 1+2 (+bridge counts). Read-only except hot-leg-seen.json."""
import json, urllib.request, time, re
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-0409"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE = ["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freemint","free_slots","free_supply","freeamount"]

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_lc = {k.lower(): k for k in seen}
print("seen total before:", len(seen))

# Leg 1: Sourcify feed
feed = json.loads(fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"))
addrs1 = [r["address"] for r in feed.get("results", [])]
print("leg1 feed:", len(addrs1), "verifiedAt newest:", addrs1 and feed["results"][0].get("verifiedAt"))
new1 = [a for a in addrs1 if a.lower() not in seen_lc and a.lower() != REG.lower() and a.lower() not in EXCLUDED]
print("leg1 new vs seen:", new1)

# Leg 2: Boltbook EN + ZH
addrs2 = []
for lang, url in [("en", "https://boltbook.fun/?lang=en"), ("zh", "https://boltbook.fun/?lang=zh")]:
    try:
        html = fetch(url, timeout=25).decode("utf-8", "ignore")
        found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        print(f"leg2 {lang}: HTTP ok, {len(html)} bytes, {len(found)} addrs")
        addrs2 += found
        open(f"{BASE}/hot-leg-{TS}-boltbook-{lang}.html", "wb").write(html.encode())
    except Exception as e:
        print(f"leg2 {lang}: FAILED {e}")
addrs2 = sorted(set(addrs2))
new2 = [a for a in addrs2 if a.lower() not in seen_lc and a.lower() != REG.lower() and a.lower() not in EXCLUDED]
print("leg2 unique addrs:", len(addrs2), "new vs seen:", new2)
kw = ["免费份额", "首个免费", "免费铸造", "免费mint", "free share", "first share free", "1 free share", "free mint share"]
for lang in ("en", "zh"):
    try:
        html = open(f"{BASE}/hot-leg-{TS}-boltbook-{lang}.html", encoding="utf-8", errors="ignore").read().lower()
        hits = [k for k in kw if k.lower() in html]
        print(f"leg2 {lang} keyword hits:", hits)
    except Exception as e:
        print(f"leg2 {lang} kw check failed:", e)

# Shape-check all new
to_check = sorted(set([a.lower() for a in new1 + new2]))
print("shape-check queue:", to_check)
shape = {}
for a in to_check:
    abi = None; status = None
    for t in range(3):
        try:
            d = json.loads(fetch(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"))
            abi = d.get("abi") or []
            status = "ok"; break
        except Exception as e:
            status = str(e); time.sleep(2)
    if abi is None:
        shape[a] = {"error": status}; print(a, "ERROR", status); continue
    fns = [f.get("name", "") for f in abi if f.get("type") == "function"]
    src = json.dumps(abi).lower()
    mint = [f for f in fns if "mint" in f.lower()]
    quote = [f for f in fns if "quote" in f.lower() or "cost" in f.lower() or f.lower() in ("price", "getprice")]
    free = [f for f in fns if any(k in f.lower() for k in FREE)]
    agent = [f for f in fns if "agent" in f.lower() or "registry" in f.lower()]
    token = [f for f in fns if f.lower() in ("name", "symbol", "decimals", "totalsupply")]
    s1 = bool(mint) and bool(quote) and bool(free) and (REG.lower() in src or bool(agent))
    s2 = len(token) == 4 and any("mintfree" in f.lower() for f in fns) and bool(free) and (REG.lower() in src or bool(agent))
    shape[a] = {"S1": s1, "S2": s2, "mint": mint, "quote": quote, "free": free, "agent": agent, "token": token, "n_fns": len(fns)}
    print(a, "S1", s1, "S2", s2, "mint", mint, "quote", quote, "free", free, "agent", agent, "token", token)

json.dump({"feed": addrs1, "boltbook": addrs2, "new": to_check, "shape": shape},
          open(f"{BASE}/hot-leg-{TS}-sourcify-shape.json", "w"), indent=1)

# Update seen (lowercase-normalised keys for new entries; never rewrite existing keys)
now = "2026-11-07T04:09:00+07:00"
for a, s in shape.items():
    if a not in seen_lc:
        seen[a] = {"first_seen_wib": now,
                   "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={bool(s.get('mint'))} quote={bool(s.get('quote'))} free={s.get('free')} agent={bool(s.get('agent'))} token={s.get('token')}",
                   "source": "sourcify-feed+boltbook" if a in [x.lower() for x in new1] else "boltbook",
                   "status": "sale-shape" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"}
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
print("seen total after:", len(seen))

# Bridge leg (read-only counts)
bridge = json.load(open(f"{BASE}/scan-bridge.json"))
contracts = bridge.get("contracts", {})
snap_text = open(f"{BASE}/onchain-snapshot.json", encoding="utf-8", errors="ignore").read().lower()
disc = [a for a, v in contracts.items() if v.get("same_owner_discarded")]
in_snap = [a for a in contracts if a.lower() in snap_text]
not_in = [a for a in contracts if a.lower() not in snap_text]
print("bridge total:", len(contracts), "same_owner_discarded:", len(disc),
      "in-snapshot-by-text:", len(in_snap), "not-in-snapshot:", len(not_in))
print("DONE")
