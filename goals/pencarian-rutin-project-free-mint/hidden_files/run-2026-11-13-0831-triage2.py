#!/usr/bin/env python3
"""Triage2 for free-mint-search run 2026-11-13 08:31 WIB.
First on-chain reads (this job) for Boltbook-new contracts NOT in snapshot:
NDAEMN, DacityCoin, Foxglow. Generic NFT views + agent-shape views.
Read-only; writes run-2026-11-13-0831-triage2.json. No preview/mint."""
import json, subprocess, time, concurrent.futures
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def words(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
    except Exception:
        return None
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def read_one(name, addr, views):
    calls = []
    for i, (key, sig, *rest) in enumerate(views):
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": sel(sig) + (rest[0] if rest else "")}, "latest"]})
    res = {"address": addr, "views": {}, "summary": {}}
    for ep in EPS:
        try:
            r = post_rpc(ep, calls)
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
    ("agentFreeUsed", "agentFreeUsed()"),
    ("FREE_SUPPLY", "FREE_SUPPLY()"), ("FREE_MAX", "FREE_MAX()"),
    ("FREE_CAP", "FREE_CAP()"), ("MAX_SUPPLY", "MAX_SUPPLY()"),
    ("mintOpen", "mintOpen()"), ("mintStart", "mintStart()"),
    ("mintOpensAt", "mintOpensAt()"), ("mintEnd", "mintEnd()"),
    ("name", "name()"), ("symbol", "symbol()"),
    ("agentIdRegistry", "agentIdRegistry()"), ("registry", "registry()"),
    ("REGISTRY", "REGISTRY()"),
    ("mintsBy_user", "mintsBy(address)", enc_addr(USER)),
    ("holdsAgentId_user", "holdsAgentId(address)", enc_addr(USER)),
    ("balanceOf_user", "balanceOf(address)", enc_addr(USER)),
    ("freeClaimed_user", "freeClaimed(address)", enc_addr(USER))]
TARGETS = {
 "NDAEMN": ("0xa55d0dd67e443790fef78fe003e1c800201c1d08", GEN),
 "DacityCoin": ("0x90ddd762f407b3edf43f732cd5a68a9e4695a6bd", GEN),
 "Foxglow": ("0x6e159c9cd56beadb523b80d195dde39c042a1d48", GEN),
}
def main():
    t0 = time.time()
    out = {"started_wib": "2026-11-13T08:31+07:00", "reads": {}}
    try:
        r = post_rpc(EPS[0], {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
        out["block"] = int(r.get("result"), 16)
    except Exception as e:
        out["block_error"] = str(e)[:100]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(read_one, n, a, v): n for n, (a, v) in TARGETS.items()}
        for f in concurrent.futures.as_completed(futs):
            n = futs[f]
            try:
                out["reads"][n] = f.result()
            except Exception as e:
                out["reads"][n] = {"address": TARGETS[n][0], "error": str(e)[:120]}
    for n, r in out["reads"].items():
        if isinstance(r, dict):
            r["summary"] = {k: v for k, v in r.get("views", {}).items() if v is not None}
    out["elapsed_s"] = round(time.time() - t0, 1)
    print(json.dumps(out, indent=1))
    json.dump(out, open(BASE + "run-2026-11-13-0831-triage2.json", "w"), indent=1)
if __name__ == "__main__":
    main()
