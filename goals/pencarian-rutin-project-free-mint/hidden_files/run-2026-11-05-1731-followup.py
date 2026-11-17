#!/usr/bin/env python3
"""Run 1731 follow-up: promotion checks for MoonCat, SEAT, Forklings, PassAgentX.
Read-only. (a) free/supply/slot view reads; (b) first-mint via Ankr address-filtered
getLogs for MoonCat + SEAT (age unverified)."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")

def rpc_call(method, params, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:
            last = e
    raise last

def call(addr, sig, args=""):
    data = sel(sig) + args
    try:
        out = rpc_call("eth_call", [{"to": addr, "data": data}, "latest"])
    except Exception:
        return None
    if not isinstance(out, str) or not out.startswith("0x") or len(out) < 66:
        return None
    try:
        return int(out[2:66], 16)
    except Exception:
        return out

TARGETS = {
    "MoonCat": "0x045425004b622733ced4139e930c622187ea6c73",
    "SEAT-f11e": "0xf11e9405b23ca0f53e6135162a85545d780a3737",
    "Forklings": "0xD7B3FD33e0b465B0e374906F60567D317b758FD8",
    "PassAgentX": "0x08b1A979Dd997492EEcc010fe986eA2e2925e620",
}
VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "FREE_SUPPLY()", "FREE_CAP()", "MAX_SUPPLY()", "mintOpen()", "mintPrice()"]
SLOT_VIEWS = [("balanceOf(address)", enc(USER)), ("mintedBy(address)", enc(USER)),
              ("freeUsed(address)", enc(USER)), ("canFreeMint(address)", enc(USER)),
              ("claimedFree(address)", enc(USER)),
              ("quote(address,uint256)", enc(USER) + enc_u(1)),
              ("freeLeft(address)", enc(USER)), ("freeFor(address)", enc(USER))]

out = {"views": {}}
for name, addr in TARGETS.items():
    d = {"address": addr}
    for v in VIEWS:
        d[v] = call(addr, v)
    for sig, args in SLOT_VIEWS:
        d[sig] = call(addr, sig, args)
    out["views"][name] = d
    print(name, d, flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-05-1731-followup.json", "w"), indent=1)

# ---- first-mint via Ankr address-filtered getLogs ----
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
TRANSFER = "0x" + keccak(b"Transfer(address,address,uint256)").hex()

def ankr_logs_addr(addr, from_block, to_block, max_pages=10):
    logs, page_token, pages = [], "", 0
    while True:
        params = {"blockchain": "bsc", "fromBlock": hex(from_block),
                  "toBlock": hex(to_block), "address": addr.lower(),
                  "pageSize": 1000, "decodeLogs": False,
                  "topics": [TRANSFER, ZERO]}
        if page_token:
            params["pageToken"] = page_token
        try:
            body = ankr_post("ankr_getLogs", params, timeout=30)
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                time.sleep(30)
                body = ankr_post("ankr_getLogs", params, timeout=30)
            else:
                raise
        result = body.get("result", {}) if isinstance(body, dict) else {}
        logs.extend(result.get("logs", []))
        page_token = result.get("nextPageToken") or ""
        pages += 1
        if not page_token or pages >= max_pages:
            break
        time.sleep(2.2)
    return logs, pages

def block_ts(blk):
    try:
        b = rpc_call("eth_getBlockByNumber", [hex(blk), False])
        return int(b["timestamp"], 16)
    except Exception:
        return None

head = int(rpc_call("eth_blockNumber", []), 16)
print("HEAD", head, flush=True)
out["head"] = head
for name in ["MoonCat", "SEAT-f11e"]:
    addr = TARGETS[name]
    # expand backwards in 20000-block jumps until logs found
    found = None
    hi = head
    lo = max(131500000, head - 20000)
    tries = 0
    while hi > 131500000 and tries < 12:
        logs, pages = ankr_logs_addr(addr, lo, hi)
        print(name, f"range {lo}-{hi}: {len(logs)} logs", flush=True)
        if logs:
            # narrow: first log in this range; then refine within range in 2000-chunks
            first_blk = min(int(l["blockNumber"], 16) for l in logs)
            # refine: scan 2000-chunks from lo upward to first chunk with logs
            c_lo = lo
            while c_lo <= first_blk:
                c_hi = min(c_lo + 1999, hi)
                clogs, _ = ankr_logs_addr(addr, c_lo, c_hi)
                if clogs:
                    first_blk = min(int(l["blockNumber"], 16) for l in clogs)
                    break
                c_lo = c_hi + 1
            found = first_blk
            break
        hi = lo - 1
        lo = max(131500000, hi - 19999)
        tries += 1
    if found:
        ts = block_ts(found)
        import datetime
        wib = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB") if ts else None
        out.setdefault("first_mint", {})[name] = {"block": found, "timestamp": ts, "wib": wib}
        print(name, "FIRST MINT block", found, "->", wib, flush=True)
    else:
        out.setdefault("first_mint", {})[name] = None
        print(name, "NO mint found down to 131500000", flush=True)
    json.dump(out, open(f"{BASE}/run-2026-11-05-1731-followup.json", "w"), indent=1)
print("DONE", flush=True)
