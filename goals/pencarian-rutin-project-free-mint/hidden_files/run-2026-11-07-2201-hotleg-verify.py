#!/usr/bin/env python3
"""Run 2201 hot-leg follow-up: full verify of 2 new S1 contracts from hot-leg 2149.
Read-only except own output file run-2026-11-07-2201-hotleg-verify.json.
- 0xa46D33862124Da90385cEb58acba63718729DEe0 (Sourcify feed S1)
- 0x2df7435f5bce0577bee213e13da68313c74d7d0b (Boltbook Agentdragon S1)
Fresh exact-view reads + Sourcify ABI/metadata + contractURI/tokenURI +
first-mint getLogs (chunked <=1000 blocks, bounded) for age.
"""
import json, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/",
       "https://rpc.ankr.com/bsc"]
DEADLINE = time.time() + 240
t0 = time.time()
out = {"run": "free-mint-search 2026-11-07 22:01 WIB discovery leg - hot-leg 2149 follow-up verify",
       "user_wallet": USER}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def raw(to, data):
    if time.time() > DEADLINE:
        return "deadline"
    for ep in EPS:
        if time.time() > DEADLINE:
            return "deadline"
        try:
            v = _fast_single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
            if v is None or v == "0x":
                return None
            try:
                return int(v, 16)
            except Exception:
                return v
        except Exception:
            continue
    return None
def call(to, sig, args=""): return raw(to, sel(sig) + args)
def decode_str(v):
    if not isinstance(v, str) or not v.startswith("0x") or len(v) < 138:
        return None
    try:
        b = bytes.fromhex(v[2:])
        off = int.from_bytes(b[32:64], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", "replace")
    except Exception:
        return None

blk = None
for ep in EPS:
    try:
        v = _fast_single(ep, "eth_blockNumber", [], 8, retries=0)
        if v:
            blk = int(v, 16); break
    except Exception:
        continue
out["block"] = blk
print("head block:", blk, flush=True)

def get_sourcify(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}"
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.loads(r.read().decode()), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP{e.code}"
    except Exception as e:
        return None, f"{type(e).__name__}:{e}"

def first_mint(addr, head, max_chunks=12):
    """Search Transfer(from=0x0) backwards in 1000-block chunks from head.
    Returns dict with first_mint_block found (lowest block with a mint in the
    scanned range) or scanned range if not found. Bounded: max_chunks."""
    topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    zero = "0x0000000000000000000000000000000000000000000000000000000000000000"
    found = None
    scanned = 0
    hi = head
    for i in range(max_chunks):
        if time.time() > DEADLINE:
            return {"status": "deadline", "scanned_chunks": scanned, "first_mint_block": found}
        lo = hi - 999
        for ep in EPS:
            try:
                res = _fast_single(ep, "eth_getLogs", [{"fromBlock": hex(lo), "toBlock": hex(hi),
                    "address": addr, "topics": [topic, zero]}], 15, retries=0)
                break
            except Exception:
                res = None
                continue
        scanned += 1
        if isinstance(res, list) and res:
            found = min(int(x["blockNumber"], 16) for x in res)
            return {"status": "found_in_scanned_range", "scanned_chunks": scanned,
                    "first_mint_block": found, "window_lo": lo, "window_hi": hi,
                    "mints_in_chunk": len(res)}
        hi = lo - 1
    return {"status": "not_found_in_last_%d_blocks" % (scanned * 1000),
            "scanned_chunks": scanned, "first_mint_block": None,
            "window_lo": hi + 1, "window_hi": head}

results = {}
for addr, label in [("0xa46D33862124Da90385cEb58acba63718729DEe0", "a46d"),
                    ("0x2df7435f5bce0577bee213e13da68313c74d7d0b", "agentdragon-2df7")]:
    d = {"label": label}
    # Sourcify
    sj, err = get_sourcify(addr)
    if sj:
        d["sourcify"] = {"match": sj.get("match"), "verifiedAt": sj.get("verifiedAt"),
                         "stdJson": bool(sj.get("stdJson")),
                         "metadata_urls": [str(sj.get("metadata", {}).get("settings", {}))[:0]] if False else None}
        abi = sj.get("abi") or []
        d["sourcify"]["n_functions"] = len([e for e in abi if e.get("type") == "function"])
        d["sourcify"]["functions"] = sorted({e.get("name") for e in abi if e.get("type") == "function"})
        raw_abi = json.dumps(abi).lower()
        d["sourcify"]["site_fn_hits"] = [n for n in d["sourcify"]["functions"]
                                         if any(w in n.lower() for w in ("website", "siteurl", "domain", "external", "uri", "url"))]
        d["sourcify"]["has_registry_ref"] = "60b9262456de011f7d15a54cdd8c48baaa8b022f" in raw_abi
        # metadata URLs (method C)
        meta = sj.get("metadata") or {}
        d["sourcify"]["metadata_sources"] = meta.get("sources", {})
        d["abi"] = abi
    else:
        d["sourcify"] = {"error": err}
    # exact views
    views = {}
    for sig, key in [("name()", "name"), ("symbol()", "symbol"),
                     ("totalSupply()", "totalSupply"), ("totalMinted()", "totalMinted"),
                     ("MAX_SUPPLY()", "MAX_SUPPLY"), ("FREE_SUPPLY()", "FREE_SUPPLY"),
                     ("FREE_CAP()", "FREE_CAP"), ("FREE_PER_WALLET()", "FREE_PER_WALLET"),
                     ("MAX_PER_WALLET()", "MAX_PER_WALLET"),
                     ("freeClaimed()", "freeClaimed"), ("freeMinted()", "freeMinted"),
                     ("freeMintedTotal()", "freeMintedTotal"),
                     ("freeSharesRemaining()", "freeSharesRemaining"),
                     ("mintOpen()", "mintOpen"), ("mintActive()", "mintActive"),
                     ("contractURI()", "contractURI"),
                     ("tokenURI(uint256)", "tokenURI_1"),
                     ("owner()", "owner"), ("agentRegistry()", "agentRegistry"),
                     ("AGENT_ID()", "AGENT_ID"), ("PRICE()", "PRICE"),
                     ("FREE_AMOUNT()", "FREE_AMOUNT"), ("FREE_SLOTS()", "FREE_SLOTS"),
                     ("MINT_START()", "MINT_START"), ("START_TIME()", "START_TIME"),
                     ("startTime()", "startTime")]:
        if sig.startswith("tokenURI"):
            v = call(addr, sig, enc_uint(1))
        else:
            v = call(addr, sig)
        views[key] = v
    for sig, key in [("balanceOf(address)", "balanceOf_user"),
                     ("freeLeft(address)", "freeLeft_user"),
                     ("freeUsed(address)", "freeUsed_user"),
                     ("mintedBy(address)", "mintedBy_user"),
                     ("freeClaimed(address)", "freeClaimed_user"),
                     ("freeMinted(address)", "freeMinted_user"),
                     ("freeFor(address)", "freeFor_user"),
                     ("mintedCount(address)", "mintedCount_user"),
                     ("hasMinted(address)", "hasMinted_user")]:
        views[key] = call(addr, sig, enc(USER))
    for sig, key in [("quote(address,uint256)", "quote_user1"),
                     ("quote(address,uint256,uint256)", "quote_user1_tier0")]:
        args = enc(USER) + enc_uint(1) if "uint256,uint256" not in sig else enc(USER) + enc_uint(1) + enc_uint(0)
        views[key] = call(addr, sig, args)
    for k in ("name", "symbol", "contractURI", "tokenURI_1"):
        if views.get(k):
            views[k] = decode_str(views[k])
    d["views"] = views
    # first-mint age check only if there are mints
    ts = views.get("totalSupply")
    tm = views.get("totalMinted")
    if isinstance(ts, int) and ts > 0:
        d["first_mint"] = first_mint(addr, blk)
        if d["first_mint"].get("first_mint_block"):
            fb = d["first_mint"]["first_mint_block"]
            # block timestamp via dataseed (Ankr returns fake timestamps - never use Ankr for this)
            ts_block = None
            for ep in EPS[:4]:
                try:
                    b = _fast_single(ep, "eth_getBlockByNumber", [hex(fb), False], 10, retries=0)
                    if b and b.get("timestamp"):
                        ts_block = int(b["timestamp"], 16); break
                except Exception:
                    continue
            d["first_mint"]["block_timestamp"] = ts_block
            if ts_block:
                import datetime
                d["first_mint"]["first_mint_wib"] = datetime.datetime.fromtimestamp(
                    ts_block, datetime.timezone(datetime.timedelta(hours=7))).isoformat()
    elif isinstance(tm, int) and tm > 0:
        d["first_mint"] = first_mint(addr, blk)
    else:
        d["first_mint"] = {"status": "no_mints_yet_totalSupply_0", "first_mint_block": None}
    results[addr] = d
    print(label, "done", json.dumps({k: v for k, v in views.items() if v is not None})[:400], flush=True)

out["contracts"] = results
out["duration_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{BASE}/run-2026-11-07-2201-hotleg-verify.json", "w"), indent=1)
print("WROTE run-2026-11-07-2201-hotleg-verify.json in", out["duration_s"], "s", flush=True)
