#!/usr/bin/env python3
"""Supplementary on-chain read for free-mint-search run 2026-11-13 21:01 WIB.
LNFT (new early-lead check), APGB (new badge check), HELIX (age-exclusion evidence).
Read-only; writes run-2026-11-13-2101-supp.json. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
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
                    out[key] = to_int(r[:66]) if len(r) >= 66 else r
            return out
        except Exception:
            continue
    return None

def get_code(addr):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [addr, "latest"]}, timeout=20)
            if isinstance(r, dict) and r.get("result"):
                return r["result"]
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
 "LNFT": ("0xb2ac84b0d2c9684436f2cf2dc7dfc8e80be78657", [
    ("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("MAX_FREE_PER_WALLET","MAX_FREE_PER_WALLET()",[]),("MAX_PER_WALLET","MAX_PER_WALLET()",[]),
    ("TOKENS_PER_FREE_MINT","TOKENS_PER_FREE_MINT()",[]),("TOKENS_PER_MINT","TOKENS_PER_MINT()",[]),
    ("TOKEN_PRICE","TOKEN_PRICE()",[]),("freeMintedPerWallet_user","freeMintedPerWallet(address)",U),
    ("mintedPerWallet_user","mintedPerWallet(address)",U),("balanceOf_user","balanceOf(address)",U),
    ("pixelReserve","pixelReserve()",[]),("AGENT_ID","AGENT_ID()",[])]),
 "APGB": ("0x14E429947AFc932802d1fb404fb81fdC01E92A6E", [
    ("totalSupply","totalSupply()",[]),("balanceOf_user","balanceOf(address)",U),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[])]),
 "HELIX": ("0x5e0Ca9E1eCB5A6205E0B0d7a1FbE16983d2E8665", [
    ("totalSupply","totalSupply()",[]),("freeUsed_user","freeUsed(address)",U),
    ("hasAgentId_user","hasAgentId(address)",U),("mintActive","mintActive()",[]),
    ("balanceOf_user","balanceOf(address)",U)]),
}
reads, ok = {}, 0
for name, (addr, views) in ITEMS.items():
    r = raw_batch(addr, views)
    reads[name] = {"address": addr, "views": r}
    if r is not None:
        ok += 1
    print(name, "OK" if r is not None else "FAIL", json.dumps(r)[:300], flush=True)

codes = {}
for name in ("LNFT", "APGB", "HELIX"):
    addr = ITEMS[name][0]
    code = get_code(addr)
    codes[name] = {"has_code": bool(code and code != "0x"),
                   "registry_bytes_in_code": (REG in code.lower()) if code else None,
                   "code_len": len(code) if code else 0}
    print(name, "code:", codes[name], flush=True)

blk = block_number()
out = {"started_wib": "2026-11-13T21:01+07:00", "reads": reads, "reads_ok": ok,
       "reads_total": len(ITEMS), "codes": codes, "block": blk,
       "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "run-2026-11-13-2101-supp.json", "w"), indent=1)
print("DONE reads_ok", ok, "/", len(ITEMS), "block", blk, "elapsed", round(time.time() - t0, 1))
