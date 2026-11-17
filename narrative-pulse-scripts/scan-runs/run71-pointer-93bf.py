#!/usr/bin/env python3
"""Run 71 pointer discovery for the 0x2325 mint-pattern contract 0x93bf08d2 (read-only)."""
import json, sys, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import fast_rpc
from Crypto.Hash import keccak

def call(addr, data):
    try:
        return fast_rpc.race("eth_call", [{"to": addr, "data": data}, "latest"])
    except Exception as e:
        return f"ERROR:{e}"

def sel4(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

C = "0x93bf08d2936aefe0cd2ceba8f76cb566fdf9e1c9"
out = {"contract": C, "contractURI": None, "sourcify": None}
r = call(C, sel4("contractURI()"))
print("contractURI raw:", str(r)[:300])
if isinstance(r, str) and not r.startswith("ERROR") and len(r) >= 130:
    try:
        ln = int(r[130:194], 16)
        out["contractURI"] = bytes.fromhex(r[194:194 + ln * 2]).decode("utf-8", "replace")
    except Exception as e:
        out["contractURI"] = f"decode-error {e}"
else:
    out["contractURI"] = f"unreadable({str(r)[:80]})"
print("contractURI decoded:", out["contractURI"])
try:
    req = urllib.request.Request(
        f"https://sourcify.dev/server/v2/contract/56/{C}?fields=sources",
        headers={"User-Agent": "Muse-scan/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8", "replace")
    out["sourcify"] = {"status": resp.status, "len": len(body),
                       "has_url": ("http" in body.lower()),
                       "snippet": body[:400]}
except Exception as e:
    out["sourcify"] = {"error": str(e)[:200]}
print(json.dumps(out, indent=1)[:2000])
json.dump(out, open("run71-pointer-93bf.json", "w"), indent=1)

# extra: symbol() retry + Sourcify ABI grep for site functions / URLs
def read_str(addr, sig):
    r = call(addr, sel4(sig))
    if not isinstance(r, str) or r.startswith("ERROR") or len(r) < 130:
        return f"unreadable({str(r)[:80]})"
    try:
        ln = int(r[130:194], 16)
        return bytes.fromhex(r[194:194 + ln * 2]).decode("utf-8", "replace")
    except Exception as e:
        return f"decode-error {e}"
print("symbol retry:", repr(read_str(C, "symbol()")))
print("name retry:", repr(read_str(C, "name()")))
try:
    req = urllib.request.Request(
        f"https://sourcify.dev/server/v2/contract/56/{C}?fields=abi",
        headers={"User-Agent": "Muse-scan/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8", "replace")
    import re as _re
    urls = sorted(set(_re.findall(r'https?://[A-Za-z0-9\-._~:/?#@!$&\'()*+,;=%]+', body)))
    print("sourcify abi status:", resp.status, "len:", len(body))
    print("abi urls:", urls[:20])
    print("abi site-fn:", [f for f in ["website", "siteURL", "domain", "external"] if f.lower() in body.lower()])
    out["sourcify_abi"] = {"status": resp.status, "len": len(body), "urls": urls[:20]}
except Exception as e:
    print("sourcify abi error:", str(e)[:200])
    out["sourcify_abi"] = {"error": str(e)[:200]}
json.dump(out, open("run71-pointer-93bf.json", "w"), indent=1)
