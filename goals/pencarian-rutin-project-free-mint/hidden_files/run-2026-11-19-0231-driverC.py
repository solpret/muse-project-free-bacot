#!/usr/bin/env python3
"""Run 2026-11-19 02:31 WIB, driver C: verify new leads found this run.
- Sweep leads (Boltbook post z47wuf650ZFf): AgentMintPass 0xfcad..., AGATE Pass
  0x5b63..., AgentDrop 0x1dd8... (none in snapshot; none reported by hot-leg).
- Bridge not-in-snapshot: 0x01f9ca4ff95d49594cc8b6591022186dc5c1bc72.
- Boltbook-new dynamic (driver B): 0x6b21..., 0x7aca..., 0xccda... (shape S1/S2 false;
  re-check agent-shape + free views on-chain).
Read-only. Sourcify ABI + Quicknode batch reads + Boltbook post fetch."""
import json, re, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from eth_hash.auto import keccak
from quicknode import ProxyHTTPSConnection
from dynamic_credentials import dynamic_credential_entry
QN_HOST = "stylish-thrilling-star.bsc.quiknode.pro"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
out = {"run": "free-mint-search 2026-11-19 02:31 WIB (driver C: new-lead verify)"}

def https_get(host, path, timeout=25, redirects=3):
    conn = ProxyHTTPSConnection(host, 443, timeout=timeout)
    try:
        conn.request("GET", path, headers={"User-Agent": UA, "Accept": "*/*"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
        loc = resp.getheader("Location")
    finally:
        conn.close()
    if status in (301, 302, 303, 307, 308) and loc and redirects > 0:
        if loc.startswith("http"):
            from urllib.parse import urlparse
            u = urlparse(loc)
            return https_get(u.hostname, u.path + ("?" + u.query if u.query else ""), timeout, redirects - 1)
        return https_get(host, loc, timeout, redirects - 1)
    return status, raw

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

def curl_json(payload, timeout=40):
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

def rpc_batch(calls, timeout=40):
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    resp = curl_json(payload, timeout=timeout)
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
            res.append("revert")
        else:
            res.append(None)
    return res

TARGETS = [
 ("AgentMintPass", "0xfcadfb7cc85b6ea540d64e4f4b9f162e630f55c0"),
 ("AGATE-Pass", "0x5b63bd45e61a2e6540548c3509b598b6384206c5"),
 ("AgentDrop", "0x1dd8740ffca0be3caac3b4a3eb41fdff506e38a9"),
 ("bridge-0x01f9", "0x01f9ca4ff95d49594cc8b6591022186dc5c1bc72"),
 ("bb-new-0x6b21", "0x6b2180b08d9fb0ec94fa02685dcdcc26712bf85d"),
 ("bb-new-0x7aca", "0x7acaa1d0853055cd1af9615e4cc46c6c591521d2"),
 ("bb-new-0xccda", "0xccda6fa01b7ac7475c344b5717f1f59634823d07"),
]
VIEWS = [
 ("name", "name()", None), ("symbol", "symbol()", None),
 ("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
 ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
 ("freeLeft", "freeLeft()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
 ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
 ("mintedBy_user", "mintedBy(address)", "user"),
 ("freeClaimed_user", "freeClaimed(address)", "user"),
 ("hasClaimedFree_user", "hasClaimedFree(address)", "user"),
 ("freeMintedByWallet_user", "freeMintedByWallet(address)", "user"),
 ("balanceOf_user", "balanceOf(address)", "user"),
 ("quote_user_1", "quote(address,uint256)", "user1"),
 ("cost_user_1", "cost(address,uint256)", "user1"),
 ("agentRegistry", "agentRegistry()", None), ("registry", "registry()", None),
 ("contractURI", "contractURI()", None),
]

# ---- Sourcify ABI shape per target ----
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted",
              "freeCardsRemaining"}
def sourcify_shape(addr):
    try:
        st, raw = https_get("sourcify.dev", f"/server/v2/contract/56/{addr}?fields=abi", timeout=25)
        meta = json.loads(raw.decode()); abi = meta.get("abi", [])
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
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        agent_shaped = agent_ref or has_mint and bool(free_views) or bool(names & {"FREE_SUPPLY", "freeMinted", "freeClaimed"})
        return {"verified": True, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token,
                "agent_shaped": agent_shaped, "n_fns": len(names), "verifiedAt": meta.get("verifiedAt"),
                "fn_names": sorted(names)}
    except Exception as e:
        return {"verified": False, "error": f"{type(e).__name__}: {str(e)[:120]}"}

# ---- Boltbook post fetch (launch-time evidence for the 3 sweep leads) ----
try:
    st, raw = https_get("boltbook.fun", "/p/z47wuf650ZFf?lang=en", timeout=25)
    html = raw.decode("utf-8", errors="replace")
    open(f"{HF}/run-2026-11-19-0231-boltbook-post-z47w.html", "w").write(html)
    m = re.findall(r"(2026-11-1[89][T ][0-9:]+(?:Z|\+07:00)?)", html)
    m2 = re.findall(r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})", html)
    out["boltbook_post"] = {"http": st, "bytes": len(html),
        "addrs_found": sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html))),
        "date_strings": sorted(set(m + m2))[:10]}
except Exception as e:
    out["boltbook_post"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# ---- on-chain reads ----
import concurrent.futures as _cf
calls, meta = [], []
for name, addr in TARGETS:
    for label, sig, arg in VIEWS:
        calls.append((addr, encode(sig, arg)))
        meta.append((name, addr, label))
CHUNK = 5
idxs = list(range(0, len(calls), CHUNK))
res = [None] * len(calls)
errors = []
def _one(i):
    try:
        r = rpc_batch(calls[i:i+CHUNK], timeout=40)
        print(f"chunk {i}-{i+len(calls[i:i+CHUNK])-1} OK", flush=True)
        return i, r, None
    except Exception as e:
        print(f"chunk {i}-{i+len(calls[i:i+CHUNK])-1} FAIL {type(e).__name__}", flush=True)
        return i, [None]*len(calls[i:i+CHUNK]), f"calls {i}-{i+len(calls[i:i+CHUNK])-1}: {type(e).__name__}: {str(e)[:150]}"
with _cf.ThreadPoolExecutor(max_workers=4) as ex:
    for i, r, err in ex.map(_one, idxs):
        res[i:i+len(r)] = r
        if err:
            errors.append(err)
reads = {}
for (name, addr, label), val in zip(meta, res):
    reads.setdefault(name, {"address": addr, "views": {}})["views"][label] = val
try:
    blk = curl_json([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}], timeout=40)
    block = int(blk[0]["result"], 16)
except Exception as e:
    block = f"error: {str(e)[:120]}"
out["block"] = block
out["errors"] = errors
out["n_calls"] = len(calls)
for name, addr in TARGETS:
    reads[name]["sourcify"] = sourcify_shape(addr)
out["reads"] = reads
out["elapsed_s"] = round(time.time() - T0, 1)
out["executions"] = "none - no preview, no mint, no claim (read-only)"
json.dump(out, open(f"{HF}/run-2026-11-19-0231-driverC.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("block", "errors", "n_calls", "elapsed_s", "boltbook_post")}, indent=1, default=str)[:3000])
