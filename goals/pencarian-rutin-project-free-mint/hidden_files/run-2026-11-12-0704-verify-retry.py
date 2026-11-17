#!/usr/bin/env python3
"""Hot-leg run 2026-11-12 07:04 WIB, leg 4 RETRY (fresh script for this run only).
First attempt (run-2026-11-12-0704-verify.py) FAILED: 46-call eth_call batches
trigger rate limit -32005 on all dataseed endpoints (all 12 contracts None,
last 3 deadline-skipped). Retry with per-item views in 5-call chunks (0554
pattern). No preview, no mint, no snapshot writes.
Writes run-2026-11-12-0704-verify-retry.json.
"""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
DEADLINE = time.time() + 150
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]

def enc(a):
    return a[2:].lower().rjust(64, "0")

def to_int(v):
    try:
        return int(v, 16) if v and v != "0x" else None
    except Exception:
        return None

def post_rpc(ep, payload, timeout=15):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def fname(sig):
    n = sig.split("(")[0]
    if n == "balanceOf": return "balanceOf_user"
    if n in ("freeAvailable", "freeClaimed", "freeCountBy", "mintsBy", "holdsAgentId",
             "mintedBy", "freeUsed", "firstFreeByWallet"): return n + "_user"
    return n

ITEMS = {
 "Stampooor": ("0x467696af8c2206B977B24081445104632dc1D459",
   ["freeMinted()", "freeAvailable(address)", "balanceOf(address)", "mintOpen()",
    "totalMinted()", "FREE_SUPPLY()", "freeClaimed(address)"]),
 "SEVEN": ("0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96",
   ["totalSupply()", "freeMinted()", "FREE_CAP()", "mintOpen()", "balanceOf(address)"]),
 "Eco": ("0xd31b168F7b6f3dB39BEd89433124595aaa91cfF3",
   ["freeMinted()", "totalMinted()", "FREE_WALLETS()", "freeWalletsLeft()", "freeWalletCount()",
    "MAX_SUPPLY()", "mintOpen()", "mintOpensAt()", "FREE_PER_WALLET()", "balanceOf(address)",
    "freeCountBy(address)", "mintsBy(address)", "holdsAgentId(address)"]),
 "AGCR": ("0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc",
   ["totalSupply()", "totalMinted()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()",
    "freeAvailable(address)", "balanceOf(address)", "freeClaimed(address)", "mintOpen()"]),
 "MECHA": ("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
   ["totalSupply()", "totalMinted()", "freeClaimed()", "FREE_SUPPLY()", "MAX_SUPPLY()",
    "freeAvailable(address)", "balanceOf(address)"]),
 "BUCKET": ("0x2b0d3b384C341020aed1d49907b5708C423bA6DA",
   ["totalSupply()", "totalFreeCount()", "FIRST_FREE_CAP()", "X_FREE_CAP()", "mintOpenedAt()",
    "balanceOf(address)", "freeUsed(address)"]),
 "MOONDRILL": ("0x87b354E2014D2e418927A1105dD219A2e7b063b0",
   ["totalSupply()", "firstFreeUsed()", "FIRST_FREE_CAP()", "X_FREE_CAP()", "paidMinted()",
    "mintOpen()", "balanceOf(address)", "firstFreeByWallet(address)", "freeMinted()"]),
 "CRTSAINTS": ("0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F",
   ["totalSupply()", "firstFreeUsed()", "FIRST_FREE_CAP()", "X_FREE_CAP()", "paidMinted()",
    "mintOpen()", "balanceOf(address)", "firstFreeByWallet(address)"]),
 "SUDOSAINTS": ("0x869d330bb48e7ab32da16745ef9a36a69d34f12f",
   ["totalSupply()", "freeMinted()", "FREE_CAP()", "FREE_SUPPLY()", "mintOpen()", "balanceOf(address)"]),
 "Pickgrid": ("0x7f541bcc33abed0e64455565da723e949c6f76f0",
   ["totalSupply()", "freeMinted()", "FREE_CAP()", "mintOpen()", "balanceOf(address)"]),
 "LuckyCatch": ("0xD405C90079c594DA2456F5b37B4158A12f1382e5",
   ["totalSupply()", "totalMinted()", "mintOpen()", "balanceOf(address)", "mintStart()", "PRICE()"]),
 "BinanceLife": ("0x4367b86F889014e6fD57fE812B86A581b913C645",
   ["totalMinted()", "freeMinted()", "MAX_SUPPLY()", "balanceOf(address)", "mintStart()"]),
 "0x2e50": ("0x2e508C6510d9550031932f0D6Fe691DCe38E66E3",
   ["totalSupply()", "firstFreeUsed()", "FIRST_FREE_CAP()", "X_FREE_CAP()", "paidMinted()",
    "mintOpen()", "balanceOf(address)", "firstFreeByWallet(address)", "freeMinted()"]),
 "binanceai-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
   ["launched()"]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
   ["freeSharesLeft()", "openedAt()", "freeClaimed()"]),
}

CALLS = []
for name, (addr, sigs) in ITEMS.items():
    for sig in sigs:
        args = enc(USER) if "(address)" in sig else ""
        CALLS.append((f"{name}.{fname(sig)}", addr, sig, args))

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

block = get_block()
results = {}
notes = []
CHUNK = 5
for ci in range(0, len(CALLS), CHUNK):
    if time.time() > DEADLINE:
        for key, _, _, _ in CALLS[ci:]:
            results[key] = None
        notes.append(f"deadline-hit at chunk@{ci}")
        break
    chunk = CALLS[ci:ci + CHUNK]
    batch = [{"jsonrpc": "2.0", "id": i, "method": "eth_call",
              "params": [{"to": addr, "data": sel(sig) + args}, "latest"]}
             for i, (key, addr, sig, args) in enumerate(chunk)]
    done = False
    for ep in EPS:
        if time.time() > DEADLINE:
            break
        try:
            arr = post_rpc(ep, batch, timeout=15)
            if isinstance(arr, list) and arr and all("result" in it or "error" in it for it in arr):
                for item in arr:
                    i = item.get("id")
                    if i is None or i >= len(chunk):
                        continue
                    key = chunk[i][0]
                    if "error" in item:
                        results[key] = None
                    else:
                        res = item.get("result")
                        results[key] = to_int(res) if res and len(res) >= 66 else None
                done = True
                break
        except Exception:
            continue
    if not done:
        for key, _, _, _ in chunk:
            results[key] = None
        notes.append(f"chunk@{ci} failed all endpoints")
    time.sleep(0.3)

reread = {}
for name, (addr, sigs) in ITEMS.items():
    d = {"address": addr}
    for sig in sigs:
        d[fname(sig)] = results.get(f"{name}.{fname(sig)}")
    reread[name] = d
out = {"started_wib": "2026-11-12 07:04 WIB (retry)", "block": block,
       "leg4_reread": reread, "leg4_notes": notes,
       "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "run-2026-11-12-0704-verify-retry.json", "w"), indent=1)
for name, d in reread.items():
    print(name, {k: v for k, v in d.items() if k != "address" and v is not None})
print("BLOCK", block, "ELAPSED", out["elapsed_s"], "NOTES", notes)
