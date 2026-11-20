#!/usr/bin/env python3
"""Hot-leg run 2026-11-19 05:19 WIB (job free-mint-hot-leg).
Legs, in order, skip-on-stall: (1) Sourcify feed limit 20 + shape-check ONLY
new addresses (not in hot-leg-seen.json / snapshot); (2) Boltbook EN+ZH front
page, shape-check only new addresses; (3) on-chain re-read of snapshot PLAN
items (read-only, compare vs run-2026-11-19-0501-reread.json for changes);
(4) scan-bridge.json read-only. Writes ONLY this run's JSON files +
hot-leg-seen.json (new contracts) + hot-leg-reported.json (only if reportable).
NEVER rewrites main snapshot / scan seen / track-c-checked. No preview/mint/claim.
No Ankr (dead 401 since 2026-11-09; hot-leg runs no chain-wide scan anyway)."""
import json, re, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from eth_hash.auto import keccak
from quicknode import ProxyHTTPSConnection
from dynamic_credentials import dynamic_credential_entry
QN_HOST = "stylish-thrilling-star.bsc.quiknode.pro"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
STAMP = "2026-11-19-0519"
out = {"run": "free-mint-hot-leg 2026-11-19 05:19 WIB", "started_wib": "2026-11-19 05:19 WIB"}

def https_get(host, path, timeout=20, redirects=3):
    conn = ProxyHTTPSConnection(host, 443, timeout=timeout)
    try:
        conn.request("GET", path, headers={"User-Agent": UA, "Accept": "*/*"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
        loc = resp.getheader("Location")
    finally:
        conn.close()
    if status in (301, 302, 303, 307, 308) and loc and redirects > 0:
        if loc.startswith("http"):
            from urllib.parse import urlparse
            u = urlparse(loc)
            return https_get(u.hostname, u.path + ("?" + u.query if u.query else ""), timeout, redirects - 1)
        return https_get(host, loc, timeout, redirects - 1)
    return status, raw

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def encode(sig, arg):
    data = "0x" + sel(sig)
    if arg == "user":
        data += enc_addr(USER)
    elif arg == "one":
        data += "%064x" % 1
    elif arg == "user1":
        data += enc_addr(USER) + "%064x" % 1
    return data

def curl_json(payload, timeout=40):
    entry = dynamic_credential_entry("custom.quicknode")
    surrogate = str(entry["surrogate"]).strip()
    conn = ProxyHTTPSConnection(QN_HOST, 443, timeout=timeout)
    try:
        conn.request("POST", f"/{surrogate}/", body=json.dumps(payload).encode(),
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
    finally:
        conn.close()
    if status != 200:
        raise IOError(f"quicknode http {status}: {raw[:150]!r}")
    return json.loads(raw.decode())

def rpc_batch(calls, timeout=40):
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    resp = curl_json(payload, timeout=timeout)
    if not isinstance(resp, list):
        raise IOError(f"non-list batch response: {str(resp)[:200]}")
    by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
    res = []
    for i in range(len(calls)):
        it = by_id.get(i + 1, {})
        if "result" in it and it["result"] not in (None, "0x"):
            try:
                res.append(int(it["result"], 16))
            except Exception:
                res.append(it["result"])
        elif "error" in it:
            res.append(f"err:{it['error']}")
        else:
            res.append(None)
    return res

# ---- (1) Sourcify feed ----
try:
    status, raw = https_get("sourcify.dev", "/server/v2/contracts/56?limit=20&sort=desc", timeout=20)
    feed = json.loads(raw.decode())
    items = feed if isinstance(feed, list) else feed.get("results", feed.get("contracts", []))
    addrs = [it.get("address") for it in items if isinstance(it, dict) and it.get("address")]
    out["sourcify_feed"] = {"http": status, "total": len(addrs), "addresses": addrs,
        "verifiedAt_top": (items[0].get("verifiedAt") if items and isinstance(items[0], dict) else None)}
except Exception as e:
    out["sourcify_feed"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# ---- (2) Boltbook EN + ZH ----
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
bb_addrs = set()
for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        from urllib.parse import urlparse
        u = urlparse(url)
        status, raw = https_get(u.hostname, u.path + ("?" + u.query if u.query else ""), timeout=25)
        html = raw.decode("utf-8", errors="replace")
        open(f"{HF}/run-{STAMP}-boltbook-{lang}.html", "w").write(html)
        addrs = sorted(set(ADDR_RE.findall(html)))
        bb_addrs.update(a.lower() for a in addrs)
        out[f"boltbook_{lang}"] = {"bytes": len(html), "http_code": str(status),
            "full_address_contracts": len(addrs), "addresses": addrs,
            "free_kw": html.lower().count("free mint") + html.lower().count("free-mint")}
    except Exception as e:
        out[f"boltbook_{lang}"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# ---- shape-check helper ----
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted",
              "freeCardsRemaining"}
def shape_check(addr):
    try:
        st2, raw2 = https_get("sourcify.dev", f"/server/v2/contract/56/{addr}?fields=abi", timeout=20)
        meta2 = json.loads(raw2.decode()); abi = meta2.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate", "agentIDRegistry", "holdsAgentID", "setAgentIDRegistry", "holdsAgentId"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token,
                "n_fns": len(names), "status": "checked", "verifiedAt": meta2.get("verifiedAt")}
    except Exception as e:
        return {"address": addr, "status": "shape-check-failed", "error": f"{type(e).__name__}: {str(e)[:120]}"}

# ---- shape-check targets: feed + boltbook new vs hot-leg-seen + snapshot ----
try:
    hl_seen = json.load(open(f"{HF}/hot-leg-seen.json"))
    hl_l = {k.lower() for k in hl_seen}
    snap = json.load(open(f"{HF}/onchain-snapshot.json"))
    snap_l = set()
    for v in snap.get("contracts", {}).values():
        if isinstance(v, dict) and isinstance(v.get("address"), str):
            snap_l.add(v["address"].lower())
    for v in (snap.get("track_c", {}) or {}).values():
        if isinstance(v, dict):
            for f in ("address", "sale", "token"):
                if isinstance(v.get(f), str) and v[f].startswith("0x"):
                    snap_l.add(v[f].lower())
    cand = []
    for a in out.get("sourcify_feed", {}).get("addresses", []):
        if a.lower() not in hl_l and a.lower() not in snap_l and a not in cand:
            cand.append(a)
    for a in sorted(bb_addrs):
        if a not in hl_l and a not in snap_l and a not in [c.lower() for c in cand]:
            cand.append(a)
    out["shape_targets"] = cand
    out["shape_check_new"] = [shape_check(a) for a in cand]
    out["shape_check_sale_shape"] = [x for x in out["shape_check_new"] if x.get("S1") or x.get("S2")]
    # record newly seen (checked) contracts into hot-leg-seen.json (append-only)
    now_iso = "2026-11-19T05:19:00+07:00"
    new_seen = {}
    for x in out["shape_check_new"]:
        a = x["address"]
        if a not in hl_seen:
            new_seen[a] = {"first_seen_wib": now_iso,
                "note": str(x)[:400], "source": "sourcify-feed" if a in out.get("sourcify_feed", {}).get("addresses", []) else "boltbook-en+zh",
                "status": "checked-sale-shape" if (x.get("S1") or x.get("S2")) else "checked-not-sale-shape"}
    if new_seen:
        hl_seen.update(new_seen)
        json.dump(hl_seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)
    out["hot_leg_seen_added"] = len(new_seen)
except Exception as e:
    out["shape_check_new"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# ---- (3) Leg-4 re-read of snapshot PLAN items (same PLAN as run 0501) ----
PLAN = [
 ("HIVE Agents", "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77",
  [("totalSupply", "totalSupply()", None), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("PUNNY", "0xaFAE0Bf373ad87E88555afe1605111F66C99062C",
  [("totalMinted", "totalMinted()", None), ("freeMinted", "freeMinted()", None),
   ("freeRemaining", "freeRemaining()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("mintStart", "mintStart()", None), ("mintClosed", "mintClosed()", None),
   ("hasClaimedFree_user", "hasClaimedFree(address)", "user"),
   ("mintedBy_user", "mintedBy(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Vitaliq Scans", "0xad0d78689d047bb9a32f5bf93438373a73da68ec",
  [("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None),
   ("genesisStart", "genesisStart()", None), ("holdsAgentId_user", "holdsAgentId(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Bubblebruin", "0xc205F8c74733D914776D66cBc4Cf10BF701D96Aa",
  [("totalSupply", "totalSupply()", None), ("freeClaimed", "freeClaimed()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Matrix", "0x1F669b714337F3C2585072c53fdDD89581F928fF",
  [("freeMinted", "freeMinted()", None), ("freeRemaining", "freeRemaining()", None),
   ("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None)]),
 ("AGCLUB", "0x67270bb351515abf3089ca5420456897363f5e75",
  [("totalMinted", "totalMinted()", None), ("freeMinted", "freeMinted()", None),
   ("FREE_CAP", "FREE_CAP()", None), ("mintOpen", "mintOpen()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Ledgera", "0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d",
  [("freeClaimed", "freeClaimed()", None), ("totalSupply", "totalSupply()", None),
   ("mintOpen", "mintOpen()", None), ("freeUsed_user", "freeUsed(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
  [("freeSharesLeft", "freeSharesLeft()", None), ("openedAt", "openedAt()", None),
   ("freeClaimed", "freeClaimed()", None), ("freeBooked_user", "freeBooked(address)", "user")]),
 ("AONE-sale", "0x84D82E933D7781fe11245e7bbd3Eb23dbb963666",
  [("freeMinted", "freeMinted()", None), ("freeQuotaLeft", "freeQuotaLeft()", None),
   ("FREE_TOTAL", "FREE_TOTAL()", None), ("LAUNCH", "LAUNCH()", None),
   ("freeTaken_user", "freeTaken(address)", "user"),
   ("quote_user_1", "quote(address,uint256)", "user1")]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", "launched()", None), ("failed", "failed()", None),
   ("isRefundPhase", "isRefundPhase()", None), ("totalShares", "totalShares()", None),
   ("tokenClaimed_user", "tokenClaimed(address)", "user")]),
 ("ARKYN", "0x69b0b5756671680766d232eb4b0f39a34be5d852",
  [("totalMinted", "totalMinted()", None), ("totalSupply", "totalSupply()", None)]),
 ("Lumenhold", "0x9701980b0afd825134390ee46fb3bd675a2f356f",
  [("totalSupply", "totalSupply()", None), ("freeClaimed", "freeClaimed()", None)]),
 ("AgentNOVA", "0x43462d7f269fde4914b03e1e07067a61b62b9540",
  [("totalSupply", "totalSupply()", None)]),
 ("STOCK AGENT", "0xba7068233da805bdebcc167be361c219002e6b7f",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
   ("freeLeft", "freeLeft()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("cost_user_1", "cost(address,uint256)", "user1"), ("quote_user_1", "quote(address,uint256)", "user1"),
   ("freeMintedByWallet_user", "freeMintedByWallet(address)", "user"),
   ("mintedCount_user", "mintedCount(address)", "user"),
   ("freeClaimed_user", "freeClaimed(address)", "user"),
   ("freeUsed_user", "freeUsed(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("AgentMintPass", "0xfcadfb7cc85b6ea540d64e4f4b9f162e630f55c0",
  [("totalMinted", "totalMinted()", None), ("balanceOf_user", "balanceOf(address)", "user"),
   ("mintedCount_user", "mintedCount(address)", "user")]),
 ("AGATE-Pass", "0x5b63bd45e61a2e6540548c3509b598b6384206c5",
  [("totalMinted", "totalMinted()", None), ("balanceOf_user", "balanceOf(address)", "user"),
   ("hasMinted_user", "hasMinted(address)", "user")]),
 ("AgentDrop", "0x1dd8740ffca0be3caac3b4a3eb41fdff506e38a9",
  [("totalMinted", "totalMinted()", None), ("balanceOf_user", "balanceOf(address)", "user"),
   ("hasMinted_user", "hasMinted(address)", "user")]),
 ("THYRK", "0x4d90ffc3075fb8897edff6d7c6269c906664a20e",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
   ("freeLeft", "freeLeft()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("cost_user_1", "cost(address,uint256)", "user1"), ("quote_user_1", "quote(address,uint256)", "user1"),
   ("freeMintedByWallet_user", "freeMintedByWallet(address)", "user"),
   ("mintedCount_user", "mintedCount(address)", "user"),
   ("freeClaimed_user", "freeClaimed(address)", "user"),
   ("freeUsed_user", "freeUsed(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
]
BSCCAT_ADDR = "0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A"
BSCCAT_VIEWS = [("totalMinted", "totalMinted()", None), ("soldShares", "soldShares()", None),
  ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
  ("freeSharesLeft", "freeSharesLeft()", None), ("FREE_SHARES", "FREE_SHARES()", None),
  ("FREE_SUPPLY", "FREE_SUPPLY()", None), ("totalShares", "totalShares()", None),
  ("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None),
  ("opened", "opened()", None), ("poolOpen", "poolOpen()", None),
  ("isPoolOpen", "isPoolOpen()", None), ("launched", "launched()", None),
  ("hasMinted_user", "hasMinted(address)", "user"),
  ("freeClaimed_user", "freeClaimed(address)", "user"),
  ("freeUsed_user", "freeUsed(address)", "user"),
  ("freeLeft_user", "freeLeft(address)", "user"),
  ("mintedBy_user", "mintedBy(address)", "user"),
  ("quote_user_1", "quote(address,uint256)", "user1"),
  ("cost_user_1", "cost(address,uint256)", "user1"),
  ("costOf_1", "costOf(uint256)", "one"), ("bnbQuote_1", "bnbQuote(uint256)", "one"),
  ("token", "token()", None), ("TOKEN", "TOKEN()", None),
  ("balanceOf_user", "balanceOf(address)", "user")]
PEPE_MINT = "0x7E920e9e4Ad8E4497aEa7EB9bAF60Cd6c6C8D980"
PEPE_VIEWS = [("freeMinted", "freeMinted()", None), ("soldShares", "soldShares()", None),
  ("FREE_SHARES", "FREE_SHARES()", None), ("opened", "opened()", None),
  ("costOf_1", "costOf(uint256)", "one"),
  ("hasMinted_user", "hasMinted(address)", "user")]

import concurrent.futures as _cf
calls, meta = [], []
for name, addr, views in PLAN:
    for label, sig, arg in views:
        calls.append((addr, encode(sig, arg)))
        meta.append((name, addr, label))
for label, sig, arg in BSCCAT_VIEWS:
    calls.append((BSCCAT_ADDR, encode(sig, arg)))
    meta.append(("bsccat", BSCCAT_ADDR, label))
for label, sig, arg in PEPE_VIEWS:
    calls.append((PEPE_MINT, encode(sig, arg)))
    meta.append(("pepe", PEPE_MINT, label))
CHUNK = 5
idxs = list(range(0, len(calls), CHUNK))
res = [None] * len(calls)
chunk_errors = []
def _one(i):
    try:
        r = rpc_batch(calls[i:i+CHUNK], timeout=40)
        return i, r, None
    except Exception as e:
        return i, [None]*len(calls[i:i+CHUNK]), f"calls {i}-{i+len(calls[i:i+CHUNK])-1}: {type(e).__name__}: {str(e)[:150]}"
def _persist():
    reads, bsccat, pepe = {}, {"address": BSCCAT_ADDR, "views": {}}, {}
    for (name, addr, label), val in zip(meta, res):
        if name == "bsccat":
            bsccat["views"][label] = val
        elif name == "pepe":
            pepe[label] = val
        else:
            reads.setdefault(name, {"address": addr, "views": {}})[ "views"][label] = val
    try:
        blk = curl_json([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}], timeout=40)
        block = int(blk[0]["result"], 16)
    except Exception as e:
        block = f"error: {str(e)[:120]}"
    json.dump({"reads": reads, "bsccat": bsccat, "pepe": pepe, "errors": chunk_errors,
               "n_calls": len(calls), "elapsed_s": round(time.time()-T0, 1), "block": block},
              open(f"{HF}/run-{STAMP}-reread.json", "w"), indent=1)
    return block
block = None
try:
    with _cf.ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(_one, i): i for i in idxs}
        done = 0
        for fut in _cf.as_completed(futs):
            i, r, err = fut.result()
            res[i:i+len(r)] = r
            if err: chunk_errors.append(err)
            done += 1
            block = _persist()
    out["leg4_block"] = block
    out["leg4_chunk_errors"] = chunk_errors
    out["leg4_n_calls"] = len(calls)
    out["leg4_chunks_done"] = done
except Exception as e:
    out["leg4"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# ---- diff vs previous reread (0501) ----
try:
    prev = json.load(open(f"{HF}/run-2026-11-19-0501-reread.json"))
    cur = json.load(open(f"{HF}/run-{STAMP}-reread.json"))
    changes = []
    for name, entry in cur.get("reads", {}).items():
        pv = prev.get("reads", {}).get(name, {}).get("views", {})
        for label, val in entry.get("views", {}).items():
            old = pv.get(label)
            if val != old:
                changes.append({"item": name, "field": label, "old": old, "new": val})
    for sect in ("bsccat", "pepe"):
        pv = prev.get(sect, {}).get("views", {}) if sect == "bsccat" else prev.get(sect, {})
        cv = cur.get(sect, {}).get("views", {}) if sect == "bsccat" else cur.get(sect, {})
        for label, val in cv.items():
            old = pv.get(label)
            if val != old:
                changes.append({"item": sect, "field": label, "old": old, "new": val})
    out["leg4_changes_vs_0501"] = changes
    out["leg4_prev_block"] = prev.get("block")
except Exception as e:
    out["leg4_changes_vs_0501"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# ---- (4) Bridge (read-only) ----
try:
    snap = json.load(open(f"{HF}/onchain-snapshot.json"))
    snap_addrs = {str(v.get("address", "")).lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
    bridge = json.load(open(f"{HF}/scan-bridge.json"))
    baddrs = list(bridge.get("contracts", {}).keys())
    not_in = [a for a in baddrs if a.lower() not in snap_addrs]
    disc = [a for a, c in bridge.get("contracts", {}).items() if isinstance(c, dict) and c.get("same_owner_discarded")]
    out["bridge"] = {"total": len(baddrs), "not_in_snapshot": len(not_in),
                     "not_in_snapshot_list": not_in, "same_owner_discarded": len(disc)}
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

out["elapsed_s"] = round(time.time() - T0, 1)
out["executions"] = "none - no preview, no mint, no claim (read-only)"
json.dump(out, open(f"{HF}/run-{STAMP}.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str)[:6000])
