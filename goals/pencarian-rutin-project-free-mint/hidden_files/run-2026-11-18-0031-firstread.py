#!/usr/bin/env python3
"""free-mint-search run 2026-11-18 00:31 WIB — first-read of new discoveries.
Targets: THYRK + STOCK AGENT (new Boltbook front-page, not in snapshot/seen),
Sourcify-new 0xd966 + 0x8157 (not shape-checked by hot-leg 0024/0029).
Read-only: shape via Sourcify ABI + on-chain views via bsc-dataseed batch.
Writes: run-2026-11-18-0031-firstread.json only. No snapshot write here."""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
RPC_URL = "https://bsc-dataseed.binance.org/"
T0 = time.time()
out = {"run": "free-mint-search 2026-11-18 00:31 WIB first-read"}

def fetch(url, timeout=20):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-A", "free-mint-search/1.0", url],
                       capture_output=True, timeout=timeout + 5)
    if r.returncode != 0 or not r.stdout:
        raise IOError(f"curl failed rc={r.returncode}")
    return r.stdout

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedTotal"]

def shape(addr):
    try:
        raw = fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=20)
        d = json.loads(raw)
        abi = d.get("abi") or (d.get("stdJson", {}) or {}).get("abi") or []
        va = d.get("verifiedAt")
    except Exception as e:
        return {"status": "shape-check-failed", "error": f"{type(e).__name__}: {str(e)[:150]}"}
    names = [f.get("name", "").lower() for f in abi if isinstance(f, dict)]
    has_mint = any(n.startswith("mint") or n in ("claimfree", "claim", "mintfree") for n in names)
    has_quote = any("quote" in n or "price" in n or n.startswith("cost") for n in names)
    free = sorted(set(n for n in names if any(k.lower() in n for k in FREE_VIEWS)))
    agent = any("agent" in n or "registry" in n for n in names) or REGISTRY.lower() in json.dumps(abi).lower()
    tokenish = all(k in names for k in ("name", "symbol", "decimals", "totalsupply"))
    noarg_free = any(n in ("mintfree", "claimfree") for n in names)
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = tokenish and noarg_free and bool(free) and agent
    fn_names = sorted(set(names))
    return {"S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
            "free_views": free, "agent_ref": agent, "is_token": tokenish,
            "n_fns": len(abi), "status": "checked", "verifiedAt": va,
            "fn_names": fn_names}

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def encode(sig, arg):
    data = "0x" + sel(sig)
    if arg == "user":
        data += enc_addr(USER)
    elif arg == "one":
        data += "%064x" % 1
    elif arg == "user1":
        data += enc_addr(USER) + "%064x" % 1
    return data

def curl_json(url, payload, timeout=25):
    r = subprocess.run(["curl", "-s", "-L", "--max-time", str(timeout), url,
                        "-H", "Content-Type: application/json",
                        "-d", json.dumps(payload)],
                       capture_output=True, timeout=timeout + 5)
    if r.returncode != 0 or not r.stdout:
        raise IOError(f"curl failed rc={r.returncode}")
    return json.loads(r.stdout.decode())

def rpc_batch(calls, timeout=25):
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    resp = curl_json(RPC_URL, payload, timeout=timeout)
    if not isinstance(resp, list):
        raise IOError(f"non-list batch response: {str(resp)[:200]}")
    by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
    res = []
    for i in range(len(calls)):
        it = by_id.get(i + 1, {})
        if "result" in it and it["result"] not in (None, "0x"):
            try:
                res.append(int(it["result"], 16))
            except Exception:
                res.append(it["result"])
        elif "error" in it:
            res.append(f"err:{str(it['error'])[:80]}")
        else:
            res.append(None)
    return res

VIEWS = [("totalSupply", "totalSupply()", None),
         ("totalMinted", "totalMinted()", None),
         ("freeMinted", "freeMinted()", None),
         ("freeClaimed", "freeClaimed()", None),
         ("freeLeft", "freeLeft()", None),
         ("freeSupply", "freeSupply()", None),
         ("FREE_SUPPLY", "FREE_SUPPLY()", None),
         ("MAX_SUPPLY", "MAX_SUPPLY()", None),
         ("mintOpen", "mintOpen()", None),
         ("mintPrice", "mintPrice()", None),
         ("cost_user_1", "cost(address,uint256)", "user1"),
         ("quote_user_1", "quote(address,uint256)", "user1"),
         ("mintedCount_user", "mintedCount(address)", "user"),
         ("freeClaimed_user", "freeClaimed(address)", "user"),
         ("balanceOf_user", "balanceOf(address)", "user")]

targets = {
    "THYRK": "0x4d90ffc3075fb8897edff6d7c6269c906664a20e",
    "STOCK AGENT": "0xba7068233da805bdebcc167be361c219002e6b7f",
    "Sourcify-0xd966": "0xd966018EAfD53A03C552D0575FA3Cc83eD887777",
    "Sourcify-0x8157": "0x8157708A9dd2e49B7fF50DA75F64AD61A481E800",
}
results = {}
for name, addr in targets.items():
    s = shape(addr)
    results[name] = {"address": addr, "shape": s}
    print(name, "shape:", {k: s.get(k) for k in ("S1", "S2", "has_mint", "has_quote", "free_views", "agent_ref", "is_token", "n_fns", "status")})

# On-chain reads only for the two Boltbook NFT-shaped discoveries
calls, meta = [], []
for name in ("THYRK", "STOCK AGENT"):
    addr = targets[name]
    for label, sig, arg in VIEWS:
        calls.append((addr, encode(sig, arg)))
        meta.append((name, label))
res = rpc_batch(calls)
for (name, label), val in zip(meta, res):
    results[name].setdefault("views", {})[label] = val
try:
    blk = curl_json(RPC_URL, [{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}])
    out["block"] = int(blk[0]["result"], 16)
except Exception as e:
    out["block"] = f"error: {str(e)[:120]}"

out["results"] = results
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{HF}/run-2026-11-18-0031-firstread.json", "w"), indent=1)
print(json.dumps({k: v for k, v in results.items()}, indent=1, default=str)[:4000])
print("block:", out["block"], "elapsed:", out["elapsed_s"])
