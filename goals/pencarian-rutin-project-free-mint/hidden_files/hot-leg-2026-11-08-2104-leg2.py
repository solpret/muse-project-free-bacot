#!/usr/bin/env python3
"""Hot-leg 2104 leg2: shape-check Driftnauts + Freedrop (new from census post) + retry 5 carryover unverified."""
import json, subprocess, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-2104"
NOW = "2026-11-08T21:04:38+07:00"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124",
            "0x8b47354E7b76B1970a0D06365c8244a810d37493"}
FREE = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
        "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted",
        "freeCardsRemaining"}
AGENT = {"agentId", "agentRegistry", "registry", "AGENT_ID", "AGENT_REGISTRY", "hasAgentId"}
RPC = "https://bsc-dataseed.bnbchain.org/"
seen = json.load(open(BASE + "hot-leg-seen.json"))
log = {"run": "free-mint-hot-leg 2026-11-08 21:04:38 WIB leg2"}
t0 = time.time()

def curl_json(url, timeout=20):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def shape_check(addr, source):
    if addr.lower() == REGISTRY.lower() or addr.lower() in {e.lower() for e in EXCLUDED}:
        return {"addr": addr, "skipped": "registry-or-excluded"}
    try:
        code = subprocess.run(["curl", "-sL", "--max-time", "15", "-X", "POST", RPC,
                               "-H", "Content-Type: application/json",
                               "-d", json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                                                 "params": [addr, "latest"]})],
                              capture_output=True, text=True, timeout=20).stdout
        code = json.loads(code).get("result")
    except Exception as ex:
        return {"addr": addr, "error": f"eth_getCode {ex}"}
    if code == "0x":
        seen[addr] = {"first_seen_wib": NOW, "source": source,
                      "status": "checked-not-contract",
                      "note": "eth_getCode 0x - EOA/wallet address, not a contract; no sale shape, not a lead."}
        return {"addr": addr, "result": "EOA-checked-not-contract"}
    try:
        abi = curl_json(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi").get("abi", [])
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
    seen[addr] = {"first_seen_wib": NOW, "source": source,
                  "status": "sale-shape-pass" if (s1 or s2) else "checked-not-sale-shape",
                  "note": f"S1={s1} S2={s2} fns={sorted(names)}"}
    return {"addr": addr, "result": "sale-shape-pass" if (s1 or s2) else "checked-not-sale-shape",
            "S1": s1, "S2": s2, "n_fns": len(names)}

bolt = ["0x6a926234d3767f2eeb3db12c1b4c9e2912c5589b",
        "0x9293756219863f27daa1363c7bb92c3b3874ac2b"]
log["leg2_boltbook_new"] = [shape_check(a, "boltbook-en") for a in bolt]
carry = ["0x8c2f7bec2d7b31d9c706d25eb4d008f0754ce255",
         "0xb2625d56a7fc855bf7432b5584b390a4b4d9c7fd",
         "0xffbced696d2667cef82ba1306016c85da5cf7777",
         "0x4ef929af00cb93993c3d01834c4da79200d31e32",
         "0xa04513d85e02e1a1623a985269b3ebd46fa76b98"]
log["leg2_boltbook_carryover"] = [shape_check(a, "boltbook-en") for a in carry]
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
log["seen_total_after"] = len(seen)
log["elapsed_sec"] = round(time.time() - t0, 1)
json.dump(log, open(BASE + TAG + "-leg2.log", "w"), indent=1)
print(json.dumps(log, indent=1))
