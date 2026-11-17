#!/usr/bin/env python3
"""Run 2131: on-chain verification of 2 Sourcify shape-pass contracts.
Read-only. Writes run-2026-11-06-2131-sourcify-verify.json."""
import json, subprocess, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2131"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
RPCS = ["https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed1.bnbchain.org",
        "https://bsc.publicnode.com", "https://bsc-dataseed3.bnbchain.org"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data, timeout=6):
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

def call(to, sig, args=""): return raw(to, sel(sig) + args)

def raw_str(to, data, timeout=6):
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

def dec_str(hexv):
    if not hexv or len(hexv) < 130: return None
    try:
        b = bytes.fromhex(hexv[2:])
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96+ln].decode("utf-8", "replace")
    except Exception:
        return None

def block_ts(n):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                               "params": [hex(n), False]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=6) as r: out = json.load(r)
            return int(out["result"]["timestamp"], 16)
        except Exception:
            continue
    return None

def first_transfer(addr, head):
    """First Transfer (from 0x0) via chunked eth_getLogs, newest->oldest search in 1000-block chunks back up to 200k blocks."""
    topic0 = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    from_topic = "0x" + "00" * 32
    lo = max(0, head - 200000)
    # binary-ish: scan backwards in 5000-block chunks, stop at first chunk with a hit, then narrow
    hi = head
    found = None
    while hi > lo:
        frm = max(lo, hi - 4999)
        for rpc in RPCS:
            try:
                body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                                   "params": [{"fromBlock": hex(frm), "toBlock": hex(hi),
                                               "address": addr, "topics": [topic0, from_topic]}]}).encode()
                req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=15) as r: out = json.load(r)
                logs = out.get("result", [])
                if logs:
                    found = logs
                    break
                break
            except Exception:
                continue
        if found:
            # narrow within this chunk: earliest log
            first = min(found, key=lambda l: int(l["blockNumber"], 16))
            return first
        hi = frm - 1
    return None

def head():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None

out = {}
H = head()
out["head"] = H
print("head", H, flush=True)

# --- Contract 1: NFT soulbound claim ---
a1 = "0x7fe03C055588bd5018825175D791103c5CBEd8be"
r1 = {"address": a1}
r1["name"] = dec_str(raw_str(a1, sel("name()")))
r1["symbol"] = dec_str(raw_str(a1, sel("symbol()")))
r1["totalSupply"] = call(a1, "totalSupply()")
r1["totalMinted"] = call(a1, "totalMinted()")
r1["claimOpen"] = call(a1, "claimOpen()")
r1["claimTimeLeft"] = call(a1, "claimTimeLeft()")
r1["CLAIM_START"] = call(a1, "CLAIM_START()")
r1["CLAIM_END"] = call(a1, "CLAIM_END()")
r1["CLAIM_WINDOW"] = call(a1, "CLAIM_WINDOW()")
r1["MIN_BALANCE"] = call(a1, "MIN_BALANCE()")
ag = call(a1, "AGENT_ID()")
r1["AGENT_ID_raw"] = ag
r1["AGENT_ID_is_registry"] = (ag == int(REGISTRY, 16)) if isinstance(ag, int) else None
r1["agentRegistry"] = call(a1, "agentRegistry()")
r1["balanceOf_user"] = call(a1, "balanceOf(address)", enc(USER))
r1["claimed_user"] = call(a1, "claimed(address)", enc(USER))
r1["hasClaimed_user"] = call(a1, "hasClaimed(address)", enc(USER))
r1["freeClaimed_user"] = call(a1, "freeClaimed(address)", enc(USER))
ft = first_transfer(a1, H) if H else None
if ft:
    bn = int(ft["blockNumber"], 16)
    ts = block_ts(bn)
    r1["firstMintBlock"] = bn
    r1["firstMintTs"] = ts
    import datetime
    r1["firstMintWib"] = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S") if ts else None
    r1["firstMinter"] = "0x" + ft["topics"][2][26:]
else:
    r1["firstMintBlock"] = None
out["sourcify_nft_claim"] = r1
print("C1", json.dumps(r1), flush=True)

# --- Contract 2: Track-C S2 token+sale ---
a2 = "0x9e2738B3DD3773c6c71cA24Fbc92660B501C0B6b"
r2 = {"address": a2}
r2["name"] = dec_str(raw_str(a2, sel("name()")))
r2["symbol"] = dec_str(raw_str(a2, sel("symbol()")))
r2["decimals"] = call(a2, "decimals()")
r2["totalSupply"] = call(a2, "totalSupply()")
r2["freeClaimed"] = call(a2, "freeClaimed()")
r2["freeTaken_user"] = call(a2, "freeTaken(address)", enc(USER))
r2["FREE_PER_WALLET"] = call(a2, "FREE_PER_WALLET()")
r2["FREE_TOKENS"] = call(a2, "FREE_TOKENS()")
r2["FREE_SUPPLY"] = call(a2, "FREE_SUPPLY()")
r2["FREE_AMOUNT"] = call(a2, "FREE_AMOUNT()")
ag2 = call(a2, "AGENT_ID()")
r2["AGENT_ID_raw"] = ag2
r2["AGENT_ID_is_registry"] = (ag2 == int(REGISTRY, 16)) if isinstance(ag2, int) else None
r2["agentRegistry"] = call(a2, "agentRegistry()")
r2["balanceOf_user"] = call(a2, "balanceOf(address)", enc(USER))
r2["launched"] = call(a2, "launched()")
r2["claimOpen"] = call(a2, "claimOpen()")
r2["mintOpen"] = call(a2, "mintOpen()")
ft2 = first_transfer(a2, H) if H else None
if ft2:
    bn = int(ft2["blockNumber"], 16)
    ts = block_ts(bn)
    r2["firstMintBlock"] = bn
    r2["firstMintTs"] = ts
    import datetime
    r2["firstMintWib"] = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S") if ts else None
    r2["firstMinter"] = "0x" + ft2["topics"][2][26:]
else:
    r2["firstMintBlock"] = None
out["sourcify_trackc_s2"] = r2
print("C2", json.dumps(r2), flush=True)

json.dump(out, open(f"{BASE}/run-{TS}-sourcify-verify.json", "w"), indent=1)
print("WROTE run-%s-sourcify-verify.json" % TS, flush=True)
