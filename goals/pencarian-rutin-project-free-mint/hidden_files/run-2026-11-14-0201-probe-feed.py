#!/usr/bin/env python3
"""Sourcify feed probe for free-mint-search run 2026-11-14 02:01 WIB.
Shape-checks the 15 feed contracts NOT in hot-leg-seen (verifiedAt 18:14-19:07Z).
Agent-shape: registry 0x60B926...22F in ABI/bytecode, AgentGate, free-mint fn,
free-supply constant; sale-shape S1/S2 per body. Read-only; no preview/mint."""
import json, subprocess, time, re
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG = "60b9262456de011f7d15a54cdd8c48baa8b022f"
ADDRS = [
 "0xfB70c26dE2AA5fB02Fa2342EaDe5c32Fbf875E8E",
 "0x8b7aB23DCB21A1209b821Da1d53f93E12b667C95",
 "0x9025871F606Dc6dAc15aE331DB83ff5Cd83557A7",
 "0x027FFe566B1F3f9Bb3Ddbd835DD01d0b62Af9DB7",
 "0x3811e5Fc190589764d2653A5E6fC16B4080Fc4DE",
 "0x9a266cceA08d3E8628224Cb68bc240fEd47b1E76",
 "0x0FA947aE540F35b782e4eF35B43fAD5284DEc3d1",
 "0x5e8A8a4A3ebFde53afcb50722F82359E3586D0bd",
 "0xfF172b79d040faefA1Bf34B47151edc87130246E",
 "0x76E0471d81D1D4027046b8d381E6a064CeC9c0e4",
 "0x8b5ca265B7FAf150839E9ab47D1354f245868c5e",
 "0x4a2A838eeCf26614C25886281FAF1b54683660bc",
 "0x0d29a23fe8C6AFAFD2237CbF812a5b1D7FE6ab44",
 "0x2f0980Ad16A96f7287087E242259736ab59e6531",
 "0x912DcAfaF5114A888D60f58B3A5141c67Cc5FAD5",
]
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
t0 = time.time()

def curl(url, timeout=25):
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url],
                           capture_output=True, text=True, timeout=timeout + 5)
        return r.stdout
    except Exception as e:
        return ""

def rpc(ep, payload, timeout=20):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def get_code(addr):
    for ep in EPS:
        try:
            r = rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                         "params": [addr, "latest"]}, timeout=20)
            if isinstance(r, dict) and r.get("result"):
                return r["result"]
        except Exception:
            continue
    return None

FREE_PAT = re.compile(r"free|FREE", re.I)
MINT_PAT = re.compile(r"mint|claim", re.I)
QUOTE_PAT = re.compile(r"quote|cost|price", re.I)

results = {}
for a in ADDRS:
    row = {"address": a}
    raw = curl(f"https://sourcify.dev/server/v2/contract/56/{a}", timeout=25)
    try:
        meta = json.loads(raw)
        abi = meta.get("abi") or meta.get("metadata", {}).get("output", {}).get("abi") or []
        if not abi and isinstance(meta.get("stdJson"), dict):
            abi = meta["stdJson"].get("output", {}).get("abi") or []
        fns = [x.get("name", "") for x in abi if isinstance(x, dict) and x.get("type") == "function"]
        row["verified"] = True
        row["fn_count"] = len(fns)
        row["fns"] = fns
        row["has_mint"] = any(MINT_PAT.search(f) for f in fns)
        row["has_free_view"] = any(FREE_PAT.search(f) for f in fns)
        row["has_quote"] = any(QUOTE_PAT.search(f) for f in fns)
        row["has_agentgate"] = any("agent" in f.lower() or "gate" in f.lower() for f in fns)
        row["abi_registry_ref"] = REG in raw.lower()
    except Exception as e:
        row["verified"] = False
        row["abi_error"] = str(e)[:120]
        row["fns"] = []
    code = get_code(a)
    if code:
        row["code_bytes"] = (len(code) - 2) // 2
        row["code_registry_bytes"] = REG in code.lower()
    else:
        row["code_bytes"] = None
        row["code_registry_bytes"] = None
    row["agent_shaped"] = bool(
        (row.get("abi_registry_ref") or row.get("code_registry_bytes"))
        or (row.get("has_agentgate") and (row.get("has_mint") or row.get("has_free_view"))))
    results[a] = row
    print(a, "verified" if row.get("verified") else "NOT_VERIFIED",
          "fns", row.get("fn_count"), "mint", row.get("has_mint"),
          "free", row.get("has_free_view"), "quote", row.get("has_quote"),
          "agentgate", row.get("has_agentgate"), "regABI", row.get("abi_registry_ref"),
          "regCODE", row.get("code_registry_bytes"), "codeB", row.get("code_bytes"),
          "AGENT_SHAPED", row["agent_shaped"], flush=True)

json.dump({"run": "2026-11-14-0201", "elapsed_s": round(time.time() - t0, 1),
           "results": results},
          open(BASE + "run-2026-11-14-0201-probe-feed.json", "w"), indent=1)
print("DONE elapsed", round(time.time() - t0, 1))
