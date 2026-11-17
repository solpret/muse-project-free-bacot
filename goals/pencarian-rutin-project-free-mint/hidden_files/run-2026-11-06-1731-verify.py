#!/usr/bin/env python3
"""Verify run 2026-11-06 1731 WIB. Read-only.
Re-checks: Driftnauts (strong-lead-gate-blocked; free % + slot on-chain only),
CATAI (EARLY; legs b/c promotion check), Quantumfarm (strong-lead-gate-blocked;
deadline 21:00:37 WIB tonight), Soul Agent (EARLY; free % still inference?),
StarAgent (deadline ~21:26 WIB tonight), KING Agent (free % re-check).
No first-mint timestamp work this run (all first mints already verified).
"""
import json, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1731"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed2.bnbchain.org"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data, timeout=6):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None

def raw_hex(to, data, timeout=6):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "error" in out: continue
            return out["result"]
        except Exception:
            continue
    return None

def decode_str(hx):
    if not hx or hx == "0x": return None
    try:
        b = bytes.fromhex(hx[2:])
        if len(b) < 96: return None
        off = int.from_bytes(b[32:64], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", "ignore")
    except Exception:
        return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

ITEMS = {
 "Driftnauts": ("0x6a926234d3767f2eeb3db12c1b4c9e2912c5589b",
                 ["totalSupply()", "totalMinted()", "freeMinted()", "freeClaimed()",
                  "FREE_CAP()", "MAX_SUPPLY()", "PAID_CAP()", "paidMinted()",
                  "mintedBy(address)", "canFreeMint(address)", "claimedFree(address)",
                  "balanceOf(address)", "quote(address,uint256)"]),
 "CATAI": ("0x4aB809dc6e0C62a82d5Bff2F128C9FA30D752297",
           ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
            "FREE_SUPPLY()", "FREE_SLOTS()", "MAX_SUPPLY()", "PRICE()",
            "mintedBy(address)", "balanceOf(address)", "quote(address,uint256)"]),
 "Quantumfarm": ("0xA6Cf213F21C68b87f03Aa7d2a005e78F651eE010",
                 ["totalSupply()", "totalMinted()", "freeClaimed()", "freeLeft()",
                  "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "mintedBy(address)",
                  "freeUsed(address)", "freeFor(address)", "balanceOf(address)",
                  "quote(address,uint256)"]),
 "Soul Agent": ("0x8fdb9411753c58476a41f7b88a44989f8d687d63",
                ["totalSupply()", "totalMinted()", "FREE_MINTS_PER_WALLET()",
                 "FREE_TIER_END()", "mintedPerWallet(address)", "balanceOf(address)",
                 "quoteFor(address,uint256)"]),
 "StarAgent": ("0x7d390e37Ed41A359f276D8764ca15432704B99b7",
               ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
                "MAX_SUPPLY()", "mintedBy(address)", "balanceOf(address)",
                "quote(address,uint256)"]),
 "KING Agent": ("0x2A2463d243E5c4dF850e48f350392AD23B494132",
                ["totalSupply()", "totalMinted()", "freeQuota()", "remainingFree()",
                 "mintedBy(address)", "costOf(address,uint256)", "balanceOf(address)",
                 "agentGateOn()", "mintOpen()"]),
}

def read_item(args):
    name, (addr, views) = args
    d = {"address": addr}
    for sig in views:
        key = sig.split("(")[0]
        if "address" in sig and "uint256" in sig:
            v = call(addr, sig, enc(USER) + enc_uint(1)); key += "_user_1"
        elif "address" in sig:
            v = call(addr, sig, enc(USER)); key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    d["name"] = decode_str(raw_hex(addr, sel("name()")) or "")
    d["symbol"] = decode_str(raw_hex(addr, sel("symbol()")) or "")
    d["contractURI"] = decode_str(raw_hex(addr, sel("contractURI()")) or "")
    print(name, json.dumps(d, default=str), flush=True)
    return name, d

out = {}
with ThreadPoolExecutor(max_workers=6) as ex:
    for name, d in ex.map(read_item, ITEMS.items()):
        out[name] = d
json.dump(out, open(f"{BASE}/run-{TS}-verify.json", "w"), indent=1, ensure_ascii=False)
print("VERIFY DONE", flush=True)
