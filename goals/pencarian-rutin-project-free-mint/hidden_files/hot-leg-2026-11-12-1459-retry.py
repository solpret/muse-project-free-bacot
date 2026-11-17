#!/usr/bin/env python3
"""Bounded retry (1459 followup): leg3 for new S1 pass 0x5A0e, LuckyCatch leg4,
shape-check deferred 0x5CA1. Read-only; writes ONLY hot-leg-2026-11-12-1459-followup.json."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-12 14:59 WIB followup-retry", "started_wib": now_wib}
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def _post_one(ep, payload, timeout=12):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)
def post_rpc_race(payload, timeout=12):
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = {ex.submit(_post_one, ep, payload, timeout): ep for ep in EPS}
        for fut in as_completed(futs):
            try:
                res = fut.result()
                if isinstance(res, list) and len(res) == len(payload):
                    return res
            except Exception:
                continue
    return None
def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    res = post_rpc_race(calls, timeout=12)
    if res is None: return None
    return {key: (None if (isinstance(it, dict) and "error" in it)
                  else (to_int(it.get("result")) if isinstance(it, dict) else None))
            for it, key in zip(res, keys)}
LEG3_VIEWS = ["name()", "symbol()", "totalSupply()", "totalMinted()", "freeClaimed()",
              "freeMinted()", "FREE_SUPPLY()", "FREE_CAP()", "FREE_SHARES()", "MAX_SUPPLY()",
              "mintOpen()", "balanceOf(address)", "freeClaimed(address)", "freeUsed(address)",
              "mintedBy(address)", "mintStart()", "freeLeft()", "freeAvailable(address)",
              "saleStart()", "saleEnd()", "PRICE()", "price()", "launched()",
              "freeSharesLeft()", "freeSharesRemaining()", "freeClaimedByWallet(address)",
              "currentState()", "finalized()", "refunding()", "totalFreeMinted()", "openedAt()"]
r = raw_batch("0x5A0e704cf30Da4e84812C66eD94F012542e10046", LEG3_VIEWS)
out["leg3_retry_0x5A0e"] = {"views": r, "summary": {k: v for k, v in r.items() if v is not None} if r else None}
LEG4_VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
         "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)", "freeClaimed(address)",
         "freeUsed(address)", "mintedBy(address)", "freeMintedBy(address)", "mintStart()",
         "freeLeft()", "freeAvailable(address)", "saleStart()", "saleEnd()", "PRICE()",
         "price()", "launched()", "freeSharesLeft()", "openedAt()", "freeSharesRemaining()",
         "freeClaimedByWallet(address)", "currentState()", "finalized()", "refunding()",
         "totalFreeMinted()", "FREE_SHARES()", "freeLeftFor(address)"]
r2 = raw_batch("0xD405C90079c594DA2456F5b37B4158A12f1382e5", LEG4_VIEWS)
out["leg4_retry_LuckyCatch"] = {"views": r2, "summary": {k: v for k, v in r2.items() if v is not None} if r2 else None}
# shape-check deferred 0x5CA1 via Sourcify ABI
def curl_json(url, timeout=8):
    try:
        b = subprocess.run(["curl", "-s", "-m", str(timeout), "-A", "Mozilla/5.0", url],
                           capture_output=True, timeout=timeout + 5).stdout
        return json.loads(b.decode(errors="replace"))
    except Exception:
        return None
a = "0x5CA1c4B97647eB095e3036aFC2453a4232923FAe"
abi_j = curl_json(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", 8)
abi = None
if isinstance(abi_j, dict):
    abi = abi_j.get("abi") or (abi_j.get("stdJson") or {}).get("abi")
if abi:
    names = {(fn.get("name") or "").lower() for fn in abi if isinstance(fn, dict)}
    has_mint = any("mint" in n for n in names)
    has_quote = any(("quote" in n or n in ("cost", "price", "mintprice", "getprice")) for n in names)
    free_views = sorted(n for n in names if "free" in n)
    agent = any(("agent" in n and ("registry" in n or "gate" in n or "id" in n)) for n in names) or ("agent_id_registry" in json.dumps(abi).lower())
    is_token = any(n in names for n in ("name", "symbol", "decimals", "totalsupply"))
    out["shape_retry_0x5CA1"] = {"status": "checked", "S1": has_mint and has_quote and bool(free_views) and agent,
        "S2": is_token and ("mintfree" in names) and bool(free_views) and agent,
        "mint": has_mint, "quote": has_quote, "free": free_views, "agent": agent}
else:
    out["shape_retry_0x5CA1"] = {"status": "shape-check-failed", "note": "ABI still unfetchable"}
out["pending_next_run"] = {"leg4_skipped_deadline": ["0x016b9CE7", "0x2e50", "MOONDRILL", "CRTSAINTS",
    "SUDOSAINTS", "BinanceLife", "BUCKET", "Kongtou-AirdropCnNFT", "0x7Eb9", "NAOMI", "AgenticGangster"],
    "note": "leg4 deadline-hit in 1459 main run; re-read next run (no state change known)."}
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + "hot-leg-2026-11-12-1459-followup.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
