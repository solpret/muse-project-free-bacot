#!/usr/bin/env python3
"""Run 0431: probe new S1 contract 0xD265a929... Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0xD265a929D0E50bD5ee4675e4E97F38D8380802E2"
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

VIEWS_UINT = ["totalMinted()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()",
              "freePhaseStart()", "priorityMinted()", "PRIORITY_CAP()",
              "PRIORITY_WINDOW()", "paidPrice()", "DEFAULT_PAID_PRICE()",
              "EVOLVE_COST_TO_BUDDY()", "EVOLVE_COST_TO_GUARDIAN()",
              "priorityActive()", "MAX_STAGE()"]
VIEWS_ADDR = ["registry()", "agtc()", "palsToken()", "owner()"]
VIEWS_STR = ["name()", "symbol()", "baseURI()"]
VIEWS_USER_UINT = ["balanceOf(address)", "hasFreeMinted(address)"]

def post(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

calls, keys = [], []
for sig in VIEWS_UINT:
    calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                  "params": [{"to": ADDR, "data": sel(sig)}, "latest"]}); keys.append(("uint", sig))
for sig in VIEWS_ADDR:
    calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                  "params": [{"to": ADDR, "data": sel(sig)}, "latest"]}); keys.append(("addr", sig))
for sig in VIEWS_STR:
    calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                  "params": [{"to": ADDR, "data": sel(sig)}, "latest"]}); keys.append(("str", sig))
for sig in VIEWS_USER_UINT:
    calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                  "params": [{"to": ADDR, "data": sel(sig) + enc(USER)}, "latest"]}); keys.append(("uint_user", sig))
# tokenURI(1)
calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
              "params": [{"to": ADDR, "data": sel("tokenURI(uint256)") + "0"*63 + "1"}, "latest"]}); keys.append(("str", "tokenURI(1)"))
calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_blockNumber", "params": []}); keys.append(("block", "eth_blockNumber"))

out = {"address": ADDR}
for ep in EPS:
    try:
        r = post(ep, calls, timeout=25)
        if isinstance(r, list) and len(r) == len(calls):
            for (kind, sig), item in zip(keys, r):
                res = item.get("result") if isinstance(item, dict) else None
                if kind == "uint" or kind == "uint_user":
                    out[sig] = to_int(res)
                elif kind == "addr":
                    out[sig] = dec_addr(res)
                elif kind == "str":
                    out[sig] = dec_str(res)
                elif kind == "block":
                    out["block"] = int(res, 16) if res else None
            print("EP OK", ep, flush=True)
            break
        else:
            print("EP BAD", ep, str(r)[:200], flush=True)
    except Exception as e:
        print("EP ERR", ep, e, flush=True)
print(json.dumps(out, indent=1))
json.dump(out, open(BASE + "run-2026-11-11-0431-d265-probe.json", "w"), indent=1)
