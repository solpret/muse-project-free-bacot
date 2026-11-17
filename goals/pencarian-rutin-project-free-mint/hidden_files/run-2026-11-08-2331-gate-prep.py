#!/usr/bin/env python3
"""Run 2331 gate-prep for FrankensteinFriends + VampireVibes (methods C/E/H/I/J + earlier-window first-mint bound).
Read-only: Sourcify metadata fetch, fast_rpc eth_calls, dataseed eth_getLogs (single-address, chunked 1000).
Writes run-2026-11-08-2331-gate-prep.json. No preview/mint."""
import json, sys, time, urllib.request, re
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
TARGETS = {
    "FrankensteinFriends": "0xedfd9e6517ad4491ac6c7c98508566e2490ce708",
    "VampireVibes": "0xa5fb4e0e83837e9c7035b47c2f02d7db075563de",
}
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def raw_call(addr, sig, arg=None, raw_arg=None, timeout=30):
    data = sel(sig) + (raw_arg if raw_arg is not None else (enc(arg) if arg else ""))
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]},
                           timeout=timeout, retries=0)
            if isinstance(out, dict) and "error" in out: return None, out["error"]
            return (out.get("result") if isinstance(out, dict) else None), None
        except Exception:
            continue
    return None, "all-endpoints-failed"

def decode_string(r):
    if not r or r == "0x": return None
    try:
        b = bytes.fromhex(r[2:])
        if len(b) < 64: return None
        ln = int.from_bytes(b[32:64], "big")
        if ln > 100000: return None
        return b[64:64+ln].decode("utf-8", "replace")
    except Exception:
        return None

def dataseed_logs(addr, frm, to):
    """eth_getLogs on dataseed, single address, Transfer topic0 + zero from. Returns (count, first_block, err)."""
    params = {"fromBlock": hex(frm), "toBlock": hex(to), "address": addr,
              "topics": [TRANSFER, ZERO]}
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                                "params": [params]}, timeout=60, retries=0)
            if isinstance(out, dict) and "error" in out:
                return None, None, str(out["error"])[:200]
            logs = out if isinstance(out, list) else []
            first = min((int(l["blockNumber"], 16) for l in logs), default=None)
            return len(logs), first, None
        except Exception as e:
            continue
    return None, None, "all-endpoints-failed"

out = {"run": "2331", "targets": {}}
for name, addr in TARGETS.items():
    print(f"== {name} {addr}", flush=True)
    rec = {"address": addr}
    # (E) owner()
    v, err = raw_call(addr, "owner()")
    rec["owner"] = ("0x" + v[-40:]) if v and len(v) >= 42 else None
    print(f"  owner={rec['owner']} err={err}", flush=True)
    # (H) contractURI()
    v, err = raw_call(addr, "contractURI()")
    rec["contractURI"] = decode_string(v)
    print(f"  contractURI={rec['contractURI']} err={str(err)[:120] if err else None}", flush=True)
    # (I) tokenURI(1) + tokenURI(0)
    for tid in (1, 0):
        v, err = raw_call(addr, "tokenURI(uint256)", raw_arg="0"*63 + str(tid))
        s = decode_string(v)
        rec[f"tokenURI_{tid}"] = s
        print(f"  tokenURI({tid})={str(s)[:200]}", flush=True)
    # (C) Sourcify metadata: fetch sources, grep http URLs
    urls = set()
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}",
                                     headers={"User-Agent": "free-bacot-run2331"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
        blob = json.dumps(data)
        for u in re.findall(r'https?://[^\s"\'\\<>]+', blob):
            if "sourcify.dev" not in u and "github.com" not in u or "github.com" in u:
                urls.add(u)
        rec["sourcify_match"] = data.get("match")
        rec["sourcify_urls"] = sorted(urls)[:20]
    except Exception as e:
        rec["sourcify_urls"] = []
        rec["sourcify_error"] = str(e)[:200]
    print(f"  sourcify_urls={rec['sourcify_urls']}", flush=True)
    # (J) ABI site-function grep (reuse Sourcify ABI)
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
                                     headers={"User-Agent": "free-bacot-run2331"})
        with urllib.request.urlopen(req, timeout=30) as r:
            abi = json.load(r).get("abi", [])
        names = [e.get("name", "") for e in abi if isinstance(e, dict)]
        site_fns = [n for n in names if any(w in n.lower() for w in ("website", "siteurl", "domain", "external", "url", "uri"))]
        rec["abi_site_fns"] = site_fns
        rec["abi_has_agent"] = any("agent" in n.lower() for n in names)
    except Exception as e:
        rec["abi_site_fns"] = []
        rec["abi_error"] = str(e)[:200]
    print(f"  abi_site_fns={rec['abi_site_fns']} abi_has_agent={rec.get('abi_has_agent')}", flush=True)
    # earlier-window first-mint bound: [132411334, 132420333] via dataseed (9 x 1000-block chunks)
    earliest = None; total = 0; errs = []
    chunk = 132411334
    while chunk <= 132420333:
        cto = min(chunk + 999, 132420333)
        n, first, err = dataseed_logs(addr, chunk, cto)
        if err:
            errs.append(f"{chunk}-{cto}: {err}")
        else:
            total += n or 0
            if first is not None and (earliest is None or first < earliest):
                earliest = first
        print(f"  dataseed chunk {chunk}-{cto}: n={n} first={first} err={err}", flush=True)
        chunk = cto + 1
        time.sleep(0.5)
    rec["earlier_window"] = {"range": "132411334-132420333", "mint_logs": total,
                             "earliest_block": earliest, "errors": errs}
    print(f"  earlier window: {total} mint logs, earliest={earliest}, errs={errs}", flush=True)
    out["targets"][name] = rec

json.dump(out, open(BASE + "/run-2026-11-08-2331-gate-prep.json", "w"), indent=1)
print("saved", BASE + "/run-2026-11-08-2331-gate-prep.json", flush=True)
