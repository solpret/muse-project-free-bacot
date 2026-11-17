#!/usr/bin/env python3
"""DRAGON freeMint preview via baw (read-only simulation, no broadcast).
Writes run-2026-11-17-0731-dragon-preview.json + verdict to stdout."""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
import importlib.util
spec = importlib.util.spec_from_file_location("fcfs", "/home/hatch/workspace/fast_exec/fcfs_fast.py")
fcfs = importlib.util.module_from_spec(spec); spec.loader.exec_module(fcfs)
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
CFG = {"chain_id": "56",
       "agent_wallet": "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E",
       "mint_contract": "0xfc191b76041498b14dcae3c802af3389c74263e6",
       "free_calldata": "0x5b70ea9f",
       "expected_delta_raw": None}
class Log:
    def write(self, m): print("[log]", m)
prev = fcfs.run_preview(CFG, Log())
json.dump(prev, open(f"{HF}/run-2026-11-17-0731-dragon-preview.json", "w"), indent=1)
clean, why = fcfs.preview_is_clean(CFG, prev)
print("PREVIEW_CODE:", fcfs._preview_code(prev))
print("PREVIEW_CLEAN:", clean)
print("PREVIEW_WHY:", why)
print("REQUEST_ID:", (prev.get("data") or {}).get("requestId"))
print("PREVIEW_KEYS:", sorted((prev.get("data") or {}).keys()))
