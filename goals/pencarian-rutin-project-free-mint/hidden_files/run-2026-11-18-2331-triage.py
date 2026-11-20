#!/usr/bin/env python3
"""Run 2331 triage: Boltbook-new 0x42c9 + 0x9b0c, df6b eth_getCode,
ARKT-8334 agent-shape, Agent Vein token->core()->sale shape.
Read-only. Uses Quicknode tunnel like the main driver."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from eth_hash.auto import keccak
from quicknode import ProxyHTTPSConnection
from dynamic_credentials import dynamic_credential_entry
QN_HOST = "stylish-thrilling-star.bsc.quiknode.pro"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "60b9262456de011f7d15a54cdd8c48baa8b022f"

def https_get(host, path, timeout=20):
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
        conn.request("POST", f"/{surrogate}/", body=json.dumps(payload).encode(),
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
    finally:
        conn.close()
    if status != 200:
        raise IOError(f"quicknode http {status}: {raw[:150]!r}")
    return json.loads(raw.decode())

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def call(to, sig, arg=None):
    data = "0x" + sel(sig)
    if arg == "user":
        data += enc_addr(USER)
    elif arg == "one":
        data += "%064x" % 1
    elif arg == "user1":
        data += enc_addr(USER) + "%064x" % 1
    r = qn([{"jsonrpc": "2.0", "id": 1, "method": "eth_call",
             "params": [{"to": to, "data": data}, "latest"]}])
    it = r[0] if isinstance(r, list) else r
    if "result" in it and it["result"] not in (None, "0x"):
        return it["result"]
    if "error" in it:
        return f"err:{it['error'].get('message', it['error']) if isinstance(it['error'], dict) else it['error']}"
    return None

def call_int(to, sig, arg=None):
    v = call(to, sig, arg)
    if isinstance(v, str) and v.startswith("0x"):
        try:
            return int(v, 16)
        except Exception:
            return v
    return v

def get_code(to):
    r = qn([{"jsonrpc": "2.0", "id": 1, "method": "eth_getCode", "params": [to, "latest"]}])
    it = r[0] if isinstance(r, list) else r
    return it.get("result", "")

def decode_str(hexv):
    if not isinstance(hexv, str) or not hexv.startswith("0x") or len(hexv) < 138:
        return None
    try:
        b = bytes.fromhex(hexv[2:])
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96 + ln].decode("utf-8", errors="replace")
    except Exception:
        return None

def sourcify_abi(addr):
    try:
        st, raw = https_get("sourcify.dev", f"/server/v2/contract/56/{addr}?fields=abi", timeout=20)
        meta = json.loads(raw.decode())
        abi = meta.get("abi", [])
        fns = sorted({e["name"] for e in abi if e.get("type") == "function"})
        return {"verified": True, "n_fns": len(fns), "fns": fns, "verifiedAt": meta.get("verifiedAt")}
    except Exception as e:
        return {"verified": False, "error": f"{type(e).__name__}: {str(e)[:120]}"}

out = {}
# --- df6b: code? ---
code = get_code("0xdf6bede5287207e3def3dcbe142e202e2c0d5645")
out["df6b"] = {"code_len": len(code) - 2 if code.startswith("0x") else len(code),
               "has_code": bool(code and code != "0x"),
               "registry_bytes": REG in code.lower() if code else False}
# --- ARKT-8334 agent-shape ---
a8334 = "0x8334C7d0e8aF217EEA5251A0A181e628971535e1"
c8334 = get_code(a8334)
abi8334 = sourcify_abi(a8334)
out["arkt8334"] = {"code_len": len(c8334) - 2, "registry_bytes": REG in c8334.lower(),
                   "sourcify": abi8334,
                   "totalSupply": call_int(a8334, "totalSupply()"),
                   "totalMinted": call_int(a8334, "totalMinted()"),
                   "freeMinted": call_int(a8334, "freeMinted()"),
                   "name": decode_str(call(a8334, "name()")),
                   "symbol": decode_str(call(a8334, "symbol()"))}
# --- Boltbook-new 0x42c9 + 0x9b0c ---
for label, addr in (("bolt-42c9", "0x42c9ed912025df33ca1676aad4651cdded3f09ed"),
                    ("bolt-9b0c", "0x9b0c237a123277fcf8768550bbdd7767c73cf5d3")):
    c = get_code(addr)
    abi = sourcify_abi(addr)
    out[label] = {"address": addr, "code_len": len(c) - 2 if c.startswith("0x") else 0,
                  "has_code": bool(c and c != "0x"), "registry_bytes": REG in c.lower() if c else False,
                  "sourcify": abi,
                  "name": decode_str(call(addr, "name()")),
                  "symbol": decode_str(call(addr, "symbol()")),
                  "totalSupply": call_int(addr, "totalSupply()"),
                  "totalMinted": call_int(addr, "totalMinted()"),
                  "freeMinted": call_int(addr, "freeMinted()"),
                  "freeClaimed": call_int(addr, "freeClaimed()"),
                  "FREE_SUPPLY": call_int(addr, "FREE_SUPPLY()"),
                  "MAX_SUPPLY": call_int(addr, "MAX_SUPPLY()"),
                  "mintOpen": call_int(addr, "mintOpen()"),
                  "balanceOf_user": call_int(addr, "balanceOf(address)", "user")}
# --- Agent Vein: token -> core() -> sale ---
VEIN = "0x17ccdcd9763e824a59c78f60c10e6976d5663479"
vein = {"token": VEIN,
        "name": decode_str(call(VEIN, "name()")),
        "symbol": decode_str(call(VEIN, "symbol()")),
        "decimals": call_int(VEIN, "decimals()"),
        "totalSupply": call_int(VEIN, "totalSupply()"),
        "core_raw": call(VEIN, "core()")}
core = vein["core_raw"]
sale = None
if isinstance(core, str) and core.startswith("0x") and len(core) == 66:
    sale = "0x" + core[-40:]
    vein["sale"] = sale
    sc = get_code(sale)
    abi = sourcify_abi(sale)
    fns = set(abi.get("fns", []))
    FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
                  "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted",
                  "freeCardsRemaining"}
    vein["sale_shape"] = {
        "code_len": len(sc) - 2, "registry_bytes": REG in sc.lower() if sc else False,
        "sourcify": abi,
        "has_mint": any(n.lower().startswith("mint") for n in fns),
        "has_quote": bool(fns & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"}),
        "free_views": sorted(fns & FREE_VIEWS),
        "agent_ref": bool(fns & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate"}),
        "is_token": bool(fns & {"name", "symbol", "decimals", "totalSupply"}),
        "freeSharesRemaining": call_int(sale, "freeSharesRemaining()"),
        "FREE_SHARES_TOTAL": call_int(sale, "FREE_SHARES_TOTAL()"),
        "freeShareClaimedBy_user": call_int(sale, "freeShareClaimedBy(address)", "user"),
        "quote_user_1": call_int(sale, "quote(address,uint256)", "user1"),
    }
    s1 = (vein["sale_shape"]["has_mint"] and vein["sale_shape"]["has_quote"]
          and bool(vein["sale_shape"]["free_views"])
          and (vein["sale_shape"]["agent_ref"] or vein["sale_shape"]["registry_bytes"]))
    vein["sale_shape"]["S1"] = s1
out["agent_vein"] = vein
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-18-2331-triage.json", "w"), indent=1)
print(json.dumps(out, indent=1))
