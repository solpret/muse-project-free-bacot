#!/usr/bin/env python3
"""Verify run 2026-11-12 08:01 WIB — new S1/early-shape contract
0xb5A132A2Efd8351DA2c04e38E2568dd8DC5b1c1a (src/AirdropCnNFT.sol).
Read-only curl transport. Writes run-2026-11-12-0801-verify.json."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-12 08:01 WIB"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0xb5A132A2Efd8351DA2c04e38E2568dd8DC5b1c1a"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

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

VIEWS = ["name()", "symbol()", "totalMinted()", "freeMinted()", "FREE_CAP()",
         "MAX_SUPPLY()", "MAX_PER_WALLET()", "mintOpen()", "mintOpensAt()",
         "price()", "nextTokenId()", "agentIdRegistry()", "treasury()",
         "owner()", "freeClaimed(address)", "mintsBy(address)", "balanceOf(address)"]

def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            outd = {}
            for item, key in zip(res, keys):
                outd[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return outd
        except Exception:
            continue
    return None

def raw_str(addr, sig):
    data = sel(sig)
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            r = res.get("result")
            if r and r != "0x":
                b = bytes.fromhex(r[2:])
                # string ABI: offset(32) + len(32) + data
                if len(b) >= 64:
                    ln = int.from_bytes(b[32:64], "big")
                    return b[64:64+ln].decode(errors="replace")
            return None
        except Exception:
            continue
    return None

out = {"started_wib": TS, "address": ADDR, "block": get_block()}
print("BLOCK", out["block"], flush=True)
got = raw_batch(ADDR, VIEWS)
out["views"] = got if got is not None else {"_batch_fail": True}
out["name_str"] = raw_str(ADDR, "name()")
out["symbol_str"] = raw_str(ADDR, "symbol()")
# tokenURI(1) if any minted
tm = (got or {}).get("totalMinted")
if tm and tm > 0:
    out["tokenURI_1"] = raw_str(ADDR, "tokenURI(uint256)") if False else None
    # tokenURI takes uint256 arg: build manually
    data = sel("tokenURI(uint256)") + "0000000000000000000000000000000000000000000000000000000000000001"
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": ADDR, "data": data}, "latest"]}, timeout=25)
            r = res.get("result")
            if r and r != "0x":
                b = bytes.fromhex(r[2:])
                if len(b) >= 64:
                    ln = int.from_bytes(b[32:64], "big")
                    out["tokenURI_1"] = b[64:64+ln].decode(errors="replace")
            break
        except Exception:
            continue
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + "/run-2026-11-12-0801-verify.json", "w"), indent=1)
print(json.dumps(out, indent=1))
