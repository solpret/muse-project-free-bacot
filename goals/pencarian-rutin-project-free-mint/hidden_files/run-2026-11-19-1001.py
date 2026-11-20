#!/usr/bin/env python3
"""Run 2026-11-19 10:01 WIB. Run 2026-11-19 10:01 WIB: same PLAN as 0701 (Vitaliq Scans removed: age-excluded run 0701).
Pre-flight + re-read + Boltbook; per-chunk incremental persist to reread JSON,
curl timeout 40s, 3 workers. Read-only except snapshot merge by separate script."""
import json, re, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from eth_hash.auto import keccak
from quicknode import ProxyHTTPSConnection
from dynamic_credentials import dynamic_credential_entry
QN_HOST = "stylish-thrilling-star.bsc.quiknode.pro"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
def https_get(host, path, timeout=20, redirects=3):
    conn = ProxyHTTPSConnection(host, 443, timeout=timeout)
    try:
        conn.request("GET", path, headers={"User-Agent": UA, "Accept": "*/*"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
        loc = resp.getheader("Location")
    finally:
        conn.close()
    if status in (301,302,303,307,308) and loc and redirects > 0:
        if loc.startswith("http"):
            from urllib.parse import urlparse
            u = urlparse(loc)
            return https_get(u.hostname, u.path + ("?" + u.query if u.query else ""), timeout, redirects-1)
        return https_get(host, loc, timeout, redirects-1)
    return status, raw
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
now_wib = "2026-11-19 10:01 WIB"
RPC_URL = "https://bsc-dataseed.binance.org/"
out = {"run": "free-mint-search 2026-11-19 10:01 WIB (run)", "started_wib": now_wib}
# ---- RPC helpers ----
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

def curl_json(url, payload, timeout=40):
    # url ignored: all JSON-RPC goes via Quicknode tunnel (dataseed curl dead since 16:29)
    entry = dynamic_credential_entry("custom.quicknode")
    surrogate = str(entry["surrogate"]).strip()
    conn = ProxyHTTPSConnection(QN_HOST, 443, timeout=timeout)
    try:
        conn.request("POST", f"/{surrogate}/", body=json.dumps(payload).encode(),
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
    finally:
        conn.close()
    if status != 200:
        raise IOError(f"quicknode http {status}: {raw[:150]!r}")
    return json.loads(raw.decode())

def rpc_batch(calls, timeout=25):
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    resp = curl_json(RPC_URL, payload, timeout=timeout)
    if not isinstance(resp, list):
        raise IOError(f"non-list batch response: {str(resp)[:200]}")
    by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
    res = []
    for i in range(len(calls)):
        it = by_id.get(i + 1, {})
        if "result" in it and it["result"] not in (None, "0x"):
            try:
                res.append(int(it["result"], 16))
            except Exception:
                res.append(it["result"])
        elif "error" in it:
            res.append(f"err:{it['error']}")
        else:
            res.append(None)
    return res

def rpc_batch_chunked(calls, chunk=5):
    # 1331 fix: sequential curl batches (56 x ~7s) blew the 420s budget on
    # 1301-style egress (run 1331 first attempt: killed at 420s, zero output).
    # Run chunks in parallel (8 workers); per-item error semantics unchanged.
    import concurrent.futures as _cf
    idxs = list(range(0, len(calls), chunk))
    out = [None] * len(idxs)
    errors = []
    def _one(j):
        i = idxs[j]
        try:
            r = rpc_batch(calls[i:i + chunk])
            print(f"chunk {j + 1}/{len(idxs)} calls {i}-{i + len(calls[i:i+chunk]) - 1} OK", flush=True)
            return j, r, None
        except Exception as e:
            print(f"chunk {j + 1}/{len(idxs)} calls {i}-{i + len(calls[i:i+chunk]) - 1} FAIL {type(e).__name__}", flush=True)
            return j, [None] * len(calls[i:i + chunk]), f"calls {i}-{i + len(calls[i:i+chunk]) - 1}: {type(e).__name__}: {str(e)[:150]}"
    with _cf.ThreadPoolExecutor(max_workers=4) as ex:
        for j, r, err in ex.map(_one, range(len(idxs))):
            out[j] = r
            if err:
                errors.append(err)
    res = []
    for r in out:
        res += r
    return res, errors

# ---- Scan pre-flight (real, small ankr_getLogs, <60s) ----
try:
    import sys as _s2; _s2.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
    from ankr import ankr_post as _ankr_post
    _blk = curl_json(RPC_URL, [{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}], timeout=40)
    _head = int(_blk[0]["result"], 16)
    _pf = _ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": _head - 50, "toBlock": _head,
        "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                   "0x0000000000000000000000000000000000000000000000000000000000000000"]}, timeout=45)
    out["preflight"] = {"ok": True, "head": _head, "logs_returned": len(_pf.get("logs", [])) if isinstance(_pf, dict) else "n/a"}
    out["scan_leg"] = "PRE-FLIGHT OK - scan script run separately (bounded, see runlog)"
except Exception as _e:
    out["preflight"] = {"ok": False, "error": f"{type(_e).__name__}: {str(_e)[:150]}"}
    out["scan_leg"] = "FAST-FAIL (pre-flight failed); watermark NOT advanced"
def curl_get(url, out_path, timeout=25):
    from urllib.parse import urlparse
    u = urlparse(url)
    status, raw = https_get(u.hostname, u.path + ("?" + u.query if u.query else ""), timeout=timeout)
    html = raw.decode("utf-8", errors="replace")
    open(out_path, "w").write(html)
    return html, str(status)

PLAN = [
 ("HIVE Agents", "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77",
  [("totalSupply", "totalSupply()", None), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("PUNNY", "0xaFAE0Bf373ad87E88555afe1605111F66C99062C",
  [("totalMinted", "totalMinted()", None), ("freeMinted", "freeMinted()", None),
   ("freeRemaining", "freeRemaining()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("mintStart", "mintStart()", None), ("mintClosed", "mintClosed()", None),
   ("hasClaimedFree_user", "hasClaimedFree(address)", "user"),
   ("mintedBy_user", "mintedBy(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Bubblebruin", "0xc205F8c74733D914776D66cBc4Cf10BF701D96Aa",
  [("totalSupply", "totalSupply()", None), ("freeClaimed", "freeClaimed()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Matrix", "0x1F669b714337F3C2585072c53fdDD89581F928fF",
  [("freeMinted", "freeMinted()", None), ("freeRemaining", "freeRemaining()", None),
   ("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None)]),
 ("AGCLUB", "0x67270bb351515abf3089ca5420456897363f5e75",
  [("totalMinted", "totalMinted()", None), ("freeMinted", "freeMinted()", None),
   ("FREE_CAP", "FREE_CAP()", None), ("mintOpen", "mintOpen()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Ledgera", "0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d",
  [("freeClaimed", "freeClaimed()", None), ("totalSupply", "totalSupply()", None),
   ("mintOpen", "mintOpen()", None), ("freeUsed_user", "freeUsed(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
  [("freeSharesLeft", "freeSharesLeft()", None), ("openedAt", "openedAt()", None),
   ("freeClaimed", "freeClaimed()", None), ("freeBooked_user", "freeBooked(address)", "user")]),
 ("AONE-sale", "0x84D82E933D7781fe11245e7bbd3Eb23dbb963666",
  [("freeMinted", "freeMinted()", None), ("freeQuotaLeft", "freeQuotaLeft()", None),
   ("FREE_TOTAL", "FREE_TOTAL()", None), ("LAUNCH", "LAUNCH()", None),
   ("freeTaken_user", "freeTaken(address)", "user"),
   ("quote_user_1", "quote(address,uint256)", "user1")]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", "launched()", None), ("failed", "failed()", None),
   ("isRefundPhase", "isRefundPhase()", None), ("totalShares", "totalShares()", None),
   ("tokenClaimed_user", "tokenClaimed(address)", "user")]),
 ("ARKYN", "0x69b0b5756671680766d232eb4b0f39a34be5d852",
  [("totalMinted", "totalMinted()", None), ("totalSupply", "totalSupply()", None)]),
 ("Lumenhold", "0x9701980b0afd825134390ee46fb3bd675a2f356f",
  [("totalSupply", "totalSupply()", None), ("freeClaimed", "freeClaimed()", None)]),
 ("AgentNOVA", "0x43462d7f269fde4914b03e1e07067a61b62b9540",
  [("totalSupply", "totalSupply()", None)]),
 ("STOCK AGENT", "0xba7068233da805bdebcc167be361c219002e6b7f",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
   ("freeLeft", "freeLeft()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("cost_user_1", "cost(address,uint256)", "user1"), ("quote_user_1", "quote(address,uint256)", "user1"),
   ("freeMintedByWallet_user", "freeMintedByWallet(address)", "user"),
   ("mintedCount_user", "mintedCount(address)", "user"),
   ("freeClaimed_user", "freeClaimed(address)", "user"),
   ("freeUsed_user", "freeUsed(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("AgentMintPass", "0xfcadfb7cc85b6ea540d64e4f4b9f162e630f55c0",
  [("totalMinted", "totalMinted()", None), ("balanceOf_user", "balanceOf(address)", "user"),
   ("mintedCount_user", "mintedCount(address)", "user")]),
 ("AGATE-Pass", "0x5b63bd45e61a2e6540548c3509b598b6384206c5",
  [("totalMinted", "totalMinted()", None), ("balanceOf_user", "balanceOf(address)", "user"),
   ("hasMinted_user", "hasMinted(address)", "user")]),
 ("AgentDrop", "0x1dd8740ffca0be3caac3b4a3eb41fdff506e38a9",
  [("totalMinted", "totalMinted()", None), ("balanceOf_user", "balanceOf(address)", "user"),
   ("hasMinted_user", "hasMinted(address)", "user")]),
 ("THYRK", "0x4d90ffc3075fb8897edff6d7c6269c906664a20e",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
   ("freeLeft", "freeLeft()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("cost_user_1", "cost(address,uint256)", "user1"), ("quote_user_1", "quote(address,uint256)", "user1"),
   ("freeMintedByWallet_user", "freeMintedByWallet(address)", "user"),
   ("mintedCount_user", "mintedCount(address)", "user"),
   ("freeClaimed_user", "freeClaimed(address)", "user"),
   ("freeUsed_user", "freeUsed(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
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


# ---- incremental re-read (persist after every chunk) ----
import concurrent.futures as _cf
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
CHUNK = 5
idxs = list(range(0, len(calls), CHUNK))
res = [None] * len(calls)
chunk_errors = []
def _one(i):
    try:
        r = rpc_batch(calls[i:i+CHUNK], timeout=40)
        print(f"chunk calls {i}-{i+len(calls[i:i+CHUNK])-1} OK", flush=True)
        return i, r, None
    except Exception as e:
        print(f"chunk calls {i}-{i+len(calls[i:i+CHUNK])-1} FAIL {type(e).__name__}", flush=True)
        return i, [None]*len(calls[i:i+CHUNK]), f"calls {i}-{i+len(calls[i:i+CHUNK])-1}: {type(e).__name__}: {str(e)[:150]}"
def _persist():
    reads, bsccat, pepe = {}, {"address": BSCCAT_ADDR, "views": {}}, {}
    for (name, addr, label), val in zip(meta, res):
        if name == "bsccat":
            bsccat["views"][label] = val
        elif name == "pepe":
            pepe[label] = val
        else:
            reads.setdefault(name, {"address": addr, "views": {}})[ "views"][label] = val
    global _cached_block
    if _cached_block is None:
        try:
            blk = curl_json(RPC_URL, [{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}], timeout=40)
            _cached_block = int(blk[0]["result"], 16)
        except Exception as e:
            _cached_block = f"error: {str(e)[:120]}"
    block = _cached_block
    json.dump({"reads": reads, "bsccat": bsccat, "pepe": pepe, "errors": chunk_errors,
               "n_calls": len(calls), "elapsed_s": round(time.time()-T0, 1), "block": block},
              open(f"{HF}/run-2026-11-19-1001-reread.json", "w"), indent=1)
    return block
_cached_block = None
block = None
with _cf.ThreadPoolExecutor(max_workers=3) as ex:
    futs = {ex.submit(_one, i): i for i in idxs}
    done = 0
    for fut in _cf.as_completed(futs):
        i, r, err = fut.result()
        res[i:i+len(r)] = r
        if err: chunk_errors.append(err)
        done += 1
        print(f"progress {done}/{len(idxs)} chunks", flush=True)
        block = _persist()
out["leg4_block"] = block
out["leg4_chunk_errors"] = chunk_errors
out["leg4_n_calls"] = len(calls)
out["leg4_chunks_done"] = done

# ---- Route 2: Boltbook EN + ZH ----
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        html, code = curl_get(url, f"{HF}/run-2026-11-19-1001-boltbook-{lang}.html")
        addrs = sorted(set(ADDR_RE.findall(html)))
        out[f"boltbook_{lang}"] = {"bytes": len(html), "http_code": code,
            "full_address_contracts": len(addrs), "addresses": addrs,
            "free_kw": html.lower().count("free mint") + html.lower().count("free-mint")}
    except Exception as e:
        out[f"boltbook_{lang}"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
out["elapsed_s"] = round(time.time() - T0, 1)
out["executions"] = "none - no preview, no mint, no claim (this script is read-only)"
json.dump(out, open(f"{HF}/run-2026-11-19-1001.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("preflight", "scan_leg", "leg4_block", "leg4_chunk_errors", "boltbook_en", "boltbook_zh", "elapsed_s") if k in out}, indent=1, default=str)[:4000])
