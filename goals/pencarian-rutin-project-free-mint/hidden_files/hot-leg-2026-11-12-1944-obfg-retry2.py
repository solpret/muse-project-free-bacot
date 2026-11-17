#!/usr/bin/env python3
"""Hot-leg run 2026-11-12 19:44 WIB — OBFG second retry: uint batch for
0x5314071bba19943f58347bA5deC423E5032A6818 (follow-up batch returned null),
full quote(user,1) decode incl. trailing string, first-mint log probe if
freeMinted>0. Tight deadline T0+90s. Read-only; writes only own file."""
import json, time, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-12-1944"
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
NEW = "0x5314071bba19943f58347bA5deC423E5032A6818"
out = {"run": "free-mint-hot-leg 2026-11-12 19:44 WIB obfg-retry2", "started_wib": now_wib}

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

VIEWS = ["totalSupply()", "totalMinted()", "freeMinted()", "FREE_SUPPLY()", "FREE_PER_WALLET()",
         "freeRemaining()", "isFreeOpen()", "mintOpen()", "saleOpen()", "saleStart()", "saleEnd()",
         "SALE_END()", "PRICE()", "price()", "cost()", "maxSupply()", "MAX_SUPPLY()", "paidMinted()",
         "paidSupply()", "remainingSupply()", "publicRemaining()", "FREE_MODE()", "MAX_PER_TX()",
         "MAX_PER_WALLET()", "PAID_PER_WALLET()", "raisedWei()", "settledWei()", "saleClosed()",
         "freeAvailable(address)", "freeMintedBy(address)", "mintedBy(address)",
         "balanceOf(address)", "hasAgentId(address)", "remainingQuota(address)",
         "paidAvailable(address)", "owner()"]
r = None
for attempt in range(3):
    if time.time() > T0 + 60:
        break
    r = raw_batch(NEW, VIEWS)
    if r is not None and any(v is not None for v in r.values()):
        break
    time.sleep(2)
out["views"] = r
out["summary"] = {k: v for k, v in r.items() if v is not None} if r else None

# Full quote(user,1) decode
quote = None
if time.time() < T0 + 75:
    data = sel("quote(address,uint256)") + enc(USER) + format(1, "064x")
    res = post_rpc_race([{"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": NEW, "data": data}, "latest"]}], timeout=12)
    if isinstance(res, list) and res and isinstance(res[0], dict) and res[0].get("result"):
        try:
            b = bytes.fromhex(res[0]["result"][2:])
            words = [int.from_bytes(b[i:i + 32], "big") for i in range(0, min(len(b), 160), 32)]
            tail = None
            if len(words) >= 5 and words[4] < len(b):
                off = words[4]
                ln = int.from_bytes(b[off:off + 32], "big")
                tail = b[off + 32:off + 32 + ln].decode(errors="replace")
            quote = {"words": words, "tail_string": tail}
        except Exception as e:
            quote = {"decode_error": str(e)[:100]}
out["quote_user_1"] = quote

# First-mint probe if launched
out["first_mint_probe"] = None
try:
    fm = (r or {}).get("freeMinted")
    if fm is not None and fm > 0 and time.time() < T0 + 88:
        payload = [{"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                    "params": [{"fromBlock": "0x7ef3f00", "toBlock": "latest", "address": NEW,
                                "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                                           "0x0000000000000000000000000000000000000000000000000000000000000000"]}]}]
        res = post_rpc_race(payload, timeout=15)
        logs = res[0].get("result") if isinstance(res, list) and res and isinstance(res[0], dict) else None
        if isinstance(logs, list) and logs:
            first = logs[0]
            blk = int(first.get("blockNumber", "0x0"), 16)
            out["first_mint_probe"] = {"n_logs": len(logs), "first_block": blk,
                                       "first_tx": first.get("transactionHash")}
            # block timestamp
            rb = post_rpc_race([{"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                 "params": [hex(blk), False]}], timeout=12)
            if isinstance(rb, list) and rb and isinstance(rb[0], dict):
                ts = (rb[0].get("result") or {}).get("timestamp")
                if ts:
                    out["first_mint_probe"]["first_block_ts"] = int(ts, 16)
                    out["first_mint_probe"]["first_block_wib"] = datetime.fromtimestamp(
                        int(ts, 16), tz=timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        elif isinstance(logs, list):
            out["first_mint_probe"] = {"n_logs": 0, "note": "no Transfer-from-zero in range"}
        else:
            out["first_mint_probe"] = {"error": "getLogs unreadable", "raw": str(res)[:200]}
except Exception as e:
    out["first_mint_probe"] = {"error": str(e)[:150]}

if r and any(v is not None for v in r.values()):
    try:
        seen = json.load(open(BASE + "hot-leg-seen.json"))
        if isinstance(seen.get(NEW), dict):
            ssum = out["summary"] or {}
            seen[NEW]["note"] = (seen[NEW].get("note", "") +
                f" | RETRY2 {now_wib}: " + ", ".join(f"{k}={v}" for k, v in ssum.items())[:300] +
                f" | quote1={quote}").strip()[:1000]
            json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
    except Exception as e:
        out["seen_write_error"] = str(e)[:100]
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-{TAG}-obfg-retry2.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
