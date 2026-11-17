#!/usr/bin/env python3
"""Independent verification of Arachnoir early-lead claims (run 1301).
Read-only, dataseed curl transport (Ankr dead, 401)."""
import json, subprocess
from Crypto.Hash import keccak
ADDR = "0xe6ffadcfb8766e6199ec74f896da37f00b0f5bca"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v not in (None, "0x") else None
    except Exception: return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig: data = sel(sig) + enc(USER); key = base + "_user"
        else: data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post(ep, calls)
            if not isinstance(res, list) or len(res) != len(calls): continue
            return {k: (None if (isinstance(it, dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it, dict) else None)) for it, k in zip(res, keys)}
        except Exception: continue
    return None
def block():
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})
            return int(r["result"], 16)
        except Exception: continue
    return None
def get_logs(ep, payload, timeout=60):
    return post(ep, payload, timeout=timeout)
out = {"block": block()}
out["views"] = batch(ADDR, ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
    "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "AGENT_ID()", "agentId()", "owner()",
    "balanceOf(address)", "freeLeft(address)", "freeFor(address)", "freeUsed(address)",
    "contractURI()", "name()", "symbol()"])
# owner() returns address (not int) - re-read raw
def raw_call(addr, data):
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": addr, "data": data}, "latest"]})
            if isinstance(r, dict) and "result" in r: return r["result"]
        except Exception: continue
    return None
def addr_of(hexv):
    try: return "0x" + hexv[-40:] if hexv and len(hexv) >= 42 else hexv
    except Exception: return hexv
out["owner_raw"] = addr_of(raw_call(ADDR, sel("owner()")))
out["agentid_raw"] = addr_of(raw_call(ADDR, sel("AGENT_ID()")))
out["registry_match"] = (out["agentid_raw"] or "").lower() == REGISTRY.lower()
# same-owner discards check
try:
    disc = json.load(open("same-owner-discards.json"))
    lows = set()
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(k, str) and k.startswith("0x"): lows.add(k.lower())
                walk(v)
        elif isinstance(o, list):
            for x in o: walk(x)
        elif isinstance(o, str) and o.startswith("0x") and len(o) == 42:
            lows.add(o.lower())
    walk(disc)
    out["owner_in_discards"] = (out["owner_raw"] or "").lower() in lows
    out["discards_checked"] = len(lows)
except Exception as e:
    out["discards_error"] = str(e)
# first mint: dataseed eth_getLogs Transfer from zero, contract filter, window from ~132530000
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
head = out["block"]
logs_out = {"attempted": False, "first_block": None, "n_logs": None, "error": None}
if head:
    logs_out["attempted"] = True
    frm = head - 12000
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
               "params": [{"fromBlock": hex(frm), "toBlock": hex(head),
                           "address": ADDR, "topics": [TRANSFER, ZERO]}]}
    for ep in EPS:
        try:
            r = get_logs(ep, payload, timeout=60)
            res = r.get("result") if isinstance(r, dict) else None
            if isinstance(res, list):
                logs_out["n_logs"] = len(res)
                if res:
                    first = min(res, key=lambda l: int(l["blockNumber"], 16))
                    logs_out["first_block"] = int(first["blockNumber"], 16)
                    logs_out["first_tx"] = first.get("transactionHash")
                    blk = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                    "params": [hex(logs_out["first_block"]), False]})
                    ts = blk.get("result", {}).get("timestamp") if isinstance(blk, dict) else None
                    logs_out["first_block_ts"] = int(ts, 16) if ts else None
                break
            logs_out["error"] = str(r)[:300]
        except Exception as e:
            logs_out["error"] = str(e)[:300]
out["first_mint_logs"] = logs_out
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-09-1301-arachnoir.json", "w"), indent=1)
