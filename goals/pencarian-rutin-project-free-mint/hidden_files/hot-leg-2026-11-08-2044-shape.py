#!/usr/bin/env python3
"""Hot-leg 2044 leg2 shape-check: JINCHAN + AgentVOLT v6 + OBSIDIAN (new addresses from Boltbook EN/ZH front pages)."""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-2044"
NOW = "2026-11-08T20:44:38+07:00"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124",
            "0x8b47354E7b76B1970a0D06365c8244a810d37493"}
FREE = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
        "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted",
        "freeCardsRemaining"}
AGENT = {"agentId", "agentRegistry", "registry", "AGENT_ID", "AGENT_REGISTRY", "hasAgentId"}
seen = json.load(open(BASE + "hot-leg-seen.json"))
log = {"run": TAG + " leg2 shape-check"}
t0 = time.time()
def shape_check(addr, source):
    if addr.lower() == REGISTRY.lower() or addr.lower() in {e.lower() for e in EXCLUDED}:
        return {"addr": addr, "skipped": "registry-or-excluded"}
    try:
        code = batch([("eth_getCode", [addr, "latest"])], timeout=15)[0]
    except Exception as ex:
        return {"addr": addr, "error": f"eth_getCode {ex}"}
    if code == "0x":
        seen[addr] = {"first_seen_wib": NOW, "source": source, "status": "checked-not-contract",
                      "note": "eth_getCode 0x - EOA, not a contract."}
        return {"addr": addr, "result": "EOA-checked-not-contract"}
    try:
        out = subprocess.run(["curl", "-sL", "--max-time", "20",
                              f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                             capture_output=True, text=True).stdout
        abi = json.loads(out).get("abi", [])
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
addrs = [("0xccc127d1a7ef1e385757784a9878f7279bf3b19d", "boltbook-zh-19"),
         ("0xe0deb1a792eebd9cba7fd74b70a283bfa2630771", "boltbook-en-17"),
         ("0x57e3f981791c3be85d74e74a2f402d7d00f6ed9c", "boltbook-zh-5")]
log["shape_checks"] = [shape_check(a, s) for a, s in addrs]
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
log["seen_total_after"] = len(seen)
log["elapsed_sec"] = round(time.time() - t0, 1)
json.dump(log, open(BASE + TAG + "-shape.log", "w"), indent=1)
print(json.dumps(log, indent=1))
