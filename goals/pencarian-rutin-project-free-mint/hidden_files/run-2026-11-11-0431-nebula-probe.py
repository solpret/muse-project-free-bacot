#!/usr/bin/env python3
"""Run 0431: probe NEBULA sale 0xf08ac9c91dcfc5b74eae6c87e744cfefe0d32a68. Read-only."""
import json, subprocess
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0xf08ac9c91dcfc5b74eae6c87e744cfefe0d32a68"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        return int(v, 16) if v not in (None, "0x") else None
    except Exception:
        return None
def dec_str(h):
    try:
        if not h or h == "0x": return None
        b = bytes.fromhex(h[2:])
        if len(b) < 96: return None
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", "replace")
    except Exception:
        return None
def dec_addr(h):
    try:
        return "0x" + h[-40:] if h and len(h) >= 42 else None
    except Exception:
        return None

def post(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

calls, keys = [], []
for sig in ["MAX_SHARES()", "totalShares()", "totalFreeShares()", "totalPaidShares()",
            "PRICE()", "TOKENS_PER_SHARE()", "LIQ_TOKENS_PER_SHARE()", "totalSupply()",
            "decimals()", "BASE_QUOTA()", "MAX_PER_TX()", "totalRaised()", "totalTreasuryBNB()"]:
    calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                  "params": [{"to": ADDR, "data": sel(sig)}, "latest"]}); keys.append(("uint", sig))
for sig in ["agentIdRegistry()", "treasury()"]:
    calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                  "params": [{"to": ADDR, "data": sel(sig)}, "latest"]}); keys.append(("addr", sig))
for sig in ["name()", "symbol()"]:
    calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                  "params": [{"to": ADDR, "data": sel(sig)}, "latest"]}); keys.append(("str", sig))
for sig in ["freeUsed(address)", "sharesOf(address)", "quotaOf(address)", "isAgent(address)", "balanceOf(address)"]:
    calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                  "params": [{"to": ADDR, "data": sel(sig) + enc(USER)}, "latest"]}); keys.append(("uint_user", sig))
# quote(user, 1)
calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
              "params": [{"to": ADDR, "data": sel("quote(address,uint256)") + enc(USER) + "0"*63 + "1"}, "latest"]}); keys.append(("quote", "quote(user,1)"))
calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_blockNumber", "params": []}); keys.append(("block", "eth_blockNumber"))

out = {"address": ADDR}
for ep in EPS:
    try:
        r = post(ep, calls, timeout=25)
        if isinstance(r, list) and len(r) == len(calls):
            for (kind, sig), item in zip(keys, r):
                res = item.get("result") if isinstance(item, dict) else None
                if kind in ("uint", "uint_user"):
                    out[sig] = to_int(res)
                elif kind == "addr":
                    out[sig] = dec_addr(res)
                elif kind == "str":
                    out[sig] = dec_str(res)
                elif kind == "quote":
                    if res and res != "0x" and len(res) >= 130:
                        b = bytes.fromhex(res[2:])
                        out[sig] = [int.from_bytes(b[0:32], "big"), int.from_bytes(b[32:64], "big")]
                    else:
                        out[sig] = None
                elif kind == "block":
                    out["block"] = int(res, 16) if res else None
            print("EP OK", ep, flush=True)
            break
        else:
            print("EP BAD", ep, str(r)[:200], flush=True)
    except Exception as e:
        print("EP ERR", ep, e, flush=True)
print(json.dumps(out, indent=1))
json.dump(out, open(BASE + "run-2026-11-11-0431-nebula-probe.json", "w"), indent=1)
