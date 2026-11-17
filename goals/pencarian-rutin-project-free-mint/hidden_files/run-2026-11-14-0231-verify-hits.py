#!/usr/bin/env python3
"""Focused on-chain verify for free-mint-search run 2026-11-14 02:31 WIB.
4 agent-shaped Sourcify hits (ABI-verified this run, first-seen in feed 19:20-19:49 UTC).
Read-only; writes run-2026-11-14-0231-verify-hits.json. No preview/mint.
Egress to bsc-dataseed is SLOW (~15s/call) but alive - long timeouts used."""
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
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42: d += enc_addr(a)
        else: d += enc_u(int(a))
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
            return out, ep
        except Exception as e:
            continue
    return None, None
def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=45)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16), ep
        except Exception: continue
    return None, None
U = [USER]
ITEMS = {
 "AngelEye-77D9": ("0x77D98247BA3dDAfa9ffBceA1F13d3e4cFe3f2d4C", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("freeRemaining","freeRemaining()",[]),
    ("FREE_POOL","FREE_POOL()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintStart","mintStart()",[]),("mintEnd","mintEnd()",[]),("saleActive","saleActive()",[]),
    ("name","name()",[]),("symbol","symbol()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "AbsurdAgentNFT-72C1": ("0x72c14121681F1133545947B0735563835CC07B67", [
    ("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintStartTime","mintStartTime()",[]),("mintOpen","mintOpen()",[]),
    ("name","name()",[]),("symbol","symbol()",[]),("balanceOf_user","balanceOf(address)",U),
    ("freeClaimed_user","freeClaimed(address)",U),("isEligible_user","isEligible(address)",U)]),
 "NovaRemnants-38C1": ("0x38C1695eb72B7522c8d6452a4CE27122532A0d69", [
    ("genesisOpen","genesisOpen()",[]),("genesisStart","genesisStart()",[]),
    ("totalRemnants","totalRemnants()",[]),("currentCycle","currentCycle()",[]),
    ("firstBoundary","firstBoundary()",[]),
    ("name","name()",[]),("symbol","symbol()",[]),("balanceOf_user","balanceOf(address)",U),
    ("priceFor_user","priceFor(address)",U)]),
 "AngelEye-07bD": ("0x07bD6DbbEf508ad83BA2C557ED979732488894A1", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("freeRemaining","freeRemaining()",[]),
    ("FREE_POOL","FREE_POOL()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintStart","mintStart()",[]),("mintEnd","mintEnd()",[]),("saleActive","saleActive()",[]),
    ("name","name()",[]),("symbol","symbol()",[]),("balanceOf_user","balanceOf(address)",U)]),
}
blk, blk_ep = block_number()
res = {"run": "2026-11-14-0231", "block": blk, "block_ep": blk_ep, "elapsed_s": None, "items": {}}
for name, (addr, views) in ITEMS.items():
    out, ep = raw_batch(addr, views)
    res["items"][name] = {"address": addr, "ep": ep, "views": out}
    print(name, "via", ep, "->", json.dumps(out))
res["elapsed_s"] = round(time.time() - t0, 1)
json.dump(res, open(BASE + "run-2026-11-14-0231-verify-hits.json", "w"), indent=1)
print("BLOCK", blk, "via", blk_ep, "elapsed", res["elapsed_s"])
