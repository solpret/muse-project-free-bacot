#!/usr/bin/env python3
"""Discovery for free-mint-search run 2026-11-13 17:31: Sourcify
recently-verified feed (limit 20, parse via 'results') + Boltbook EN+ZH,
shape-check only contracts new vs hot-leg-seen.json.
Shape-check fallback (hot-leg 1014 finding: Sourcify ABI route broken -
plural 404 even for verified, singular returns metadata only):
  1) Sourcify singular route; if ABI present, use it.
  2) Else eth_getCode selector probe (bsc-dataseed): check 4-byte selectors
     for mint / quote-cost / free-view / agent fns in runtime bytecode.
A probe-positive contract is NOT a lead by itself - it needs full on-chain
shape verification; a probe-negative contract is recorded checked with the
probe evidence (Sourcify route broken, so NOT declared not-sale-shape on
Sourcify alone). Read-only; writes run-2026-11-13-1731-discovery.json."""
import json, re, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
def curl(url, timeout=25):
    try:
        return subprocess.run(["curl","-sL","--max-time",str(timeout),url],
            capture_output=True, text=True, timeout=timeout+5).stdout
    except Exception:
        return ""
def rpc_post(ep, payload, timeout=20):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout+5).stdout
    return json.loads(out)
MINT_S = ["mint(uint256)","mint(address,uint256)","mint()","mintFree()","claimFree()",
          "claimFreeAgent(uint256)","buyShares(uint256)","mintShares(uint256)","mint(address)"]
QUOTE_S = ["quote(address,uint256)","quote(uint256)","costOf(address,uint256)","getQuote(uint256)","price()"]
FREE_S = ["freeClaimed()","freeLeft()","freeSharesRemaining()","freeAvailable(address)",
          "freeClaimed(address)","freeFor(address)","freeUsed()","freeMinted()","freeSupply()",
          "freeSharePoolExhausted()","freeSharesClaimed()","freeClaimedByAgent(uint256)"]
AGENT_S = ["agentIdRegistry()","registry()","agentRegistry()","holdsAgentId(address)","agentIdOf(address)"]
def probe(addr):
    for ep in EPS:
        try:
            r = rpc_post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_getCode",
                              "params":[addr,"latest"]}, timeout=20)
            code = (r.get("result") or "")[2:]
            if not code or code == "0x":
                return {"code": "empty", "is_contract": False}
            cb = bytes.fromhex(code)
            def has(sigs):
                return [s for s in sigs if bytes.fromhex(sel(s)) in cb]
            return {"is_contract": True, "code_len": len(cb),
                    "mint": has(MINT_S), "quote": has(QUOTE_S),
                    "free": has(FREE_S), "agent": has(AGENT_S)}
        except Exception as e:
            continue
    return {"code": "probe-failed"}
def main():
    t0 = time.time()
    out = {"started_wib": "2026-11-13T17:31+07:00"}
    seen = {}
    try: seen = json.load(open(BASE + "hot-leg-seen.json"))
    except Exception as e: out["seen_load_error"] = str(e)[:100]
    seen_addrs = set(k.lower() for k in seen.keys()) if isinstance(seen, dict) else set()
    out["seen_total"] = len(seen_addrs)
    raw = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 25)
    feed_new = []
    try:
        fj = json.loads(raw)
        items = fj.get("results", fj if isinstance(fj, list) else [])
        out["feed_n"] = len(items)
        out["feed_verifiedAt_range"] = [items[0].get("verifiedAt") if items else None,
                                        items[-1].get("verifiedAt") if items else None]
        for it in items:
            a = (it.get("address") or "").lower()
            va = it.get("verifiedAt") or (it.get("match") or {}).get("verifiedAt")
            if a and a not in seen_addrs:
                feed_new.append({"address": it.get("address"), "verifiedAt": va})
        out["feed_new"] = feed_new
    except Exception as e:
        out["feed_error"] = str(e)[:200] + " raw_len=" + str(len(raw))
    out["feed_shape"] = {}
    for it in feed_new:
        a = it["address"]
        rec = {}
        try:
            meta = curl(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", 20)
            mj = json.loads(meta)
            abi = mj.get("abi") or (mj.get("stdJson", {}).get("output", {}).get("abi")) or []
            fns = [f.get("name") for f in abi if f.get("type") == "function"]
            rec["sourcify_abi_fns"] = len(fns)
            if fns:
                src = json.dumps(mj).lower()
                has_mint = any(n in fns for n in ("mint","claimFree","mintFree","claimFreeAgent"))
                has_quote = any("quote" in n.lower() or "cost" in n.lower() for n in fns)
                free_views = [n for n in fns if "free" in n.lower()]
                agent = ("0x60b9262456de011f7d15a54cdd8c48baaa8b022f" in src) or ("agent" in " ".join(fns).lower())
                rec.update({"method":"sourcify-abi","S1": bool(has_mint and has_quote and free_views and agent),
                            "mint": has_mint, "quote": has_quote, "free": free_views,
                            "agent": agent, "n_fns": len(fns), "status":"checked"})
            else:
                rec["sourcify_abi_empty"] = True
        except Exception as e:
            rec["sourcify_error"] = str(e)[:120]
        if rec.get("sourcify_abi_fns", 0) == 0:
            pr = probe(a)
            rec["probe"] = pr
            if pr.get("is_contract"):
                s1 = bool(pr["mint"] and pr["quote"] and pr["free"] and pr["agent"])
                s2 = bool(pr["mint"] and pr["free"] and pr["agent"])
                rec.update({"method":"selector-probe","S1_probe": s1, "S2_probe": s2,
                            "status":"probe-positive" if (s1 or s2) else "probe-negative"})
            else:
                rec.update({"method":"selector-probe","status":"probe-" + str(pr.get("code"))})
        out["feed_shape"][a] = rec
    out["boltbook"] = {}
    for lang, url in (("en","https://boltbook.fun/"),("zh","https://boltbook.fun/?lang=zh")):
        html = curl(url, 25)
        addrs = sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", html)))
        out["boltbook"][lang] = {"bytes": len(html), "addrs": addrs,
                                 "new": [a for a in addrs if a.lower() not in seen_addrs]}
    out["elapsed_s"] = round(time.time()-t0, 1)
    print(json.dumps(out, indent=1))
    json.dump(out, open(BASE + "run-2026-11-13-1731-discovery.json","w"), indent=1)
if __name__ == "__main__":
    main()
