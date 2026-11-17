#!/usr/bin/env python3
"""Farmbuxiang gate-completion checks (run 1301): slot (freeLeft/freeFor),
(H) contractURI, (I) tokenURI external_url, (J) Sourcify ABI site-function grep.
Read-only, dataseed curl + Sourcify curl. Ankr NOT used."""
import json, subprocess, base64, re
from Crypto.Hash import keccak
ADDR = "0x6810056D235c949f425b394dE590835096dd6AdC"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return hex(n)[2:].rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v not in (None, "0x") else None
    except Exception: return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def raw_call(addr, data, timeout=25):
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": addr, "data": data}, "latest"]}, timeout=timeout)
            if isinstance(r, dict) and "result" in r: return r["result"]
        except Exception: continue
    return None
def decode_str(hexv):
    # abi-encoded string: offset(32) len(32) data
    try:
        b = bytes.fromhex(hexv[2:])
        if len(b) < 64: return None
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode("utf-8", "replace")
    except Exception: return None
out = {}
out["freeLeft_user"] = to_int(raw_call(ADDR, sel("freeLeft(address)") + enc(USER)))
out["freeFor_user"] = to_int(raw_call(ADDR, sel("freeFor(address)") + enc(USER)))
out["freeUsed_user"] = to_int(raw_call(ADDR, sel("freeUsed(address)") + enc(USER)))
out["freeClaimed_addr"] = to_int(raw_call(ADDR, sel("freeClaimed(address)") + enc(USER)))
out["contractURI"] = decode_str(raw_call(ADDR, sel("contractURI()")) or "")
out["tokenURI_1"] = decode_str(raw_call(ADDR, sel("tokenURI(uint256)") + enc_uint(1)) or "")
out["tokenURI_600"] = decode_str(raw_call(ADDR, sel("tokenURI(uint256)") + enc_uint(600)) or "")
# (J) Sourcify ABI
try:
    abi_raw = subprocess.run(["curl", "-sL", "--max-time", "20",
        f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi"],
        capture_output=True, text=True, timeout=25).stdout
    d = json.loads(abi_raw)
    abi = d.get("abi") or []
    fns = [e.get("name") for e in abi if isinstance(e, dict) and e.get("type") == "function"]
    out["sourcify_match"] = d.get("match") or d.get("stdJson", {}).get("match")
    out["abi_functions"] = fns
    site_fns = [f for f in fns if any(w in f.lower() for w in ("website", "siteurl", "site", "domain", "external", "twitter", "social"))]
    out["site_functions"] = site_fns
    out["site_fn_values"] = {}
    for f in site_fns:
        out["site_fn_values"][f] = decode_str(raw_call(ADDR, sel(f + "()")) or "")
except Exception as e:
    out["sourcify_error"] = str(e)[:300]
print(json.dumps(out, indent=1)[:4000])
json.dump(out, open("run-2026-11-09-1301-farmbuxiang.json", "w"), indent=1)
