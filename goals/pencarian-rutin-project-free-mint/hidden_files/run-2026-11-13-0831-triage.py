#!/usr/bin/env python3
"""Triage for free-mint-search run 2026-11-13 08:31 WIB.
Fresh reads: ONLYAI Crystals (Boltbook lead, contract from search) +
PIXEL BOYZ (Boltbook post today claims free pool 287->136; excluded age-over-48h 11-07 - confirm same-phase drain).
Read-only; writes run-2026-11-13-0831-triage.json. No preview/mint."""
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
TARGETS = {
 "ONLYAI": ("0x156482AD3F0eebD8E3F70d494ebD1dA3F738f5Ba",
    [("totalSupply", "totalSupply()"), ("totalMinted", "totalMinted()"),
     ("freeMinted", "freeMinted()"), ("freeClaimed", "freeClaimed()"),
     ("FREE_SUPPLY", "FREE_SUPPLY()"), ("MAX_SUPPLY", "MAX_SUPPLY()"),
     ("mintOpen", "mintOpen()"), ("mintStart", "mintStart()"),
     ("mintOpensAt", "mintOpensAt()"), ("MINT_START", "MINT_START()"),
     ("OPEN_TIME", "OPEN_TIME()"), ("name", "name()"), ("symbol", "symbol()"),
     ("agentIdRegistry", "agentIdRegistry()"), ("registry", "registry()"),
     ("mintsBy_user", "mintsBy(address)", enc_addr(USER)),
     ("holdsAgentId_user", "holdsAgentId(address)", enc_addr(USER)),
     ("balanceOf_user", "balanceOf(address)", enc_addr(USER)),
     ("freeClaimed_user", "freeClaimed(address)", enc_addr(USER))]),
 "PixelBoyz": ("0xaFB50403C0838D5b45F8748138BA33A70E23b8cf",
    [("totalSupply", "totalSupply()"), ("totalMinted", "totalMinted()"),
     ("freeMinted", "freeMinted()"), ("freeClaimed", "freeClaimed()"),
     ("FREE_SUPPLY", "FREE_SUPPLY()"), ("MAX_SUPPLY", "MAX_SUPPLY()"),
     ("mintOpen", "mintOpen()"), ("freeSaleActive", "freeSaleActive()"),
     ("freeAllocationRemaining", "freeAllocationRemaining()"),
     ("freeSaleStart", "freeSaleStart()"), ("name", "name()"), ("symbol", "symbol()"),
     ("agentIdRegistry", "agentIdRegistry()"),
     ("walletFreeRemaining_user", "walletFreeRemaining(address)", enc_addr(USER)),
     ("freeMintedByWallet_user", "freeMintedByWallet(address)", enc_addr(USER)),
     ("hasAgentId_user", "hasAgentId(address)", enc_addr(USER)),
     ("balanceOf_user", "balanceOf(address)", enc_addr(USER))]),
}
def main():
    t0 = time.time()
    out = {"started_wib": "2026-11-13T08:31+07:00", "reads": {}}
    try:
        r = post_rpc(EPS[0], {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
        out["block"] = int(r.get("result"), 16)
    except Exception as e:
        out["block_error"] = str(e)[:100]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
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
    json.dump(out, open(BASE + "run-2026-11-13-0831-triage.json", "w"), indent=1)
if __name__ == "__main__":
    main()
