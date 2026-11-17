#!/usr/bin/env python3
"""Hot-leg 2026-11-11 22:19 WIB — micro-salvage: remaining decision reads.
(1) BB 0x7c71 S1 on-chain verify (ABI first, then views).
(2) AGCR free-pool verify (Boltbook 2367/2400 claim).
(3) S1 0x6C50 age via mintOpenSat() + price().
(4) Early leads BUCKET/MOONDRILL/0x2e50/CRTSAINTS totals (skipped by budget).
(5) WFPASS mintOpen (pre-launch watch).
Sequential curl -m 6, budget 150s. Writes own run json only."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-11-2219"
T0 = time.time()
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
DEADLINE = 150.0

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")

def curl_json(url, timeout=12):
    try:
        r = subprocess.run(["curl", "-s", "-m", str(timeout), url],
                           capture_output=True, timeout=timeout + 5)
        return json.loads(r.stdout.decode(errors="replace"))
    except Exception:
        return None

def call(addr, sig, args=""):
    data = sel(sig) + args
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": addr, "data": data}, "latest"]})
    for ep in ("https://bsc-dataseed.binance.org/", "https://bsc.nodereal.io/"):
        if time.time() - T0 > DEADLINE:
            return {"error": "budget-exceeded"}
        try:
            r = subprocess.run(["curl", "-s", "-m", "6", "-H", "Content-Type: application/json",
                                "-d", body, ep], capture_output=True, timeout=10)
            j = json.loads(r.stdout.decode(errors="replace"))
            if "error" in j:
                continue
            raw = j.get("result")
            if raw in (None, "0x"):
                return {"error": "empty-return"}
            if len(raw) >= 66:
                v = raw[2:66]
                if set(v) <= set("0123456789abcdef"):
                    try:
                        return int(v, 16)
                    except Exception:
                        return raw
            return raw
        except Exception:
            continue
    return {"error": "all-endpoints-failed"}

U = enc_addr(USER)
out = {"run": "free-mint-hot-leg 2026-11-11 22:19 WIB micro-salvage"}

def read_views(addr, sigs):
    res = {}
    for sig in sigs:
        res[sig] = call(addr, sig, U if "(address)" in sig else "")
        time.sleep(0.15)
        if isinstance(res[sig], dict) and res[sig].get("error") == "budget-exceeded":
            break
    return res

# (1) BB 0x7c71
BB = "0x7c71b7158b9b3122f35570d6b737ea4a2db8e205"
j = curl_json(f"https://sourcify.dev/server/v2/contract/56/{BB}?fields=abi", 12)
bb_names = None
if isinstance(j, dict):
    abi = j.get("abi") or (j.get("stdJson") or {}).get("abi")
    if abi:
        bb_names = sorted({(f.get("name") or "").lower() for f in abi if isinstance(f, dict)})
out["bb_abi_names"] = bb_names
print("BB_ABI", len(bb_names) if bb_names else None, flush=True)
cands = ["totalSupply()", "totalMinted()", "freeMinted()", "FREE_CAP()", "freeCap()",
         "FREE_SUPPLY()", "mintOpen()", "mintStart()", "mintOpenSat()",
         "freeClaimed(address)", "balanceOf(address)"]
out["bb_onchain"] = read_views(BB, cands)
print("BB", json.dumps(out["bb_onchain"]), flush=True)

# (2) AGCR
AGCR = "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc"
out["agcr_onchain"] = read_views(AGCR, ["freeMinted()", "FREE_SUPPLY()", "freeSupply()",
                                        "mintOpen()", "totalSupply()",
                                        "freeClaimed(address)", "balanceOf(address)"])
print("AGCR", json.dumps(out["agcr_onchain"]), flush=True)

# (3) S1 0x6C50 age + price
S1 = "0x6C504A7B392b1D57845F57d2abb5C4d49211Aa7f"
out["s1_age_price"] = read_views(S1, ["mintOpenSat()", "price()"])
print("S1", json.dumps(out["s1_age_price"]), flush=True)

# (4) early leads
early = {
    "BUCKET": ("0x2b0d3b384C341020aed1d49907b5708C423bA6DA",
               ["totalSupply()", "totalFreeCount()"]),
    "MOONDRILL": ("0x87b354E2014D2e418927A1105dD219A2e7b063b0",
                  ["totalSupply()", "firstFreeUsed()", "freeMinted()"]),
    "0x2e50": ("0x2e508C6510d9550031932f0D6Fe691DCe38E66E3",
               ["totalSupply()", "firstFreeUsed()", "freeMinted()"]),
    "CRTSAINTS": ("0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F",
                  ["totalSupply()", "firstFreeUsed()", "freeMinted()"]),
}
out["early"] = {}
for name, (addr, views) in early.items():
    if time.time() - T0 > DEADLINE:
        out["early"][name] = {"status": "skipped-budget"}
        continue
    out["early"][name] = read_views(addr, views)
    print(name, json.dumps(out["early"][name]), flush=True)

# (5) WFPASS
out["wfpass"] = read_views("0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C", ["mintOpen()"])
print("WFPASS", json.dumps(out["wfpass"]), flush=True)

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-run-{TAG}-salvage.json", "w"), indent=1)
print("ELAPSED", out["elapsed_s"])
