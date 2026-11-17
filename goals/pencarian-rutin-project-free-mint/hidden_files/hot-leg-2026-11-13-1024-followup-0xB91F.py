#!/usr/bin/env python3
"""Follow-up verification for probe-possible-sale 0xB91FfD05... (hot-leg 1024):
bytecode selector scan for mint/quote fns + value reads (saleOpen, freeClaimed,
registry value, start-time views, name/symbol). Read-only."""
import json, subprocess
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
ADDR = "0xB91FfD05C37D4bc91b588100309bDc5Fa6D70aCd"

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

SIGS = ["mintFree()", "claimFree()", "mint(address,uint256)", "mint(uint256)",
        "mintWithAgentId(address,uint256)", "quote(address,uint256)",
        "costOf(address,uint256)", "getQuote(address,uint256)",
        "freeClaimed(address)", "freeFor(address)", "freeAvailable(address)",
        "saleStart()", "mintStart()", "mintOpensAt()", "saleOpensAt()",
        "freeSharesRemaining()", "freeMinted()", "freeLeft()",
        "name()", "symbol()", "decimals()"]
VIEWS = [("saleOpen", False), ("freeClaimed", False), ("totalSupply", False),
         ("AGENT_ID_REGISTRY", False), ("freeClaimed", True), ("freeFor", True),
         ("freeAvailable", True), ("saleStart", False), ("mintStart", False),
         ("mintOpensAt", False), ("saleOpensAt", False),
         ("freeSharesRemaining", False), ("freeMinted", False), ("freeLeft", False)]

reqs = [{"jsonrpc": "2.0", "id": 0, "method": "eth_getCode", "params": [ADDR, "latest"]}]
for i, (fn, uarg) in enumerate(VIEWS, start=1):
    data = sel(fn + ("(address)" if uarg else "()")) + (USER_PAD if uarg else "")
    reqs.append({"jsonrpc": "2.0", "id": i, "method": "eth_call",
                 "params": [{"to": ADDR, "data": data}, "latest"]})
p = subprocess.run(["curl", "-sS", "-m", "30", "-A", "Mozilla/5.0",
                    "-H", "Content-Type: application/json", "-d", json.dumps(reqs),
                    "https://bsc-dataseed.binance.org/"],
                   capture_output=True, text=True, timeout=40)
out = {"contract": ADDR, "selectors_in_bytecode": {}, "views": {}}
resp = json.loads(p.stdout)
items = resp if isinstance(resp, list) else [resp]
code = ""
for it in items:
    if it.get("id") == 0:
        code = it.get("result") or ""
        out["code_len"] = len(code)
        continue
    i = it.get("id")
    if i is None or i > len(VIEWS):
        continue
    fn, uarg = VIEWS[i - 1]
    r = it.get("result")
    key = fn + ("_user" if uarg else "")
    if r and isinstance(r, str) and len(r) >= 66 and not it.get("error"):
        raw = r[2:]
        if fn in ("name", "symbol"):
            try:
                ln = int(raw[64:128], 16)
                out["views"][key] = bytes.fromhex(raw[128:128 + ln * 2]).decode("utf-8", "replace")
            except Exception:
                out["views"][key] = r[:80]
        elif fn == "AGENT_ID_REGISTRY":
            out["views"][key] = "0x" + raw[-40:]
        else:
            try:
                out["views"][key] = int(raw[-64:], 16)
            except Exception:
                out["views"][key] = r[:80]
    else:
        out["views"][key] = None  # revert / no such fn
if code:
    code_low = code.lower()
    for s in SIGS:
        s_hex = sel(s)[2:]
        out["selectors_in_bytecode"][s] = s_hex in code_low
json.dump(out, open(f"{HF}/hot-leg-2026-11-13-1024-followup-0xB91F.json", "w"), indent=1)
print(json.dumps(out, indent=1))
