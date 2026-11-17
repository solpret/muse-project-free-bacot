#!/usr/bin/env python3
"""Extra verify run 1931: CinderCrucible, Apex, MossSignal, AgentBubble, Mihao.
One JSON-RPC batch per contract, read-only. Writes run-2026-11-13-1931-verify-extra.json."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def words(h):
    try:
        b = bytes.fromhex(h[2:])
        return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
    except Exception:
        return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def read_one(name, addr, views):
    calls = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
              "params": [{"to": addr, "data": sel(sig) + (rest[0] if rest else "")}, "latest"]}
             for i, (key, sig, *rest) in enumerate(views)]
    res = {"address": addr, "views": {}}
    for ep in EPS:
        try:
            r = post(ep, calls)
            if not isinstance(r, list) or len(r) != len(calls):
                continue
            for it, (key, sig, *rest) in zip(r, views):
                if not isinstance(it, dict) or "error" in it or not it.get("result") or it["result"] == "0x":
                    res["views"][key] = None; continue
                w = words(it["result"])
                res["views"][key] = w[0] if w is not None and len(w) == 1 else w
            res["endpoint"] = ep
            return res
        except Exception as e:
            res.setdefault("errors", []).append(str(e)[:80])
    return res
GEN = [("totalSupply", "totalSupply()"), ("totalMinted", "totalMinted()"),
       ("freeMinted", "freeMinted()"), ("freeClaimed", "freeClaimed()"),
       ("FREE_SUPPLY", "FREE_SUPPLY()"), ("FREE_CAP", "FREE_CAP()"),
       ("FREE_MAX", "FREE_MAX()"), ("MAX_SUPPLY", "MAX_SUPPLY()"),
       ("mintOpen", "mintOpen()"), ("saleOpen", "saleOpen()"),
       ("saleStart", "saleStart()"), ("saleEnd", "saleEnd()"),
       ("freeAvailable", "freeAvailable(address)", enc_addr(USER)),
       ("freeClaimed_user", "freeClaimed(address)", enc_addr(USER)),
       ("balanceOf_user", "balanceOf(address)", enc_addr(USER)),
       ("costOf_user_1", "costOf(address,uint256)", enc_addr(USER) + enc_u(1))]
TARGETS = {
    "CinderCrucible": "0x73f1A09e49cA70F8ac6a2F8673Bf7f0f69219b23",
    "Apex": "0x6DdE73D48Ed92c9C60B77711d37fEc0B03ACBE18",
    "MossSignal": "0xb2e5d82900b854d3cb8c6bb917426abadb687f68",
    "AgentBubble": "0x0d72970046c056db90888351b739246f468bff0b",
    "Mihao": "0xea4ef9da567f59ea7b5f5b7e08305f4e613bab73",
}
t0 = time.time()
out = {"started_wib": "2026-11-13 19:31 WIB", "reads": {}}
for name, addr in TARGETS.items():
    out["reads"][name] = read_one(name, addr, GEN)
out["elapsed_s"] = round(time.time() - t0, 1)
out["block"] = None
try:
    r = post(EPS[0], {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})
    out["block"] = int(r["result"], 16)
except Exception:
    pass
json.dump(out, open(BASE + "run-2026-11-13-1931-verify-extra.json", "w"), indent=1)
print(json.dumps({k: v["views"] for k, v in out["reads"].items()}, indent=1)[:3000])
print("block", out["block"], "elapsed", out["elapsed_s"])
