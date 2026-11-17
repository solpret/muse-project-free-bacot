#!/usr/bin/env python3
"""Hot-leg 16:34 retry: Sourcify feed (curl), Boltbook en/zh (curl),
leg4 retry for failed chunks 20/30 vs 16:31 baseline. Merges into
run-hot-leg-2026-11-15-1634.json. Read-only except that run log + seen."""
import json, time, re, subprocess
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124",
            "0x8b47354E7b76B1970a0D06365c8244a810d37493"}
t0 = time.time()
run = json.load(open(BASE + "run-hot-leg-2026-11-15-1634.json"))

def curl(url, timeout=30):
    try:
        out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url],
                             capture_output=True, text=True, timeout=timeout+10).stdout
        return out
    except Exception as e:
        return ""

# ---- Sourcify retry ----
raw = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc")
feed = []
try:
    parsed = json.loads(raw)
    feed = parsed.get("contracts", []) if isinstance(parsed, dict) else parsed
except Exception as e:
    pass
feed_addrs = [c.get("address") for c in feed if isinstance(c, dict) and c.get("address")]
run["sourcify_feed_retry"] = {"ok": bool(feed_addrs), "count": len(feed_addrs),
    "raw_head": raw[:200], "top": feed_addrs[0] if feed_addrs else None,
    "top_verifiedAt": feed[0].get("verifiedAt") if feed and isinstance(feed[0], dict) else None}

# ---- Boltbook retry ----
def bb(lang):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    body = curl(url)
    addrs = sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", body)))
    return {"ok": len(body) > 1000, "bytes": len(body), "addrs": addrs}
run["boltbook_en_retry"] = bb("en")
run["boltbook_zh_retry"] = bb("zh")

seen = json.load(open(BASE + "hot-leg-seen.json"))
def is_seen(a): return a.lower() in {k.lower() for k in seen}
new_feed = [a for a in feed_addrs if a and not is_seen(a) and a.lower() not in {e.lower() for e in EXCLUDED} and a.lower() != REGISTRY.lower()]
bb_addrs = sorted(set(run["boltbook_en_retry"]["addrs"] + run["boltbook_zh_retry"]["addrs"]))
new_bb = [a for a in bb_addrs if not is_seen(a) and a.lower() not in {e.lower() for e in EXCLUDED}]
targets = []
for a in new_feed + new_bb:
    if a not in targets: targets.append(a)
run["new_contracts_retry"] = {"sourcify": new_feed, "boltbook": new_bb, "targets": targets}

FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted"]
def shape_check(addr):
    raw3 = curl(f"https://sourcify.dev/server/v2/contracts/56/{addr}")
    try:
        meta = json.loads(raw3)
        abi = meta.get("abi") or meta.get("stdJson", {}).get("abi") or []
    except Exception as e:
        return {"address": addr, "status": "abi-fetch-failed", "error": str(e)[:120]}
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
shapes = [shape_check(a) for a in targets]
run["shape_check_retry"] = shapes
run["shape_hits_retry"] = [s for s in shapes if s.get("S1") or s.get("S2")]
for s in shapes:
    a = s["address"]
    if a not in seen:
        seen[a] = {"first_seen_wib": "2026-11-15T16:34+07:00",
                   "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')}",
                   "source": "hot-leg-1634-retry", "status": "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "sale-shape"}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Leg4 retry: chunks 20 and 30 (REOPIR, Matrix Agents, ORBIT) ----
base = json.load(open(BASE + "run-2026-11-15-1631-reread.json"))
base_reads = base["reads"]
NAMES = ["REOPIR", "Matrix Agents", "ORBIT"]
base3 = {n: base_reads[n] for n in NAMES if n in base_reads}
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
for name, it in base3.items():
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
                "params":[{"to": base3[c[0]]["address"], "data": c[2]}, "latest"]} for i,c in enumerate(chunk)]
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
            reads.setdefault(name, {"address": base3[name]["address"], "views": {}})["views"][vn] = val
        blk = by_id.get(len(chunk), {}).get("result")
        if blk: block = int(blk, 16)
    except Exception as ex:
        errors.append({"chunk": s, "error": f"{type(ex).__name__}: {str(ex)[:120]}"})
diffs = {}
for name, it in base3.items():
    now_views = reads.get(name, {}).get("views", {})
    for vn, bv in it["views"].items():
        if bv is None or vn.startswith("freeClaimedByAgent"): continue
        nv = now_views.get(vn)
        if nv is None:
            diffs.setdefault(name, {})[vn] = {"1631": bv, "now": None, "note": "read-failed-now"}
        elif nv != bv:
            diffs.setdefault(name, {})[vn] = {"1631": bv, "now": nv}
n_ok = sum(1 for it in reads.values() for v in it["views"].values() if v is not None)
run["leg4_retry"] = {"reads": reads, "block": block, "errors": errors,
                     "n_calls": len(calls), "n_ok": n_ok, "diffs_vs_1631": diffs,
                     "elapsed_s": round(time.time()-t0, 1)}
# merge retry reads into leg4 reads and recompute diffs
for name, it in reads.items():
    run["leg4"]["reads"].setdefault(name, {"address": it["address"], "views": {}}).update(it)
    for vn, val in it["views"].items():
        run["leg4"]["reads"][name]["views"][vn] = val
        if name in run["leg4"]["diffs_vs_1631"] and vn in run["leg4"]["diffs_vs_1631"][name]:
            bv = base_reads[name]["views"].get(vn)
            if val is None:
                run["leg4"]["diffs_vs_1631"][name][vn] = {"1631": bv, "now": None, "note": "read-failed-now"}
            elif val != bv:
                run["leg4"]["diffs_vs_1631"][name][vn] = {"1631": bv, "now": val}
            else:
                del run["leg4"]["diffs_vs_1631"][name][vn]
            if not run["leg4"]["diffs_vs_1631"][name]:
                del run["leg4"]["diffs_vs_1631"][name]
run["elapsed_s"] = round(run.get("elapsed_s", 0) + (time.time()-t0), 1)
json.dump(run, open(BASE + "run-hot-leg-2026-11-15-1634.json", "w"), indent=1)
print(json.dumps({"sourcify_retry": run["sourcify_feed_retry"],
    "boltbook_en": {k: run["boltbook_en_retry"][k] for k in ("ok","bytes")},
    "boltbook_zh": {k: run["boltbook_zh_retry"][k] for k in ("ok","bytes")},
    "new_retry": run["new_contracts_retry"], "shape_hits_retry": run["shape_hits_retry"],
    "leg4_retry": run["leg4_retry"], "merged_diffs": run["leg4"]["diffs_vs_1631"],
    "elapsed_s": run["elapsed_s"]}, indent=1))
