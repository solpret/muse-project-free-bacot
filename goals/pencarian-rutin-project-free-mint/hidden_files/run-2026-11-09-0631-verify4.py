#!/usr/bin/env python3
"""Verify4 run 2026-11-09 0631 WIB — (1) AgenticGangsterNFT any-mint probe in
[130000000, 132151777] + binary search if found; (2) ShadowSquad contractURI +
tokenURI(0/1) reads (methods H/I for the website gate); (3) SakuraNFT
contractURI/tokenURI (gate record for the excluded item, cheap).
Read-only; writes run-2026-11-09-0631-verify4.json only.
"""
import json, subprocess, sys, datetime
sys.set_int_max_str_digits(100000)
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def post_rpc(ep, payload, timeout=40):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def block_ts(block):
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                "params": [hex(block), False]}, timeout=40)
            if isinstance(res, dict) and isinstance(res.get("result"), dict):
                return int(res["result"]["timestamp"], 16)
        except Exception:
            continue
    return None
def wib(ts):
    if ts is None: return None
    return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
def any_mint(addr, frm, to):
    try:
        res = ankr_post("ankr_getLogs", {"blockchain": "bsc", "address": addr,
            "fromBlock": str(frm), "toBlock": str(to),
            "topics": [TRANSFER, ZERO_TOPIC], "pageSize": 1000}, timeout=55)
        return len(res.get("result", {}).get("logs", [])) > 0, None
    except Exception as e:
        return None, str(e)[:150]
def first_mint(addr, lo, hi):
    ok, err = any_mint(addr, lo, hi)
    print(f"  probe [{lo},{hi}]: {ok} {err or ''}", flush=True)
    if ok is None: return {"first_mint_block": None, "error": err}
    if not ok: return {"first_mint_block": None, "no_mint_in_range": [lo, hi]}
    while lo < hi:
        mid = (lo + hi) // 2
        ok2, err2 = any_mint(addr, lo, mid)
        if ok2 is None:
            return {"first_mint_block": None, "error": err2, "lo": lo, "hi": hi}
        if ok2: hi = mid
        else: lo = mid + 1
    ts = block_ts(lo)
    return {"first_mint_block": lo, "timestamp": ts, "wib": wib(ts)}

def call_raw(addr, data):
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]}, timeout=40)
            if isinstance(res, dict) and isinstance(res.get("result"), str):
                return res["result"]
        except Exception:
            continue
    return None

def decode_string(hexstr):
    try:
        if not isinstance(hexstr, str) or len(hexstr) < 130: return None
        raw = bytes.fromhex(hexstr[2:])
        ln = int.from_bytes(raw[64:96], "big")
        if 0 < ln < 2000:
            return raw[96:96 + ln].decode("utf-8", "replace")
    except Exception:
        pass
    return None

out = {}
GANG = "0x0A2a07eF09DD7D83E2312476F0588aBaA3E34Ce3"
print("AgenticGangsterNFT any-mint [130000000,132151777]", flush=True)
out["gangster_first_mint_wide"] = first_mint(GANG, 130000000, 132151777)
print(" ->", out["gangster_first_mint_wide"], flush=True)

SHADOW = "0x0bc496BC51D14ae6C4A7003B05061323d4De9206"
SAKURA = "0xE56fD19a19E684b94db1Dd3c81896736E3631D47"
for name, addr in (("ShadowSquad", SHADOW), ("SakuraNFT", SAKURA)):
    d = {}
    r = call_raw(addr, sel("contractURI()"))
    d["contractURI_raw"] = (r or "")[:400]
    d["contractURI"] = decode_string(r) if r else None
    for tid in (0, 1):
        r = call_raw(addr, sel("tokenURI(uint256)") + enc_u(tid))
        d[f"tokenURI_{tid}_raw"] = (r or "")[:400]
        d[f"tokenURI_{tid}"] = decode_string(r) if r else None
    out[name] = d
    print(name, json.dumps(d)[:1500], flush=True)

# Sourcify metadata for ShadowSquad + SakuraNFT (method C: URLs in metadata)
import subprocess as sp
for name, addr in (("ShadowSquad", SHADOW), ("SakuraNFT", SAKURA)):
    try:
        r = sp.run(["curl", "-sL", "--max-time", "20",
                    f"https://sourcify.dev/server/v2/contracts/56/{addr}"],
                   capture_output=True, text=True, timeout=25).stdout
        j = json.loads(r)
        std = j.get("stdJson", {})
        meta = std.get("metadata", {}) if isinstance(std, dict) else {}
        out[name + "_sourcify"] = {
            "match": j.get("match"),
            "creationMatch": j.get("creationMatch"),
            "verifiedAt": j.get("verifiedAt"),
            "metadata_settings": str(meta.get("settings", {}))[:300],
            "sources": list((meta.get("sources") or {}).keys())[:10],
        }
        print(name, "sourcify:", out[name + "_sourcify"], flush=True)
    except Exception as e:
        out[name + "_sourcify"] = {"error": str(e)[:200]}
        print(name, "sourcify ERR", str(e)[:150], flush=True)

json.dump(out, open(f"{HF}/run-2026-11-09-0631-verify4.json", "w"), indent=1)
print("VERIFY4 DONE", flush=True)
