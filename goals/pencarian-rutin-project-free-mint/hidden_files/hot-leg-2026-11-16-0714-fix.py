#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-16 0714 - FIX pass: leg2 via curl, leg4 chunked
batches, bridge dict handling. Read-only except hot-leg-seen.json + run JSON."""
import json, re, subprocess, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
now_wib = "2026-11-16 07:14 WIB"
T0 = time.time()
run = json.load(open(f"{HF}/hot-leg-run-2026-11-16-0714.json"))
seen = json.load(open(f"{HF}/hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}

def curl_get(url, out_path, timeout=20):
    r = subprocess.run(["curl", "-s", "-L", "-A",
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
                        "--max-time", str(timeout), url, "-o", out_path, "-w", "%{http_code}"],
                       capture_output=True, text=True, timeout=timeout + 5)
    return r.stdout.strip()

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeCardsRemaining"}

def shape_check(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        meta = json.loads(fetch(url, timeout=15).decode())
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

# ---- Leg 2 redo via curl ----
for lang, url in (("en", "https://boltbook.fun/"),
                  ("zh", "https://boltbook.fun/?lang=zh")):
    path = f"{HF}/hot-leg-2026-11-16-0714-boltbook-{lang}.html"
    try:
        code = curl_get(url, path)
        html = open(path, encoding="utf-8", errors="replace").read()
        addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        new = [a for a in addrs if a.lower() not in seen_l
               and a.lower() not in EXCLUDED and a.lower() != REGISTRY.lower()]
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)
        figs = []
        for m in re.finditer(r"(.{0,40}\d[\d,]*/\d[\d,]{2,}.{0,10})", text):
            s = m.group(1).strip()
            if len(s) > 12:
                figs.append(s)
        run[f"boltbook_{lang}"] = {"bytes": len(html), "http_code": code,
                                   "full_address_contracts": len(addrs),
                                   "addresses": addrs, "new": len(new),
                                   "new_contracts": new,
                                   "free_kw": len(re.findall(r"free", html, re.I)),
                                   "zh_free_kw": len(re.findall(r"\u514d\u8d39", html)),
                                   "figures": figs[:25]}
    except Exception as e:
        run[f"boltbook_{lang}"] = {"error": f"{type(e).__name__}: {str(e)[:200]}",
                                   "note": "curl retry also failed; retried next run"}

# shape-check any new boltbook addresses
bb_new = []
for lang in ("en", "zh"):
    bb_new += run.get(f"boltbook_{lang}", {}).get("new_contracts", [])
bb_new = list(dict.fromkeys(bb_new))
if bb_new:
    checks = [shape_check(a) for a in bb_new]
    run["shape_check_boltbook"] = checks
    run["shape_hits"] = run.get("shape_hits", []) + [s for s in checks if s.get("S1") or s.get("S2")]
    for a in bb_new:
        if a not in seen:
            seen[a] = {"first_seen_wib": now_wib, "source": "boltbook-curl",
                       "status": "checked-not-sale-shape",
                       "note": json.dumps([s for s in checks if s["address"] == a])[:600]}
    json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)

# ---- Leg 4 redo: chunked batches of 8 ----
def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def batch_read_chunk(calls, timeout=15):
    import fast_rpc
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
            if not isinstance(out, list):
                raise IOError(f"non-list batch response: {str(out)[:200]}")
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
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", "launched()", None), ("failed", "failed()", None),
   ("isRefundPhase", "isRefundPhase()", None), ("totalShares", "totalShares()", None),
   ("tokenClaimed_user", "tokenClaimed(address)", "user")]),
]
calls, meta = [], []
for name, addr, views in PLAN:
    for label, sig, arg in views:
        data = "0x" + sel(sig)
        if arg == "user":
            data += enc_addr(USER)
        calls.append((addr, data))
        meta.append((name, addr, label))
reread = {}
ep_used = None
chunk_errors = []
for i in range(0, len(calls), 8):
    chunk = calls[i:i + 8]
    try:
        res, ep = batch_read_chunk(chunk)
        ep_used = ep
        for (name, addr, label), val in zip(meta[i:i + 8], res):
            reread.setdefault(name, {"address": addr, "views": {}})["views"][label] = val
    except Exception as e:
        chunk_errors.append(f"calls {i}-{i + len(chunk) - 1}: {type(e).__name__}: {str(e)[:150]}")
        for name, addr, label in meta[i:i + 8]:
            reread.setdefault(name, {"address": addr, "views": {}})["views"][label] = None
run["leg4_reread"] = {"reads": reread, "endpoint": ep_used,
                      "n_calls": len(calls), "chunk_size": 8,
                      "chunk_errors": chunk_errors,
                      "note": "56-call single batch silently returned all-null (non-list/error response swallowed); chunked retry applied"}
try:
    payload = json.dumps([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}]).encode()
    req = urllib.request.Request(ep_used or "https://bsc-dataseed.binance.org/",
                                 data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        run["leg4_reread"]["block"] = int(json.loads(r.read().decode())[0]["result"], 16)
except Exception as e:
    run["leg4_reread"]["block_error"] = str(e)[:120]

# ---- Bridge redo (dict handling) ----
try:
    bridge = json.load(open(f"{HF}/scan-bridge.json"))
    contracts = bridge.get("contracts", {}) if isinstance(bridge, dict) else {}
    snap = json.load(open(f"{HF}/onchain-snapshot.json"))
    snap_addrs = set()
    for coll in ("contracts", "track_c"):
        for k, v in snap.get(coll, {}).items():
            if isinstance(v, dict) and v.get("address"):
                snap_addrs.add(v["address"].lower())
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
    run["bridge_scan"] = {"total": len(contracts), "not_in_snapshot": len(not_in),
                          "not_in_snapshot_list": not_in[:20],
                          "same_owner_discarded": discarded}
except Exception as e:
    run["bridge_scan"] = {"error": f"{type(e).__name__}: {str(e)[:200]}",
                          "note": "bridge skip - run continues"}

run["fix_elapsed_s"] = round(time.time() - T0, 1)
json.dump(run, open(f"{HF}/hot-leg-run-2026-11-16-0714.json", "w"), indent=1)
print(json.dumps(run, indent=1))
