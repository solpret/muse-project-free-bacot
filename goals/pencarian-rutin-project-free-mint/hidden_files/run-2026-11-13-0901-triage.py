#!/usr/bin/env python3
"""Triage for free-mint-search run 2026-11-13 09:01 WIB.
Targets: 4 new Boltbook addresses + SEVENFOLD (first read by this job)
+ THYRK re-read. On-chain batch reads (name/symbol/supply/free views/
time views/agent refs/user slot) + Sourcify metadata (verifiedAt, ABI fn
names, registry ref). Read-only; writes run-2026-11-13-0901-triage.json.
No preview/mint."""
import json, subprocess, time, re
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENT_ID = 107187496765866644729837695198686237165740365523485558112864918211974996443404
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
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
def curl(url, timeout=25):
    try:
        return subprocess.run(["curl", "-sL", "--max-time", str(timeout), url],
                              capture_output=True, text=True, timeout=timeout + 5).stdout
    except Exception:
        return ""
def read_one(addr, views):
    calls = []
    for i, (key, sig, *rest) in enumerate(views):
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": sel(sig) + (rest[0] if rest else "")}, "latest"]})
    res = {"address": addr, "views": {}}
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
VIEWS = [("name", "name()"), ("symbol", "symbol()"),
    ("totalSupply", "totalSupply()"), ("totalMinted", "totalMinted()"),
    ("freeMinted", "freeMinted()"), ("freeClaimed", "freeClaimed()"),
    ("freeRemaining", "freeRemaining()"), ("FREE_SUPPLY", "FREE_SUPPLY()"),
    ("FREE_CAP", "FREE_CAP()"), ("FREE_MAX", "FREE_MAX()"),
    ("MAX_SUPPLY", "MAX_SUPPLY()"), ("mintOpen", "mintOpen()"),
    ("mintStart", "mintStart()"), ("mintOpensAt", "mintOpensAt()"),
    ("saleStart", "saleStart()"), ("START_TIME", "START_TIME()"),
    ("agentIdRegistry", "agentIdRegistry()"), ("registry", "registry()"),
    ("price", "price()"), ("mintPrice", "mintPrice()"),
    ("balanceOf_user", "balanceOf(address)", enc_addr(USER)),
    ("freeClaimedByAgent_user", "freeClaimedByAgent(uint256)", enc_u(AGENT_ID)),
    ("mintsBy_user", "mintsBy(address)", enc_addr(USER)),
    ("holdsAgentId_user", "holdsAgentId(address)", enc_addr(USER)),
    ("costOf_user_1", "costOf(address,uint256)", enc_addr(USER) + enc_u(1))]
TARGETS = {
 "BB-new-0x1558": "0x1558d52c7424b2cbdd9a1771a7088f11312f3a55",
 "BB-new-0x8444": "0x84448336a7387397da5ce910cfe1462aca53c024",
 "BB-new-0x9adc": "0x9adc0bb1c1fed65d1b8b6af7028527dbcb948b6c",
 "BB-new-0xee7d": "0xee7d3a695476f2645f0f61ff493f02664ed4908d",
 "SEVENFOLD": "0x4ca724a354db4f743607ecc1a5f117b2e617c8ae",
 "THYRK": "0x4d90ffc3075fb8897edff6d7c6269c906664a20e",
 "OLIVER-abi": "0xad86e4d52e55709d1bda08f922853d4b109e0810",
}
def main():
    t0 = time.time()
    out = {"started_wib": "2026-11-13T09:01+07:00", "reads": {}}
    try:
        r = post_rpc(EPS[1], {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
        out["block"] = int(r.get("result"), 16)
    except Exception as e:
        out["block_error"] = str(e)[:100]
    for name, addr in TARGETS.items():
        if name == "OLIVER-abi":
            continue
        out["reads"][name] = read_one(addr, VIEWS)
    # Sourcify metadata for triage targets + OLIVER ABI (slot-signature check)
    out["sourcify"] = {}
    for name, addr in TARGETS.items():
        try:
            meta = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", 20)
            mj = json.loads(meta)
            abi = mj.get("abi") or []
            fns = [f.get("name") for f in abi if f.get("type") == "function"]
            src = json.dumps(mj).lower()
            out["sourcify"][name] = {
                "verified": bool(abi), "verifiedAt": mj.get("verifiedAt") or mj.get("match", {}).get("verifiedAt"),
                "n_fns": len(fns), "fns": fns,
                "agent_registry_ref": REGISTRY in src,
                "has_mint": any(n in fns for n in ("mint", "claimFree", "mintFree", "claimFreeAgent")),
                "has_quote": any("quote" in n.lower() or "cost" in n.lower() for n in fns),
                "free_views": [n for n in fns if "free" in n.lower()],
            }
        except Exception as e:
            out["sourcify"][name] = {"status": "fetch-failed", "error": str(e)[:120]}
    # Boltbook front-page context: which post mentions each new address
    html = curl("https://boltbook.fun/", 25)
    out["boltbook_ctx"] = {}
    for name, addr in TARGETS.items():
        idx = html.lower().find(addr.lower())
        if idx >= 0:
            seg = html[max(0, idx - 600):idx + 100]
            seg = re.sub(r"<[^>]+>", " ", seg)
            seg = re.sub(r"\s+", " ", seg).strip()
            out["boltbook_ctx"][name] = seg[-600:]
        else:
            out["boltbook_ctx"][name] = "address not found in front-page HTML"
    out["elapsed_s"] = round(time.time() - t0, 1)
    print(json.dumps(out, indent=1)[:6000])
    json.dump(out, open(BASE + "run-2026-11-13-0901-triage.json", "w"), indent=1)
if __name__ == "__main__":
    main()
