#!/usr/bin/env python3
"""Focused re-read for free-mint-search run 2026-11-14 03:31 WIB.
Per-contract batch pattern (proven 0231). 45s timeouts. Key items only:
0231 early leads + 0204 prior-state movers + active track-C/B.
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
def post_rpc(ep, payload, timeout=45):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a, str) and a.startswith("0x") and len(a) == 42 else enc_u(int(a))
    return d
def raw_batch(addr, views):
    calls, keys = [], []
    for i, (key, sig, args) in enumerate(views):
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=45)
            if not isinstance(res, list) or len(res) != len(calls): continue
            out = {}
            for it, key in zip(res, keys):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    out[key] = None
                else:
                    r = it["result"]
                    out[key] = to_int(r[:66]) if len(r) >= 66 else r
            return out
        except Exception:
            continue
    return None
def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=45)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16)
        except Exception: continue
    return None
U = [USER]
D = [("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
     ("freeClaimed","freeClaimed()",[]),("freeClaimed_user","freeClaimed(address)",U),
     ("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
     ("FREE_SHARES","FREE_SHARES()",[]),("freeSharesRemaining","freeSharesRemaining()",[]),
     ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
     ("balanceOf_user","balanceOf(address)",U)]
ITEMS = {
 "AngelEye-77D9": ("0x77D98247BA3dDAfa9ffBceA1F13d3e4cFe3f2d4C", D+[("freeRemaining","freeRemaining()",[]),("FREE_POOL","FREE_POOL()",[]),("saleActive","saleActive()",[]),("mintStart","mintStart()",[]),("mintEnd","mintEnd()",[])]),
 "AngelEye-07bD": ("0x07bD6DbbEf508ad83BA2C557ED979732488894A1", D+[("freeRemaining","freeRemaining()",[]),("FREE_POOL","FREE_POOL()",[]),("saleActive","saleActive()",[]),("mintStart","mintStart()",[]),("mintEnd","mintEnd()",[])]),
 "NovaRemnants": ("0x38C1695eb72B7522c8d6452a4CE27122532A0d69", D+[("genesisOpen","genesisOpen()",[]),("genesisStart","genesisStart()",[]),("totalRemnants","totalRemnants()",[]),("currentCycle","currentCycle()",[]),("priceFor_user","priceFor(address)",U)]),
 "AbsurdAgentNFT": ("0x72c14121681F1133545947B0735563835CC07B67", D+[("mintStartTime","mintStartTime()",[]),("isEligible_user","isEligible(address)",U)]),
 "HIVE": ("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77", D),
 "BinanceAI-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [("launched","launched()",[]),("failed","failed()",[]),("isRefundPhase","isRefundPhase()",[]),("totalShares","totalShares()",[]),("tokenClaimed_user","tokenClaimed(address)",U)]),
 "BinanceAI-token": ("0x209173F09aFbCA053C0de9e9763f503e9fb54a3c", [("totalSupply","totalSupply()",[]),("balanceOf_user","balanceOf(address)",U)]),
}
# pull remaining key items from 0201 verify reads (addresses only)
v201 = json.load(open(BASE + "run-2026-11-14-0201-verify.json"))
for name in ["Agentx","OBFG","Zero","OLIVER","CRACE","2e34","PX24","SKRR","OUTY","NOTV","JNTM","AgentMuse","ME30","CY24","MECHA","Mossbound","Ochre","CinderAgents","BUILD","Mihao","Kitebots","JAGENT","AgentGrove","FERO","PIXELPHARAOH","Ponke"]:
    if name in v201.get("reads", {}):
        ITEMS[name] = (v201["reads"][name]["address"], D)
ITEMS["TrashBandit"] = ("0x2d61347D9b48De99cBdF0D8D7a2DD73f5B15E90D", D)
reads, ok = {}, 0
for name, (addr, views) in ITEMS.items():
    r = raw_batch(addr, views)
    reads[name] = {"address": addr, "views": r}
    if r is not None: ok += 1
    ts = r.get("totalSupply") if r else None
    fc = r.get("freeClaimed") if r else None
    fm = r.get("freeMinted") if r else None
    print(name, "OK" if r is not None else "FAIL", "ts=", ts, "freeClaimed=", fc, "freeMinted=", fm, flush=True)
blk = block_number()
out = {"started_wib": "2026-11-14T03:31+07:00", "reads": reads, "reads_ok": ok,
       "reads_total": len(ITEMS), "block": blk, "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "run-2026-11-14-0331-reread.json", "w"), indent=1)
print("DONE reads_ok", ok, "/", len(ITEMS), "block", blk, "elapsed", round(time.time() - t0, 1))
