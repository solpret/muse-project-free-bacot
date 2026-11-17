#!/usr/bin/env python3
"""Hot-leg 0614 (2026-11-14): same pattern as 0609 run.
- Sourcify feed: FRESH crawl this run; new = in feed but NOT in hot-leg-seen.json.
- Boltbook EN/ZH: fresh fetch attempt (60s); fall back to noting stale cached copies.
- Kicks: SELLOUT 222/222 confirmed 0609, ALREADY REPORTED ONCE (hot-leg-reported.json)
  -> confirm fresh only, NEVER re-report.
- WANGCAI 0x61A2ff / YUANBAO 0xE8cF99 (new 0559): AGENT_ID()=registry, FREE_SUPPLY 188,
  freeClaimed 25/188 (13,3%) and 38/188 (20,2%) at 0609, age UNVERIFIED -> watchlist-only. This run:
  re-check freeClaimed/totalSupply/mintOpen + tokenURI(1) website probe (lesson 0609:
  probe tokenURI routinely). Age follow-up stays with main job (not in snapshot yet).
- Shape-check lesson 0609: name heuristic misses AGENT_ID() constant -> for NEW
  contracts with AGENT_ID in ABI but S1/S2 false, call AGENT_ID() and compare value
  to registry 0x60B9...022F.
- DragonAgents 70.3% BUT age-excluded (>46h) -> moot, diam.
- CRACE sellout main-job-captured; OLIVER 997/1000 age-excluded, already reported.
- Agentx: thread CLOSED (user declined override 13 Nov) - NO re-check, NO report.
LESSON: NEVER send a >24-call batch; ALL batches chunked to <=24 calls.
RPC timeout 60s per chunk; skip stalled legs. Read-only except
hot-leg-seen.json (new feed contracts recorded) + run output files."""
import json, re, subprocess, time
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
KICKS = "0x5726100e0D9ACB20cFB13e80e0fe42DF146730A8"
WANGCAI = "0x61A2ff9Be3db25e23886bC59D92d44fAa05959Cd"
YUANBAO = "0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
REG_PAD = REG[2:].lower().rjust(64, "0")
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def curl(url, data=None, timeout=60):
    cmd = ["curl", "-sS", "-m", str(timeout), "-A", "Mozilla/5.0"]
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", data]
    cmd.append(url)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
        return p.stdout if p.returncode == 0 and p.stdout else None
    except Exception:
        return None

def rpc_chunked(calls, timeout=60):
    out = []
    for i in range(0, len(calls), 24):
        chunk = calls[i:i + 24]
        body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(chunk), timeout=timeout)
        used_fb = False
        if not body:
            body = curl("https://bsc-dataseed1.bnbchain.org/", data=json.dumps(chunk), timeout=timeout)
            used_fb = True
        if not body:
            out += [(c["id"], None, "fetch-failed") for c in chunk]
            continue
        try:
            resp = json.loads(body)
            items = resp if isinstance(resp, list) else [resp]
            by_id = {it.get("id"): it for it in items if isinstance(it, dict)}
            if not used_fb and all(not by_id.get(c["id"], {}).get("result") for c in chunk):
                body2 = curl("https://bsc-dataseed1.bnbchain.org/", data=json.dumps(chunk), timeout=timeout)
                if body2:
                    try:
                        resp2 = json.loads(body2)
                        items2 = resp2 if isinstance(resp2, list) else [resp2]
                        by_id2 = {it.get("id"): it for it in items2 if isinstance(it, dict)}
                        if any(by_id2.get(c["id"], {}).get("result") for c in chunk):
                            by_id = by_id2
                    except Exception:
                        pass
            for c in chunk:
                it = by_id.get(c["id"], {})
                out.append((c["id"], it.get("result"), it.get("error")))
        except Exception as e:
            out += [(c["id"], None, f"parse-failed: {e}") for c in chunk]
    return out

def now_wib():
    return time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time() + 7 * 3600))

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        p = subprocess.run(["curl", "-sS", "-m", "60", "-A", "Mozilla/5.0", url],
                           capture_output=True, text=True, timeout=70)
        if p.returncode != 0 or not p.stdout:
            return None, f"curl rc={p.returncode} err={p.stderr[:100]}"
        meta = json.loads(p.stdout)
        return meta.get("abi", []), None
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:120]}"

def shape(addr, verified_at):
    abi, err = fetch_abi(addr)
    if abi is None:
        return {"address": addr, "verifiedAt": verified_at, "S1": None, "S2": None,
                "error": err, "status": "shape-check-failed"}
    names = set()
    for e in abi:
        if e.get("type") == "function":
            names.add(e["name"])
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
    free_views = sorted(names & set(FREE_VIEWS))
    agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId",
                              "agentGate", "AgentGate", "AGENT_ID_REGISTRY", "agentIdRegistry"})
    is_token = bool({"name", "symbol", "decimals", "totalSupply"} <= names)
    fns = {}
    for e in abi:
        if e.get("type") == "function":
            fns.setdefault(e["name"], []).append(e)
    mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
    s1 = bool(has_mint and has_quote and free_views and agent_ref)
    s2 = bool(is_token and mintfree and (names & {"freeClaimed", "freeMinted"})
              and (names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref)
    r = {"address": addr, "verifiedAt": verified_at, "S1": s1, "S2": s2,
         "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
         "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names),
         "functions": sorted(names), "status": "checked"}
    # lesson 0609: AGENT_ID() constant variant missed by name heuristic
    if (not s1 and not s2) and "AGENT_ID" in names:
        body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(
            [{"jsonrpc": "2.0", "id": 0, "method": "eth_call",
              "params": [{"to": addr, "data": sel("AGENT_ID()")}, "latest"]}]), timeout=60)
        try:
            j = json.loads(body) if body else {}
            res = (j[0].get("result") if isinstance(j, list) else j.get("result")) or ""
            r["AGENT_ID_value"] = res[-40:] if len(res) >= 42 else res
            r["AGENT_ID_is_registry"] = bool(res and res[-40:].lower() == REG[2:].lower())
        except Exception as e:
            r["AGENT_ID_error"] = str(e)[:120]
    return r

def token_uri(addr, tid=1):
    data = sel("tokenURI(uint256)") + "0" * 63 + str(tid)
    body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(
        [{"jsonrpc": "2.0", "id": 0, "method": "eth_call",
          "params": [{"to": addr, "data": data}, "latest"]}]), timeout=60)
    try:
        j = json.loads(body) if body else {}
        r = (j[0].get("result") if isinstance(j, list) else j.get("result")) or ""
        if r and len(r) > 130:
            ln = int(r[66:130], 16)
            return bytes.fromhex(r[130:130 + ln * 2]).decode("utf-8", "replace")
        return r
    except Exception as e:
        return f"decode error: {e}"

t0 = time.time()
out = {"run": "free-mint-hot-leg 2026-11-14 06:14 WIB", "started_wib": now_wib()}

try:
    seen = json.load(open(f"{HF}/hot-leg-seen.json"))
    seen_keys = {k.lower() for k in seen.keys()}
except Exception as e:
    seen, seen_keys = {}, set()
    out["seen_load_error"] = str(e)
out["seen_n"] = len(seen_keys)

# --- leg 1: Sourcify feed, fresh ---
feed_raw = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=60)
feed_list, new_feed = [], []
if feed_raw:
    try:
        fj = json.loads(feed_raw)
        items = fj.get("results", fj) if isinstance(fj, dict) else fj
        for it in items:
            addr = it.get("address") or it.get("contractAddress")
            va = it.get("verifiedAt") or it.get("creationMatch") or ""
            if addr:
                feed_list.append((addr, str(va)))
        new_feed = [(a, v) for a, v in feed_list if a.lower() not in seen_keys]
    except Exception as e:
        out["feed_parse_error"] = str(e)[:200]
out["sourcify_feed"] = {"crawl_wib": now_wib(), "total": len(feed_list),
                        "new": len(new_feed),
                        "new_contracts": [a for a, _ in new_feed],
                        "top5": [a for a, _ in feed_list[:5]],
                        "note": "0609 crawl 06:15:47 WIB (2 NEW: 0x5a7f4C + 0xC467f3, not sale-shape)"}

# --- leg 2: Boltbook EN + ZH fresh fetch attempt ---
def boltbook_fetch(url, tag):
    html = curl(url, timeout=60)
    if not html:
        return {"crawl": "fetch-failed (60s timeout/empty)", "new": "unknown",
                "note": "STALE cached copies reused: EN 2026-11-12 23:23 UTC, ZH 2026-11-13 10:59 UTC - 0 NEW in those copies"}
    fn = f"{HF}/run-2026-11-14-0614-boltbook-{tag}.html"
    open(fn, "w").write(html)
    addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    new_addrs = [a for a in addrs if a.lower() not in seen_keys]
    return {"crawl": now_wib(), "bytes": len(html), "full_address_contracts": len(addrs),
            "new": len(new_addrs), "new_contracts": new_addrs,
            "note": "fresh fetch OK this run"}
out["boltbook_en"] = boltbook_fetch("https://boltbook.fun/", "en")
out["boltbook_zh"] = boltbook_fetch("https://boltbook.fun/?lang=zh", "zh")

# --- shape-check NEW feed contracts + NEW boltbook contracts ---
to_shape = list(new_feed)
for tag in ("boltbook_en", "boltbook_zh"):
    for a in out[tag].get("new_contracts", []) or []:
        if a.lower() not in {x.lower() for x, _ in to_shape}:
            to_shape.append((a, "boltbook-" + tag))
shapes = [shape(a, v) for a, v in to_shape]
out["shape_check"] = shapes
out["s1_pass"] = [r["address"] for r in shapes if r.get("S1")]
out["s2_pass"] = [r["address"] for r in shapes if r.get("S2")]

# --- snapshot: Kicks entry + WANGCAI/YUANBAO presence ---
try:
    snap = json.load(open(f"{HF}/onchain-snapshot.json"))
    cons = snap.get("contracts", {})
    out["snapshot_kicks"] = cons.get("Kicks", "not in snapshot contracts")
    blob = json.dumps(snap)
    out["snapshot_wangcai_yuanbao_present"] = ("61A2ff" in blob) or ("WANGCAI" in blob) or ("YUANBAO" in blob)
except Exception as e:
    out["snapshot_kicks"] = f"read error: {e}"
    out["snapshot_wangcai_yuanbao_present"] = f"read error: {e}"

# --- leg 4 re-reads ---
PLAN = [
 ("Kicks", KICKS,
  [("freeMinted", False), ("FREE_CAP", False), ("freeCount", True), ("mintOpen", False),
   ("totalMinted", False), ("balanceOf", True)]),
 ("WANGCAI", WANGCAI,
  [("freeClaimed", False), ("FREE_SUPPLY", False), ("totalSupply", False),
   ("mintOpen", False), ("mintedBy", True), ("AGENT_ID", False)]),
 ("YUANBAO", YUANBAO,
  [("freeClaimed", False), ("FREE_SUPPLY", False), ("totalSupply", False),
   ("mintOpen", False), ("mintedBy", True), ("AGENT_ID", False)]),
 ("DragonAgents", "0xad0D8ac3D61fC8ab397B7136C69fcBf1281a4998",
  [("freeClaimed", False), ("FREE_SUPPLY", False), ("totalSupply", False),
   ("mintOpen", False), ("mintedBy", True)]),
 ("CRACE", "0x7B1ca439312368dE8652b9B5d7A54cA74A884680",
  [("freeMinted", False), ("FREE_QUOTA", False), ("mintOpen", False),
   ("totalSupply", False), ("freeClaimed", True)]),
 ("OLIVER", "0xad86e4d52e55709d1bda08f922853d4b109e0810",
  [("freeMinted", False), ("FREE_MAX", False), ("freeRemaining", False), ("mintOpen", False)]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", False), ("failed", False), ("isRefundPhase", False), ("tokenClaimed", True)]),
 ("AngelEye-77D9", "0x77D98247BA3dDAfa9ffBceA1F13d3e4cFe3f2d4C",
  [("freeMinted", False), ("freeRemaining", False), ("FREE_POOL", False),
   ("saleActive", False), ("mintStart", False)]),
 ("AbsurdAgentNFT", "0x72c14121681F1133545947B0735563835CC07B67",
  [("totalMinted", False), ("mintOpen", False), ("mintStartTime", False)]),
 ("AZEN", "0x699b6397986cc6c444069efe692023b1253dc26d",
  [("totalSupply", False), ("MAX_SUPPLY", False), ("freeMintedPerWallet", True)]),
 ("NovaRemnants", "0x38C1695eb72B7522c8d6452a4CE27122532A0d69",
  [("totalRemnants", False), ("genesisOpen", False), ("currentCycle", False)]),
 ("RaceAgents", "0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f",
  [("freeMinted", False), ("FREE_MAX", False), ("totalSupply", False), ("mintOpen", False)]),
 ("ACARD", "0xf1d544cc495a05320f36cd02d12e8ef9d9fbff69",
  [("freeMinted", False), ("FREE_CAP", False), ("totalMinted", False),
   ("mintOpen", False), ("freeClaimed", True)]),
 ("ARCADEWARDEN", "0xdb7257dbf18ca1539159c64534ffd68ef14c2f32",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("FREE_CAP", False),
   ("totalSupply", False), ("mintOpen", False), ("freeClaimed", True)]),
 ("NovaAgent", "0xe471c0e3e61837d3aa4b19bc6c2ac402f91e9b6f",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("totalSupply", False), ("mintOpen", False)]),
]
reqs, keys = [], []
for name, addr, views in PLAN:
    for fn, uarg in views:
        data = sel(fn + ("(address)" if uarg else "()")) + (USER_PAD if uarg else "")
        reqs.append({"jsonrpc": "2.0", "id": len(reqs), "method": "eth_call",
                     "params": [{"to": addr, "data": data}, "latest"]})
        keys.append((name, fn + ("_user" if uarg else "")))
reads, raw = {}, {}
for cid, r, err in rpc_chunked(reqs, timeout=60):
    name, fn = keys[cid]
    raw.setdefault(name, {})[fn] = r
    v = None
    if r and r != "0x" and len(r) >= 66:
        try:
            v = int(r[-64:], 16)
        except Exception:
            v = None
    reads.setdefault(name, {})[fn] = v
out["reads"] = reads
out["reads_ok"] = sum(1 for n in reads if any(v is not None for v in reads[n].values()))
out["reads_total"] = len(PLAN)
# AGENT_ID raw values (address, not uint)
for nm in ("WANGCAI", "YUANBAO"):
    r = (raw.get(nm, {}).get("AGENT_ID") or "")
    out[f"{nm.lower()}_AGENT_ID_raw"] = r
    out[f"{nm.lower()}_AGENT_ID_is_registry"] = bool(r and r[-40:].lower() == REG[2:].lower())
# tokenURI(1) probes for the pair (website discovery, lesson 0609)
out["wangcai_tokenURI_1"] = (token_uri(WANGCAI, 1) or "")[:600]
out["yuanbao_tokenURI_1"] = (token_uri(YUANBAO, 1) or "")[:600]

try:
    b = json.load(open(f"{HF}/scan-bridge.json"))
    c = b.get("contracts", {})
    out["bridge"] = {"n": len(c),
                     "not_in_snapshot": sum(1 for v in c.values() if not v.get("in_freebacot_snapshot")),
                     "same_owner_discarded": sum(1 for v in c.values() if v.get("same_owner_discarded")),
                     "note": "unchanged vs runs 0204-0609 (116 contracts) unless counts differ"}
except Exception as e:
    out["bridge"] = {"error": str(e)}

flags = {}
ki = reads.get("Kicks", {})
if ki.get("freeMinted") is not None and ki.get("FREE_CAP"):
    flags["Kicks_freeMinted"] = ki["freeMinted"]
    flags["Kicks_FREE_CAP"] = ki["FREE_CAP"]
    flags["Kicks_pct"] = round(ki["freeMinted"] / ki["FREE_CAP"] * 100, 1)
    flags["Kicks_totalMinted"] = ki.get("totalMinted")
    flags["Kicks_freeCount_user"] = ki.get("freeCount_user")
    flags["Kicks_balanceOf_user"] = ki.get("balanceOf_user")
    flags["Kicks_mintOpen"] = ki.get("mintOpen")
    flags["Kicks_soldout"] = bool(ki["freeMinted"] >= ki["FREE_CAP"])
    flags["Kicks_decision"] = ("SELLOUT confirmed fresh (222/222); ALREADY REPORTED ONCE run 0609 "
                               "(hot-leg-reported.json) - NO duplicate report" if flags["Kicks_soldout"]
                               else "NOT sold out - re-evaluate")
for nm, addr in (("WANGCAI", WANGCAI), ("YUANBAO", YUANBAO)):
    d = reads.get(nm, {})
    flags[f"{nm}_freeClaimed"] = d.get("freeClaimed")
    flags[f"{nm}_FREE_SUPPLY"] = d.get("FREE_SUPPLY")
    if d.get("freeClaimed") is not None and d.get("FREE_SUPPLY"):
        flags[f"{nm}_pct"] = round(d["freeClaimed"] / d["FREE_SUPPLY"] * 100, 1)
    flags[f"{nm}_totalSupply"] = d.get("totalSupply")
    flags[f"{nm}_mintOpen"] = d.get("mintOpen")
    flags[f"{nm}_mintedBy_user"] = d.get("mintedBy_user")
    flags[f"{nm}_AGENT_ID_is_registry"] = out.get(f"{nm.lower()}_AGENT_ID_is_registry")
    flags[f"{nm}_tokenURI_1"] = (out.get(f"{nm.lower()}_tokenURI_1") or "")[:300]
    flags[f"{nm}_in_snapshot"] = out.get("snapshot_wangcai_yuanbao_present")
    pct = flags.get(f"{nm}_pct")
    if pct is not None and pct > 70:
        flags[f"{nm}_decision"] = ("pct>70% BUT age UNVERIFIED (not in snapshot, no first-mint) "
                                   "-> watchlist-only, NEVER preview/mint, report only if main job verifies age+website")
    else:
        flags[f"{nm}_decision"] = ("age UNVERIFIED (not in snapshot, no first-mint verification) "
                                   "-> watchlist-only, NOT a lead, NEVER preview/mint; "
                                   "main-job follow-up pending")
da = reads.get("DragonAgents", {})
if da.get("freeClaimed") is not None and da.get("FREE_SUPPLY"):
    flags["DragonAgents_pct"] = round(da["freeClaimed"] / da["FREE_SUPPLY"] * 100, 1)
    flags["DragonAgents_totalSupply"] = da.get("totalSupply")
    flags["DragonAgents_mintedBy_user"] = da.get("mintedBy_user")
    flags["DragonAgents_decision"] = "age-excluded (>46 jam) -> bukan strong lead, moot, diam"
cr = reads.get("CRACE", {})
if cr.get("freeMinted") is not None and cr.get("FREE_QUOTA"):
    flags["CRACE_freeMinted"] = cr["freeMinted"]
    flags["CRACE_FREE_QUOTA"] = cr["FREE_QUOTA"]
    flags["CRACE_soldout"] = bool(cr["freeMinted"] >= cr["FREE_QUOTA"])
    flags["CRACE_slot_open"] = bool(cr.get("freeClaimed_user") == 0)
    flags["CRACE_totalSupply"] = cr.get("totalSupply")
    flags["CRACE_decision"] = "SELLOUT confirmed fresh; main-job-captured run 0509 - NO duplicate report"
ol = reads.get("OLIVER", {})
if ol.get("freeMinted") is not None and ol.get("FREE_MAX"):
    flags["OLIVER_pct"] = round(ol["freeMinted"] / ol["FREE_MAX"] * 100, 1)
    flags["OLIVER_freeRemaining"] = ol.get("freeRemaining")
    flags["OLIVER_decision"] = "age-excluded 21:00 13 Nov, already reported - LOG ONLY"
ba = reads.get("binanceai-mint", {})
flags["binanceai_launched"] = ba.get("launched")
flags["binanceai_failed"] = ba.get("failed")
flags["binanceai_refundPhase"] = ba.get("isRefundPhase")
flags["binanceai_tokenClaimed_user"] = ba.get("tokenClaimed_user")
flags["binanceai_decision"] = "still pending (launched=0, refund phase) - no change, no report" if ba.get("launched") == 0 else "CHANGED - review"
ae = reads.get("AngelEye-77D9", {})
if ae.get("freeMinted") is not None:
    flags["AngelEye77D9_freeMinted"] = ae["freeMinted"]
    flags["AngelEye77D9_freeRemaining"] = ae.get("freeRemaining")
    flags["AngelEye77D9_FREE_POOL"] = ae.get("FREE_POOL")
    flags["AngelEye77D9_saleActive"] = ae.get("saleActive")
    flags["AngelEye77D9_mintStart"] = ae.get("mintStart")
    flags["AngelEye77D9_note"] = "age/pool/slot UNVERIFIED - watchlist-only, NOT a lead, NEVER preview/mint"
ab = reads.get("AbsurdAgentNFT", {})
flags["AbsurdAgentNFT_totalMinted"] = ab.get("totalMinted")
flags["AbsurdAgentNFT_mintOpen"] = ab.get("mintOpen")
flags["AbsurdAgentNFT_mintStartTime"] = ab.get("mintStartTime")
flags["AbsurdAgentNFT_note"] = "pre-launch (mintStartTime 1794650400 = 17:00 WIB 14 Nov) - watchlist-only"
az = reads.get("AZEN", {})
if az.get("totalSupply") is not None:
    flags["AZEN_totalSupply"] = az["totalSupply"]
    flags["AZEN_MAX_SUPPLY"] = az.get("MAX_SUPPLY")
    flags["AZEN_freeMintedPerWallet_user"] = az.get("freeMintedPerWallet_user")
    flags["AZEN_note"] = "ERC-721 agent-shaped free-mint NFT; NOT literal S1/S2; NFT early-lead stays with main 30-min job"
nr = reads.get("NovaRemnants", {})
flags["NovaRemnants_totalRemnants"] = nr.get("totalRemnants")
flags["NovaRemnants_genesisOpen"] = nr.get("genesisOpen")
flags["NovaRemnants_currentCycle"] = nr.get("currentCycle")
ra = reads.get("RaceAgents", {})
if ra.get("freeMinted") is not None and ra.get("FREE_MAX"):
    flags["RaceAgents_pct"] = round(ra["freeMinted"] / ra["FREE_MAX"] * 100, 1)
    flags["RaceAgents_totalSupply"] = ra.get("totalSupply")
    flags["RaceAgents_mintOpen"] = ra.get("mintOpen")
ac = reads.get("ACARD", {})
if ac:
    flags["ACARD_freeMinted"] = ac.get("freeMinted")
    flags["ACARD_FREE_CAP"] = ac.get("FREE_CAP")
    flags["ACARD_totalMinted"] = ac.get("totalMinted")
    flags["ACARD_mintOpen"] = ac.get("mintOpen")
    flags["ACARD_freeClaimed_user"] = ac.get("freeClaimed_user")
    flags["ACARD_shape"] = "S1-literal-pass BUT ERC-721 NFT, NOT a track-C lead; NFT early-lead stays with main job"
aw = reads.get("ARCADEWARDEN", {})
flags["ARCADEWARDEN_probe"] = {k: v for k, v in aw.items()}
flags["ARCADEWARDEN_decision"] = ("probe hits present - needs ABI/shape follow-up by main job; NOT a lead this run (no registry/agent evidence, no age/website)"
                                   if any(v is not None for v in aw.values()) else
                                   "probe no hits - NOT sale-shape, stays seen shape-check-failed")
na = reads.get("NovaAgent", {})
flags["NovaAgent_probe"] = {k: v for k, v in na.items()}
flags["NovaAgent_decision"] = ("probe hits present - Sourcify still UNVERIFIED, no agent/registry evidence; NOT a lead, main job follow-up"
                               if any(v is not None for v in na.values()) else
                               "probe no hits - NOT sale-shape, stays seen")
for r in shapes:
    flags[f"NEW_{r['address'][:8]}"] = (f"S1={r.get('S1')} S2={r.get('S2')} status={r.get('status')} "
                                        f"mint={r.get('has_mint')} quote={r.get('has_quote')} "
                                        f"free={r.get('free_views')} agent={r.get('agent_ref')} "
                                        f"token={r.get('is_token')} "
                                        f"AGENT_ID_is_registry={r.get('AGENT_ID_is_registry')} err={r.get('error')}")
    if r.get("S1") or r.get("S2"):
        flags[f"NEW_{r['address'][:8]}_decision"] = "SALE-SHAPE PASS - needs on-chain free-pool/slot/age verify + website gate before any lead report; handled by main job if not promoted here"
    elif r.get("AGENT_ID_is_registry"):
        flags[f"NEW_{r['address'][:8]}_decision"] = "NOT literal S1/S2 BUT AGENT_ID()=registry exact -> agent-shaped variant (0609 lesson); age UNVERIFIED -> watchlist-only, main-job follow-up"
    else:
        flags[f"NEW_{r['address'][:8]}_decision"] = "NOT sale-shape (or shape-check-failed) - recorded in seen only, NOT a lead, no report"
flags["Agentx"] = "thread CLOSED (user tolak override 13 Nov) - NO re-check, NO report, NEVER preview/mint."
out["flags"] = flags
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-14-0614.json", "w"), indent=1)

# --- update hot-leg-seen.json with newly seen contracts ---
try:
    seen2 = json.load(open(f"{HF}/hot-leg-seen.json"))
except Exception:
    seen2 = {}
now_iso = now_wib()
for a, v in to_shape:
    if a not in seen2:
        seen2[a] = {"first_seen": now_iso, "source": "hot-leg 0614 " + str(v)}
for tag in ("boltbook_en", "boltbook_zh"):
    for a in out[tag].get("new_contracts", []) or []:
        if a not in seen2:
            seen2[a] = {"first_seen": now_iso, "source": "hot-leg 0614 " + tag}
for a, note in ((KICKS, "hot-leg 0614 re-read"),
                (WANGCAI, "hot-leg 0614 re-read"),
                (YUANBAO, "hot-leg 0614 re-read")):
    if a in seen2 and isinstance(seen2[a], dict):
        seen2[a]["last_seen_0614"] = now_iso
json.dump(seen2, open(f"{HF}/hot-leg-seen.json", "w"))
out["seen_updated_n"] = len(seen2)
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-14-0614.json", "w"), indent=1)
print(json.dumps(out, indent=1))
