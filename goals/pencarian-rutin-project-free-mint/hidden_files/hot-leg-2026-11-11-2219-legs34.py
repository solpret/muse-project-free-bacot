#!/usr/bin/env python3
"""Hot-leg 2026-11-11 22:19 WIB — leg 3 (new S1 verify) + leg 4 prio re-read.
Sequential curl eth_calls, -m 6, dataseed then nodereal. Read-only on-chain;
writes only own run json. Budget: stop after ~200s."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-11-2219"
T0 = time.time()
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
DEADLINE = 200.0

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
out = {"run": "free-mint-hot-leg 2026-11-11 22:19 WIB leg3+leg4"}

# block number
blk = call("0x0000000000000000000000000000000000000000", "totalSupply()")
out["block_probe"] = blk  # dummy; replaced below
try:
    r = subprocess.run(["curl", "-s", "-m", "6", "-H", "Content-Type: application/json",
                        "-d", json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}),
                        "https://bsc-dataseed.binance.org/"], capture_output=True, timeout=10)
    out["block"] = int(json.loads(r.stdout.decode())["result"], 16)
except Exception as e:
    out["block"] = {"error": str(e)}

def abi_names(addr):
    j = curl_json(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", 12)
    if isinstance(j, dict):
        abi = j.get("abi") or (j.get("stdJson") or {}).get("abi")
        if abi:
            return {(f.get("name") or "").lower() for f in abi if isinstance(f, dict)}
    return None

def read_views(addr, candidates):
    res = {}
    for sig in candidates:
        name = sig.split("(")[0].lower()
        res[sig] = call(addr, sig, U if "(address)" in sig else "")
        time.sleep(0.15)
        if isinstance(res[sig], dict) and res[sig].get("error") == "budget-exceeded":
            break
    return res

# ---- Leg 3: new S1 0x6C50... ----
S1 = "0x6C504A7B392b1D57845F57d2abb5C4d49211Aa7f"
s1_names = abi_names(S1)
out["s1_abi_names"] = sorted(s1_names) if s1_names else None
cands = ["name()", "symbol()", "totalSupply()", "totalMinted()", "freeMinted()",
         "FREE_CAP()", "freeCap()", "FREE_SUPPLY()", "mintOpen()", "mintStart()",
         "freeAvailable(address)", "freeClaimed(address)", "balanceOf(address)",
         "mintedBy(address)", "freeUsedBy(address)"]
out["s1_onchain"] = read_views(S1, cands)
print("S1", json.dumps(out["s1_onchain"]), flush=True)

# ---- Boltbook-new 0x7c71... shape-check via ABI ----
BB = "0x7c71b7158b9b3122f35570d6b737ea4a2db8e205"
bb_names = abi_names(BB)
if bb_names is not None:
    has_mint = any("mint" in n for n in bb_names)
    has_quote = any(("quote" in n or n in ("cost", "price", "mintprice")) for n in bb_names)
    free_views = sorted(n for n in bb_names if "free" in n)
    agent = any(("agent" in n and ("registry" in n or "gate" in n or "id" in n)) for n in bb_names)
    out["boltbook_new_shape"] = {"addr": BB, "S1": bool(has_mint and has_quote and free_views and agent),
                                 "S2": False, "mint": has_mint, "quote": has_quote,
                                 "free": free_views, "agent": agent, "n_fns": len(bb_names)}
else:
    out["boltbook_new_shape"] = {"addr": BB, "status": "shape-check-failed", "note": "ABI unfetchable"}
print("BB", json.dumps(out["boltbook_new_shape"]), flush=True)

# ---- AGCR registry retry ----
AGCR = "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc"
out["agcr_registry"] = call(AGCR, "AGENT_ID_REGISTRY()")
print("AGCR", json.dumps(out["agcr_registry"]), flush=True)

# ---- Leg 4 prio re-read ----
prio = {
    "Stampooor": ("0x467696af8c2206B977B24081445104632dc1D459",
                  ["freeMinted()", "freeAvailable(address)", "balanceOf(address)"]),
    "AgentPals": ("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", ["freeMinted()"]),
    "MECHA": ("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
              ["totalMinted()", "freeClaimed()", "freeAvailable(address)", "balanceOf(address)"]),
    "BUCKET": ("0x2b0d3b384C341020aed1d49907b5708C423bA6DA",
               ["totalSupply()", "totalFreeCount()", "freeAvailable(address)", "balanceOf(address)"]),
    "MOONDRILL": ("0x87b354E2014D2e418927A1105dD219A2e7b063b0",
                  ["totalSupply()", "firstFreeUsed()", "freeMinted()", "balanceOf(address)"]),
    "0x2e50": ("0x2e508C6510d9550031932f0D6Fe691DCe38E66E3",
               ["totalSupply()", "firstFreeUsed()", "freeMinted()", "balanceOf(address)"]),
    "CRTSAINTS": ("0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F",
                  ["totalSupply()", "firstFreeUsed()", "freeMinted()", "balanceOf(address)"]),
    "WFPASS": ("0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C",
               ["mintOpen()", "freeMinted()", "totalMinted()"]),
}
out["prio"] = {}
for name, (addr, views) in prio.items():
    if time.time() - T0 > DEADLINE:
        out["prio"][name] = {"status": "skipped-budget"}
        continue
    out["prio"][name] = read_views(addr, views)
    print(name, json.dumps(out["prio"][name]), flush=True)

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-run-{TAG}-legs34.json", "w"), indent=1)
print("ELAPSED", out["elapsed_s"])
