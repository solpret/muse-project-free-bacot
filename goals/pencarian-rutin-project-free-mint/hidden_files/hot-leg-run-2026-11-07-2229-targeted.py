#!/usr/bin/env python3
"""Hot-leg 2229 targeted follow-up: leg4 re-read retried after transient RPC probe
failure (main run probe failed; curl re-probe shows dataseed.binance.org +
dataseed1.bnbchain.org healthy, publicnode rate-limited -32005, Ankr now
unauthorized/API-key). Single-call reads only (batch-revert safe). Working
endpoints only. Focus: Tri333 25% threshold watch + all leg4 items."""
import json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org", "https://bsc-dataseed1.bnbchain.org",
       "https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed3.bnbchain.org"]
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
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": to, "data": data}, "latest"]}).encode()
    for ep in EPS:
        if time.time() > DEADLINE:
            return "deadline"
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r:
                o = json.load(r)
            if "error" in o:
                continue
            v = o.get("result")
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

blk = None
for ep in EPS:
    try:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
        req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as r:
            o = json.load(r)
        if o.get("result"):
            blk = int(o["result"], 16); break
    except Exception:
        continue
out["block"] = blk

NFT_VIEWS = ["totalSupply()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
             "balanceOf(address)", "mintedBy(address)", "freeUsed(address)",
             "claimedFree(address)", "mintOpen()"]
SALE_VIEWS = ["freeClaimed()", "freeSharesRemaining()", "freeLeft(address)",
              "quote(address,uint256)", "mintedBy(address)", "mintOpen()",
              "totalMinted()", "freeMinted()", "totalSupply()", "balanceOf(address)",
              "freeFor(address)"]
LEAD_VIEWS = ["totalMints()", "MAX_MINTS()", "freeLeft(address)", "quote(address,uint256)",
              "mintedBy(address)", "mintOpen()", "totalSupply()", "balanceOf(address)"]
ITEMS = {
 "Orchidia": ("0x09bcdd97186f6f37521bd1b281d329e48ac54b89", NFT_VIEWS),
 "Agent Goats": ("0x0E9E0a3B46dC0d36A1Ab64f553Dd8A0693E6aAa6", NFT_VIEWS),
 "Tacotron": ("0x05debe4445232205ae7e79d02cb5de5aa0641eff", NFT_VIEWS),
 "Agent Frogs": ("0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31", NFT_VIEWS),
 "Wuyuhive": ("0x250e800025a9a7861970e253bab6975a57f80567", NFT_VIEWS),
 "Thronemind": ("0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90", NFT_VIEWS),
 "Ink Koi": ("0xbd4B4e7189ae9356514664146b0eD683601200A9", NFT_VIEWS),
 "Night Bandits Club": ("0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf", NFT_VIEWS),
 "ADCHAR": ("0x6E8b05C2dD1C625D839f33f60B837d9AF25E6044", NFT_VIEWS),
 "Saturnagent": ("0xef870a9b4a529373fb2e174b59ca7a66eb018074", SALE_VIEWS),
 "Lumenhold": ("0x9701980b0afd825134390ee46fb3bd675a2f356f", SALE_VIEWS),
 "Horus AI": ("0x794ad67a5590c7e5848e49181297f9cc7c6ce00e", NFT_VIEWS),
 "AURISLE": ("0xC52a979C20C5a43e5Be4Ffa6d1A4DD50069D5E2D", NFT_VIEWS),
 "DinoAgent": ("0xcE19D6A5FF15e088D4bf23614242927139084895", NFT_VIEWS),
 "Tri333": ("0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f", NFT_VIEWS),
 "LOCKSMITH": ("0x05e8738290be6639fD0f7236ebF444E5466D3164", NFT_VIEWS),
 "AgentBook": ("0xEECaCBE6eAC6D6F2a38e8daA9049C7AA08aD43b0", SALE_VIEWS),
 "CipherAgent": ("0x158b5e25015758a94703A27c152889451E5d52E5", LEAD_VIEWS),
 "MarsAgent": ("0x2231FdAe405c33dc4993f8C577c453802FF1AcE9", LEAD_VIEWS),
 "HUNT PASS": ("0x885128Cf234c768F1353e2C1432D55873C6b67dD", NFT_VIEWS),
 "King's Game": ("0x9eA27f3F0919DaF6a4401CFd09563162d395061D", NFT_VIEWS),
 "Paw Gang": ("0x587C303982187Ec578dF309d27670327b13202F8", NFT_VIEWS),
 "fab7dd20-variant": ("0xfab7dd20e8816e10227C1222bd4Bd446FecF1B72",
    ["totalSupply()", "freeMinted()", "FREE_SHARES()", "freeClaimed(address)", "balanceOf(address)", "startTime()"]),
}
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
def read_item(args):
    name, (addr, views) = args
    d = {"address": addr}
    for sig in views:
        key = sig.split("(")[0]
        if sig.startswith("quote("):
            v = call(addr, sig, enc(USER) + enc_uint(1)); key += "_user1"
        elif "address" in sig:
            v = call(addr, sig, enc(USER)); key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    snap_v = snap.get("contracts", {}).get(name, {}) or snap.get("track_c", {}).get(name, {})
    d["snap"] = {k: snap_v.get(k) for k in ("freeClaimed", "FREE_SUPPLY", "freeSupply", "totalSupply", "status", "freeMinted", "totalMinted") if snap_v.get(k) is not None}
    return name, d
if blk is None:
    out["leg4_reread"] = {"block": None, "status": "SKIPPED - RPC still unreachable on retry; no conclusion drawn. Retry next run.", "items_attempted": len(ITEMS)}
else:
    with ThreadPoolExecutor(max_workers=20) as ex:
        leg4 = dict(ex.map(read_item, list(ITEMS.items())))
    out["leg4_reread"] = {"block": blk, "items": leg4}
    # Tri333 cap views (threshold math)
    out["tri333_caps"] = {
        "FREE_SUPPLY": call("0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f", "FREE_SUPPLY()"),
        "MAX_SUPPLY": call("0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f", "MAX_SUPPLY()"),
        "FREE_CAP": call("0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f", "FREE_CAP()"),
        "freeCount_user": call("0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f", "freeCount(address)", enc(USER)),
        "freeMinted": call("0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f", "freeMinted()"),
    }
    # New S1 0xcfE5 from 2219 - watchlist-only growth check
    out["cfe5"] = {
        "totalSupply": call("0xcfE5E4925A76A3AA11aFA79e04c6fad3611cee40", "totalSupply()"),
        "freeMinted": call("0xcfE5E4925A76A3AA11aFA79e04c6fad3611cee40", "freeMinted()"),
        "balanceOf_user": call("0xcfE5E4925A76A3AA11aFA79e04c6fad3611cee40", "balanceOf(address)", enc(USER)),
    }
out["duration_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{BASE}/hot-leg-run-2026-11-07-2229-targeted.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str))
