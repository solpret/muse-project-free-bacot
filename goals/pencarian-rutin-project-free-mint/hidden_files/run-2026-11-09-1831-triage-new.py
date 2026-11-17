#!/usr/bin/env python3
"""Triage NEW discovery items run 1831 (2026-11-09). Read-only.
Targets: Shard Id NFT 0x5c46de8d0c5dfdf535558d363f492967cd5e146b,
NEURA distributor 0xf027B84D8b1Ae4025fbDa156e843b2773B953DFC,
JOLT 0x63C9d73f09bb7CCD8E363510676Bd9ecD563f8e4.
Writes run-2026-11-09-1831-triage-new.json. Never previews/mints."""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
PCS_FACTORY = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c6"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return None if v in (None, "0x") else int(v, 16)
    except Exception: return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig: data = sel(sig) + enc(USER); key = base + "_user"
        else: data = sel(sig); key = base
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
def call1(addr, sig, arg=None):
    data = sel(sig)
    if arg == "user": data += enc(USER)
    elif isinstance(arg, str) and arg.startswith("0x"): data += arg[2:].lower().rjust(64, "0")
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            if isinstance(r, dict) and "result" in r: return to_int(r["result"])
        except Exception: continue
    return None
def code(addr):
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                          "params": [addr, "latest"]}, timeout=25)
            c = r.get("result")
            if isinstance(c, str): return c
        except Exception: continue
    return None
def block_ts(num):
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                          "params": [hex(num), False]}, timeout=25)
            ts = r.get("result", {}).get("timestamp")
            if ts: return int(ts, 16)
        except Exception: continue
    return None
def blocknum():
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception: continue
    return None
def sourcify(addr):
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata",
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=25) as r: d = json.load(r)
        abi = d.get("abi") or []
        fns = [f.get("name") for f in abi if isinstance(f, dict) and f.get("type") == "function"]
        return {"match": d.get("match"), "verifiedAt": d.get("verifiedAt"), "fns": fns,
                "metadata": d.get("metadata")}
    except Exception as e:
        return {"error": str(e)[:200]}

out = {"block": blocknum(), "targets": {}}
print("BLOCK", out["block"], flush=True)

# --- Shard Id NFT ---
SHARD = "0x5c46de8d0c5dfdf535558d363f492967cd5e146b"
VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "mintStart()", "mintEnd()",
         "balanceOf(address)", "freeClaimed(address)", "owner()", "name()", "symbol()",
         "contractURI()", "tokenURI(uint256)"]
got = batch(SHARD, [v for v in VIEWS if "tokenURI" not in v])
# tokenURI(1) separately with uint arg
t1 = call1(SHARD, "tokenURI(uint256)", "0x" + format(1, "064x")) if False else None
c = code(SHARD)
sf = sourcify(SHARD)
out["targets"]["Shard Id"] = {"address": SHARD, "views": got, "code_len": (len(c) - 2) // 2 if c else None,
    "registry_bytes": (REG in (c or "").lower()) if c else None, "sourcify": sf,
    "first_mint_block_claimed": 132576049,
    "first_mint_block_ts": block_ts(132576049)}
print("Shard Id", got, "reg=", out["targets"]["Shard Id"]["registry_bytes"],
      "sf=", sf.get("match") or sf.get("error"), "firstMintTs=", out["targets"]["Shard Id"]["first_mint_block_ts"], flush=True)

# --- NEURA distributor ---
NEURA_DIST = "0xf027B84D8b1Ae4025fbDa156e843b2773B953DFC"
sf_n = sourcify(NEURA_DIST)
c_n = code(NEURA_DIST)
print("NEURA sourcify:", sf_n.get("match") or sf_n.get("error"), "fns:", sf_n.get("fns"), flush=True)
# generic views that may exist on a distributor
nv = batch(NEURA_DIST, ["owner()", "token()", "launched()", "totalClaimed()",
                        "totalShares()", "claimed(address)", "claimable(address)",
                        "hasClaimed(address)", "claimFree()"])
out["targets"]["NEURA-distributor"] = {"address": NEURA_DIST, "views": nv,
    "code_len": (len(c_n) - 2) // 2 if c_n else None,
    "registry_bytes": (REG in (c_n or "").lower()) if c_n else None, "sourcify": sf_n}
print("NEURA views:", nv, flush=True)
# NEU token + pair check via token() if readable
neu_token = None
if nv and nv.get("token"):
    neu_token = "0x" + format(nv["token"], "040x")
    print("NEU token:", neu_token, flush=True)
    # PCS factory getPair(token, WBNB)
    data = sel("getPair(address,address)") + WBNB[2:].lower().rjust(64, "0") + neu_token[2:].lower().rjust(64, "0")
    pair = None
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": PCS_FACTORY, "data": data}, "latest"]}, timeout=25)
            if isinstance(r, dict) and "result" in r: pair = to_int(r["result"]); break
        except Exception: continue
    out["targets"]["NEURA-distributor"]["neu_token"] = neu_token
    out["targets"]["NEURA-distributor"]["pair_wbnb"] = ("0x" + format(pair, "040x")) if pair else None
    print("NEU/WBNB pair:", out["targets"]["NEURA-distributor"]["pair_wbnb"], flush=True)

# --- JOLT ---
JOLT = "0x63C9d73f09bb7CCD8E363510676Bd9ecD563f8e4"
sf_j = sourcify(JOLT)
c_j = code(JOLT)
jv = batch(JOLT, ["launched()", "totalClaims()", "totalDistributed()", "owner()",
                  "token()", "claimed(address)", "claimable(address)", "hasClaimed(address)",
                  "dailyCap()", "seasonEnd()", "launchTime()", "totalSupply()", "name()", "symbol()"])
out["targets"]["JOLT"] = {"address": JOLT, "views": jv,
    "code_len": (len(c_j) - 2) // 2 if c_j else None,
    "registry_bytes": (REG in (c_j or "").lower()) if c_j else None, "sourcify": sf_j}
print("JOLT views:", jv, "reg=", out["targets"]["JOLT"]["registry_bytes"],
      "sf=", sf_j.get("match") or sf_j.get("error"), "fns:", sf_j.get("fns"), flush=True)

# --- same-owner discards check ---
try:
    disc = json.load(open(f"{BASE}/same-owner-discards.json"))
    addrs = set()
    if isinstance(disc, dict):
        for v in disc.values():
            if isinstance(v, dict):
                for f in ("address", "contract"):
                    if v.get(f): addrs.add(str(v[f]).lower())
            elif isinstance(v, str): addrs.add(v.lower())
    elif isinstance(disc, list):
        for v in disc:
            if isinstance(v, dict):
                for f in ("address", "contract"):
                    if v.get(f): addrs.add(str(v[f]).lower())
            elif isinstance(v, str): addrs.add(v.lower())
    out["same_owner_discards_check"] = {a: (a.lower() in addrs) for a in
        [SHARD, NEURA_DIST, JOLT]}
    print("DISCARDS:", out["same_owner_discards_check"], flush=True)
except Exception as e:
    out["same_owner_discards_check"] = {"error": str(e)[:150]}
    print("DISCARDS CHECK FAILED:", e, flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-09-1831-triage-new.json", "w"), indent=1)
print("TRIAGE NEW DONE")
