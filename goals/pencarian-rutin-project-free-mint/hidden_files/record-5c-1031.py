#!/usr/bin/env python3
"""Record route 5c results for run 2026-11-07-1031 into track-c-scan-checked.json
(same format as prior triage runs) + annotate the 0x892E correction."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
results = json.load(open(f"{BASE}/trackc-5c-1031.json"))
before_list = len(checked.get("checked", []))
before_dict = sum(1 for k in checked if k.startswith("0x"))

for r in results:
    a = r["address"]
    if a not in checked.get("checked", []):
        checked.setdefault("checked", []).append(a)
    checked[a] = {
        "source": "run-2026-11-07-1031-5c",
        "status": "checked-not-sale-shape",
        "note": (f"mint_count={r['mint_count']} S1={r['S1']} S2={r['S2']} "
                 f"mint={r['has_mint']} quote={r['has_quote']} free={r['free_views']} "
                 f"agent={bool(r['gate_names']) or r['registry_bytes'] is True} "
                 f"sourcify={r['sourcify']} reg_bytes={r['registry_bytes']}"),
    }

# Correction annotation for 0x892E: prior 5c entry recorded agent=False via a
# NAME-ONLY agent test; fresh 5a verification proves AGENT_ID_REGISTRY()
# returns the exact registry address and registry bytes are in the code.
addr892 = "0x892E438425b3A41BC75b25C22Fd878b3fa2e308d"
if addr892 in checked:
    checked[addr892]["correction_1031"] = (
        "Route 5a re-check 2026-11-07-1031: S1 PASSES. AGENT_ID_REGISTRY() = "
        "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (exact); registry bytes in "
        "deployed code = True; mint=True quote=True free=['freeUsed']. Prior "
        "agent=False came from a name-only ABI test that misses the "
        "AGENT_ID_REGISTRY constant. See trackc-892e-verify-1031.json. "
        "Original verdict preserved above; parent decides promotion.")
    checked[addr892]["status_1031"] = "sale-shape-S1 (route 5a, corrected)"

json.dump(checked, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)
print(f"checked list: {before_list} -> {len(checked.get('checked', []))}")
print(f"dict entries: {before_dict} -> {sum(1 for k in checked if k.startswith('0x'))}")
print("recorded 5c:", [r["address"] for r in results])
print("annotated 0x892E correction")
