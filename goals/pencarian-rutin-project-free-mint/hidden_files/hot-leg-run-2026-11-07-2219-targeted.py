#!/usr/bin/env python3
"""Hot-leg 2219 targeted follow-up: confirm AgentBook sellout; re-read HUNT PASS / Tri333 /
DinoAgent / Wuyuhive counts; identify new S1 0xcfE5. Single-call reads only (batch-revert safe)."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/",
       "https://rpc.ankr.com/bsc"]
DEADLINE = time.time() + 110
t0 = time.time()
out = {}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def raw(to, data):
    if time.time() > DEADLINE:
        return "deadline"
    for ep in EPS:
        if time.time() > DEADLINE:
            return "deadline"
        try:
            v = _fast_single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
            if v is None or v == "0x":
                return None
            try:
                return int(v, 16)
            except Exception:
                return v
        except Exception:
            continue
    return None
def call(to, sig, args=""): return raw(to, sel(sig) + args)
def decode_str(v):
    if not isinstance(v, str) or not v.startswith("0x") or len(v) < 138:
        return None
    try:
        b = bytes.fromhex(v[2:])
        off = int.from_bytes(b[32:64], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", "replace")
    except Exception:
        return None

def read(addr, views):
    d = {}
    for sig, key in views:
        if "address" in sig:
            d[key] = call(addr, sig, enc(USER))
        else:
            d[key] = call(addr, sig)
    for k in ("name", "symbol", "contractURI"):
        if d.get(k):
            d[k] = decode_str(d[k])
    return d

blk = None
for ep in EPS:
    try:
        v = _fast_single(ep, "eth_blockNumber", [], 8, retries=0)
        if v:
            blk = int(v, 16); break
    except Exception:
        continue
out["block"] = blk

# AgentBook - sellout confirmation
out["agentbook"] = read("0xEECaCBE6eAC6D6F2a38e8daA9049C7AA08aD43b0", [
    ("freeClaimed()", "freeClaimed"), ("FREE_SUPPLY()", "FREE_SUPPLY"),
    ("MAX_SUPPLY()", "MAX_SUPPLY"), ("totalSupply()", "totalSupply"),
    ("totalMinted()", "totalMinted"), ("mintedBy(address)", "mintedBy_user"),
    ("freeUsed(address)", "freeUsed_user"), ("balanceOf(address)", "balanceOf_user"),
    ("mintOpen()", "mintOpen"), ("name()", "name"), ("symbol()", "symbol")])

# HUNT PASS - totalMinted re-check (null in main leg4 batch)
out["huntpass"] = read("0x885128Cf234c768F1353e2C1432D55873C6b67dD", [
    ("totalMinted()", "totalMinted"), ("freeClaimed()", "freeClaimed"),
    ("freeMinted()", "freeMinted"), ("FREE_SUPPLY()", "FREE_SUPPLY"),
    ("totalSupply()", "totalSupply"), ("mintedBy(address)", "mintedBy_user"),
    ("balanceOf(address)", "balanceOf_user"), ("mintOpen()", "mintOpen")])

# Tri333 - cap views to compute %
out["tri333"] = read("0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f", [
    ("FREE_SUPPLY()", "FREE_SUPPLY"), ("MAX_SUPPLY()", "MAX_SUPPLY"),
    ("freeMinted()", "freeMinted"), ("totalSupply()", "totalSupply"),
    ("totalMinted()", "totalMinted"), ("freeClaimed()", "freeClaimed"),
    ("mintedBy(address)", "mintedBy_user"), ("balanceOf(address)", "balanceOf_user"),
    ("name()", "name"), ("symbol()", "symbol")])

# DinoAgent - confirm 593/777 + user slot
out["dinoagent"] = read("0xcE19D6A5FF15e088D4bf23614242927139084895", [
    ("freeMinted()", "freeMinted"), ("FREE_SUPPLY()", "FREE_SUPPLY"),
    ("totalSupply()", "totalSupply"), ("totalMinted()", "totalMinted"),
    ("freeUsed(address)", "freeUsed_user"), ("mintedBy(address)", "mintedBy_user"),
    ("balanceOf(address)", "balanceOf_user"), ("mintOpen()", "mintOpen"),
    ("name()", "name"), ("symbol()", "symbol")])

# Wuyuhive - confirm 1546/3000 + user slot
out["wuyuhive"] = read("0x250e800025a9a7861970e253bab6975a57f80567", [
    ("freeClaimed()", "freeClaimed"), ("FREE_SUPPLY()", "FREE_SUPPLY"),
    ("totalSupply()", "totalSupply"), ("mintedBy(address)", "mintedBy_user"),
    ("balanceOf(address)", "balanceOf_user"), ("mintOpen()", "mintOpen")])

# New S1 0xcfE5 - identify
out["cfe5_new_s1"] = read("0xcfE5E4925A76A3AA11aFA79e04c6fad3611cee40", [
    ("name()", "name"), ("symbol()", "symbol"), ("freeMinted()", "freeMinted"),
    ("FREE_SUPPLY()", "FREE_SUPPLY"), ("MAX_SUPPLY()", "MAX_SUPPLY"),
    ("mintOpen()", "mintOpen"), ("totalSupply()", "totalSupply"),
    ("balanceOf(address)", "balanceOf_user"), ("contractURI()", "contractURI"),
    ("freeClaimed()", "freeClaimed")])

out["duration_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{BASE}/hot-leg-run-2026-11-07-2219-targeted.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str))
