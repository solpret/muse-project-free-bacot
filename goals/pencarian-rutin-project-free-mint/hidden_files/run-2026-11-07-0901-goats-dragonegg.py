#!/usr/bin/env python3
"""Fresh per-view verification run 0901: Agent Goats (strong-lead check) + DragonEgg
(danger record). Read-only; writes run-2026-11-07-0901-goats-dragonegg.json.
Per-view race() (not batch) because the LEAN batch returned None for these."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak
from fast_rpc import race

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def read_one(addr, sig):
    data = sel(sig) + enc(USER) if "(address)" in sig else sel(sig)
    try:
        return race("eth_call", [{"to": addr, "data": data}, "latest"])
    except Exception as e:
        return f"FAIL:{type(e).__name__}"

out = {"block": None}
try:
    out["block"] = int(race("eth_blockNumber", []), 16)
except Exception as e:
    print("BLOCK FAIL", e, flush=True)

AGOAT = "0x0E9E0a3B46dC0d36A1Ab64f553Dd8A0693E6aAa6"
goats = {}
for sig in ["AGENT_ID()", "FREE_SUPPLY()", "MAX_SUPPLY()", "MAX_PER_WALLET()",
            "freeClaimed()", "totalSupply()", "mintOpen()", "cost()", "price()",
            "mintedBy(address)", "contractURI()", "owner()"]:
    raw = read_one(AGOAT, sig)
    if isinstance(raw, str) and raw.startswith("FAIL"):
        goats[sig] = None
        print(f"AGOAT {sig} FAIL", flush=True)
    elif sig == "contractURI()":
        goats[sig] = raw
        print(f"AGOAT {sig} = {str(raw)[:200]}", flush=True)
    else:
        v = to_int(raw)
        goats[sig] = v
        print(f"AGOAT {sig} = {hex(v) if isinstance(v, int) and v > 10**15 else v}", flush=True)
out["AgentGoats"] = goats

DREGG = "0xb0cc430fa9EfD6dfb8605df570f9acc449c8f7f1"
dregg = {}
for sig in ["totalSupply()", "totalMinted()", "freeMinted()", "FREE_CAP()",
            "MAX_SUPPLY()", "launchTime()", "agentIdRegistry()", "mintOpen()",
            "freeUsed(address)", "balanceOf(address)", "contractURI()", "owner()"]:
    raw = read_one(DREGG, sig)
    if isinstance(raw, str) and raw.startswith("FAIL"):
        dregg[sig] = None
        print(f"DREGG {sig} FAIL", flush=True)
    elif sig == "contractURI()":
        dregg[sig] = raw
        print(f"DREGG {sig} = {str(raw)[:200]}", flush=True)
    else:
        v = to_int(raw)
        dregg[sig] = v
        print(f"DREGG {sig} = {hex(v) if isinstance(v, int) and v > 10**15 else v}", flush=True)
out["DragonEgg"] = dregg

# First-mint block timestamp for DragonEgg (block 132116386) + AgentGoats first mint
try:
    b = race("eth_getBlockByNumber", ["0x" + format(132116386, "x"), False])
    out["dragonegg_first_mint_block_ts"] = int(b.get("timestamp", "0x0"), 16)
    print("DREGG first mint block ts:", out["dragonegg_first_mint_block_ts"], flush=True)
except Exception as e:
    print("DREGG block ts FAIL", e, flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-07-0901-goats-dragonegg.json", "w"), indent=1)
print("DONE", flush=True)
