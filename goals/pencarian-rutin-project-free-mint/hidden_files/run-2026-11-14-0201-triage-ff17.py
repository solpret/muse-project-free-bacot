#!/usr/bin/env python3
"""Targeted triage for feed contracts 0xfF17 (mintFree + holdsAgentId + AGENT_ID)
and 0x027F (gate view) for free-mint-search run 2026-11-14 02:01 WIB.
Reads AGENT_ID()/genesis state/holdsAgentId(user) on 0xfF17 and gate() on 0x027F.
Read-only; no preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        else:
            d += enc_u(int(a))
    return d
def raw_batch(addr, views):
    calls, keys = [], []
    for i, (key, sig, args) in enumerate(views):
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            out = {}
            for it, key in zip(res, keys):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    out[key] = None
                else:
                    r = it["result"]
                    if len(r) >= 66 and all(c in "0123456789abcdef" for c in r[2:66]):
                        v = to_int(r[:66])
                        out[key] = ("0x" + r[26:66]) if len(r) == 66 and v is not None and v > 2**64 else v
                    else:
                        out[key] = r
            return out
        except Exception:
            continue
    return None
def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
            if isinstance(r, dict) and r.get("result"):
                return int(r["result"], 16)
        except Exception:
            continue
    return None

FF17 = "0xfF172b79d040faefA1Bf34B47151edc87130246E"
RUNE = "0x027FFe566B1F3f9Bb3Ddbd835DD01d0b62Af9DB7"
U = [USER]
res = {}
res["fF17"] = raw_batch(FF17, [
    ("AGENT_ID", "AGENT_ID()", []),
    ("genesisOpen", "genesisOpen()", []),
    ("genesisStart", "genesisStart()", []),
    ("commitStart", "commitStart()", []),
    ("commitEnd", "commitEnd()", []),
    ("totalSnippets", "totalSnippets()", []),
    ("isSealed", "isSealed()", []),
    ("isZeroDay", "isZeroDay()", []),
    ("holdsAgentId_user", "holdsAgentId(address)", U),
    ("COMPILED_THRESHOLD", "COMPILED_THRESHOLD()", []),
    ("SHIPPED_THRESHOLD", "SHIPPED_THRESHOLD()", []),
    ("TIER1_PRICE", "TIER1_PRICE()", []),
    ("TIER2_PRICE", "TIER2_PRICE()", []),
    ("WINDOW", "WINDOW()", []),
    ("currentCommit", "currentCommit()", []),
    ("name", "name()", []),
    ("symbol", "symbol()", []),
])
res["rune027F"] = raw_batch(RUNE, [
    ("gate", "gate()", []),
    ("factory", "factory()", []),
    ("market", "market()", []),
    ("startsAt", "startsAt()", []),
    ("endsAt", "endsAt()", []),
    ("opened", "opened()", []),
    ("totalIssued", "totalIssued()", []),
    ("maxLots", "maxLots()", []),
    ("name", "name()", []),
    ("symbol", "symbol()", []),
])
res["block"] = block_number()
res["elapsed_s"] = round(time.time() - t0, 1)
print(json.dumps(res, indent=1, default=str))
json.dump(res, open(BASE + "run-2026-11-14-0201-triage-ff17.json", "w"), indent=1, default=str)
print("DONE")
