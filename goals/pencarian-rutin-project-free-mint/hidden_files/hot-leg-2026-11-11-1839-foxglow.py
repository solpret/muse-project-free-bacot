#!/usr/bin/env python3
"""Foxglow 0x6e159c9cd56beadb523b80d195dde39c042a1d48 fast on-chain verification (hot-leg 18:39 follow-up). S1 shape re-verified via AGENT_ID() (uppercase fn the case-sensitive shape-checker missed). Reads: registry, supplies, pool, user slot, quote. Plus one narrow eth_getLogs attempt for first Transfer-from-zero (age corroboration; Ankr/public RPC known -32005-dead, attempt recorded either way)."""
import json, time, urllib.request, concurrent.futures
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x6e159c9cd56beadb523b80d195dde39c042a1d48"
EP = "https://bsc.nodereal.io/"
EP2 = "https://bsc-dataseed.binance.org/"
T0 = time.time()

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_u(n): return ("%064x" % n)

def call(addr, sig, args=""):
    data = sel(sig) + args
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": addr, "data": data}, "latest"]}).encode()
    last_err = None
    for ep in (EP, EP2):
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r:
                j = json.loads(r.read().decode())
            if "error" in j: return {"error": str(j["error"])[:140]}
            raw = j["result"]
            if raw in (None, "0x"): return {"error": "empty-return"}
            if len(raw) >= 66:
                v = raw[2:66]
                if set(v) <= set("0123456789abcdef"):
                    try: return int(v, 16)
                    except Exception: return raw
            return raw
        except Exception as e:
            last_err = e
            continue
    return {"error": f"{type(last_err).__name__}: {str(last_err)[:100]}"}

U = enc_addr(USER)
SPECS = [
 ("AGENT_ID", "AGENT_ID()", ""),
 ("FREE_SUPPLY", "FREE_SUPPLY()", ""),
 ("MAX_SUPPLY", "MAX_SUPPLY()", ""),
 ("FREE_PER_WALLET", "FREE_PER_WALLET()", ""),
 ("MAX_PER_WALLET", "MAX_PER_WALLET()", ""),
 ("PRICE", "PRICE()", ""),
 ("totalSupply", "totalSupply()", ""),
 ("mintOpen", "mintOpen()", ""),
 ("freeClaimed_total", "freeClaimed()", ""),
 ("freeFor_user_1", "freeFor(address,uint256)", U + enc_u(1)),
 ("freeLeft_user", "freeLeft(address)", U),
 ("freeUsed_user", "freeUsed(address)", U),
 ("mintedBy_user", "mintedBy(address)", U),
 ("quote_user_1", "quote(address,uint256)", U + enc_u(1)),
 ("contractURI", "contractURI()", ""),
]
out = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(call, ADDR, sig, args): key for key, sig, args in SPECS}
    for f in concurrent.futures.as_completed(futs, timeout=60):
        out[futs[f]] = f.result()

# block number
blk = None
body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
for ep in (EP, EP2):
    try:
        req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as r:
            blk = int(json.loads(r.read().decode())["result"], 16)
        break
    except Exception:
        continue

# one eth_getLogs attempt: Transfer (from zero) to this contract, last ~2000 blocks (age corroboration attempt)
logs_note = ""
try:
    topic0 = "0x" + keccak.new(digest_bits=256).update(b"Transfer(address,address,uint256)").hexdigest()
    zero = "0x0000000000000000000000000000000000000000000000000000000000000000"
    params = {"fromBlock": hex(blk - 2000) if blk else "latest", "toBlock": "latest",
              "address": ADDR, "topics": [topic0, zero]}
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs", "params": [params]}).encode()
    done = False
    for ep in (EP, EP2):
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                j = json.loads(r.read().decode())
            if "error" in j:
                logs_note = f"eth_getLogs error via {ep}: {str(j['error'])[:140]}"
                continue
            logs = j.get("result", [])
            logs_note = f"eth_getLogs OK via {ep}: {len(logs)} Transfer-from-zero in last 2000 blocks (head {blk}); earliest block in window: {int(logs[0]['blockNumber'],16) if logs else 'none'}"
            done = True
            break
        except Exception as e:
            logs_note = f"eth_getLogs transport fail via {ep}: {type(e).__name__}: {str(e)[:100]}"
    if not done and not logs_note:
        logs_note = "eth_getLogs: no endpoint returned"
except Exception as e:
    logs_note = f"eth_getLogs attempt error: {type(e).__name__}: {str(e)[:100]}"

res = {"contract": ADDR, "name": "Foxglow", "block": blk, "reads": out, "logs_attempt": logs_note,
       "elapsed_s": round(time.time() - T0, 1)}
json.dump(res, open(BASE + "hot-leg-2026-11-11-1839-foxglow.json", "w"), indent=1)
print(json.dumps(res, indent=1))
