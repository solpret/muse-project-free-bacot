#!/usr/bin/env python3
"""Read-only run 12 pointer discovery (amendment 2026-11-03 19:10 WIB): for max 5
new contracts, read contractURI() + tokenURI(one minted tokenId) + Sourcify
sources/ABI grep for website/siteURL/domain/external functions and URL strings.
No web-name search, no guessing. No preview/mint/sign/login."""
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
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
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
    ("0x1db6fa45ec462c23cdc4b67d6301c3d5bcc3107a", 242, "Phoenixgent"),
    ("0xda552a0b709d09a2532689c6e39d981f527817b6", 235, "Glitchpilotfox"),
    ("0xd06518ea638cab567328ccd7b67e43a119c275e0", 431, "Monke Agents"),
    ("0xde94d86fdd2eeb66aaef837e43134a5d505dc39d", 182, "Cogentbyte"),
    ("0x6124b3ae64ada7b73581ccd01fef89e583e8742c", 214, "Saturnode"),
]
results = {}
for addr, tid, label in TARGETS:
    entry = {"label": label, "token_id_used": tid}
    for fn, data in (("contractURI", sel("contractURI()")),
                     ("tokenURI", sel("tokenURI(uint256)") + format(tid, "064x"))):
        try:
            r = fast_rpc.race("eth_call", [{"to": addr, "data": data}, "latest"])
            s = decode_str(r) if r else None
            entry[fn] = {"raw": s, "decoded": decode_jsonish(s) if s else None}
        except Exception as e:
            entry[fn] = {"error": str(e)[:300]}
        time.sleep(4)
    # Sourcify sources + abi
    for fields in ("sources", "abi"):
        url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields={fields}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Muse-scan/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode(errors="replace")
            urls = sorted(set(re.findall(r'https?://[A-Za-z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]+', body)))
            fns = sorted(set(re.findall(r'\b(?:website|siteURL|siteUrl|domain|external(?:_url|Url|Link)?)\b', body)))
            entry[f"sourcify_{fields}"] = {"http_status": resp.status, "body_len": len(body),
                                           "urls_found": urls[:30], "site_fn_words": fns}
        except Exception as e:
            entry[f"sourcify_{fields}"] = {"error": str(e)[:300]}
        time.sleep(2)
    results[addr] = entry
    print(addr, label, json.dumps(entry, indent=1)[:2000], flush=True)
json.dump(results, open("/tmp/tracked-scan-run12-pointer.json", "w"), indent=1)
print("saved /tmp/tracked-scan-run12-pointer.json", flush=True)
