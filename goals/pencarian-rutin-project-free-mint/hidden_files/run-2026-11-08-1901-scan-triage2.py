#!/usr/bin/env python3
"""Follow-up views for Jinchan / Gloop / Skunk Hollow, run 1901. Read-only.
Uses single eth_call per view (NOT batch) so one revert cannot poison others."""
import sys, json, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]

def sel(sig): return "0x" + keccak(sig.encode()).hex()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def call(addr, sig, args=""):
    data = sel(sig) + args
    for ep in EPS:
        try:
            r = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": addr, "data": data}, "latest"]}, timeout=10, retries=0)
            if isinstance(r, dict) and "result" in r:
                h = r["result"]
                if h in (None, "0x"): return None
                try: return int(h, 16)
                except Exception: return h
            if isinstance(r, dict) and "error" in r:
                return "REVERT"
        except Exception:
            continue
    return "ERR"

J = "0xccc127D1A7Ef1e385757784a9878F7279BF3B19D"
G = "0x79d1821bC6E7576Aac4422BEAD0951A4adc7075a"
S = "0x88E4b613609af6C479F11D78e5a696d84B78993B"

out = {}
out["Jinchan"] = {
    "opensAt": call(J, "opensAt()"),
    "mintEnd": call(J, "mintEnd()"),
    "MINT_DURATION": call(J, "MINT_DURATION()"),
    "freeMintedCount": call(J, "freeMintedCount()"),
    "freeRemaining": call(J, "freeRemaining()"),
    "paidMintedCount": call(J, "paidMintedCount()"),
    "totalMinted": call(J, "totalMinted()"),
    "hasFreeClaimed_user": call(J, "hasFreeClaimed(address)", enc_addr(USER)),
    "agentIdRegistry": call(J, "agentIdRegistry()"),
}
out["Gloop"] = {
    "MINT_START": call(G, "MINT_START()"),
    "TOTAL_SUPPLY": call(G, "TOTAL_SUPPLY()"),
    "totalMinted": call(G, "totalMinted()"),
    "difficultyBits": call(G, "difficultyBits()"),
    "tierQuota": call(G, "tierQuota()"),
    "hasMinted_user": call(G, "hasMinted(address)", enc_addr(USER)),
    "AGENT_REGISTRY": call(G, "AGENT_REGISTRY()"),
}
out["Skunk"] = {
    "totalSkunksMinted": call(S, "totalSkunksMinted()"),
    "FREE_SKUNKS_TOTAL": call(S, "FREE_SKUNKS_TOTAL()"),
    "freeSkunksRemaining": call(S, "freeSkunksRemaining()"),
    "freeSkunksClaimed": call(S, "freeSkunksClaimed()"),
    "freeWindowOpen": call(S, "freeWindowOpen()"),
    "freeWindowClosesAt": call(S, "freeWindowClosesAt()"),
    "gateStart": call(S, "gateStart()"),
    "registry": call(S, "registry()"),
    "skunkToken": call(S, "skunkToken()"),
    "freeClaimedBy_user": call(S, "freeClaimedBy(address)", enc_addr(USER)),
}
print(json.dumps(out, indent=1))
json.dump(out, open(BASE + "/run-2026-11-08-1901-scan-triage2.json", "w"), indent=1)
print("DONE")
