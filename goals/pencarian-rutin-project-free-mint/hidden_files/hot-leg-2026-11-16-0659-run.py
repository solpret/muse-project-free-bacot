#!/usr/bin/env python3
"""Hot-leg run 2026-11-16 06:59 WIB. Legs 1-4 lite + bridge (read-only).
Based on hot-leg-2026-11-16-0654-run.py (same legs, prev reread -> 0654).
- case-insensitive seen membership (0304 correction: mixed-case keys)
- bridge: addresses are dict KEYS (0304 bug fix baked in)
- bridge FIX 0449 (per 0444 runlog): snapshot keys are project NAMES;
  addresses live inside entry values -> collect all 0x addresses from
  contracts/track_c/pending_claims VALUES, not keys.
- Leg4 diff vs 0449 hot-leg reread (most recent verified state).
Leg1 Sourcify feed, Leg2 Boltbook EN+ZH, Leg3 shape-check new sale-shape,
Leg4 lite re-read of 9 key items.
Writes: hot-leg-2026-11-16-0659-feed.json, -boltbook-en/zh.html,
run-hot-leg-2026-11-16-0659.json, run-hot-leg-2026-11-16-0659-reread.json,
hot-leg-2026-11-16-0659-runlog.md. Updates hot-leg-seen.json ONLY with
newly seen contracts. NEVER writes snapshot / main seen files / bridge.
No preview/mint."""
import json, subprocess, time, re, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "2026-11-16-0659"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted",
              "freeRemaining","freeSharesLeft"]
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
t0 = time.time()
log = []
def say(s):
    print(s, flush=True); log.append(s)

def http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_lower = set(k.lower() for k in seen)
reported = json.load(open(BASE + "hot-leg-reported.json"))
prev_reread = json.load(open(BASE + "run-hot-leg-2026-11-16-0654-reread.json"))
seen_before = len(seen)
out = {"run": "free-mint-hot-leg 2026-11-16 06:59 WIB",
       "started_wib": "2026-11-16T06:59:38+07:00"}

# ---------- Leg 1: Sourcify feed ----------
feed_addrs = []
try:
    raw = http_get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 25)
    feed = json.loads(raw)
    json.dump(feed, open(BASE + f"hot-leg-{RUN}-feed.json", "w"), indent=1)
    res = feed.get("results", feed.get("contracts", []))
    feed_addrs = [c["address"].lower() for c in res]
    out["feed"] = {"n": len(feed_addrs),
                   "newest_verifiedAt": res[0].get("verifiedAt") if res else None,
                   "oldest_verifiedAt": res[-1].get("verifiedAt") if res else None}
    say(f"Leg1 feed: {len(feed_addrs)} contracts, newest {out['feed']['newest_verifiedAt']}")
except Exception as e:
    out["feed"] = {"error": str(e)}
    say(f"Leg1 feed FAIL: {e} (leg skipped)")

# ---------- Leg 2: Boltbook EN+ZH (curl; urllib failed 0354) ----------
bb_addrs = []
for lang, fn in [("en", "boltbook-en"), ("zh", "boltbook-zh")]:
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    try:
        html = subprocess.run(["curl", "-sL", "--max-time", "25", "-A", "Mozilla/5.0", url],
                              capture_output=True, timeout=30).stdout
        if not html:
            raise RuntimeError("curl returned empty body")
        open(BASE + f"hot-leg-{RUN}-{fn}.html", "wb").write(html)
        addrs = sorted(set(a.lower() for a in re.findall(r"0x[a-fA-F0-9]{40}", html.decode("utf-8", "ignore"))))
        bb_addrs += addrs
        out[f"boltbook_{lang}"] = {"bytes": len(html), "addrs": addrs}
        say(f"Leg2 Boltbook {lang}: {len(html)} bytes, {len(addrs)} distinct addresses")
    except Exception as e:
        out[f"boltbook_{lang}"] = {"bytes": 0, "addrs": [], "error": str(e)}
        say(f"Leg2 Boltbook {lang} FAIL: {e} (leg skipped)")
bb_addrs = sorted(set(bb_addrs))

# ---------- shape-check helper ----------
def fetch_abi(addr):
    try:
        raw = http_get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", 25)
        d = json.loads(raw)
        return d.get("abi") or (d.get("stdJson", {}) or {}).get("abi")
    except Exception:
        return None

def shape_check(addr):
    abi = fetch_abi(addr)
    if not abi:
        return {"S1": None, "S2": None, "mint": None, "quote": None, "free": None,
                "agent": None, "status": "shape-check-failed"}
    fnames = set()
    for e in abi:
        if e.get("type") == "function":
            fnames.add(e.get("name", ""))
    has_mint = any(n.startswith("mint") for n in fnames)
    has_quote = any(n in fnames for n in ["quote","cost","priceFor","getQuote","costOf","mintPrice"])
    has_free = sorted(n for n in fnames if n in FREE_VIEWS)
    abi_txt = json.dumps(abi)
    has_reg = any("AGENT_ID_REGISTRY" in n or "AgentGate" in n or "agentRegistry" in n for n in fnames) \
        or REGISTRY.lower() in abi_txt.lower()
    has_token = all(n in fnames for n in ["name","symbol","decimals","totalSupply"])
    s1 = has_mint and has_quote and bool(has_free) and has_reg
    s2 = has_token and "mintFree" in fnames and bool(has_free) and \
        any(n in fnames for n in ["FREE_SLOTS","FREE_SUPPLY","FREE_MAX","FREE_CAP"]) and has_reg
    return {"S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote, "free": has_free,
            "agent": has_reg, "status": "checked"}

# ---------- Leg 1+2 new-address triage (case-insensitive vs seen) ----------
new_addrs = sorted(set([a for a in feed_addrs + bb_addrs if a not in seen_lower and a not in EXCLUDED]))
say(f"New vs seen: {len(new_addrs)} (feed {len(feed_addrs)}, boltbook {len(bb_addrs)})")
feed_new = [a for a in new_addrs if a in feed_addrs]
bb_new = [a for a in new_addrs if a in bb_addrs]
out["feed_new"] = feed_new
out["boltbook_new"] = bb_new
out["feed_shape"] = {}
out["boltbook_new_shapecheck"] = {}
for a in new_addrs:
    sc = shape_check(a)
    seen[a] = {"first_seen_wib": "2026-11-16T06:59:38+07:00",
               "source": "sourcify-feed" if a in feed_addrs else "boltbook",
               "status": sc["status"],
               "note": f"S1={sc['S1']} S2={sc['S2']} mint={sc['mint']} quote={sc['quote']} free={sc['free']} agent={sc['agent']}"}
    if a in feed_addrs:
        out["feed_shape"][a] = sc
    else:
        out["boltbook_new_shapecheck"][a] = sc
    say(f"  {a} -> {sc}")

# retry shape-check-failed backlog (last 8)
failed = [k for k, v in seen.items()
          if isinstance(v, dict) and v.get("status") == "shape-check-failed"]
retry = failed[-8:]
retry_results = {}
for a in retry:
    sc = shape_check(a)
    retry_results[a] = sc["status"]
    if sc["status"] == "checked":
        seen[a] = {"first_seen_wib": seen[a].get("first_seen_wib", "?"), "source": "retry-0659",
                   "status": "checked",
                   "note": f"S1={sc['S1']} S2={sc['S2']} mint={sc['mint']} quote={sc['quote']} free={sc['free']} agent={sc['agent']}"}
    else:
        seen[a]["note"] = (seen[a].get("note", "") + " | retry 2026-11-16T06:59:38+07:00: still 404")
say(f"Retry shape-check-failed: {len(retry)} retried, results {retry_results}")
out["retry_404"] = {"total_failed": len(failed), "retried": retry, "results": retry_results}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["seen_total"] = len(seen)
say(f"Seen {seen_before} -> {len(seen)}")

# ---------- Bridge (read-only; addresses are dict KEYS) ----------
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    contracts = bridge.get("contracts", bridge) if isinstance(bridge, dict) else bridge
    blist = list(contracts.items()) if isinstance(contracts, dict) else [(c.get("address"), c) for c in contracts]
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    # FIX 0449: snapshot keys are project NAMES; addresses live in values.
    snap_txt = json.dumps(snap.get("contracts", {})) + json.dumps(snap.get("track_c", {})) + json.dumps(snap.get("pending_claims", {}))
    snap_addrs = set(a.lower() for a in re.findall(r"0x[a-fA-F0-9]{40}", snap_txt))
    b_new = [a for a, c in blist if isinstance(c, dict) and (a or "").lower() not in snap_addrs
             and not c.get("same_owner_discarded")]
    b_disc = sum(1 for a, c in blist if isinstance(c, dict) and c.get("same_owner_discarded"))
    out["bridge"] = {"n": len(blist), "same_owner_discarded": b_disc, "outside_snapshot": b_new,
                     "snapshot_value_addrs": len(snap_addrs)}
    say(f"Bridge: {len(blist)} contracts, {len(b_new)} not in snapshot values (non-discarded), {b_disc} same_owner_discarded; no promotion run ini")
except Exception as e:
    out["bridge"] = {"error": str(e)}
    say(f"Bridge SKIP (unreadable): {e}")

# ---------- Leg 4 lite: re-read 9 key items ----------
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
def post_rpc(ep, payload, timeout=150):
    outp = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(outp)

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
 "RaceAgents": ("0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_MAX","FREE_MAX()",[]),("mintOpen","mintOpen()",[])]),
 "AgentBubble": ("0x0d72970046c056db90888351b739246f468bff0b", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("freeClaimed_user","freeClaimed(address)",U)]),
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
 "Matrix Agents": ("0x1F669b714337F3C2585072c53fdDD89581F928fF", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("freeRemaining","freeRemaining()",[]),("mintOpen","mintOpen()",[]),
    ("FREE_MAX","FREE_MAX()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("paidMinted","paidMinted()",[]),("mintPrice","mintPrice()",[]),
    ("freeClaimedByAgent_masgayut","freeClaimedByAgent(bytes32)",["0xecf9f926ceb2309ff2b025ef0ce7fb6e1fd0f8ba6a79adffff80a4beb3ac410c"]),
    ("freeClaimedByAgent_masgayut_ai","freeClaimedByAgent(bytes32)",["0x621fa1d010af5819fe524dea10780d79858451bedb5e4b81ac7d183d0e9e1cc3"])]),
}

def read_chunk(chunk):
    calls, meta = [], []
    for name, (addr, views) in chunk:
        for key, sig, args in views:
            calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                          "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
            meta.append((name, key))
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=150)
            if not isinstance(res, list) or len(res) != len(calls):
                say(f"  chunk ep {ep} bad shape"); continue
            outd = {}
            for it, (name, key) in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    outd.setdefault(name, {})[key] = None
                else:
                    r = it["result"]
                    outd.setdefault(name, {})[key] = to_int(r[:66]) if len(r) >= 66 else r
            return outd, ep
        except Exception as e:
            say(f"  chunk ep {ep} exc {str(e)[:100]}"); continue
    return None, None

def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=150)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16)
        except Exception: continue
    return None

reads, ok = {}, 0
items = list(ITEMS.items())
for ci in range(0, len(items), 3):
    ch = items[ci:ci+3]
    r, ep = read_chunk(ch)
    names = [n for n, _ in ch]
    if r is None:
        say(f"Leg4 chunk {ci//3+1} FAIL {names}")
        for n in names: reads[n] = {"address": ITEMS[n][0], "views": None}
        continue
    ok += sum(1 for n in names if r.get(n) is not None)
    for n in names: reads[n] = {"address": ITEMS[n][0], "views": r.get(n)}
    say(f"Leg4 chunk {ci//3+1} OK via {ep} ({time.time()-t0:.0f}s) {names}")
    time.sleep(3)
blk = block_number()
rout = {"started_wib": "2026-11-16T06:59:38+07:00", "reads": reads, "reads_ok": ok,
        "reads_total": len(ITEMS), "block": blk, "elapsed_s": round(time.time() - t0, 1)}
json.dump(rout, open(BASE + f"run-hot-leg-{RUN}-reread.json", "w"), indent=1)
say(f"Leg4 DONE reads_ok {ok}/{len(ITEMS)} block {blk} elapsed {round(time.time()-t0,1)}s")

# ---------- diff vs 0654 hot-leg reread (most recent verified state) ----------
prev = prev_reread.get("reads", {})
changes = []
for name, cur in reads.items():
    cv = cur.get("views") or {}
    pv = (prev.get(name) or {}).get("views") or {}
    diffs = {k: (pv.get(k), v) for k, v in cv.items() if pv.get(k) != v}
    if diffs:
        changes.append((name, diffs))
        say(f"CHANGE vs 0654 {name}: {diffs}")
if not changes:
    say("Leg4: no changes vs 0654 hot-leg reread")
out["leg4_changes"] = changes
out["leg4_prev_block"] = prev_reread.get("block")
# Cross-check vs 0654 hot-leg reread (most recent verified state):
# 0654 reported MORFO totalMinted 796->797 (routine mint increment);
# so reportable = diffs vs 0654 only; the 0614 comparison is kept as
# context in the previous run's file, not recomputed here.
try:
    main0654 = prev_reread  # = 0654 reread
    mreads = main0654.get("reads", {})
    new_changes = []
    for name, cur in reads.items():
        cv = cur.get("views") or {}
        mv = (mreads.get(name) or {}).get("views") or {}
        diffs = {k: (mv.get(k), v) for k, v in cv.items() if mv.get(k) != v}
        if diffs:
            new_changes.append((name, diffs))
            say(f"NEW-CHANGE vs 0654 {name}: {diffs}")
    if not new_changes:
        say("Leg4: no new changes vs 0654 hot-leg reread")
    out["leg4_new_changes_vs_0654"] = new_changes
    out["leg4_prev0654_block"] = main0654.get("block")
except Exception as e:
    out["leg4_new_changes_vs_0654"] = {"error": str(e)}
    say(f"Leg4 cross-check vs 0654 SKIP: {e}")
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + f"run-hot-leg-{RUN}.json", "w"), indent=1)

open(BASE + f"hot-leg-{RUN}-runlog.md", "w").write("# Hot-leg run 2026-11-16 06:59 WIB\n\n" + "\n".join("- " + l for l in log) + "\n")
say("RUNLOG written")
