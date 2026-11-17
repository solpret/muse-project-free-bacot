#!/usr/bin/env python3
"""Run 2131: C2 reads-only + C1 contractURI/tokenURI external_url + first-mint block ts.
Read-only. Writes run-2026-11-06-2131-sourcify-verify3.json."""
import json, sys, datetime, urllib.request
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

def dec_abi_str(hexv):
    """Correct ABI string decode: word0 offset, word1 length, word2+ data."""
    if not hexv: return None
    try:
        b = bytes.fromhex(hexv[2:])
        if len(b) < 64: return None
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode("utf-8", "replace")
    except Exception:
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

out = {}
# C1 first-seen block timestamp
ts1 = block_ts(132024991)
out["bnbfly_firstSeenBlock"] = 132024991
out["bnbfly_firstSeenWib"] = wib(ts1)

# C1: name/symbol correct, contractURI, tokenURI full
a1 = "0x7fe03C055588bd5018825175D791103c5CBEd8be"
r1 = {"address": a1}
r1["name"] = dec_abi_str(raw_hex(a1, sel("name()")))
r1["symbol"] = dec_abi_str(raw_hex(a1, sel("symbol()")))
r1["contractURI"] = dec_abi_str(raw_hex(a1, sel("contractURI()")))
r1["tokenURI_1"] = dec_abi_str(raw_hex(a1, sel("tokenURI(uint256)") + format(1, "064x")))
r1["totalSupply"] = call(a1, "totalSupply()")
r1["claimOpen"] = call(a1, "claimOpen()")
r1["hasSBT_user"] = call(a1, "hasSBT(address)", enc(USER))
out["bnbfly"] = r1
print("C1", json.dumps(r1)[:2000], flush=True)

# C2 reads only
a2 = "0x9e2738B3DD3773c6c71cA24Fbc92660B501C0B6b"
r2 = {"address": a2}
r2["name"] = dec_abi_str(raw_hex(a2, sel("name()")))
r2["symbol"] = dec_abi_str(raw_hex(a2, sel("symbol()")))
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
out["trackc_s2"] = r2
print("C2", json.dumps(r2), flush=True)

json.dump(out, open(f"{BASE}/run-{TS}-sourcify-verify3.json", "w"), indent=1)
print("WROTE run-%s-sourcify-verify3.json" % TS, flush=True)
