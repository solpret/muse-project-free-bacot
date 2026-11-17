#!/usr/bin/env python3
"""Probe run 2026-11-11 15:31 WIB: Mihao2 0x34eA (hot-leg 1514 S1 finding,
second Mihao sale, LumenMintV3) — fresh on-chain verification for main
snapshot track_c add as watchlist-only pre-launch. Read-only; no preview,
no mint. Also checks same-owner-discards."""
import json, subprocess
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x34eA49e9BC199418f121366BdBEa8fDbab10c26b"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v not in (None, "0x") else None
    except Exception: return None

def batch_call(to, views):
    calls = []
    for i, sig in enumerate(views):
        data = sel(sig) + (enc(USER) if "(address)" in sig else "")
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": to, "data": data}, "latest"]})
    for ep in EPS:
        try:
            r = subprocess.run(["curl", "-sL", "--max-time", "25", "-X", "POST", ep,
                                "-H", "Content-Type: application/json", "-d", json.dumps(calls)],
                               capture_output=True, text=True, timeout=30)
            res = json.loads(r.stdout)
            if isinstance(res, list) and len(res) == len(calls):
                return res
        except Exception:
            continue
    return None

def dec_str(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        if len(b) < 96: return None
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96+ln].decode(errors="replace")
    except Exception:
        return None

VIEWS = ["FREE_SHARES()", "FREE_MAX()", "freeMinted()", "freeClaimedCount()",
         "totalMinted()", "freePhaseActive()", "opened()", "paused()",
         "saleEnd()", "MAX_SHARES()", "identityOf(address)", "balanceOf(address)",
         "token()", "agentRegistry()", "name()", "symbol()"]
raw = batch_call(ADDR, VIEWS)
vals = {}
if raw is not None:
    for sig, item in zip(VIEWS, raw):
        key = sig.split("(")[0] + ("_user" if "(address)" in sig else "")
        res = item.get("result") if isinstance(item, dict) else None
        if res is None or res == "0x" or (isinstance(item, dict) and "error" in item):
            vals[key] = None
        else:
            vals[key] = res
    for k in ("name", "symbol"):
        if vals.get(k): vals[k + "_decoded"] = dec_str(vals[k])
    for k, v in list(vals.items()):
        if v and k not in ("token", "agentRegistry", "name", "symbol") and not k.endswith("_decoded"):
            iv = to_int(v)
            if iv is not None: vals[k + "_int"] = iv
    for k in ("token", "agentRegistry"):
        if vals.get(k): vals[k + "_addr"] = "0x" + vals[k][-40:]
# quoteFor(1, true): (uint256,bool) -> 64-byte uint + 32-byte bool
def eth_call(to, data):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
               "params": [{"to": to, "data": data}, "latest"]}
    for ep in EPS:
        try:
            r = subprocess.run(["curl", "-sL", "--max-time", "25", "-X", "POST", ep,
                                "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                               capture_output=True, text=True, timeout=30)
            res = json.loads(r.stdout)
            if isinstance(res, dict) and "result" in res:
                return res["result"]
        except Exception:
            continue
    return None
qdata = sel("quoteFor(uint256,bool)") + format(1, "064x") + format(1, "064x")
qres = eth_call(ADDR, qdata)
vals["quoteFor_1_free_raw"] = qres
if qres and len(qres) >= 130:
    vals["quoteFor_1_free_cost_int"] = int(qres[2:66], 16)
    vals["quoteFor_1_free_tokens_int"] = int(qres[66:130], 16)

disc = json.load(open(BASE + "same-owner-discards.json"))
disc_addrs = set()
if isinstance(disc, list):
    disc_addrs = {str(x).lower() for x in disc if isinstance(x, str)}
elif isinstance(disc, dict):
    for v in disc.values():
        if isinstance(v, dict):
            for kk in ("address", "owner", "deployer"):
                if v.get(kk): disc_addrs.add(str(v[kk]).lower())
        elif isinstance(v, str):
            disc_addrs.add(v.lower())
out = {"address": ADDR, "started_wib": "2026-11-11 15:31 WIB", "views": vals,
       "discards": {"contract_in_discards": ADDR.lower() in disc_addrs}}
json.dump(out, open(BASE + "run-2026-11-11-1531-probe-mihao2.json", "w"), indent=1)
print(json.dumps({k: v for k, v in vals.items() if k.endswith("_int") or k.endswith("_decoded") or k.endswith("_addr") or k == "quoteFor_1_free_raw"}, indent=1))
print("DISCARDS:", out["discards"])
print("PROBE DONE")
