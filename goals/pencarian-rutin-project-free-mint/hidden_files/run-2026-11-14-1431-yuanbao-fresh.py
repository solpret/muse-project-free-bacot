#!/usr/bin/env python3
"""Run 1431 finalize: fresh YUANBAO free-pool read after browser (L) blocked.
Read-only; writes run-2026-11-14-1431-yuanbao-fresh.json."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-rpc.publicnode.com/", "https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]
YUAN = "0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
t0 = time.time()
out = {"started_wib": "2026-11-14T14:51+07:00"}
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a, str) and a.startswith("0x") and len(a) == 42 else enc_u(int(a))
    return d
def post_rpc(ep, payload, timeout=60):
    o = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(o)
def raw_call(addr, sig, args):
    data = build_data(sig, args)
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": addr, "data": data}, "latest"]}, timeout=60)
            if isinstance(r, dict) and isinstance(r.get("result"), str) and r["result"] not in ("0x",):
                return r["result"], ep
        except Exception:
            continue
    return None, None
def u(hexv):
    return int(hexv, 16) if hexv else None
for label, sig, args in [
    ("freeClaimed", "freeClaimed()", []),
    ("FREE_SUPPLY", "FREE_SUPPLY()", []),
    ("totalSupply", "totalSupply()", []),
    ("mintOpen", "mintOpen()", []),
    ("mintedBy_user", "mintedBy(address)", [USER]),
    ("balanceOf_user", "balanceOf(address)", [USER]),
]:
    raw, ep = raw_call(YUAN, sig, args)
    out[label] = {"value": u(raw), "ep": ep}
    print(label, "=", u(raw), "via", ep, flush=True)
# current block
for ep in EPS:
    try:
        r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=30)
        if isinstance(r, dict) and r.get("result"):
            out["block"] = int(r["result"], 16)
            print("block =", out["block"], "via", ep, flush=True)
            break
    except Exception:
        continue
out["elapsed_s"] = round(time.time() - t0, 1)
with open(BASE + "run-2026-11-14-1431-yuanbao-fresh.json", "w") as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
