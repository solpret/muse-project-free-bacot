#!/usr/bin/env python3
"""Follow-up run 2026-11-07 0931: first-mint binary search (fixed head) for
Tacotron/Orchidia/BOT-UNIT/BAOracle; retry free-view reads; BOT-UNIT + BAOracle
on-chain website()/xAccount()/x() strings; DYOR token ABIs + claim mechanics.
Read-only; writes run-2026-11-07-0931-followup.json.
"""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from Crypto.Hash import keccak
from fast_rpc import race
from ankr import get_logs

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def read_one(addr, sig, tries=3):
    data = sel(sig) + enc(USER) if "(address)" in sig else sel(sig)
    for _ in range(tries):
        try:
            return to_int(race("eth_call", [{"to": addr, "data": data}, "latest"]))
        except Exception:
            time.sleep(2)
    return None

def read_str(addr, sig, tries=3):
    data = sel(sig)
    for _ in range(tries):
        try:
            raw = race("eth_call", [{"to": addr, "data": data}, "latest"])
            if not raw or len(raw) < 130:
                return None
            b = bytes.fromhex(raw[2:])
            ln = int.from_bytes(b[32:64], "big")
            return b[64:64+ln].decode("utf-8", "replace")
        except Exception:
            time.sleep(2)
    return None

def read_quote2(addr, fn):
    data = sel(fn) + enc(USER) + "1".rjust(64, "0")
    for _ in range(3):
        try:
            return to_int(race("eth_call", [{"to": addr, "data": data}, "latest"]))
        except Exception:
            time.sleep(2)
    return None

def head_block():
    for _ in range(5):
        try:
            return int(race("eth_blockNumber", []), 16)
        except Exception:
            time.sleep(3)
    return None

def has_mint(addr, fb, tb):
    try:
        r = get_logs(addr, fb, tb, topics=[TRANSFER, ZERO])
        logs = r.get("result", {}).get("logs", []) if isinstance(r, dict) else []
        return len(logs) > 0
    except Exception as e:
        print(f"  has_mint FAIL {fb}-{tb}: {type(e).__name__}", flush=True)
        return None

def first_mint_block(addr, lo, hi):
    calls = 0
    f = has_mint(addr, lo, hi); calls += 1
    if f is None: return None, calls, "rpc-fail"
    if not f: return None, calls, "no-mint-in-range"
    a, b = lo, hi
    while a < b:
        mid = (a + b) // 2
        f = has_mint(addr, a, mid); calls += 1
        if f is None: return None, calls, "rpc-fail-mid"
        if f: b = mid
        else: a = mid + 1
    return a, calls, "ok"

def block_ts(blk):
    for _ in range(3):
        try:
            b = race("eth_getBlockByNumber", ["0x" + format(blk, "x"), False])
            return int(b.get("timestamp", "0x0"), 16)
        except Exception:
            time.sleep(2)
    return None

def fetch_abi(addr):
    try:
        req = urllib.request.Request(
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
            headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            d = json.load(resp)
        return d.get("match"), d.get("stdJson", {}).get("output", {}).get("abi") or d.get("abi")
    except Exception as e:
        return f"FAIL:{type(e).__name__}", None

out = {}
HEAD = head_block()
out["head_block"] = HEAD
print("HEAD", HEAD, flush=True)

TARGETS = {
    "Tacotron": "0x05deBE4445232205AE7E79d02cb5DE5AA0641efF",
    "Orchidia": "0x09bcdd97186f6f37521bd1b281d329e48ac54b89",
    "BOT-UNIT": "0x1482fba999e7c1da9764c5e874d18a832881e3d6",
    "BAOracle": "0xcBe2DBBFF4264Dc67Bf557c64e29997B82439354",
}
if HEAD:
    for name, addr in TARGETS.items():
        fb, calls, status = first_mint_block(addr, 131000000, HEAD)
        ts = block_ts(fb) if fb else None
        out[name] = {"first_mint_block": fb, "calls": calls, "status": status,
                     "first_mint_ts": ts}
        print(f"{name}: firstMint={fb} ts={ts} calls={calls} status={status}", flush=True)
        json.dump(out, open(f"{BASE}/run-2026-11-07-0931-followup.json", "w"), indent=1)

# Retry reads
retry = {}
retry["Orchidia"] = {s: read_one(TARGETS["Orchidia"], s) for s in
    ["freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "FREE_PER_WALLET()",
     "freeLeft()", "freeFor()", "mintedBy(address)", "totalSupply()",
     "MAX_SUPPLY()", "owner()"]}
retry["Orchidia"]["quote(user,1)"] = read_quote2(TARGETS["Orchidia"], "quote(address,uint256)")
retry["BOT-UNIT"] = {
    "website()": read_str(TARGETS["BOT-UNIT"], "website()"),
    "xAccount()": read_str(TARGETS["BOT-UNIT"], "xAccount()"),
    "hasFreeMint(user)": read_one(TARGETS["BOT-UNIT"], "hasFreeMint(address)"),
    "mintableBy(user)": read_one(TARGETS["BOT-UNIT"], "mintableBy(address)"),
    "mintedBy(user)": read_one(TARGETS["BOT-UNIT"], "mintedBy(address)"),
    "FREE_PER_WALLET()": read_one(TARGETS["BOT-UNIT"], "FREE_PER_WALLET()"),
    "totalSupply()": read_one(TARGETS["BOT-UNIT"], "totalSupply()"),
    "maxSupply()": read_one(TARGETS["BOT-UNIT"], "maxSupply()"),
    "publicRemaining()": read_one(TARGETS["BOT-UNIT"], "publicRemaining()"),
    "owner()": read_one(TARGETS["BOT-UNIT"], "owner()"),
    "quote(user,1)": read_quote2(TARGETS["BOT-UNIT"], "quote(address,uint256)"),
}
retry["BAOracle"] = {
    "website()": read_str(TARGETS["BAOracle"], "website()"),
    "x()": read_str(TARGETS["BAOracle"], "x()"),
    "agentRegistry()": read_one(TARGETS["BAOracle"], "agentRegistry()"),
    "hasAgentId(user)": read_one(TARGETS["BAOracle"], "hasAgentId(address)"),
    "freeMinted()": read_one(TARGETS["BAOracle"], "freeMinted()"),
    "freeMintLeft()": read_one(TARGETS["BAOracle"], "freeMintLeft()"),
    "totalMinted()": read_one(TARGETS["BAOracle"], "totalMinted()"),
    "totalSupply()": read_one(TARGETS["BAOracle"], "totalSupply()"),
    "MAX_SUPPLY()": read_one(TARGETS["BAOracle"], "MAX_SUPPLY()"),
    "mintedBy(user)": read_one(TARGETS["BAOracle"], "mintedBy(address)"),
    "owner()": read_one(TARGETS["BAOracle"], "owner()"),
    "quote(user,1)": read_quote2(TARGETS["BAOracle"], "quote(address,uint256)"),
}
out["retry_reads"] = retry
print("RETRY:", json.dumps(retry, indent=1), flush=True)

# DYOR token ABIs + claim mechanics
dyor = {}
for tok, taddr in [("DYOR_token_A", "0x9791d92B63a566AC578e6070ee1F8546C8b2153B"),
                   ("DYOR_token_B", "0xaFEcb35096EF3A447460bF7A3B8b701f6d5468c7")]:
    match, abi = fetch_abi(taddr)
    e = {"address": taddr, "sourcify_match": match}
    if abi:
        fns = [(x.get("name"), x.get("type")) for x in abi]
        e["fn_names"] = sorted(set(n for n, t in fns if t == "function"))
        e["claim_fns"] = [n for n in e["fn_names"] if "claim" in n.lower()]
        e["pair_views"] = [n for n in e["fn_names"] if "pair" in n.lower() or "lp" in n.lower() or "launch" in n.lower() or "uniswap" in n.lower() or "pancake" in n.lower()]
    dyor[tok] = e
    print(tok, "match", match, "claim_fns", e.get("claim_fns"), "pair_views", e.get("pair_views"), flush=True)
out["DYOR_tokens"] = dyor
json.dump(out, open(f"{BASE}/run-2026-11-07-0931-followup.json", "w"), indent=1)
print("DONE", flush=True)
