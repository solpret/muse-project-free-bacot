#!/usr/bin/env python3
"""Hot-leg run 2026-11-19 04:04 WIB. Legs: (1) Sourcify feed poll + shape-check
new; (2) Boltbook EN+ZH front pages + keyword sweep; (3) on-chain verify any
new sale-shape; (4) re-read 47-item focus set (same as 0359 reread: FOKUS +
bsccat + pepe + extras), compare vs 0359 reread (block 134379862); bridge
read-only. Direct curl (bsc-dataseed + sourcify + boltbook), no proxy.
Read-only except this run's own JSON + hot-leg-seen.json appends.
No preview/mint/claim."""
import json, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
RPC = "https://bsc-dataseed.binance.org/"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
T0 = time.time()
RUN = "free-mint-hot-leg 2026-11-19 04:04 WIB"
out = {"run": RUN, "started_wib": "2026-11-19T04:04:38+07:00"}

def curl_get(url, timeout=20):
    r = subprocess.run(["curl", "-s", "-m", str(timeout), "-A", UA, url],
                       capture_output=True, text=True, timeout=timeout + 5)
    return r.stdout

def curl_post(url, payload, timeout=30):
    r = subprocess.run(["curl", "-s", "-m", str(timeout), "-A", UA, "-H",
                        "Content-Type: application/json", "-X", "POST", url,
                        "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return r.stdout

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def sig_for(label):
    """label convention: base, base_user, base_1, base_user_1."""
    if label.endswith("_user_1"):
        return label[:-7] + "(address,uint256)", "user1"
    if label.endswith("_user"):
        return label[:-5] + "(address)", "user"
    if label.endswith("_1"):
        return label[:-2] + "(uint256)", "one"
    return label + "()", None

def encode(label):
    sig, arg = sig_for(label)
    data = "0x" + sel(sig)
    if arg == "user":
        data += enc_addr(USER)
    elif arg == "one":
        data += "%064x" % 1
    elif arg == "user1":
        data += enc_addr(USER) + "%064x" % 1
    return data

def rpc_batch(calls, timeout=30):
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    raw = curl_post(RPC, payload, timeout=timeout)
    resp = json.loads(raw)
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
        raw2 = curl_get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=20)
        meta2 = json.loads(raw2); abi = meta2.get("abi", [])
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
    raw = curl_get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=20)
    feed = json.loads(raw)
    items = feed if isinstance(feed, list) else feed.get("results", feed.get("contracts", []))
    addrs = [it.get("address") for it in items if isinstance(it, dict) and it.get("address")]
    out["sourcify_feed"] = {"total": len(addrs), "addresses": addrs,
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
        new_seen[r["address"]] = {"first_seen_wib": "2026-11-19T04:04:38+07:00",
            "note": f"S1={r['S1']} S2={r['S2']} mint={r['has_mint']} quote={r['has_quote']} free={r['free_views']} agent={r['agent_ref']} token={r['is_token']}",
            "source": "sourcify-feed", "status": "checked-not-sale-shape" if not (r["S1"] or r["S2"]) else "sale-shape"}

# ---- Leg 2: Boltbook EN+ZH ----
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
KW_EN = ["free share", "first share free", "1 free share", "free mint share"]
KW_ZH = ["免费份额", "首个免费", "免费铸造", "免费mint"]
bb_all = {}
for lang, path in (("en", "/"), ("zh", "/?lang=zh")):
    try:
        html = curl_get(f"https://boltbook.fun{path}", timeout=25)
        open(f"{HF}/hot-leg-2026-11-19-0404-boltbook-{lang}.html", "w").write(html)
        addrs2 = sorted(set(ADDR_RE.findall(html)))
        kw = {k: html.lower().count(k.lower()) for k in (KW_EN if lang == "en" else KW_ZH)}
        out[f"boltbook_{lang}"] = {"bytes": len(html), "http_code": 200 if html else None,
            "full_address_contracts": len(addrs2), "addresses": addrs2, "keywords": kw}
        bb_all[lang] = addrs2
    except Exception as e:
        out[f"boltbook_{lang}"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
        bb_all[lang] = []
bb_new = [a for a in sorted(set(bb_all.get("en", [])) | set(bb_all.get("zh", [])))
          if a.lower() not in seen_l and a.lower() not in EXCLUDED
          and a.lower() not in {x.lower() for x in feed_new}]
out["boltbook_new"] = bb_new
out["shape_check_boltbook"] = [shape_check(a) for a in bb_new]
for r in out["shape_check_boltbook"]:
    if r.get("status") == "checked":
        new_seen[r["address"]] = {"first_seen_wib": "2026-11-19T04:04:38+07:00",
            "note": f"S1={r['S1']} S2={r['S2']} mint={r['has_mint']} quote={r['has_quote']} free={r['free_views']} agent={r['agent_ref']} token={r['is_token']}",
            "source": "boltbook-en+zh", "status": "checked-not-sale-shape" if not (r["S1"] or r["S2"]) else "sale-shape"}

sale_shape = [r for r in out["shape_check_feed"] + out["shape_check_boltbook"] if r.get("S1") or r.get("S2")]
out["sale_shape_new"] = sale_shape
# ---- Leg 3: on-chain verify any new sale-shape ----
out["leg3_verify"] = []
for r in sale_shape:
    a = r["address"]
    calls = [(a, encode("freeSharesRemaining")), (a, encode("freeMinted")),
             (a, encode("freeClaimed_user")), (a, encode("quote_user_1")),
             (a, encode("mintOpen"))]
    try:
        vals = rpc_batch(calls, timeout=30)
        out["leg3_verify"].append({"address": a, "freeSharesRemaining": vals[0], "freeMinted": vals[1],
            "freeClaimed_user": vals[2], "quote_user_1": vals[3], "mintOpen": vals[4],
            "note": "age UNVERIFIED (no first-mint corroboration this run) -> watchlist-only, never reported as lead, never previewed/minted"})
    except Exception as e:
        out["leg3_verify"].append({"address": a, "error": f"{type(e).__name__}: {str(e)[:150]}"})

# ---- Leg 4: re-read focus set (same as 0359 reread) ----
plan = json.load(open(f"{HF}/hot-leg-run-2026-11-19-0404-plan.json"))
calls, meta = [], []
for p in plan:
    for label in p["views"]:
        calls.append((p["address"], encode(label)))
        meta.append((p["name"], p["address"], label))
res = [None] * len(calls)
chunk_errors = []
CHUNK = 4
idxs = list(range(0, len(calls), CHUNK))
def _one(i):
    try:
        r = rpc_batch(calls[i:i+CHUNK], timeout=30)
        return i, r, None
    except Exception as e:
        return i, [None]*len(calls[i:i+CHUNK]), f"calls {i}-{i+len(calls[i:i+CHUNK])-1}: {type(e).__name__}: {str(e)[:150]}"
def _persist():
    reads, bsccat, pepe = {}, {"address": "0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A", "views": {}}, {}
    for (name, addr, label), val in zip(meta, res):
        if name == "bsccat":
            bsccat["views"][label] = val
        elif name == "pepe":
            pepe[label] = val
        else:
            reads.setdefault(name, {"address": addr, "views": {}})[ "views"][label] = val
    try:
        blk = json.loads(curl_post(RPC, [{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}], timeout=20))
        block = int(blk["result"], 16)
    except Exception as e:
        block = f"error: {str(e)[:120]}"
    json.dump({"started_wib": "2026-11-19T04:04:38+07:00", "reads": reads, "bsccat": bsccat, "pepe": pepe,
               "errors": chunk_errors, "n_calls": len(calls), "elapsed_s": round(time.time()-T0, 1), "block": block},
              open(f"{HF}/hot-leg-run-2026-11-19-0404-reread.json", "w"), indent=1)
    return block
block = None
with ThreadPoolExecutor(max_workers=4) as ex:
    futs = {ex.submit(_one, i): i for i in idxs}
    done = 0
    for fut in as_completed(futs):
        i, r, err = fut.result()
        res[i:i+len(r)] = r
        if err: chunk_errors.append(err)
        done += 1
        block = _persist()
out["leg4_block"] = block
out["leg4_chunk_errors"] = chunk_errors
out["leg4_n_calls"] = len(calls)

# ---- Compare vs 0359 reread ----
try:
    prev = json.load(open(f"{HF}/hot-leg-run-2026-11-19-0359-reread.json"))
    cur = json.load(open(f"{HF}/hot-leg-run-2026-11-19-0404-reread.json"))
    changes = []
    for name, pv in prev["reads"].items():
        cv = cur["reads"].get(name, {}).get("views", {})
        for label, pval in pv["views"].items():
            nval = cv.get(label)
            if pval != nval:
                changes.append({"item": name, "view": label, "prev": pval, "now": nval})
    for label, pval in prev["bsccat"]["views"].items():
        nval = cur["bsccat"]["views"].get(label)
        if pval != nval:
            changes.append({"item": "bsccat", "view": label, "prev": pval, "now": nval})
    for label, pval in prev["pepe"].items():
        nval = cur["pepe"].get(label)
        if pval != nval:
            changes.append({"item": "pepe", "view": label, "prev": pval, "now": nval})
    out["leg4_changes_vs_0359"] = changes
    out["leg4_prev_block"] = prev.get("block")
    # threshold snapshot for key items
    def rd(name):
        return cur["reads"].get(name, {}).get("views", {})
    sa, lh, al = rd("STOCKAGENT"), rd("Lumenhold"), rd("ALIEN")
    out["threshold_check"] = {
        "STOCKAGENT_free_pct": round(100*(1111-sa["freeLeft"])/1111, 1) if isinstance(sa.get("freeLeft"), int) else None,
        "STOCKAGENT": {k: sa.get(k) for k in ("totalSupply","freeLeft","FREE_SUPPLY","mintOpen","quote_user_1","freeMintedByWallet_user","balanceOf_user")},
        "Lumenhold_free_pct": round(100*lh["freeClaimed"]/1500, 1) if isinstance(lh.get("freeClaimed"), int) else None,
        "Lumenhold": {k: lh.get(k) for k in ("totalSupply","freeClaimed","FREE_SUPPLY","mintOpen","balanceOf_user","mintedBy_user")},
        "ALIEN_free_pct": round(100*al["totalSupply"]/1000, 1) if isinstance(al.get("totalSupply"), int) else None,
        "ALIEN": {k: al.get(k) for k in ("totalSupply","FREE_SUPPLY","mintOpen","isFreePhase","balanceOf_user")},
        "AgentBubble": {k: rd("AgentBubble").get(k) for k in ("totalMinted","totalSupply","MAX_SUPPLY","freeMinted","mintOpen","balanceOf_user")},
        "binanceai_pending": {k: rd("binanceai-mint").get(k) for k in ("launched","failed","isRefundPhase","totalShares","tokenClaimed_user")},
        "notes": "Strong-lead bar >70% + age <24h + slot open + verified website. STOCKAGENT + Lumenhold: age + website still UNVERIFIED per snapshot (early-lead-reported-2026-11-18-0031 / watchlist-only-age-unverified-2026-11-17) -> no promotion regardless of %.",
    }
except Exception as e:
    out["leg4_compare_error"] = f"{type(e).__name__}: {str(e)[:150]}"

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

if new_seen:
    seen.update(new_seen)
    json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)
out["new_seen_added"] = len(new_seen)
out["elapsed_s"] = round(time.time() - T0, 1)
out["executions"] = "none - no preview, no mint, no claim (read-only)"
json.dump(out, open(f"{HF}/hot-leg-2026-11-19-0404.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str)[:7000])
