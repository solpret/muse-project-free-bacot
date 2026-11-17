#!/usr/bin/env python3
"""Hot-leg run 2026-11-11 18:04 WIB: Sourcify feed poll + shape-check,
Boltbook EN+ZH, bridge read-only, binanceai + RIGFORGE re-check,
focused re-read of live watchlist items (Stampooor near >70%, AgentPals,
ABYSSCABLE deadline 19:39, SUDOSAINTS, AgentRune, RAMRAIDERS, 0x7Eb9,
STALL, HANAMI, Bot Fighters track-C).
Read-only except run-2026-11-11-1804-*.json and hot-leg-seen.json appends.
Never writes snapshot/seen/state of main job. Never previews/mints.
"""
import json, re, time, urllib.request, concurrent.futures, subprocess, os
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-11 18:04 WIB"
t0 = time.time()
out = {"started_wib": TS}
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

def get(url, timeout=25, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "free-bacot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode(errors="replace")

# --- 1. Sourcify feed (retry 2x on RemoteDisconnected) ---
items, feed_err = [], None
for attempt in range(3):
    try:
        feed_raw = get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=25)
        feed = json.loads(feed_raw)
        json.dump(feed, open(BASE + "run-2026-11-11-1804-feed.json", "w"), indent=1)
        items = feed.get("results", [])
        out["feed"] = {"n": len(items), "attempt": attempt + 1,
                       "newest_verifiedAt": items[0].get("verifiedAt") if items else None,
                       "oldest_verifiedAt": items[-1].get("verifiedAt") if items else None}
        break
    except Exception as e:
        feed_err = f"{type(e).__name__}: {str(e)[:120]}"
        time.sleep(2)
else:
    out["feed"] = {"error": feed_err}
print("FEED", out["feed"], flush=True)

seen = {}
try:
    seen = json.load(open(BASE + "hot-leg-seen.json"))
    if not isinstance(seen, dict):
        seen = {}
except Exception:
    seen = {}
seen_l = {k.lower() for k in seen.keys()}
# also treat previous feed files as seen (1801 feed failed, 1754 ok)
for prevf in ("hot-leg-2026-11-11-1754-feed.json", "run-2026-11-11-1801-feed.json"):
    try:
        prev = json.load(open(BASE + prevf))
        for it in prev.get("results", []):
            seen_l.add(str(it.get("address", "")).lower())
    except Exception:
        pass
new_addrs = [it.get("address") for it in items if str(it.get("address", "")).lower() not in seen_l and it.get("address")]
json.dump(new_addrs, open(BASE + "run-2026-11-11-1804-feed-new.json", "w"), indent=1)
out["feed_new"] = new_addrs
print("FEED NEW:", new_addrs, flush=True)

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        meta = json.loads(get(url, timeout=25))
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply", "balanceOf"}) and "totalSupply" in names
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        is_nft = bool(names & {"tokenURI", "ownerOf", "safeTransferFrom"}) or "uri" in names
        return {"address": addr, "S1": s1, "S2": s2,
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token, "is_nft": is_nft,
                "fn_count": len(names)}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

shapes = []
if new_addrs:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        shapes = list(ex.map(fetch_abi, new_addrs))
out["feed_shape"] = {"s1_pass": [s["address"] for s in shapes if s.get("S1")],
                     "s2_pass": [s["address"] for s in shapes if s.get("S2")],
                     "shapes": shapes}
print("SHAPES S1", out["feed_shape"]["s1_pass"], "S2", out["feed_shape"]["s2_pass"], flush=True)

# --- 2. Boltbook EN + ZH ---
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
    html = None
    try:
        html = get(url, timeout=30)
    except Exception as e:
        try:
            r = subprocess.run(["curl", "-sL", "--max-time", "30", url], capture_output=True, text=True, timeout=35)
            if r.stdout and len(r.stdout) > 1000:
                html = r.stdout
                print(f"BOLTBOOK {lang}: urllib fail ({e}); curl OK", flush=True)
        except Exception as e2:
            print(f"BOLTBOOK {lang}: curl also fail {e2}", flush=True)
    if html:
        addrs = sorted(set(a for a in ADDR_RE.findall(html)))
        out[f"boltbook_{lang}"] = {"bytes": len(html), "addrs": addrs, "n": len(addrs)}
        open(BASE + f"run-2026-11-11-1804-boltbook-{lang}.html", "w").write(html)
        print(f"BOLTBOOK {lang}: {len(html)} bytes, {len(addrs)} addrs", flush=True)
    else:
        out[f"boltbook_{lang}"] = {"bytes": 0, "error": "urllib+curl failed", "addrs": []}
        print(f"BOLTBOOK {lang}: FAIL", flush=True)

try:
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for v in snap.get("contracts", {}).values():
        if isinstance(v, dict) and v.get("address"):
            snap_addrs.add(str(v["address"]).lower())
    for v in snap.get("track_c", {}).values():
        if isinstance(v, dict):
            for k in ("address", "sale", "token"):
                if v.get(k) and isinstance(v[k], str):
                    snap_addrs.add(v[k].lower())
except Exception:
    snap = {}
    snap_addrs = set()
bb_new = []
for lang in ("en", "zh"):
    for a in out.get(f"boltbook_{lang}", {}).get("addrs", []):
        if a.lower() not in seen_l and a.lower() not in snap_addrs and a not in bb_new:
            bb_new.append(a)
out["boltbook_new"] = bb_new
print("BOLTBOOK NEW:", bb_new, flush=True)

# --- 3. Bridge comparison (read-only) ---
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = bridge.get("contracts", {})
    not_in_snap = [a for a in bcontracts if a.lower() not in snap_addrs]
    discarded = [a for a in bcontracts if bcontracts[a].get("same_owner_discarded")]
    out["bridge"] = {"total": len(bcontracts), "not_in_snapshot": not_in_snap,
                     "same_owner_discarded": discarded, "mtime": "2026-11-08 18:21 (stale, last write)"}
    print("BRIDGE total", len(bcontracts), "not_in_snapshot", len(not_in_snap), "discarded", len(discarded), flush=True)
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
    print("BRIDGE FAIL", e, flush=True)

# --- 4. eth_call helpers (curl, BSC dataseed) ---
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]

def post_rpc(ep, payload, timeout=25):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)

def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            d = {}
            for item, key in zip(res, keys):
                d[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return d
        except Exception:
            continue
    return None

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

out["block"] = get_block()
print("BLOCK", out["block"], flush=True)

# binanceai + RIGFORGE
BIN_MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
v = raw_batch(BIN_MINT, ["launched()"])
out["binanceai"] = {"launched": (v or {}).get("launched")}
print("BINANCEAI", out["binanceai"], flush=True)

RIG_SALE = "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d"
rig = raw_batch(RIG_SALE, ["freeSharesLeft()", "openedAt()", "freeClaimed()", "freeBooked(address)"])
out["rigforge"] = rig or {"_batch_fail": True}
print("RIGFORGE", out["rigforge"], flush=True)

# --- 5. Focused re-read ---
LEAN = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
        "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
        "freeClaimed(address)"]
FOCUS = [
    ("Stampooor", "0x467696af8c2206B977B24081445104632dc1D459",
     ["totalSupply()", "totalMinted()", "freeMinted()", "FREE_SUPPLY()", "mintOpen()",
      "freeAvailable(address)", "balanceOf(address)"]),
    ("AgentPals", "0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", LEAN),
    ("ABYSSCABLE", "0xd2e9242b0d7c0186cc181a5fc8534541dad278a2", LEAN),
    ("SUDOSAINTS", "0x869d330bb48e7ab32da16745ef9a36a69d34f12f", LEAN),
    ("AgentRune", "0xc1fc0bb36d2be928809e4b3e6aa94b3dd2946f53", LEAN),
    ("RAMRAIDERS", "0x98dcfdeb5e015bbb3c9aca2a90ba0ee80e35315b", LEAN),
    ("0x7Eb9", "0x7Eb92041aa3037e39baA88154F279e3D9F85c593", LEAN),
    ("STALL", "0xe3de7fd0d12cff4a46d8bf702ab593b6f921b308", LEAN),
    ("HANAMI", "0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640", LEAN),
    ("BotFighters", "0x58a704d9e02FE11c0A61683AE7F606E4366F13eb",
     ["totalSupply()", "freeMinted()", "FREE_CAP()", "balanceOf(address)", "freeClaimed(address)"]),
]
reread = {}
def read_one(item):
    name, addr, views = item
    t = time.time()
    got = raw_batch(addr, views)
    d = {"address": addr}
    if got is None:
        d["_batch_fail"] = True
    else:
        d.update(got)
    print(f"REREAD {name}: {d} ({time.time()-t:.1f}s)", flush=True)
    return name, d
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for name, d in ex.map(read_one, FOCUS):
        reread[name] = d
out["reread"] = reread

# --- 6. Update hot-leg-seen.json (new feed + boltbook + 1801 early-shape, S1/S2 false) ---
now_iso = "2026-11-11T18:04:00+07:00"
added = []
for s in shapes:
    a = s["address"]
    if a.lower() in seen_l:
        continue
    seen[a] = {"first_seen_wib": now_iso,
               "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')}",
               "source": "sourcify-feed", "status": "checked-not-sale-shape"}
    seen_l.add(a.lower()); added.append(a)
for a in bb_new:
    if a.lower() in seen_l:
        continue
    seen[a] = {"first_seen_wib": now_iso, "note": "Boltbook front-page mention, shape-check pending next run",
               "source": "boltbook-frontpage", "status": "shape-pending"}
    seen_l.add(a.lower()); added.append(a)
# 1801 feed early-shape NFTs (S1/S2 false per run-2026-11-11-1801-shape-retry.json)
EARLY1801 = ["0xE2444a7419C4f76d68DE91b719f24C8A80e1aE4d",
             "0x433F98f0BE4Fe8C57a2Cc4036C9E75AF48108f58",
             "0xa594971e339510944a384Dd60e173733E76bEF5F",
             "0x8A7Be94d1C36A60BCdD155D37faF84403B8a26ae",
             "0x0adD0E9396481cf7F2387A896ae8CaCb956d7aD0",
             "0x12F6E9B79717548E1f37d3D25FB4AdE4C11079Bc"]
for a in EARLY1801:
    if a.lower() in seen_l:
        continue
    seen[a] = {"first_seen_wib": "2026-11-11T18:01:00+07:00",
               "note": "S1=False S2=False (1801 shape-retry), early_shape NFT (is_nft, mint+quote, no free views, no agent ref) - NOT a sale shape; hot-leg does no NFT early-lead detection (main job scan leg); not a lead, never previewed/minted.",
               "source": "sourcify-feed", "status": "checked-not-sale-shape"}
    seen_l.add(a.lower()); added.append(a)
if added:
    tmp = BASE + "hot-leg-seen.json.tmp"
    json.dump(seen, open(tmp, "w"), indent=1)
    os.replace(tmp, BASE + "hot-leg-seen.json")
out["seen_added"] = added
print("SEEN ADDED:", added, flush=True)

out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-11-1804.json", "w"), indent=1)
print("DONE in", out["elapsed_s"], "s", flush=True)
