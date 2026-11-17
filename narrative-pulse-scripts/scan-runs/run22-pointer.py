#!/usr/bin/env python3
"""Read-only run 22 pointer discovery: Botkirin (queued) + 2 new NFTs + 2 new ERC20s.
For ERC20s tokenURI is n/a (no tokenId); contractURI + Sourcify sources/ABI still tried."""
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
def decode_jsonish(s):
    if s is None: return {}
    out = {}
    if s.startswith("data:application/json;base64,"):
        try: out["json"] = json.loads(base64.b64decode(s.split(",", 1)[1]).decode(errors="replace"))
        except Exception as e: out["b64_error"] = str(e)[:200]
    elif s.startswith("data:application/json;"):
        try: out["json"] = json.loads(s.split(",", 1)[1])
        except Exception as e: out["json_error"] = str(e)[:200]
    elif s.startswith("http") or s.startswith("ipfs://"):
        out["url"] = s
    else:
        out["raw"] = s[:500]
    return out
TARGETS = [
    ("0x01f9ca4ff95d49594cc8b6591022186dc5c1bc72", 123, "DGF CARD (run-22 new)"),
    ("0x0aa11f327313682cdf072affff26d0dffc804483", 260, "Krillfarm (run-22 new)"),
    ("0xf45fe22b3a9a748c59a7099e2e7b69f41216b1cd", 248, "Mummyhive (run-22 new)"),
    ("0xc1a54df271a455e236169f8ff65b084ebfb00e15", 233, "Pilotphoenix (run-22 new)"),
    ("0xe3f0085fd94d4fb2ae9acb4b49f6c0504e3546a0", 223, "Glitchdroid (run-22 new)"),
]
results = {}
for addr, tid, label in TARGETS:
    entry = {"label": label, "token_id_used": tid}
    try:
        r = fast_rpc.race("eth_call", [{"to": addr, "data": sel("contractURI()")}, "latest"])
        s = decode_str(r) if r else None
        entry["contractURI"] = {"raw": s, "decoded": decode_jsonish(s) if s else None}
    except Exception as e:
        entry["contractURI"] = {"error": str(e)[:300]}
    time.sleep(4)
    if tid is not None:
        try:
            r = fast_rpc.race("eth_call", [{"to": addr, "data": sel("tokenURI(uint256)") + format(tid, "064x")}, "latest"])
            s = decode_str(r) if r else None
            entry["tokenURI"] = {"raw": s, "decoded": decode_jsonish(s) if s else None}
        except Exception as e:
            entry["tokenURI"] = {"error": str(e)[:300]}
        time.sleep(4)
    else:
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
    results[addr] = entry
    print(addr, label, json.dumps(entry, indent=1)[:3000], flush=True)
json.dump(results, open("/home/hatch/workspace/narrative-pulse/scan-runs/run22-pointer.json", "w"), indent=1)
print("saved /home/hatch/workspace/narrative-pulse/scan-runs/run22-pointer.json", flush=True)
