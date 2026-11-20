#!/usr/bin/env python3
"""free-mint-hot-leg run 2026-11-18 18:39 WIB. Legs 1-4 + bridge, read-only.
Adapted from hot-leg-2026-11-18-1819-run.py. Differences: leg3 threaded
(6 workers, 12s timeout each) to avoid sequential-stall timeouts that
killed the 18:19 leg3; leg4 via direct bsc-dataseed batches of 5 (worked
in the 18:31 main job: 57/59 chunks OK) instead of Quicknode tunnel
(3/6 chunks timed out at 18:19). Prev values from 18:31 main-job reread
(block 134305159) where available, else 18:19 run prevs.
Writes hot-leg-run-2026-11-18-1839.json + -reread.json; updates
hot-leg-seen.json ONLY. Never writes the main snapshot."""
import json, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
assert len(REGISTRY[2:]) == 40, "registry literal wrong length"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
RPC_URL = "https://bsc-dataseed.binance.org/"

def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def encode(sig, arg):
    d = "0x" + sel(sig)
    if arg == "user": d += enc_addr(USER)
    elif arg == "one": d += "%064x" % 1
    elif arg == "user1": d += enc_addr(USER) + "%064x" % 1
    return d

def rpc_batch(calls, timeout=20):
    payload = [{"jsonrpc": "2.0", "id": i+1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    req = urllib.request.Request(RPC_URL, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode())
    if not isinstance(data, list):
        raise IOError(f"non-list batch response: {str(data)[:150]}")
    by = {it["id"]: it for it in data if isinstance(it, dict)}
    out = []
    for i in range(len(calls)):
        it = by.get(i+1, {})
        if "result" in it and it["result"] not in (None, "0x"):
            try: out.append(int(it["result"], 16))
            except Exception: out.append(it["result"])
        elif "error" in it: out.append(f"err:{it['error']}")
        else: out.append(None)
    return out

def rpc_chunked(calls, chunk=5):
    out = []; errs = []
    for i in range(0, len(calls), chunk):
        part = calls[i:i+chunk]
        try:
            out += rpc_batch(part)
        except Exception as e:
            try:
                out += rpc_batch(part)
            except Exception as e2:
                errs.append(f"calls {i}-{i+len(part)-1}: {type(e2).__name__}: {str(e2)[:120]}")
                out += [None]*len(part)
    return out, errs

seen = json.load(open(f"{HF}/hot-leg-seen.json")); seen_l = {k.lower() for k in seen}
out = {"run": "free-mint-hot-leg 2026-11-18 18:39 WIB", "started_wib": now_wib,
       "transport": "Sourcify feed + Boltbook EN/ZH via direct curl (200); leg3 threaded Sourcify ABI (6w, 12s); leg4 direct bsc-dataseed batches of 5"}

# Leg 1 Sourcify feed (already fetched direct, /tmp/hotleg1839_sourcify.json)
try:
    feed = json.load(open("/tmp/hotleg1839_sourcify.json"))
    items = feed.get("results", [])
    addrs = [(it.get("address"), it.get("verifiedAt")) for it in items if it.get("address")]
    new1 = [(a, v) for a, v in addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED]
    out["leg1_sourcify"] = {"http": 200, "total": len(addrs), "new": len(new1),
        "new_contracts": [a for a, _ in new1],
        "verified_window": [addrs[-1][1] if addrs else None, addrs[0][1] if addrs else None]}
except Exception as e:
    out["leg1_sourcify"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}; new1 = []

# Leg 2 Boltbook EN+ZH (already fetched direct)
def boltbook(lang, src):
    html = open(src, encoding="utf-8", errors="replace").read()
    open(f"{HF}/hot-leg-2026-11-18-1839-boltbook-{lang}.html", "w", encoding="utf-8").write(html)
    addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    new = [a for a in addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED and a.lower() != REGISTRY.lower()]
    return {"bytes": len(html), "http_code": 200, "addresses": len(addrs),
            "new": len(new), "new_contracts": new,
            "free_kw": len(re.findall(r"free", html, re.I)),
            "zh_free_kw": len(re.findall("免费", html))}
for lang, src in (("en", "/tmp/bb1839_en.html"), ("zh", "/tmp/bb1839_zh.html")):
    try: out[f"leg2_boltbook_{lang}"] = boltbook(lang, src)
    except Exception as e: out[f"leg2_boltbook_{lang}"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# Leg 3 shape-check new contracts (threaded Sourcify ABI fetch, 12s each)
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
def shape_check(addr):
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata",
                                     headers={"User-Agent": "muse-hotleg/1.0"})
        meta = json.load(urllib.request.urlopen(req, timeout=12))
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function": fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token,
                "n_fns": len(names), "status": "checked", "verifiedAt": meta.get("verifiedAt")}
    except Exception as e:
        return {"address": addr, "status": "shape-check-failed", "error": f"{type(e).__name__}: {str(e)[:120]}"}
targets = [a for a, _ in new1]
for lang in ("en", "zh"):
    targets += [a for a in out.get(f"leg2_boltbook_{lang}", {}).get("new_contracts", [])]
targets = list(dict.fromkeys(targets))
sc = []
with ThreadPoolExecutor(max_workers=6) as ex:
    futs = {ex.submit(shape_check, a): a for a in targets}
    for f in as_completed(futs):
        sc.append(f.result())
sc.sort(key=lambda s: targets.index(s["address"]))
out["leg3_shape_check"] = sc
out["leg3_sale_shape"] = [s for s in sc if s.get("S1") or s.get("S2")]
out["leg3_failed"] = [s["address"] for s in sc if s.get("status") == "shape-check-failed"]
seen_added = []
for s in sc:
    if s.get("status") != "checked": continue
    seen[s["address"]] = {"first_seen_wib": now_wib, "source": "sourcify-feed",
        "status": "sale-shape" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape",
        "note": json.dumps(s)[:600], "verifiedAt": s.get("verifiedAt")}
    seen_added.append(s["address"])
out["seen_added"] = seen_added; out["seen_n"] = len(seen)
json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)

# Leg 4 targeted re-read (prev = 18:31 main-job reread block 134305159, else 18:19 prevs)
PLAN = [
 ("DGF CARD","0x01f9CA4ff95d49594cC8B6591022186dc5C1Bc72",
  [("totalMinted","totalMinted()",None),("balanceOf_user","balanceOf(address)","user")]),
 ("BinanceAI","0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched","launched()",None),("failed","failed()",None),
   ("tokenClaimed_user","tokenClaimed(address)","user")]),
 ("AlphaPulse V1","0xE09Ab25732b1e1FdA7ad4d551EEA0aAC65aD0711",
  [("totalSupply","totalSupply()",None),("mintOpen","mintOpen()",None),
   ("balanceOf_user","balanceOf(address)","user")]),
 ("FABE","0xFabE022a5943462fee1Bd221791945DA57510BE8",
  [("freeSharesRemaining","freeSharesRemaining()",None),("launched","launched()",None),
   ("freeSharesClaimed_user","freeSharesClaimed(address)","user"),
   ("totalShares","totalShares()",None)]),
 ("PUNNY","0xaFAE0Bf373ad87E88555afe1605111F66C99062C",
  [("freeMinted","freeMinted()",None),("FREE_SUPPLY","FREE_SUPPLY()",None),
   ("totalMinted","totalMinted()",None),
   ("hasClaimedFree_user","hasClaimedFree(address)","user")]),
 ("STOCK AGENT","0xba7068233da805bdebcc167be361c219002e6b7f",
  [("totalSupply","totalSupply()",None),("freeLeft","freeLeft()",None),
   ("quote_user_1","quote(address,uint256)","user1"),
   ("freeMintedByWallet_user","freeMintedByWallet(address)","user"),
   ("balanceOf_user","balanceOf(address)","user")]),
]
calls = []; meta = []
for name, addr, views in PLAN:
    for label, sig, arg in views:
        calls.append((addr, encode(sig, arg))); meta.append((name, addr, label))
res, errs = rpc_chunked(calls, chunk=5)
reads = {}
for (name, addr, label), val in zip(meta, res):
    reads.setdefault(name, {"address": addr, "views": {}})["views"][label] = val
try:
    blk = rpc_batch.__wrapped__ if False else None
    req = urllib.request.Request(RPC_URL, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        block = int(json.loads(resp.read().decode())["result"], 16)
except Exception as e:
    block = f"error: {str(e)[:120]}"
reread = {"reads": reads, "errors": errs, "n_calls": len(calls),
          "elapsed_s": round(time.time()-T0, 1), "block": block, "started_wib": now_wib}
json.dump(reread, open(f"{HF}/hot-leg-run-2026-11-18-1839-reread.json", "w"), indent=1)
out["leg4_reread"] = {"block": block, "reads": {k: v["views"] for k, v in reads.items()}, "errors": errs}
# prev: 18:31 main-job reread (DGF 1652, PUNNY 362/362, STOCK 777/334) + 17:44 prevs for the rest
prev = {"DGF CARD totalMinted": 1652, "BinanceAI launched()": 0, "BinanceAI failed()": 1, "AlphaPulse V1 totalSupply": 34,
        "FABE freeSharesRemaining": 2821, "PUNNY freeMinted": 362, "PUNNY totalMinted": 362,
        "STOCK AGENT totalSupply": 777, "STOCK AGENT freeLeft": 334}
cur = {"DGF CARD totalMinted": reads["DGF CARD"]["views"].get("totalMinted"),
       "BinanceAI launched()": reads["BinanceAI"]["views"].get("launched"),
       "BinanceAI failed()": reads["BinanceAI"]["views"].get("failed"),
       "AlphaPulse V1 totalSupply": reads["AlphaPulse V1"]["views"].get("totalSupply"),
       "FABE freeSharesRemaining": reads["FABE"]["views"].get("freeSharesRemaining"),
       "PUNNY freeMinted": reads["PUNNY"]["views"].get("freeMinted"),
       "PUNNY totalMinted": reads["PUNNY"]["views"].get("totalMinted"),
       "STOCK AGENT totalSupply": reads["STOCK AGENT"]["views"].get("totalSupply"),
       "STOCK AGENT freeLeft": reads["STOCK AGENT"]["views"].get("freeLeft")}
out["leg4_changes"] = {k: {"prev": prev[k], "now": cur[k]} for k in prev if prev[k] != cur[k]}
pu = reads["PUNNY"]["views"]; st = reads["STOCK AGENT"]["views"]
punny_pct = (pu.get("freeMinted")/pu.get("FREE_SUPPLY")*100) if isinstance(pu.get("freeMinted"), int) and isinstance(pu.get("FREE_SUPPLY"), int) and pu.get("FREE_SUPPLY") else None
stock_pct = (st.get("totalSupply")/1111*100) if isinstance(st.get("totalSupply"), int) else None
age_min = (datetime.now(timezone.utc) - datetime(2026,11,17,13,32,tzinfo=timezone.utc)).total_seconds()/60
out["leg4_promotion_check"] = {
 "PUNNY_free_pct": round(punny_pct,2) if punny_pct is not None else None,
 "PUNNY_age_min_since_mintStart": round(age_min,1),
 "PUNNY_note": "mintStart 2026-11-17 20:32 WIB; age <24h until 20:32 WIB today; website gate UNVERIFIED -> no promotion even if pct crossed; pct must be >70% for strong lead.",
 "STOCK_free_pct_inferred": round(stock_pct,2) if stock_pct is not None else None,
 "STOCK_note": "age UNVERIFIED + website gate UNVERIFIED -> no promotion even if pct crossed 70%; inferred free% = totalSupply/1111 (freeLeft cross-check).",
 "DGF_note": "age + free% still unverified (no promotion); website verified but that alone is not a tier."}
out["leg4_note"] = ("No sellout, slot loss, age-exclusion, claim opening, or tier promotion "
  "unless leg4_changes shows a qualifying state change.")

# Bridge read-only
try:
    bridge = json.load(open(f"{HF}/scan-bridge.json")); contracts = bridge.get("contracts", {})
    snap = json.load(open(f"{HF}/onchain-snapshot.json")); snap_addrs = set()
    for coll in ("contracts", "track_c"):
        for k, v in snap.get(coll, {}).items():
            if isinstance(v, dict):
                for f in ("address", "sale", "token", "mint"):
                    if v.get(f): snap_addrs.add(str(v[f]).lower())
    for k, v in snap.get("pending_claims", {}).items():
        if isinstance(v, dict):
            for f in ("mint", "token"):
                if v.get(f): snap_addrs.add(str(v[f]).lower())
    not_in = [a for a in contracts if a.lower() not in snap_addrs]
    disc = sum(1 for v in contracts.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
    out["bridge"] = {"total": len(contracts), "not_in_snapshot": len(not_in),
                     "not_in_snapshot_list": not_in,
                     "same_owner_discarded": disc,
                     "note": "bridge contracts not in snapshot are not reported as new; no bridge promotion/change unless leg4 shows one."}
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:150]}", "note": "bridge skip - run continues"}

out["elapsed_s"] = round(time.time()-T0, 1)
out["executions"] = "none - no preview, no mint, no claim (read-only run)"
reportable = bool(out["leg3_sale_shape"]) or any(
    (k in out["leg4_changes"] and out["leg4_changes"][k]["now"] is not None)
    for k in ("BinanceAI launched()", "FABE freeSharesRemaining"))
out["result"] = ("CHANGES FOUND - see leg3/leg4" if reportable else
  "SILENT - no new lead, candidate, pending claim, change, or blocked auto-mint/auto-claim.")
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-18-1839.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:14000])
