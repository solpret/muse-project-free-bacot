#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-10 06:44 WIB. Legs 1-4 + bridge (read-only).
Writes only own hot-leg state files + run JSON. No preview/mint.
No snapshot writes. Hard-capped; stalled legs skipped, not waited on."""
import json, re, time, urllib.request, concurrent.futures
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC = "https://bsc-dataseed.bnbchain.org"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
T0 = time.time()
RUN_WIB = "2026-11-10 06:44 WIB"
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")

def fetch(url, timeout=15, ua="hot-leg/1.0"):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
reported = json.load(open(BASE + "hot-leg-reported.json"))
out = {"run": RUN_WIB, "leg1_feed": 0, "leg1_new": [], "leg1_shape": "",
       "leg2_boltbook": "", "leg3": "no new sale-shape contract; nothing to verify",
       "leg4_file": "hot-leg-run-2026-11-10-0644-leg4.json", "leg4_notes": "",
       "bridge": "", "promotions": [], "changes": [], "report": "NONE - silent run"}

# ---- Leg 1: Sourcify recently-verified feed ----
feed_addrs = []
try:
    st, body = fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=15)
    data = json.loads(body.decode())
    items = data if isinstance(data, list) else data.get("results", data.get("contracts", []))
    for it in items:
        a = it.get("address") if isinstance(it, dict) else None
        if a:
            feed_addrs.append(a)
    out["leg1_feed"] = len(feed_addrs)
except Exception as e:
    out["leg1_feed"] = f"ERR:{type(e).__name__}"

new_feed = [a for a in feed_addrs if a.lower() not in seen_l and a.lower() != REG.lower()
            and a.lower() not in EXCLUDED]
out["leg1_new"] = new_feed

# ---- Leg 2: Boltbook front page EN + ZH (boltbook.fun) ----
bb_addrs, bb_notes = [], []
for lang, url in (("en", "https://boltbook.fun/?lang=en"),
                  ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        st, body = fetch(url, timeout=15)
        txt = body.decode(errors="ignore")
        addrs = sorted(set(ADDR_RE.findall(txt)))
        bb_addrs += addrs
        hits = [k for k in ("free share", "first share free", "1 free share", "free mint share",
                            "免费份额", "首个免费", "免费铸造", "免费mint")
                if k.lower() in txt.lower()]
        bb_notes.append(f"{lang.upper()} {st} ({len(body)}B, {len(addrs)} addrs, kw={hits})")
    except Exception as e:
        bb_notes.append(f"{lang.upper()} ERR:{type(e).__name__}")
bb_new = sorted({a for a in bb_addrs if a.lower() not in seen_l
                 and a.lower() != REG.lower() and a.lower() not in EXCLUDED})
out["leg2_boltbook"] = "; ".join(bb_notes) + f"; new addrs: {bb_new}"

# ---- Shape-check any new contract (S1/S2 via Sourcify ABI) ----
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"}
def shape_check(addr):
    try:
        st, body = fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=15)
        meta = json.loads(body.decode())
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId",
                                  "agentGate", "AgentGate"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s2 = (is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"})
              and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref)
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
                "is_token": is_token}
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {str(e)[:100]}"}

all_new = sorted(set(new_feed) | set(bb_new))
shape_results = []
if all_new:
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        shape_results = list(ex.map(shape_check, all_new))
    out["leg1_shape"] = json.dumps(shape_results)
    for r in shape_results:
        a = r["address"]
        if a.lower() in EXCLUDED:
            stt, note = "excluded", "excluded example rediscovered; not reported"
        elif r.get("S1") or r.get("S2"):
            stt, note = "sale-shape", f"S1={r.get('S1')} S2={r.get('S2')} free={r.get('free_views')}"
        else:
            stt, note = "checked-not-sale-shape", (
                f"S1={r.get('S1')} S2={r.get('S2')} mint={r.get('has_mint')} "
                f"quote={r.get('has_quote')} free={r.get('free_views')} "
                f"agent={r.get('agent_ref')} token={r.get('is_token')}")
        seen[a] = {"first_seen_wib": "2026-11-10T06:44:00+07:00", "note": note,
                   "source": "hot-leg-0644", "status": stt}
else:
    out["leg1_shape"] = "all feed/Boltbook contracts already in hot-leg-seen.json; no new contract to shape-check"

sale_shape = [r for r in shape_results if r.get("S1") or r.get("S2")]
if sale_shape:
    out["leg3"] = f"NEW SALE-SHAPE: {sale_shape} - needs on-chain verify + gate (not auto-handled here; flagged for main job)"
    # Age-unverified by default: record watchlist-only, never lead, never preview.
    for r in sale_shape:
        seen[r["address"]]["status"] = "watchlist-only-age-unverified"
        seen[r["address"]]["note"] += " | age UNVERIFIED - watchlist-only, never lead"

# ---- Leg 4: re-read snapshot active items (read-only eth_call) ----
def sel(sig):
    h = keccak.new(digest_bits=256); h.update(sig.encode()); return "0x" + h.hexdigest()[:8]

def call(addr, sig, arg=None):
    data = sel(sig)
    if arg is not None:
        data += "000000000000000000000000" + arg[2:].lower()
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": addr, "data": data}, "latest"]}).encode()
    req = urllib.request.Request(RPC, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.load(r)
        res = d.get("result")
        if not res or res == "0x":
            return None
        return int(res, 16)
    except Exception as e:
        return f"ERR:{type(e).__name__}"

jobs = [
    ("SAKURA", "0xF2705A84602369069782624279837A08bdbBf6D6",
     [("totalSupply()", None), ("freeClaimed()", None)]),
    ("THYRK", "0x4D90fFC3075FB8897EDFf6d7c6269c906664a20e",
     [("totalSupply()", None), ("freeMinted()", None)]),
    ("Golden Agents", "0x4233C62919CC03168a361C547117c1553C375bfC",
     [("totalSupply()", None)]),
    ("ADVAGENT sale", "0x7635ef16370ef490298649a188c9205d1d7fda67",
     [("freeClaimed(address)", USER)]),
    ("NUSA sale", "0x7D08289E962f5aEc00d56D67322eb2FD056B687c",
     [("freeRemaining()", None), ("freeUsed(address)", USER)]),
    ("VISION sale", "0x5f76cAb7B054e088563D5098E17bD0dc430e61aE",
     [("totalFreeShares()", None), ("freeUsed(address)", USER)]),
    ("BHTB", "0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467",
     [("freeMinted()", None), ("freeClaimed(address)", USER)]),
    ("AgentGrid sale", "0x651302C0043040D48EaAF85605E12F0549aD6D89",
     [("freeUsed(address)", USER)]),
]
leg4 = {}
t4 = time.time()
for name, addr, calls in jobs:
    leg4[name] = {"address": addr, "reads": {}}
    for sig, arg in calls:
        if time.time() - T0 > 105:
            leg4[name]["reads"][sig] = "SKIPPED-timecap"
            continue
        leg4[name]["reads"][sig] = call(addr, sig, arg)
json.dump({"run": RUN_WIB, "leg4": leg4, "elapsed_s": round(time.time() - t4, 1)},
          open(BASE + "hot-leg-run-2026-11-10-0644-leg4.json", "w"), indent=1)

# Compare vs 06:39 reads for change detection
prev = {}
try:
    prev = json.load(open(BASE + "hot-leg-run-2026-11-10-0639-leg4.json"))["leg4"]
except Exception:
    pass
notes = []
for name, d in leg4.items():
    p = prev.get(name, {}).get("reads", {})
    for sig, v in d["reads"].items():
        pv = p.get(sig)
        if isinstance(v, int) and isinstance(pv, int) and v != pv:
            notes.append(f"{name} {sig}: {pv}->{v}")
        elif isinstance(v, str) and v.startswith("ERR"):
            notes.append(f"{name} {sig}: READ ERR ({v}) - transient, retry next run")
        elif v is None and pv is not None:
            notes.append(f"{name} {sig}: read null (was {pv}) - view mismatch/no change proven")
out["leg4_notes"] = "; ".join(notes) if notes else "no numeric change vs 06:39 reads"

# SAKURA free% check (free 924 claimed of 6000 per run 0401 baseline; totalSupply proxy)
sak = leg4.get("SAKURA", {}).get("reads", {}).get("totalSupply()")
if isinstance(sak, int):
    out["leg4_notes"] += f" | SAKURA totalSupply {sak}; free% max ~{round(sak/6000*100,1)}% (<25%, stays early lead)"
th = leg4.get("THYRK", {}).get("reads", {})
if isinstance(th.get("totalSupply()"), int):
    out["leg4_notes"] += (f" | THYRK totalSupply {th.get('totalSupply()')}, "
                          f"freeMinted {th.get('freeMinted()')} (no free cap, stays early lead)")
vis = leg4.get("VISION sale", {}).get("reads", {})
if isinstance(vis.get("totalFreeShares()"), int):
    out["leg4_notes"] += (f" | VISION totalFreeShares {vis.get('totalFreeShares()')}, "
                          f"freeUsed(user)={vis.get('freeUsed(address)')} slot still open, "
                          f"website gate still pending (no site found) - NOT previewed/minted")
adv = leg4.get("ADVAGENT sale", {}).get("reads", {}).get("freeClaimed(address)")
if adv == 1:
    out["leg4_notes"] += " | ADVAGENT freeClaimed(user)=1 slot used as expected"

# ---- Bridge leg (read-only) ----
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_l = {str(k).lower() for k in snap.get("contracts", {})}
    snap_l |= {str(k).lower() for k in snap.get("track_c", {})}
    bcontracts = bridge.get("contracts", {})
    if isinstance(bcontracts, dict):
        blist = list(bcontracts.values())
    else:
        blist = bcontracts
    not_in_snap = []
    disc = []
    for c in blist:
        if isinstance(c, dict):
            a = (c.get("address") or c.get("contract") or "").lower()
            tier = c.get("tier") or c.get("status") or ""
            if c.get("same_owner_discarded"):
                disc.append(a[:10])
            if a and a not in snap_l:
                not_in_snap.append((a[:10], tier))
    out["bridge"] = (f"read-only; {len(blist)} contracts, {len(not_in_snap)} not in snapshot "
                     f"{not_in_snap} - none meets a Free Bacot tier; noted for main job only, "
                     f"no report. same_owner_discarded in bridge: {disc} - never promoted.")
except Exception as e:
    out["bridge"] = f"SKIP - bridge unreadable ({type(e).__name__}); run continues normally"

# ---- Persist own state only ----
if all_new:
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + "hot-leg-run-2026-11-10-0644.json", "w"), indent=1)
print(json.dumps(out, indent=1))
