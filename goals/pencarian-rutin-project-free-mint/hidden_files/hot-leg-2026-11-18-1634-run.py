#!/usr/bin/env python3
"""free-mint-hot-leg run 2026-11-18 16:34 WIB. Legs 1-4 + bridge, read-only.
Adapted from hot-leg-2026-11-18-1629-run.py, but all network goes through the
VM egress-proxy CONNECT tunnel (ProxyHTTPSConnection from quicknode.py):
curl/direct egress was dead at 16:29-16:34 (Sourcify http 000, dataseed
http 000, Boltbook 302/0 bytes), while Quicknode via the tunnel returned
block 0x801150d at 16:35. RPC reads go to Quicknode (batch eth_call,
chunk <=5); Sourcify/Boltbook GETs go through the same tunnel class.
Writes hot-leg-run-2026-11-18-1634.json + -reread.json; updates
hot-leg-seen.json ONLY. Never writes the main snapshot."""
import json, re, sys, time
from datetime import datetime, timezone, timedelta
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
from eth_hash.auto import keccak
from quicknode import ProxyHTTPSConnection
from dynamic_credentials import dynamic_credential_entry

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
assert len(REGISTRY[2:]) == 40, "registry literal wrong length"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
QN_HOST = "stylish-thrilling-star.bsc.quiknode.pro"

def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def encode(sig, arg):
    d = "0x" + sel(sig)
    if arg == "user": d += enc_addr(USER)
    elif arg == "one": d += "%064x" % 1
    elif arg == "user1": d += enc_addr(USER) + "%064x" % 1
    return d

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"

def https_get(host, path, timeout=20, redirects=3):
    conn = ProxyHTTPSConnection(host, 443, timeout=timeout)
    try:
        conn.request("GET", path, headers={"User-Agent": UA, "Accept": "*/*"})
        resp = conn.getresponse()
        raw = resp.read(); status = resp.status
        loc = resp.getheader("Location")
    finally:
        conn.close()
    if status in (301, 302, 303, 307, 308) and loc and redirects > 0:
        if loc.startswith("http"):
            from urllib.parse import urlparse
            u = urlparse(loc)
            return https_get(u.hostname, u.path + ("?" + u.query if u.query else ""), timeout, redirects-1)
        return https_get(host, loc, timeout, redirects-1)
    return status, raw

def qn_batch(calls, timeout=25):
    entry = dynamic_credential_entry("custom.quicknode")
    surrogate = str(entry["surrogate"]).strip()
    assert surrogate.startswith("hsurr:"), "non-surrogate credential"
    path = f"/{surrogate}/"  # raw surrogate on purpose; never log
    payload = [{"jsonrpc": "2.0", "id": i+1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    conn = ProxyHTTPSConnection(QN_HOST, 443, timeout=timeout)
    try:
        conn.request("POST", path, body=json.dumps(payload).encode(),
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        raw = resp.read(); status = resp.status
    finally:
        conn.close()
    if status != 200:
        raise IOError(f"quicknode http {status}: {raw[:150]!r}")
    data = json.loads(raw.decode())
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
        try: out += qn_batch(calls[i:i+chunk])
        except Exception as e:
            errs.append(f"calls {i}-{i+len(calls[i:i+chunk])-1}: {type(e).__name__}: {str(e)[:150]}")
            out += [None]*len(calls[i:i+chunk])
    return out, errs

seen = json.load(open(f"{HF}/hot-leg-seen.json")); seen_l = {k.lower() for k in seen}
out = {"run": "free-mint-hot-leg 2026-11-18 16:34 WIB", "started_wib": now_wib,
       "transport": "egress-proxy CONNECT tunnel (quicknode ProxyHTTPSConnection); direct curl dead at 16:34 probe"}

# Leg 1 Sourcify feed
try:
    status, raw = https_get("sourcify.dev", "/server/v2/contracts/56?limit=20&sort=desc", timeout=20)
    feed = json.loads(raw.decode())
    items = feed if isinstance(feed, list) else feed.get("results", feed.get("contracts", []))
    addrs = []
    for it in items:
        a = it.get("address") or (it.get("contract") or {}).get("address")
        if a: addrs.append((a, it.get("verifiedAt")))
    new1 = [(a, v) for a, v in addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED]
    out["leg1_sourcify"] = {"http": status, "total": len(addrs), "new": len(new1),
        "new_contracts": [a for a, _ in new1],
        "verified_window": [addrs[-1][1] if addrs else None, addrs[0][1] if addrs else None]}
except Exception as e:
    out["leg1_sourcify"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}; new1 = []

# Leg 2 Boltbook EN+ZH
def boltbook(lang):
    path = f"/" + ("?lang=zh" if lang == "zh" else "")
    html = ""; code = None
    for _try in range(2):
        code, raw = https_get("boltbook.fun", path, timeout=15)
        html = raw.decode("utf-8", errors="replace")
        if len(html) > 1000: break
    open(f"{HF}/hot-leg-2026-11-18-1634-boltbook-{lang}.html", "w", encoding="utf-8").write(html)
    addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    new = [a for a in addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED and a.lower() != REGISTRY.lower()]
    return {"bytes": len(html), "http_code": code, "addresses": len(addrs),
            "new": len(new), "new_contracts": new,
            "free_kw": len(re.findall(r"free", html, re.I)),
            "zh_free_kw": len(re.findall("免费", html))}
for lang in ("en", "zh"):
    try: out[f"leg2_boltbook_{lang}"] = boltbook(lang)
    except Exception as e: out[f"leg2_boltbook_{lang}"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# Leg 3 shape-check new contracts
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
def shape_check(addr):
    try:
        status, raw = https_get("sourcify.dev", f"/server/v2/contract/56/{addr}?fields=abi", timeout=20)
        meta = json.loads(raw.decode()); abi = meta.get("abi", [])
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
sc = [shape_check(a) for a in targets]
out["leg3_shape_check"] = sc
out["leg3_sale_shape"] = [s for s in sc if s.get("S1") or s.get("S2")]
seen_added = []
for s in sc:
    if s.get("status") != "checked": continue
    seen[s["address"]] = {"first_seen_wib": now_wib, "source": "sourcify-feed",
        "status": "sale-shape" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape",
        "note": json.dumps(s)[:600], "verifiedAt": s.get("verifiedAt")}
    seen_added.append(s["address"])
for a, v in new1:
    if a not in seen:
        seen[a] = {"first_seen_wib": now_wib, "source": "sourcify-feed", "status": "checked-not-sale-shape",
                   "note": "no shape-check result", "verifiedAt": v}; seen_added.append(a)
out["seen_added"] = seen_added; out["seen_n"] = len(seen)
json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)

# Leg 4 targeted re-read (continuity set + PUNNY + STOCK AGENT; prev = last known good from 16:29 script)
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
   ("quoteFor_user_1","quoteFor(address,uint256)","user1"),
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
    entry = dynamic_credential_entry("custom.quicknode")
    surrogate = str(entry["surrogate"]).strip()
    conn = ProxyHTTPSConnection(QN_HOST, 443, timeout=20)
    conn.request("POST", f"/{surrogate}/",
                 body=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode(),
                 headers={"Content-Type": "application/json"})
    resp = conn.getresponse(); blk = json.loads(resp.read().decode()); conn.close()
    block = int(blk["result"], 16)
except Exception as e:
    block = f"error: {str(e)[:120]}"
reread = {"reads": reads, "errors": errs, "n_calls": len(calls),
          "elapsed_s": round(time.time()-T0, 1), "block": block, "started_wib": now_wib}
json.dump(reread, open(f"{HF}/hot-leg-run-2026-11-18-1634-reread.json", "w"), indent=1)
out["leg4_reread"] = {"block": block, "reads": {k: v["views"] for k, v in reads.items()}, "errors": errs}
prev = {"DGF CARD totalMinted": 1644, "BinanceAI launched()": 0, "AlphaPulse V1 totalSupply": 34,
        "FABE freeSharesRemaining": 2821, "PUNNY freeMinted": 349, "PUNNY totalMinted": 349,
        "STOCK AGENT totalSupply": 760, "STOCK AGENT freeLeft": 351}
cur = {"DGF CARD totalMinted": reads["DGF CARD"]["views"].get("totalMinted"),
       "BinanceAI launched()": reads["BinanceAI"]["views"].get("launched"),
       "AlphaPulse V1 totalSupply": reads["AlphaPulse V1"]["views"].get("totalSupply"),
       "FABE freeSharesRemaining": reads["FABE"]["views"].get("freeSharesRemaining"),
       "PUNNY freeMinted": reads["PUNNY"]["views"].get("freeMinted"),
       "PUNNY totalMinted": reads["PUNNY"]["views"].get("totalMinted"),
       "STOCK AGENT totalSupply": reads["STOCK AGENT"]["views"].get("totalSupply"),
       "STOCK AGENT freeLeft": reads["STOCK AGENT"]["views"].get("freeLeft")}
out["leg4_changes"] = {k: {"prev": prev[k], "now": cur[k]} for k in prev if prev[k] != cur[k]}
pu = reads["PUNNY"]["views"]; st = reads["STOCK AGENT"]["views"]
punny_pct = (pu.get("freeMinted")/pu.get("FREE_SUPPLY")*100) if isinstance(pu.get("freeMinted"), int) and isinstance(pu.get("FREE_SUPPLY"), int) and pu.get("FREE_SUPPLY") else None
stock_free = (st.get("totalSupply")/1111*100) if isinstance(st.get("totalSupply"), int) else None
out["leg4_promotion_check"] = {
 "PUNNY_free_pct": punny_pct,
 "PUNNY_note": "age VERIFIED <24h (mintStart 2026-11-17 20:32 WIB, closes 20:32 WIB today); website gate UNVERIFIED -> no promotion even if pct crossed; pct must be >70% for strong lead.",
 "STOCK_free_pct_inferred": stock_free,
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
                     "same_owner_discarded": disc,
                     "note": "bridge contracts not in snapshot are not reported as new; no bridge promotion/change unless leg4 shows one."}
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:150]}", "note": "bridge skip - run continues"}

out["elapsed_s"] = round(time.time()-T0, 1)
out["executions"] = "none - no preview, no mint, no claim (read-only run)"
reportable = bool(out["leg3_sale_shape"]) or any(
    k in out["leg4_changes"] for k in ("BinanceAI launched()", "FABE freeSharesRemaining"))
out["result"] = ("CHANGES FOUND - see leg3/leg4" if reportable else
  "SILENT - no new lead, candidate, pending claim, change, or blocked auto-mint/auto-claim.")
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-18-1634.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:12000])
