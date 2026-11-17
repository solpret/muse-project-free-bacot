#!/usr/bin/env python3
"""Run 1601 verify-2: corrected SOUL views, WALL bytecode check, first-mint
bounds (SOUL/WALL/Quantumfarm), Quantumfarm slot re-read. Read-only.
Fixes verify.py crash (HEAD None): head via fast_rpc _single with fallback.
Never writes the main snapshot; writes run-2026-11-06-1601-verify2.json only.
"""
import json, urllib.request, urllib.error, subprocess, time, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single  # noqa: E402
from ankr import ankr_post  # noqa: E402

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1601"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed.binance.org"]
from Crypto.Hash import keccak

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data, timeout=8):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None

def raw_hex(to, data, timeout=8):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            return v
        except Exception:
            continue
    return None

def get_code(to, timeout=10):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                               "params": [to, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "result" in out and out["result"] and out["result"] != "0x":
                return out["result"]
        except Exception:
            continue
    return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

def head():
    for ep in RPCS:
        try:
            return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception as e:
            print("head fail", ep, e, flush=True)
            continue
    return None

def decode_str(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode("utf-8", "replace")
    except Exception:
        return None

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

def wib(ts):
    if ts is None: return None
    return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")

TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"

def ankr_logs(from_block, to_block, address):
    params = {"blockchain": "bsc", "fromBlock": hex(from_block), "toBlock": hex(to_block),
              "address": [address], "topics": [[TRANSFER], [ZERO_TOPIC]]}
    try:
        body = ankr_post("ankr_getLogs", params, timeout=30)
    except Exception as e:
        return ("error", str(e))
    if isinstance(body, dict) and "error" in body:
        return ("error", str(body["error"]))
    return ("ok", body.get("logs", []) if isinstance(body, dict) else [])

hd = head()
print("HEAD", hd, flush=True)
out = {"head": hd}

# ---- SOUL corrected views ----
SOUL = "0x8fdb9411753c58476a41f7b88a44989f8d687d63"
s = {"address": SOUL}
for sig in ["FREE_MINTS_PER_WALLET()", "FREE_TIER_END()", "MAX_PER_WALLET()",
            "MAX_SUPPLY()", "mintOpen()", "priceBefore3000()", "priceAfter3000()",
            "totalMinted()", "totalSupply()", "agentId()", "owner()"]:
    s[sig.split("(")[0]] = call(SOUL, sig)
s["agentId_raw"] = raw_hex(SOUL, sel("agentId()"))
s["quoteFor_user_1"] = call(SOUL, "quoteFor(address,uint256)", enc(USER) + enc_uint(1))
s["mintedPerWallet_user"] = call(SOUL, "mintedPerWallet(address)", enc(USER))
s["balanceOf_user"] = call(SOUL, "balanceOf(address)", enc(USER))
s["hasAgentId_user"] = call(SOUL, "hasAgentId(address)", enc(USER))
s["baseURI"] = decode_str(raw_hex(SOUL, sel("baseURI()")) or "")
hx = raw_hex(SOUL, sel("tokenURI(uint256)") + enc_uint(1))
s["tokenURI_1"] = decode_str(hx) if hx else None
print("SOUL", json.dumps(s, default=str), flush=True)
out["soul"] = s

# ---- WALL bytecode + view probes ----
WALL = "0xa804bBBe09fa2F5832d11D09329cc4230D1d7899"
w = {"address": WALL}
code = get_code(WALL)
w["code_len"] = len(code)//2 - 1 if code else None
if code:
    cl = code.lower()
    w["registry_bytes_in_code"] = REGISTRY[2:].lower() in cl
    for fname in ["mintFree()", "mint(uint256)", "freeMinted()", "freeClaimed()",
                  "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "totalSupply()"]:
        w[f"selector_{fname}"] = sel(fname) in cl
for sig in ["totalMinted()", "freeMinted()", "freeClaimed()", "freeLeft()",
            "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "totalSupply()"]:
    w[sig.split("(")[0]] = call(WALL, sig)
w["mintedBy_user"] = call(WALL, "mintedBy(address)", enc(USER))
w["freeUsed_user"] = call(WALL, "freeUsed(address)", enc(USER))
w["balanceOf_user"] = call(WALL, "balanceOf(address)", enc(USER))
w["quote_user_1"] = call(WALL, "quote(address,uint256)", enc(USER) + enc_uint(1))
w["name"] = decode_str(raw_hex(WALL, sel("name()")) or "")
w["symbol"] = decode_str(raw_hex(WALL, sel("symbol()")) or "")
w["contractURI"] = decode_str(raw_hex(WALL, sel("contractURI()")) or "")
w["baseURI"] = decode_str(raw_hex(WALL, sel("baseURI()")) or "")
hx = raw_hex(WALL, sel("tokenURI(uint256)") + enc_uint(1))
w["tokenURI_1"] = decode_str(hx) if hx else None
print("WALL", json.dumps(w, default=str), flush=True)
out["wall"] = w

# ---- Quantumfarm slot re-read ----
QF = "0xA6Cf213F21C68b87f03Aa7d2a005e78F651eE010"
q = {"address": QF}
for sig in ["totalSupply()", "freeClaimed()", "freeLeft()", "FREE_SUPPLY()",
            "MAX_SUPPLY()", "mintOpen()", "totalMinted()"]:
    q[sig.split("(")[0]] = call(QF, sig)
q["mintedBy_user"] = call(QF, "mintedBy(address)", enc(USER))
q["freeUsed_user"] = call(QF, "freeUsed(address)", enc(USER))
q["freeFor_user"] = call(QF, "freeFor(address)", enc(USER))
q["balanceOf_user"] = call(QF, "balanceOf(address)", enc(USER))
q["quote_user_1"] = call(QF, "quote(address,uint256)", enc(USER) + enc_uint(1))
q["name"] = decode_str(raw_hex(QF, sel("name()")) or "")
q["symbol"] = decode_str(raw_hex(QF, sel("symbol()")) or "")
q["owner"] = raw_hex(QF, sel("owner()"))
print("QF", json.dumps(q, default=str), flush=True)
out["quantumfarm"] = q
json.dump(out, open(f"{BASE}/run-{TS}-verify2.json", "w"), indent=1)

# ---- first-mint bounds (backwards, 1000-block chunks) ----
if hd:
    for name, addr in [("soul", SOUL), ("wall", WALL)]:
        to_blk = hd
        first_blk = None
        chunks = 0
        while chunks < 60 and to_blk > 0:
            frm = max(0, to_blk - 999)
            st, logs = ankr_logs(frm, to_blk, addr)
            chunks += 1
            if st == "error":
                print(name, "ankr error chunk", frm, to_blk, logs, flush=True)
                break
            if not logs:
                break
            first_blk = min(int(l["blockNumber"], 16) for l in logs)
            to_blk = frm - 1
        if first_blk is not None:
            ts = block_ts(first_blk)
            print(name, "FIRST_MINT block", first_blk, "wib", wib(ts), "chunks", chunks, flush=True)
            out[name]["firstMintBlock"] = first_blk
            out[name]["firstMintWib"] = wib(ts)
        else:
            print(name, "FIRST_MINT not found in", chunks, "chunks back; searched to block", to_blk, flush=True)
            out[name]["firstMintBlock"] = None
            out[name]["searchedToBlock"] = to_blk
        json.dump(out, open(f"{BASE}/run-{TS}-verify2.json", "w"), indent=1)
    # Quantumfarm first-mint timestamp from known firstSeenBlock
    ts = block_ts(131637153)
    print("QF firstSeenBlock 131637153 wib", wib(ts), flush=True)
    out["quantumfarm"]["firstSeenBlockWib"] = wib(ts)
    json.dump(out, open(f"{BASE}/run-{TS}-verify2.json", "w"), indent=1)

print("VERIFY2 DONE", flush=True)
