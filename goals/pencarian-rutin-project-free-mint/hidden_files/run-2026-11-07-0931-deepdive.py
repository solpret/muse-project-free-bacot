#!/usr/bin/env python3
"""Deep-dive run 2026-11-07 0931: Tacotron, Orchidia, BOT-UNIT, BAOracle (new from
Boltbook web leg) + AGOAT refresh + DYOR dual-token claim check (track B).
Read-only; writes run-2026-11-07-0931-deepdive.json.
Per-view race(); first-mint via binary search on address-filtered eth_getLogs
(Transfer from zero) over public dataseeds, 1000-block chunks.
"""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak
from fast_rpc import race, _single

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def read_one(addr, sig):
    data = sel(sig) + enc(USER) if "(address)" in sig else sel(sig)
    try:
        r = race("eth_call", [{"to": addr, "data": data}, "latest"])
        return to_int(r)
    except Exception:
        return None

def read_quote(addr):
    # quote(address,uint256) with (user,1)
    data = sel("quote(address,uint256)") + enc(USER) + "1".rjust(64, "0")
    try:
        r = race("eth_call", [{"to": addr, "data": data}, "latest"])
        return to_int(r)
    except Exception:
        return None

def read_cost(addr):
    data = sel("cost(address,uint256)") + enc(USER) + "1".rjust(64, "0")
    try:
        r = race("eth_call", [{"to": addr, "data": data}, "latest"])
        return to_int(r)
    except Exception:
        return None

def sourcify_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            d = json.load(resp)
        std = d.get("stdJson", {})
        srcs = std.get("sources", {})
        abi = None
        for v in srcs.values():
            pass
        # ABI lives under stdJson.output.abi in v2 response
        abi = std.get("output", {}).get("abi")
        if abi is None:
            abi = d.get("abi")
        return d.get("match", "?"), abi
    except Exception as e:
        return f"FAIL:{type(e).__name__}", None

def has_mint(addr, fb, tb):
    """True if any Transfer-from-zero log for addr in [fb,tb] (1000-block max)."""
    params = {"address": addr, "fromBlock": hex(fb), "toBlock": hex(tb),
              "topics": [TRANSFER, ZERO]}
    for ep in EPS:
        try:
            logs = _single(ep, "eth_getLogs", [params], 15, retries=0)
            return len(logs) > 0, len(logs)
        except Exception:
            continue
    return None, None

def first_mint_block(addr, lo, hi):
    """Binary search earliest block with a mint; returns (block, calls) or (None, calls)."""
    calls = 0
    found, n = has_mint(addr, lo, hi)
    calls += 1
    if found is None:
        return None, calls, "rpc-fail"
    if not found:
        return None, calls, "no-mint-in-range"
    # binary search: earliest block with mint in [lo,hi]
    a, b = lo, hi
    while a < b:
        mid = (a + b) // 2
        f, _ = has_mint(addr, a, mid)
        calls += 1
        if f is None:
            return None, calls, "rpc-fail-mid"
        if f:
            b = mid
        else:
            a = mid + 1
    return a, calls, "ok"

def block_ts(blk):
    try:
        b = race("eth_getBlockByNumber", ["0x" + format(blk, "x"), False])
        return int(b.get("timestamp", "0x0"), 16)
    except Exception:
        return None

VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "FREE_SUPPLY()", "FREE_CAP()", "MAX_SUPPLY()", "MAX_PER_WALLET()",
         "FREE_PER_WALLET()", "mintOpen()", "mintedBy(address)",
         "freeUsed(address)", "freeClaimed(address)", "balanceOf(address)",
         "owner()", "AGENT_ID()", "agentIdRegistry()", "registry()",
         "launchTime()", "mintOpensAt()", "price()", "cost()"]

TARGETS = {
    "Tacotron": "0x05deBE4445232205AE7E79d02cb5DE5AA0641efF",
    "Orchidia": "0x09bcdd97186f6f37521bd1b281d329e48ac54b89",
    "BOT-UNIT": "0x1482fba999e7c1da9764c5e874d18a832881e3d6",
    "BAOracle": "0xcBe2DBBFF4264Dc67Bf557c64e29997B82439354",
    "AgentGoats": "0x0E9E0a3B46dC0d36A1Ab64f553Dd8A0693E6aAa6",
}
out = {"block": None}
try:
    out["block"] = int(race("eth_blockNumber", []), 16)
except Exception as e:
    print("BLOCK FAIL", e, flush=True)
print("BLOCK", out["block"], flush=True)

for name, addr in TARGETS.items():
    d = {"address": addr}
    for sig in VIEWS:
        d[sig] = read_one(addr, sig)
    d["quote(user,1)"] = read_quote(addr)
    d["cost(user,1)"] = read_cost(addr)
    # contractURI (string)
    try:
        raw = race("eth_call", [{"to": addr, "data": sel("contractURI()")}, "latest"])
        d["contractURI_raw"] = (raw or "")[:300]
    except Exception:
        d["contractURI_raw"] = None
    match, abi = sourcify_abi(addr)
    d["sourcify_match"] = match
    if abi:
        fns = [f.get("name") for f in abi if f.get("type") == "function"]
        d["abi_fns"] = fns
        d["abi_has_registry"] = any("AGENT_ID" in f or "agentIdRegistry" in f or "registry" in f.lower() for f in fns)
        d["abi_free_views"] = [f for f in fns if f.startswith("free")]
        d["abi_mint_fns"] = [f for f in fns if "mint" in f.lower()]
    else:
        d["abi_fns"] = None
    # first mint binary search over [131000000, head]
    fb, calls, status = first_mint_block(addr, 131000000, out["block"])
    d["first_mint_block"] = fb
    d["first_mint_search_calls"] = calls
    d["first_mint_search_status"] = status
    if fb:
        d["first_mint_ts"] = block_ts(fb)
    out[name] = d
    fc = d.get("freeClaimed()") or d.get("freeMinted()")
    cap = d.get("FREE_SUPPLY()") or d.get("FREE_CAP()")
    print(f"{name}: totalSupply={d.get('totalSupply()')} free={fc}/{cap} mintOpen={d.get('mintOpen()')} bal={d.get('balanceOf(address)')} quote={d.get('quote(user,1)')} cost={d.get('cost(user,1)')} firstMint={fb} ts={d.get('first_mint_ts')} sourcify={match}", flush=True)

# DYOR dual-token claim check (track B): does the user hold a DYOR NFT?
# DYOR-8695 contract from snapshot
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
dyor = snap["contracts"].get("DYOR-8695", {})
print("DYOR-8695 snapshot:", dyor.get("address"), "status:", dyor.get("status"), flush=True)
dyor_addr = dyor.get("address")
claim = {}
if dyor_addr:
    claim["dyor_nft_contract"] = dyor_addr
    claim["user_balanceOf_dyor"] = read_one(dyor_addr, "balanceOf(address)")
    for tok, taddr in [("DYOR_token_A", "0x9791d92B63a566AC578e6070ee1F8546C8b2153B"),
                       ("DYOR_token_B", "0xaFEcb35096EF3A447460bF7A3B8b701f6d5468c7")]:
        td = {}
        for sig in ["claimableNfts(address)", "claimedNfts(address)", "totalSupply()",
                    "name()", "symbol()"]:
            td[sig] = read_one(taddr, sig)
        # token balance of user
        td["balanceOf(user)"] = read_one(taddr, "balanceOf(address)")
        claim[tok] = {"address": taddr, **td}
        print(tok, td, flush=True)
out["DYOR_claim_check"] = claim

json.dump(out, open(f"{BASE}/run-2026-11-07-0931-deepdive.json", "w"), indent=1)
print("DONE", flush=True)
