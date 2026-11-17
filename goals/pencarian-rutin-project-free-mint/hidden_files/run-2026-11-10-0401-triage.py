#!/usr/bin/env python3
"""Triage run 0401 (2026-11-10): ZENSAI twins (new Boltbook post lloyd.ai
/p/F58f-p_bLkAu ~04:25 WIB, 146/3,333 each) + Roguefall RFALL 0x5fe03829
(hot-leg 0404 Boltbook-new, S1=True by ABI names; seen before 2026-11-05
06:24 WIB with freeMinted 4 - age check pending).
Read-only; never previews/mints. Uses curl transport (25s/call) like reread.
Writes run-2026-11-10-0401-triage.json.
"""
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
def enc_u(n): return str(n).rjust(64, "0")
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
            return r.get("result") or ""
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

def raw_call(addr, data, frm=None):
    # single eth_call; returns (result_hex_or_None, error_dict_or_None)
    for ep in EPS:
        try:
            params = {"to": addr, "data": data}
            if frm: params["from"] = frm
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [params, "latest"]}, timeout=25)
            if "error" in r:
                return None, r["error"]
            return r.get("result"), None
        except Exception as e:
            continue
    return None, {"transport": "all-endpoints-failed"}

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

VIEWS_COMMON = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
         "freeClaimed(address)", "mintedBy(address)", "owner()",
         "AGENT_ID()", "agentId()", "agentRegistry()", "freeLeft(address)",
         "freeFor(address,uint256)", "quote(address,uint256)", "mintPrice()",
         "PRICE()", "price()"]
VIEWS_RFALL = ["totalSupply()", "freeMinted()", "FREE_CAP()", "MAX_SUPPLY()",
         "maxSupply()", "paidMinted()", "PRICE()", "price()", "basePrice()",
         "REGISTRY()", "canFreeMint(address)", "claimedFree(address)",
         "balanceOf(address)", "owner()", "quote(address,uint256)",
         "mintPrice()", "freeClaimed(address)", "mintedBy(address)"]

out = {"block": get_block(), "triage": {}}
print("BLOCK", out["block"], flush=True)

TARGETS = [
    ("ZENSAI-1", "0x6e9259bda18f42abceb4bec794ac3355004f743f", VIEWS_COMMON),
    ("ZENSAI-2", "0xf9e04cc1b4dc91b3cfd5a30d9717d634acf9c3e9", VIEWS_COMMON),
    ("Roguefall", "0x5fe03829a2f94a8ba3906459258b1305f0e68934", VIEWS_RFALL),
]
for label, addr, views in TARGETS:
    t = time.time()
    code = get_code(addr)
    code_len = (len(code) - 2) // 2 if code and code.startswith("0x") else 0
    reg_bytes = REGISTRY in (code or "").lower()
    status, abi = sourcify_abi(addr)
    funcs = []
    if isinstance(abi, list):
        funcs = sorted({f"{it.get('name','')}({','.join(i.get('type','') for i in it.get('inputs',[]))})"
                        for it in abi if it.get("type") == "function"})
    v = raw_batch(addr, views)
    name = get_string(addr, "name()")
    symbol = get_string(addr, "symbol()")
    d = {"address": addr, "sourcify": status, "code_len": code_len,
         "registry_bytes": reg_bytes, "name": name, "symbol": symbol,
         "functions": funcs, "views": v, "elapsed": round(time.time() - t, 1)}
    # REGISTRY() value as address (Roguefall: confirms agent-shape only if == official)
    if label == "Roguefall":
        res, err = raw_call(addr, sel("REGISTRY()"))
        d["REGISTRY_value"] = res
        d["REGISTRY_error"] = err
        # canFreeMint(user) raw (bool is 0/1 int in views already)
    if label.startswith("ZENSAI"):
        # claimed free-mint selector probe: 0x67f68fac(uint256,uint256) with (1,1), from user, value 0.
        # Static eth_call simulation only - no state change, no preview, no mint.
        data = "0x67f68fac" + enc_u(1) + enc_u(1)
        res, err = raw_call(addr, data, frm=USER)
        d["selector_probe_67f68fac_1_1"] = {"result": res, "error": err}
    out["triage"][label] = d
    print(label, addr, "sourcify=", status, "code_len=", code_len,
          "reg_bytes=", reg_bytes, "name=", name, "sym=", symbol, flush=True)
    print("  views:", json.dumps(v), flush=True)
    print("  funcs:", funcs, flush=True)
    if label == "Roguefall":
        print("  REGISTRY_value:", d.get("REGISTRY_value"), "err:", d.get("REGISTRY_error"), flush=True)
    if label.startswith("ZENSAI"):
        print("  probe:", json.dumps(d["selector_probe_67f68fac_1_1"]), flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-10-0401-triage.json", "w"), indent=1)
print(f"TRIAGE DONE in {time.time()-T0:.1f}s", flush=True)
