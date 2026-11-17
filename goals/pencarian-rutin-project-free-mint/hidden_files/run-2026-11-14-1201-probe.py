#!/usr/bin/env python3
"""Probe run 2026-11-14 12:01 WIB: 4 new Boltbook contracts (on-chain views)
+ 2 new Sourcify feed contracts (ABI S1/S2 shape). Read-only; no preview/mint.
Writes run-2026-11-14-1201-probe.json."""
import json, subprocess, time, sys
sys.set_int_max_str_digits(100000)
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a, str) and a.startswith("0x") and len(a) == 42 else enc_u(int(a))
    return d
def post_rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)

VIEWS = [
    ("name", "name()", []), ("symbol", "symbol()", []),
    ("totalSupply", "totalSupply()", []), ("totalMinted", "totalMinted()", []),
    ("freeClaimed", "freeClaimed()", []), ("freeMinted", "freeMinted()", []),
    ("FREE_SUPPLY", "FREE_SUPPLY()", []), ("MAX_SUPPLY", "MAX_SUPPLY()", []),
    ("mintOpen", "mintOpen()", []),
    ("priceFor_user", "priceFor(address)", [USER]),
    ("mintedBy_user", "mintedBy(address)", [USER]),
    ("freeUsed_user", "freeUsed(address)", [USER]),
    ("owner", "owner()", []),
    ("contractURI", "contractURI()", []),
    ("tokenURI_1", "tokenURI(uint256)", [1]),
    ("agentRegistry", "agentRegistry()", []),
]
ADDRS = {
    "REOPIR": "0x12f65bc14037ccdf3f97afc0e67a0e4aca3cf5b9",
    "B751": "0xb7517e3b31107695f2f8837fafc76999b956c871",
    "FrieAgent": "0xc64da7479c5abc8e6dfadeb4d17502ebcf9837e5",
    "OTV": "0xfab9c88d25e111edd68a2cca3e0f650863a5bf25",
}

def probe_one(name, addr):
    calls = []
    for i, (label, sig, args) in enumerate(VIEWS):
        calls.append({"jsonrpc": "2.0", "id": i, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
    calls.append({"jsonrpc": "2.0", "id": 99, "method": "eth_blockNumber", "params": []})
    res = {}
    for ep in EPS:
        try:
            out = post_rpc(ep, calls)
            if isinstance(out, list) and out:
                res = {VIEWS[r["id"]][0]: (to_int(r.get("result")) if r.get("result") else None)
                       for r in out if isinstance(r, dict) and r.get("id") != 99}
                # raw strings for name/symbol/owner/uri
                for r in out:
                    if isinstance(r, dict) and r.get("id") != 99 and r.get("result"):
                        lbl = VIEWS[r["id"]][0]
                        if lbl in ("name", "symbol", "owner", "contractURI", "tokenURI_1"):
                            res[lbl + "_raw"] = r["result"]
                blk = next((r.get("result") for r in out if isinstance(r, dict) and r.get("id") == 99), None)
                res["_block"] = int(blk, 16) if blk else None
                res["_ep"] = ep
                break
        except Exception as e:
            res = {"_error": str(e)[:200]}
    res["_name"] = name
    return name, res

results = {}
with ThreadPoolExecutor(max_workers=4) as ex:
    for name, res in ex.map(lambda kv: probe_one(*kv), ADDRS.items()):
        results[name] = res
        print(name, "block", res.get("_block"), "ts", res.get("totalSupply"), "tm", res.get("totalMinted"),
              "free", res.get("freeClaimed"), "/", res.get("FREE_SUPPLY"), "open", res.get("mintOpen"),
              "priceFor", res.get("priceFor_user"), "mintedBy", res.get("mintedBy_user"),
              "freeUsed", res.get("freeUsed_user"), flush=True)

# Sourcify ABI shape check for the 2 new feed contracts
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed"}
FEED_NEW = [("0x65606174235aD06Af14D18D363747f821C758Bc1", "2026-11-14T04:50:23Z"),
            ("0xC7a3f01a829525b44B3B7dbD309f3455AcbC34E7", "2026-11-14T04:50:23Z")]
def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        p = subprocess.run(["curl", "-sS", "-m", "30", "-A", "Mozilla/5.0", url],
                           capture_output=True, text=True, timeout=40)
        if p.returncode != 0 or not p.stdout:
            return addr, None, f"curl rc={p.returncode}"
        return addr, json.loads(p.stdout).get("abi", []), None
    except Exception as e:
        return addr, None, f"{type(e).__name__}: {str(e)[:100]}"
shapes = []
for addr, vat in FEED_NEW:
    addr2, abi, err = fetch_abi(addr)
    if abi is None:
        shapes.append({"address": addr, "verifiedAt": vat, "S1": None, "S2": None, "error": err, "status": "abi-fetch-failed"})
        print(addr, "ABI FAILED", err, flush=True); continue
    names = set(); fns = {}
    for e in abi:
        if e.get("type") == "function":
            names.add(e["name"]); fns.setdefault(e["name"], []).append(e)
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
    free_views = sorted(names & FREE_VIEWS)
    agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate",
                              "AgentGate", "AGENT_ID_REGISTRY", "agentIdRegistry", "AGENT_ID"})
    is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
    mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
    s1 = bool(has_mint and has_quote and free_views and agent_ref)
    s2 = bool(is_token and mintfree and (names & {"freeClaimed", "freeMinted"}) and
              (names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref)
    shapes.append({"address": addr, "verifiedAt": vat, "S1": s1, "S2": s2, "has_mint": has_mint,
                   "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
                   "is_token": is_token, "n_fns": len(names), "status": "checked"})
    print(addr, "S1", s1, "S2", s2, "mint", has_mint, "quote", has_quote, "free", free_views,
          "agent", agent_ref, "n", len(names), flush=True)

out = {"started_wib": "2026-11-14T12:01+07:00", "probes": results, "feed_shapes": shapes,
       "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "run-2026-11-14-1201-probe.json", "w"), indent=1)
print("DONE elapsed", out["elapsed_s"])
