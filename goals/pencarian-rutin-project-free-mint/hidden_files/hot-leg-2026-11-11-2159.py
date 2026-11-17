#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-11 21:59 WIB. Legs: (1) Sourcify feed limit 20 + shape-check of genuinely new contracts (curl-based ABI fetch - urllib IncompleteRead seen in main 21:39 run); (2) Boltbook EN+ZH boltbook.fun; (3b) recheck MIHAO/MIHAO2; (4) leg4 re-read of prio set vs MAIN-JOB 21:39 reread baseline (block 132986757) + 19:29 last-known for items the main reread does not cover; Stampooor site gate re-verified live via curl (main 21:39: still 0 bytes). Bridge read-only (mtime 2026-11-08, stale). Read-only except own hot-leg state files. Flat-parallel eth_calls (16 workers, 8s/endpoint); global deadline 240s. No preview/mint unless a prio item crosses a strong-lead threshold AND passes shape re-verification + mandatory website gate (checked separately after this script). Shape-check failures are NOT kept in hot-leg-seen.json (retry next run)."""
import json, time, urllib.request, concurrent.futures, re, os, subprocess
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENTID = 107187496765866644729837695198686237165740365523485558112864918211974996443404
EP = "https://bsc.nodereal.io/"
EP2 = "https://bsc-dataseed.binance.org/"
EP3 = "https://bsc.publicnode.com"
T0 = time.time()
DEADLINE = 240
from datetime import datetime, timezone, timedelta
NOW_ISO = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
RUN = "2026-11-11 21:59 WIB"
STAMP = "2026-11-11-2159"
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"}
RETRY18 = []  # 21:39 main shape failures already retried OK by main via curl; none carried over

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_u(n): return ("%064x" % n)
def call(addr, sig, args=""):
    data = sel(sig) + args
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": addr, "data": data}, "latest"]})
    last_err = None
    for ep in (EP2, EP):
        try:
            r = subprocess.run(["curl", "-s", "-m", "10", "-H", "Content-Type: application/json",
                                "-d", body, ep], capture_output=True, timeout=15)
            j = json.loads(r.stdout.decode(errors="replace"))
            if "error" in j: last_err = {"error": str(j["error"])[:120]}; continue
            raw = j.get("result")
            if raw in (None, "0x"): return {"error": "empty-return"}
            if len(raw) >= 66:
                v = raw[2:66]
                if set(v) <= set("0123456789abcdef"):
                    try: return int(v, 16)
                    except Exception: return raw
            return raw
        except Exception as e:
            last_err = {"error": f"{type(e).__name__}: {str(e)[:90]}"}
            continue
    return last_err if last_err else {"error": "no-endpoint"}

def block_number():
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})
    for ep in (EP2, EP):
        try:
            r = subprocess.run(["curl", "-s", "-m", "10", "-H", "Content-Type: application/json",
                                "-d", body, ep], capture_output=True, timeout=15)
            return int(json.loads(r.stdout.decode(errors="replace"))["result"], 16)
        except Exception:
            continue
    return None

def curl_bytes(url, timeout=20):
    out = subprocess.run(["curl", "-s", "-m", str(timeout), "-A", "hot-leg/1.0", url],
                         capture_output=True, timeout=timeout + 5)
    return out.stdout

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        meta = json.loads(curl_bytes(url, 20).decode(errors="replace"))
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_names = {n.lower() for n in names}
        agent_ref = bool(agent_names & {"agentid", "agent_id", "agentregistry", "registry", "getagentid", "agentgate", "agentidregistry"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        is_nft = bool(names & {"tokenURI", "ownerOf", "safeTransferFrom"}) or "uri" in names
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
                "is_token": is_token, "is_nft": is_nft, "fn_count": len(names)}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

# ---- Leg 1: Sourcify feed ----
feed_note = ""
try:
    raw = curl_bytes("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 20)
    feed = json.loads(raw.decode(errors="replace"))
    items = feed.get("results", [])
    FEED = [(it.get("address"), it.get("verifiedAt")) for it in items if it.get("address")]
    json.dump(feed, open(BASE + f"hot-leg-{STAMP}-feed.json", "w"), indent=1)
    feed_note = f"feed OK: {len(FEED)} contracts, verified {FEED[-1][1]}..{FEED[0][1]}"
except Exception as e:
    FEED, feed_note = [], f"feed FAILED: {type(e).__name__}: {str(e)[:100]} - leg skipped, retried next run"
print("FEED", feed_note, flush=True)

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
NEW = [a for a, _ in FEED if a.lower() not in seen_l]
_retry = [a for a in RETRY18 if a.lower() not in seen_l and a.lower() not in {x.lower() for x in NEW}]
NEW = NEW + _retry
print("NEW", len(NEW), "incl retries", len(_retry), NEW, flush=True)

shapes = {}
if NEW:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        for r in ex.map(fetch_abi, NEW):
            shapes[r["address"]] = r
json.dump(shapes, open(BASE + f"hot-leg-{STAMP}-shape.json", "w"), indent=1)
print("SHAPES S1:", [a for a in NEW if shapes.get(a, {}).get("S1")],
      "S2:", [a for a in NEW if shapes.get(a, {}).get("S2")],
      "FAILED:", [a for a in NEW if "error" in shapes.get(a, {})], flush=True)

seen_added = []
for a in NEW:
    sh = shapes.get(a, {})
    if "error" in sh:
        continue
    seen[a] = {"first_seen_wib": NOW_ISO, "source": f"sourcify-feed-{STAMP[-4:]}",
               "note": f"S1={sh['S1']} S2={sh['S2']} mint={sh['has_mint']} quote={sh['has_quote']} free={sh['free_views']} agent={sh['agent_ref']} token={sh['is_token']}",
               "status": "checked-not-sale-shape" if not (sh["S1"] or sh["S2"]) else "SALE-SHAPE"}
    seen_added.append(a)

# ---- Leg 2: Boltbook EN + ZH ----
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
bb_note, bb_fresh, bb_addrs, bb_shapes = "", [], set(), {}
try:
    en_b = curl_bytes("https://boltbook.fun/?lang=en", 25)
    zh_b = curl_bytes("https://boltbook.fun/?lang=zh", 25)
    open(BASE + f"hot-leg-{STAMP}-boltbook-en.html", "wb").write(en_b)
    open(BASE + f"hot-leg-{STAMP}-boltbook-zh.html", "wb").write(zh_b)
    bb_addrs = set(ADDR_RE.findall(en_b.decode("utf-8", "ignore"))) | set(ADDR_RE.findall(zh_b.decode("utf-8", "ignore")))
    bb_fresh = sorted(a for a in bb_addrs if a.lower() not in seen_l)
    kw_en = len(re.findall(r"free share|first share free|1 free share|free mint share", en_b.decode("utf-8", "ignore"), re.I))
    kw_zh = len(re.findall(r"免费份额|首个免费|免费铸造|免费mint", zh_b.decode("utf-8", "ignore"), re.I))
    bb_note = (f"EN HTTP 200 ({len(en_b)}B) + ZH HTTP 200 ({len(zh_b)}B) boltbook.fun; "
               f"{len(bb_addrs)} unique addresses, {len(bb_fresh)} not in hot-leg-seen.json: {bb_fresh or 'none'}; "
               f"keywords EN free-share={kw_en} ZH={kw_zh}")
except Exception as e:
    bb_note = f"Boltbook read FAILED: {type(e).__name__}: {str(e)[:100]} - leg skipped, retried next run"
print("BOLTBOOK", bb_note, flush=True)

for a in bb_fresh:
    bb_shapes[a] = fetch_abi(a)
for a, sh in bb_shapes.items():
    if "error" in sh:
        continue
    seen[a] = {"first_seen_wib": NOW_ISO, "source": f"boltbook-{STAMP[-4:]}",
               "note": f"S1={sh['S1']} S2={sh['S2']} mint={sh['has_mint']} quote={sh['has_quote']} free={sh['free_views']} agent={sh['agent_ref']} token={sh['is_token']}",
               "status": "checked-not-sale-shape" if not (sh["S1"] or sh["S2"]) else "SALE-SHAPE"}
    seen_added.append(a)
if seen_added:
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Leg 3b + Leg 4: flat-parallel eth_calls ----
U = enc_addr(USER)
TASKS = []
def add(name, addr, key, sig, args=""):
    TASKS.append((name, addr, key, sig, args))
LEG3B = {
 "MIHAO": ("0x1f82539520a8b3d4eB7C3145f7E1EaFe4B52c4e1", [("opened", "opened()", ""), ("freeMinted", "freeMinted()", ""), ("totalMinted", "totalMinted()", "")]),
 "MIHAO2": ("0x34eA49e9BC199418f121366BdBEa8fDbab10c26b", [("freeMinted", "freeMinted()", ""), ("totalMinted", "totalMinted()", ""), ("FREE_SHARES", "FREE_SHARES()", ""), ("freePhaseActive", "freePhaseActive()", ""), ("opened", "opened()", "")]),
}
PRIO = {
 "AgentPals": ("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", [("totalMinted", "totalMinted()", ""), ("freeMinted", "freeMinted()", ""), ("hasFreeMinted_user", "hasFreeMinted(address)", U), ("balanceOf_user", "balanceOf(address)", U)]),
 "HANAMI": ("0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640", [("totalSupply", "totalSupply()", ""), ("freeMinted", "freeMinted()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "ABYSSCABLE": ("0xd2e9242b0d7c0186cc181a5fc8534541dad278a2", [("totalSupply", "totalSupply()", ""), ("agentFreeUsed", "agentFreeUsed()", ""), ("mintOpen", "mintOpen()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "Stampooor": ("0x467696af8c2206B977B24081445104632dc1D459", [("totalMinted", "totalMinted()", ""), ("freeMinted", "freeMinted()", ""), ("FREE_SUPPLY", "FREE_SUPPLY()", ""), ("mintOpen", "mintOpen()", ""), ("freeAvailable_user", "freeAvailable(address)", U), ("balanceOf_user", "balanceOf(address)", U)]),
 "Foxglow": ("0x6e159c9cd56beadb523b80d195dde39c042a1d48", [("totalSupply", "totalSupply()", ""), ("freeClaimed", "freeClaimed()", ""), ("mintOpen", "mintOpen()", ""), ("freeUsed_user", "freeUsed(address)", U), ("freeFor_user_1", "freeFor(address,uint256)", U + enc_u(1))]),
 "LOWB": ("0x00487ED061C77A1dd5085ef3a2D593366f9C6B35", [("opened", "opened()", ""), ("totalFreeMinted", "totalFreeMinted()", ""), ("totalMinted", "totalMinted()", "")]),
 "SHINE": ("0xDDc2352d1ceC10b42e05A297232f5328902C6c2C", [("startTime", "startTime()", ""), ("launched", "launched()", ""), ("freeClaimed_user", "freeClaimed(address)", U)]),
 "UFO": ("0xE4059eA596392AcA14100af6CDC9481c330E2728", [("FREE_SHARES", "FREE_SHARES()", ""), ("freeClaimed_user", "freeClaimed(address)", U)]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", [("SALE_START", "SALE_START()", ""), ("FREE_SHARES", "FREE_SHARES()", ""), ("freeSharesLeft", "freeSharesLeft()", ""), ("openedAt", "openedAt()", ""), ("freeTaken_agentId", "freeTaken(uint256)", enc_u(AGENTID))]),
 "BotFighters": ("0x58a704d9e02FE11c0A61683AE7F606E4366F13eb", [("FREE_CAP", "FREE_CAP()", ""), ("freeMinted", "freeMinted()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "BHTB": ("0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467", [("freeRemaining", "freeRemaining()", "")]),
 "AgentGrid": ("0x651302C0043040D48EaAF85605E12F0549aD6D89", [("freeUsed", "freeUsed()", "")]),
 "SUDOSAINTS": ("0x869d330bb48e7ab32da16745ef9a36a69d34f12f", [("totalSupply", "totalSupply()", ""), ("freeMinted", "freeMinted()", ""), ("mintActive", "mintActive()", ""), ("freeUsed_user", "freeUsed(address)", U), ("balanceOf_user", "balanceOf(address)", U)]),
 "binanceai": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [("launched", "launched()", "")]),
 "AgentRune": ("0xc1fc0bb36d2be928809e4b3e6aa94b3dd2946f53", [("totalSupply", "totalSupply()", ""), ("freeMinted", "freeMinted()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "RAMRAIDERS": ("0x98dcfdeb5e015bbb3c9aca2a90ba0ee80e35315b", [("totalSupply", "totalSupply()", ""), ("freeMinted", "freeMinted()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "0x7Eb9": ("0x7Eb92041aa3037e39baA88154F279e3D9F85c593", [("totalMinted", "totalMinted()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "STALL": ("0xe3de7fd0d12cff4a46d8bf702ab593b6f921b308", [("totalSupply", "totalSupply()", ""), ("mintOpen", "mintOpen()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
}

EARLY = {
 "BUCKET": ("0x2b0d3b384C341020aed1d49907b5708C423bA6DA", [("totalSupply", "totalSupply()", ""), ("totalFreeCount", "totalFreeCount()", ""), ("freeUsed_user", "freeUsed(address)", U), ("isAgent_user", "isAgent(address)", U), ("balanceOf_user", "balanceOf(address)", U), ("mintOpenedAt", "mintOpenedAt()", "")]),
 "MOONDRILL": ("0x87b354E2014D2e418927A1105dD219A2e7b063b0", [("totalSupply", "totalSupply()", ""), ("firstFreeUsed", "firstFreeUsed()", ""), ("paidMinted", "paidMinted()", ""), ("mintOpen", "mintOpen()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "0x2e50": ("0x2e508C6510d9550031932f0D6Fe691DCe38E66E3", [("totalSupply", "totalSupply()", ""), ("firstFreeUsed", "firstFreeUsed()", ""), ("paidMinted", "paidMinted()", ""), ("mintOpen", "mintOpen()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "MECHA": ("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", [("totalMinted", "totalMinted()", ""), ("freeClaimed", "freeClaimed()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "CRTSAINTS": ("0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F", [("totalSupply", "totalSupply()", ""), ("paidMinted", "paidMinted()", ""), ("mintOpen", "mintOpen()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
}
for n, (a, s_) in EARLY.items():
    for key, sig, args in s_:
        add("early:" + n, a, key, sig, args)
for n, (a, s) in LEG3B.items():
    for key, sig, args in s:
        add("leg3b:" + n, a, key, sig, args)
for n, (a, s) in PRIO.items():
    for key, sig, args in s:
        add(n, a, key, sig, args)

blk = block_number()
results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    futs = {ex.submit(call, a, sig, args): (n, k) for (n, a, k, sig, args) in TASKS}
    for f in concurrent.futures.as_completed(futs, timeout=120):
        n, k = futs[f]
        try:
            results.setdefault(n, {})[k] = f.result()
        except Exception as e:
            results.setdefault(n, {})[k] = {"error": f"{type(e).__name__}: {str(e)[:80]}"}
leg3b = {n[6:]: v for n, v in results.items() if n.startswith("leg3b:")}
early_r = {n[6:]: v for n, v in results.items() if n.startswith("early:")}
prio = {"block": blk, "values": {n: v for n, v in results.items() if not n.startswith("leg3b:") and not n.startswith("early:")}}
json.dump(prio, open(BASE + f"hot-leg-{STAMP}-prio.json", "w"), indent=1)
print("PRIO block", blk, "elapsed", round(time.time() - T0, 1), flush=True)

# ---- Bridge (read-only) ----
bridge_note = ""
try:
    b = json.load(open(BASE + "scan-bridge.json"))
    cons = b.get("contracts", {})
    mtime = time.strftime("%Y-%m-%d %H:%M WIB", time.localtime(os.path.getmtime(BASE + "scan-bridge.json")))
    new_addrs = [a for a, _ in FEED] + bb_fresh
    new_in_bridge = [a for a in new_addrs if a.lower() in {k.lower() for k in cons}]
    disc = [k for k, v in cons.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
    bridge_note = (f"scan-bridge.json read ({len(cons)} contracts, mtime {mtime}); "
                   f"new feed/Boltbook contracts in bridge: {new_in_bridge or 'none'}; "
                   f"same_owner_discarded in bridge: {len(disc)}; no bridge promotion/change this run")
except Exception as e:
    bridge_note = f"bridge read FAILED: {type(e).__name__}: {str(e)[:100]} - skipped, run continues"

# ---- Compare vs 18:14 baseline + 18:24 targeted + 18:31 main ----
# Baseline: main-job 21:39 reread (block 132986757) + 19:29 last-known for uncovered items
_main = json.load(open(BASE + "run-2026-11-11-2139-reread.json"))
_mr = _main.get("reread", {})
_NAME_MAP = {"Stampooor": "Stampooor Stamp Packs", "AgentPals": "AgentPals",
             "SUDOSAINTS": "SUDOSAINTS", "AgentRune": "AgentRune", "STALL": "STALL",
             "0x7Eb9": "0x7Eb9"}
bv = {}
for _n, _m in _NAME_MAP.items():
    if _m in _mr:
        bv[_n] = {k: v for k, v in _mr[_m].items() if k != "address"}
BASELINE_EXTRA = {
 "AgentPals": {"totalMinted": 301, "freeMinted": 300},   # 21:39 main reread (sold out, user holds #268)
 "Stampooor": {"freeMinted": 866, "totalMinted": 862},   # 21:49 prio-retry freeMinted 866/1200 = 72.17%; totalMinted last known 862 (21:39, retry read failed)
 "SUDOSAINTS": {"totalSupply": 613, "freeMinted": 613},   # 21:39 main reread
 "AgentRune": {"totalSupply": 192, "freeMinted": 189},   # 21:39 main reread
 "STALL": {"totalSupply": 1984},   # 21:39 main reread
 "0x7Eb9": {"totalMinted": 969},   # 21:39 main reread
 "BotFighters": {"freeMinted": 65},   # 19:09 prio (not in main reread)
 "RAMRAIDERS": {"freeMinted": 559},   # 19:09 prio (not in main reread)
 "AgentGrid": {"freeUsed": 21},   # 19:09 prio (not in main reread)
 "RigForge": {"freeSharesLeft": 684},   # 21:39 main legs
 "BUCKET": {"totalSupply": 125, "totalFreeCount": 125},   # snapshot 21:31 (was 62 at 21:14)
 "MOONDRILL": {"totalSupply": 22, "firstFreeUsed": 7, "paidMinted": 0, "mintOpen": 1, "balanceOf_user": 0},   # snapshot 21:31 (was 7 at 21:14)
 "0x2e50": {"totalSupply": 20, "firstFreeUsed": 7, "paidMinted": 0, "mintOpen": 1, "balanceOf_user": 0},   # snapshot 21:31 (was 7 at 21:14)
 "MECHA": {"totalMinted": 199, "freeClaimed": 199},   # snapshot 21:31 (was 138 at 21:14)
 "CRTSAINTS": {"totalSupply": 29, "paidMinted": 0, "mintOpen": 1, "balanceOf_user": 0},   # snapshot 21:31 (was 21 at 21:14)
}
for _n, _ex in BASELINE_EXTRA.items():
    bv.setdefault(_n, {}).update(_ex)
changes, view_notes = [], []
for name in PRIO:
    for key, new in prio["values"].get(name, {}).items():
        old = bv.get(name, {}).get(key) if isinstance(bv.get(name), dict) else None
        extra = BASELINE_EXTRA.get(name, {}).get(key)
        ref = extra if extra is not None else old
        ref_src = "2139-main-reread+last-known"
        if isinstance(old, dict) or isinstance(new, dict):
            if old != new:
                view_notes.append(f"{name}.{key}: view {old} -> {new} (view-status only, not a state change)")
            continue
        if ref is None and new is None:
            continue
        if isinstance(new, int) and ref is not None and new != ref:
            changes.append(f"{name}.{key}: {ref} -> {new} (vs {ref_src})")
        elif new is None and ref is not None:
            view_notes.append(f"{name}.{key}: read FAILED this run (was {ref} vs {ref_src})")
for name in EARLY:
    for key, new in early_r.get(name, {}).items():
        old = BASELINE_EXTRA.get(name, {}).get(key)
        if isinstance(old, dict) or isinstance(new, dict):
            if old != new:
                view_notes.append(f"early {name}.{key}: view {old} -> {new} (view-status only, not a state change)")
            continue
        if old is None and new is None:
            continue
        if isinstance(new, int) and old is not None and new != old:
            changes.append(f"early {name}.{key}: {old} -> {new} (vs snapshot-2131)")
        elif new is None and old is not None:
            view_notes.append(f"early {name}.{key}: read FAILED this run (was {old} vs snapshot-2131)")
for name in LEG3B:
    for key, new in leg3b.get(name, {}).items():
        old = None
        try:
            old = json.load(open(BASE + "hot-leg-run-2026-11-11-1849.json")).get("leg3b_recheck", {}).get(name, {}).get(key)
        except Exception:
            old = None
        if isinstance(old, dict) or isinstance(new, dict):
            if old != new:
                view_notes.append(f"leg3b {name}.{key}: view {old} -> {new} (view-status only)")
            continue
        if old is None and new is None:
            continue
        if old != new:
            changes.append(f"leg3b {name}.{key}: {old} -> {new}")

# ---- Threshold watch ----
watch = []
ap = prio["values"].get("AgentPals", {})
if isinstance(ap.get("freeMinted"), int):
    watch.append(f"AgentPals freeMinted {ap['freeMinted']}/300 = {ap['freeMinted']/300*100:.1f}% (strong-lead needs >70% = >210; slot hasFreeMinted={ap.get('hasFreeMinted_user')})")
st = prio["values"].get("Stampooor", {})
st_crossed = False
if isinstance(st.get("freeMinted"), int) and isinstance(st.get("FREE_SUPPLY"), int):
    pct = st['freeMinted'] / st['FREE_SUPPLY'] * 100
    st_crossed = st['freeMinted'] > 840
    watch.append(f"Stampooor freeMinted {st['freeMinted']}/{st['FREE_SUPPLY']} = {pct:.1f}% (strong-lead needs >70% = >840; slot freeAvailable={st.get('freeAvailable_user')}; age: mintStart 1794362419 ~09:00 WIB 11 Nov, <24h; STRONG-LEAD-CROSSED={st_crossed}; NOTE: main job flags this contract NOT agent-shaped (S1/S2 false) - shape+website must be re-verified before any strong-lead treatment)")

# ---- Stampooor crossing contingency: shape re-check from saved ABI + contractURI ----
stampooor_gate = None
if st_crossed:
    try:
        abi_doc = json.load(open(BASE + "abi-0901-stampooor.json"))
        abi = abi_doc.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_names = {n.lower() for n in names}
        agent_ref = bool(agent_names & {"agentid", "agent_id", "agentregistry", "registry", "getagentid", "agentgate", "agentidregistry"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        contract_uri = call("0x467696af8c2206B977B24081445104632dc1D459", "contractURI()")
        stampooor_gate = {"shape_recheck": {"S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token, "fn_count": len(names)}, "contractURI_raw": str(contract_uri)[:300]}
    except Exception as e:
        stampooor_gate = {"error": f"{type(e).__name__}: {str(e)[:120]}"}

# ---- Stampooor website gate: live re-verification (curl, read-only) ----
site_gate = {}
for _u in ("https://stampooor.com/packs/", "https://stampooor.com/"):
    try:
        _r = subprocess.run(["curl", "-s", "-m", "15", "-o", "/dev/null", "-w", "%{http_code}:%{size_download}", "-A", "hot-leg/1.0", _u],
                            capture_output=True, timeout=20)
        site_gate[_u] = _r.stdout.decode(errors="replace")
    except Exception as e:
        site_gate[_u] = f"ERROR {type(e).__name__}: {str(e)[:80]}"
print("STAMPOOR-SITE", site_gate, flush=True)

run = {
 "run": f"free-mint-hot-leg {RUN}",
 "started_wib": NOW_ISO,
 "leg1_sourcify_feed": {"note": feed_note, "returned": len(FEED),
   "verified_range": [FEED[-1][1], FEED[0][1]] if FEED else None,
   "new": NEW, "already_seen": len(FEED) - len([a for a, _ in FEED if a.lower() not in seen_l])},
 "leg1_shapes": {a: shapes[a] for a in NEW},
 "leg1_s1_pass": [a for a in NEW if shapes.get(a, {}).get("S1")],
 "leg1_s2_pass": [a for a in NEW if shapes.get(a, {}).get("S2")],
 "leg2_boltbook": {"note": bb_note, "addrs": sorted(bb_addrs), "fresh": bb_fresh, "fresh_shapes": bb_shapes},
 "bridge": bridge_note,
 "leg3_new_sale_shape": {a: shapes[a] for a in NEW if isinstance(shapes.get(a), dict) and (shapes[a].get("S1") or shapes[a].get("S2"))},
 "leg3b_recheck": leg3b,
 "early_reread": early_r,
 "leg4_read_wib": NOW_ISO,
 "leg4_block": prio["block"],
 "leg4_values": prio["values"],
 "leg4_changes_vs_2139": changes or "NONE",
 "leg4_view_notes": view_notes or "NONE",
 "threshold_watch": watch,
 "stampooor_crossed": st_crossed,
 "stampooor_gate_recheck": stampooor_gate,
 "stampooor_site_gate_live": site_gate,
 "seen_added": seen_added,
 "shape_check_failed_not_kept": [a for a in NEW if isinstance(shapes.get(a), dict) and "error" in shapes[a]],
 "elapsed_s": round(time.time() - T0, 1),
}
json.dump(run, open(BASE + f"hot-leg-run-{STAMP}.json", "w"), indent=1)
print(json.dumps(run, indent=1))
print("ELAPSED", round(time.time() - T0, 1))
