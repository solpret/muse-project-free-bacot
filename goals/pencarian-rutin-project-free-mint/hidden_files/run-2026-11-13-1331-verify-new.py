#!/usr/bin/env python3
"""Verify new contracts for free-mint-search run 2026-11-13 13:31 WIB.
- 0xe589A94316C68d4A4f008f841Deb7e9612445244: Sourcify feed new, S1=true
  (84 fns: mint+quote+free+agent). Full on-chain read: identity, free
  pool, user slot/quote, launch/open times, registry, contractURI.
- 0xc972e47d067664effb42ea9f1a2ca667065e4c17: Boltbook EN+ZH new vs
  hot-leg-seen. Sourcify ABI + selector probe + basic reads.
Read-only; writes run-2026-11-13-1331-verify-new.json. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENT_ID = 107187496765866644729837695198686237165740365523485558112864918211974996443404
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
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
def abi_fns(addr):
    try:
        mj = json.loads(curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", 20))
        abi = mj.get("abi") or []
        fns = [f for f in abi if f.get("type") == "function"]
        return {"n_fns": len(fns),
                "fn_sigs": sorted(set(f.get("name") + "(" + ",".join(i.get("type","") for i in f.get("inputs",[])) + ")" for f in fns)),
                "verified": bool(abi)}
    except Exception as e:
        return {"error": str(e)[:120]}
E589 = "0xe589A94316C68d4A4f008f841Deb7e9612445244"
C972 = "0xc972e47d067664effb42ea9f1a2ca667065e4c17"
VIEWS_E589 = [
    ("name", "name()"), ("symbol", "symbol()"), ("decimals", "decimals()"),
    ("totalSupply", "totalSupply()"), ("totalMinted", "totalMinted()"),
    ("FREE_SUPPLY", "FREE_SUPPLY()"), ("FREE_PER_WALLET", "FREE_PER_WALLET()"),
    ("FREE_MODE", "FREE_MODE()"), ("freeMinted", "freeMinted()"),
    ("freeRemaining", "freeRemaining()"), ("isFreeOpen", "isFreeOpen()"),
    ("freeStart", "freeStart()"), ("mintStart", "mintStart()"),
    ("saleStart", "saleStart()"), ("mintOpensAt", "mintOpensAt()"),
    ("startTime", "startTime()"), ("START_TIME", "START_TIME()"),
    ("openTime", "openTime()"), ("opened", "opened()"),
    ("mintOpen", "mintOpen()"), ("saleOpen", "saleOpen()"),
    ("MAX_SUPPLY", "MAX_SUPPLY()"), ("price", "price()"),
    ("mintPrice", "mintPrice()"), ("PRICE", "PRICE()"),
    ("agentIdRegistry", "agentIdRegistry()"), ("registry", "registry()"),
    ("agentRegistry", "agentRegistry()"),
    ("freeAvailable_user", "freeAvailable(address)", enc_addr(USER)),
    ("freeClaimed_user", "freeClaimed(address)", enc_addr(USER)),
    ("freeMintedBy_user", "freeMintedBy(address)", enc_addr(USER)),
    ("freeMintedByAgent_user", "freeMintedByAgent(uint256)", enc_u(AGENT_ID)),
    ("freeMintedByHandle_user", "freeMintedByHandle(uint256)", enc_u(AGENT_ID)),
    ("quote_user_1", "quote(address,uint256)", enc_addr(USER) + enc_u(1)),
    ("costOf_user_1", "costOf(address,uint256)", enc_addr(USER) + enc_u(1)),
    ("balanceOf_user", "balanceOf(address)", enc_addr(USER)),
    ("token", "token()"), ("owner", "owner()"),
    ("contractURI", "contractURI()"), ("tokenURI_0", "tokenURI(uint256)", enc_u(0)),
    ("tokenURI_1", "tokenURI(uint256)", enc_u(1)),
]
VIEWS_C972 = [
    ("name", "name()"), ("symbol", "symbol()"), ("totalSupply", "totalSupply()"),
    ("totalMinted", "totalMinted()"), ("freeMinted", "freeMinted()"),
    ("FREE_SUPPLY", "FREE_SUPPLY()"), ("MAX_SUPPLY", "MAX_SUPPLY()"),
    ("mintOpen", "mintOpen()"), ("mintStart", "mintStart()"),
    ("agentIdRegistry", "agentIdRegistry()"), ("registry", "registry()"),
    ("freeClaimed_user", "freeClaimed(address)", enc_addr(USER)),
    ("balanceOf_user", "balanceOf(address)", enc_addr(USER)),
    ("price", "price()"), ("owner", "owner()"),
]
def main():
    t0 = time.time()
    out = {"started_wib": "2026-11-13T13:31+07:00"}
    out["e589_abi"] = abi_fns(E589)
    r = read_one(E589, VIEWS_E589)
    r["summary"] = {k: v for k, v in r.get("views", {}).items() if v is not None}
    out["e589"] = r
    out["c972_abi"] = abi_fns(C972)
    r2 = read_one(C972, VIEWS_C972)
    r2["summary"] = {k: v for k, v in r2.get("views", {}).items() if v is not None}
    out["c972"] = r2
    out["elapsed_s"] = round(time.time() - t0, 1)
    print(json.dumps(out, indent=1))
    json.dump(out, open(BASE + "run-2026-11-13-1331-verify-new.json", "w"), indent=1)
if __name__ == "__main__":
    main()
