#!/usr/bin/env python3
"""hot-leg run 2026-11-17 19:19 WIB (same pattern as 1909; focus set 16 + CAT402 pre-launch re-check).
Legs 1+2 (Sourcify feed + Boltbook EN/ZH), shape-check new contracts,
leg 3 on-chain verify for new S1/S2 contracts (per 1734 pattern),
bridge leg (read-only), leg 4 reread focus set (16 items).
Read-only except hot-leg-seen.json notes and this run's own outputs.
No preview/mint. No snapshot rewrite."""
import json, re, time, urllib.request, subprocess, base64
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
T0 = time.time()
from datetime import datetime, timezone, timedelta
NOW = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
out = {"run": "free-mint-hot-leg 2026-11-17 19:19 WIB", "started_wib": NOW}

def fetch(url, timeout=15):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-A", "hot-leg/1.0", url],
                       capture_output=True)
    if r.returncode == 0 and r.stdout:
        return r.stdout
    req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

seen = json.load(open(BASE + "hot-leg-seen.json"))

# --- Leg 1: Sourcify feed ---
try:
    raw = fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=15)
    feed = json.loads(raw)
    contracts = []
    for c in (feed if isinstance(feed, list) else feed.get("results", [])):
        a = c.get("address") if isinstance(c, dict) else None
        if a: contracts.append(a)
    va = [c.get("verifiedAt") for c in (feed if isinstance(feed, list) else feed.get("results", [])) if isinstance(c, dict) and c.get("verifiedAt")]
    seen_l = {k.lower() for k in seen}
    new = [a for a in contracts if a.lower() not in seen_l and a.lower() != REGISTRY.lower()]
    out["feed"] = {"n": len(contracts), "newest_verifiedAt": max(va) if va else None,
                   "oldest_verifiedAt": min(va) if va else None}
    out["feed_new"] = new
except Exception as e:
    out["feed"] = {"error": f"{type(e).__name__}: {e}"}
    new = []

# --- Leg 2: Boltbook EN + ZH ---
def boltbook(lang):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    raw = fetch(url, timeout=20)
    text = raw.decode("utf-8", errors="ignore")
    addrs = sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", text)))
    return {"bytes": len(raw), "addrs": addrs,
            "kw": {"free share": text.lower().count("free share"),
                   "first share free": text.lower().count("first share free"),
                   "free mint share": text.lower().count("free mint share"),
                   "1 free share": text.lower().count("1 free share"),
                   "免费份额": text.count("免费份额"), "首个免费": text.count("首个免费"),
                   "免费铸造": text.count("免费铸造"), "免费mint": text.count("免费mint")}}
bb = {}
for lang in ("en", "zh"):
    try: bb[lang] = boltbook(lang)
    except Exception as e: bb[lang] = {"error": f"{type(e).__name__}: {e}"}
out["boltbook_en"] = bb["en"]; out["boltbook_zh"] = bb["zh"]
bb_new = []
seen_l = {k.lower() for k in seen}
for lang in ("en", "zh"):
    for a in bb.get(lang, {}).get("addrs", []):
        if a.lower() not in seen_l and a.lower() not in [x.lower() for x in bb_new]: bb_new.append(a)
out["boltbook_new"] = bb_new

# --- Shape-check new contracts (legs 1+2) ---
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedTotal"]
def shape(addr):
    try:
        raw = fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=15)
        d = json.loads(raw)
        abi = d.get("abi") or (d.get("stdJson", {}) or {}).get("abi") or []
    except Exception as e:
        return {"status": "shape-check-failed", "error": f"{type(e).__name__}: {e}"}
    names = [f.get("name", "").lower() for f in abi if isinstance(f, dict)]
    has_mint = any(n.startswith("mint") or n in ("claimfree", "claim", "mintfree") for n in names)
    has_quote = any("quote" in n or "price" in n or n.startswith("cost") for n in names)
    free = sorted(set(n for n in names if any(k.lower() in n for k in FREE_VIEWS)))
    agent = any("agent" in n or "registry" in n for n in names) or REGISTRY.lower() in json.dumps(abi).lower()
    tokenish = all(k in names for k in ("name", "symbol", "decimals", "totalsupply"))
    noarg_free = any(n in ("mintfree", "claimfree") for n in names)
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = tokenish and noarg_free and bool(free) and agent
    return {"S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
            "free": free, "agent": agent, "status": "checked"}
EXCLUDED = ("0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493")
shape_res = {}
for a in (new + bb_new):
    if a.lower() in EXCLUDED:
        shape_res[a] = {"status": "excluded-example"}
        continue
    shape_res[a] = shape(a)
out["feed_shape"] = {a: shape_res[a] for a in new}
out["boltbook_new_shapecheck"] = {a: shape_res[a] for a in bb_new}

# --- Leg 3: on-chain verify new S1/S2 contracts ---
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42: d += enc_addr(a)
        elif isinstance(a, str) and a.startswith("0x"): d += enc_u(int(a, 16))
        else: d += enc_u(int(a))
    return d
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def dec_str(hexs):
    try:
        b = bytes.fromhex(hexs[2:])
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", errors="ignore")
    except Exception: return None
def post_rpc(ep, payload, timeout=60):
    o = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(o)

leg3 = {}
U = [USER]
for a in (new + bb_new):
    sh = shape_res.get(a, {})
    if not (sh.get("S1") or sh.get("S2")):
        continue
    views = [("freeClaimed", "freeClaimed()", []), ("FREE_SUPPLY", "FREE_SUPPLY()", []),
             ("FREE_PER_WALLET", "FREE_PER_WALLET()", []), ("freeLeft_user", "freeLeft(address)", U),
             ("freeUsed_user", "freeUsed(address)", U), ("freeFor_user1", "freeFor(address,uint256)", [USER, 1]),
             ("quote_user1", "quote(address,uint256)", [USER, 1]),
             ("AGENT_ID", "AGENT_ID()", []), ("agentIdRequired", "agentIdRequired()", []),
             ("mintOpen", "mintOpen()", []), ("totalSupply", "totalSupply()", []),
             ("name", "name()", []), ("symbol", "symbol()", []), ("contractURI", "contractURI()", [])]
    calls, meta = [], []
    for key, sig, args in views:
        calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                      "params": [{"to": a, "data": build_data(sig, args)}, "latest"]})
        meta.append(key)
    got = None
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=60)
            if isinstance(res, list) and len(res) == len(calls):
                got = (res, ep); break
        except Exception as e:
            print("  leg3 ep", ep, "exc", str(e)[:80], flush=True); continue
    if got is None:
        leg3[a] = {"error": "all RPC endpoints failed"}
        continue
    res, ep = got
    vals = {}
    for it, key in zip(res, meta):
        if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
            vals[key] = None
        else:
            r = it["result"]
            if key in ("name", "symbol", "contractURI"):
                vals[key] = dec_str(r)
            elif key == "AGENT_ID":
                vals[key] = "0x" + r[-40:] if len(r) >= 42 else r
            else:
                vals[key] = to_int(r[:66]) if len(r) >= 66 else r
    # contractURI decode for gate method H
    cu = vals.get("contractURI") or ""
    ext = None
    if cu.startswith("data:application/json;base64,"):
        try:
            ext = json.loads(base64.b64decode(cu.split(",", 1)[1]).decode("utf-8", errors="ignore"))
        except Exception as e:
            ext = {"decode_error": str(e)[:80]}
    elif cu.startswith("{"):
        try: ext = json.loads(cu)
        except Exception: ext = None
    vals["contractURI_json"] = ext
    # snapshot membership (do not report as new if already there)
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    in_snap = False
    for sec in ("contracts", "track_c"):
        for v in (snap.get(sec) or {}).values():
            if isinstance(v, dict):
                for f in ("address", "sale", "contract", "token"):
                    if isinstance(v.get(f), str) and v[f].lower() == a.lower():
                        in_snap = True
    vals["in_main_snapshot"] = in_snap
    vals["rpc_ep"] = ep
    leg3[a] = vals
out["leg3"] = leg3

seen_l = {k.lower() for k in seen}
for a in (new + bb_new):
    if a.lower() not in seen_l:
        note = json.dumps(shape_res.get(a, {}))[:300]
        if a in leg3:
            note = json.dumps(leg3[a])[:400]
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed" if a in new else "boltbook",
                   "status": shape_res.get(a, {}).get("status", "checked"),
                   "note": note}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["seen_total"] = len(seen)


# --- Leg 3b: CAT402 pre-launch re-check (found 18:59 run, S1, gateStart=0) ---
CAT402 = "0xdAba96c14B38725b23502BE6dFE021c08B7a5fB1"
try:
    cviews = [("registry", "registry()", []), ("FREE_CATS_TOTAL", "FREE_CATS_TOTAL()", []),
              ("freeCatsClaimed", "freeCatsClaimed()", []),
              ("freeCatsRemaining", "freeCatsRemaining()", []),
              ("isFreeEligible_user", "isFreeEligible(address)", U),
              ("freeClaimedBy_user", "freeClaimedBy(address)", U),
              ("MAX_CATS_PER_WALLET", "MAX_CATS_PER_WALLET()", []),
              ("TOTAL_CATS", "TOTAL_CATS()", []),
              ("quoteBuy_1", "quoteBuy(uint256)", [1]),
              ("gateStart", "gateStart()", []),
              ("freeWindowOpen", "freeWindowOpen()", []),
              ("windowOpen", "windowOpen()", []),
              ("totalCatsMinted", "totalCatsMinted()", []),
              ("paidCatsSold", "paidCatsSold()", [])]
    ccalls, cmeta = [], []
    for key, sig, args in cviews:
        ccalls.append({"jsonrpc": "2.0", "id": len(ccalls)+1, "method": "eth_call",
                       "params": [{"to": CAT402, "data": build_data(sig, args)}, "latest"]})
        cmeta.append(key)
    cgot = None
    for ep in EPS:
        try:
            res = post_rpc(ep, ccalls, timeout=60)
            if isinstance(res, list) and len(res) == len(ccalls):
                cgot = (res, ep); break
        except Exception as e:
            print("  cat402 ep", ep, "exc", str(e)[:80], flush=True); continue
    if cgot is None:
        out["cat402_recheck"] = {"error": "all RPC endpoints failed"}
    else:
        res, ep = cgot
        vals = {}
        for it, key in zip(res, cmeta):
            if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                vals[key] = None
            elif key == "registry":
                vals[key] = "0x" + it["result"][-40:] if len(it["result"]) >= 42 else it["result"]
            else:
                vals[key] = to_int(it["result"][:66]) if len(it["result"]) >= 66 else it["result"]
        vals["rpc_ep"] = ep
        out["cat402_recheck"] = vals
        prev = {"gateStart": 0, "freeWindowOpen": False, "windowOpen": False,
                "totalCatsMinted": 0, "paidCatsSold": 0, "freeCatsClaimed": 0,
                "freeCatsRemaining": 100}
        changed = {k: {"prev": prev.get(k), "now": vals.get(k)} for k in prev
                   if prev.get(k) != vals.get(k)}
        out["cat402_changes_vs_1914"] = changed
        if changed:
            seen[CAT402]["note"] = (seen[CAT402].get("note", "") +
                f" | RE-CHECK run 19:19: {json.dumps(changed)[:500]}")
            json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
except Exception as e:
    out["cat402_recheck"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# --- Bridge leg (read-only) ---
try:
    br = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = br.get("contracts", {})
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    def _addr_vals(section, fields):
        o = set()
        for v in (snap.get(section) or {}).values():
            if isinstance(v, dict):
                for f in fields:
                    x = v.get(f)
                    if isinstance(x, str) and x.startswith("0x") and len(x) == 42:
                        o.add(x.lower())
        return o
    snap_addrs = (_addr_vals("contracts", ["address", "sale", "contract"])
                  | _addr_vals("track_c", ["sale", "address", "token", "contract"])
                  | _addr_vals("pending_claims", ["address", "sale", "mint"]))
    outside = []
    discarded = 0
    for addr, info in bcontracts.items():
        if info.get("same_owner_discarded"):
            discarded += 1
            continue
        if addr.lower() not in snap_addrs:
            outside.append(addr)
    out["bridge"] = {"n": len(bcontracts), "same_owner_discarded": discarded,
                     "outside_snapshot": outside}
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {e}"}

# --- Leg 4: reread focus set ---
NFT_VIEWS = [("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
             ("freeClaimed","freeClaimed()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
             ("FREE_MAX","FREE_MAX()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
             ("mintOpen","mintOpen()",[]),("freeRemaining","freeRemaining()",[]),
             ("balanceOf_user","balanceOf(address)",U),
             ("freeClaimed_user","freeClaimed(address)",U)]
ITEMS = {
 "BoldLeonidas": ("0x84bcb8c16566e81ce902530c9da1e3de291f9941", NFT_VIEWS),
 "PunchCard": ("0x1d4ef0587dd3ff3875a141d4711c60bca40587c4", NFT_VIEWS),
 "FrieAgent-B751": ("0xb7517e3b31107695f2f8837fafc76999b956c871",
    [("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
     ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "FrieAgent-c64d": ("0xc64da7479c5abc8e6dfadeb4d17502ebcf9837e5",
    [("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
     ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "Flare-bd6f": ("0xbd6ff7ed8fe96b79cb3cbf9dc32656ff7a98a599",
    [("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
     ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "MatrixAgents": ("0x1F669b714337F3C2585072c53fdDD89581F928fF",
    [("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
     ("freeRemaining","freeRemaining()",[]),("mintOpen","mintOpen()",[]),
     ("balanceOf_user","balanceOf(address)",U)]),
 "ALIEN": ("0xf5767ac3beb8bbfaf4596dfc1925fc5aca779dcb", NFT_VIEWS),
 "PXIO-Miners": ("0x58e8f1b34B60687B36BCdc78e02a2fd443De71Ab", NFT_VIEWS),
 "AGCLUB": ("0x67270bb351515abf3089ca5420456897363f5e75", NFT_VIEWS),
 "DogeRageFi": ("0x097ff90fce52f4f0e1f41d6f8c799db9cd67099f",
    [("freeMinted","freeMinted()",[]),("FREE_SHARES","FREE_SHARES()",[]),
     ("freeClaimed","freeClaimed()",[]),("totalSupply","totalSupply()",[]),
     ("mintOpen","mintOpen()",[]),("freeClaimed_user","freeClaimed(address)",U)]),
 "DRAGON": ("0xfc191b76041498b14dcae3c802af3389c74263e6",
    [("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
     ("FREE_SUPPLY","FREE_SUPPLY()",[]),("freeRemaining","freeRemaining()",[]),
     ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U),
     ("freeClaimed_user","freeClaimed(address)",U)]),
 "Abyssora": ("0x4785e7b396d13fb23b50bd66a6f828797c862770",
    [("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
     ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
     ("balanceOf_user","balanceOf(address)",U)]),
 "MineCard": ("0xf8a72c4538cd9d570b2c771f01a0d561a90a64eb",
    [("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
     ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
     ("mintedBy_user","mintedBy(address)",U),
     ("balanceOf_user","balanceOf(address)",U)]),
 "BinanceAI-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched","launched()".replace("()", "()"),[]),("failed","failed()",[]),
    ("isRefundPhase","isRefundPhase()",[]),("totalShares","totalShares()".replace("()", "()"),[]),
    ("tokenClaimed_user","tokenClaimed(address)",U)]),
 "HANAMI-BLOOM": ("0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640", NFT_VIEWS),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
    [("openedAt","openedAt()".replace("()", "()"),[]),("freeSharesLeft","freeSharesLeft()",[]),
     ("freeClaimed","freeClaimed()",[]),
     ("freeBooked_user","freeBooked(address)",U)]),
}
def chunked(items, n=3):
    items = list(items.items())
    for i in range(0, len(items), n):
        yield items[i:i+n]
def read_chunk(chunk):
    calls, meta = [], []
    for name, (addr, views) in chunk:
        for key, sig, args in views:
            calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                          "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
            meta.append((name, key))
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=60)
            if not isinstance(res, list) or len(res) != len(calls):
                print("  chunk ep", ep, "bad shape", str(res)[:120], flush=True); continue
            o = {}
            for it, (name, key) in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    o.setdefault(name, {})[key] = None
                else:
                    r = it["result"]
                    o.setdefault(name, {})[key] = to_int(r[:66]) if len(r) >= 66 else r
            return o, ep
        except Exception as e:
            print("  chunk ep", ep, "exc", str(e)[:100], flush=True); continue
    return None, None
def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=60)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16)
        except Exception: continue
    return None

reads, ok = {}, 0
for ci, ch in enumerate(chunked(ITEMS, 3)):
    r, ep = read_chunk(ch)
    names = [n for n, _ in ch]
    if r is None:
        print(f"chunk {ci+1} FAIL {names}", flush=True)
        for n in names: reads[n] = {"address": ITEMS[n][0], "views": None}
        continue
    ok += sum(1 for n in names if r.get(n) is not None)
    for n in names: reads[n] = {"address": ITEMS[n][0], "views": r.get(n)}
    print(f"chunk {ci+1} OK via {ep} ({time.time()-T0:.0f}s) {names}", flush=True)
    time.sleep(2)
blk = block_number()
reread = {"started_wib": NOW, "reads": reads, "reads_ok": ok,
          "reads_total": len(ITEMS), "block": blk, "elapsed_s": round(time.time() - T0, 1)}
json.dump(reread, open(BASE + "run-hot-leg-2026-11-17-1919-reread.json", "w"), indent=1)
out["reread_block"] = blk
out["reread_ok"] = f"{ok}/{len(ITEMS)}"
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + "run-hot-leg-2026-11-17-1919.json", "w"), indent=1)
print("DONE ok", ok, "/", len(ITEMS), "block", blk, "elapsed", round(time.time() - T0, 1))
