#!/usr/bin/env python3
"""Deep verify 3 scan first-seen agent-shaped contracts, run 1901. Read-only."""
import sys, json, urllib.request, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import batch
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
ADDRS = ["0xccc127D1A7Ef1e385757784a9878F7279BF3B19D",
         "0x79d1821bC6E7576Aac4422BEAD0951A4adc7075a",
         "0x88E4b613609af6C479F11D78e5a696d84B78993B"]
REG_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"

def sel(sig): return "0x" + keccak(sig.encode()).hex()[:8]
def enc_addr(a): return "000000000000000000000000" + a[2:].lower()
def call(addr, data, timeout=15):
    for ep in EPS:
        try:
            return batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=timeout)[0]
        except Exception:
            continue
    return {"error": "all endpoints failed"}
def dec(h):
    if not isinstance(h, str) or not h or h == "0x": return None
    try: return int(h, 16)
    except Exception: return None
def dec_str(h):
    if not isinstance(h, str) or not h or h == "0x": return None
    try:
        b = bytes.fromhex(h[2:]); ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception: return None

discards = json.load(open(BASE + "/same-owner-discards.json"))
disc_owners = {str(d.get("owner", "")).lower() for d in discards if isinstance(d, dict)}

out = {}
for A in ADDRS:
    r = {}
    def tc(sig, args=""):
        return call(A, sel(sig) + args)
    r["name"] = dec_str(tc("name()"))
    r["symbol"] = dec_str(tc("symbol()"))
    r["totalSupply"] = dec(tc("totalSupply()"))
    r["totalMinted"] = dec(tc("totalMinted()"))
    r["MAX_SUPPLY"] = dec(tc("MAX_SUPPLY()"))
    r["FREE_SUPPLY"] = dec(tc("FREE_SUPPLY()"))
    r["freeClaimed"] = dec(tc("freeClaimed()"))
    r["freeMinted"] = dec(tc("freeMinted()"))
    r["freeLeft"] = dec(tc("freeLeft()"))
    r["mintOpen"] = dec(tc("mintOpen()"))
    r["price"] = dec(tc("price()"))
    r["owner_raw"] = tc("owner()")
    o = r["owner_raw"]
    r["owner"] = ("0x" + o[-40:]) if isinstance(o, str) and len(o) >= 42 else None
    r["owner_in_discards"] = (r["owner"] or "").lower() in disc_owners if r["owner"] else None
    r["agentRegistry_raw"] = tc("agentRegistry()")
    r["AGENT_ID_raw"] = tc("AGENT_ID()")
    r["balanceOf_user"] = dec(tc("balanceOf(address)", enc_addr(USER)))
    r["freeClaimed_user"] = dec(tc("freeClaimed(address)", enc_addr(USER)))
    # Sourcify ABI: mint fns + free views
    url = f"https://sourcify.dev/server/v2/contract/56/{A}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            j = json.load(resp)
        abi = j.get("abi") or []
        fns = [f.get("name", "") for f in abi if f.get("type") == "function"]
        r["sourcify"] = "verified"
        r["fns"] = fns
        r["mint_fns"] = [f for f in fns if f.lower().startswith("mint") or f in ("freeMint", "claimFree")]
        r["free_views"] = [f for f in fns if f.lower().startswith("free")]
        r["registry_in_abi_json"] = REG_BYTES in json.dumps(j).lower()
    except Exception as e:
        r["sourcify"] = f"error:{str(e)[:80]}"
    out[A] = r
    print(A, json.dumps(r), flush=True)

json.dump(out, open(BASE + "/run-2026-11-08-1901-scan-triage.json", "w"), indent=1)
print("DONE")
