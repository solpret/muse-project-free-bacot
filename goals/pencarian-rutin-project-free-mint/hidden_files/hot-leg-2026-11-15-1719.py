#!/usr/bin/env python3
"""Hot-leg 16:44 WIB 2026-11-15: Sourcify feed + Boltbook en/zh + shape-check
new contracts + leg4 re-read of 11 active items vs main 16:31 baseline +
scan-bridge check. Read-only except hot-leg-seen.json (new entries only)
and this run log."""
import json, time, re, urllib.request, urllib.error, subprocess, os
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124",
            "0x8b47354E7b76B1970a0D06365c8244a810d37493"}
t0 = time.time()
run = {"run": "hot-leg 2026-11-15 17:19 WIB", "started_wib": "2026-11-15T17:19+07:00"}

def http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return True, r.read(), None
    except urllib.error.HTTPError as e:
        try: partial = e.read()
        except Exception: partial = b""
        return False, partial, f"HTTPError {e.code} ({len(partial)} bytes read)"
    except Exception as e:
        return False, b"", f"{type(e).__name__}: {str(e)[:120]}"

# ---- Leg 1: Sourcify feed ----
ok, data, err = http_get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc")
feed = []
if ok:
    try:
        parsed = json.loads(data)
        feed = (parsed.get("results") if isinstance(parsed, dict) and isinstance(parsed.get("results"), list) else (parsed.get("contracts") or [])) if isinstance(parsed, dict) else parsed
    except Exception as e:
        err = f"parse: {e}"
feed_addrs = [c.get("address") for c in feed if isinstance(c, dict) and c.get("address")]
run["sourcify_feed"] = {"ok": ok, "count": len(feed_addrs), "error": err,
    "top": feed_addrs[0] if feed_addrs else None,
    "top_verifiedAt": feed[0].get("verifiedAt") if feed and isinstance(feed[0], dict) else None}

# ---- Leg 2: Boltbook ----
def fetch_boltbook(lang):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    ok2, d2, e2 = http_get(url)
    if not ok2:
        ok2, d2, e2 = http_get(url)
        e2 = "retry: " + str(e2)
    addrs = sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", d2.decode("utf-8", "ignore")))) if d2 else []
    return {"ok": ok2, "bytes": len(d2), "error": e2,
            "full_address_contracts": len(addrs), "addrs": addrs}
run["boltbook_en"] = fetch_boltbook("en")
run["boltbook_zh"] = fetch_boltbook("zh")

# ---- seen / new ----
seen = json.load(open(BASE + "hot-leg-seen.json"))
def is_seen(a): return a.lower() in {k.lower() for k in seen}
new_feed = [a for a in feed_addrs if a and not is_seen(a) and a.lower() not in {e.lower() for e in EXCLUDED} and a.lower() != REGISTRY.lower()]
bb_addrs = sorted(set(run["boltbook_en"]["addrs"] + run["boltbook_zh"]["addrs"]))
new_bb = [a for a in bb_addrs if not is_seen(a) and a.lower() not in {e.lower() for e in EXCLUDED}]
targets = []
for a in new_feed + new_bb:
    if a not in targets: targets.append(a)
RETRY_FAILED = [a for a, v in seen.items() if isinstance(v, dict) and v.get("status") == "shape-check-failed" and str(v.get("first_seen_wib","")).startswith("2026-11-15")]
for a in RETRY_FAILED:
    if a not in targets: targets.append(a)
run["retry_shape_failed"] = RETRY_FAILED
run["new_contracts"] = {"sourcify": new_feed, "boltbook": new_bb, "targets": targets}

# ---- Leg 3: shape-check ----
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted"]
def shape_check(addr):
    ok3, d3, e3 = http_get(f"https://sourcify.dev/server/v2/contracts/56/{addr}")
    if not ok3:
        return {"address": addr, "status": "abi-fetch-failed", "error": e3}
    try:
        meta = json.loads(d3)
        abi = meta.get("abi") or meta.get("stdJson", {}).get("abi") or []
    except Exception as e:
        return {"address": addr, "status": "abi-parse-failed", "error": str(e)[:120]}
    fns = [f.get("name","") for f in abi if isinstance(f, dict) and f.get("type")=="function"]
    fnset = set(fns)
    has_mint = any(n.startswith("mint") for n in fnset)
    has_quote = any(("quote" in n.lower() or "cost" in n.lower() or "price" in n.lower()) for n in fnset)
    free_views = [v for v in FREE_VIEWS if v in fnset]
    agent_ref = any(("agent" in n.lower() or "AgentGate" in n or "registry" in n.lower()) for n in fnset) or REGISTRY.lower() in json.dumps(meta).lower()
    is_token = bool({"name","symbol","decimals","totalSupply"} <= fnset)
    s1 = has_mint and has_quote and bool(free_views) and agent_ref
    s2 = is_token and ("mintFree" in fnset) and bool({"freeClaimed","freeMinted"} & fnset) and bool({"FREE_SLOTS","FREE_SUPPLY"} & fnset) and agent_ref
    return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
            "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
            "is_token": is_token, "n_fns": len(fnset), "status": "checked",
            "verifiedAt": next((c.get("verifiedAt") for c in feed if isinstance(c, dict) and c.get("address","").lower()==addr.lower()), None)}
run["shape_check"] = [shape_check(a) for a in targets]
run["shape_hits"] = [s for s in run["shape_check"] if s.get("S1") or s.get("S2")]
now_wib = "2026-11-15T17:19+07:00"
for s in run["shape_check"]:
    a = s["address"]
    if a not in seen:
        seen[a] = {"first_seen_wib": now_wib,
                   "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')} err={s.get('error')}",
                   "source": "hot-leg-1719", "status": "shape-check-failed" if s.get("status") in ("abi-fetch-failed", "abi-parse-failed") else ("sale-shape" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape")}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Leg 4: re-read 11 active items vs main 16:31 baseline ----
base = json.load(open(BASE + "run-hot-leg-2026-11-15-1719.json"))
base_reads = base["leg4"]["reads"]
NAMES11 = ["AGCLUB","Ledgera","RAVE","REOPIR","Matrix Agents","ORBIT",
           "BinanceAI-mint","RigForge","RaceAgents","Pengu","Zephyra"]
base11 = {n: base_reads[n] for n in NAMES11 if n in base_reads}
NOARG = {"totalSupply","totalMinted","freeMinted","freeClaimed","FREE_SUPPLY","FREE_CAP",
         "FREE_MAX","FREE_MINT_CAP","MAX_SUPPLY","maxSupply","mintOpen","launched","failed",
         "isRefundPhase","totalShares","remainingSupply","standardRemaining","legendaryRemaining",
         "paused","TOKEN_PRICE","claimOpen","mintStartTime","AGENT_ID","freeSharesLeft",
         "openedAt","freeBlock","mintOpenTimestamp","mintPaused","price","PRICE","mintPrice",
         "paidMinted","totalSpecimens","currentExperiment","genesisStart","genesisOpen",
         "mintsLeft","freeMintsLeft","freeRemaining","owner"}
ADDRARG = {"balanceOf","freeClaimedOf","freeUsed","mintedBy","mintedByWallet",
           "freeMintedPerWallet","mintedPerWallet","mintCountOf","mintsBy","holdsAgentId",
           "hasAgentId","isEligible","tokenClaimed","freeBooked","hasFreeClaimed"}
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
calls = []
for name, it in base11.items():
    for vn, bv in it["views"].items():
        if bv is None or vn.startswith("freeClaimedByAgent"): continue
        if vn == "priceFor_user_1":
            calls.append((name, vn, sel("priceFor(address,uint256)") + enc_addr(USER) + enc_u(1)))
        elif vn.endswith("_user"):
            fn = vn[:-5]
            if fn in ADDRARG or fn == "freeClaimed":
                calls.append((name, vn, sel(f"{fn}(address)") + enc_addr(USER)))
        elif vn in NOARG:
            calls.append((name, vn, sel(f"{vn}()")))
        elif vn in ADDRARG:
            calls.append((name, vn, sel(f"{vn}(address)") + enc_addr(USER)))
reads, block, errors = {}, None, []
CH = 10
for s in range(0, len(calls), CH):
    chunk = calls[s:s+CH]
    payload = [{"jsonrpc":"2.0","id":i,"method":"eth_call",
                "params":[{"to": base11[c[0]]["address"], "data": c[2]}, "latest"]} for i,c in enumerate(chunk)]
    payload.append({"jsonrpc":"2.0","id":len(chunk),"method":"eth_blockNumber","params":[]})
    try:
        out = subprocess.run(["curl","-sL","--max-time","30","-X","POST",
                              "https://bsc-dataseed.binance.org/",
                              "-H","Content-Type: application/json",
                              "-d", json.dumps(payload)], capture_output=True, text=True, timeout=40).stdout
        resp = json.loads(out)
        if not isinstance(resp, list):
            errors.append({"chunk": s, "resp": str(resp)[:200]}); continue
        by_id = {r.get("id"): r for r in resp}
        for i,(name,vn,_d) in enumerate(chunk):
            r = by_id.get(i, {})
            val = to_int(r.get("result")) if r.get("result") else None
            reads.setdefault(name, {"address": base11[name]["address"], "views": {}})["views"][vn] = val
        blk = by_id.get(len(chunk), {}).get("result")
        if blk: block = int(blk, 16)
    except Exception as ex:
        errors.append({"chunk": s, "error": f"{type(ex).__name__}: {str(ex)[:120]}"})
# retry failed chunks once (same payloads)
failed_chunks = [e["chunk"] for e in errors if "chunk" in e]
for s in failed_chunks:
    chunk = calls[s:s+CH]
    payload = [{"jsonrpc":"2.0","id":i,"method":"eth_call",
                "params":[{"to": base11[c[0]]["address"], "data": c[2]}, "latest"]} for i,c in enumerate(chunk)]
    payload.append({"jsonrpc":"2.0","id":len(chunk),"method":"eth_blockNumber","params":[]})
    try:
        out = subprocess.run(["curl","-sL","--max-time","30","-X","POST",
                              "https://bsc-dataseed.binance.org/",
                              "-H","Content-Type: application/json",
                              "-d", json.dumps(payload)], capture_output=True, text=True, timeout=40).stdout
        resp = json.loads(out)
        if not isinstance(resp, list):
            errors.append({"chunk": s, "retry": "bad-resp"}); continue
        by_id = {r.get("id"): r for r in resp}
        for i,(name,vn,_d) in enumerate(chunk):
            r = by_id.get(i, {})
            val = to_int(r.get("result")) if r.get("result") else None
            reads.setdefault(name, {"address": base11[name]["address"], "views": {}})["views"][vn] = val
        blk = by_id.get(len(chunk), {}).get("result")
        if blk: block = int(blk, 16)
        errors[:] = [e for e in errors if e.get("chunk") != s]
        run_retry_ok = True
    except Exception as ex:
        errors.append({"chunk": s, "retry_error": f"{type(ex).__name__}: {str(ex)[:120]}"})
diffs = {}
for name, it in base11.items():
    now_views = reads.get(name, {}).get("views", {})
    for vn, bv in it["views"].items():
        if bv is None or vn.startswith("freeClaimedByAgent"): continue
        nv = now_views.get(vn)
        if nv is None:
            diffs.setdefault(name, {})[vn] = {"1704": bv, "now": None, "note": "read-failed-now"}
        elif nv != bv:
            diffs.setdefault(name, {})[vn] = {"1704": bv, "now": nv}
n_ok = sum(1 for it in reads.values() for v in it["views"].values() if v is not None)
run["leg4"] = {"ok": len(errors)==0 and n_ok>0, "reads": reads, "block": block,
               "errors": errors, "n_calls": len(calls), "n_ok": n_ok,
               "base": "run-hot-leg-2026-11-15-1719.json", "diffs_vs_1719": diffs}

# ---- Bridge (read-only) ----
try:
    br = json.load(open(BASE + "scan-bridge.json"))
    cons = br.get("contracts", {})
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for sec in ("contracts","track_c","pending_claims"):
        for v in snap.get(sec, {}).values():
            if isinstance(v, dict) and v.get("address"): snap_addrs.add(v["address"].lower())
    not_in_snap = [a for a in cons if a.lower() not in snap_addrs]
    sod = [a for a,c in cons.items() if c.get("same_owner_discarded")]
    run["bridge"] = {"ok": True, "total": len(cons), "not_in_snapshot": not_in_snap,
                     "same_owner_discarded": len(sod)}
except Exception as e:
    run["bridge"] = {"ok": False, "error": f"{type(e).__name__}: {str(e)[:120]}"}
run["elapsed_s"] = round(time.time() - t0, 1)
json.dump(run, open(BASE + "run-hot-leg-2026-11-15-1719.json", "w"), indent=1)
print(json.dumps(run, indent=1))
