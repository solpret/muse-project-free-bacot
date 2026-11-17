#!/usr/bin/env python3
"""Run 1001: verify new Boltbook/hot-leg discoveries on-chain (read-only).
Contracts: Iron Bloom, HELM, Hivebyte, MWORKS, 2 hot-leg-1024 addrs.
Writes run-2026-11-10-1001-newdisc.json. Never writes snapshot."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
TARGETS = {
    "Iron Bloom": "0xb8c7658f6fc4d0d91da2dd6faeaf0328ff57ccaf",
    "HELM": "0xe0df49c281b8584f03ed21beac0e5002ec4a0599",
    "Hivebyte": "0xae9d85e78a609f185b4682d87da12d13b03cf8d8",
    "MWORKS": "0xCc844748C64b9b8e45aC4504553C9757c7CDB7E0",
    "hotleg1024-A": "0x60f7212010600bcbebbfe2a558237004c7f401fd",
    "hotleg1024-B": "0xbf87e6fe445e235699103df56ef8d40a88b9e8ba",
}
INT_VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
             "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
             "freeClaimed(address)", "START_TIME()", "startTime()", "mintPrice()"]
STR_VIEWS = ["name()", "symbol()", "contractURI()"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None
def dec_str(v):
    try:
        if v is None or v == "0x": return None
        b = bytes.fromhex(v[2:])
        # abi string: offset(32) + len(32) + data
        if len(b) >= 64:
            ln = int.from_bytes(b[32:64], "big")
            s = b[64:64+ln].decode("utf-8", "replace")
            return s
        return b.decode("utf-8", "replace")
    except Exception as e: return f"DECODE_ERR {e}"

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

def read_contract(addr):
    calls, keys, kinds = [], [], []
    for i, sig in enumerate(INT_VIEWS):
        base = sig.split("(")[0]
        data = sel(sig) + (enc(USER) if "(address)" in sig else "")
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(base + ("_user" if "(address)" in sig else "")); kinds.append("int")
    for j, sig in enumerate(STR_VIEWS):
        base = sig.split("(")[0]
        calls.append({"jsonrpc": "2.0", "id": len(INT_VIEWS) + j + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": sel(sig)}, "latest"]})
        keys.append(base); kinds.append("str")
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            outd = {}
            for item, key, kind in zip(res, keys, kinds):
                if not isinstance(item, dict) or "error" in item:
                    outd[key] = None
                elif kind == "int":
                    outd[key] = to_int(item.get("result"))
                else:
                    outd[key] = dec_str(item.get("result"))
            outd["_ep"] = ep
            return outd
        except Exception:
            continue
    return {"_ep": None, "_error": "all endpoints failed"}

out = {"block": get_block(), "run": "2026-11-10 10:01 WIB", "reads": {}}
print("BLOCK", out["block"], flush=True)
for name, addr in TARGETS.items():
    t0 = time.time()
    r = read_contract(addr)
    out["reads"][name] = {"address": addr, **r}
    print(name, addr, "->", {k: v for k, v in r.items() if k != "_ep"},
          f"({time.time()-t0:.1f}s)", flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-10-1001-newdisc.json", "w"), indent=1)
print("WROTE run-2026-11-10-1001-newdisc.json")
