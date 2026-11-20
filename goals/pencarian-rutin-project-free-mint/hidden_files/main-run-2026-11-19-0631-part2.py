#!/usr/bin/env python3
"""Main run free-mint-search 2026-11-19 06:31 WIB — part 2 (read-only):
(a) shape-check 5 new Sourcify contracts (same logic as hot-leg shape());
(b) on-chain verify DeepShard + Mine Card (single-call urllib, rotating endpoints);
(c) scan-leg PRE-FLIGHT: one small ankr_getLogs (50 blocks) <60s.
No preview/mint. Failed read = None, never 0.
"""
import json, subprocess, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = "0x" + "00" * 12 + USER[2:].lower()
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
out = {"run": "free-mint-search 2026-11-19 06:31 WIB part2"}

# --- (a) shape-check ---
def fetch(url, timeout=15):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-A", "free-mint-search/1.0", url],
                       capture_output=True)
    if r.returncode == 0 and r.stdout:
        return r.stdout
    req = urllib.request.Request(url, headers={"User-Agent": "free-mint-search/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedTotal"]
def shape(addr):
    try:
        raw = fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=15)
        d = json.loads(raw)
        abi = d.get("abi") or (d.get("stdJson", {}) or {}).get("abi") or []
        va2 = d.get("verifiedAt") or (d.get("stdJson", {}) or {}).get("verifiedAt")
    except Exception as e:
        return {"status": "shape-check-failed", "error": f"{type(e).__name__}: {e}"}
    names = [f.get("name", "").lower() for f in abi if isinstance(f, dict)]
    has_mint = any(n.startswith("mint") or n in ("claimfree", "claim", "mintfree") for n in names)
    has_quote = any("quote" in n or "price" in n or n.startswith("cost") for n in names)
    free = sorted(set(n for n in names if any(k.lower() in n for k in FREE_VIEWS)))
    agent = any("agent" in n or "registry" in n for n in names) or REGISTRY.lower() in json.dumps(abi).lower()
    tokenish = all(k in names for k in ("name", "symbol", "decimals", "totalsupply"))
    noarg_free = any(n in ("mintfree", "claimfree") for n in names)
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = tokenish and noarg_free and bool(free) and agent
    return {"S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
            "free_views": free, "agent_ref": agent, "is_token": tokenish,
            "n_fns": len(abi), "status": "checked", "verifiedAt": va2}

NEW = ["0x867884e933DB5a7d70839f34fa4A6569dF43A6Fc",
       "0x84045F4367589B16cf13209c1F31366dbde8e28a",
       "0x796A08bdA69891467faB15435474ad8c84418048",
       "0x7aFb047e1E5cCB1789BCFF7973804DF8AD7C66EA",
       "0x5210F29f9B9aE103D6a21F8385fc838551F96d5B"]
out["shape_check"] = {a: shape(a) for a in NEW}
out["shape_hits"] = [a for a, r in out["shape_check"].items() if r.get("S1") or r.get("S2")]

# --- (b) on-chain DeepShard + Mine Card ---
def sel(sig):
    h = keccak.new(digest_bits=256); h.update(sig.encode()); return "0x" + h.hexdigest()[:8]

def eth_call(ep, to, data, timeout=12):
    req = urllib.request.Request(ep, data=json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
         "params": [{"to": to, "data": data}, "latest"]}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        j = json.load(r)
        if "result" in j and j["result"]:
            return int(j["result"], 16)
        return None

ITEMS2 = {
    "DeepShard": ("0xC463960af285b7EDA0909D362Ae31783597C2076",
                  [("totalSupply", "totalSupply()"), ("mintOpen", "mintOpen()"),
                   ("balanceOf_user", "balanceOf(address)", "user")]),
    "Mine Card": ("0xf8a72c4538cd9d570b2c771f01a0d561a90a64eb",
                  [("totalSupply", "totalSupply()"), ("totalMinted", "totalMinted()"),
                   ("balanceOf_user", "balanceOf(address)", "user")]),
}
out["reads2"] = {}
ep_i = 0
for name, (addr, views) in ITEMS2.items():
    for v in views:
        key, sig = v[0], v[1]
        data = sel(sig)
        if len(v) > 2 and v[2] == "user":
            data += USER_PAD[2:]
        val = None
        for attempt in range(3):
            ep = EPS[(ep_i + attempt) % len(EPS)]
            try:
                val = eth_call(ep, addr, data)
                ep_i += 1
                break
            except Exception:
                time.sleep(1.5)
        out["reads2"].setdefault(name, {})[key] = val
        time.sleep(0.3)

# --- (c) scan pre-flight: one small ankr_getLogs, 50 blocks ---
from ankr import ankr_post
t0 = time.time()
try:
    head = ankr_post("eth_blockNumber", [], timeout=20)
    head_n = int(head["result"], 16) if isinstance(head, dict) and head.get("result") else None
except Exception as e:
    head_n, head = None, f"{type(e).__name__}: {e}"
out["preflight_head"] = head_n
if head_n:
    try:
        body = ankr_post("ankr_getLogs", {
            "blockchain": "bsc",
            "fromBlock": hex(head_n - 50), "toBlock": hex(head_n),
            "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
            "pageSize": 50, "decodeLogs": False}, timeout=55)
        out["preflight"] = {"ok": True, "elapsed_s": round(time.time() - t0, 1),
                            "logs": len(body.get("result", {}).get("logs", [])) if isinstance(body, dict) else "n/a",
                            "raw_keys": list(body.keys()) if isinstance(body, dict) else type(body).__name__}
    except Exception as e:
        out["preflight"] = {"ok": False, "elapsed_s": round(time.time() - t0, 1),
                            "error": f"{type(e).__name__}: {e}"}
else:
    out["preflight"] = {"ok": False, "error": f"head read failed: {head}"}

print(json.dumps(out, indent=1))
json.dump(out, open(BASE + "main-run-2026-11-19-0631-part2.json", "w"), indent=1)
