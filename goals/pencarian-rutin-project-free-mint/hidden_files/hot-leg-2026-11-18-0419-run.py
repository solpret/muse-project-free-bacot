#!/usr/bin/env python3
"""free-mint-hot-leg run 2026-11-18 04:19 WIB. Read-only legs 1-4 + bridge.
Writes: hot-leg-run-2026-11-18-0419.json, hot-leg-run-2026-11-18-0419-reread.json,
boltbook html snapshots; updates hot-leg-seen.json ONLY (never main snapshot /
scan seen / track-c-checked). Leg-4 reader: direct curl JSON-RPC batches of 20
to bsc-dataseed (1804 note: fast_rpc timed out + 429 on 0329 run); revert errors
stored as err:{dict} strings to match the 1804 reread format for clean diffs."""
import json, re, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
T0 = time.time()
now_wib = "2026-11-18 04:19 WIB"
RPC_URL = "https://bsc-dataseed.binance.org/"

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def encode(sig, arg):
    data = "0x" + sel(sig)
    if arg == "user":
        data += enc_addr(USER)
    elif arg == "one":
        data += "%064x" % 1
    elif arg == "user1":
        data += enc_addr(USER) + "%064x" % 1
    return data

def curl_json(url, payload, timeout=20):
    r = subprocess.run(["curl", "-s", "-L", "--max-time", str(timeout), url,
                        "-H", "Content-Type: application/json",
                        "-d", json.dumps(payload)],
                       capture_output=True, timeout=timeout + 5)
    if r.returncode != 0 or not r.stdout:
        raise IOError(f"curl failed rc={r.returncode}")
    return json.loads(r.stdout.decode())

def rpc_batch(calls, timeout=20):
    """calls: list of (to, data). Returns list of int | raw-hex-str | 'err:{dict}' | None."""
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    resp = curl_json(RPC_URL, payload, timeout=timeout)
    if not isinstance(resp, list):
        raise IOError(f"non-list batch response: {str(resp)[:200]}")
    by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
    out = []
    for i in range(len(calls)):
        it = by_id.get(i + 1, {})
        if "result" in it and it["result"] not in (None, "0x"):
            try:
                out.append(int(it["result"], 16))
            except Exception:
                out.append(it["result"])
        elif "error" in it:
            out.append(f"err:{it['error']}")
        else:
            out.append(None)
    return out

def rpc_batch_chunked(calls, chunk=20):
    out = []
    errors = []
    for i in range(0, len(calls), chunk):
        try:
            out += rpc_batch(calls[i:i + chunk])
        except Exception as e:
            errors.append(f"calls {i}-{i + len(calls[i:i+chunk]) - 1}: {type(e).__name__}: {str(e)[:150]}")
            out += [None] * len(calls[i:i + chunk])
    return out, errors

seen = json.load(open(f"{HF}/hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
out = {"run": "free-mint-hot-leg 2026-11-18 04:19 WIB", "started_wib": now_wib}

# ---- Leg 1: Sourcify feed ----
try:
    r = subprocess.run(["curl", "-s", "-L", "--max-time", "20",
                        "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"],
                       capture_output=True, timeout=25)
    if r.returncode != 0 or not r.stdout:
        raise IOError(f"curl feed failed rc={r.returncode}")
    feed = json.loads(r.stdout.decode())
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
                            "all": [a for a, _ in addrs], "fetch": "direct curl"}
except Exception as e:
    out["sourcify_feed"] = {"error": f"{type(e).__name__}: {e}"}
    new1 = []

# ---- Leg 2: Boltbook EN + ZH via curl ----
def curl_get(url, out_path, timeout=20):
    r = subprocess.run(["curl", "-s", "-L", "-A",
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
                        "--max-time", str(timeout), url, "-o", out_path, "-w", "%{http_code}"],
                       capture_output=True, text=True, timeout=timeout + 5)
    return r.stdout.strip()

def boltbook(lang):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    path = f"{HF}/hot-leg-2026-11-18-0419-boltbook-{lang}.html"
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
TXHASH_PREFIXES = set()
for lang in ("en", "zh"):
    _p = f"{HF}/hot-leg-2026-11-18-0419-boltbook-{lang}.html"
    try:
        _h = open(_p, encoding="utf-8", errors="replace").read()
        for _m in re.finditer(r"0x[0-9a-fA-F]{64}", _h):
            TXHASH_PREFIXES.add(_m.group(0)[:42].lower())
    except Exception:
        pass
for _a in list(TXHASH_PREFIXES):
    if _a not in seen:
        seen[_a] = {"first_seen_wib": now_wib, "source": "boltbook-frontpage",
                    "status": "checked-not-contract",
                    "note": "First 40 hex chars of a 66-char tx hash in a Boltbook post, not a contract address; regex artifact, never shape-checked."}
targets = [a for a, _ in new1]
for lang in ("en", "zh"):
    b = out.get(f"boltbook_{lang}", {})
    targets += [a for a in b.get("new_contracts", []) if a.lower() not in TXHASH_PREFIXES]
targets = list(dict.fromkeys(targets))
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeCardsRemaining"}

def shape_check(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        r = subprocess.run(["curl", "-s", "-L", "--max-time", "20", url],
                           capture_output=True, timeout=25)
        if r.returncode != 0 or not r.stdout:
            raise IOError(f"curl fallback failed rc={r.returncode}")
        meta = json.loads(r.stdout.decode())
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

def probe_shape(addr):
    views = ["name()", "totalSupply()", "mintOpen()", "freeMinted()", "freeClaimed()",
             "freeSharesRemaining()", "freeLeft()", "FREE_SLOTS()", "FREE_SUPPLY()",
             "agentRegistry()", "mintFree()"]
    calls = [(addr, encode(v, None)) for v in views]
    try:
        res, _errs = rpc_batch_chunked(calls, chunk=20)
    except Exception as e:
        return {"address": addr, "status": "shape-check-failed",
                "error": f"probe failed: {type(e).__name__}: {str(e)[:100]}"}
    got = {v: r for v, r in zip(views, res) if r is not None and not (isinstance(r, str) and r.startswith("err:"))}
    agent = got.get("agentRegistry()") is not None
    free_hit = any(k in got for k in ("freeMinted()", "freeClaimed()", "freeSharesRemaining()",
                                      "freeLeft()", "FREE_SLOTS()", "FREE_SUPPLY()"))
    mintfree = got.get("mintFree()") is not None
    if not agent and not free_hit and not mintfree:
        return {"address": addr, "S1": False, "S2": False, "status": "checked-not-sale-shape",
                "detail": f"on-chain probe: name/totalSupply={'name()' in got}/{'totalSupply()' in got}; "
                          f"mintOpen={got.get('mintOpen()')}; sale views all revert; no agentRegistry",
                "verifiedAt": None}
    return {"address": addr, "S1": None, "S2": None, "status": "shape-check-inconclusive",
            "detail": f"on-chain probe hit: {sorted(got.keys())} - needs manual review, retry next run",
            "verifiedAt": None}

out["shape_check_targets"] = targets
_sc = []
for a in targets:
    r = shape_check(a)
    if r.get("status") == "shape-check-failed":
        r = probe_shape(a)
    _sc.append(r)
out["shape_check"] = _sc
out["shape_hits"] = [s for s in out["shape_check"] if s.get("S1") or s.get("S2")]

seen_added = []
for sc in out["shape_check"]:
    a = sc["address"]
    if sc.get("status") in ("shape-check-failed", "shape-check-inconclusive"):
        continue
    seen[a] = {"first_seen_wib": now_wib, "source": "sourcify-feed",
               "status": "sale-shape" if (sc.get("S1") or sc.get("S2")) else "checked-not-sale-shape",
               "note": json.dumps(sc)[:600],
               "verifiedAt": sc.get("verifiedAt")}
    seen_added.append(a)
for a, v in new1:
    if a not in seen:
        seen[a] = {"first_seen_wib": now_wib, "source": "sourcify-feed",
                   "status": "checked-not-sale-shape", "note": "no shape-check result",
                   "verifiedAt": v}
        seen_added.append(a)
for lang in ("en", "zh"):
    b = out.get(f"boltbook_{lang}", {})
    for a in b.get("new_contracts", []):
        if a not in seen:
            _sc_a = [s for s in out["shape_check"] if s["address"] == a]
            if _sc_a and _sc_a[0].get("status") in ("shape-check-failed", "shape-check-inconclusive"):
                continue
            seen[a] = {"first_seen_wib": now_wib, "source": f"boltbook-{lang}",
                       "status": "checked-not-sale-shape",
                       "note": json.dumps(_sc_a)[:600]}
            seen_added.append(a)
out["seen_added"] = seen_added
out["seen_n"] = len(seen)
json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)

# ---- Leg 4: re-read snapshot priority entries (READ-ONLY) ----
# (name, address, [(label, sig, arg)]) arg: None | "user" | "one" | "user1"
PLAN = [
 ("JADE", "0x1b8894391a3dcfe7e248c321103265ab52e273e0",
  [("cost_user_1", "cost(address,uint256)", "user1"), ("freeClaimed", "freeClaimed()", None),
   ("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None),
   ("mintedBy_user", "mintedBy(address)", "user"), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("AgentBubble", "0x0d72970046c056db90888351b739246f468bff0b",
  [("freeMinted", "freeMinted()", None), ("totalSupply", "totalSupply()", None),
   ("totalMinted", "totalMinted()", None), ("MAX_SUPPLY", "MAX_SUPPLY()", None),
   ("mintOpen", "mintOpen()", None), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("DRAGON", "0xfc191b76041998b14dcae3c802af3389c74263e6",
  [("freeMinted", "freeMinted()", None), ("totalMinted", "totalMinted()", None),
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
 ("PIXELFROGS", "0x454054e55FA2D7Ba37df7F3ceA269696f19037dF",
  [("totalSupply", "totalSupply()", None), ("freeMinted", "freeMinted()", None),
   ("freeLeft", "freeLeft()", None), ("mintOpen", "mintOpen()", None),
   ("freeClaimed_user", "freeClaimed(address)", "user")]),
 ("Flare-bd6f", "0xbd6ff7ed8fe96b79cb3cbf9dc32656ff7a98a599",
  [("totalSupply", "totalSupply()", None)]),
 ("PunchCard", "0x1d4ef0587dd3ff3875a141d4711c60bca40587c4",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("paidMinted", "paidMinted()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("mintPriceFor_user_1", "mintPriceFor(address,uint256)", "user1"),
   ("mintedCount_user", "mintedCount(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
  [("freeSharesLeft", "freeSharesLeft()", None), ("openedAt", "openedAt()", None),
   ("freeClaimed", "freeClaimed()", None), ("freeBooked_user", "freeBooked(address)", "user")]),
 ("Stromboat", "0xC3CB4dF5256c8429Eab306E924BF6E3E6c72163d",
  [("freeMinted", "freeMinted()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("totalMinted", "totalMinted()", None), ("paidMinted", "paidMinted()", None),
   ("freeMintedBy_user", "freeMintedBy(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", "launched()", None), ("failed", "failed()", None),
   ("isRefundPhase", "isRefundPhase()", None), ("totalShares", "totalShares()", None),
   ("tokenClaimed_user", "tokenClaimed(address)", "user")]),
]
BSCCAT_ADDR = "0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A"
BSCCAT_VIEWS = [("totalMinted", "totalMinted()", None), ("soldShares", "soldShares()", None),
  ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
  ("freeSharesLeft", "freeSharesLeft()", None), ("FREE_SHARES", "FREE_SHARES()", None),
  ("FREE_SUPPLY", "FREE_SUPPLY()", None), ("totalShares", "totalShares()", None),
  ("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None),
  ("opened", "opened()", None), ("poolOpen", "poolOpen()", None),
  ("isPoolOpen", "isPoolOpen()", None), ("launched", "launched()", None),
  ("hasMinted_user", "hasMinted(address)", "user"),
  ("freeClaimed_user", "freeClaimed(address)", "user"),
  ("freeUsed_user", "freeUsed(address)", "user"),
  ("freeLeft_user", "freeLeft(address)", "user"),
  ("mintedBy_user", "mintedBy(address)", "user"),
  ("quote_user_1", "quote(address,uint256)", "user1"),
  ("cost_user_1", "cost(address,uint256)", "user1"),
  ("costOf_1", "costOf(uint256)", "one"), ("bnbQuote_1", "bnbQuote(uint256)", "one"),
  ("token", "token()", None), ("TOKEN", "TOKEN()", None),
  ("balanceOf_user", "balanceOf(address)", "user")]
PEPE_MINT = "0x7E920e9e4Ad8E4497aEa7EB9bAF60Cd6c6C8D980"
PEPE_VIEWS = [("freeMinted", "freeMinted()", None), ("soldShares", "soldShares()", None),
  ("FREE_SHARES", "FREE_SHARES()", None), ("opened", "opened()", None),
  ("costOf_1", "costOf(uint256)", "one"),
  ("hasMinted_user", "hasMinted(address)", "user")]

calls, meta = [], []
for name, addr, views in PLAN:
    for label, sig, arg in views:
        calls.append((addr, encode(sig, arg)))
        meta.append((name, addr, label))
for label, sig, arg in BSCCAT_VIEWS:
    calls.append((BSCCAT_ADDR, encode(sig, arg)))
    meta.append(("bsccat", BSCCAT_ADDR, label))
for label, sig, arg in PEPE_VIEWS:
    calls.append((PEPE_MINT, encode(sig, arg)))
    meta.append(("pepe", PEPE_MINT, label))

res, chunk_errors = rpc_batch_chunked(calls, chunk=20)
# Transient-null retry (0324 lesson): null where prev reread had a value -> retry
# once against the backup endpoint; a recovered value means RPC read failure, NOT a change.
retry_info = {"attempted": 0, "recovered": 0, "still_null": []}
try:
    _prev = json.load(open(f"{HF}/hot-leg-run-2026-11-18-0414-reread.json"))
    _prev_map = {}
    for _n, _c in _prev.get("reads", {}).items():
        for _k, _v in _c.get("views", {}).items():
            _prev_map[(_n, _k)] = _v
    for _k, _v in _prev.get("bsccat", {}).get("views", {}).items():
        _prev_map[("bsccat", _k)] = _v
    for _k, _v in _prev.get("pepe", {}).items():
        _prev_map[("pepe", _k)] = _v
    _null_idx = [i for i, v in enumerate(res) if v is None and _prev_map.get(meta[i][:1] + meta[i][2:]) is not None]
    if _null_idx:
        retry_info["attempted"] = len(_null_idx)
        _bak = "https://bsc-dataseed1.defibit.io/"
        _payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                     "params": [{"to": calls[i][0], "data": calls[i][1]}, "latest"]}
                    for i in _null_idx]
        try:
            _resp = curl_json(_bak, _payload, timeout=20)
            _by = {it["id"]: it for it in _resp if isinstance(it, dict)}
            for _j, i in enumerate(_null_idx):
                # FIX 0414: payload ids are i+1 (original call index), not _j+1;
                # the old lookup never matched, so the backup retry recovered 0.
                _it = _by.get(i + 1, {})
                if "result" in _it and _it["result"] not in (None, "0x"):
                    try:
                        res[i] = int(_it["result"], 16)
                    except Exception:
                        res[i] = _it["result"]
                    retry_info["recovered"] += 1
                else:
                    retry_info["still_null"].append(f"{meta[i][0]}.{meta[i][2]}")
        except Exception as e:
            retry_info["error"] = f"{type(e).__name__}: {str(e)[:120]}"
            retry_info["still_null"] = [f"{meta[i][0]}.{meta[i][2]}" for i in _null_idx]
except Exception as e:
    retry_info["error"] = f"prev-load: {type(e).__name__}: {str(e)[:120]}"
reads, bsccat, pepe = {}, {"address": BSCCAT_ADDR, "views": {}}, {}
for (name, addr, label), val in zip(meta, res):
    if name == "bsccat":
        bsccat["views"][label] = val
    elif name == "pepe":
        pepe[label] = val
    else:
        reads.setdefault(name, {"address": addr, "views": {}})["views"][label] = val
try:
    blk = curl_json(RPC_URL, [{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}])
    block = int(blk[0]["result"], 16)
except Exception as e:
    block = f"error: {str(e)[:120]}"
reread_out = {"reads": reads, "bsccat": bsccat, "pepe": pepe, "errors": chunk_errors,
              "n_calls": len(calls), "elapsed_s": round(time.time() - T0, 1), "block": block}
json.dump(reread_out, open(f"{HF}/hot-leg-run-2026-11-18-0419-reread.json", "w"), indent=1)
out["leg4_reread_file"] = "hot-leg-run-2026-11-18-0419-reread.json"
out["leg4_rpc_note"] = "chunked direct JSON-RPC batches of 20 (no fast_rpc race - it timed out + 429 on 0329 run)"
out["leg4_block"] = block
out["leg4_chunk_errors"] = chunk_errors
out["leg4_null_retry"] = retry_info

# ---- Diff vs 0414 run ----
try:
    prev = json.load(open(f"{HF}/hot-leg-run-2026-11-18-0414-reread.json"))
    prev_reads = prev.get("reads", {})
    diffs = []
    for name, cur in reads.items():
        pv = prev_reads.get(name, {}).get("views", {})
        cv = cur.get("views", {})
        d = {k: {"prev": pv.get(k), "now": cv.get(k)} for k in cv if pv.get(k) != cv.get(k)}
        if d:
            diffs.append({"item": name, "type": "value-change", "diff": d})
    out["leg4_changes_vs_0414"] = diffs
    prev_bs = prev.get("bsccat", {}).get("views", {})
    cur_bs = bsccat["views"]
    out["bsccat_changes_vs_0414"] = {k: {"prev": prev_bs.get(k), "now": cur_bs.get(k)}
                                     for k in cur_bs if prev_bs.get(k) != cur_bs.get(k)}
    prev_pepe = prev.get("pepe", {})
    out["pepe_changes_vs_0414"] = {k: {"prev": prev_pepe.get(k), "now": pepe.get(k)}
                                   for k in pepe if prev_pepe.get(k) != pepe.get(k)}
except Exception as e:
    out["leg4_changes_vs_0414"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# ---- Threshold check (strong-lead bar >70% + age <24h + slot open) ----
try:
    th = {}
    pc = reads.get("PunchCard", {}).get("views", {})
    if pc.get("freeMinted") is not None and pc.get("MAX_SUPPLY"):
        th["PunchCard_free_pct"] = round(100.0 * pc["freeMinted"] / pc["MAX_SUPPLY"], 1)
    th["PunchCard_totalSupply"] = pc.get("totalSupply")
    th["PunchCard_slot"] = {"mintPriceFor_user_1": pc.get("mintPriceFor_user_1"),
                            "mintedCount_user": pc.get("mintedCount_user"),
                            "balanceOf_user": pc.get("balanceOf_user"),
                            "mintOpen": pc.get("mintOpen")}
    ag = reads.get("AGCLUB", {}).get("views", {})
    if ag.get("freeMinted") is not None and ag.get("FREE_CAP"):
        th["AGCLUB_free_pct"] = round(100.0 * ag["freeMinted"] / ag["FREE_CAP"], 1)
    mx = reads.get("Matrix", {}).get("views", {})
    if mx.get("freeMinted") is not None and mx.get("freeRemaining") is not None:
        th["Matrix_free_pct"] = round(100.0 * mx["freeMinted"] / (mx["freeMinted"] + mx["freeRemaining"]), 1)
    lg = reads.get("Ledgera", {}).get("views", {})
    th["Ledgera_freeClaimed"] = lg.get("freeClaimed")
    ab = reads.get("AgentBubble", {}).get("views", {})
    if ab.get("freeMinted") is not None and ab.get("MAX_SUPPLY"):
        th["AgentBubble_free_pct"] = round(100.0 * ab["freeMinted"] / ab["MAX_SUPPLY"], 1)
    th["AgentBubble_freeMinted"] = ab.get("freeMinted")
    th["AgentBubble_MAX_SUPPLY"] = ab.get("MAX_SUPPLY")
    pf = reads.get("PIXELFROGS", {}).get("views", {})
    if pf.get("freeMinted") is not None and pf.get("freeLeft") is not None:
        th["PIXELFROGS_free_pct"] = round(100.0 * pf["freeMinted"] / (pf["freeMinted"] + pf["freeLeft"]), 1)
    th["notes"] = ("Strong-lead bar >70% + age <24h + slot open. None above 70% => no promotion. "
                   "PIXELFROGS free% uses freeMinted/(freeMinted+freeLeft). "
                   "AgentBubble above 70% but launch age still UNVERIFIED (no saleStart/ "
                   "mintOpensAt view, carried from 0204 run) => NO strong-lead promotion. "
                   "bsccat website gate PASS carried from 02:17 WIB live read (bsccat.com "
                   "prints exact mint contract 0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A twice; "
                   "registry 0x60B9...022F printed) - site NOT re-read this run.")
    out["threshold_check"] = th
except Exception as e:
    out["threshold_check"] = {"error": str(e)[:120]}

# ---- Bridge (read-only) ----
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

# ---- Poffzi fcfs liveness (informational only) ----
try:
    _pg = subprocess.run(["pgrep", "-af", "fcfs_fast"], capture_output=True, text=True, timeout=10)
    out["poffzi_fcfs"] = _pg.stdout.strip()[:300] or "NO PROCESS FOUND"
except Exception as e:
    out["poffzi_fcfs"] = f"check failed: {e}"

out["elapsed_s"] = round(time.time() - T0, 1)
out["executions"] = "none - no preview, no mint, no claim (this script is read-only)"
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-18-0419.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:14000])
