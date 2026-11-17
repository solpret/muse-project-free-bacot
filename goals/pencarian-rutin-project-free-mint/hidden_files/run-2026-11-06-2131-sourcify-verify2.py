#!/usr/bin/env python3
"""Run 2131: focused verify of 2 Sourcify shape-passes (narrow ranges, short timeouts).
Read-only. Writes run-2026-11-06-2131-sourcify-verify2.json."""
import json, sys, time, urllib.request, datetime
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

def raw_hex(to, data, timeout=6):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            return v if v and v != "0x" else None
        except Exception:
            continue
    return None

def dec_str(hexv):
    if not hexv: return None
    try:
        b = bytes.fromhex(hexv[2:])
        if len(b) < 96: return None
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96+ln].decode("utf-8", "replace")
    except Exception:
        return None

def get_logs(addr, frm, to, topics, timeout=12):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                               "params": [{"fromBlock": hex(frm), "toBlock": hex(to),
                                           "address": addr, "topics": topics}]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "result" in out: return out["result"]
        except Exception:
            continue
    return None

def block_ts(n, timeout=6):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                               "params": [hex(n), False]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            return int(out["result"]["timestamp"], 16)
        except Exception:
            continue
    return None

def wib(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S") if ts else None

def head():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None

T0 = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
H = head()
out = {"head": H, "read_wib": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")}
print("head", H, flush=True)

# --- C1 ---
a1 = "0x7fe03C055588bd5018825175D791103c5CBEd8be"
r1 = {"address": a1}
r1["name_raw"] = raw_hex(a1, sel("name()"))
r1["name"] = dec_str(r1["name_raw"])
r1["symbol"] = dec_str(raw_hex(a1, sel("symbol()")))
r1["totalSupply"] = call(a1, "totalSupply()")
r1["claimOpen"] = call(a1, "claimOpen()")
r1["claimTimeLeft"] = call(a1, "claimTimeLeft()")
r1["CLAIM_START"] = call(a1, "CLAIM_START()")
r1["CLAIM_START_wib"] = wib(r1["CLAIM_START"])
r1["CLAIM_END_wib"] = wib(call(a1, "CLAIM_END()"))
r1["MIN_BALANCE"] = call(a1, "MIN_BALANCE()")
r1["hasSBT_user"] = call(a1, "hasSBT(address)", enc(USER))
r1["balanceOf_user"] = call(a1, "balanceOf(address)", enc(USER))
r1["tokenURI_1"] = dec_str(raw_hex(a1, sel("tokenURI(uint256)") + format(1, "064x")))
r1["ownerOf_1"] = call(a1, "ownerOf(uint256)", format(1, "064x"))
# first Transfer from zero, narrow range: claim start block ~132024400; scan 132023500..head in 1000-block chunks
logs = []
frm = 132023500
while frm <= H:
    to = min(H, frm + 999)
    res = get_logs(a1, frm, to, [T0, ZERO])
    if res: logs.extend(res)
    frm = to + 1
r1["transfer_logs_found"] = len(logs)
if logs:
    first = min(logs, key=lambda l: int(l["blockNumber"], 16))
    bn = int(first["blockNumber"], 16)
    ts = block_ts(bn)
    r1["firstMintBlock"] = bn
    r1["firstMintWib"] = wib(ts)
    r1["firstMinter"] = "0x" + first["topics"][2][26:]
    r1["distinctMinters"] = len({"0x" + l["topics"][2][26:].lower() for l in logs})
    r1["mintCountWindow"] = len(logs)
out["sourcify_nft_claim"] = r1
print("C1", json.dumps(r1), flush=True)

# --- C2 ---
a2 = "0x9e2738B3DD3773c6c71cA24Fbc92660B501C0B6b"
r2 = {"address": a2}
r2["name"] = dec_str(raw_hex(a2, sel("name()")))
r2["symbol"] = dec_str(raw_hex(a2, sel("symbol()")))
r2["decimals"] = call(a2, "decimals()")
r2["totalSupply"] = call(a2, "totalSupply()")
r2["SUPPLY"] = call(a2, "SUPPLY()")
r2["SALE_TOKENS"] = call(a2, "SALE_TOKENS()")
r2["FREE_TOKENS"] = call(a2, "FREE_TOKENS()")
r2["FREE_PER_WALLET"] = call(a2, "FREE_PER_WALLET()")
r2["freeClaimed"] = call(a2, "freeClaimed()")
r2["freeTaken_user"] = call(a2, "freeTaken(address)", enc(USER))
r2["claimed_user"] = call(a2, "claimed(address)", enc(USER))
ag2 = call(a2, "AGENT_ID()")
r2["AGENT_ID_raw"] = ag2
r2["AGENT_ID_is_registry"] = (ag2 == int(REGISTRY, 16)) if isinstance(ag2, int) else None
r2["startTime"] = call(a2, "startTime()")
r2["startTime_wib"] = wib(r2["startTime"])
r2["LIST_DEADLINE_wib"] = wib(call(a2, "LIST_DEADLINE()"))
r2["listed"] = call(a2, "listed()")
r2["pair"] = raw_hex(a2, sel("pair()"))
r2["soldTokens"] = call(a2, "soldTokens()")
r2["raised"] = call(a2, "raised()")
r2["HARDCAP"] = call(a2, "HARDCAP()")
r2["RATE"] = call(a2, "RATE()")
r2["balanceOf_user"] = call(a2, "balanceOf(address)", enc(USER))
# first FreeClaimed event: topic0 keccak("FreeClaimed(address,uint256)") and (address)
for sig in ["FreeClaimed(address,uint256)", "FreeClaimed(address)"]:
    t0 = "0x" + keccak.new(digest_bits=256, data=sig.encode()).hexdigest()
    logs2 = []
    frm = max(0, H - 60000)
    while frm <= H:
        to = min(H, frm + 1999)
        res = get_logs(a2, frm, to, [t0])
        if res: logs2.extend(res)
        frm = to + 1
    if logs2:
        first = min(logs2, key=lambda l: int(l["blockNumber"], 16))
        bn = int(first["blockNumber"], 16)
        r2["firstFreeClaim_sig"] = sig
        r2["firstFreeClaimBlock"] = bn
        r2["firstFreeClaimWib"] = wib(block_ts(bn))
        r2["freeClaimCountWindow"] = len(logs2)
        break
else:
    r2["firstFreeClaimBlock"] = None
    r2["firstFreeClaim_sig"] = None
out["sourcify_trackc_s2"] = r2
print("C2", json.dumps(r2), flush=True)

json.dump(out, open(f"{BASE}/run-{TS}-sourcify-verify2.json", "w"), indent=1)
print("WROTE run-%s-sourcify-verify2.json" % TS, flush=True)
