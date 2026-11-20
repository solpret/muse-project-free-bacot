#!/usr/bin/env python3
"""Hot-leg run 2026-11-18 17:44 WIB (scheduled 17:44:38).
Cloned pattern from 1739 run: legs (1) Sourcify feed, (2) Boltbook EN+ZH,
(3) shape-check new contracts, (4) re-read 6-item focus set vs 1739 reread,
bridge read-only. Transport: Quicknode ProxyHTTPSConnection CONNECT tunnel
(direct curl dead since 16:29/16:34 probes). Read-only except own
hot-leg-seen.json + run JSONs. No preview/mint/claim."""
import json, re, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
from eth_hash.auto import keccak
from quicknode import ProxyHTTPSConnection
from dynamic_credentials import dynamic_credential_entry
QN_HOST = "stylish-thrilling-star.bsc.quiknode.pro"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
NOW = "2026-11-18 17:44 WIB"
RUN_TAG = "free-mint-hot-leg 2026-11-18 17:44 WIB"
PREV_REREAD = "hot-leg-run-2026-11-18-1739-reread.json"
PREV_RUN = "hot-leg-run-2026-11-18-1739.json"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
t0 = time.time()
def log(*a): print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)
def https_get(host, path, timeout=20, redirects=3):
    conn = ProxyHTTPSConnection(host, 443, timeout=timeout)
    try:
        conn.request("GET", path, headers={"User-Agent": UA, "Accept": "*/*"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
        loc = resp.getheader("Location")
    finally:
        conn.close()
    if status in (301,302,303,307,308) and loc and redirects > 0:
        if loc.startswith("http"):
            from urllib.parse import urlparse
            u = urlparse(loc)
            return https_get(u.hostname, u.path + ("?" + u.query if u.query else ""), timeout, redirects-1)
        return https_get(host, loc, timeout, redirects-1)
    return status, raw

seen = json.load(open(HF + "/hot-leg-seen.json"))
seen_l = {k.lower(): v for k, v in seen.items()}
seen_n0 = len(seen)

# (1) Sourcify feed
feed_addrs, feed_meta, feed_err, feed_http = [], [], None, None
try:
    status, raw = https_get("sourcify.dev", "/server/v2/contracts/56?limit=20&sort=desc", timeout=20)
    feed_http = status
    data = json.loads(raw.decode())
    items = data if isinstance(data, list) else data.get("results", data)
    for it in items[:20]:
        a = it.get("address") if isinstance(it, dict) else None
        if a:
            feed_addrs.append(a)
            feed_meta.append({"address": a, "verifiedAt": it.get("verifiedAt"), "match": it.get("match")})
    log("feed", feed_http, len(feed_addrs))
except Exception as e:
    feed_err = f"{type(e).__name__}: {str(e)[:150]}"
    log("feed ERROR", feed_err)
feed_new = [a for a in feed_addrs if a.lower() not in seen_l and a.lower() != REG.lower()
            and a.lower() not in EXCLUDED]
log("feed new:", feed_new)

# (2) Boltbook EN + ZH
def boltbook(host_path):
    try:
        status, raw = https_get("boltbook.fun", host_path, timeout=25)
        text = raw.decode("utf-8", "ignore")
        addrs = []
        for m in re.finditer(r"0x[0-9a-fA-F]{40}", text):
            a = m.group(0)
            if a not in addrs:
                addrs.append(a)
        kw = sum(text.lower().count(k) for k in ("free share", "first share free", "1 free share", "free mint share"))
        zhkw = sum(text.count(k) for k in ("\u514d\u8d39\u4efd\u989d", "\u9996\u4e2a\u514d\u8d39", "\u514d\u8d39\u94f8\u9020", "\u514d\u8d39mint"))
        return {"bytes": len(raw), "http_code": status, "addresses": addrs, "free_kw": kw, "zh_free_kw": zhkw, "error": None}
    except Exception as e:
        return {"bytes": 0, "http_code": None, "addresses": [], "free_kw": 0, "zh_free_kw": 0,
                "error": f"{type(e).__name__}: {str(e)[:120]}"}
en = boltbook("/")
zh = boltbook("/?lang=zh")
log("boltbook EN", en["bytes"], "addrs", len(en["addresses"]))
log("boltbook ZH", zh["bytes"], "addrs", len(zh["addresses"]))
bb_all = en["addresses"] + [a for a in zh["addresses"] if a not in en["addresses"]]
bb_new = [a for a in bb_all if a.lower() not in seen_l and a.lower() not in EXCLUDED]
en_new = [a for a in en["addresses"] if a.lower() not in seen_l and a.lower() not in EXCLUDED]
zh_new = [a for a in zh["addresses"] if a.lower() not in seen_l and a.lower() not in EXCLUDED]
log("boltbook new:", bb_new)

# (3) shape-check new contracts
FREE_VIEWS = {"freesharesremaining", "freeclaimed", "freefor", "freeleft", "freeused",
              "freeavailable", "freesharepoolexhausted", "freessharesclaimed", "freeminted",
              "freesharesleft", "freesharesclaimed"}
def shape_check(addr, verified_at=None):
    try:
        status, raw = https_get("sourcify.dev", f"/server/v2/contract/56/{addr}?fields=abi", timeout=20)
        d = json.loads(raw.decode())
        abi = d.get("abi") or d.get("stdJson", {}).get("abi") or []
        if not abi:
            return {"address": addr, "S1": False, "S2": False, "status": "no-abi-from-sourcify",
                    "verifiedAt": verified_at}
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns[e.get("name", "").lower()] = e
        names = set(fns)
        has_mint = any(n.startswith("mint") or n in ("claimfree", "claim", "buy", "purchase") for n in names)
        has_quote = bool(names & {"cost", "quote", "costof", "bnbquote", "price", "getcost"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentregistry", "registry", "agentgate", "agentid"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalsupply"})
        has_mintfree = "mintfree" in names
        has_free_slots = bool(names & {"free_slots", "free_supply", "freeslots", "freesupply", "free_amount", "freeamount"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and has_mintfree and bool(names & {"freeclaimed", "freeminted"}) and has_free_slots and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token,
                "n_fns": len(fns), "status": "checked", "verifiedAt": verified_at}
    except Exception as e:
        return {"address": addr, "S1": False, "S2": False,
                "status": f"shape-check-error: {type(e).__name__}: {str(e)[:100]}",
                "verifiedAt": verified_at}
new_contracts = []
for a in feed_new + bb_new:
    if a.lower() not in {x.lower() for x in new_contracts}:
        new_contracts.append(a)
vmap = {m["address"].lower(): m.get("verifiedAt") for m in feed_meta}
shape_out = [shape_check(a, vmap.get(a.lower())) for a in new_contracts]
hits = [s["address"] for s in shape_out if s.get("S1") or s.get("S2")]
for s in shape_out:
    log("shape", s["address"][:12], "S1", s.get("S1"), "S2", s.get("S2"), s.get("status"))
log("shape hits:", hits)

# ---- RPC via Quicknode tunnel ----
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0" * 24 + a[2:].lower()
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        elif isinstance(a, str) and a.startswith("0x"):
            d += "%064x" % int(a, 16)
        else:
            d += "%064x" % int(a)
    return "0x" + d
def qn_post(payload, timeout=25):
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
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return v
def rpc_batch(calls):
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]} for i, (to, data) in enumerate(calls)]
    resp = qn_post(payload)
    if not isinstance(resp, list):
        raise IOError(f"non-list batch response: {str(resp)[:200]}")
    by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
    res = []
    for i in range(len(calls)):
        it = by_id.get(i + 1, {})
        if "result" in it and it["result"] not in (None, "0x"):
            res.append(to_int(it["result"][:66]) if len(it["result"]) >= 66 else it["result"])
        elif "error" in it:
            res.append(f"err:{it['error']}")
        else:
            res.append(None)
    return res
def read_all(items, chunk=5):
    calls, meta = [], []
    for name, addr, views in items:
        for key, sig, args in views:
            calls.append((addr, build_data(sig, args)))
            meta.append((name, key))
    reads, errors = {}, []
    for bi in range(0, len(calls), chunk):
        batch, bmeta = calls[bi:bi+chunk], meta[bi:bi+chunk]
        try:
            vals = rpc_batch(batch)
            for v, (name, key) in zip(vals, bmeta):
                reads.setdefault(name, {})[key] = v
        except Exception as e:
            errors.append({"batch": bi // chunk, "error": f"{type(e).__name__}: {str(e)[:120]}"})
            for name, key in bmeta:
                reads.setdefault(name, {})[key] = None
    return reads, errors

U = [USER]
ITEMS = [
 ("DGF CARD", "0x01f9CA4ff95d49594cC8B6591022186dc5C1Bc72", [
    ("totalMinted", "totalMinted()", []), ("balanceOf_user", "balanceOf(address)", U)]),
 ("BinanceAI", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched", "launched()", []), ("failed", "failed()", []),
    ("tokenClaimed_user", "tokenClaimed(address)", U)]),
 ("AlphaPulse V1", "0xE09Ab25732b1e1FdA7ad4d551EEA0aAC65aD0711", [
    ("totalSupply", "totalSupply()", []), ("mintOpen", "mintOpen()", []),
    ("balanceOf_user", "balanceOf(address)", U)]),
 ("FABE", "0xFabE022a5943462fee1Bd221791945DA57510BE8", [
    ("freeSharesRemaining", "freeSharesRemaining()", []), ("launched", "launched()", []),
    ("freeSharesClaimed_user", "freeSharesClaimed(address)", U), ("totalShares", "totalShares()", [])]),
 ("PUNNY", "0xaFAE0Bf373ad87E88555afe1605111F66C99062C", [
    ("freeMinted", "freeMinted()", []), ("FREE_SUPPLY", "FREE_SUPPLY()", []),
    ("totalMinted", "totalMinted()", []), ("hasClaimedFree_user", "hasClaimedFree(address)", U)]),
 ("STOCK AGENT", "0xba7068233da805bdebcc167be361c219002e6b7f", [
    ("totalSupply", "totalSupply()", []), ("freeLeft", "freeLeft()", []),
    ("quote_user_1", "quote(address,uint256)", [USER, 1]),
    ("quoteFor_user_1", "quoteFor(address,uint256)", [USER, 1]),
    ("freeMintedByWallet_user", "freeMintedByWallet(address)", U),
    ("balanceOf_user", "balanceOf(address)", U)]),
]
t_rpc = time.time()
reads, errors = read_all(ITEMS)
blk = None
try:
    r = qn_post({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})
    if isinstance(r, dict) and r.get("result"):
        blk = int(r["result"], 16)
except Exception as e:
    errors.append({"block": f"{type(e).__name__}: {str(e)[:100]}"})
log(f"reread {len(reads)} items, errors {errors}, block {blk}, rpc {time.time()-t_rpc:.1f}s")

# change detection vs 1739 reread
changes = {}
try:
    prev = json.load(open(HF + "/" + PREV_REREAD))
    prev_reads = {n: v.get("views") for n, v in (prev.get("reads", {}) or {}).items()}
    for name, cur in reads.items():
        pv = prev_reads.get(name)
        if pv is None:
            continue
        diff = {k: {"prev": pv.get(k), "now": cur.get(k)} for k in set(pv) | set(cur) if pv.get(k) != cur.get(k)}
        if diff:
            changes[name] = diff
except Exception as ex:
    changes = {"_meta": f"prev-compare-error: {str(ex)[:120]}"}
log("changes:", json.dumps(changes))

# promotion check (info only)
pun = reads.get("PUNNY") or {}
stk = reads.get("STOCK AGENT") or {}
pun_pct = round(100.0 * pun["freeMinted"] / pun["FREE_SUPPLY"], 2) if isinstance(pun.get("freeMinted"), int) and pun.get("FREE_SUPPLY") else None
stk_pct = round(100.0 * stk["totalSupply"] / 1111, 2) if isinstance(stk.get("totalSupply"), int) else None
promo = {
  "PUNNY_free_pct": pun_pct,
  "PUNNY_note": "age VERIFIED <24h (mintStart 2026-11-17 20:32 WIB, closes 20:32 WIB today); website gate UNVERIFIED -> no promotion even if pct crossed; pct must be >70% for strong lead.",
  "STOCK_free_pct_inferred": stk_pct,
  "STOCK_note": "age UNVERIFIED + website gate UNVERIFIED -> no promotion even if pct crossed 70%; inferred free% = totalSupply/1111 (freeLeft cross-check).",
  "DGF_note": "age + free% still unverified (no promotion); website verified but that alone is not a tier.",
}

# bridge (read-only)
try:
    bridge = json.load(open(HF + "/scan-bridge.json"))
    b_contracts = bridge.get("contracts", bridge) if isinstance(bridge, dict) else bridge
    if isinstance(b_contracts, dict):
        b_list = list(b_contracts.keys())
        b_disc = sum(1 for v in b_contracts.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
    else:
        b_list, b_disc = b_contracts, 0
    snap = json.load(open(HF + "/onchain-snapshot.json"))
    snap_addrs = set()
    for v in snap.get("contracts", {}).values():
        if isinstance(v, dict) and v.get("address"):
            snap_addrs.add(v["address"].lower())
    for v in snap.get("track_c", {}).values():
        if isinstance(v, dict):
            if v.get("sale"): snap_addrs.add(str(v["sale"]).lower())
            if v.get("token"): snap_addrs.add(str(v["token"]).lower())
    not_in_snap = [a for a in b_list if a.lower() not in snap_addrs]
    bridge_out = {"total": len(b_list), "not_in_snapshot": len(not_in_snap),
                  "not_in_snapshot_list": not_in_snap, "same_owner_discarded": b_disc}
except Exception as ex:
    bridge_out = {"error": f"{type(ex).__name__}: {str(ex)[:120]}"}
log("bridge", bridge_out)

# update seen (own file only)
added = []
for s in shape_out:
    a = s["address"]
    if a.lower() not in seen_l:
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed/boltbook",
                   "status": ("sale-shape-S1/S2" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"),
                   "note": str(s.get("status", ""))[:800]}
        added.append(a)
if added:
    json.dump(seen, open(HF + "/hot-leg-seen.json", "w"))
log("seen", seen_n0, "->", len(seen), "added", added)

n_calls = sum(len(v) for _, _, v in ITEMS)
reread = {"reads": {n: {"address": a, "views": reads.get(n)} for n, a, _ in ITEMS},
          "errors": errors, "n_calls": n_calls,
          "elapsed_s": round(time.time() - t_rpc, 1), "block": blk, "started_wib": NOW}
json.dump(reread, open(HF + "/hot-leg-run-2026-11-18-1744-reread.json", "w"), indent=1)

ver_window = None
if feed_meta:
    vs = [m.get("verifiedAt") for m in feed_meta if m.get("verifiedAt")]
    ver_window = [min(vs), max(vs)] if vs else None
result = "SILENT - no new lead, candidate, pending claim, change, or blocked auto-mint/auto-claim."
if hits or changes:
    result = "REVIEW - shape hit or state change detected; see leg3_sale_shape / leg4_changes."
out = {"run": RUN_TAG, "started_wib": NOW,
       "transport": "egress-proxy CONNECT tunnel (quicknode ProxyHTTPSConnection); direct curl dead at 16:34 probe",
       "leg1_sourcify": {"http": feed_http, "total": len(feed_addrs), "new": len(feed_new),
                         "new_contracts": feed_new, "verified_window": ver_window, "error": feed_err},
       "leg2_boltbook_en": {"bytes": en["bytes"], "http_code": en["http_code"],
                            "addresses": len(en["addresses"]), "new": len(en_new), "new_contracts": en_new,
                            "free_kw": en["free_kw"], "zh_free_kw": en["zh_free_kw"], "error": en["error"]},
       "leg2_boltbook_zh": {"bytes": zh["bytes"], "http_code": zh["http_code"],
                            "addresses": len(zh["addresses"]), "new": len(zh_new), "new_contracts": zh_new,
                            "free_kw": zh["free_kw"], "zh_free_kw": zh["zh_free_kw"], "error": zh["error"]},
       "leg3_shape_check": shape_out, "leg3_sale_shape": hits,
       "seen_added": added, "seen_n": len(seen),
       "leg4_reread": {"block": blk, "reads": reads, "errors": errors},
       "leg4_changes": changes, "leg4_promotion_check": promo,
       "leg4_note": "No sellout, slot loss, age-exclusion, claim opening, or tier promotion unless leg4_changes shows a qualifying state change.",
       "bridge": bridge_out,
       "elapsed_s": round(time.time() - t0, 1),
       "executions": "none - no preview, no mint, no claim (read-only run)",
       "result": result}
json.dump(out, open(HF + "/hot-leg-run-2026-11-18-1744.json", "w"), indent=1)
print("DONE elapsed", out["elapsed_s"], "changes", json.dumps(changes), "hits", hits)
print("RESULT", result)
