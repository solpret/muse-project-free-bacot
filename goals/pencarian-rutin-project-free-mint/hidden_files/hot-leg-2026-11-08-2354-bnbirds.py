#!/usr/bin/env python3
"""Hot-leg 2354: BNBirds retry - Sourcify ABI check (ABI-0 in 2344, not recorded)."""
import json, subprocess
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0x5d6967fe8400c4504c5035e1fb834967da7efbde"
def curl_json(url, timeout=12):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),url],
                         capture_output=True, text=True, timeout=timeout+5).stdout
    return json.loads(out)
try:
    abi = curl_json(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi").get("abi", [])
    names = {e["name"] for e in abi if e.get("type")=="function"}
except Exception as ex:
    names = None
    print("ABI fetch error:", ex)
out = {"addr": ADDR, "sourcify_abi_n": None if names is None else len(names)}
if names is not None:
    FREE={"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
    AGENT={"agentId","agentRegistry","registry","AGENT_ID","AGENT_REGISTRY","hasAgentId"}
    s1=any(n.lower().startswith("mint") for n in names) and bool(names & {"quote","cost"}) and bool(names & FREE) and bool(names & AGENT)
    s2=bool(names & {"name","symbol","decimals","totalSupply"}) and "mintFree" in names and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and bool(names & AGENT)
    out.update({"result": "sale-shape-pass" if (s1 or s2) else "checked-not-sale-shape", "S1": s1, "S2": s2, "names": sorted(names)})
    if s1 or s2:
        print("SALE SHAPE PASS - needs full triage")
print(json.dumps(out, indent=1))
json.dump(out, open(BASE+"hot-leg-2026-11-08-2354-bnbirds-probe.json","w"), indent=1)
