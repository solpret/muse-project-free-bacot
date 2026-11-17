import json, subprocess, time
ADDRS = [
 ("0x9A1F78B53204172237a759f23421a216027626B6", 36),
 ("0x66239b70133773A72A0D589E5564E88a50Cd39e7", 29),
 ("0xC28916D607109C73066fe8F517f9c899A3bf9122", 10),
 ("0xc7fFd72C66FF4db04181d93dd311004477722377", 10),
 ("0x9d972c27dB2789bed8efe4bDD4AFC32F798b2c57", 10),
 ("0x4198a3e403D16ce75E450DA344F982E1e91FA893", 10),
]
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F".lower()
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeMint"]
def curl_json(url):
    p = subprocess.run(["curl","-sS","--max-time","25","-H","User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36","-H","Accept: application/json",url],
                       capture_output=True, text=True)
    if p.returncode != 0: raise RuntimeError(f"curl rc={p.returncode} {p.stderr[:150]}")
    return json.loads(p.stdout)
out = {"source": "onchain-scan-2026-11-07-0031.json window 132049244-132050243 (endpoint /v2/contract singular, corrected)", "checked": []}
for addr, mc in ADDRS:
    rec = {"address": addr, "mint_count": mc}
    try:
        meta = curl_json(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi")
        if not meta.get("match"):
            rec.update({"verified": False, "reason": "sourcify-not-verified", "sale_shape": "NOT-SALE-SHAPE (unverified)"})
        else:
            std = meta.get("abi", None) or {}
            abi = std if isinstance(std, list) else []
            fns = [f.get("name") for f in abi if f.get("type") == "function"]
            src = json.dumps(std)[:200000] if std else ""
            has_mint = any(n and ("mint" in n.lower()) for n in fns)
            has_quote = any(n and ("quote" in n.lower() or "cost" in n.lower() or "price" in n.lower()) for n in fns)
            free_views = [n for n in fns if n and any(v.lower() in n.lower() for v in FREE_VIEWS)]
            reg_ref = REG in src.lower() or any(n and "agent" in n.lower() and ("regist" in n.lower() or "gate" in n.lower()) for n in fns)
            is_token = all(n in fns for n in ["name","symbol","decimals","totalSupply"])
            rec.update({"verified": True, "verifiedAt": meta.get("verifiedAt"), "functions": len(fns),
                        "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                        "registry_ref": reg_ref, "is_token": is_token, "sample_fns": fns[:30]})
            s1 = has_mint and has_quote and bool(free_views) and reg_ref
            s2 = is_token and has_mint and bool(free_views) and reg_ref
            rec["sale_shape"] = "S1" if s1 else ("S2" if s2 else "NOT-SALE-SHAPE")
    except Exception as e:
        rec.update({"verified": False, "error": str(e)[:200], "sale_shape": "UNVERIFIED-TRANSPORT-FAILED"})
    out["checked"].append(rec)
    print(addr, mc, rec["sale_shape"], flush=True)
    time.sleep(0.5)
json.dump(out, open("run-2026-11-07-0031-5c-newscan.json","w"), indent=1)
print("hits:", [c["address"] for c in out["checked"] if c["sale_shape"] in ("S1","S2")])
print("transport-failed:", [c["address"] for c in out["checked"] if c["sale_shape"]=="UNVERIFIED-TRANSPORT-FAILED"])
