#!/usr/bin/env python3
"""Promotion-watch deep-check v3 (lean), run 2026-11-13 20:31 WIB. READ-ONLY.
Only essential views, one small batch per contract, single endpoint first.
No Ankr. No preview/mint/execution."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
OUT = BASE + "run-2026-11-13-2031-promowatch.json"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

def post(ep, payload, timeout=8):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def rpc(method, params, timeout=8, rounds=2):
    for _ in range(rounds):
        for ep in EPS:
            try:
                r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout)
                if isinstance(r, dict) and r.get("result") is not None:
                    return r["result"]
            except Exception:
                continue
    return None

def batch_read(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc_addr(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post(ep, calls, timeout=10)
            if isinstance(res, list) and len(res) == len(calls):
                return {k: (None if (isinstance(it, dict) and "error" in it)
                            else (to_int(it.get("result")) if isinstance(it, dict) else None))
                        for it, k in zip(res, keys)}
        except Exception:
            continue
    return {"error": "batch failed"}

def str_read(addr, sig):
    r = rpc("eth_call", [{"to": addr, "data": sel(sig)}, "latest"])
    if not r or r == "0x":
        return None
    try:
        b = bytes.fromhex(r[2:])
        if len(b) >= 64:
            off = int.from_bytes(b[:32], "big"); ln = int.from_bytes(b[32:64], "big")
            if 0 < ln < 20000 and off + 32 + ln <= len(b):
                return b[32+off:32+off+ln].decode("utf-8", errors="replace")
        return b.decode("utf-8", errors="replace").strip("\x00")
    except Exception:
        return r[:200]

res = json.load(open(OUT))
tip = res["block"]; spb = res["sec_per_block"]
now = int(time.time())

JOBS = {
 "Zero": ("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647",
         ["totalMinted()", "freeMinted()", "FREE_CAP()", "mintOpensAt()", "mintOpen()",
          "freeClaimed(address)", "balanceOf(address)", "mintsBy(address)",
          "holdsAgentId(address)", "price()", "owner()"]),
 "BUBB": ("0x0d72970046c056db90888351b739246f468bff0b",
         ["totalSupply()", "freeMinted()", "FREE_SUPPLY()", "FREE_CAP()",
          "freeRemaining()", "mintOpen()", "freeClaimed(address)",
          "freeAvailable(address)", "balanceOf(address)", "owner()"]),
 "AgentLabs": ("0x639329f5dc4317c44D9Fed961a1217ba845012F7",
         ["totalSpecimens()", "totalSupply()", "genesisOpen()", "currentExperiment()",
          "experimentEnd()", "isSealed()", "participants()", "priceFor(address)",
          "specimensOf(address)", "balanceOf(address)", "holdsAgentId(address)"]),
}
for name, (addr, views) in JOBS.items():
    e = {"address": addr, "views": batch_read(addr, views)}
    e["contractURI"] = str_read(addr, "contractURI()")
    res["reads"][name] = e
    json.dump(res, open(OUT, "w"), indent=1)
    print(name, {k: v for k, v in e["views"].items() if v is not None},
          "| contractURI:", str(e.get("contractURI"))[:150], flush=True)

# hist24h freeMinted for age bounds
b24 = res.get("block24h_ago") or (tip - int(86400 / spb))
if not res.get("block24h_ts"):
    blk = rpc("eth_getBlockByNumber", [hex(b24), False])
    res["block24h_ago"] = b24
    res["block24h_ts"] = int(blk["timestamp"], 16) if blk else None
    json.dump(res, open(OUT, "w"), indent=1)
print("block24h_ago", b24, "ts", res.get("block24h_ts"), flush=True)
hist = res.get("hist24h", {})
for name, addr in [("OLIVER", "0xad86e4d52e55709d1bda08f922853d4b109e0810"),
                   ("Pickgrid", "0x7f541bcc33abed0e64455565da723e949c6f76f0"),
                   ("RoyalRush", "0x2e34d33256C920C33b2a03FEC132A2c74061d5D3"),
                   ("BUBB", "0x0d72970046c056db90888351b739246f468bff0b"),
                   ("Zero", "0x89B340435e4fD27e00442f7F1b3a3b3244b4E647")]:
    fm = rpc("eth_call", [{"to": addr, "data": sel("freeMinted()")}, hex(b24)])
    ts = rpc("eth_call", [{"to": addr, "data": sel("totalSupply()")}, hex(b24)])
    hist[name] = {"freeMinted@24h": to_int(fm) if fm else ("RPC-FAIL" if fm is None else None),
                  "totalSupply@24h": to_int(ts) if ts else ("RPC-FAIL" if ts is None else None)}
    print("HIST24", name, hist[name], flush=True)
    res["hist24h"] = hist
    json.dump(res, open(OUT, "w"), indent=1)
res["elapsed_s"] = round(time.time() - t0, 1)
json.dump(res, open(OUT, "w"), indent=1)
print("ELAPSED", res["elapsed_s"])
