#!/usr/bin/env python3
"""Redo leg 4 + bridge for hot-leg run 2026-11-16 16:34 WIB.
Fixes vs first attempt: (1) explicit per-name merge (no nested-comprehension
key collision); (2) validate len(resp)==len(calls) and every entry has 'result';
(3) retry failed chunk once after 8s across endpoints; (4) bridge reads
bridge['contracts'] (top level is seeded/writer/contracts).
Overwrites run-2026-11-16-1634-reread.json and patches the bridge+reread
sections of run-hot-leg-2026-11-16-1634.json. Read-only otherwise."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        elif isinstance(a, str) and a.startswith("0x"):
            d += enc_u(int(a, 16))
        else:
            d += enc_u(int(a))
    return d
def post_rpc(ep, payload, timeout=120):
    outp = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(outp)

U = [USER]
ITEMS = {
 "AGCLUB": ("0x67270bb351515abf3089ca5420456897363f5e75", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("FREE_CAP","FREE_CAP()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("totalMinted","totalMinted()",[]),
    ("balanceOf_user","balanceOf(address)",U)]),
 "MORFO": ("0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186", [
    ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[])]),
 "BinanceAI-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched","launched()",[]),("failed","failed()",[]),
    ("isRefundPhase","isRefundPhase()",[]),("totalShares","totalShares()",[]),
    ("tokenClaimed_user","tokenClaimed(address)",U)]),
 "ORBIT": ("0x7d5F7f323db3050AF92E9aa1584E883B3b24d680", [
    ("freeClaimed","freeClaimed()",[]),("FREE_MAX","FREE_MAX()",[]),
    ("claimOpen","claimOpen()",[]),("hasFreeClaimed_user","hasFreeClaimed(address)",U),
    ("totalSupply","totalSupply()",[])]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", [
    ("freeSharesLeft","freeSharesLeft()",[]),("openedAt","openedAt()",[]),
    ("freeClaimed","freeClaimed()",[]),("freeBooked_user","freeBooked(address)",U)]),
 "CosmicSentinel": ("0x88731d1eb41c36f3d705fdb58b658244c06afc36", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
}

def read_one(name, addr, views):
    calls, meta = [], []
    for key, sig, args in views:
        calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        meta.append(key)
    for attempt in range(2):
        for ep in EPS:
            try:
                resp = post_rpc(ep, calls)
                if (isinstance(resp, list) and len(resp) == len(calls)
                        and all(isinstance(r, dict) and "result" in r for r in resp)):
                    merged = {}
                    for key, r in zip(meta, resp):
                        merged[key] = to_int(r.get("result"))
                    return merged, None
                last = f"bad response {ep}: {str(resp)[:100]}"
            except Exception as ex:
                last = str(ex)[:120]
        time.sleep(8)
    return None, last

reread = {"started_wib": "2026-11-16T16:34+07:00 (redo)", "reads": {}, "reads_ok": 0,
          "reads_total": len(ITEMS), "block": None, "redo": True}
for name, (addr, views) in ITEMS.items():
    merged, err = read_one(name, addr, views)
    if merged is not None:
        reread["reads"][name] = {"address": addr, "views": merged}
        reread["reads_ok"] += 1
    else:
        reread["reads"][name] = {"address": addr, "views": {}, "error": err}
try:
    b = post_rpc(EPS[0], [{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}], timeout=30)
    reread["block"] = int(b[0]["result"], 16) if isinstance(b, list) else None
except Exception:
    reread["block"] = None
reread["elapsed_s"] = round(time.time() - t0, 1)
json.dump(reread, open(BASE + "run-2026-11-16-1634-reread.json", "w"), indent=1)

# bridge (read-only), fixed nesting
snap = json.load(open(BASE + "onchain-snapshot.json"))
snap_addrs = set()
for sec in ("contracts", "track_c", "pending_claims"):
    for entry in snap.get(sec, {}).values():
        if isinstance(entry, dict):
            for k in ("address", "sale", "token", "mint"):
                v = entry.get(k)
                if isinstance(v, str) and v.startswith("0x"):
                    snap_addrs.add(v.lower())
raw_bridge = json.load(open(BASE + "scan-bridge.json"))
contracts = raw_bridge.get("contracts", raw_bridge) if isinstance(raw_bridge, dict) else {}
outside = [a for a in contracts if isinstance(a, str) and a.startswith("0x") and a.lower() not in snap_addrs]
discarded = [a for a, v in contracts.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
bridge = {"n": len(contracts), "same_owner_discarded": len(discarded), "outside_snapshot": outside}

summary = json.load(open(BASE + "run-hot-leg-2026-11-16-1634.json"))
summary["reread"] = {"block": reread["block"], "reads_ok": reread["reads_ok"],
                     "reads_total": reread["reads_total"],
                     "summary": {n: v["views"] for n, v in reread["reads"].items()},
                     "errors": {n: v.get("error") for n, v in reread["reads"].items() if v.get("error")}}
summary["bridge"] = bridge
summary["elapsed_s"] = round(summary.get("elapsed_s", 0) + reread["elapsed_s"], 1)
json.dump(summary, open(BASE + "run-hot-leg-2026-11-16-1634.json", "w"), indent=1)
print(json.dumps({"reread": summary["reread"], "bridge": bridge, "elapsed_s": reread["elapsed_s"]}, indent=1))
