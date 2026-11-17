#!/usr/bin/env python3
"""Run 1601 verify-4: first-mint deep search (SOUL/WALL) with curl-based
block timestamps (urllib block_ts proved flaky under RPC degradation),
WALL eth_getCode via curl, SOUL tokenURI metadata via alt IPFS gateways.
Read-only. Writes run-2026-11-06-1601-verify4.json.
"""
import json, subprocess, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post  # noqa: E402
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1601"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"

def wib(ts):
    if ts is None: return None
    return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")

def curl_rpc(method, params, ep="https://bsc-dataseed2.bnbchain.org"):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    out = subprocess.run(["curl", "-s", "-m", "12", "-X", "POST", "-H",
                          "Content-Type: application/json", "-d", body, ep],
                         capture_output=True, text=True, timeout=20)
    try:
        d = json.loads(out.stdout)
        return d.get("result")
    except Exception:
        return None

def block_ts(blk):
    r = curl_rpc("eth_getBlockByNumber", [hex(blk), False])
    if r and r.get("timestamp"):
        return int(r["timestamp"], 16)
    # fallback publicnode
    r = curl_rpc("eth_getBlockByNumber", [hex(blk), False], "https://bsc.publicnode.com")
    if r and r.get("timestamp"):
        return int(r["timestamp"], 16)
    return None

def ankr_logs_wide(from_block, to_block, address):
    logs = []
    token = None
    for page in range(12):
        params = {"blockchain": "bsc", "fromBlock": hex(from_block), "toBlock": hex(to_block),
                  "address": [address], "topics": [[TRANSFER], [ZERO_TOPIC]], "pageSize": 1000}
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

for name, addr in [("soul", SOUL), ("wall", WALL)]:
    # walk backwards in 100k-block windows from 131800000 until an empty window
    hi = 131799999
    first_blk = None
    windows = []
    while hi > 131000000:
        lo = hi - 99999
        st, err, logs = ankr_logs_wide(lo, hi, addr)
        print(name, f"window {lo}-{hi}:", st, "logs:", len(logs), flush=True)
        windows.append((lo, hi, len(logs) if st == "ok" else err))
        if st != "ok":
            break
        if not logs:
            break
        first_blk = min(int(l["blockNumber"], 16) for l in logs)
        hi = lo - 1
    ts = block_ts(first_blk) if first_blk else None
    print(name, "FIRST_MINT block", first_blk, "wib", wib(ts), flush=True)
    out[name] = {"firstMintBlock": first_blk, "firstMintWib": wib(ts), "windows": windows}

# WALL code via curl
code = curl_rpc("eth_getCode", [WALL, "latest"])
w = {"code_len": (len(code)//2 - 1) if code else None}
if code:
    cl = code.lower()
    w["registry_bytes_in_code"] = REGISTRY[2:].lower() in cl
    def sel(s):
        k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
    for fname in ["mintFree()", "mint(uint256)", "freeMinted()", "freeClaimed()",
                  "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "totalSupply()",
                  "mintedBy(address)", "quote(address,uint256)", "agentId()",
                  "hasAgentId(address)"]:
        w[f"selector_{fname}"] = sel(fname) in cl
print("WALL code:", json.dumps(w), flush=True)
out["wall_code"] = w

# SOUL tokenURI metadata via alt gateways
cid = "QmdujoV4umgvWTLqU1bAXJhhLPGP1Vu26t6GteY16RXZSe/1"
for gw in ["https://gateway.pinata.cloud/ipfs/", "https://cloudflare-ipfs.com/ipfs/",
           "https://dweb.link/ipfs/", "https://ipfs.io/ipfs/"]:
    url = gw + cid
    try:
        out2 = subprocess.run(["curl", "-sL", "--max-time", "15", url],
                              capture_output=True, text=True, timeout=20)
        print("IPFS", gw, "len", len(out2.stdout), "head:", out2.stdout[:300], flush=True)
        if out2.stdout.strip().startswith("{"):
            out["soul_tokenURI_1"] = json.loads(out2.stdout)
            break
    except Exception as e:
        print("IPFS", gw, "error", e, flush=True)
out.setdefault("soul_tokenURI_1", None)

# QF firstSeenBlock timestamp via curl
ts = block_ts(131637153)
print("QF firstSeenBlock 131637153 wib", wib(ts), flush=True)
out["qf_firstSeenBlockWib"] = wib(ts)

json.dump(out, open(f"{BASE}/run-{TS}-verify4.json", "w"), indent=1)
print("VERIFY4 DONE", flush=True)
