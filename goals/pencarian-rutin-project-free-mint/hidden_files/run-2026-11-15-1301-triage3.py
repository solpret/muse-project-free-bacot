#!/usr/bin/env python3
"""Deep triage round 3 run 1301: first-mint via eth_getLogs bisection + PICK modes + bytecode registry grep. Read-only."""
import json, urllib.request, datetime
from Crypto.Hash import keccak

RPC = "https://bsc-dataseed.binance.org/"
ZERO_TOPIC = "0x" + "0" * 64
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]

def post(payload, timeout=60):
    req = urllib.request.Request(RPC, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

def call(to, data, block="latest"):
    r = post({"jsonrpc": "2.0", "id": 0, "method": "eth_call",
              "params": [{"to": to, "data": data}, block]})
    if "error" in r: return None
    return r.get("result")

def dec(h):
    if not h: return None
    try: return int(h, 16)
    except Exception: return None

head = int(post({"jsonrpc": "2.0", "id": 0, "method": "eth_blockNumber", "params": []})["result"], 16)
print("head:", head, "now WIB:", datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M"))

def has_mint_in_range(addr, lo, hi):
    r = post({"jsonrpc": "2.0", "id": 0, "method": "eth_getLogs",
              "params": [{"fromBlock": hex(lo), "toBlock": hex(hi), "address": addr,
                          "topics": [TRANSFER, ZERO_TOPIC]}]}, timeout=90)
    if "error" in r:
        return ("error", str(r["error"])[:150])
    logs = r.get("result", [])
    return ("ok", logs)

def first_mint(addr, label):
    # bisect: find earliest block in [head-200000, head] with a mint Transfer
    lo, hi = head - 200000, head
    status, res = has_mint_in_range(addr, lo, hi)
    print(label, "window check:", status, len(res) if status == "ok" else res)
    if status != "ok" or not res:
        return {"first_mint": None, "note": "no mint in last 200k blocks" if status == "ok" else f"logs error: {res}"}
    # bisect on existence
    while hi - lo > 1:
        mid = (lo + hi) // 2
        s, r = has_mint_in_range(addr, lo, mid)
        if s != "ok":
            return {"first_mint": None, "note": f"bisect logs error at [{lo},{mid}]: {r}"}
        if r: hi = mid
        else: lo = mid
    # earliest log in [hi-2000, hi]
    s, r = has_mint_in_range(addr, max(hi - 2000, 0), hi)
    if s == "ok" and r:
        blk = int(r[0]["blockNumber"], 16)
        b = post({"jsonrpc": "2.0", "id": 0, "method": "eth_getBlockByNumber",
                  "params": [hex(blk), False]})
        ts = int(b["result"]["timestamp"], 16)
        dt = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7)))
        return {"first_mint_block": blk, "first_mint_wib": dt.strftime("%Y-%m-%d %H:%M:%S WIB"),
                "age_hours_at_run": round((datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))) - dt).total_seconds() / 3600, 2)}
    return {"first_mint": None, "note": "bisect converged but no log re-read"}

out = {}
for label, addr in [("PICK", "0x2296367f74b2ec266cf4667d98501ae7110f5a58"),
                    ("AZEN", "0x699b6397986cc6c444069efe692023b1253dc26d"),
                    ("GearMachine", "0x391a13af7819e36a84f16754c133ca39d08d273d")]:
    out[label] = first_mint(addr, label)
    print(label, json.dumps(out[label]))

# PICK mode constants
for c in ["MODE_ALL_FREE()", "MODE_ALL_PAID()", "MODE_FIRST_FREE()", "MODE_HASH_FREE()", "agentIdRequired()"]:
    print("PICK", c, dec(call("0x2296367f74b2ec266cf4667d98501ae7110f5a58", sel(c))))

# bytecode registry grep
REG = bytes.fromhex("60B9262456dE011F7d15a54CdD8c48bAaa8B022F")
for label, addr in [("PICK", "0x2296367f74b2ec266cf4667d98501ae7110f5a58"),
                    ("AZEN", "0x699b6397986cc6c444069efe692023b1253dc26d"),
                    ("GearMachine", "0x391a13af7819e36a84f16754c133ca39d08d273d")]:
    r = post({"jsonrpc": "2.0", "id": 0, "method": "eth_getCode", "params": [addr, "latest"]})
    code = bytes.fromhex((r.get("result") or "0x")[2:])
    print(label, "bytecode has registry addr:", REG.lower() in code.lower(), "code bytes:", len(code))

json.dump(out, open("run-2026-11-15-1301-triage3.json", "w"), indent=1)
