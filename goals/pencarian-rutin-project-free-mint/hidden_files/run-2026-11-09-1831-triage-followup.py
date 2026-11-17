#!/usr/bin/env python3
"""Follow-up triage run 1831 — correct view names for NEURA/JOLT/Shard Id.
Read-only. Writes run-2026-11-09-1831-triage-followup.json."""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return None if v in (None, "0x") else int(v, 16)
    except Exception: return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def batch(addr, views):
    # views: (key, sig, arg) arg None|'user'|('uint',n)|('addr',hex)
    calls, keys = [], []
    for i, (key, sig, arg) in enumerate(views):
        data = sel(sig)
        if arg == "user": data += enc_addr(USER)
        elif isinstance(arg, tuple) and arg[0] == "uint": data += enc_u(arg[1])
        elif isinstance(arg, tuple) and arg[0] == "addr": data += arg[1][2:].lower().rjust(64, "0")
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls): continue
            outd = {}
            for item, key in zip(res, keys):
                outd[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return outd
        except Exception: continue
    return None
def call_raw(addr, data):
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            if isinstance(r, dict) and "result" in r: return r["result"]
        except Exception: continue
    return None
def decode_str(hexdata):
    # ABI-encoded string return
    try:
        b = bytes.fromhex(hexdata[2:])
        if len(b) < 96: return None
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off + 32], "big")
        return b[off + 32:off + 32 + ln].decode("utf-8", "replace")
    except Exception as e:
        return f"<decode err {e}>"
def abi_sigs(addr):
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=25) as r: d = json.load(r)
        abi = d.get("abi") or []
        sigs = []
        for f in abi:
            if isinstance(f, dict) and f.get("type") == "function":
                ins = ",".join(i.get("type", "") for i in f.get("inputs", []))
                sigs.append(f"{f.get('name')}({ins})")
        return sigs
    except Exception as e:
        return [f"<err {e}>"]
def blocknum():
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception: continue
    return None

out = {"block": blocknum(), "items": {}}
print("BLOCK", out["block"], flush=True)

SHARD = "0x5c46de8d0c5dfdf535558d363f492967cd5e146b"
print("Shard ABI sigs (mint/quote/registry/agentIdOf/mintedBy):", flush=True)
for s in abi_sigs(SHARD):
    if any(k in s for k in ("mint", "quote", "registry", "agentIdOf", "PRICE", "MAX_PER")):
        print("  ", s, flush=True)
sgot = batch(SHARD, [
    ("PRICE", "PRICE()", None),
    ("registry", "registry()", None),
    ("MAX_PER_WALLET", "MAX_PER_WALLET()", None),
    ("mintedBy_user", "mintedBy(address)", "user"),
    ("agentIdOf_user", "agentIdOf(address)", "user"),
    ("quote_user_1", "quote(address,uint256)", None),  # placeholder, replaced below
])
# quote(address,uint256) needs two args; do it raw
qdata = sel("quote(address,uint256)") + enc_addr(USER) + enc_u(1)
qraw = call_raw(SHARD, qdata)
sgot["quote_user_1_raw"] = qraw
sgot["quote_user_1_first_word"] = to_int(qraw) if qraw else None
# tokenURI(1) as string
tdata = sel("tokenURI(uint256)") + enc_u(1)
traw = call_raw(SHARD, tdata)
sgot["tokenURI_1"] = decode_str(traw) if traw else None
# contractURI as string
cdata = sel("contractURI()")
craw = call_raw(SHARD, cdata)
sgot["contractURI_str"] = decode_str(craw) if craw else None
out["items"]["Shard Id"] = {"address": SHARD, "views": sgot}
print("Shard:", {k: (str(v)[:200]) for k, v in sgot.items()}, flush=True)

NEURA = "0xf027B84D8b1Ae4025fbDa156e843b2773B953DFC"
ngot = batch(NEURA, [
    ("claimOpen", "claimOpen()", None),
    ("saleOpen", "saleOpen()", None),
    ("freePoolRemaining", "freePoolRemaining()", None),
    ("FREE_POOL", "FREE_POOL()", None),
    ("FREE_PER_WALLET", "FREE_PER_WALLET()", None),
    ("freeClaimCount", "freeClaimCount()", None),
    ("freeClaimed_user", "freeClaimed(address)", "user"),
    ("salePoolRemaining", "salePoolRemaining()", None),
    ("totalSold", "totalSold()", None),
])
out["items"]["NEURA"] = {"address": NEURA, "views": ngot}
print("NEURA:", ngot, flush=True)

JOLT = "0x63C9d73f09bb7CCD8E363510676Bd9ecD563f8e4"
print("JOLT ABI sigs (claim/launched/pair/fee):", flush=True)
for s in abi_sigs(JOLT):
    if any(k in s for k in ("claim", "launch", "pair", "FEE", "agent", "season", "endsAt", "startTime", "MAX", "poolReserve")):
        print("  ", s, flush=True)
jgot = batch(JOLT, [
    ("seasonState", "seasonState()", None),
    ("endsAt", "endsAt()", None),
    ("startTime", "startTime()", None),
    ("claimsOf_user", "claimsOf(address)", "user"),
    ("claimsTodayOf_user", "claimsTodayOf(address)", "user"),
    ("claimDay", "claimDay()", None),
    ("claimDayCount", "claimDayCount()", None),
    ("ladderAmount", "ladderAmount()", None),
    ("pair", "pair()", None),
    ("poolReserve", "poolReserve()", None),
    ("agentRegistry", "agentRegistry()", None),
    ("MAX_CLAIMS", "MAX_CLAIMS()", None),
    ("MAX_PER_DAY", "MAX_PER_DAY()", None),
    ("CLAIM_FEE", "CLAIM_FEE()", None),
    ("opened", "opened()", None),
    ("openSeason", "openSeason()", None),
    ("hasAgentId_user", "hasAgentId(address)", "user"),
])
out["items"]["JOLT"] = {"address": JOLT, "views": jgot}
print("JOLT:", {k: (str(v)[:120]) for k, v in jgot.items()}, flush=True)
# JOLT pair token0/token1 if pair exists
if jgot.get("pair"):
    pair = "0x" + format(jgot["pair"], "040x")
    pgot = batch(pair, [("token0", "token0()", None), ("token1", "token1()", None),
                        ("reserve0", "getReserves()", None)])
    out["items"]["JOLT"]["pair_detail"] = {"address": pair, "views": pgot}
    print("JOLT pair:", pair, pgot, flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-09-1831-triage-followup.json", "w"), indent=1)
print("FOLLOWUP DONE")
