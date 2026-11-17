#!/usr/bin/env python3
"""Probe new Boltbook leads for run 2026-11-14 00:01 WIB. Read-only."""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
t0 = time.time()
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42: d += enc_addr(a)
        else: d += enc_u(int(a))
    return d
def raw_batch(addr, views):
    calls, keys = [], []
    for i, (key, sig, args) in enumerate(views):
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls): continue
            out = {}
            for it, key in zip(res, keys):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    out[key] = None
                else:
                    r = it["result"]
                    out[key] = to_int(r[:66]) if len(r) >= 66 else r
            return out
        except Exception:
            continue
    return None
def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16)
        except Exception:
            continue
    return None
def sourcify(addr):
    try:
        req = urllib.request.Request("https://sourcify.dev/server/v2/contracts/56/" + addr,
                                     headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=20) as r:
            j = json.load(r)
        std = j.get("stdJson", {})
        srcs = std.get("sources", {})
        txt = json.dumps(std)[:6000]
        fns = []
        try:
            abi = j.get("creationMatch", {}) and None
            out = j.get("runtimeMatch", {})
        except Exception:
            pass
        # collect function names from ABI if present
        abi = None
        try:
            abi = j["stdJson"]["output"]["contracts"]
        except Exception:
            abi = None
        return {"match": j.get("match"), "status": j.get("status"),
                "has_stdjson": bool(std), "stdjson_len": len(txt)}
    except Exception as e:
        return {"error": str(e)[:200]}
U = [USER]
ITEMS = {
 "PulseDistrict": ("0xf6cc6364c0d7764a5a751c08314db181df5b825c", [
    ("name","name()",[]),("symbol","symbol()",[]),
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("FREE_MAX","FREE_MAX()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("agentId","agentId()",[]),
    ("freeClaimed_user","freeClaimed(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "FossilDrawer": ("0x747e7ca26921bc1bde97cb27b445983c8269bb72", [
    ("name","name()",[]),("symbol","symbol()",[]),
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("FREE_MAX","FREE_MAX()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("agentId","agentId()",[]),
    ("freeClaimed_user","freeClaimed(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "DreamCompile": ("0x3964bfc3354c0d18886dcad52abc55c689e6a1d4", [
    ("name","name()",[]),("symbol","symbol()",[]),
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("FREE_MAX","FREE_MAX()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("agentId","agentId()",[]),
    ("freeClaimed_user","freeClaimed(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "VoxelSector": ("0x2c93e68462f0d20ccc54a19d39d9ed25d9f3b9be", [
    ("name","name()",[]),("symbol","symbol()",[]),
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("FREE_MAX","FREE_MAX()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("agentId","agentId()",[]),
    ("freeClaimed_user","freeClaimed(address)",U),("balanceOf_user","balanceOf(address)",U)]),
}
out = {}
for name, (addr, views) in ITEMS.items():
    r = raw_batch(addr, views)
    s = sourcify(addr)
    out[name] = {"address": addr, "views": r, "sourcify": s}
    print(name, json.dumps(r), "| sourcify:", json.dumps(s)[:200], flush=True)
blk = block_number()
res = {"started_wib": "2026-11-14T00:01+07:00", "reads": out, "block": blk,
       "elapsed_s": round(time.time() - t0, 1)}
json.dump(res, open(BASE + "run-2026-11-14-0001-probe-new.json", "w"), indent=1)
print("DONE block", blk, "elapsed", round(time.time() - t0, 1))
