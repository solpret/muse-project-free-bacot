#!/usr/bin/env python3
"""free-mint-hot-leg run 2026-11-16 11:09 WIB. Read-only legs 1-4 + bridge.
Writes: hot-leg-run-2026-11-16-1109.json, boltbook html snapshots; updates
hot-leg-seen.json ONLY (never main snapshot / scan seen / track-c-checked)."""
import json, re, subprocess, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
import fast_rpc

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
T0 = time.time()
now_wib = "2026-11-16 11:09 WIB"

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def call(to, sig, arg=None):
    data = "0x" + sel(sig)
    if arg == "user":
        data += enc_addr(USER)
    return (to, data)

def batch_read(calls, timeout=15):
    """One JSON-RPC batch; per-item errors -> None (tolerates reverts)."""
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    body = json.dumps(payload).encode()
    last_err = None
    for ep in fast_rpc.healthy_endpoints() or fast_rpc.ENDPOINTS:
        try:
            req = urllib.request.Request(ep, data=body,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                out = json.loads(r.read().decode())
            res = []
            by_id = {it["id"]: it for it in out if isinstance(it, dict)}
            for i in range(len(calls)):
                it = by_id.get(i + 1, {})
                if "result" in it and it["result"] not in (None, "0x"):
                    try:
                        res.append(int(it["result"], 16))
                    except Exception:
                        res.append(it["result"])
                else:
                    res.append(None)
            return res, ep
        except Exception as e:
            last_err = e
            continue
    raise IOError(f"batch_read failed on all endpoints: {last_err}")

seen = json.load(open(f"{HF}/hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
out = {"run": "free-mint-hot-leg 2026-11-16 11:09 WIB", "started_wib": now_wib}

# ---- Leg 1: Sourcify feed ----
try:
    raw = fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc")
    feed = json.loads(raw.decode())
    items = feed if isinstance(feed, list) else feed.get("results", feed.get("contracts", []))
    addrs = []
    for it in items:
        a = it.get("address") or (it.get("contract") or {}).get("address")
        if a:
            addrs.append((a, it.get("verifiedAt")))
    new1 = [(a, v) for a, v in addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED]
    out["sourcify_feed"] = {"total": len(addrs), "new": len(new1),
                            "new_contracts": [a for a, _ in new1],
                            "top": addrs[0][0] if addrs else None,
                            "top_verifiedAt": addrs[0][1] if addrs else None,
                            "all": [a for a, _ in addrs]}
except Exception as e:
    out["sourcify_feed"] = {"error": f"{type(e).__name__}: {e}"}
    new1 = []

# ---- Leg 2: Boltbook EN + ZH via curl (urllib IncompleteRead 0714) ----
def curl_get(url, out_path, timeout=20):
    r = subprocess.run(["curl", "-s", "-L", "-A",
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
                        "--max-time", str(timeout), url, "-o", out_path, "-w", "%{http_code}"],
                       capture_output=True, text=True, timeout=timeout + 5)
    return r.stdout.strip()

def boltbook(lang):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    path = f"{HF}/hot-leg-2026-11-16-1109-boltbook-{lang}.html"
    code = curl_get(url, path)
    html = open(path, encoding="utf-8", errors="replace").read()
    addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    new = [a for a in addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED
           and a.lower() != REGISTRY.lower()]
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    figs = []
    for m in re.finditer(r"(.{0,40}\d[\d,]*/\d[\d,]{2,}.{0,10})", text):
        s = m.group(1).strip()
        if len(s) > 12:
            figs.append(s)
    return {"bytes": len(html), "http_code": code, "full_address_contracts": len(addrs),
            "addresses": addrs, "new": len(new), "new_contracts": new,
            "free_kw": len(re.findall(r"free", html, re.I)),
            "zh_free_kw": len(re.findall(r"\u514d\u8d39", html)),
            "figures": figs[:25]}

for lang in ("en", "zh"):
    try:
        out[f"boltbook_{lang}"] = boltbook(lang)
    except Exception as e:
        out[f"boltbook_{lang}"] = {"error": f"{type(e).__name__}: {e}"}

# ---- Leg 3: shape-check new contracts ----
targets = []
for a, _ in new1:
    targets.append(a)
for lang in ("en", "zh"):
    b = out.get(f"boltbook_{lang}", {})
    targets += b.get("new_contracts", [])
RETRY_TARGETS = []  # 1059 retry targets checked OK at 1059
targets += [a for a in RETRY_TARGETS if a not in targets]
targets = list(dict.fromkeys(targets))
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeCardsRemaining"}

def shape_check(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        try:
            raw = fetch(url, timeout=15)
        except Exception:
            r = subprocess.run(["curl", "-s", "-L", "--max-time", "20", url],
                               capture_output=True, timeout=25)
            if r.returncode != 0 or not r.stdout:
                raise IOError(f"curl fallback failed rc={r.returncode}")
            raw = r.stdout
        meta = json.loads(raw.decode())
        abi = meta.get("abi", [])
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
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) \
            and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token,
                "n_fns": len(names), "status": "checked",
                "verifiedAt": meta.get("verifiedAt")}
    except Exception as e:
        return {"address": addr, "status": "shape-check-failed",
                "error": f"{type(e).__name__}: {str(e)[:120]}"}

out["shape_check_targets"] = targets
out["shape_check"] = [shape_check(a) for a in targets]
out["shape_hits"] = [s for s in out["shape_check"] if s.get("S1") or s.get("S2")]

# record newly seen (feed + boltbook) in hot-leg-seen.json
for sc in out["shape_check"]:
    a = sc["address"]
    if a in RETRY_TARGETS and a in seen and sc.get("status") == "checked":
        seen[a] = {"first_seen_wib": seen[a].get("first_seen_wib", now_wib),
                   "source": "sourcify-feed-retry-1109",
                   "status": "sale-shape" if (sc.get("S1") or sc.get("S2")) else "checked-not-sale-shape",
                   "note": json.dumps(sc)[:600], "verifiedAt": sc.get("verifiedAt")}
for a, v in new1:
    seen[a] = {"first_seen_wib": now_wib, "source": "sourcify-feed",
               "status": "checked-not-sale-shape" if not any(
                   s["address"] == a and (s.get("S1") or s.get("S2"))
                   for s in out["shape_check"]) else "sale-shape",
               "note": json.dumps([s for s in out["shape_check"] if s["address"] == a])[:600],
               "verifiedAt": v}
for lang in ("en", "zh"):
    b = out.get(f"boltbook_{lang}", {})
    for a in b.get("new_contracts", []):
        if a not in seen:
            seen[a] = {"first_seen_wib": now_wib, "source": f"boltbook-{lang}",
                       "status": "checked-not-sale-shape",
                       "note": json.dumps([s for s in out["shape_check"]
                                           if s["address"] == a])[:600]}
json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)

# ---- Leg 4: re-read snapshot priority entries (READ-ONLY) ----
PLAN = [
 ("AgentBubble", "0x0d72970046c056db90888351b739246f468bff0b",
  [("freeMinted", "freeMinted()", None), ("totalSupply", "totalSupply()", None),
   ("totalMinted", "totalMinted()", None), ("MAX_SUPPLY", "MAX_SUPPLY()", None),
   ("mintOpen", "mintOpen()", None), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Matrix", "0x1F669b714337F3C2585072c53fdDD89581F928fF",
  [("freeMinted", "freeMinted()", None), ("freeRemaining", "freeRemaining()", None),
   ("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None)]),
 ("AGCLUB", "0x67270bb351515abf3089ca5420456897363f5e75",
  [("totalMinted", "totalMinted()", None), ("freeMinted", "freeMinted()", None),
   ("FREE_CAP", "FREE_CAP()", None), ("mintOpen", "mintOpen()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("BNBG", "0x1595013dfc8c6b3f4b172254bf09bdaf1421002b",
  [("totalMinted", "totalMinted()", None)]),
 ("SPARKS", "0xd52fd117c4b47d03e4e16e778871f09faa5a024b",
  [("totalSupply", "totalSupply()", None)]),
 ("Ledgera", "0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d",
  [("freeClaimed", "freeClaimed()", None), ("totalSupply", "totalSupply()", None),
   ("mintOpen", "mintOpen()", None), ("freeUsed_user", "freeUsed(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("BoldLeonidas", "0x84bcb8c16566e81ce902530c9da1e3de291f9941",
  [("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("RaceAgents", "0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f",
  [("totalSupply", "totalSupply()", None), ("freeMinted", "freeMinted()", None),
   ("mintOpen", "mintOpen()", None)]),
 ("CPASS", "0x5877d2bb9f226cc3e438f4d656caeb27deafc576",
  [("totalMinted", "totalMinted()", None), ("mintOpen", "mintOpen()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("REOPIR", "0x12f65bc14037ccdf3f97afc0e67a0e4aca3cf5b9",
  [("freeClaimed", "freeClaimed()", None), ("totalSupply", "totalSupply()", None),
   ("mintOpen", "mintOpen()", None)]),
 ("RAVE", "0x7c40B78992d86EDfFB5553C74dB5EF427100bb95",
  [("totalMinted", "totalMinted()", None), ("freeMinted", "freeMinted()", None),
   ("mintOpen", "mintOpen()", None)]),
 ("MORFO", "0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186",
  [("totalMinted", "totalMinted()", None), ("mintOpen", "mintOpen()", None)]),
 ("AgentNOVA", "0x43462d7f269fde4914b03e1e07067a61b62b9540",
  [("totalSupply", "totalSupply()", None)]),
 ("Zephyra", "0x00a9791be6317d6e3a6c60f75a706c870d882048",
  [("totalMinted", "totalMinted()", None)]),
 ("Pengu", "0x5AEc03C90656743475810926B2B2bd443D5c26a4",
  [("totalMinted", "totalMinted()", None), ("freeMinted", "freeMinted()", None)]),
 ("Kryntar", "0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe",
  [("totalMinted", "totalMinted()", None), ("standardRemaining", "standardRemaining()", None),
   ("legendaryRemaining", "legendaryRemaining()", None), ("mintOpen", "mintOpen()", None)]),
 ("ONI", "0x99d01eD93829DBB0EEc11F3a733388c789dA6caD",
  [("totalMinted", "totalMinted()", None), ("totalSupply", "totalSupply()", None)]),
 ("HAPPE", "0x72c14121681F1133545947B0735563835CC07B67",
  [("totalMinted", "totalMinted()", None), ("freeMinted", "freeMinted()", None)]),
 ("JADE", "0x1b8894391a3dcfe7e248c321103265ab52e273e0",
  [("freeClaimed", "freeClaimed()", None), ("totalSupply", "totalSupply()", None),
   ("mintOpen", "mintOpen()", None), ("mintedBy_user", "mintedBy(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("PIXELFROGS", "0x454054e55FA2D7Ba37df7F3ceA269696f19037dF",
  [("totalSupply", "totalSupply()", None), ("freeMinted", "freeMinted()", None),
   ("freeLeft", "freeLeft()", None), ("mintOpen", "mintOpen()", None),
   ("freeClaimed_user", "freeClaimed(address)", "user")]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", "launched()", None), ("failed", "failed()", None),
   ("isRefundPhase", "isRefundPhase()", None), ("totalShares", "totalShares()", None),
   ("tokenClaimed_user", "tokenClaimed(address)", "user")]),
]
calls, meta = [], []
# JADE cost(address,uint256) two-arg read (cost(user,1) must be 0 for free slot)
import hashlib
def _sel(sig):
    return keccak(sig.encode())[:4].hex()
_cost_data = "0x" + _sel("cost(address,uint256)") + "0"*24 + USER[2:].lower() + "%064x" % 1
calls.append(("0x1b8894391a3dcfe7e248c321103265ab52e273e0", _cost_data))
meta.append(("JADE", "0x1b8894391a3dcfe7e248c321103265ab52e273e0", "cost_user_1"))
for name, addr, views in PLAN:
    for label, sig, arg in views:
        calls.append(call(addr, sig, arg))
        meta.append((name, addr, label))
def batch_read_chunk(calls, timeout=15):
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    body = json.dumps(payload).encode()
    last_err = None
    for ep in fast_rpc.healthy_endpoints() or fast_rpc.ENDPOINTS:
        try:
            req = urllib.request.Request(ep, data=body,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                outp = json.loads(r.read().decode())
            if not isinstance(outp, list):
                raise IOError(f"non-list batch response: {str(outp)[:200]}")
            res = []
            by_id = {it["id"]: it for it in outp if isinstance(it, dict)}
            for i in range(len(calls)):
                it = by_id.get(i + 1, {})
                if "result" in it and it["result"] not in (None, "0x"):
                    try:
                        res.append(int(it["result"], 16))
                    except Exception:
                        res.append(it["result"])
                else:
                    res.append(None)
            return res, ep
        except Exception as e:
            last_err = e
            continue
    raise IOError(f"batch_read failed on all endpoints: {last_err}")

reread = {}
ep_used = None
chunk_errors = []
for i in range(0, len(calls), 8):
    chunk = calls[i:i + 8]
    try:
        res, ep_used = batch_read_chunk(chunk)
        for (name, addr, label), val in zip(meta[i:i + 8], res):
            reread.setdefault(name, {"address": addr, "views": {}})["views"][label] = val
    except Exception as e:
        chunk_errors.append(f"calls {i}-{i + len(chunk) - 1}: {type(e).__name__}: {str(e)[:150]}")
        for name, addr, label in meta[i:i + 8]:
            reread.setdefault(name, {"address": addr, "views": {}})["views"][label] = None
out["leg4_reread"] = {"reads": reread, "endpoint": ep_used, "n_calls": len(calls),
                      "chunk_size": 8, "chunk_errors": chunk_errors,
                      "note": "chunked batches of 8 (0714 lesson: 56-call single batch silently all-null)"}
try:
    payload = json.dumps([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}]).encode()
    req = urllib.request.Request(ep_used or "https://bsc-dataseed.binance.org/",
                                 data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        out["leg4_reread"]["block"] = int(json.loads(r.read().decode())[0]["result"], 16)
except Exception as e:
    out["leg4_reread"]["block_error"] = str(e)[:120]

# ---- Bridge (read-only; dict with "contracts" key) ----
try:
    bridge = json.load(open(f"{HF}/scan-bridge.json"))
    contracts = bridge.get("contracts", {}) if isinstance(bridge, dict) else {}
    snap = json.load(open(f"{HF}/onchain-snapshot.json"))
    snap_addrs = set()
    for coll in ("contracts", "track_c"):
        for k, v in snap.get(coll, {}).items():
            if isinstance(v, dict) and v.get("address"):
                snap_addrs.add(v["address"].lower())
            elif isinstance(v, dict):
                for f in ("sale", "token", "mint", "address"):
                    if v.get(f):
                        snap_addrs.add(str(v[f]).lower())
    for k, v in snap.get("pending_claims", {}).items():
        if isinstance(v, dict):
            for f in ("mint", "token"):
                if v.get(f):
                    snap_addrs.add(v[f].lower())
    not_in = []
    discarded = 0
    for addr, v in contracts.items():
        if isinstance(v, dict) and v.get("same_owner_discarded"):
            discarded += 1
        if addr.lower() not in snap_addrs:
            not_in.append(addr)
    out["bridge_scan"] = {"total": len(contracts), "not_in_snapshot": len(not_in),
                          "not_in_snapshot_list": not_in[:20],
                          "same_owner_discarded": discarded}
except Exception as e:
    out["bridge_scan"] = {"error": f"{type(e).__name__}: {str(e)[:200]}",
                          "note": "bridge skip - run continues"}

# ---- PEPE re-read (track-C lead, audit-blocked since 10:19) ----
PEPE_MINT = "0x7E920e9e4Ad8E4497aEa7EB9bAF60Cd6c6C8D980"
def _enc_u(n):
    return "%064x" % n
_pepe_calls = [
    (PEPE_MINT, "0x" + sel("freeMinted()")),
    (PEPE_MINT, "0x" + sel("soldShares()")),
    (PEPE_MINT, "0x" + sel("FREE_SHARES()")),
    (PEPE_MINT, "0x" + sel("opened()")),
    (PEPE_MINT, "0x" + sel("costOf(uint256)") + _enc_u(1)),
    (PEPE_MINT, "0x" + sel("hasMinted(address)") + enc_addr(USER)),
]
_pepe_labels = ["freeMinted", "soldShares", "FREE_SHARES", "opened", "costOf_1", "hasMinted_user"]
try:
    _pr, _ep2 = batch_read_chunk(_pepe_calls)
    out["pepe_reread"] = dict(zip(_pepe_labels, _pr))
except Exception as e:
    out["pepe_reread"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
out["elapsed_s"] = round(time.time() - T0, 1)
out["executions"] = "none - no preview, no mint, no claim (this script is read-only)"
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-16-1109.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:12000])
