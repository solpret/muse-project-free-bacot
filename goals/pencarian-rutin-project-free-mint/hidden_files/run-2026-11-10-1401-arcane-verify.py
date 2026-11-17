#!/usr/bin/env python3
"""Arcane Stones on-chain verification (read-only)."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x23f3De28E55C392F24A217B2B1602C90e0292f35"
MARKET = "0x85e624e0C10A04619351fc5277F1D81c80707517"
AGENT_TOKEN_ID = 107187496765866644729837695198686237165740365523485558112864918211974996443404
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def call(addr, data):
    for ep in EPS:
        try:
            out = subprocess.run(["curl", "-sL", "--max-time", "25", "-X", "POST", ep,
                                  "-H", "Content-Type: application/json",
                                  "-d", json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                                    "params": [{"to": addr, "data": data}, "latest"]})],
                                 capture_output=True, text=True, timeout=30).stdout
            r = json.loads(out).get("result")
            if r: return r
        except Exception: continue
    return None
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
out = {"address": ADDR}
out["totalSupply"] = to_int(call(ADDR, sel("totalSupply()")))
out["balanceOf_user"] = to_int(call(ADDR, sel("balanceOf(address)") + enc(USER)))
out["mintedByAgentId_user"] = to_int(call(ADDR, sel("mintedByAgentId(uint256)") + enc_u(AGENT_TOKEN_ID)))
out["owner"] = ("0x" + call(ADDR, sel("owner()"))[-40:]) if call(ADDR, sel("owner()")) else None
out["soldOutAt"] = to_int(call(ADDR, sel("soldOutAt()")))
out["revealDelay"] = to_int(call(ADDR, sel("revealDelay()")))
out["tokenURI_1"] = call(ADDR, sel("tokenURI(uint256)") + enc_u(1))
out["market_MIN_PRICE"] = to_int(call(MARKET, sel("MIN_PRICE()")))
# Sourcify
try:
    req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi",
                                 headers={"User-Agent": "free-bacot/1401"})
    with urllib.request.urlopen(req, timeout=30) as r: m = json.loads(r.read().decode())
    abi = m.get("abi", [])
    fns = [e.get("name", "") for e in abi if e.get("type") == "function"]
    blob = json.dumps(abi).lower()
    out["sourcify"] = m.get("match") or m.get("stdJson", {}).get("match") or "?"
    out["verifiedAt"] = m.get("verifiedAt")
    out["abi_shape"] = {"abi_len": len(abi),
                        "registry_ref": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f" in blob,
                        "agent_fns": [n for n in fns if "agent" in n.lower()],
                        "fns": fns}
except Exception as e:
    out["sourcify"] = f"ERR {type(e).__name__}: {str(e)[:100]}"
print(json.dumps(out, indent=1), flush=True)
disc = json.load(open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/same-owner-discards.json"))
disc_owners = {str(x.get("owner", "")).lower() for x in disc if isinstance(x, dict)}
print("owner_in_discards:", str(out.get("owner") or "").lower() in disc_owners)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-10-1401-arcane-verify.json", "w"), indent=1)
print("DONE")
