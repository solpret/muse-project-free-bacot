#!/usr/bin/env python3
"""free-mint-search run 2026-11-17 07:31 WIB. Read-only legs 1-5 + bridge.
Reuses hot-leg run.py patterns (batch_read chunked 8 + curl fallback).
Writes: run-2026-11-17-0731-reread.json, run-2026-11-17-0731-sourcify.json,
run-2026-11-17-0731-feedshape.json, run-2026-11-17-0731-runlog.md.
Updates snapshot ONLY with last_run_wib + runNote0731_1117 (no other keys).
No preview/mint/claim. Ankr scan leg: pre-flight only (401 x19 history -> expect
fast-fail; scan NOT launched on pre-flight failure)."""
import json, re, subprocess, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from eth_hash.auto import keccak
import fast_rpc

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
T0 = time.time()
NOW = "2026-11-17 07:31 WIB"

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "free-mint-search/1.0"})
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

def curl_batch(calls, timeout=15):
    out = []
    for i in range(0, len(calls), 5):
        chunk = calls[i:i+5]
        payload = [{"jsonrpc": "2.0", "id": j+1, "method": "eth_call",
                    "params": [{"to": to, "data": data}, "latest"]}
                   for j, (to, data) in enumerate(chunk)]
        r = subprocess.run(["curl", "-s", "--max-time", str(timeout),
                            "https://bsc-dataseed.binance.org/",
                            "-H", "Content-Type: application/json",
                            "-d", json.dumps(payload)],
                           capture_output=True, timeout=timeout+5)
        if r.returncode != 0 or not r.stdout:
            raise IOError(f"curl batch failed rc={r.returncode}")
        resp = json.loads(r.stdout.decode())
        by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
        for j in range(len(chunk)):
            it = by_id.get(j+1, {})
            if "result" in it and it["result"] not in (None, "0x"):
                try:
                    out.append(int(it["result"], 16))
                except Exception:
                    out.append(it["result"])
            else:
                out.append(None)
    return out

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

def batch_read_fallback(calls, timeout=15):
    try:
        return batch_read_chunk(calls, timeout=timeout)
    except Exception:
        return curl_batch(calls, timeout=timeout), "direct-curl-bsc-dataseed"

out = {"run": "free-mint-search 2026-11-17 07:31 WIB", "started_wib": NOW}

# ---- Pre-flight Ankr (route 4 gate; fast-fail on failure) ----
try:
    from ankr import ankr_post
    from fast_rpc import _single
    EPS = ["https://bsc-dataseed.binance.org/",
           "https://bsc-dataseed1.bnbchain.org/",
           "https://bsc-dataseed2.bnbchain.org/",
           "https://bsc-dataseed3.bnbchain.org/"]
    latest = None
    for ep in EPS:
        try:
            latest = int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
            break
        except Exception:
            continue
    if latest is None:
        raise IOError("eth_blockNumber failed on all public endpoints")
    TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    ZERO_TOPIC = "0x" + "00" * 32
    params = {"blockchain": "bsc", "fromBlock": hex(latest - 49),
              "toBlock": hex(latest), "pageSize": 1000,
              "decodeLogs": False, "topics": [TRANSFER, ZERO_TOPIC]}
    t_pf = time.time()
    body = ankr_post("ankr_getLogs", params, timeout=30)
    result = body.get("result", {}) if isinstance(body, dict) else {}
    out["ankr_preflight"] = {"status": "OK", "head": latest,
                             "chunk": [latest - 49, latest],
                             "logs_returned": len(result.get("logs", [])),
                             "elapsed_s": round(time.time() - t_pf, 2)}
    out["scan_leg"] = "pre-flight OK - scan NOT launched in this run (30-min job runs pre-flight only; full scan is backfill/driver scope, watermark unchanged)"
except Exception as e:
    out["ankr_preflight"] = {"status": "FAIL", "error": f"{type(e).__name__}: {str(e)[:300]}"}
    out["scan_leg"] = ("FAST-FAIL: pre-flight failed, scan leg skipped for this run per 2026-11-06 amendment; "
                       "watermark NOT advanced; triage + 5c skipped (no scan output)")

# ---- Leg 1: Sourcify feed ----
seen = json.load(open(f"{HF}/hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
try:
    try:
        raw = fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc")
    except Exception:
        r = subprocess.run(["curl", "-s", "-L", "--max-time", "20",
                            "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"],
                           capture_output=True, timeout=25)
        if r.returncode != 0 or not r.stdout:
            raise IOError(f"curl fallback failed rc={r.returncode}")
        raw = r.stdout
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
    json.dump(feed if isinstance(feed, list) else items,
              open(f"{HF}/run-2026-11-17-0731-sourcify.json", "w"), indent=1)
except Exception as e:
    out["sourcify_feed"] = {"error": f"{type(e).__name__}: {e}"}
    new1 = []

# ---- Leg 2: Boltbook EN + ZH ----
def curl_get(url, out_path, timeout=20):
    r = subprocess.run(["curl", "-s", "-L", "-A",
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
                        "--max-time", str(timeout), url, "-o", out_path, "-w", "%{http_code}"],
                       capture_output=True, text=True, timeout=timeout + 5)
    return r.stdout.strip()

def boltbook(lang):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    path = f"{HF}/run-2026-11-17-0731-boltbook-{lang}.html"
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

# ---- Leg 3: shape-check new contracts (feed + boltbook) ----
targets = []
for a, _ in new1:
    targets.append(a)
for lang in ("en", "zh"):
    b = out.get(f"boltbook_{lang}", {})
    targets += [a for a in b.get("new_contracts", [])]
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
_sc = []
for a in targets:
    _sc.append(shape_check(a))
out["shape_check"] = _sc
out["shape_hits"] = [s for s in _sc if s.get("S1") or s.get("S2")]
json.dump({s["address"]: s for s in _sc},
          open(f"{HF}/run-2026-11-17-0731-feedshape.json", "w"), indent=1)

# ---- Leg 4: full watchlist re-read (41 items from 23:01 reread + hot-leg PLAN) ----
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
 ("Flare-bd6f", "0xbd6ff7ed8fe96b79cb3cbf9dc32656ff7a98a599",
  [("totalSupply", "totalSupply()", None)]),
 ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
  [("freeSharesLeft", "freeSharesLeft()", None), ("openedAt", "openedAt()", None),
   ("freeClaimed", "freeClaimed()", None), ("freeBooked_user", "freeBooked(address)", "user")]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", "launched()", None), ("failed", "failed()", None),
   ("isRefundPhase", "isRefundPhase()", None), ("totalShares", "totalShares()", None),
   ("tokenClaimed_user", "tokenClaimed(address)", "user")]),
 # --- extra 25 from 23:01 full reread (not in hot-leg PLAN) ---
 ("NOISE", "0xBA5352A3A05Ec637394810D791a412E78A349247",
  [("totalMinted", "totalMinted()", None), ("remainingSupply", "remainingSupply()", None),
   ("mintOpen", "mintOpen()", None), ("MAX_SUPPLY", "MAX_SUPPLY()", None),
   ("freeUsed_user", "freeUsed(address)", "user")]),
 ("Zero", "0x89B340435e4fD27e00442f7F1b3a3b3244b4E647",
  [("totalSupply", "totalSupply()", None), ("freeClaimed", "freeClaimed()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("HIVE", "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77",
  [("totalSupply", "totalSupply()", None), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("WANGCAI", "0x61A2ff9Be3db25e23886bC59D92d44fAa05959Cd",
  [("totalSupply", "totalSupply()", None), ("freeClaimed", "freeClaimed()", None),
   ("FREE_SUPPLY", "FREE_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("mintedBy_user", "mintedBy(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("YUANBAO", "0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E",
  [("totalSupply", "totalSupply()", None), ("freeClaimed", "freeClaimed()", None),
   ("FREE_SUPPLY", "FREE_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("mintedBy_user", "mintedBy(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("PX24", "0xe712510fcb27935e657e41ebb97982d6b123136c",
  [("totalSupply", "totalSupply()", None), ("freeClaimed", "freeClaimed()", None)]),
 ("LumenFindings", "0x4158B701EaA30E8FaDBaA526F70780A38318c1C4",
  [("totalSpecimens", "totalSpecimens()", None), ("currentExperiment", "currentExperiment()", None),
   ("genesisStart", "genesisStart()", None), ("genesisOpen", "genesisOpen()", None),
   ("holdsAgentId_user", "holdsAgentId(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("ORBIT", "0x7d5F7f323db3050AF92E9aa1584E883B3b24d680",
  [("freeClaimed", "freeClaimed()", None), ("FREE_MAX", "FREE_MAX()", None),
   ("claimOpen", "claimOpen()", None), ("hasFreeClaimed_user", "hasFreeClaimed(address)", "user"),
   ("totalSupply", "totalSupply()", None)]),
 ("TrashBandits".strip(), "0x2d61347D9b48De99cBdF0D8D7a2DD73f5B15E90D",
  [("totalMinted", "totalMinted()", None), ("MAX_SUPPLY", "MAX_SUPPLY()", None),
   ("mintOpen", "mintOpen()", None), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("SKRR", "0x9081f02876c173d0c69f042959cfd0d61c668b17",
  [("totalSupply", "totalSupply()", None), ("freeClaimed", "freeClaimed()", None)]),
 ("FrieAgent-B751", "0xb7517e3b31107695f2f8837fafc76999b956c871",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintedBy_user", "mintedBy(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("FrieAgent-c64d", "0xc64da7479c5abc8e6dfadeb4d17502ebcf9837e5",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintedBy_user", "mintedBy(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("MAMI", "0xfe36c6d7a1e352cd0822c6818269d190e8e63c13",
  [("totalSupply", "totalSupply()", None), ("freeClaimed", "freeClaimed()", None),
   ("FREE_SUPPLY", "FREE_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("mintedBy_user", "mintedBy(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("INKI", "0x5ae38f527340e1aaf4ea214f9778bdc2266e2bd7",
  [("totalSupply", "totalSupply()", None), ("freeClaimed", "freeClaimed()", None),
   ("FREE_SUPPLY", "FREE_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("mintedBy_user", "mintedBy(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("HashcatDepot", "0x5aff123300685b6e08aa4396227baf44aabbd4ed",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("mintsLeft", "mintsLeft()", None), ("mintedBy_user", "mintedBy(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("OTV", "0xfab9c88d25e111edd68a2cca3e0f650863a5bf25",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("FREE_MINT_CAP", "FREE_MINT_CAP()", None), ("freeMintsLeft", "freeMintsLeft()", None),
   ("PRICE", "PRICE()", None), ("mintOpen", "mintOpen()", None)]),
 ("HANAMI", "0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640",
  [("totalSupply", "totalSupply()", None), ("freeMinted", "freeMinted()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("CosmicSentinel", "0x88731d1eb41c36f3d705fdb58b658244c06afc36",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("MAX_SUPPLY", "MAX_SUPPLY()", None),
   ("mintOpen", "mintOpen()", None), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("DogeRageFi", "0x097ff90fce52f4f0e1f41d6f8c799db9cd67099f",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeSupply", "freeSupply()", None), ("maxSupply", "maxSupply()", None),
   ("mintOpen", "mintOpen()", None), ("mintedBy_user", "mintedBy(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("ALIEN", "0xf5767ac3beb8bbfaf4596dfc1925fc5aca779dcb",
  [("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None),
   ("FREE_SUPPLY", "FREE_SUPPLY()", None), ("MAX_SUPPLY", "MAX_SUPPLY()", None),
   ("isFreePhase", "isFreePhase()", None), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Punch Card", "0x1d4ef0587dd3ff3875a141d4711c60bca40587c4",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("mintOpen", "mintOpen()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("PXIO", "0x58e8f1b34B60687B36BCdc78e02a2fd443De71Ab",
  [("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None),
   ("mintedBy_user", "mintedBy(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Poffzi", "0x3D7A6e3d007990B36ab092404C9027a3CD989C14",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("saleStart", "saleStart()", None),
   ("saleEnd", "saleEnd()", None), ("saleOpen", "saleOpen()", None),
   ("balanceOf_user", "balanceOf(address)", "user"),
   ("freeDone_user", "freeDone(address)", "user")]),
 ("Vezlune", "0xA9531f2C18E9398b50c13f1a108EbE7462927154",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("DRAGON", "0xfc191b76041498b14dcae3c802af3389c74263e6",
  [("totalMinted", "totalMinted()", None), ("freeMinted", "freeMinted()", None),
   ("FREE_SUPPLY", "FREE_SUPPLY()", None), ("MAX_SUPPLY", "MAX_SUPPLY()", None),
   ("mintStart", "mintStart()", None), ("mintEnd", "mintEnd()", None),
   ("mintEnded", "mintEnded()", None), ("freeRemaining", "freeRemaining()", None),
   ("paidMinted", "paidMinted()", None), ("hasClaimedFree_user", "hasClaimedFree(address)", "user"),
   ("mintedBy_user", "mintedBy(address)", "user"), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("XCOPY", "0x3fbec44c7c845374267b06033940abe45c63edfa",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("remaining", "remaining()", None), ("mintedCount", "mintedCount()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
]
calls, meta = [], []
_cost_data = "0x" + sel("cost(address,uint256)") + "0"*24 + USER[2:].lower() + "%064x" % 1
calls.append(("0x1b8894391a3dcfe7e248c321103265ab52e273e0", _cost_data))
meta.append(("JADE", "0x1b8894391a3dcfe7e248c321103265ab52e273e0", "cost_user_1"))
for name, addr, views in PLAN:
    for label, sig, arg in views:
        calls.append(call(addr, sig, arg))
        meta.append((name, addr, label))
reread = {}
ep_used = None
chunk_errors = []
for i in range(0, len(calls), 8):
    chunk = calls[i:i + 8]
    try:
        res, ep_used = batch_read_chunk(chunk)
    except Exception:
        try:
            res = curl_batch(chunk)
            ep_used = "direct-curl-bsc-dataseed"
        except Exception as e2:
            chunk_errors.append(f"calls {i}-{i + len(chunk) - 1} (curl fallback): {type(e2).__name__}: {str(e2)[:150]}")
            for name, addr, label in meta[i:i + 8]:
                reread.setdefault(name, {"address": addr, "views": {}})["views"][label] = None
            continue
    for (name, addr, label), val in zip(meta[i:i + 8], res):
        reread.setdefault(name, {"address": addr, "views": {}})["views"][label] = val
out["leg4_reread"] = {"reads": reread, "reads_ok": len(reread), "reads_total": len(PLAN),
                      "endpoint": ep_used, "n_calls": len(calls),
                      "chunk_size": 8, "chunk_errors": chunk_errors}
try:
    payload = json.dumps([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}]).encode()
    req = urllib.request.Request(ep_used or "https://bsc-dataseed.binance.org/",
                                 data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        out["leg4_reread"]["block"] = int(json.loads(r.read().decode())[0]["result"], 16)
except Exception as e:
    out["leg4_reread"]["block_error"] = str(e)[:120]
out["leg4_reread"]["elapsed_s"] = round(time.time() - T0, 1)

# ---- Diff vs 04:31 reread + threshold check ----
try:
    prev = json.load(open(f"{HF}/run-2026-11-17-0701-reread.json"))
    prev_reads = prev.get("reads", {})
    diffs = {}
    for name, cur in reread.items():
        pv = prev_reads.get(name, {}).get("views", {})
        cv = cur.get("views", {})
        d = {k: [pv.get(k), cv.get(k)] for k in cv if pv.get(k) != cv.get(k)}
        if d:
            diffs[name] = d
    out["leg4_changes_vs_0701"] = diffs
except Exception as e:
    out["leg4_changes_vs_0701"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
try:
    th = {}
    ag = reread.get("AGCLUB", {}).get("views", {})
    if ag.get("freeMinted") is not None and ag.get("FREE_CAP"):
        th["AGCLUB_free_pct"] = round(100.0 * ag["freeMinted"] / ag["FREE_CAP"], 1)
    mx = reread.get("Matrix", {}).get("views", {})
    if mx.get("freeMinted") is not None and mx.get("FREE_MAX"):
        th["Matrix_free_pct"] = round(100.0 * mx["freeMinted"] / mx["FREE_MAX"], 1)
    lg = reread.get("Ledgera", {}).get("views", {})
    if lg.get("freeClaimed") is not None and lg.get("FREE_SUPPLY"):
        th["Ledgera_free_pct"] = round(100.0 * lg["freeClaimed"] / lg["FREE_SUPPLY"], 1)
    rc = reread.get("RaceAgents", {}).get("views", {})
    if rc.get("freeMinted") is not None and rc.get("FREE_MAX"):
        th["RaceAgents_free_pct"] = round(100.0 * rc["freeMinted"] / rc["FREE_MAX"], 1)
    out["threshold_check"] = th
except Exception as e:
    out["threshold_check"] = {"error": str(e)[:120]}

# ---- PEPE re-read (track-C, audit-blocked) ----
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
    try:
        _pr, _ep2 = batch_read_chunk(_pepe_calls)
    except Exception:
        _pr = curl_batch(_pepe_calls)
        _ep2 = "direct-curl-bsc-dataseed"
    out["pepe_reread"] = dict(zip(_pepe_labels, _pr))
except Exception as e:
    out["pepe_reread"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

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

out["executions"] = "none - no preview, no mint, no claim (this run is read-only unless a new strong lead/candidate passes all gates + safety; see runlog)"
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{HF}/run-2026-11-17-0731.json", "w"), indent=1)
json.dump({"started_wib": NOW, "reads": reread,
           "reads_ok": len(reread), "reads_total": len(PLAN),
           "block": out["leg4_reread"].get("block"),
           "elapsed_s": out["leg4_reread"].get("elapsed_s")},
          open(f"{HF}/run-2026-11-17-0731-reread.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:14000])
