#!/usr/bin/env python3
"""Verify run 2026-11-09 0531 WIB — two S1-shape hits:
 Compasyn 0xcd1bb8013e924e26ed4131a69304f2969c4f8d28 (Boltbook, NFT?)
 0x2CCb3fA957E69AbD46A6651CC1444EF2Ea9bd591 (Sourcify feed, verified 22:30:20Z)
Read-only on-chain view reads (curl transport, dataseed) + Sourcify metadata.
Writes run-2026-11-09-0531-verify.json.
"""
import json, subprocess, time, sys
sys.set_int_max_str_digits(100000)
from Crypto.Hash import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
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

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        elif "(uint256)" in sig:
            data = sel(sig) + "0" * 63 + "1"; key = base + "_1"
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
            outd["_raw"] = {k: (item.get("result") if isinstance(item, dict) else None) for item, k in zip(res, keys)}
            return outd
        except Exception:
            continue
    return None

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

VIEWS = ["name()", "symbol()", "totalSupply()", "totalMinted()", "freeClaimed()",
         "freeMinted()", "freeLeft()", "freeFor()", "FREE_SUPPLY()", "MAX_SUPPLY()",
         "mintOpen()", "balanceOf(address)", "freeClaimed(address)", "freeUsed(address)",
         "owner()", "agentIdRegistry()", "AGENT_ID()", "START_TIME()", "mintEnd()",
         "quote(address,uint256)", "tokenURI(uint256)", "contractURI()"]
# quote(address,uint256): encode USER + 1
def quote_call(addr):
    data = sel("quote(address,uint256)") + enc(USER) + "0" * 63 + "1"
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            if isinstance(res, dict) and "result" in res:
                return to_int(res.get("result")), res.get("result")
        except Exception:
            continue
    return None, None

def sourcify_meta(addr):
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "20",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata"],
                           capture_output=True, text=True, timeout=25)
        d = json.loads(r.stdout)
        abi = d.get("abi") or []
        fns = sorted({e.get("name") for e in abi if isinstance(e, dict) and e.get("type") == "function"})
        meta = d.get("metadata") or {}
        return {"match": d.get("match"), "verifiedAt": d.get("verifiedAt"),
                "functions": fns, "metadata_sources": list((meta.get("sources") or {}).keys())[:10],
                "compiler": (meta.get("compiler") or {}).get("version")}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:200]}"}

def decode_str(hexv):
    try:
        if not hexv or hexv == "0x":
            return None
        b = bytes.fromhex(hexv[2:])
        if len(b) < 96:
            return None
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96 + ln].decode("utf-8", errors="replace")
    except Exception:
        return None

out = {"run": "2026-11-09-0531", "block": get_block(), "contracts": {}}
for addr in ["0xcd1bb8013e924e26ed4131a69304f2969c4f8d28",
             "0x2CCb3fA957E69AbD46A6651CC1444EF2Ea9bd591"]:
    print("VERIFY", addr, flush=True)
    d = {"address": addr}
    got = raw_batch(addr, VIEWS)
    if got is None:
        d["read_error"] = "all endpoints failed"
    else:
        for k, v in got.items():
            if k == "_raw":
                d["_raw"] = v
            else:
                d[k] = v
        raw = got.get("_raw", {})
        for k in ("name", "symbol", "tokenURI_1", "contractURI"):
            if raw.get(k):
                d[k + "_str"] = decode_str(raw[k])
    q, qraw = quote_call(addr)
    d["quote_user_1"] = q
    d["quote_user_1_raw"] = qraw
    d["sourcify"] = sourcify_meta(addr)
    out["contracts"][addr] = d
    print(json.dumps({k: v for k, v in d.items() if k not in ("_raw", "sourcify")}, default=str), flush=True)
    print("sourcify:", json.dumps(d["sourcify"], default=str)[:600], flush=True)

json.dump(out, open(f"{HF}/run-2026-11-09-0531-verify.json", "w"), indent=1)
print("VERIFY DONE block", out["block"])
