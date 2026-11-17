#!/usr/bin/env python3
"""Run 1601 verify-3: fix first-mint bounds (wide-range Ankr queries instead of
the buggy backwards-empty-chunk loop), retry WALL eth_getCode, retry QF
firstSeenBlock timestamp. Read-only. Writes run-2026-11-06-1601-verify3.json.
"""
import json, urllib.request, sys, time, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post  # noqa: E402

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1601"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed.binance.org"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"

def wib(ts):
    if ts is None: return None
    return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")

def block_ts(blk):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                               "params": [hex(blk), False]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: out = json.load(r)
            if "result" in out and out["result"]:
                return int(out["result"]["timestamp"], 16)
        except Exception:
            continue
    return None

def get_code(to):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                               "params": [to, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r: out = json.load(r)
            if "result" in out and out["result"] and out["result"] != "0x":
                return out["result"]
        except Exception:
            continue
    return None

def ankr_logs_wide(from_block, to_block, address):
    """Wide range, paged via nextPageToken (ankr_post handles paging? No -
    ankr_post is a single call; use pageSize + nextPageToken manually)."""
    logs = []
    token = None
    for page in range(12):
        params = {"blockchain": "bsc", "fromBlock": hex(from_block), "toBlock": hex(to_block),
                  "address": [address], "topics": [[TRANSFER], [ZERO_TOPIC]],
                  "pageSize": 1000}
        if token: params["nextPageToken"] = token
        try:
            body = ankr_post("ankr_getLogs", params, timeout=60)
        except Exception as e:
            return ("error", str(e), logs)
        if isinstance(body, dict) and "error" in body:
            return ("error", str(body["error"]), logs)
        res = body.get("result", body) if isinstance(body, dict) else {}
        logs += res.get("logs", [])
        token = res.get("nextPageToken")
        if not token:
            break
    return ("ok", None, logs)

out = {}
SOUL = "0x8fdb9411753c58476a41f7b88a44989f8d687d63"
WALL = "0xa804bBBe09fa2F5832d11D09329cc4230D1d7899"
HEAD = 131985606

for name, addr in [("soul", SOUL), ("wall", WALL)]:
    # wide query from early morning today (block ~131900000) to head
    st, err, logs = ankr_logs_wide(131900000, HEAD, addr)
    print(name, "wide 131900000-head:", st, "logs:", len(logs), "err:", err, flush=True)
    if st == "ok" and logs:
        first_blk = min(int(l["blockNumber"], 16) for l in logs)
        ts = block_ts(first_blk)
        print(name, "FIRST_MINT block", first_blk, "wib", wib(ts), "mints_in_range", len(logs), flush=True)
        out[name] = {"firstMintBlock": first_blk, "firstMintWib": wib(ts),
                     "mintsSince131900000": len(logs)}
        # check whether any mint exists before 131900000 (older window)
        st2, err2, logs2 = ankr_logs_wide(131800000, 131899999, addr)
        print(name, "older window 131800000-131899999:", st2, "logs:", len(logs2), flush=True)
        out[name]["mints131800000_131899999"] = len(logs2) if st2 == "ok" else None
        if st2 == "ok" and logs2:
            fb2 = min(int(l["blockNumber"], 16) for l in logs2)
            out[name]["firstMintBlock"] = fb2
            out[name]["firstMintWib"] = wib(block_ts(fb2))
            print(name, "EARLIER first mint block", fb2, "wib", out[name]["firstMintWib"], flush=True)
    else:
        out[name] = {"firstMintBlock": None, "note": f"wide query {st} {err}"}

# WALL code retry
code = get_code(WALL)
w = {"code_len": (len(code)//2 - 1) if code else None}
if code:
    cl = code.lower()
    w["registry_bytes_in_code"] = REGISTRY[2:].lower() in cl
    from Crypto.Hash import keccak
    def sel(s):
        k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
    for fname in ["mintFree()", "mint(uint256)", "freeMinted()", "freeClaimed()",
                  "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "totalSupply()",
                  "mintedBy(address)", "quote(address,uint256)"]:
        w[f"selector_{fname}"] = sel(fname) in cl
print("WALL code:", json.dumps(w), flush=True)
out["wall_code"] = w

# QF firstSeenBlock timestamp retry
ts = block_ts(131637153)
print("QF firstSeenBlock 131637153 wib", wib(ts), flush=True)
out["qf_firstSeenBlockWib"] = wib(ts)

json.dump(out, open(f"{BASE}/run-{TS}-verify3.json", "w"), indent=1)
print("VERIFY3 DONE", flush=True)
