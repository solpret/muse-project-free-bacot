#!/usr/bin/env python3
"""Hot-leg run 2026-11-12 01:49 WIB: Sourcify feed poll + shape-check,
Boltbook EN+ZH, bridge comparison (read-only), leg-4 priority re-read
(Stampooor gate-blocked strong lead 882/1200 (73.5%, deadline ~09:00 WIB),
Moonfang minted+sold out 200/200, Eco early lead, SEVEN 61%, Pickgrid 72% age-
unverified, AGCR 99% age-unverified, SUDOSAINTS/RIGFORGE/CAP7/BINANCEAI
+ others), Stampooor site re-check.
Read-only except hot-leg-run-2026-11-12-0149.json and hot-leg-seen.json
additions/updates for newly seen contracts. Never writes snapshot/seen/
state of the main job. Guard: all-null eth_call results = READ FAILURE,
never a state reading (prior state retained).
"""
import json, re, time, urllib.request, concurrent.futures, subprocess
from datetime import datetime, timezone, timedelta
WIB = timezone(timedelta(hours=7))
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-12 01:49 WIB"
t0 = time.time()
out = {"run": "free-mint-hot-leg 2026-11-12 01:49 WIB", "started_wib": TS}
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
RETRY_SHAPE = ["0x6f1b01eeecb2204299473a5b9fb90d9ca32eb658"]

def get(url, timeout=25, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "free-bacot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode(errors="replace")

def curl_get(url, timeout=25):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url],
                       capture_output=True, text=True, timeout=timeout + 5)
    if r.stdout and len(r.stdout) > 50:
        return r.stdout
    raise RuntimeError(f"curl empty/short: rc={r.returncode}")

# --- 1. Sourcify feed ---
items = []
try:
    feed_raw = get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc")
    feed = json.loads(feed_raw)
except Exception as e:
    try:
        feed_raw = curl_get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc")
        feed = json.loads(feed_raw)
        out["feed_note"] = "urllib fail; curl retry OK"
    except Exception as e2:
        out["feed"] = {"error": f"urllib {type(e).__name__}: {str(e)[:100]}; curl {type(e2).__name__}: {str(e2)[:100]}"}
        feed = {}
if feed:
    json.dump(feed, open(BASE + "run-2026-11-12-0149-feed.json", "w"), indent=1)
    items = feed.get("results", [])
    out["feed"] = {"n": len(items), "newest_verifiedAt": items[0].get("verifiedAt") if items else None,
                   "oldest_verifiedAt": items[-1].get("verifiedAt") if items else None}

seen = {}
try:
    seen = json.load(open(BASE + "hot-leg-seen.json"))
    if not isinstance(seen, dict):
        seen = {}
except Exception:
    seen = {}
seen_l = {k.lower() for k in seen.keys()}
for _prevf in ("run-2026-11-12-0144-feed.json", "run-2026-11-12-0139-feed.json", "run-2026-11-12-0134-feed.json", "run-2026-11-12-0124-feed.json", "run-2026-11-12-0109-feed.json",
               "run-2026-11-12-0039-feed.json", "run-2026-11-11-2359-feed.json",
               "run-2026-11-11-2334-feed.json", "run-2026-11-11-2331-feed.json"):
    try:
        prev = json.load(open(BASE + _prevf))
        for it in prev.get("results", []):
            seen_l.add(str(it.get("address", "")).lower())
    except Exception:
        pass
new_addrs = [it.get("address") for it in items
             if str(it.get("address", "")).lower() not in seen_l and it.get("address")
             and str(it.get("address", "")).lower() not in EXCLUDED]
out["feed_new"] = new_addrs

def shape_of(addr, meta):
    abi = meta.get("abi", [])
    fns = {}
    for e in abi:
        if e.get("type") == "function":
            fns.setdefault(e["name"], []).append(e)
    names = set(fns)
    has_mint = any(n.lower().startswith("mint") for n in names)
    lnames = {n.lower() for n in names}
    has_quote = bool(lnames & {"quote", "cost", "getquote", "mintcost", "price", "getprice", "mintprice"})
    free_views = sorted(names & set(FREE_VIEWS))
    agent_ref = bool(lnames & {"agentid", "agentregistry", "registry", "getagentid", "agentgate", "agentidregistry"})
    is_token = bool(names & {"name", "symbol", "decimals", "totalSupply", "balanceOf"}) and "totalSupply" in names
    mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
    s1 = has_mint and has_quote and bool(free_views) and agent_ref
    s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
    is_nft = bool(names & {"tokenURI", "ownerOf", "safeTransferFrom"}) or "uri" in names
    free_mint_fn = bool(names & {"freeMint", "mintFree", "claimFree", "mint"}) or any(n.lower().startswith("freemint") for n in names)
    early_shape = is_nft and (agent_ref or free_mint_fn)
    return {"address": addr, "S1": s1, "S2": s2, "early_shape": early_shape,
            "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
            "agent_ref": agent_ref, "is_token": is_token, "is_nft": is_nft,
            "fn_count": len(names)}

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        meta = json.loads(get(url, timeout=25))
        return shape_of(addr, meta)
    except Exception as ex:
        try:
            meta = json.loads(curl_get(url, timeout=25))
            r = shape_of(addr, meta)
            r["via"] = "curl"
            return r
        except Exception as ex2:
            return {"address": addr, "error": f"urllib {type(ex).__name__}: {str(ex)[:80]}; curl {type(ex2).__name__}: {str(ex2)[:80]}"}

shape_targets = list(new_addrs)
for a in RETRY_SHAPE:
    if a.lower() not in [x.lower() for x in shape_targets]:
        shape_targets.append(a)
shapes = []
if shape_targets:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        shapes = list(ex.map(fetch_abi, shape_targets))
out["feed_shape"] = {"s1_pass": [s["address"] for s in shapes if s.get("S1")],
                     "s2_pass": [s["address"] for s in shapes if s.get("S2")],
                     "early_shape": [s["address"] for s in shapes if s.get("early_shape")],
                     "shapes": shapes}
print("FEED", out["feed"], "NEW", new_addrs, "S1", out["feed_shape"]["s1_pass"],
      "S2", out["feed_shape"]["s2_pass"], "EARLY", out["feed_shape"]["early_shape"], flush=True)

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
        open(BASE + f"run-2026-11-12-0149-boltbook-{lang}.html", "w").write(html)
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
            for k in ("sale", "token", "address"):
                if v.get(k):
                    snap_addrs.add(str(v[k]).lower())
except Exception:
    snap = {}
    snap_addrs = set()
bb_new = []
for lang in ("en", "zh"):
    for a in out.get(f"boltbook_{lang}", {}).get("addrs", []):
        if a.lower() not in seen_l and a.lower() not in snap_addrs and a.lower() not in EXCLUDED and a not in bb_new:
            bb_new.append(a)
out["boltbook_new"] = bb_new
print("BOLTBOOK NEW:", bb_new, flush=True)

# --- record newly seen contracts in hot-leg-seen.json (own file only) ---
now_wib = datetime.now(WIB).strftime("%Y-%m-%dT%H:%M:%S+07:00")
added = 0
for s in shapes:
    a = s["address"]
    if s.get("error"):
        seen[a] = {"first_seen_wib": seen.get(a, {}).get("first_seen_wib", now_wib),
                   "note": f"run 0144 shape-check FAILED: {s.get('error')}",
                   "source": "sourcify-feed",
                   "status": "shape-check-failed"}
        added += 1
        continue
    if a.lower() in seen_l:
        continue
    seen[a] = {"first_seen_wib": seen.get(a, {}).get("first_seen_wib", now_wib),
               "note": f"run 0144: S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')}" + (f" via={s.get('via')}" if s.get("via") else ""),
               "source": "sourcify-feed",
               "status": "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else ("sale-shape-s1" if s.get("S1") else "sale-shape-s2")}
    added += 1
for a in bb_new:
    if a.lower() in seen_l:
        continue
    seen[a] = {"first_seen_wib": now_wib, "note": "Boltbook front-page mention, shape-check pending next run",
               "source": "boltbook-frontpage", "status": "seen-boltbook-unchecked"}
    added += 1
if added:
    with open(BASE + "hot-leg-seen.json", "w") as f:
        json.dump(seen, f, indent=1)
out["seen_added"] = added
print("SEEN ADDED/UPDATED:", added, flush=True)

# --- 3. Bridge comparison (read-only) ---
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = bridge.get("contracts", {})
    not_in_snap = [a for a in bcontracts if a.lower() not in snap_addrs]
    discarded = [a for a in bcontracts if bcontracts[a].get("same_owner_discarded")]
    out["bridge"] = {"total": len(bcontracts), "not_in_snapshot": not_in_snap,
                     "same_owner_discarded": discarded}
    print("BRIDGE total", len(bcontracts), "not_in_snapshot", len(not_in_snap), "discarded", len(discarded), flush=True)
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
    print("BRIDGE FAIL", e, flush=True)

# --- 4. eth_call helpers (curl batch) ---
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    o = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(o)

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

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
            outd = {}
            for item, key in zip(res, keys):
                outd[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return outd
        except Exception:
            continue
    return None

# --- 5. Leg 4: priority re-read ---
ITEMS = [
    ("Stampooor", "0x467696af8c2206B977B24081445104632dc1D459",
     ["totalMinted()", "freeMinted()", "FREE_SUPPLY()", "freeAvailable()", "mintOpen()", "balanceOf(address)", "freeClaimed(address)"]),
    ("Eco", "0xd31b168F7b6f3dB39BEd89433124595aaa91cfF3",
     ["totalMinted()", "freeMinted()", "FREE_WALLETS()", "freeWalletsLeft()", "freeWalletCount()", "MAX_SUPPLY()", "mintOpen()", "mintOpensAt()", "balanceOf(address)", "freeCountBy(address)", "mintsBy(address)", "holdsAgentId(address)"]),
    ("Moonfang", "0x79b0CE8b39c3Ed230487172751612b4F631398Bc",
     ["totalSupply()", "freeMinted()", "FREE_CAP()", "mintOpen()", "balanceOf(address)", "mintedBy(address)"]),
    ("AGCR", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc",
     ["totalSupply()", "totalMinted()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "freeAvailable()", "mintOpen()", "balanceOf(address)", "freeClaimed(address)"]),
    ("MECHA", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
     ["totalSupply()", "totalMinted()", "freeClaimed()", "FREE_SUPPLY()", "MAX_SUPPLY()", "freeAvailable()", "balanceOf(address)"]),
    ("WFPASS", "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C",
     ["mintOpen()", "freeMinted()", "totalMinted()", "totalSupply()", "balanceOf(address)"]),
    ("CRTSAINTS", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F",
     ["totalSupply()", "firstFreeUsed()", "paidMinted()", "mintOpen()", "balanceOf(address)", "firstFreeByWallet(address)"]),
    ("BUCKET", "0x2b0d3b384C341020aed1d49907b5708C423bA6DA",
     ["totalSupply()", "totalFreeCount()", "mintOpenedAt()", "balanceOf(address)", "freeUsed(address)"]),
    ("MOONDRILL", "0x87b354E2014D2e418927A1105dD219A2e7b063b0",
     ["totalSupply()", "firstFreeUsed()", "paidMinted()", "mintOpen()", "balanceOf(address)", "firstFreeByWallet(address)"]),
    ("0x2e50", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3",
     ["totalSupply()", "firstFreeUsed()", "paidMinted()", "mintOpen()", "balanceOf(address)", "firstFreeByWallet(address)"]),
    ("ORIGAMIX", "0x43CAb600E87B0F96e7a310109774797FC3DF5756",
     ["totalSupply()", "firstFreeUsed()", "paidMinted()", "mintOpen()", "balanceOf(address)", "firstFreeByWallet(address)"]),
    ("CAP7-Obrigado", "0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd",
     ["totalSupply()", "freeMinted()", "sharesMinted()", "soldOut()", "phase()", "balanceOf(address)", "freeClaimed(address)"]),
    ("BotFighters", "0x58a704d9e02FE11c0A61683AE7F606E4366F13eb",
     ["totalSupply()", "totalMinted()", "freeMinted()", "FREE_CAP()", "balanceOf(address)"]),
    ("RIGFORGE", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
     ["freeSharesLeft()", "openedAt()", "freeClaimed()"]),
    ("BINANCEAI", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
     ["launched()"]),
    ("SEVEN", "0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96",
     ["totalSupply()", "freeMinted()", "FREE_CAP()", "mintOpen()", "balanceOf(address)"]),
    ("Pickgrid", "0x7f541bcc33abed0e64455565da723e949c6f76f0",
     ["totalSupply()", "freeMinted()", "FREE_CAP()", "mintOpen()", "balanceOf(address)"]),
    ("SUDOSAINTS", "0x869d330bb48e7ab32da16745ef9a36a69d34f12f",
     ["totalSupply()", "freeMinted()", "FREE_SUPPLY()", "FREE_CAP()", "mintOpen()", "balanceOf(address)"]),
]
out["leg4_block"] = get_block()
print("BLOCK", out["leg4_block"], flush=True)
reread = {}
def read_one(item):
    name, addr, views = item
    res = raw_batch(addr, views)
    if res is not None and all(v is None for v in res.values()):
        return name, {"address": addr, "read_failure_all_null": True, **res}
    return name, {"address": addr, **(res or {"error": "all-endpoints-failed"})}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for name, data in ex.map(read_one, ITEMS):
        reread[name] = data
out["leg4_reread"] = reread
for name, data in reread.items():
    print("REREAD", name, {k: v for k, v in data.items() if k != "address"}, flush=True)

# --- 6. Stampooor site re-check ---
STAMP = "0x467696af8c2206B977B24081445104632dc1D459"
stamp = {}
for label, url in (("root", "https://stampooor.com/"), ("packs", "https://stampooor.com/packs/")):
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "20", "-o", "/dev/null", "-w", "%{http_code} %{size_download}",
                            url], capture_output=True, text=True, timeout=25)
        stamp[label] = r.stdout.strip() or "(empty)"
    except Exception as e:
        stamp[label] = f"ERR {type(e).__name__}: {str(e)[:80]}"
try:
    r = subprocess.run(["curl", "-sL", "--max-time", "20", "https://stampooor.com/packs/"],
                       capture_output=True, text=True, timeout=25)
    if r.stdout:
        stamp["packs_prints_contract"] = STAMP.lower() in r.stdout.lower()
        stamp["packs_bytes"] = len(r.stdout)
except Exception as e:
    stamp["packs_fetch_err"] = f"{type(e).__name__}: {str(e)[:80]}"
out["stampooor_site"] = stamp
print("STAMPOOOR SITE:", stamp, flush=True)

out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "hot-leg-run-2026-11-12-0149.json", "w"), indent=1)
print("DONE in", out["elapsed_s"], "s", flush=True)
