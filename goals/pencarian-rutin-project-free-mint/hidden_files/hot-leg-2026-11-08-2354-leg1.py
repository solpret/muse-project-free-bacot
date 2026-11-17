#!/usr/bin/env python3
"""Hot-leg 2344 leg1: parallel shape-check of the 12 new Sourcify feed contracts
(5 brand-new verified 16:39-16:45 UTC + 7 transport-failed retries from 2319).
eth_getCode with endpoint fallback (dataseed/dataseed2/publicnode); ABI via Sourcify.
Records only checked contracts in hot-leg-seen.json; transport failures NOT recorded."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-2354"
NOW = "2026-11-08T23:54:38+07:00"
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
 ("0xca93c24bD06eFf6136E346169A44ea1b16f889F3", "2026-11-08T16:56:16Z"),
 ("0xB3AC4612E609fce2B98c2f6602D5EFCeeB61C473", "2026-11-08T16:53:36Z"),
 ("0xc1BD667EfFF832992d0166A3187CCD289A26Af8E", "2026-11-08T16:51:50Z"),
 ("0xCc4425A7F63148CA1A70c9504B171811349aC84A", "2026-11-08T16:49:24Z"),
 ("0x98C716d82A219Ce5cf25579dDAb95bF8db24a052", "2026-11-08T16:39:49Z"),
 ("0xcc9f9530B558addd9525d3fB10f483CC8D769C05", "2026-11-08T16:03:34Z"),
 ("0xA036460E8117B903b5191Dc48AfC8441f20Eb3C3", "2026-11-08T16:03:28Z"),
 ("0xee5df6033087FE02fD20de179f3A105A549d8489", "2026-11-08T16:01:24Z"),
 ("0x5e9f29c4b8b23dD3aB3cAbB4a59c875983dCB036", "2026-11-08T15:56:33Z"),
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
                "seen": {"first_seen_wib": NOW, "source": "sourcify-feed-2354", "status": "checked-not-contract",
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
            "seen": {"first_seen_wib": NOW, "source": "sourcify-feed-2354",
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
