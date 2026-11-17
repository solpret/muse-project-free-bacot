#!/usr/bin/env python3
"""Lean re-read run 2026-11-06 23:31 WIB — read-only, never writes snapshot/state.
Priority contracts first, then all snapshot contracts + track_c.
Batch eth_call per contract (fast_rpc.call_many); on batch failure fall back
to racing totalSupply + balanceOf only. Incremental JSON write per contract.
"""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import call_many, race

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2331"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def to_int(v):
    if v is None: return None
    try: return int(v, 16)
    except Exception: return None

# Generic lean views: (sig, key, args)
LEAN = [("totalSupply()", "totalSupply", ""),
        ("totalMinted()", "totalMinted", ""),
        ("freeClaimed()", "freeClaimed", ""),
        ("freeMinted()", "freeMinted", ""),
        ("FREE_SUPPLY()", "FREE_SUPPLY", ""),
        ("MAX_SUPPLY()", "MAX_SUPPLY", ""),
        ("mintOpen()", "mintOpen", ""),
        ("balanceOf(address)", "balanceOf_user", "addr")]

PRIORITY_VIEWS = {
 "Soul Agent": ["totalSupply()", "totalMinted()", "FREE_MINTS_PER_WALLET()", "FREE_TIER_END()", "mintedPerWallet(address)", "balanceOf(address)", "quoteFor(address,uint256)"],
 "MoonCat": ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "mintedBy(address)", "quote(address,uint256)", "mintOpen()"],
 "Qilingentle": ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "balanceOf(address)", "mintedBy(address)", "quote(address,uint256)", "mintOpen()"],
 "Hivejupiter": ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "balanceOf(address)", "mintedBy(address)", "quote(address,uint256)", "mintOpen()"],
 "Saturnswarm": ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "balanceOf(address)", "mintedBy(address)", "quote(address,uint256)", "mintOpen()"],
 "Boohiveling": ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "balanceOf(address)", "mintedBy(address)", "quote(address,uint256)", "mintOpen()"],
 "Pulsekeep": ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_CAP()", "MAX_SUPPLY()", "balanceOf(address)", "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)", "claimedFree(address)", "quote(address,uint256)"],
 "KING Agent": ["totalSupply()", "totalMinted()", "freeQuota()", "remainingFree()", "mintedBy(address)", "costOf(address,uint256)", "balanceOf(address)", "agentGateOn()", "mintOpen()"],
 "Forklings": ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "costOf(address,uint256)", "mintsLeft(address)", "mintOpen()", "mintedBy(address)", "price()"],
 "Lion's Share": ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "costOf(address,uint256)", "mintedBy(address)", "balanceOf(address)", "mintOpen()", "MAX_SUPPLY()", "price()"],
 "PassAgentX": ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)", "claimedFree(address)", "quote(address,uint256)"],
 "WHALE-B": ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "mintedBy(address)", "MAX_SUPPLY()", "mintOpen()"],
 "ChimpAgent": ["totalSupply()", "totalMints()", "MAX_MINTS()", "FREE_PER_WALLET()", "MAX_PER_WALLET()", "PRICE()", "MINT_DEADLINE()", "mintOpen()", "tradingOpen()", "freeLeft(address)", "quote(address,uint256)", "mintedBy(address)", "balanceOf(address)"],
}

PRIORITY_ADDR = {
 "Soul Agent": "0x8fdb9411753c58476a41f7b88a44989f8d687d63",
 "MoonCat": "0x045425004b622733ced4139e930c622187ea6c73",
 "Qilingentle": "0x423d25764E4D3D792C08e04C759cE3b0FcDE8596",
 "Hivejupiter": "0x8DF74cBe998F8d447E7c77dD5117aFB940605400",
 "Saturnswarm": "0x238C995A1376e08395b970870A546C57aE184434",
 "Boohiveling": "0xC1dAf114e377242eEB76d180B24b491758Acb4f7",
 "Pulsekeep": "0x65c89bD01A03B9B9B73eD29d3B3aF8D2eb034DFc",
 "KING Agent": "0x2A2463d243E5c4dF850e48f350392AD23B494132",
 "Forklings": "0xD7B3FD33e0b465B0e374906F60567D317b758FD8",
 "Lion's Share": "0x6AC03204aFE631D673938Eb82D2F121B015eAB3F",
 "PassAgentX": "0x08b1A979Dd997492EEcc010fe986eA2e2925e620",
 "WHALE-B": "0xf81b542c41f982a7d7a8e2ee8cab5feee6203218",
 "ChimpAgent": "0x57D41Ff4895A19f518a0Ec3A2Fa56284a85f5689",
}

def build_calls(addr, views):
    calls, keys = [], []
    for sig in views:
        base = sig.split("(")[0]
        if "(address,uint256)" in sig:
            data = sel(sig) + enc(USER) + enc_uint(1); key = base + "_user_1"
        elif "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append((addr, data)); keys.append(key)
    return calls, keys

def read_contract(addr, views, lean=False):
    """Batch; on failure, race totalSupply + balanceOf only."""
    calls, keys = build_calls(addr, views)
    d = {"address": addr}
    try:
        res = call_many(calls, timeout=15)
        for k, v in zip(keys, res):
            d[k] = to_int(v)
        d["_batch_ok"] = True
    except Exception as e:
        d["_batch_error"] = str(e)[:120]
        # fallback: only the two most robust views
        for sig, key in (("totalSupply()", "totalSupply"), ("balanceOf(address)", "balanceOf_user")):
            try:
                data = sel(sig) + (enc(USER) if "address" in sig else "")
                d[key] = to_int(race("eth_call", [{"to": addr, "data": data}, "latest"]))
            except Exception:
                d[key] = None
        for k in keys:
            d.setdefault(k, None)
        d["_batch_ok"] = False
    return d

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
contracts = snap.get("contracts", {})
track_c = snap.get("track_c", {})

try:
    blk = int(race("eth_blockNumber", []), 16)
except Exception as e:
    blk = None
    print("BLOCK-FAIL", e, flush=True)
print("BLOCK", blk, flush=True)

out = {"block": blk, "reread": {}, "track_c": {}, "started_wib": "2026-11-06 23:31 WIB"}
out_path = f"{BASE}/run-{TS}-reread.json"

def save():
    with open(out_path + ".tmp", "w") as f:
        json.dump(out, f, indent=1)
    import os; os.replace(out_path + ".tmp", out_path)

# --- Priority first (sequential, full views) ---
for name, addr in PRIORITY_ADDR.items():
    t = time.time()
    d = read_contract(addr, PRIORITY_VIEWS[name])
    out["reread"][name] = d
    save()
    print(f"PRIO {name} {d} ({time.time()-t:.1f}s)", flush=True)

# --- Rest of snapshot contracts: lean batch, parallel ---
rest = [(k, v.get("address")) for k, v in contracts.items() if k not in PRIORITY_ADDR and v.get("address")]
print(f"REST contracts: {len(rest)}", flush=True)
lean_views = [s for s, _, _ in LEAN]

def read_lean(item):
    name, addr = item
    t = time.time()
    d = read_contract(addr, lean_views)
    print(f"LEAN {name} totalSupply={d.get('totalSupply')} freeClaimed={d.get('freeClaimed')} bal={d.get('balanceOf_user')} ({time.time()-t:.1f}s)", flush=True)
    return name, d

with ThreadPoolExecutor(max_workers=8) as ex:
    for name, d in ex.map(read_lean, rest):
        out["reread"][name] = d
        save()

# --- track_c: lean sale views, parallel ---
TC_VIEWS = ["totalSupply()", "freeMinted()", "freeSharesRemaining()", "freeClaimed(address)", "balanceOf(address)"]
tc_items = []
for k, v in track_c.items():
    a = v.get("address") or v.get("sale") or v.get("token")
    if a and isinstance(a, str) and a.startswith("0x"):
        tc_items.append((k, a))
print(f"TRACK_C items: {len(tc_items)}", flush=True)

def read_tc(item):
    name, addr = item
    t = time.time()
    d = read_contract(addr, TC_VIEWS)
    print(f"TC {name} totalSupply={d.get('totalSupply')} freeMinted={d.get('freeMinted')} ({time.time()-t:.1f}s)", flush=True)
    return name, d

with ThreadPoolExecutor(max_workers=8) as ex:
    for name, d in ex.map(read_tc, tc_items):
        out["track_c"][name] = d
        save()

print(f"REREAD DONE in {time.time()-T0:.1f}s block {blk} reread={len(out['reread'])} track_c={len(out['track_c'])}", flush=True)
