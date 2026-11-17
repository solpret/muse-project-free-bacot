#!/usr/bin/env python3
"""Hot-leg 2344 leg1: parallel shape-check of the 12 new Sourcify feed contracts
(5 brand-new verified 16:39-16:45 UTC + 7 transport-failed retries from 2319).
eth_getCode with endpoint fallback (dataseed/dataseed2/publicnode); ABI via Sourcify.
Records only checked contracts in hot-leg-seen.json; transport failures NOT recorded."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-2344"
NOW = "2026-11-08T23:44:38+07:00"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
        "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted",
        "freeCardsRemaining"}
AGENT = {"agentId", "agentRegistry", "registry", "AGENT_ID", "AGENT_REGISTRY", "hasAgentId"}
EPS = ["https://bsc-dataseed.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc.publicnode.com/"]
FEED = [
 ("0xcBb2ff0Ea1b90f2A40318C34799528ba5431FEE0", "2026-11-08T16:45:30Z"),
 ("0xF9c88a47e036994096347083632DF01b202e4270", "2026-11-08T16:45:20Z"),
 ("0x9c6A008f73a1d1941f4763b88C6eE8c8E4ef8B0a", "2026-11-08T16:41:51Z"),
 ("0x98C716d82A219Ce5cf25579dDAb95bF8db24a052", "2026-11-08T16:39:49Z"),
 ("0x18C67a826CCa4375BC552Bbd58DAb3EcDcDC31a5", "2026-11-08T16:39:03Z"),
 ("0x2d00120B6a4f66a05F610aDDc6e24DA0bE9C8515", "2026-11-08T16:23:56Z"),
 ("0x332EFB8A690Fd31cB174683f23ff81eD0a4d7F29", "2026-11-08T16:17:24Z"),
 ("0xC874d1706BB687e3ED1a1c0Cec0328C71f517c5E", "2026-11-08T16:15:56Z"),
 ("0x5160C9A62b48544696f3F12081377098EddfA34e", "2026-11-08T16:14:36Z"),
 ("0x1D45176318eb9B9613F4dF62aed8A070D9F1aB71", "2026-11-08T16:04:54Z"),
 ("0xD743c793b23D1adE2099892B010d4F4530d44E0a", "2026-11-08T16:04:45Z"),
 ("0xB12e5b1F6FAE946b05428DCa5eaf3b45337fDB82", "2026-11-08T16:04:08Z"),
]
seen = json.load(open(BASE + "hot-leg-seen.json"))
log = {"run": "free-mint-hot-leg 2026-11-08 23:44:38 WIB leg1", "feed_n": 20, "new_n": 12}
t0 = time.time()

def curl_json(url, payload=None, timeout=10):
    cmd = ["curl", "-sL", "--max-time", str(timeout)]
    if payload is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(payload)]
    cmd.append(url)
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def get_code(addr):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode", "params": [addr, "latest"]}
    for ep in EPS:
        try:
            r = curl_json(ep, payload, timeout=10).get("result")
            if r is not None:
                return r, ep
        except Exception:
            continue
    return None, None

def shape_check(addr, verified_at):
    if addr.lower() == REGISTRY.lower() or addr.lower() in EXCLUDED:
        return {"addr": addr, "skipped": "registry-or-excluded"}
    code, ep = get_code(addr)
    if code is None:
        return {"addr": addr, "error": "eth_getCode empty on all endpoints (transport artifact, not recorded)"}
    if code == "0x":
        return {"addr": addr, "result": "EOA-checked-not-contract", "record": True,
                "seen": {"first_seen_wib": NOW, "source": "sourcify-feed-2344", "status": "checked-not-contract",
                         "note": "eth_getCode 0x via %s - EOA/wallet address, not a contract; no sale shape, not a lead." % ep}}
    try:
        abi = curl_json(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
                        timeout=12).get("abi", [])
        names = {e["name"] for e in abi if e.get("type") == "function"}
    except Exception as ex:
        return {"addr": addr, "error": f"ABI fetch {ex}"}
    if not names:
        return {"addr": addr, "result": "ABI-0-functions-unverified-not-recorded"}
    s1 = any(n.lower().startswith("mint") for n in names) and bool(names & {"quote", "cost"}) \
        and bool(names & FREE) and bool(names & AGENT)
    s2 = bool(names & {"name", "symbol", "decimals", "totalSupply"}) and "mintFree" in names \
        and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) \
        and bool(names & AGENT)
    return {"addr": addr, "result": "sale-shape-pass" if (s1 or s2) else "checked-not-sale-shape",
            "S1": s1, "S2": s2, "n_fns": len(names), "verified_at": verified_at, "record": True,
            "seen": {"first_seen_wib": NOW, "source": "sourcify-feed-2344",
                     "status": "sale-shape-pass" if (s1 or s2) else "checked-not-sale-shape",
                     "S1": s1, "S2": s2, "n_fns": len(names), "verified_at": verified_at}}

results = {}
with ThreadPoolExecutor(max_workers=6) as ex:
    futs = {ex.submit(shape_check, a, v): a for a, v in FEED}
    for f in futs:
        r = f.result()
        results[r["addr"]] = r
        if r.get("record"):
            seen[r["addr"].lower()] = r["seen"]
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
log["results"] = results
log["seen_total"] = len(seen)
log["elapsed_sec"] = round(time.time() - t0, 1)
json.dump(log, open(BASE + TAG + "-leg1.log", "w"), indent=1)
print(json.dumps(log, indent=1))
print("ELAPSED", round(time.time() - t0, 1))
