#!/usr/bin/env python3
"""free-mint-hot-leg run 2026-11-18 22:04 WIB. Legs 1-4 + bridge, read-only.
Adapted from hot-leg-2026-11-18-2159-run.py. Prevs = last GOOD reads (21:54;
21:59 leg4 fully FAILED - transport, all 22 calls null, block errored).
AGENTONE freeMinted 10000 (SELLOUT already REPORTED at the 21:34 run - do
not re-report). No shape-check carryover (0 failed at 21:59).
PUNNY age-exclusion ALREADY REPORTED once at the 20:34 run - do not re-report.
STOCK 70% crossing already reported at the 18:44 run - do not re-report.
Change detection skips null current reads (read failure, not a change).
Writes hot-leg-run-2026-11-18-2204.json + -reread.json; updates
hot-leg-seen.json ONLY for checked contracts. Never writes the main snapshot."""
import json, re, subprocess, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from keccak_pure import keccak256 as _k256  # pure-python fallback: eth_hash backend (pycryptodome/pysha3) NOT installed in this env; keccak_pure self-tests vectors on import

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
assert len(REGISTRY[2:]) == 40, "registry literal wrong length"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
RETRY_2154 = []  # 21:59 resolved all 7 carryovers clean; 0 shape-check failures carried forward
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
RPC_URL = "https://bsc-dataseed.binance.org/"

def sel(sig): return _k256(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def encode(sig, arg):
    d = "0x" + sel(sig)
    if arg == "user": d += enc_addr(USER)
    elif arg == "one": d += "%064x" % 1
    elif arg == "user1": d += enc_addr(USER) + "%064x" % 1
    return d

def rpc_batch(calls, timeout=10):
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
            errs.append(f"calls {i}-{i+len(part)-1}: {type(e).__name__}: {str(e)[:120]}")
            out += [None]*len(part)
    return out, errs

def curl_get(url, timeout=10):
    p = subprocess.run(["curl", "-sS", "--max-time", str(timeout), "-A", "muse-hotleg/1.0",
                        "-L", url], capture_output=True, timeout=timeout + 5)
    if p.returncode != 0:
        raise IOError(f"curl rc={p.returncode}: {p.stderr.decode(errors='replace')[:120]}")
    return p.stdout

seen = json.load(open(f"{HF}/hot-leg-seen.json")); seen_l = {k.lower() for k in seen}
out = {"run": "free-mint-hot-leg 2026-11-18 22:04 WIB", "started_wib": now_wib,
       "transport": "Sourcify feed + Boltbook EN/ZH via curl (10s); leg3 Sourcify ABI via curl threaded (10w, 10s); leg4 direct bsc-dataseed batches of 5"}

# Leg 1 Sourcify feed
new1 = []
try:
    feed = json.loads(curl_get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc").decode())
    items = feed.get("results", [])
    addrs = [(it.get("address"), it.get("verifiedAt")) for it in items if it.get("address")]
    new1 = [(a, v) for a, v in addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED]
    out["leg1_sourcify"] = {"http": 200, "total": len(addrs), "new": len(new1),
        "new_contracts": [a for a, _ in new1],
        "verified_window": [addrs[-1][1] if addrs else None, addrs[0][1] if addrs else None]}
except Exception as e:
    out["leg1_sourcify"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# Leg 2 Boltbook EN+ZH
def boltbook(lang, url):
    html = curl_get(url).decode("utf-8", errors="replace")
    open(f"{HF}/hot-leg-2026-11-18-2204-boltbook-{lang}.html", "w", encoding="utf-8").write(html)
    addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    new = [a for a in addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED and a.lower() != REGISTRY.lower()]
    return {"bytes": len(html), "http_code": 200, "addresses": len(addrs),
            "new": len(new), "new_contracts": new,
            "free_kw": len(re.findall(r"free", html, re.I)),
            "zh_free_kw": len(re.findall("免费", html))}
for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
    try: out[f"leg2_boltbook_{lang}"] = boltbook(lang, url)
    except Exception as e: out[f"leg2_boltbook_{lang}"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# Leg 3 shape-check via curl (transport fix from 21:14)
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
def shape_check(addr):
    try:
        p = subprocess.run(["curl", "-sS", "--max-time", "10", "-A", "muse-hotleg/1.0",
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata"],
            capture_output=True, timeout=15)
        if p.returncode != 0:
            return {"address": addr, "status": "shape-check-failed",
                    "error": f"curl rc={p.returncode}: {p.stderr.decode(errors='replace')[:100]}"}
        meta = json.loads(p.stdout.decode())
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
targets += [a for a in RETRY_2154 if a.lower() not in seen_l]
targets = list(dict.fromkeys(targets))
sc = []
if time.time() - T0 < 100:
    with ThreadPoolExecutor(max_workers=10) as ex:
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
    # Persist partial progress now so legs 1-3 survive a later crash.
    out["partial"] = True
    json.dump(out, open(f"{HF}/hot-leg-run-2026-11-18-2204.json", "w"), indent=1)
else:
    out["leg3_shape_check"] = {"skipped": "over budget before leg3", "targets": targets}

# Leg 4 targeted re-read (prevs = last good reads 21:54; AGENTONE 10000, sellout reported 21:34)
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
 ("AGENTONE","0x84D82E933D7781fe11245e7bbd3Eb23dbb963666",
  [("freeMinted","freeMinted()",None)]),
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
    req = urllib.request.Request(RPC_URL, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        block = int(json.loads(resp.read().decode())["result"], 16)
except Exception as e:
    block = f"error: {str(e)[:120]}"
reread = {"reads": reads, "errors": errs, "n_calls": len(calls),
          "elapsed_s": round(time.time()-T0, 1), "block": block, "started_wib": now_wib}
json.dump(reread, open(f"{HF}/hot-leg-run-2026-11-18-2204-reread.json", "w"), indent=1)
out["leg4_reread"] = {"block": block, "reads": {k: v["views"] for k, v in reads.items()}, "errors": errs}
prev = {"DGF CARD totalMinted": 1676, "BinanceAI launched()": 0, "BinanceAI failed()": 1, "AlphaPulse V1 totalSupply": 34,
        "FABE freeSharesRemaining": 2821, "PUNNY freeMinted": 379, "PUNNY totalMinted": 379,
        "STOCK AGENT totalSupply": 801, "STOCK AGENT freeLeft": 310, "AGENTONE freeMinted": 10000}
cur = {"DGF CARD totalMinted": reads["DGF CARD"]["views"].get("totalMinted"),
       "BinanceAI launched()": reads["BinanceAI"]["views"].get("launched"),
       "BinanceAI failed()": reads["BinanceAI"]["views"].get("failed"),
       "AlphaPulse V1 totalSupply": reads["AlphaPulse V1"]["views"].get("totalSupply"),
       "FABE freeSharesRemaining": reads["FABE"]["views"].get("freeSharesRemaining"),
       "PUNNY freeMinted": reads["PUNNY"]["views"].get("freeMinted"),
       "PUNNY totalMinted": reads["PUNNY"]["views"].get("totalMinted"),
       "STOCK AGENT totalSupply": reads["STOCK AGENT"]["views"].get("totalSupply"),
       "STOCK AGENT freeLeft": reads["STOCK AGENT"]["views"].get("freeLeft"),
       "AGENTONE freeMinted": reads["AGENTONE"]["views"].get("freeMinted")}
out["leg4_changes"] = {k: {"prev": prev[k], "now": cur[k]} for k in prev
                        if cur[k] is not None and prev[k] != cur[k]}
out["leg4_read_failures"] = [k for k in prev if cur[k] is None]
pu = reads["PUNNY"]["views"]; st = reads["STOCK AGENT"]["views"]; ag = reads["AGENTONE"]["views"]
punny_pct = (pu.get("freeMinted")/pu.get("FREE_SUPPLY")*100) if isinstance(pu.get("freeMinted"), int) and isinstance(pu.get("FREE_SUPPLY"), int) and pu.get("FREE_SUPPLY") else None
stock_pct = (st.get("totalSupply")/1111*100) if isinstance(st.get("totalSupply"), int) else None
aone_pct = (ag.get("freeMinted")/10000*100) if isinstance(ag.get("freeMinted"), int) else None
age_min = (datetime.now(timezone.utc) - datetime(2026,11,17,13,32,tzinfo=timezone.utc)).total_seconds()/60
out["leg4_promotion_check"] = {
 "PUNNY_free_pct": round(punny_pct,2) if punny_pct is not None else None,
 "PUNNY_age_min_since_mintStart": round(age_min,1),
 "PUNNY_note": "mintStart 2026-11-17 20:32 WIB; age-exclusion ALREADY REPORTED once at the 20:34 run - not re-reported; far below 70%, website gate UNVERIFIED -> no promotion either way.",
 "STOCK_free_pct_inferred": round(stock_pct,2) if stock_pct is not None else None,
 "STOCK_note": "crossed 70% already REPORTED at 18:44 run - no re-report; age UNVERIFIED + website gate UNVERIFIED -> still no strong-lead promotion; inferred free% = totalSupply/1111 (freeLeft cross-check).",
 "AGENTONE_free_pct": round(aone_pct,2) if aone_pct is not None else None,
 "AGENTONE_note": "minted by user 17:59 run (2 hero cards, quota used); SELLOUT 10000/10000 already REPORTED at 21:34 run - no re-report; pool tracking only. FREE_TOTAL 10000.",
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
reportable = bool(out.get("leg3_sale_shape")) or any(
    (k in out["leg4_changes"] and out["leg4_changes"][k]["now"] is not None)
    for k in ("BinanceAI launched()", "FABE freeSharesRemaining"))
out["result"] = ("CHANGES FOUND - see leg3/leg4" if reportable else
  "SILENT - no new lead, candidate, pending claim, change, or blocked auto-mint/auto-claim.")
out.pop("partial", None)
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-18-2204.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:14000])
