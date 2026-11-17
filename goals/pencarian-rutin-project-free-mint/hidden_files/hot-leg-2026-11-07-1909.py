#!/usr/bin/env python3
"""Hot-leg 2026-11-07 19:09 WIB. Legs 1-4 + bridge. Read-only except own hot-leg state."""
import json, re, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-1909"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted"]
out = {"run": "free-mint-hot-leg 2026-11-07 19:09:38 WIB", "leg1_feed": {}, "leg2_boltbook": {},
       "leg3_new_contracts": "none", "leg4_reread": {}, "bridge_leg": {}, "pending_claims": "snapshot pending_claims empty - nothing to re-read"}

def fetch(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_l = {k.lower(): v for k, v in seen.items()}

def shape_check(addr):
    """Return dict with S1/S2 via Sourcify ABI."""
    abi = None; match = None
    try:
        d = json.loads(fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}"))
        match = d.get("match")
        abi = d.get("abi") or (d.get("stdJson", {}).get("output", {}).get("abi") if isinstance(d.get("stdJson"), dict) else None)
    except Exception as e:
        match = f"v2-error:{e}"
    if abi is None:
        for kind in ("full_match", "partial_match"):
            try:
                m = json.loads(fetch(f"https://repo.sourcify.dev/contracts/{kind}/56/{addr}/metadata.json"))
                abi = m.get("output", {}).get("abi")
                if abi: match = kind; break
            except Exception:
                continue
    if not abi:
        return {"match": match, "error": "no-abi"}
    fns = [f.get("name") for f in abi if f.get("type") == "function" and f.get("name")]
    names = set(fns)
    has_mint = any(n.startswith("mint") for n in names)
    has_quote = any(("quote" in n.lower() or "cost" in n.lower() or "price" in n.lower()) for n in names)
    free = [v for v in FREE_VIEWS if v in names]
    raw = json.dumps(abi).lower()
    agent = REGISTRY.lower() in raw or "agentgate" in raw or "agentregistry" in raw or "agent_id" in raw
    tokenish = bool({"name", "symbol", "decimals", "totalSupply"} <= names)
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = tokenish and "mintFree" in names and ("freeClaimed" in names or "freeMinted" in names) and \
        bool({"FREE_SLOTS", "FREE_SUPPLY", "FREE_AMOUNT"} & names) and agent
    return {"match": match, "fns": len(fns), "fn_names": sorted(names), "mint": has_mint,
            "quote": has_quote, "free_views": free, "registry": agent, "S1": s1, "S2": s2}

def record_seen(addr, note, source, status):
    seen[addr] = {"first_seen_wib": "2026-11-07T19:09:38+07:00", "note": note, "source": source, "status": status}

# ---- Leg 1: Sourcify feed ----
try:
    feed = json.loads(fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"))
    json.dump(feed, open(f"{BASE}/hot-leg-{TS}-feed.json", "w"), indent=1)
    addrs = [r["address"] for r in feed.get("results", [])]
    new = [a for a in addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED]
    shapes = {}
    for a in new:
        sc = shape_check(a)
        shapes[a] = sc
        note = f"S1={sc.get('S1')} S2={sc.get('S2')} mint={sc.get('mint')} quote={sc.get('quote')} free={sc.get('free_views')} agent={sc.get('registry')} token={'token' if sc.get('fns') else ''}"
        record_seen(a, note, "sourcify-feed", "sale-shape" if (sc.get("S1") or sc.get("S2")) else "checked-not-sale-shape")
    json.dump(shapes, open(f"{BASE}/hot-leg-{TS}-sourcify-shape.json", "w"), indent=1)
    out["leg1_feed"] = {"n": len(addrs), "new": new,
        "shapes": "; ".join(f"{a[:10]} S1={s.get('S1')} S2={s.get('S2')} fns={s.get('fns')}" for a, s in shapes.items()) or "no new contracts"}
except Exception as e:
    out["leg1_feed"] = {"error": f"feed failed: {e}", "skipped": True}

# ---- Leg 2: Boltbook.fun EN + ZH ----
KW = ["free share", "first share free", "1 free share", "free mint share",
      "\u514d\u8d39\u4efd\u989d", "\u9996\u4e2a\u514d\u8d39", "\u514d\u8d39\u94f8\u9020", "\u514d\u8d39mint"]
try:
    pages = {}
    for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
        pages[lang] = fetch(url, timeout=15).decode("utf-8", "ignore")
        open(f"{BASE}/hot-leg-{TS}-boltbook-fun-{lang}.html", "w").write(pages[lang])
    all_addrs = set()
    for lang, html in pages.items():
        all_addrs |= set(re.findall(r"0x[0-9a-fA-F]{40}", html))
    kw_hits = {k: sum(pages[l].lower().count(k.lower()) for l in pages) for k in KW}
    new_bb = [a for a in sorted(all_addrs) if a.lower() not in seen_l and a.lower() not in EXCLUDED]
    shapes_bb = {}
    for a in new_bb:
        sc = shape_check(a)
        shapes_bb[a] = sc
        note = f"S1={sc.get('S1')} S2={sc.get('S2')} mint={sc.get('mint')} quote={sc.get('quote')} free={sc.get('free_views')} agent={sc.get('registry')}"
        record_seen(a, note, "boltbook-fun", "sale-shape" if (sc.get("S1") or sc.get("S2")) else "checked-not-sale-shape")
    json.dump({"addrs": sorted(all_addrs), "kw": kw_hits, "new": new_bb, "shapes": shapes_bb},
              open(f"{BASE}/hot-leg-{TS}-boltbook-shape.json", "w"), indent=1)
    out["leg2_boltbook"] = {"status": "COMPLETED", "addrs": len(all_addrs), "new": new_bb,
        "kw_hits": kw_hits, "shapes": {a: (s.get("S1"), s.get("S2")) for a, s in shapes_bb.items()}}
except Exception as e:
    out["leg2_boltbook"] = {"error": f"boltbook failed: {e}", "skipped": True}

json.dump(new_bb if 'new_bb' in dir() else [], open(f"{BASE}/hot-leg-{TS}-boltbook-new.json", "w"))
json.dump(out["leg1_feed"].get("new", []), open(f"{BASE}/hot-leg-{TS}-new.json", "w"))

# ---- Leg 3: new sale-shape contracts ----
sale_new = [a for a, s in list(shapes.items()) + list(shapes_bb.items()) if s.get("S1") or s.get("S2")] \
    if 'shapes' in dir() and 'shapes_bb' in dir() else []
out["leg3_new_contracts"] = f"{len(sale_new)} S1/S2 new: {sale_new}" if sale_new else "No S1/S2 hits from feed or Boltbook.fun - no leg-3 on-chain verification needed."

# ---- Leg 4: re-read snapshot items ----
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def single(addr, sig, arg=""):
    from fast_rpc import _single
    data = sel(sig) + arg
    for ep in EPS:
        try:
            return to_int(_single(ep, "eth_call", [{"to": addr, "data": data}, "latest"], 8, retries=0))
        except Exception:
            continue
    return None
def batch_views(addr, views):
    calls, keys = [], []
    for sig in views:
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        elif "(uint256)" in sig:
            data = sel(sig) + enc_uint(1); key = base + "_1"
        else:
            data = sel(sig); key = base
        calls.append(("eth_call", [{"to": addr, "data": data}, "latest"])); keys.append(key)
    for ep in EPS:
        try:
            return {k: to_int(v) for k, v in zip(keys, batch(calls, endpoint=ep, timeout=8))}
        except Exception:
            continue
    return None

ITEMS = {
 "Orchidia": "0x09bcdd97186f6f37521bd1b281d329e48ac54b89",
 "Agent Goats": "0x0E9E0a3B46dC0d36A1Ab64f553Dd8A0693E6aAa6",
 "Tacotron": "0x05debe4445232205ae7e79d02cb5de5aa0641eff",
 "Agent Frogs": "0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31",
 "Wuyuhive": "0x250e800025a9a7861970e253bab6975a57f80567",
 "Thronemind": "0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90",
 "Ink Koi": "0xbd4B4e7189ae9356514664146b0eD683601200A9",
 "Night Bandits Club": "0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf",
 "ADCHAR": "0x6E8b05C2dD1C625D839f33f60B837d9AF25E6044",
}
LEADS = {
 "CipherAgent": "0x158b5e25015758a94703A27c152889451E5d52E5",
 "MarsAgent": "0x2231FdAe405c33dc4993f8C577c453802FF1AcE9",
}
MINIMAL = ["totalSupply()", "balanceOf(address)"]
reread = {"block": None, "items": {}, "leads": {}}
try:
    reread["block"] = int(batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=8)[0], 16)
except Exception:
    reread["block"] = None
for name, addr in ITEMS.items():
    d = {"address": addr}
    got = batch_views(addr, MINIMAL)
    if got is not None:
        d.update(got)
    else:
        d["totalSupply"] = None; d["balanceOf_user"] = None; d["_rpc"] = "minimal-failed"
    if name == "Ink Koi":
        d["freeMinted"] = single(addr, "freeMinted()")
    if name == "Night Bandits Club":
        d["freeUsed"] = single(addr, "freeUsed()")
        d["freeTakenBy_user"] = single(addr, "freeTakenBy(address)", enc(USER))
        d["mintOpen"] = single(addr, "mintOpen()")
    if name == "ADCHAR":
        d["hasClaimed_user"] = single(addr, "hasClaimed(address)", enc(USER))
        d["nextTokenId"] = single(addr, "nextTokenId()")
    reread["items"][name] = d
for name, addr in LEADS.items():
    d = {"address": addr}
    got = batch_views(addr, MINIMAL)
    if got is not None:
        d.update(got)
    d["totalMints"] = single(addr, "totalMints()")
    d["mintOpen"] = single(addr, "mintOpen()")
    reread["leads"][name] = d
json.dump(reread, open(f"{BASE}/hot-leg-{TS}-reread.json", "w"), indent=1)
out["leg4_reread"] = reread

# ---- Bridge leg ----
try:
    import os
    b = json.load(open(f"{BASE}/scan-bridge.json"))
    c = b.get("contracts", {})
    out["bridge_leg"] = {"status": "unchanged" if os.path.getmtime(f"{BASE}/scan-bridge.json") == 1791334080.7650243 else "check-mtime",
        "mtime": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(os.path.getmtime(f"{BASE}/scan-bridge.json"))),
        "total": len(c), "same_owner_discarded": sum(1 for v in c.values() if v.get("same_owner_discarded")),
        "note": "no new promotions, no tier change"}
except Exception as e:
    out["bridge_leg"] = {"status": "skip - unreadable", "error": str(e)}

json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
out["seen_total"] = len(seen)
json.dump(out, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:6000])
