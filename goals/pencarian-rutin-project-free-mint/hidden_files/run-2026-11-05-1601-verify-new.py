#!/usr/bin/env python3
"""Run 1601: strict agent-shape verify for registry-hit first-seen contracts
(Lucky Box LUCK, DinoEra DINO). STRICT rule: agent-shaped ONLY if (a) registry
bytes verified via a DIRECT eth_getCode call AND (b) free views actually
RESPOND on-chain (freeMinted/FREE_SUPPLY/quote/canFreeMint/etc. returning a
value, not reverting). Sourcify-UNVERIFIED + registry-bytes-only + no responding
free shape = NOT agent-shaped. First mint via Ankr getLogs Transfer-from-zero
binary search; block timestamp = age. Read-only. No preview/mint."""
import json, sys, datetime, urllib.request
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-05-1601"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
REGISTRY_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed3.bnbchain.org"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TARGETS = [
    ("Lucky Box", "0xd08ef372B52C29255fEd7004f59bF41571451894", 131790141),
    ("DinoEra", "0xb7ae3eF58f4507a29115DEc6Eb8De7fEEcc3b6C4", 131790141),
]
LO = 131700000  # search low bound: ~90k blocks (~11h) before window start

def any_mint(addr, lo, hi):
    params = {"blockchain": "bsc", "fromBlock": hex(lo), "toBlock": hex(hi),
              "pageSize": 1000, "decodeLogs": False, "topics": [TRANSFER, ZERO], "address": addr}
    body = ankr_post("ankr_getLogs", params, timeout=30)
    logs = (body.get("result", {}) or {}).get("logs", []) if isinstance(body, dict) else []
    for lg in logs:
        if len(lg.get("topics", [])) == 4:
            return int(lg["blockNumber"], 16)
    return None

def first_mint(addr, lo, hi):
    if any_mint(addr, lo, hi) is None:
        return None
    while lo < hi:
        mid = (lo + hi) // 2
        if any_mint(addr, lo, mid) is not None:
            hi = mid
        else:
            lo = mid + 1
    return lo

def block_ts(n):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                               "params": [hex(n), False]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                return int(json.load(r)["result"]["timestamp"], 16)
        except Exception:
            continue
    return None

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]

def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")

def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=12) as r:
                out = json.load(r)
            if "error" in out:
                return {"error": str(out["error"])[:80]}
            v = out["result"]
            if not v or v == "0x":
                return None
            try:
                return int(v, 16)
            except Exception:
                return v
        except Exception:
            continue
    return {"error": "rpc-fail"}

def get_code(to):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                               "params": [to, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=12) as r:
                return json.load(r)["result"]
        except Exception:
            continue
    return None

def cstr(v):
    if isinstance(v, dict) or not v or v == "0x":
        return v
    try:
        h = v[2:]; ln = int(h[64:128], 16)
        return bytes.fromhex(h[128:128 + ln * 2]).decode(errors="replace")
    except Exception:
        return v

def call(to, sig, args=""):
    return raw(to, sel(sig) + args)

def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                return int(json.load(r)["result"], 16)
        except Exception:
            continue
    return None

FREE_VIEWS = ["freeMinted()", "freeClaimed()", "FREE_CAP()", "FREE_SUPPLY()",
              "FREE_AMOUNT()", "freeLeft()", "freeSupply()", "freeMintedBy(address)",
              "freeClaimedBy(address)", "canFreeMint(address)", "claimedFree(address)",
              "freeFor(address)", "freeUsed(address)", "freeAvailable()"]

res = {"block": block(), "run": "1601", "search_window": [LO, None]}
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
for name, addr, win_start in TARGETS:
    code = get_code(addr)
    reg_direct = bool(code and REGISTRY_BYTES in code[2:].lower()) if isinstance(code, str) else None
    print(f"{name} direct eth_getCode registry-bytes hit: {reg_direct} (code len {len(code) if isinstance(code, str) else '?'})", flush=True)
    hi = win_start
    b = first_mint(addr, LO, hi)
    note = ""
    if b is None:
        note = f"NO ERC721 mint found in {LO}-{hi}; first mint may be inside window only (scan first_block) or LO too high"
    elif b <= LO + 5:
        note = "earliest at search low bound - may be earlier"
    ts = block_ts(b) if b else None
    wib = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat() if ts else None
    age_h = round((now.timestamp() - ts) / 3600, 2) if ts else None
    res[name + "_firstMint"] = {"block": b, "ts": ts, "wib": wib, "age_hours": age_h, "note": note}
    res[name + "_registry_direct"] = reg_direct
    print(name, "firstMint", res[name + "_firstMint"], flush=True)
    reads = {}
    for fn in ["name()", "symbol()", "totalSupply()", "MAX_SUPPLY()", "mintOpen()",
               "owner()", "PRICE()", "price()", "START_TIME()", "startTime()"]:
        v = call(addr, fn)
        reads[fn] = cstr(v) if fn in ("name()", "symbol()") else v
    for fn in FREE_VIEWS:
        if "(address)" in fn:
            v = call(addr, fn.split("(")[0] + "(address)", enc(USER))
            reads[fn] = v
        else:
            reads[fn] = call(addr, fn)
    reads["quote(user,1)"] = call(addr, "quote(address,uint256)", enc(USER) + enc_u(1))
    reads["freeLeft(user)"] = call(addr, "freeLeft(address)", enc(USER))
    reads["mintedBy(user)"] = call(addr, "mintedBy(address)", enc(USER))
    reads["balanceOf(user)"] = call(addr, "balanceOf(address)", enc(USER))
    reads["contractURI()"] = cstr(call(addr, "contractURI()"))
    reads["REGISTRY()"] = call(addr, "REGISTRY()")
    reads["AGENT_REGISTRY()"] = call(addr, "AGENT_REGISTRY()")
    # (b): any free view responding with a non-error value?
    responding = [k for k, v in reads.items()
                  if ("free" in k.lower() or "FREE" in k)
                  and not isinstance(v, dict) and v is not None]
    reads["free_views_responding"] = responding
    fm = reads.get("freeMinted()")
    cap = reads.get("FREE_CAP()")
    if cap is None:
        cap = reads.get("FREE_SUPPLY()")
    if isinstance(fm, int) and isinstance(cap, int) and cap > 0:
        reads["free_pct_verified"] = round(100.0 * fm / cap, 2)
    else:
        reads["free_pct_verified"] = "UNVERIFIED"
    reads["agent_shaped_strict"] = bool(reg_direct and responding)
    res[name + "_read"] = reads
    print(name, json.dumps(reads), flush=True)

json.dump(res, open(f"{BASE}/run-{TS}-verify-new.json", "w"), indent=1)
print("DONE block", res["block"])
