#!/usr/bin/env python3
"""Hot-leg 2026-11-12 1814 follow-up: re-read leg-4 items whose raced batch
returned null in the main run (RPC degraded). Race first, then sequential
endpoint fallback with longer timeout. Read-only; writes only own file."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-12-1814"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed1.defibit.io/"]
def _post_one(ep, payload, timeout=15):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)
def post_rpc(payload):
    # race first two, then sequential fallback over all endpoints
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = {ex.submit(_post_one, ep, payload, 15): ep for ep in EPS[:2]}
        for fut in as_completed(futs):
            try:
                res = fut.result()
                if isinstance(res, list) and len(res) == len(payload):
                    return res, "race"
            except Exception:
                continue
    for ep in EPS:
        try:
            res = _post_one(ep, payload, 20)
            if isinstance(res, list) and len(res) == len(payload):
                return res, f"fallback:{ep}"
        except Exception:
            continue
    return None, None

VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
         "FREE_CAP()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)", "freeClaimed(address)",
         "freeUsed(address)", "mintedBy(address)", "saleStart()", "PRICE()", "price()",
         "freeRemaining()", "freeLeft()", "isFreeOpen()", "FREE_MODE()", "freeAvailable(address)",
         "launched()", "freeSharesRemaining()", "freeMintedBy(address)", "mintStart()",
         "freeSharesLeft()", "openedAt()", "currentState()", "finalized()", "refunding()",
         "totalFreeMinted()", "FREE_SHARES()", "freeLeftFor(address)"]
TARGETS = [
    ("RunicKey", "0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4"),
    ("Stampooor", "0x467696af8c2206B977B24081445104632dc1D459"),
    ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d"),
    ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"),
    ("LuckyCatch", "0xD405C90079c594DA2456F5b37B4158A12f1382e5"),
    ("AGCR", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc"),
    ("SUDOSAINTS", "0x869d330bb48e7ab32da16745ef9a36a69d34f12f"),
    ("Ronin", "0xF62FA2ee1490708D51DeF7212493D5c7878Fa110"),
    ("THONK", "0x22e69F9a7BeC3D991C0ceB5a103E509319E42B2A"),
]
out = {"run": "hot-leg 2026-11-12 1814 leg4-retry", "reads": {}}
for name, addr in TARGETS:
    if time.time() - T0 > 150:
        out["reads"][name] = {"address": addr, "error": "deadline-skipped"}; continue
    calls, keys = [], []
    for i, sig in enumerate(VIEWS):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    res, via = post_rpc(calls)
    if res is None:
        out["reads"][name] = {"address": addr, "views": None}
    else:
        views = {}
        for it, key in zip(res, keys):
            views[key] = None if (isinstance(it, dict) and "error" in it) else (
                to_int(it.get("result")) if isinstance(it, dict) else None)
        e = {"address": addr, "via": via, "views": views,
             "summary": {k: v for k, v in views.items() if v is not None}}
        fm = views.get("freeMinted"); fs = views.get("FREE_SUPPLY")
        if fm is not None and fs:
            e["free_pct"] = round(100.0 * fm / fs, 2)
        out["reads"][name] = e
    time.sleep(0.2)
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-{TAG}-leg4retry.json", "w"), indent=1)
print(json.dumps(out, indent=1))
