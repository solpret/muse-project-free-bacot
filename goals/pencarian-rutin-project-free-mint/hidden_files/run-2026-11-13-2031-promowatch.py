#!/usr/bin/env python3
"""Promotion-watch deep-check v2, run 2026-11-13 20:31 WIB. READ-ONLY.
Lean curl batches (chunk 20, timeout 10s, 2 endpoints), incremental writes.
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
def enc_uint(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

def post(ep, payload, timeout=10):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def rpc(method, params, timeout=10, rounds=3):
    for _ in range(rounds):
        for ep in EPS:
            try:
                r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout)
                if isinstance(r, dict) and r.get("result") is not None:
                    return r["result"]
            except Exception:
                continue
    return None

VIEWS = [
 "totalSupply()", "totalMinted()", "freeMinted()", "freeClaimed()",
 "FREE_SUPPLY()", "FREE_MAX()", "FREE_CAP()", "FREE_SLOTS()", "MAX_SUPPLY()",
 "MAX_PER_WALLET()", "mintOpen()", "freeRemaining()", "freeLeft()",
 "paidMinted()", "mintOpensAt()", "saleStart()", "mintStart()", "START_TIME()",
 "startTime()", "openedAt()", "mintOpenedAt()", "genesisOpen()", "genesisStart()",
 "totalSpecimens()", "currentExperiment()", "experimentEnd()", "isSealed()",
 "participants()", "price()", "mintPrice()", "PAID_PRICE()", "launched()",
 "owner()", "agentRegistry()", "AGENT_ID_REGISTRY()",
 "freeClaimed(address)", "freeClaimedByAgent(address)", "freeAvailable(address)",
 "freeLeftFor(address)", "freeFor(address)", "freeUsed(address)",
 "mintedBy(address)", "freeMintedBy(address)", "mintsBy(address)",
 "balanceOf(address)", "holdsAgentId(address)", "specimensOf(address)",
 "participantsOf(address)", "priceFor(address)", "quote(address,uint256)",
]
TARGETS = {
 "OLIVER": "0xad86e4d52e55709d1bda08f922853d4b109e0810",
 "Pickgrid": "0x7f541bcc33abed0e64455565da723e949c6f76f0",
 "RoyalRush": "0x2e34d33256C920C33b2a03FEC132A2c74061d5D3",
 "Zero": "0x89B340435e4fD27e00442f7F1b3a3b3244b4E647",
 "BUBB": "0x0d72970046c056db90888351b739246f468bff0b",
 "AgentLabs": "0x639329f5dc4317c44D9Fed961a1217ba845012F7",
}

def batch_read(addr):
    out = {}
    for ci in range(0, len(VIEWS), 20):
        chunk = VIEWS[ci:ci+20]
        calls, keys = [], []
        for i, sig in enumerate(chunk):
            base = sig.split("(")[0]
            if "(address)" in sig:
                data = sel(sig) + enc_addr(USER); key = base + "_user"
            elif sig == "quote(address,uint256)":
                data = sel(sig) + enc_addr(USER) + enc_uint(1); key = "quote_user_1"
            else:
                data = sel(sig); key = base
            calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                          "params": [{"to": addr, "data": data}, "latest"]})
            keys.append(key)
        got = False
        for ep in EPS:
            try:
                res = post(ep, calls, timeout=10)
                if isinstance(res, list) and len(res) == len(calls):
                    for it, k in zip(res, keys):
                        out[k] = None if (isinstance(it, dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it, dict) else None)
                    got = True
                    break
            except Exception:
                continue
        if not got:
            for k in keys:
                out.setdefault(k, "BATCH-FAIL")
    return out

def str_read(addr, sig, arg=None):
    data = sel(sig) + (enc_uint(arg) if arg is not None else "")
    r = rpc("eth_call", [{"to": addr, "data": data}, "latest"])
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

def dump(res):
    res["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(res, open(OUT, "w"), indent=1)

tip = int(rpc("eth_blockNumber", []), 16)
tip_blk = rpc("eth_getBlockByNumber", [hex(tip), False])
tip_ts = int(tip_blk["timestamp"], 16)
old_blk = rpc("eth_getBlockByNumber", [hex(tip - 10000), False])
old_ts = int(old_blk["timestamp"], 16)
spb = (tip_ts - old_ts) / 10000.0
now = int(time.time())
print(f"tip={tip} tip_ts={tip_ts} spb={spb:.3f} lag={now-tip_ts}s", flush=True)
res = {"run": "2026-11-13 20:31 WIB promowatch", "block": tip, "block_ts": tip_ts,
       "sec_per_block": round(spb, 3), "reads": {}}
dump(res)
for name, addr in TARGETS.items():
    e = {"address": addr, "views": batch_read(addr)}
    e["contractURI"] = str_read(addr, "contractURI()")
    e["tokenURI_1"] = str_read(addr, "tokenURI(uint256)", arg=1)
    res["reads"][name] = e
    dump(res)
    summ = {k: v for k, v in e["views"].items() if v is not None}
    print(name, summ, "| contractURI:", str(e.get("contractURI"))[:120],
          "| tokenURI1:", str(e.get("tokenURI_1"))[:120], flush=True)

blocks_24h = int(86400 / spb)
b24 = tip - blocks_24h
b24_blk = rpc("eth_getBlockByNumber", [hex(b24), False])
b24_ts = int(b24_blk["timestamp"], 16) if b24_blk else None
print(f"block24h_ago={b24} ts={b24_ts}", flush=True)
res["block24h_ago"] = b24; res["block24h_ts"] = b24_ts
dump(res)
hist = {}
for name, addr in TARGETS.items():
    fm = rpc("eth_call", [{"to": addr, "data": sel("freeMinted()")}, hex(b24)])
    ts = rpc("eth_call", [{"to": addr, "data": sel("totalSupply()")}, hex(b24)])
    hist[name] = {"freeMinted@24h": to_int(fm) if fm else ("RPC-FAIL" if fm is None else None),
                  "totalSupply@24h": to_int(ts) if ts else ("RPC-FAIL" if ts is None else None)}
    print("HIST24", name, hist[name], flush=True)
    res["hist24h"] = hist
    dump(res)
print("ELAPSED", round(time.time() - t0, 1))
