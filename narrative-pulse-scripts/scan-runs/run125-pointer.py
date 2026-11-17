#!/usr/bin/env python3
"""Run 125 pointer-discovery (read-only, cap 5/run, amendment 19:10 WIB).
Backfill the next 5 oldest bridge entries with gate=None (all run-1 findings, seeded 2026-11-03 11:41 WIB).
For each: contractURI() -> decode -> external_link/external_url/website;
tokenURI(tokenId) -> decode (base64 JSON / IPFS / HTTP) -> external_url/website;
grep Sourcify sources + ABI for website/siteURL/domain/external + URL strings.
A candidate URL counts as website ONLY if the fetched page prints the exact
contract address (same standard as methods H/G). No preview/mint/sign/login.
"""
import json, sys, time, re, base64, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import fast_rpc
from Crypto.Hash import keccak

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def dec_str(h):
    try:
        if not isinstance(h, str) or not h.startswith("0x"):
            return None
        b = bytes.fromhex(h[2:])
        if len(b) < 96:
            return None
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception:
        return None

def call(a, d):
    return fast_rpc.race("eth_call", [{"to": a, "data": d}, "latest"])

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Muse-scan/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read().decode(errors="replace")

def sourcify(addr, fields):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields={fields}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Muse-scan/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode(errors="replace")
        return {"http_status": resp.status, "body_len": len(body),
                "urls_found": sorted(set(re.findall(r'https?://[A-Za-z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]+', body)))[:30],
                "site_fn_words": sorted(set(re.findall(r'\b(?:website|siteURL|siteUrl|domain|external(?:_url|Url|Link)?)\b', body)))}
    except Exception as e:
        return {"error": str(e)[:300]}

def decode_token_uri(uri):
    """Return (decoded_text_or_None, note)."""
    if not uri:
        return None, "empty"
    if uri.startswith("data:application/json;base64,"):
        try:
            return base64.b64decode(uri.split(",", 1)[1]).decode(errors="replace"), "base64 JSON"
        except Exception as e:
            return None, f"base64 decode failed: {e}"
    if uri.startswith("ipfs://"):
        gw = "https://ipfs.io/ipfs/" + uri[7:]
        try:
            _, body = fetch(gw)
            return body, "ipfs via ipfs.io"
        except Exception as e:
            return None, f"ipfs fetch failed: {str(e)[:120]}"
    if uri.startswith("http"):
        try:
            _, body = fetch(uri)
            return body, "http fetch"
        except Exception as e:
            return None, f"http fetch failed: {str(e)[:120]}"
    return None, f"unhandled scheme: {uri[:60]}"

def extract_urls(text):
    if not text:
        return []
    return sorted(set(re.findall(r'https?://[A-Za-z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]+', text)))

TARGETS = [
    ("0x6c90d2302bf0a9daaf453f3af2cd79f3c9b79cf8", "Emberforge", "ERC721", 77),
    ("0xe5ba385649a5655188f3a11916cb22da36d3517e", "Rackfarm", "ERC721", 345),
    ("0xf11c5f7ac5d42b912b8e611b55b825134c3679ba", "Musk Agent", "ERC721", 8),
    ("0x7561c414a7a6ff44fc81e9bfc2eda8f57c3ec61e", "Agent Panda", "ERC721", 867),
    ("0xde1f985f8a49d022811c49cf1d8506ca38abf86c", "AigentCard", "ERC721", 1744),
]

out = {}
for addr, name, kind, tid in TARGETS:
    e = {"name": name, "kind": kind, "token_id": tid}
    # contractURI()
    try:
        e["contractURI"] = {"raw": dec_str(call(addr, sel("contractURI()")))}
    except Exception as ex:
        e["contractURI"] = {"error": str(ex)[:300]}
    time.sleep(2)
    # tokenURI(tokenId)
    if kind == "ERC721":
        data = sel("tokenURI(uint256)") + f"{tid:064x}"
    else:
        data = sel("uri(uint256)") + f"{tid:064x}"
    try:
        raw_uri = dec_str(call(addr, data))
        e["tokenURI_raw"] = raw_uri
        dec, note = decode_token_uri(raw_uri)
        e["tokenURI_decoded_note"] = note
        e["tokenURI_decoded"] = (dec or "")[:2000] if dec else None
        e["tokenURI_urls"] = extract_urls(dec)[:20] if dec else []
    except Exception as ex:
        e["tokenURI"] = {"error": str(ex)[:300]}
    time.sleep(2)
    # Sourcify
    for f in ("sources", "abi"):
        e[f"sourcify_{f}"] = sourcify(addr, f)
        time.sleep(2)
    # candidate URLs from contractURI + tokenURI
    cands = set()
    for u in extract_urls(e.get("contractURI", {}).get("raw") or ""):
        cands.add(u)
    for u in e.get("tokenURI_urls", []):
        cands.add(u)
    for u in e.get("sourcify_sources", {}).get("urls_found", []):
        # only project-ish hosts, skip docs/github generic
        if any(h in u for h in ("github.com", "docs.", "openzeppelin", "eips.ethereum", "ethereum.org")):
            continue
        cands.add(u)
    e["candidate_urls"] = sorted(cands)
    # verify each candidate: page must print exact contract address
    verified = None
    for u in sorted(cands):
        try:
            st, body = fetch(u)
            if addr.lower() in body.lower() or addr[2:].lower() in body.lower():
                verified = {"url": u, "http_status": st}
                break
            e.setdefault("candidate_fetch", []).append({"url": u, "http_status": st, "prints_contract": False})
        except Exception as ex:
            e.setdefault("candidate_fetch", []).append({"url": u, "error": str(ex)[:200]})
    e["website_verified"] = verified
    out[addr] = e
    print(f"{name} {addr[:10]} verified={verified} cands={sorted(cands)[:5]}", flush=True)

json.dump(out, open("/home/hatch/workspace/narrative-pulse/scan-runs/run125-pointer.json", "w"), indent=1)
print("saved run125-pointer.json")
