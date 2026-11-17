#!/usr/bin/env python3
"""Hot-leg run 2026-11-12 20:19 WIB — follow-up (bounded ~120s).
1) Re-read new sale-shape 0xBC1B... (leg3 views null in main run) with retries.
2) THONK retry (null 4x). 3) CRTSAINTS + MECHA leg4 nulls. 4) OliverAgents:
   slot/pool re-read + ONE eth_getLogs attempt for first-mint block (age corroboration).
5) Boltbook EN+ZH retry (both 0 bytes in main run). Read-only except own seen notes."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-12-2019"
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"followup": "free-mint-hot-leg 2026-11-12 20:19 WIB", "started_wib": now_wib}

def curl(url, timeout=10, data=None):
    cmd = ["curl", "-sL", "-m", str(timeout), "-A", "Mozilla/5.0"]
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", data]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout + 5)
        return r.stdout
    except Exception:
        return b""

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
    if res is None:
        return None
    return {key: (None if (isinstance(it, dict) and "error" in it)
                  else (to_int(it.get("result")) if isinstance(it, dict) else None))
            for it, key in zip(res, keys)}
def retry_batch(addr, views, attempts=3):
    for _ in range(attempts):
        if time.time() > T0 + 100:
            break
        r = raw_batch(addr, views)
        if r is not None and any(v is not None for v in r.values()):
            return r
        time.sleep(2)
    return r

LEG3_VIEWS = ["name()", "symbol()", "totalSupply()", "totalMinted()", "freeClaimed()",
              "freeMinted()", "FREE_SUPPLY()", "FREE_CAP()", "FREE_SHARES()", "MAX_SUPPLY()",
              "mintOpen()", "balanceOf(address)", "freeClaimed(address)", "freeUsed(address)",
              "mintedBy(address)", "mintStart()", "freeLeft()", "freeAvailable(address)",
              "saleStart()", "saleEnd()", "PRICE()", "price()", "launched()",
              "freeSharesLeft()", "freeSharesRemaining()", "freeClaimedByWallet(address)",
              "currentState()", "finalized()", "refunding()", "totalFreeMinted()", "openedAt()",
              "free_cap()", "freecount()", "mintFree()"]
LEG4_VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
              "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)", "freeClaimed(address)",
              "freeUsed(address)", "mintedBy(address)", "freeMintedBy(address)", "mintStart()",
              "freeLeft()", "freeAvailable(address)", "saleStart()", "saleEnd()", "PRICE()",
              "price()", "launched()", "freeSharesLeft()", "openedAt()", "freeSharesRemaining()",
              "freeClaimedByWallet(address)", "currentState()", "finalized()", "refunding()",
              "totalFreeMinted()", "FREE_SHARES()", "freeLeftFor(address)"]

BC1B = "0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053"
bc1b = retry_batch(BC1B, LEG3_VIEWS, 3)
out["bc1b"] = {"views": bc1b, "summary": {k: v for k, v in bc1b.items() if v is not None} if bc1b else None}

THONK = "0x22e69F9a7BeC3D991C0ceB5a103E509319E42B2A"
thonk = retry_batch(THONK, LEG3_VIEWS, 2)
out["thonk"] = {"views": thonk, "summary": {k: v for k, v in thonk.items() if v is not None} if thonk else None}

for name, addr in (("CRTSAINTS", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F"),
                   ("MECHA", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78")):
    r = retry_batch(addr, LEG4_VIEWS, 2)
    out[f"leg4_retry_{name}"] = {"views": r, "summary": {k: v for k, v in r.items() if v is not None} if r else None}

# OliverAgents: pool/slot + first-mint log attempt
OLIVER = "0xad86e4d52e55709d1bda08f922853d4b109e0810"
ol = retry_batch(OLIVER, ["freeMinted()", "freeRemaining()", "FREE_MAX()", "totalSupply()",
                          "balanceOf(address)", "mintOpen()", "freeClaimedByAgent(address)",
                          "freeClaimed(address)", "freeAvailable(address)"], 2)
out["oliver"] = {"views": ol, "summary": {k: v for k, v in ol.items() if v is not None} if ol else None}
# eth_getLogs: Transfer(address,address,uint256) from 0x0, blocks 133095000-133112000
logs = None
try:
    payload = [{"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs", "params": [{
        "fromBlock": hex(133095000), "toBlock": hex(133112000),
        "address": OLIVER,
        "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                   "0x0000000000000000000000000000000000000000000000000000000000000000"]}]}]
    res = post_rpc_race(payload, timeout=20)
    if isinstance(res, list) and res and isinstance(res[0], dict):
        if "result" in res[0]:
            logs = res[0]["result"]
            out["oliver_first_mint_logs"] = {"n": len(logs),
                "first_block": int(logs[0]["blockNumber"], 16) if logs else None,
                "first_tx": logs[0]["transactionHash"] if logs else None}
        else:
            out["oliver_first_mint_logs"] = {"error": str(res[0].get("error"))[:200]}
    else:
        out["oliver_first_mint_logs"] = {"error": "no-result"}
except Exception as e:
    out["oliver_first_mint_logs"] = {"error": str(e)[:200]}
if out["oliver_first_mint_logs"].get("first_block"):
    try:
        b = post_rpc_race([{"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                            "params": [hex(out["oliver_first_mint_logs"]["first_block"]), False]}], timeout=12)
        if isinstance(b, list) and b and isinstance(b[0], dict) and b[0].get("result"):
            ts = int(b[0]["result"]["timestamp"], 16)
            out["oliver_first_mint_logs"]["first_mint_time_wib"] = (
                datetime.fromtimestamp(ts, tz=timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB"))
    except Exception as e:
        out["oliver_first_mint_logs"]["block_time_error"] = str(e)[:120]

# Boltbook retry (both 0 bytes in main run)
import re
for lang in ("en", "zh"):
    url = "https://boltbook.fun/?lang=zh" if lang == "zh" else "https://boltbook.fun/?lang=en"
    raw = curl(url, 10)
    open(BASE + f"hot-leg-{TAG}-boltbook-{lang}-retry.html", "wb").write(raw)
    html = raw.decode(errors="replace")
    out[f"boltbook_retry_{lang}"] = {"bytes": len(html),
                                     "addrs": sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", html)))}
    time.sleep(0.2)

# Update seen notes (own file only)
seen = json.load(open(BASE + "hot-leg-seen.json"))
if bc1b and isinstance(seen.get(BC1B), dict):
    ssum = out["bc1b"]["summary"] or {}
    seen[BC1B]["note"] = (seen[BC1B].get("note", "") +
        f" | LEG3-FOLLOWUP {now_wib}: " + ", ".join(f"{k}={v}" for k, v in ssum.items())[:300]).strip()[:600]
if thonk and isinstance(seen.get(THONK), dict):
    ssum = out["thonk"]["summary"] or {}
    seen[THONK]["note"] = (seen[THONK].get("note", "") +
        f" | LEG3-RETRY {now_wib}: " + ", ".join(f"{k}={v}" for k, v in ssum.items())[:300]).strip()[:600]
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-{TAG}-followup.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
