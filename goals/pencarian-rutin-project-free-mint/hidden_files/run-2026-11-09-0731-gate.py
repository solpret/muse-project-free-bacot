#!/usr/bin/env python3
"""Lean gate reads run 2026-11-09 0731 WIB — batched curl (like reread.py).
ShadowSquad + MONEY: contractURI/tokenURI raw (methods H/I) + LEAN free views.
FOUNT/Ringgent/MiraAgent/Glitchpilotfox: LEAN views + name/symbol.
Read-only; writes run-2026-11-09-0731-gate.json only."""
import json, sys, time, subprocess
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
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
        elif sig == "quote(address,uint256)":
            data = sel(sig) + enc(USER) + enc_u(1); key = "quote_user1"
        elif sig == "tokenURI(uint256)":
            data = sel(sig) + enc_u(1); key = "tokenURI_1_raw"
        elif sig == "tokenURI0(uint256)":
            data = sel("tokenURI(uint256)") + enc_u(0); key = "tokenURI_0_raw"
        elif sig == "contractURI()":
            data = sel(sig); key = "contractURI_raw"
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
                r = item.get("result") if isinstance(item, dict) else None
                if "error" in item if isinstance(item, dict) else False:
                    outd[key] = None
                elif key.endswith("_raw"):
                    outd[key] = r
                else:
                    outd[key] = to_int(r)
            return outd
        except Exception:
            continue
    return None

def abi_decode_str(raw):
    try:
        if not raw or len(raw) < 132: return None
        b = bytes.fromhex(raw[2:])
        ln = int.from_bytes(b[32:64], "big")
        if ln <= 0 or ln > 20000: return None
        return b[64:64+ln].decode("utf-8", "replace")
    except Exception:
        return None

def eth_call_str(addr, sig):
    data = sel(sig)
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            r = res.get("result") if isinstance(res, dict) else None
            if isinstance(r, str) and len(r) > 130:
                raw = bytes.fromhex(r[2:])
                ln = int.from_bytes(raw[64:96], "big")
                if 0 < ln < 100:
                    return raw[96:96 + ln].decode("utf-8", "replace")
        except Exception:
            continue
    return None

LEAN = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
        "FREE_SUPPLY()", "FREE_CAP()", "MAX_SUPPLY()", "mintOpen()",
        "balanceOf(address)", "freeClaimed(address)", "freeUsed(address)",
        "mintedBy(address)", "quote(address,uint256)"]
TARGETS = {
  "ShadowSquad": "0x0bc496BC51D14ae6C4A7003B05061323d4De9206",
  "MONEY": "0x085a493ac880188a69ad38449f505dA9E730C50B",
  "FOUNT": "0x4d146a58cB2D38ce91961358Dc090282e6ec7396",
  "Ringgent": "0xf1d1650dbfeb0fa8082481c8213accd59af3cf4a",
  "MiraAgent": "0xa545c7aa04885bbd9cf7ae450ae52c40dcb9e449",
  "Glitchpilotfox": "0xda552a0b709d09a2532689c6e39d981f527817b6",
}
out = {"run": "2026-11-09-0731-gate", "contracts": {}}

def work(item):
    name, addr = item
    d = {"address": addr}
    views = list(LEAN)
    if name in ("ShadowSquad", "MONEY"):
        views += ["contractURI()", "tokenURI(uint256)", "tokenURI0(uint256)"]
    r = raw_batch(addr, views)
    if r is None:
        d["_batch_ok"] = False
    else:
        d.update(r)
        d["_batch_ok"] = True
    for k in ("contractURI_raw", "tokenURI_1_raw", "tokenURI_0_raw"):
        if d.get(k):
            d[k.replace("_raw", "")] = abi_decode_str(d[k])
    d["name"] = eth_call_str(addr, "name()")
    d["symbol"] = eth_call_str(addr, "symbol()")
    print(name, {k: v for k, v in d.items() if v is not None and not str(v).startswith("0x0000")},
          f"({time.time()-T0:.0f}s)", flush=True)
    return name, d

with ThreadPoolExecutor(max_workers=6) as ex:
    for name, d in ex.map(work, TARGETS.items()):
        out["contracts"][name] = d

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{HF}/run-2026-11-09-0731-gate.json", "w"), indent=1)
print("GATE DONE", out["elapsed_s"], "s", flush=True)
