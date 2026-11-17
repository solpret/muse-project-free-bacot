#!/usr/bin/env python3
"""Hot-leg run 2026-11-17 01:44 WIB (scheduled 01:44:38).
Legs: (1) Sourcify feed poll + ABI shape-check new S1/S2; (2) Boltbook EN+ZH;
(3) on-chain verify only if new sale-shape; (4) focus re-read of the 23-entry
active set (same as 0139 run) vs 0139 reads for changes, plus PEPE-mint re-read
(audit-blocked track-C lead); bridge read-only. Retry pool: none.
Read-only except hot-leg-seen.json (own file) + this run JSON.
No preview/mint/claim. No snapshot writes.
NOTE: prev run 0139 (5 min ago)."""
import json, re, subprocess, time, os
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
NOW = "2026-11-17T01:44+07:00"
RUN_TAG = "free-mint-hot-leg 2026-11-17 01:44 WIB"
PREV_RUN = "hot-leg-run-2026-11-17-0144.json"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124",
            "0x8b47354E7b76B1970a0D06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
EPS = ["https://bsc-dataseed3.bnbchain.org/", "https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-rpc.publicnode.com/"]
t0 = time.time()

def log(*a): print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)

def get(url, timeout=20):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout),
                        "-A", "hot-leg/1.0", url],
                       capture_output=True, text=True, timeout=timeout + 10)
    if r.returncode != 0:
        raise RuntimeError(f"curl rc={r.returncode}: {r.stderr[:120]}")
    return r.stdout

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower(): v for k, v in seen.items()}
seen_n0 = len(seen)

# (1) Sourcify feed
feed_error = None
try:
    feed = json.loads(get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"))
    results = feed.get("results", [])
except Exception as ex:
    feed_error = f"{type(ex).__name__}: {str(ex)[:120]}"
    results = []
    log("feed SKIP (stalled):", feed_error)
feed_addrs = [r["address"] for r in results]
vat = {r["address"].lower(): r.get("verifiedAt") for r in results}
feed_new = [a for a in feed_addrs if a.lower() not in seen_l and a.lower() != REG.lower()
            and a.lower() not in {e.lower() for e in EXCLUDED}]
log("feed total", len(results), "new", len(feed_new), feed_new,
    "top", feed_addrs[0] if feed_addrs else None)

# (2) Boltbook en + zh
def boltbook(url):
    html = get(url)
    addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    return html, addrs
bb_errors = {}
try:
    en_html, en_addrs = boltbook("https://boltbook.fun/")
except Exception as ex:
    bb_errors["en"] = f"{type(ex).__name__}: {str(ex)[:120]}"
    log("boltbook EN SKIP (stalled):", bb_errors["en"])
    en_html, en_addrs = "", []
try:
    zh_html, zh_addrs = boltbook("https://boltbook.fun/?lang=zh")
except Exception as ex:
    bb_errors["zh"] = f"{type(ex).__name__}: {str(ex)[:120]}"
    log("boltbook ZH SKIP (stalled):", bb_errors["zh"])
    zh_html, zh_addrs = "", []
bb_addrs = sorted(set(en_addrs) | set(zh_addrs))
bb_new = [a for a in bb_addrs if a.lower() not in seen_l
          and a.lower() not in {e.lower() for e in EXCLUDED}]
kw_en = len(re.findall(r"free share|first share free|1 free share|free mint share",
                       en_html, re.I))
kw_zh_en = len(re.findall(r"免费份额|首个免费|免费铸造|免费mint", en_html))
kw_en_zh = len(re.findall(r"free share|first share free|1 free share|free mint share",
                          zh_html, re.I))
kw_zh = len(re.findall(r"免费份额|首个免费|免费铸造|免费mint", zh_html))
log("boltbook en", len(en_html), "addrs", len(en_addrs), "new", len(bb_new), bb_new,
    "| zh", len(zh_html), "addrs", len(zh_addrs))

# (3) shape-check new contracts
def shape(addr, v=None):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        meta = json.loads(get(url, timeout=15))
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId",
                                  "agentGate", "AgentGate", "AGENT_ID_REGISTRY",
                                  "agentIdRegistry", "AGENT_ID"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = (is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"})
              and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref)
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
                "is_token": is_token, "n_fns": len(names), "status": "checked",
                "verifiedAt": v}
    except Exception as ex:
        return {"address": addr, "status": "shape-check-failed",
                "error": f"{type(ex).__name__}: {str(ex)[:120]}", "verifiedAt": v}

targets = [(a, vat.get(a.lower())) for a in feed_new]
targets += [(a, None) for a in bb_new if a.lower() not in {x.lower() for x, _ in targets}]
with ThreadPoolExecutor(max_workers=8) as ex:
    shape_out = list(ex.map(lambda t: shape(t[0], t[1]), targets))
for r in shape_out:
    log("shape", r["address"][:12], "S1", r.get("S1"), "S2", r.get("S2"),
        "mint", r.get("has_mint"), "quote", r.get("has_quote"),
        "free", r.get("free_views"), "agent", r.get("agent_ref"), r.get("status"),
        r.get("error", ""))
hits = [s["address"] for s in shape_out if s.get("S1") or s.get("S2")]
log("shape hits:", hits)

# (4) leg-4 focus re-read — same 23-entry active set as 0139 run
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
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        elif isinstance(a, str) and a.startswith("0x"):
            d += enc_u(int(a, 16))
        else:
            d += enc_u(int(a))
    return d
def post_rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)

U = [USER]
ITEMS = {
 "JADE": ("0x1b8894391a3dcfe7e248c321103265ab52e273e0", [
    ("cost_user_1", "cost(address,uint256)", [USER, 1]),
    ("freeClaimed", "freeClaimed()", []), ("totalSupply", "totalSupply()", []),
    ("mintOpen", "mintOpen()", []), ("mintedBy_user", "mintedBy(address)", U),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "AgentBubble": ("0x0d72970046c056db90888351b739246f468bff0b", [
    ("freeMinted", "freeMinted()", []), ("totalSupply", "totalSupply()", []),
    ("totalMinted", "totalMinted()", []), ("MAX_SUPPLY", "MAX_SUPPLY()", []),
    ("mintOpen", "mintOpen()", []), ("balanceOf_user", "balanceOf(address)", U)]),
 "Matrix": ("0x1F669b714337F3C2585072c53fdDD89581F928fF", [
    ("freeMinted", "freeMinted()", []), ("freeRemaining", "freeRemaining()", []),
    ("totalSupply", "totalSupply()", []), ("mintOpen", "mintOpen()", [])]),
 "AGCLUB": ("0x67270bb351515abf3089ca5420456897363f5e75", [
    ("totalMinted", "totalMinted()", []), ("freeMinted", "freeMinted()", []),
    ("FREE_CAP", "FREE_CAP()", []), ("mintOpen", "mintOpen()", []),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "BNBG": ("0x1595013dfc8c6b3f4b172254bf09bdaf1421002b", [
    ("totalMinted", "totalMinted()", [])]),
 "SPARKS": ("0xd52fd117c4b47d03e4e16e778871f09faa5a024b", [
    ("totalSupply", "totalSupply()", [])]),
 "Ledgera": ("0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d", [
    ("freeClaimed", "freeClaimed()", []), ("totalSupply", "totalSupply()", []),
    ("mintOpen", "mintOpen()", []), ("freeUsed_user", "freeUsed(address)", U),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "BoldLeonidas": ("0x84bcb8c16566e81ce902530c9da1e3de291f9941", [
    ("totalSupply", "totalSupply()", []), ("mintOpen", "mintOpen()", []),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "RaceAgents": ("0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f", [
    ("totalSupply", "totalSupply()", []), ("freeMinted", "freeMinted()", []),
    ("mintOpen", "mintOpen()", [])]),
 "CPASS": ("0x5877d2bb9f226cc3e438f4d656caeb27deafc576", [
    ("totalMinted", "totalMinted()", []), ("mintOpen", "mintOpen()", []),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "REOPIR": ("0x12f65bc14037ccdf3f97afc0e67a0e4aca3cf5b9", [
    ("freeClaimed", "freeClaimed()", []), ("totalSupply", "totalSupply()", []),
    ("mintOpen", "mintOpen()", [])]),
 "RAVE": ("0x7c40B78992d86EDfFB5553C74dB5EF427100bb95", [
    ("totalMinted", "totalMinted()", []), ("freeMinted", "freeMinted()", []),
    ("mintOpen", "mintOpen()", [])]),
 "MORFO": ("0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186", [
    ("totalMinted", "totalMinted()", []), ("mintOpen", "mintOpen()", [])]),
 "AgentNOVA": ("0x43462d7f269fde4914b03e1e07067a61b62b9540", [
    ("totalSupply", "totalSupply()", [])]),
 "Zephyra": ("0x00a9791be6317d6e3a6c60f75a706c870d882048", [
    ("totalMinted", "totalMinted()", [])]),
 "Pengu": ("0x5AEc03C90656743475810926B2B2bd443D5c26a4", [
    ("totalMinted", "totalMinted()", []), ("freeMinted", "freeMinted()", [])]),
 "Kryntar": ("0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe", [
    ("totalMinted", "totalMinted()", []), ("standardRemaining", "standardRemaining()", []),
    ("legendaryRemaining", "legendaryRemaining()", []), ("mintOpen", "mintOpen()", [])]),
 "ONI": ("0x99d01eD93829DBB0EEc11F3a733388c789dA6caD", [
    ("totalMinted", "totalMinted()", []), ("totalSupply", "totalSupply()", [])]),
 "HAPPE": ("0x72c14121681F1133545947B0735563835CC07B67", [
    ("totalMinted", "totalMinted()", []), ("freeMinted", "freeMinted()", [])]),
 "PIXELFROGS": ("0x454054e55FA2D7Ba37df7F3ceA269696f19037dF", [
    ("totalSupply", "totalSupply()", []), ("freeMinted", "freeMinted()", []),
    ("freeLeft", "freeLeft()", []), ("mintOpen", "mintOpen()", []),
    ("freeClaimed_user", "freeClaimed(address)", U)]),
 "Flare-bd6f": ("0xbd6ff7ed8fe96b79cb3cbf9dc32656ff7a98a599", [
    ("totalSupply", "totalSupply()", [])]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", [
    ("freeSharesLeft", "freeSharesLeft()", []), ("openedAt", "openedAt()", []),
    ("freeClaimed", "freeClaimed()", []),
    ("freeBooked_user", "freeBooked(address)", U)]),
 "binanceai-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched", "launched()", []), ("failed", "failed()", []),
    ("isRefundPhase", "isRefundPhase()", []), ("totalShares", "totalShares()", []),
    ("tokenClaimed_user", "tokenClaimed(address)", U)]),
}
PEPE = {"PEPE-mint": ("0x7E920e9e4Ad8E4497aEa7EB9bAF60Cd6c6C8D980", [
    ("FREE_SHARES", "FREE_SHARES()", []), ("soldShares", "soldShares()", []),
    ("freeMinted", "freeMinted()", []), ("opened", "opened()", []),
    ("openedTime", "openedTime()", []), ("mintStartTime", "mintStartTime()", []),
    ("mintableNow", "mintableNow()", []), ("costOf_1", "costOf(uint256)", [1]),
    ("bnbQuote_1", "bnbQuote(uint256)", [1]), ("hasMinted_user", "hasMinted(address)", U)])}

def chunked(items, n=4):
    items = list(items.items())
    for i in range(0, len(items), n):
        yield items[i:i+n]

def read_chunk(chunk):
    calls, meta = [], []
    for name, (addr, views) in chunk:
        for key, sig, args in views:
            calls.append({"jsonrpc": "2.0", "id": len(calls) + 1, "method": "eth_call",
                          "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
            meta.append((name, key))
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=60)
            if not isinstance(res, list) or len(res) != len(calls):
                log("  chunk ep", ep, "bad shape"); continue
            out = {}
            for it, (name, key) in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    out.setdefault(name, {})[key] = None
                else:
                    r = it["result"]
                    out.setdefault(name, {})[key] = to_int(r[:66]) if len(r) >= 66 else r
            return out, ep
        except Exception as e:
            log("  chunk ep", ep, "exc", str(e)[:100]); continue
    return None, None

def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber",
                              "params": []}, timeout=60)
            if isinstance(r, dict) and r.get("result"):
                return int(r["result"], 16)
        except Exception:
            continue
    return None

reads, ok, chunk_errors = {}, 0, []
for ci, ch in enumerate(chunked(ITEMS, 4)):
    r, ep = read_chunk(ch)
    names = [n for n, _ in ch]
    if r is None:
        log(f"chunk {ci+1} FAIL {names}")
        chunk_errors.append(names)
        for n in names:
            reads[n] = {"address": ITEMS[n][0], "views": None}
        continue
    ok += sum(1 for n in names if r.get(n) is not None)
    for n in names:
        reads[n] = {"address": ITEMS[n][0], "views": r.get(n)}
    log(f"chunk {ci+1} OK via {ep} {names}")
pepe_read, pepe_ep = read_chunk(list(PEPE.items()))
pepe_out = pepe_read.get("PEPE-mint") if pepe_read else None
log("pepe re-read via", pepe_ep, pepe_out)
blk = block_number()
log("reread ok", ok, "/", len(ITEMS), "block", blk)

# change detection vs 0139 run
changes = []
try:
    prev = json.load(open(BASE + PREV_RUN))
    prev_reads = prev.get("leg4_reread", {}).get("reads", {})
    for name, cur in reads.items():
        pv = (prev_reads.get(name) or {}).get("views")
        cv = cur.get("views")
        if pv is None or cv is None:
            if pv != cv:
                changes.append({"item": name, "type": "read-availability-change",
                                "prev": pv, "now": cv})
            continue
        diff = {k: {"prev": pv.get(k), "now": cv.get(k)}
                for k in set(pv) | set(cv) if pv.get(k) != cv.get(k)}
        if diff:
            changes.append({"item": name, "type": "value-change", "diff": diff})
    pv_pepe = prev.get("pepe_reread")
    if pv_pepe != pepe_out:
        pdiff = {k: {"prev": pv_pepe.get(k) if isinstance(pv_pepe, dict) else None,
                     "now": (pepe_out or {}).get(k)}
                 for k in set(list(pv_pepe.keys()) if isinstance(pv_pepe, dict) else [])
                 | set((pepe_out or {}).keys())
                 if (pv_pepe.get(k) if isinstance(pv_pepe, dict) else None) != (pepe_out or {}).get(k)}
        changes.append({"item": "PEPE-mint", "type": "value-change", "diff": pdiff})
except Exception as ex:
    changes.append({"item": "_meta", "type": "prev-compare-error", "error": str(ex)[:120]})
log("changes vs 0134:", json.dumps(changes)[:3000])


# threshold check (info only): AGCLUB free% vs 50/70, Matrix/Ledgera counters, BOLD totalSupply (NOT a verified free counter)
def pct(a, b):
    return round(100.0 * a / b, 1) if a is not None and b else None
ag = reads.get("AGCLUB", {}).get("views") or {}
mx = reads.get("Matrix", {}).get("views") or {}
lg = reads.get("Ledgera", {}).get("views") or {}
bo = reads.get("BoldLeonidas", {}).get("views") or {}
threshold = {"AGCLUB_free_pct": pct(ag.get("freeMinted"), ag.get("FREE_CAP")),
             "Matrix_freeMinted": mx.get("freeMinted"),
             "Ledgera_freeClaimed": lg.get("freeClaimed"),
             "BOLD_totalSupply_over_MAX": pct(bo.get("totalSupply"), 1111),
             "BOLD_note": "totalSupply/MAX is NOT a verified free counter (no freeClaimed/freeMinted view); free% stays UNVERIFIED, website unverified, age unverified - no strong-lead promotion possible"}
log("threshold", threshold)

# getCode check for new Boltbook addresses that are not sale-shape (owner/EOA detection)
def get_code(addr):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [addr, "latest"]}, timeout=30)
            if isinstance(r, dict) and r.get("result") is not None:
                return r["result"]
        except Exception:
            continue
    return None
getcode_out = {}
for a in bb_new:
    if a.lower() not in {s2["address"].lower() for s2 in shape_out if s2.get("S1") or s2.get("S2")}:
        code = get_code(a)
        getcode_out[a] = {"code": (code[:20] + "...len=" + str(len(code)) if code else None),
                          "is_contract": bool(code and code != "0x")}
        log("getCode", a, "is_contract", getcode_out[a]["is_contract"])

# bridge (read-only)
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    b_contracts = bridge.get("contracts", bridge) if isinstance(bridge, dict) else bridge
    if isinstance(b_contracts, dict):
        b_list = list(b_contracts.keys())
        b_disc = sum(1 for v in b_contracts.values()
                     if isinstance(v, dict) and v.get("same_owner_discarded"))
    else:
        b_list, b_disc = b_contracts, 0
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for v in snap.get("contracts", {}).values():
        if isinstance(v, dict) and v.get("address"):
            snap_addrs.add(v["address"].lower())
    for v in snap.get("track_c", {}).values():
        if isinstance(v, dict):
            if v.get("sale"):
                snap_addrs.add(str(v["sale"]).lower())
            if v.get("token"):
                snap_addrs.add(str(v["token"]).lower())
    not_in_snap = [a for a in b_list if a.lower() not in snap_addrs]
    bridge_out = {"total": len(b_list), "not_in_snapshot": len(not_in_snap),
                  "not_in_snapshot_list": not_in_snap,
                  "same_owner_discarded": b_disc}
except Exception as ex:
    bridge_out = {"error": f"{type(ex).__name__}: {str(ex)[:120]}"}
log("bridge", bridge_out)

# update seen (own file only)
added = []
for a in feed_new:
    if a.lower() not in seen_l:
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                   "status": "seen-0144", "note": ""}
        added.append(a)
added_l = {x.lower() for x in added}
for a in bb_new:
    if a.lower() not in seen_l and a.lower() not in added_l:
        seen[a] = {"first_seen_wib": NOW, "source": "boltbook-en",
                   "status": "seen-0144", "note": ""}
        added.append(a); added_l.add(a.lower())
for a, gc in getcode_out.items():
    if not gc["is_contract"] and a.lower() not in seen_l and a.lower() not in added_l:
        seen[a] = {"first_seen_wib": NOW, "source": "boltbook-en",
                   "status": "checked-not-contract",
                   "note": "Address on Boltbook front page run 0139; eth_getCode 0x = EOA, not a contract; not a lead."}
        added.append(a); added_l.add(a.lower())
for r in shape_out:
    a = r["address"]
    if r.get("status") == "checked":
        cur = seen.get(a)
        if isinstance(cur, dict) and cur.get("status", "").startswith("seen-0139"):
            cur["status"] = "checked-not-sale-shape"
            cur["note"] = json.dumps(r)[:500]
        elif a.lower() not in seen_l and a not in added:
            seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                       "status": "checked-not-sale-shape",
                       "note": json.dumps(r)[:500]}
            added.append(a); added_l.add(a.lower())
    elif r.get("status") == "shape-check-failed" and a.lower() not in seen_l and a.lower() not in added_l:
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                   "status": "shape-check-failed", "note": json.dumps(r)[:500]}
        added.append(a)
if added:
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"))
log("seen", seen_n0, "->", len(seen), "added", added)

out = {"run": RUN_TAG, "started_wib": NOW,
       "sourcify_feed": {"total": len(results), "error": feed_error, "new": len(feed_new),
                         "new_contracts": feed_new,
                         "top": feed_addrs[0] if feed_addrs else None,
                         "top_verifiedAt": results[0].get("verifiedAt") if results else None,
                         "all": feed_addrs},
       "boltbook_en": {"bytes": len(en_html), "http_code": "200" if en_html else None, "error": bb_errors.get("en"),
                       "full_address_contracts": len(en_addrs),
                       "addresses": en_addrs,
                       "new": len([a for a in en_addrs if a.lower() not in seen_l]),
                       "new_contracts": [a for a in en_addrs if a.lower() not in seen_l],
                       "free_kw": kw_en, "zh_free_kw": kw_zh_en},
       "boltbook_zh": {"bytes": len(zh_html), "http_code": "200" if zh_html else None, "error": bb_errors.get("zh"),
                       "full_address_contracts": len(zh_addrs),
                       "addresses": zh_addrs,
                       "new": len([a for a in zh_addrs if a.lower() not in seen_l]),
                       "new_contracts": [a for a in zh_addrs if a.lower() not in seen_l],
                       "free_kw": kw_en_zh, "zh_free_kw": kw_zh},
       "shape_check_targets": [t[0] for t in targets],
       "shape_check": shape_out,
       "shape_hits": hits,
       "leg4_reread": {"reads": reads, "endpoint": EPS[0],
                       "n_calls": sum(len(v[1]) for v in ITEMS.values()),
                       "chunk_size": 4, "chunk_errors": chunk_errors,
                       "note": "chunked batches of 4 contracts",
                       "block": blk},
       "leg4_changes_vs_0139": changes,
       "pepe_reread": pepe_out,
       "bridge_scan": bridge_out,
       "seen_added": added, "seen_n": len(seen), "seen_n_prev": seen_n0,
       "threshold_check": threshold, "getcode_check": getcode_out,
       "elapsed_s": round(time.time() - t0, 1),
       "executions": "none - no preview, no mint, no claim (this script is read-only)"}
json.dump(out, open(BASE + "hot-leg-run-2026-11-17-0144.json", "w"), indent=1)
print("DONE elapsed", out["elapsed_s"], "changes", len(changes), "hits", hits)
