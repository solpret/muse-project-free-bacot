#!/usr/bin/env python3
"""Hot-leg run 2026-11-19 01:44 WIB. Legs: (1) Sourcify feed poll + shape-check
new; (2) Boltbook EN+ZH front pages + keyword sweep; (3) on-chain verify any
new sale-shape; (4) re-read FOKUS-15 (main-job 0101 PLAN) + bsccat + pepe +
hot-leg extras (AgentEcho/Kageveil/XCOPY/PunchCard/ARKT/EIM/ARKT-claim),
compare vs 0101 reread (block 134356258) + 0734 log; bridge read-only.
Read-only except this run's own JSON + hot-leg-seen.json appends + run log.
No preview/mint/claim."""
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
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
T0 = time.time()
RUN = "hot-leg 2026-11-19 01:44 WIB"
out = {"run": RUN, "started_wib": "2026-11-19 01:44 WIB"}

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
            res.append(f"err:{str(it['error'])[:80]}")
        else:
            res.append(None)
    return res

# ---- Leg 1: Sourcify feed ----
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
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token,
                "n_fns": len(names), "status": "checked", "verifiedAt": meta2.get("verifiedAt")}
    except Exception as e:
        return {"address": addr, "status": "shape-check-failed", "error": f"{type(e).__name__}: {str(e)[:120]}"}

seen = json.load(open(f"{HF}/hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
new_seen = {}
try:
    status, raw = https_get("sourcify.dev", "/server/v2/contracts/56?limit=20&sort=desc", timeout=20)
    feed = json.loads(raw.decode())
    items = feed if isinstance(feed, list) else feed.get("results", feed.get("contracts", []))
    addrs = [it.get("address") for it in items if isinstance(it, dict) and it.get("address")]
    out["sourcify_feed"] = {"http": status, "total": len(addrs), "addresses": addrs,
        "verifiedAt_top": (items[0].get("verifiedAt") if items and isinstance(items[0], dict) else None)}
except Exception as e:
    out["sourcify_feed"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
    addrs = []

feed_new = [a for a in addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED
            and a.lower() != REGISTRY.lower()]
out["feed_new"] = feed_new
out["shape_check_feed"] = [shape_check(a) for a in feed_new]
for r in out["shape_check_feed"]:
    if r.get("status") == "checked":
        new_seen[r["address"]] = {"first_seen_wib": "2026-11-19T01:44:38+07:00",
            "note": f"S1={r['S1']} S2={r['S2']} mint={r['has_mint']} quote={r['has_quote']} free={r['free_views']} agent={r['agent_ref']} token={r['is_token']}",
            "source": "sourcify-feed", "status": "checked-not-sale-shape" if not (r["S1"] or r["S2"]) else "sale-shape"}

# ---- Leg 2: Boltbook EN+ZH ----
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
KW_EN = ["free share", "first share free", "1 free share", "free mint share"]
KW_ZH = ["免费份额", "首个免费", "免费铸造", "免费mint"]
for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        status, raw = https_get("boltbook.fun", "/" if lang == "en" else "/?lang=zh", timeout=25)
        html = raw.decode("utf-8", errors="replace")
        open(f"{HF}/hot-leg-2026-11-19-0144-boltbook-{lang}.html", "w").write(html)
        addrs2 = sorted(set(ADDR_RE.findall(html)))
        kw = {k: html.lower().count(k.lower()) for k in (KW_EN if lang == "en" else KW_ZH)}
        out[f"boltbook_{lang}"] = {"bytes": len(html), "http_code": status,
            "full_address_contracts": len(addrs2), "addresses": addrs2, "keywords": kw}
    except Exception as e:
        out[f"boltbook_{lang}"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
        addrs2 = []
    if lang == "en":
        bb_en = addrs2
    else:
        bb_zh = addrs2
bb_new = [a for a in sorted(set(bb_en) | set(bb_zh))
          if a.lower() not in seen_l and a.lower() not in EXCLUDED
          and a.lower() not in {x.lower() for x in feed_new}]
out["boltbook_new"] = bb_new
out["shape_check_boltbook"] = [shape_check(a) for a in bb_new]
for r in out["shape_check_boltbook"]:
    if r.get("status") == "checked":
        new_seen[r["address"]] = {"first_seen_wib": "2026-11-19T01:44:38+07:00",
            "note": f"S1={r['S1']} S2={r['S2']} mint={r['has_mint']} quote={r['has_quote']} free={r['free_views']} agent={r['agent_ref']} token={r['is_token']}",
            "source": "boltbook-en+zh", "status": "checked-not-sale-shape" if not (r["S1"] or r["S2"]) else "sale-shape"}

sale_shape = [r for r in out["shape_check_feed"] + out["shape_check_boltbook"] if r.get("S1") or r.get("S2")]
out["sale_shape_new"] = sale_shape
# ---- Leg 3: on-chain verify any new sale-shape (free pool + user slot) ----
out["leg3_verify"] = []
for r in sale_shape:
    a = r["address"]
    calls = [(a, encode("freeSharesRemaining()", None)), (a, encode("freeMinted()", None)),
             (a, encode("freeClaimed(address)", "user")), (a, encode("quote(address,uint256)", "user1")),
             (a, encode("mintOpen()", None))]
    try:
        vals = rpc_batch(calls, timeout=40)
        out["leg3_verify"].append({"address": a, "freeSharesRemaining": vals[0], "freeMinted": vals[1],
            "freeClaimed_user": vals[2], "quote_user_1": vals[3], "mintOpen": vals[4],
            "note": "age UNVERIFIED (no first-mint corroboration this run) -> watchlist-only, never reported as lead, never previewed/minted"})
    except Exception as e:
        out["leg3_verify"].append({"address": a, "error": f"{type(e).__name__}: {str(e)[:150]}"})

# ---- Leg 4: re-read FOKUS-15 + bsccat + pepe + extras ----
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
GEN = [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
       ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
       ("normalMinted", "normalMinted()", None), ("mintOpen", "mintOpen()", None),
       ("paused", "paused()", None), ("hasClaimed_user", "hasClaimed(address)", "user"),
       ("balanceOf_user", "balanceOf(address)", "user")]
EXTRAS = [
 ("AgentEcho", "0xff2DAc2389a6A9593209b6008d5ffA9E73AA19C2", GEN),
 ("Kageveil Genesis", "0xf79860f419be7b604d909e254785400d9edbd9d0", GEN),
 ("XCOPY", "0x3fbeC44c7c845374267b06033940aBe45C63eDFA", GEN),
 ("PunchCard", "0x1d4Ef0587dD3FF3875a141D4711C60BcA40587C4", GEN),
 ("ARKT", "0xF91b1ebbcb2b038107ed10b4Cb163Ed51CE39037", GEN),
 ("EIM", "0x1FcCFAB61461C4B5C4D1b16580D12a7E32012Baa", GEN),
 ("ARKT-claim", "0x62a7AC33ca463331858693b8Aa05B16688bA29E0",
  [("totalSupply", "totalSupply()", None), ("paused", "paused()", None),
   ("hasClaimed_user", "hasClaimed(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
]
calls, meta = [], []
for name, addr, views in PLAN + EXTRAS:
    for label, sig, arg in views:
        calls.append((addr, encode(sig, arg)))
        meta.append((name, addr, label))
for label, sig, arg in BSCCAT_VIEWS:
    calls.append((BSCCAT_ADDR, encode(sig, arg)))
    meta.append(("bsccat", BSCCAT_ADDR, label))
for label, sig, arg in PEPE_VIEWS:
    calls.append((PEPE_MINT, encode(sig, arg)))
    meta.append(("pepe", PEPE_MINT, label))

import concurrent.futures as _cf
res = [None] * len(calls)
chunk_errors = []
CHUNK = 5
idxs = list(range(0, len(calls), CHUNK))
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
              open(f"{HF}/hot-leg-2026-11-19-0144-reread.json", "w"), indent=1)
    return block
block = None
with _cf.ThreadPoolExecutor(max_workers=4) as ex:
    futs = {ex.submit(_one, i): i for i in idxs}
    done = 0
    for fut in _cf.as_completed(futs):
        i, r, err = fut.result()
        res[i:i+len(r)] = r
        if err: chunk_errors.append(err)
        done += 1
        print(f"progress {done}/{len(idxs)} chunks", flush=True)
        block = _persist()
out["leg4_block"] = block
out["leg4_chunk_errors"] = chunk_errors
out["leg4_n_calls"] = len(calls)

# ---- Bridge (read-only) ----
try:
    snap = json.load(open(f"{HF}/onchain-snapshot.json"))
    snap_addrs = {str(v.get("address", "")).lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
    bridge = json.load(open(f"{HF}/scan-bridge.json"))
    baddrs = list(bridge.get("contracts", {}).keys())
    not_in = [a for a in baddrs if a.lower() not in snap_addrs]
    disc = [a for a, c in bridge.get("contracts", {}).items() if c.get("same_owner_discarded")]
    out["bridge"] = {"total": len(baddrs), "not_in_snapshot": len(not_in),
                     "not_in_snapshot_list": not_in, "same_owner_discarded": len(disc)}
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# ---- persist new seen entries ----
if new_seen:
    seen.update(new_seen)
    json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)
out["new_seen_added"] = len(new_seen)
out["elapsed_s"] = round(time.time() - T0, 1)
out["executions"] = "none - no preview, no mint, no claim (read-only)"
json.dump(out, open(f"{HF}/hot-leg-2026-11-19-0144.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str)[:6000])
