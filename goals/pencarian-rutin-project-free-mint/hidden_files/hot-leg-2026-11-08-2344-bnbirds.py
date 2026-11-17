#!/usr/bin/env python3
"""Hot-leg 2344: probe BNBirds 0x5d69... (Boltbook-new, Sourcify unverified per post).
eth_getCode + a few known view selectors; no ABI available so no S1/S2 verdict possible."""
import json, subprocess
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc.publicnode.com/"]
ADDR = "0x5d6967fe8400c4504c5035e1fb834967da7efbde"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def post(ep, payload, timeout=12):
    try:
        out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                              "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                             capture_output=True, text=True, timeout=timeout + 5).stdout
        return json.loads(out) if out.strip() else {}
    except Exception:
        return {}

def rpc(method, params):
    for ep in EPS:
        r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
        if r.get("result") is not None:
            return r["result"], ep
    return None, None

def ti(v):
    try: return int(v, 16)
    except Exception: return None

code, ep = rpc("eth_getCode", [ADDR, "latest"])
out = {"addr": ADDR, "code_len": len(code) if code else None, "code_ep": ep}
if code and code != "0x":
    for sig in ["totalSupply()", "freeMinted()", "freeClaimed()", "MAX_SUPPLY()",
                "FREE_SUPPLY()", "totalMinted()", "mintOpen()"]:
        r, _ = rpc("eth_call", [{"to": ADDR, "data": sel(sig)}, "latest"])
        out[sig] = ti(r)
    try:
        abi = subprocess.run(["curl", "-sL", "--max-time", "12",
                              f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi"],
                             capture_output=True, text=True, timeout=15).stdout
        out["sourcify_abi_n"] = len(json.loads(abi).get("abi", [])) if abi.strip() else "fetch-empty"
    except Exception as ex:
        out["sourcify_abi_error"] = str(ex)
print(json.dumps(out, indent=1))
json.dump(out, open(BASE + "hot-leg-2026-11-08-2344-bnbirds-probe.json", "w"), indent=1)
