#!/usr/bin/env python3
"""Supplement to hot-leg run 2026-11-19 07:54 WIB.
(1) VeinCore 0x534BE3... shape-hit re-probe with exact ABI signatures.
(2) Re-read of the 3 leg-4 focus items missing from the 2339 template
    (AgentMintPass / AGATE-Pass / AgentDrop) vs their 0744 values.
Read-only; writes only its own output JSON."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
T0 = time.time()
from datetime import datetime, timezone, timedelta
NOW = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42: d += enc_addr(a)
        elif isinstance(a, str) and a.startswith("0x"): d += enc_u(int(a, 16))
        else: d += enc_u(int(a))
    return d
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def post_rpc(ep, payload, timeout=60):
    o = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(o)

def batch(addr, views):
    calls, meta = [], []
    for key, sig, args in views:
        calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        meta.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=60)
            if isinstance(res, list) and len(res) == len(calls):
                o = {}
                for it, key in zip(res, meta):
                    if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                        o[key] = None
                    else:
                        r = it["result"]
                        if key in ("token", "pair", "owner", "AGENT_ID_REGISTRY"):
                            o[key] = "0x" + r[-40:] if len(r) >= 42 else r
                        else:
                            o[key] = to_int(r[:66]) if len(r) >= 66 else r
                return o, ep
        except Exception:
            continue
    return None, None

U = [USER]
VEIN = "0x534BE3A81b70ffec244162838f7aB6c37f056676"
vein_views = [("FREE_SHARES", "FREE_SHARES()", []), ("FREE_MINT_AMOUNT", "FREE_MINT_AMOUNT()", []),
              ("MAX_MINT_SHARES", "MAX_MINT_SHARES()", []), ("SHARE_PRICE", "SHARE_PRICE()", []),
              ("freeClaimed", "freeClaimed()", []), ("freeMinted_user", "freeMinted(address)", U),
              ("saleOpen", "saleOpen()", []), ("poolsOpen", "poolsOpen()", []),
              ("saleRemaining", "saleRemaining()", []), ("saleSold", "saleSold()", []),
              ("mintedShares_user", "mintedShares(address)", U), ("totalShares", "totalShares()", []),
              ("token", "token()", []), ("pair", "pair()", []), ("owner", "owner()", []),
              ("vestingStart", "vestingStart()", []), ("AGENT_ID_REGISTRY", "AGENT_ID_REGISTRY()", []),
              ("epoch", "epoch()", [])]
vein, vein_ep = batch(VEIN, vein_views)

MISSING = {
    "AgentMintPass": ("0xfcadfb7cc85b6ea540d64e4f4b9f162e630f55c0",
        [("totalSupply", "totalSupply()", []), ("totalMinted", "totalMinted()", []),
         ("freeMinted", "freeMinted()", []), ("freeClaimed", "freeClaimed()", []),
         ("mintOpen", "mintOpen()", []), ("balanceOf_user", "balanceOf(address)", U)]),
    "AGATE-Pass": ("0x5b63bd45e61a2e6540548c3509b598b6384206c5",
        [("totalSupply", "totalSupply()", []), ("totalMinted", "totalMinted()", []),
         ("freeMinted", "freeMinted()", []), ("freeClaimed", "freeClaimed()", []),
         ("mintOpen", "mintOpen()", []), ("balanceOf_user", "balanceOf(address)", U)]),
    "AgentDrop": ("0x1dd8740ffca0be3caac3b4a3eb41fdff506e38a9",
        [("totalSupply", "totalSupply()", []), ("totalMinted", "totalMinted()", []),
         ("freeMinted", "freeMinted()", []), ("freeClaimed", "freeClaimed()", []),
         ("mintOpen", "mintOpen()", []), ("balanceOf_user", "balanceOf(address)", U)]),
}
reads = {}
for name, (addr, views) in MISSING.items():
    v, ep = batch(addr, views)
    reads[name] = {"address": addr, "views": v, "rpc_ep": ep}

blk = None
for ep in EPS:
    try:
        r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=60)
        if isinstance(r, dict) and r.get("result"):
            blk = int(r["result"], 16); break
    except Exception:
        continue

prev = json.load(open(BASE + "hot-leg-run-2026-11-19-0744-reread.json"))
changes = []
for name, item in reads.items():
    pv = (prev.get("reads", {}).get(name) or {}).get("views") or {}
    cv = item.get("views") or {}
    diff = {k: {"prev": pv.get(k), "now": cv.get(k)}
            for k in set(list(pv.keys()) + list(cv.keys())) if pv.get(k) != cv.get(k)}
    if diff:
        changes.append({"item": name, "type": "value-change", "diff": diff})

out = {"run": "free-mint-hot-leg 2026-11-19 07:54 WIB supplement",
       "started_wib": NOW, "block": blk,
       "veincore": {"address": VEIN, "views": vein, "rpc_ep": vein_ep},
       "missing_leg4": reads, "missing_leg4_changes_vs_0744": changes,
       "elapsed_s": round(time.time() - T0, 1)}
json.dump(out, open(BASE + "hot-leg-run-2026-11-19-0754-supplement.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("DONE elapsed", round(time.time() - T0, 1))
