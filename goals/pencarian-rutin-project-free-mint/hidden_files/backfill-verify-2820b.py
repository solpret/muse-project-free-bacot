#!/usr/bin/env python3
"""Agent Panda 0x2820 verify part 2: correct Ankr params + free-path retry.
Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import race
from Crypto.Hash import keccak
from ankr import ankr_post

ADDR = "0x2820e61eD78aC29F52eDAE05F01aB552307b907C"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_NP = USER[2:].lower()
ZERO_TOPIC = "0x" + "0" * 64
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def call(data, label):
    try:
        r = race("eth_call", [{"to": ADDR, "data": data}, "latest"])
        if isinstance(r, str) and r.startswith("0x") and len(r) >= 66:
            print(f"{label}: {int(r,16)}")
            return int(r, 16)
        print(f"{label}: revert-or-short: {str(r)[:120]}")
        return None
    except Exception as e:
        print(f"{label}: TRANSPORT-FAIL {type(e).__name__}: {str(e)[:100]}")
        return None

def ankr_mints(lo, hi):
    """Return (count, earliest_block) of Transfer-from-zero logs in range."""
    params = {"blockchain": "bsc", "fromBlock": hex(lo), "toBlock": hex(hi),
              "address": ADDR, "topics": [TRANSFER, ZERO_TOPIC],
              "pageSize": 1000, "decodeLogs": False}
    total = 0; earliest = None; pages = 0; token = None
    while pages < 10:
        p = dict(params)
        if token: p["pageToken"] = token
        try:
            body = ankr_post("ankr_getLogs", p, timeout=30)
        except Exception as e:
            print(f"  ankr {lo}-{hi} page {pages} FAIL {type(e).__name__}: {str(e)[:120]}")
            return None, None
        res = body.get("result", {}) if isinstance(body, dict) else {}
        logs = res.get("logs", [])
        total += len(logs)
        for lg in logs:
            b = int(lg["blockNumber"], 16)
            if earliest is None or b < earliest: earliest = b
        token = res.get("nextPageToken")
        pages += 1
        if not token: break
        time.sleep(2.2)
    return total, earliest

print("== free-path retry (slow, 3s gaps) ==")
for label, data in [
    ("freeRemainingFor(user)", sel("freeRemainingFor(address)") + USER_NP),
    ("freeMintedBy(user)", sel("freeMintedBy(address)") + USER_NP),
    ("free_per_wallet_agent()", sel("free_per_wallet_agent()")),
    ("mint_price()", sel("mint_price()")),
    ("max_supply()", sel("max_supply()")),
    ("totalMinted()", sel("totalMinted()")),
    ("agentRegistry()", sel("agentRegistry()")),
]:
    call(data, label)
    time.sleep(3)

print("== earliest mint search (50k-block chunks backward from 132116365) ==")
hi = 132116365
earliest_overall = None
lo = hi
while lo > 131300000:
    lo = max(131300000, hi - 49999)
    n, e = ankr_mints(lo, hi)
    print(f"  {lo}-{hi}: count={n} earliest={e}")
    if n is None:
        print("  TRANSPORT FAIL - stop, age unverified for this range")
        break
    if e is not None:
        earliest_overall = e
        break  # earliest chunk containing a mint; refine inside it below
    hi = lo - 1
if earliest_overall is not None:
    print(f"EARLIEST-MINT-BLOCK in searched range: {earliest_overall}")
    try:
        b = race("eth_getBlockByNumber", [hex(earliest_overall), False])
        ts = int(b["timestamp"], 16)
        print("earliest-mint-wib:", time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7*3600)))
        print("age-hours-now:", round((time.time() - ts)/3600, 1))
    except Exception as e:
        print("block ts FAIL:", e)
else:
    print("NO MINT found in 131300000-132116365 (or search failed) - first mint may predate 131300000")
