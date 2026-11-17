#!/usr/bin/env python3
"""Hot-leg 2319 legs1-2 recovery: parallel shape-check of the 14 new feed contracts
(3 already shape-checked in the 2304 run - recorded from that file) + 7 carryover retries.
Reuses the saved 2319 feed JSON; does not re-fetch the feed."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-2319"
NOW = "2026-11-08T23:19:38+07:00"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
        "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted",
        "freeCardsRemaining"}
AGENT = {"agentId", "agentRegistry", "registry", "AGENT_ID", "AGENT_REGISTRY", "hasAgentId"}
RPC = "https://bsc-dataseed.bnbchain.org/"
seen = json.load(open(BASE + "hot-leg-seen.json"))
log = {"run": "free-mint-hot-leg 2026-11-08 23:19:38 WIB legs1-2-recovery",
       "note": "legs12.py was killed by the 280s shell timeout during sequential shape-checks; feed JSON survived. This recovery runs the shape-checks in parallel with 10s timeouts."}
t0 = time.time()

def curl_json(url, payload=None, timeout=10):
    cmd = ["curl", "-sL", "--max-time", str(timeout)]
    if payload is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(payload)]
    cmd.append(url)
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def shape_check(addr, source):
    if addr.lower() == REGISTRY.lower() or addr.lower() in EXCLUDED:
        return {"addr": addr, "skipped": "registry-or-excluded"}
    try:
        code = curl_json(RPC, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                                "params": [addr, "latest"]}, timeout=10).get("result")
    except Exception as ex:
        return {"addr": addr, "error": f"eth_getCode {ex}"}
    if code is None:
        return {"addr": addr, "error": "eth_getCode empty response (transport artifact, not recorded)"}
    if code == "0x":
        return {"addr": addr, "result": "EOA-checked-not-contract", "record": True,
                "seen": {"first_seen_wib": NOW, "source": source, "status": "checked-not-contract",
                         "note": "eth_getCode 0x - EOA/wallet address, not a contract; no sale shape, not a lead."}}
    try:
        abi = curl_json(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
                        timeout=10).get("abi", [])
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
            "S1": s1, "S2": s2, "n_fns": len(names), "record": True,
            "seen": {"first_seen_wib": NOW, "source": source,
                     "status": "sale-shape-pass" if (s1 or s2) else "checked-not-sale-shape",
                     "note": f"S1={s1} S2={s2} fns={sorted(names)}"}}

# 3 contracts already shape-checked in the 2304 run (S1/S2 false) - record from that file, no re-fetch
pre = json.load(open(BASE + "hot-leg-2026-11-08-2304-shapecheck.json"))
log["recorded_from_2304_shapecheck"] = []
for s in pre:
    a = s["address"]
    seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
               "status": "checked-not-sale-shape",
               "note": f"S1={s['S1']} S2={s['S2']} fns={s['fns']} (shape-checked in run 2304)"}
    log["recorded_from_2304_shapecheck"].append(a)

feed = json.load(open(BASE + TAG + "-sourcify.json"))
items = feed if isinstance(feed, list) else feed.get("results", [])
seen_low = {k.lower() for k in seen}
to_check = [it["address"] for it in items if it["address"].lower() not in seen_low]
carryover = ["0x8c2f7bec2d7b31d9c706d25eb4d008f0754ce255",
             "0xb2625d56a7fc855bf7432b5584b390a4b4d9c7fd",
             "0xffbced696d2667cef82ba1306016c85da5cf7777",
             "0x4ef929af00cb93993c3d01834c4da79200d31e32",
             "0xa04513d85e02e1a1623a985269b3ebd46fa76b98",
             "0xafa58c073bf30bdbead63d60a18943b613598f72",
             "0xe37c757d96eac44f7ebcdfde446bf55da43a903d"]
jobs = [(a, "sourcify-feed") for a in to_check] + [(a, "boltbook-carryover") for a in carryover]
with ThreadPoolExecutor(max_workers=10) as ex:
    results = list(ex.map(lambda j: shape_check(*j), jobs))
for r in results:
    if r.get("record"):
        seen[r["addr"]] = r["seen"]
log["leg1_feed_new"] = to_check
log["leg1_shape_results"] = results
log["carryover_results"] = [r for r in results if r["addr"] in carryover]
log["sale_shapes"] = [r for r in results if r.get("result") == "sale-shape-pass"]
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
log["seen_total_after"] = len(seen)
log["elapsed_sec"] = round(time.time() - t0, 1)
json.dump(log, open(BASE + TAG + "-legs12-recovery.log", "w"), indent=1)
print(json.dumps(log, indent=1))
print("ELAPSED", round(time.time() - t0, 1))
