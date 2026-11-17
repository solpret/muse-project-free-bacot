#!/usr/bin/env python3
"""Triage SAKURA 0xfcfdc06c85877d3f2d316595882e1aa9e7f2eebc (Boltbook 0231 lead).
Read-only, batched eth_call via dataseed curl. Writes run-2026-11-10-0231-deltavane.json
"""
import json, subprocess, time
from Crypto.Hash import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0xfcfdc06c85877d3f2d316595882e1aa9e7f2eebc"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def post_rpc(ep, payload, timeout=30):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

VIEWS = ["name()", "symbol()", "totalSupply()", "totalMinted()", "freeClaimed()",
         "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()",
         "balanceOf(address)", "freeClaimed(address)", "mintedBy(address)",
         "freeFor(address)", "freeLeft()", "freeUsed(address)", "mintPrice()",
         "contractURI()", "remainingFree()", "costOf(address,uint256)"]
# costOf takes (address,uint256): encode manually below if needed

def batch_call(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if sig == "costOf(address,uint256)":
            data = sel(sig) + enc(USER) + "1".rjust(64, "0")
            key = "costOf_user_1"
        elif "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=30)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            outd = {}
            for item, key in zip(res, keys):
                if isinstance(item, dict) and "error" in item:
                    outd[key] = "ERR:" + str(item["error"].get("message", ""))[:50]
                elif isinstance(item, dict):
                    outd[key] = item.get("result")
                else:
                    outd[key] = None
            return outd
        except Exception:
            continue
    return None

def decode_str(raw):
    if not raw or raw == "0x" or (isinstance(raw, str) and raw.startswith("ERR")):
        return raw
    try:
        b = bytes.fromhex(raw[2:])
        if len(b) >= 64:
            ln = int.from_bytes(b[32:64], "big")
            if 0 < ln < 10000:
                return b[64:64+ln].decode("utf-8", "ignore")
        return raw
    except Exception:
        return raw

def main():
    t0 = time.time()
    raw = batch_call(ADDR, VIEWS)
    res = {"address": ADDR, "elapsed_s": round(time.time() - t0, 1)}
    if raw is None:
        res["batch"] = "ALL_ENDPOINTS_FAILED"
        print(json.dumps(res, indent=1)); return
    views = {}
    for k, v in raw.items():
        if k in ("name", "symbol", "contractURI"):
            views[k] = decode_str(v)
        elif isinstance(v, str) and v.startswith("ERR"):
            views[k] = v
        else:
            views[k] = to_int(v)
    res["views"] = views
    # eth_getCode for registry bytes
    code = None
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [ADDR, "latest"]}, timeout=30)
            if isinstance(r, dict) and "result" in r:
                code = r["result"]; break
        except Exception:
            continue
    res["code_len"] = len(code) - 2 if code else None
    res["registry_bytes"] = (REG in (code or "").lower()) if code else None
    # head block
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
            if isinstance(r, dict) and "result" in r:
                res["head_block"] = int(r["result"], 16); break
        except Exception:
            continue
    json.dump(res, open(HF + "run-2026-11-10-0231-deltavane.json", "w"), indent=1)
    print(json.dumps(res, indent=1))

if __name__ == "__main__":
    main()
