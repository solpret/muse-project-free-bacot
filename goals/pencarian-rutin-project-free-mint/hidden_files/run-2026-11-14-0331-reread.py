#!/usr/bin/env python3
"""Re-read for free-mint-search run 2026-11-14 03:31 WIB.
Active watchlist = 0201 verify set (61) + 0231 new items (AngelEye x2,
NovaRemnants, AbsurdAgentNFT) + HIVE/Bubblebruin/Zapcourier.
Multi-contract JSON-RPC batching (10 contracts/request) for slow egress.
Read-only; writes run-2026-11-14-0331-reread.json. No preview/mint."""
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
        d += enc_addr(a) if isinstance(a, str) and a.startswith("0x") and len(a) == 42 else enc_u(int(a))
    return d
def post_rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

U = [USER]
DEFAULT = [("totalSupply","totalSupply() ",[]),("totalMinted","totalMinted()",[]),
    ("freeClaimed","freeClaimed()",[]),("freeClaimed_user","freeClaimed(address)",U),
    ("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("FREE_SHARES","FREE_SHARES()",[]),("freeSharesRemaining","freeSharesRemaining()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("balanceOf_user","balanceOf(address)",U)]
# fix stray space in totalSupply sig
DEFAULT[0] = ("totalSupply","totalSupply()",[])
EXTRA = {
 "AngelEye-77D9": [("freeRemaining","freeRemaining()",[]),("FREE_POOL","FREE_POOL()",[]),
    ("saleActive","saleActive()",[]),("mintStart","mintStart()",[]),("mintEnd","mintEnd()",[])],
 "AngelEye-07bD": [("freeRemaining","freeRemaining()",[]),("FREE_POOL","FREE_POOL()",[]),
    ("saleActive","saleActive()",[]),("mintStart","mintStart()",[]),("mintEnd","mintEnd()",[])],
 "NovaRemnants": [("genesisOpen","genesisOpen()",[]),("genesisStart","genesisStart()",[]),
    ("totalRemnants","totalRemnants()",[]),("currentCycle","currentCycle()",[]),
    ("priceFor_user","priceFor(address)",U)],
 "AbsurdAgentNFT": [("mintStartTime","mintStartTime()",[]),("isEligible_user","isEligible(address)",U)],
 "BinanceAI-mint": [("launched","launched()",[]),("failed","failed()",[]),
    ("isRefundPhase","isRefundPhase()",[]),("totalShares","totalShares()",[]),
    ("tokenClaimed_user","tokenClaimed(address)",U)],
 "BinanceAI-token": [("totalSupply","totalSupply()",[]),("balanceOf_user","balanceOf(address)",U)],
}
# base set from 0201 verify reads
v201 = json.load(open(BASE + "run-2026-11-14-0201-verify.json"))
ITEMS = {}
for name, rec in v201.get("reads", {}).items():
    ITEMS[name] = rec["address"]
ADD = {
 "AngelEye-77D9": "0x77D98247BA3dDAfa9ffBceA1F13d3e4cFe3f2d4C",
 "AngelEye-07bD": "0x07bD6DbbEf508ad83BA2C557ED979732488894A1",
 "NovaRemnants": "0x38C1695eb72B7522c8d6452a4CE27122532A0d69",
 "AbsurdAgentNFT": "0x72c14121681F1133545947B0735563835CC07B67",
 "HIVE": "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77",
 "Bubblebruin": "0xc205F8c74733D914776D66cBc4Cf10BF701D96Aa",
 "Zapcourier": "0x672c1dF4F7121DaCBD3504995441C47d2fAbCdDC",
 "BinanceAI-mint": "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
 "BinanceAI-token": "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c",
}
ITEMS.update(ADD)
# BinanceAI-mint/token get only their custom views (default would be noise)
CUSTOM_ONLY = {"BinanceAI-mint", "BinanceAI-token"}

def chunked(items, n=10):
    items = list(items.items())
    for i in range(0, len(items), n):
        yield items[i:i+n]

def read_chunk(chunk):
    calls, meta = [], []
    for name, addr in chunk:
        views = list(EXTRA.get(name, []))
        if name not in CUSTOM_ONLY:
            views = DEFAULT + views
        for key, sig, args in views:
            calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                          "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
            meta.append((name, key))
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=60)
            if not isinstance(res, list) or len(res) != len(calls):
                print("  chunk ep", ep, "bad shape", type(res), flush=True); continue
            out = {}
            for it, (name, key) in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    out.setdefault(name, {})[key] = None
                else:
                    r = it["result"]
                    out.setdefault(name, {})[key] = to_int(r[:66]) if len(r) >= 66 else r
            return out, ep
        except Exception as e:
            print("  chunk ep", ep, "exc", str(e)[:80], flush=True); continue
    return None, None

def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=60)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16)
        except Exception: continue
    return None

reads, ok = {}, 0
chunks = list(chunked(ITEMS, 10))
for ci, ch in enumerate(chunks):
    r, ep = read_chunk(ch)
    names = [n for n, _ in ch]
    if r is None:
        print(f"chunk {ci+1}/{len(chunks)} FAIL {names}", flush=True)
        for n in names: reads[n] = {"address": dict(ch)[n], "views": None}
        continue
    ok += sum(1 for n in names if r.get(n) is not None)
    for n in names: reads[n] = {"address": dict(ch)[n], "views": r.get(n)}
    print(f"chunk {ci+1}/{len(chunks)} OK via {ep} ({time.time()-t0:.0f}s) {names[0]}..{names[-1]}", flush=True)
blk = block_number()
out = {"started_wib": "2026-11-14T03:31+07:00", "reads": reads, "reads_ok": ok,
       "reads_total": len(ITEMS), "block": blk, "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "run-2026-11-14-0331-reread.json", "w"), indent=1)
print("DONE reads_ok", ok, "/", len(ITEMS), "block", blk, "elapsed", round(time.time() - t0, 1))
