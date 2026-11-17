#!/usr/bin/env python3
"""Triage run 0301 (2026-11-10): Adventure Agent AI 0x7635ef16 (new Boltbook
post, nanomind.ai) + HAMMER 0xa9e6f0e6 re-check (paid-only per run 0231).
Read-only; never previews/mints. Uses curl transport (25s/call) like reread.
Writes run-2026-11-10-0301-triage.json."""
import json, subprocess, time, urllib.request, urllib.error
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "60b9262456de011f7d15a54cdd8c48baa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
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

def get_code(addr):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [addr, "latest"]}, timeout=25)
            code = r.get("result") or ""
            return code
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

def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        elif "(address,uint256)" in sig:
            data = sel(sig) + enc(USER) + "0" * 63 + "1"; key = base + "_user1"
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
            return outd
        except Exception:
            continue
    return None

def sourcify_abi(address):
    url = f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"
    for i in range(3):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode())
                return ("verified", data.get("abi"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ("not_verified", None)
            time.sleep(3)
        except Exception:
            time.sleep(3)
    return ("error", None)

def get_string(addr, sig):
    # name()/symbol() return dynamic string; decode manually
    for ep in EPS:
        try:
            data = sel(sig)
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            res = r.get("result")
            if not res or res == "0x" or "error" in r:
                continue
            b = bytes.fromhex(res[2:])
            if len(b) >= 96:
                off = int.from_bytes(b[0:32], "big")
                ln = int.from_bytes(b[off:off+32], "big")
                return b[off+32:off+32+ln].decode("utf-8", "ignore")
            return None
        except Exception:
            continue
    return None

VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
         "freeClaimed(address)", "mintedBy(address)", "owner()",
         "AGENT_ID()", "agentId()", "agentRegistry()", "freeLeft(address)",
         "freeFor(address,uint256)", "quote(address,uint256)", "mintPrice()",
         "PRICE()", "price()"]

out = {"block": get_block(), "triage": {}}
print("BLOCK", out["block"], flush=True)

for label, addr in [("AdventureAgent", "0x7635ef16370ef490298649a188c9205d1d7fda67"),
                    ("HAMMER", "0xa9e6f0e6935662aa30f578884662738f05d1c1e4")]:
    t = time.time()
    code = get_code(addr)
    code_len = (len(code) - 2) // 2 if code and code.startswith("0x") else 0
    reg_bytes = REGISTRY in (code or "").lower()
    status, abi = sourcify_abi(addr)
    funcs = []
    if isinstance(abi, list):
        funcs = sorted({f"{it.get('name','')}({','.join(i.get('type','') for i in it.get('inputs',[]))})"
                        for it in abi if it.get("type") == "function"})
    views = raw_batch(addr, VIEWS)
    name = get_string(addr, "name()")
    symbol = get_string(addr, "symbol()")
    d = {"address": addr, "sourcify": status, "code_len": code_len,
         "registry_bytes": reg_bytes, "name": name, "symbol": symbol,
         "functions": funcs, "views": views, "elapsed": round(time.time() - t, 1)}
    out["triage"][label] = d
    print(label, addr, "sourcify=", status, "code_len=", code_len,
          "reg_bytes=", reg_bytes, "name=", name, "sym=", symbol, flush=True)
    print("  views:", json.dumps(views), flush=True)
    print("  funcs:", funcs, flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-10-0301-triage.json", "w"), indent=1)
print(f"TRIAGE DONE in {time.time()-T0:.1f}s", flush=True)
