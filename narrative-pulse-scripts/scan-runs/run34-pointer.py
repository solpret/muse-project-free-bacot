#!/usr/bin/env python3
"""Read-only run 34 pointer discovery: ACAT NFT (new, token #2546) + 币安加油 token ERC20 (new).
contractURI/tokenURI/Sourcify/ABI grep only. No preview/mint/sign/login."""
import json, sys, time, re, base64, urllib.request
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import fast_rpc
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def decode_str(hexdata):
    try:
        b = bytes.fromhex(hexdata[2:])
        if len(b) < 96: return None
        off = int.from_bytes(b[0:32], "big"); ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception:
        return None
def call(addr, data):
    return fast_rpc.race("eth_call", [{"to": addr, "data": data}, "latest"])
def sourcify(addr, fields):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields={fields}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Muse-scan/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode(errors="replace")
        urls = sorted(set(re.findall(r'https?://[A-Za-z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]+', body)))
        fns = sorted(set(re.findall(r'\b(?:website|siteURL|siteUrl|domain|external(?:_url|Url|Link)?)\b', body)))
        return {"http_status": resp.status, "body_len": len(body), "urls_found": urls[:30], "site_fn_words": fns}
    except Exception as e:
        return {"error": str(e)[:300]}

out = {}
# --- ACAT ---
addr = "0x28a38a372639e8c481ad41b9b16e52c3c6366acc"
e = {"label": "ACAT ERC721 #2546 (run-34 new, already in Free Bacot snapshot as ACAT-28a3 EARLY)"}
for fn in ["contractURI()", "owner()"]:
    try:
        r = call(addr, sel(fn)); e[fn] = {"raw": decode_str(r) if r else None}
    except Exception as ex: e[fn] = {"error": str(ex)[:300]}
    time.sleep(4)
try:
    data = "0x" + sel("tokenURI(uint256)") + "2546".rjust(64, "0") if False else None
    # tokenURI(uint256): selector + uint256 arg
    arg = format(2546, "064x")
    r = call(addr, sel("tokenURI(uint256)") + arg)
    s = decode_str(r) if r else None
    e["tokenURI_2546"] = {"raw": (s[:500] if s else None)}
    if s and s.startswith("data:application/json;base64,"):
        try:
            j = json.loads(base64.b64decode(s.split(",", 1)[1]).decode())
            e["tokenURI_2546"]["json_keys"] = list(j.keys())
            e["tokenURI_2546"]["external_url"] = j.get("external_url")
            e["tokenURI_2546"]["website"] = j.get("website")
        except Exception as ex: e["tokenURI_2546"]["decode_error"] = str(ex)[:200]
    elif s and s.startswith("http"):
        e["tokenURI_2546"]["http_url"] = s[:300]
except Exception as ex: e["tokenURI_2546"] = {"error": str(ex)[:300]}
time.sleep(2)
for f in ("sources", "abi"): e[f"sourcify_{f}"] = sourcify(addr, f); time.sleep(2)
out[addr] = e
print(json.dumps({addr: e}, indent=1), flush=True)
# --- 币安加油 token ---
addr2 = "0x397bf425926f521ac5bebe5062793bb224e3ef8f"
e2 = {"label": "币安加油 token ERC20 (run-34 new; sale 0xc9b4...; user minted same project 2026-11-04 ~17:00 WIB)"}
for fn in ["contractURI()", "owner()"]:
    try:
        r = call(addr2, sel(fn)); e2[fn] = {"raw": decode_str(r) if r else None}
    except Exception as ex: e2[fn] = {"error": str(ex)[:300]}
    time.sleep(4)
e2["tokenURI"] = {"n/a": "ERC20, no tokenId"}
for f in ("sources", "abi"): e2[f"sourcify_{f}"] = sourcify(addr2, f); time.sleep(2)
out[addr2] = e2
print(json.dumps({addr2: e2}, indent=1), flush=True)
json.dump(out, open("/home/hatch/workspace/narrative-pulse/scan-runs/run34-pointer.json", "w"), indent=1)
print("saved run34-pointer.json", flush=True)
