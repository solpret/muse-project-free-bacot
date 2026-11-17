#!/usr/bin/env python3
"""Read-only run 32 pointer discovery: Notbnb NOTBNB ERC20 (new). tokenURI n/a."""
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
addr = "0xc7c171e479f6ad8a728e77b7484bb7d0b4984d0f"
entry = {"label": "Notbnb NOTBNB ERC20 (run-32 new)", "token_id_used": None}
try:
    r = fast_rpc.race("eth_call", [{"to": addr, "data": sel("contractURI()")}, "latest"])
    s = decode_str(r) if r else None
    entry["contractURI"] = {"raw": s}
except Exception as e:
    entry["contractURI"] = {"error": str(e)[:300]}
time.sleep(4)
entry["tokenURI"] = {"n/a": "ERC20, no tokenId"}
for fields in ("sources", "abi"):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields={fields}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Muse-scan/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode(errors="replace")
        urls = sorted(set(re.findall(r'https?://[A-Za-z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]+', body)))
        fns = sorted(set(re.findall(r'\b(?:website|siteURL|siteUrl|domain|external(?:_url|Url|Link)?)\b', body)))
        entry[f"sourcify_{fields}"] = {"http_status": resp.status, "body_len": len(body), "urls_found": urls[:30], "site_fn_words": fns}
    except Exception as e:
        entry[f"sourcify_{fields}"] = {"error": str(e)[:300]}
    time.sleep(2)
print(json.dumps(entry, indent=1), flush=True)
json.dump({addr: entry}, open("/home/hatch/workspace/narrative-pulse/scan-runs/run32-pointer.json", "w"), indent=1)
print("saved run32-pointer.json", flush=True)
