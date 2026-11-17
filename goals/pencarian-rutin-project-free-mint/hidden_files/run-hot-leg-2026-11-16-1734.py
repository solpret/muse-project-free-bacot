#!/usr/bin/env python3
"""hot-leg run 2026-11-16 17:34 WIB. Legs 1+2 (Sourcify feed + Boltbook EN/ZH),
shape-check new contracts, bridge leg (read-only), leg 4 reread focus set
(AGCLUB, MORFO, BinanceAI-mint, ORBIT, RigForge, CosmicSentinel — same as
1729 run). Read-only except hot-leg-seen.json notes and this run's own
outputs. No preview/mint. No snapshot rewrite."""
import json, re, time, urllib.request, subprocess
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
T0 = time.time()
NOW = "2026-11-16T17:34:38+07:00"
out = {"run": "free-mint-hot-leg 2026-11-16 17:34 WIB", "started_wib": NOW}

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

seen = json.load(open(BASE + "hot-leg-seen.json"))

# --- Leg 1: Sourcify feed ---
try:
    raw = fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=15)
    feed = json.loads(raw)
    contracts = []
    for c in (feed if isinstance(feed, list) else feed.get("results", [])):
        a = c.get("address") if isinstance(c, dict) else None
        if a: contracts.append(a)
    va = [c.get("verifiedAt") for c in (feed if isinstance(feed, list) else feed.get("results", [])) if isinstance(c, dict) and c.get("verifiedAt")]
    new = [a for a in contracts if a not in seen and a.lower() != REGISTRY.lower()]
    out["feed"] = {"n": len(contracts), "newest_verifiedAt": max(va) if va else None,
                   "oldest_verifiedAt": min(va) if va else None}
    out["feed_new"] = new
except Exception as e:
    out["feed"] = {"error": f"{type(e).__name__}: {e}"}
    new = []

# --- Leg 2: Boltbook EN + ZH ---
def boltbook(lang):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    try:
        raw = fetch(url, timeout=20)
    except Exception:
        r = subprocess.run(["curl", "-sL", "--max-time", "25", url], capture_output=True)
        if r.returncode != 0 or not r.stdout:
            raise RuntimeError("curl fallback failed: " + r.stderr.decode(errors="ignore")[:120])
        raw = r.stdout
    text = raw.decode("utf-8", errors="ignore")
    addrs = sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", text)))
    return {"bytes": len(raw), "addrs": addrs,
            "kw": {"free share": text.lower().count("free share"),
                   "first share free": text.lower().count("first share free"),
                   "free mint share": text.lower().count("free mint share"),
                   "1 free share": text.lower().count("1 free share"),
                   "免费份额": text.count("免费份额"), "首个免费": text.count("首个免费"),
                   "免费铸造": text.count("免费铸造"), "免费mint": text.count("免费mint")}}
bb = {}
for lang in ("en", "zh"):
    try: bb[lang] = boltbook(lang)
    except Exception as e: bb[lang] = {"error": f"{type(e).__name__}: {e}"}
out["boltbook_en"] = bb["en"]; out["boltbook_zh"] = bb["zh"]
bb_new = []
for lang in ("en", "zh"):
    for a in bb.get(lang, {}).get("addrs", []):
        if a not in seen and a not in bb_new: bb_new.append(a)
out["boltbook_new"] = bb_new

# --- Shape-check new contracts (legs 1+2) ---
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedTotal"]
def shape(addr):
    try:
        raw = fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=15)
        d = json.loads(raw)
        abi = d.get("abi") or (d.get("stdJson", {}) or {}).get("abi") or []
    except Exception as e:
        return {"status": "shape-check-failed", "error": f"{type(e).__name__}: {e}"}
    names = [f.get("name", "").lower() for f in abi if isinstance(f, dict)]
    has_mint = any(n.startswith("mint") or n in ("claimfree", "claim", "mintfree") for n in names)
    has_quote = any("quote" in n or "price" in n or n.startswith("cost") for n in names)
    free = sorted(set(n for n in names if any(k.lower() in n for k in FREE_VIEWS)))
    agent = any("agent" in n or "registry" in n for n in names) or REGISTRY.lower() in json.dumps(abi).lower()
    tokenish = all(k in names for k in ("name", "symbol", "decimals", "totalsupply"))
    noarg_free = any(n in ("mintfree", "claimfree") for n in names)
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = tokenish and noarg_free and bool(free) and agent
    return {"S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
            "free": free, "agent": agent, "status": "checked"}
EXCLUDED = ("0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493")
shape_res = {}
for a in (new + bb_new):
    if a.lower() in EXCLUDED:
        shape_res[a] = {"status": "excluded-example"}
        continue
    shape_res[a] = shape(a)
out["feed_shape"] = {a: shape_res[a] for a in new}
out["boltbook_new_shapecheck"] = {a: shape_res[a] for a in bb_new}

# record newly seen (hot-leg's own file only)
for a in (new + bb_new):
    if a not in seen:
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed" if a in new else "boltbook",
                   "status": shape_res.get(a, {}).get("status", "checked"),
                   "note": json.dumps(shape_res.get(a, {}))[:300]}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["seen_total"] = len(seen)

# --- Bridge leg (read-only) ---
try:
    br = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = br.get("contracts", {})
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for sec in ("contracts", "track_c"):
        for e in snap.get(sec, {}).values():
            if isinstance(e, dict) and e.get("address"):
                snap_addrs.add(e["address"].lower())
    for e in snap.get("pending_claims", {}).values():
        if isinstance(e, dict) and e.get("mint"):
            snap_addrs.add(e["mint"].lower())
    outside = []
    discarded = 0
    for addr, info in bcontracts.items():
        if info.get("same_owner_discarded"):
            discarded += 1
            continue
        if addr.lower() not in snap_addrs:
            outside.append(addr)
    out["bridge"] = {"n": len(bcontracts), "same_owner_discarded": discarded,
                     "outside_snapshot": outside}
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {e}"}

# --- Leg 4: reread focus set ---
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42: d += enc_addr(a)
        elif isinstance(a, str) and a.startswith("0x"): d += enc_u(int(a, 16))
        else: d += enc_u(int(a))
    return d
def post_rpc(ep, payload, timeout=60):
    o = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(o)

U = [USER]
ITEMS = {
 "AGCLUB": ("0x67270bb351515abf3089ca5420456897363f5e75", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("FREE_CAP","FREE_CAP()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("totalMinted","totalMinted()",[]),
    ("balanceOf_user","balanceOf(address)",U)]),
 "MORFO": ("0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186", [
    ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[])]),
 "BinanceAI-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched","launched()",[]),("failed","failed()",[]),
    ("isRefundPhase","isRefundPhase()",[]),("totalShares","totalShares()",[]),
    ("tokenClaimed_user","tokenClaimed(address)",U)]),
 "ORBIT": ("0x7d5F7f323db3050AF92E9aa1584E883B3b24d680", [
    ("freeClaimed","freeClaimed()",[]),("FREE_MAX","FREE_MAX()",[]),
    ("claimOpen","claimOpen()",[]),("hasFreeClaimed_user","hasFreeClaimed(address)",U),
    ("totalSupply","totalSupply()",[])]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", [
    ("freeSharesLeft","freeSharesLeft()",[]),("openedAt","openedAt()",[]),
    ("freeClaimed","freeClaimed()",[]),("freeBooked_user","freeBooked(address)",U)]),
 "CosmicSentinel": ("0x88731d1eb41c36f3d705fdb58b658244c06afc36", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
}
def chunked(items, n=3):
    items = list(items.items())
    for i in range(0, len(items), n):
        yield items[i:i+n]
def read_chunk(chunk):
    calls, meta = [], []
    for name, (addr, views) in chunk:
        for key, sig, args in views:
            calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                          "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
            meta.append((name, key))
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=60)
            if not isinstance(res, list) or len(res) != len(calls):
                print("  chunk ep", ep, "bad shape", str(res)[:120], flush=True); continue
            o = {}
            for it, (name, key) in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    o.setdefault(name, {})[key] = None
                else:
                    r = it["result"]
                    o.setdefault(name, {})[key] = to_int(r[:66]) if len(r) >= 66 else r
            return o, ep
        except Exception as e:
            print("  chunk ep", ep, "exc", str(e)[:100], flush=True); continue
    return None, None
def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=60)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16)
        except Exception: continue
    return None

reads, ok = {}, 0
for ci, ch in enumerate(chunked(ITEMS, 3)):
    r, ep = read_chunk(ch)
    names = [n for n, _ in ch]
    if r is None:
        print(f"chunk {ci+1} FAIL {names}", flush=True)
        for n in names: reads[n] = {"address": ITEMS[n][0], "views": None}
        continue
    ok += sum(1 for n in names if r.get(n) is not None)
    for n in names: reads[n] = {"address": ITEMS[n][0], "views": r.get(n)}
    print(f"chunk {ci+1} OK via {ep} ({time.time()-T0:.0f}s) {names}", flush=True)
    time.sleep(3)
blk = block_number()
reread = {"started_wib": NOW, "reads": reads, "reads_ok": ok,
          "reads_total": len(ITEMS), "block": blk, "elapsed_s": round(time.time() - T0, 1)}
json.dump(reread, open(BASE + "run-hot-leg-2026-11-16-1734-reread.json", "w"), indent=1)
out["reread_block"] = blk
out["reread_ok"] = f"{ok}/{len(ITEMS)}"
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + "run-hot-leg-2026-11-16-1734.json", "w"), indent=1)
print("DONE ok", ok, "/", len(ITEMS), "block", blk, "elapsed", round(time.time() - T0, 1))
