#!/usr/bin/env python3
"""Verify for free-mint-search run 2026-11-14 01:01 WIB (retry 6 FAIL).
Fresh re-read of the active watchlist (same set as run 20:31 + BUILD, Moon, Zora, D8DA, Cinder Agents, PIXELPHARAOH, Ponke, Early5877; minus Agentx (age-excluded) and GoldVein (sold out)).
Read-only; writes run-2026-11-14-0101-retry.json. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
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
    """views: list of (key, sig, args). Returns dict key->int|raw|None."""
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
                    out[key] = to_int(r[:66]) if len(r) >= 66 else r
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

U = [USER]
ITEMS = {
 "OBFG": ("0x5314071bba19943f58347ba5dec423e5032a6818", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("saleStart","saleStart()",[]),("saleOpen","saleOpen()",[]),
    ("freeAvailable_user","freeAvailable(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "OUTY": ("0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412", [
    ("minted","minted()",[]),("freeSold","freeSold()",[]),("paidSold","paidSold()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("PAID_CAP","PAID_CAP()",[]),
    ("START","START()",[]),("FREE_END","FREE_END()",[]),("FREE_FEE","FREE_FEE()",[]),
    ("PRICE","PRICE()",[]),("phase","phase()",[]),("freeOpen","freeOpen()",[]),
    ("paidOpen","paidOpen()",[]),("freeQuotaOf_user","freeQuotaOf(address)",U),
    ("quotaOf_user","quotaOf(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "PX24": ("0xe712510fcb27935e657e41ebb97982d6b123136c", [
    ("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U),
    ("costOf_user_1","costOf(address,uint256)",[USER,1])]),
 "CY24": ("0x731d879ee2cd4bbf32efef9178d51d5c1441d052", [
    ("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U),
    ("costOf_user_1","costOf(address,uint256)",[USER,1])]),
 "MECHA": ("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", [
    ("totalMinted","totalMinted()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[])]),
 "MossSignal": ("0xb2e5d82900b854d3cb8c6bb917426abadb687f68", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("freeAvailable_user","freeAvailable(address)",U),("balanceOf_user","balanceOf(address)",U)]),
}

reads, ok = {}, 0
for name, (addr, views) in ITEMS.items():
    r = raw_batch(addr, views)
    reads[name] = {"address": addr, "views": r, "summary": r}
    if r is not None:
        ok += 1
    print(name, "OK" if r is not None else "FAIL", json.dumps(r)[:220], flush=True)

blk = block_number()
out = {"started_wib": "2026-11-14T00:01+07:00", "reads": reads, "reads_ok": ok,
       "reads_total": len(ITEMS), "block": blk, "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "run-2026-11-14-0101-retry.json", "w"), indent=1)
print("DONE reads_ok", ok, "/", len(ITEMS), "block", blk, "elapsed", round(time.time() - t0, 1))
