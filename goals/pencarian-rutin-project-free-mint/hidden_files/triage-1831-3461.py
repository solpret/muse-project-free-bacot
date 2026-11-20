#!/usr/bin/env python3
"""Triage Boltbook-new 0x3461a1595a0d80d8bc643c6ad08adc67248744ee (run 1831). Read-only."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
from eth_hash.auto import keccak
from quicknode import ProxyHTTPSConnection
from dynamic_credentials import dynamic_credential_entry
QN_HOST = "stylish-thrilling-star.bsc.quiknode.pro"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
ADDR = "0x3461a1595a0d80d8bc643c6ad08adc67248744ee"
def https_get(host, path, timeout=25):
    conn = ProxyHTTPSConnection(host, 443, timeout=timeout)
    try:
        conn.request("GET", path, headers={"User-Agent": UA, "Accept": "*/*"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
    finally:
        conn.close()
    return status, raw
def qn(payload, timeout=25):
    entry = dynamic_credential_entry("custom.quicknode")
    surrogate = str(entry["surrogate"]).strip()
    conn = ProxyHTTPSConnection(QN_HOST, 443, timeout=timeout)
    try:
        conn.request("POST", f"/{surrogate}/", body=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
    finally:
        conn.close()
    if status != 200: raise IOError(f"quicknode http {status}: {raw[:150]!r}")
    return json.loads(raw.decode())
out = {"address": ADDR}
# 1. Sourcify ABI
try:
    st, raw = https_get("sourcify.dev", f"/server/v2/contract/56/{ADDR}?fields=abi", timeout=25)
    meta = json.loads(raw.decode())
    abi = meta.get("abi", [])
    fns = {}
    for e in abi:
        if e.get("type") == "function": fns.setdefault(e["name"], []).append(e)
    names = set(fns)
    out["sourcify_http"] = st
    out["verifiedAt"] = meta.get("verifiedAt")
    out["n_fns"] = len(names)
    out["fn_names"] = sorted(names)
    FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
                  "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
    free_views = sorted(names & FREE_VIEWS)
    agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
    is_token = bool(names & {"name","symbol","decimals","totalSupply"})
    mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
    out.update({"has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref_abi": agent_ref, "is_token": is_token,
                "S1": has_mint and has_quote and bool(free_views) and agent_ref,
                "S2": is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref})
except Exception as e:
    out["sourcify_error"] = f"{type(e).__name__}: {str(e)[:200]}"
# 2. eth_getCode + registry bytes
try:
    r = qn([{"jsonrpc": "2.0", "id": 1, "method": "eth_getCode", "params": [ADDR, "latest"]}])
    code = r[0].get("result", "")
    out["code_len"] = len(code)
    out["registry_bytes"] = "60b9262456de011f7d15a54cdd8c48baa8b022f" in str(code).lower()
    out["agent_ref"] = out.get("agent_ref_abi") or out["registry_bytes"]
    out["S1"] = out.get("S1") or (out.get("has_mint") and out.get("has_quote") and bool(out.get("free_views")) and out["agent_ref"])
    out["S2"] = out.get("S2") or (out.get("is_token") and False and out["agent_ref"])
except Exception as e:
    out["code_error"] = f"{type(e).__name__}: {str(e)[:200]}"
# 3. on-chain probes if agent-shaped or token-like
def sel(sig): return keccak(sig.encode())[:4].hex()
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def enc(sig, arg=None):
    d = "0x" + sel(sig)
    if arg == "user": d += "0"*24 + USER[2:].lower()
    elif arg == "user1": d += "0"*24 + USER[2:].lower() + "%064x" % 1
    elif arg == "one": d += "%064x" % 1
    return d
views = ["totalSupply()", "totalMinted()", "freeMinted()", "freeClaimed()", "freeLeft()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "name()", "symbol()"]
calls = [{"jsonrpc": "2.0", "id": i+1, "method": "eth_call", "params": [{"to": ADDR, "data": enc(s)}, "latest"]} for i, s in enumerate(views)]
try:
    r = qn(calls)
    by = {it["id"]: it for it in r if isinstance(it, dict)}
    res = {}
    for i, s in enumerate(views):
        it = by.get(i+1, {})
        if "result" in it and it["result"] not in (None, "0x"):
            try: res[s] = int(it["result"], 16)
            except Exception: res[s] = it["result"]
        elif "error" in it: res[s] = f"err:{str(it['error'])[:80]}"
        else: res[s] = None
    out["views"] = res
except Exception as e:
    out["views_error"] = f"{type(e).__name__}: {str(e)[:200]}"
print(json.dumps(out, indent=1, default=str))
json.dump(out, open("triage-1831-3461.json", "w"), indent=1)
