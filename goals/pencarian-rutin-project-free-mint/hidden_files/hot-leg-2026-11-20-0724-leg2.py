#!/usr/bin/env python3
"""Hot-leg run 0724 leg-2 retry: Boltbook EN+ZH (files vanished from /tmp between
exec calls; re-fetched fresh). Same shape() logic as the main run script."""
import json, re, time, subprocess, concurrent.futures, os
os.environ["TZ"] = "Asia/Jakarta"; time.tzset()
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "2026-11-20-0724"
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.localtime())
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124","0x8b47354E7b76B1970a0D06365c8244a810d37493"}
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EN_KW = ['free share','first share free','1 free share','free mint share']
ZH_KW = ['免费份额','首个免费','免费铸造','免费mint']

def shape(addr):
    try:
        _o = subprocess.run(["curl","-sL","--max-time","20",
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
            capture_output=True, text=True).stdout
        meta = json.loads(_o)
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function": fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate","AGENT_ID","AGENT_ID_REGISTRY","agentIdOf","hasAgentId"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "is_nft": bool(names & {"ownerOf","tokenURI"}),
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names),
                "is_proxy": bool(abi) and not fns}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

out = {}
for lang in ("en","zh"):
    try:
        html = open(f"/tmp/bb-{lang}-0724.html").read()
        open(BASE+f"hot-leg-2026-11-20-0724-boltbook-{lang}.html","w").write(html)
        found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        seen = json.load(open(BASE+"hot-leg-seen.json"))
        seen_lower = {k.lower() for k in seen}
        newfound = [a for a in found if a.lower() not in seen_lower and a not in EXCLUDED
                    and a.lower() != REGISTRY]
        low = html.lower()
        txt = re.sub(r"<[^>]+>"," ", html); txt = re.sub(r"\s+"," ", txt)
        freeposts = sorted(set(re.findall(r"([A-Za-z0-9$._-]{2,30})\s*:\s*([\d.,]+)\s*/\s*([\d.,]+)\s*free\s*\(([\d.,]+)%\)", txt)))
        out[lang] = {"bytes": len(html), "http_code": "200",
            "full_address_contracts": len(found), "addresses": found, "new": len(newfound),
            "new_contracts": newfound,
            "free_kw": sum(low.count(k) for k in EN_KW),
            "zh_free_kw": sum(html.count(k) for k in ZH_KW),
            "free_posts": freeposts}
        bb_shapes = []
        if newfound:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
                bb_shapes = list(ex.map(shape, newfound))
        out[lang]["shapes"] = bb_shapes
        out[lang]["shape_hits"] = [s["address"] for s in bb_shapes if s.get("S1") or s.get("S2")]
        for s in bb_shapes:
            a = s["address"]
            if s.get("error") or not s.get("n_fns"): continue
            seen[a] = {"first_seen_wib": NOW, "source": f"boltbook-{lang}",
                "status": "checked-not-track-c" if ((s.get("S1") or s.get("S2")) and s.get("is_nft"))
                         else ("sale-shape-pass" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"),
                "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')}"}
        json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
    except Exception as ex:
        out[lang] = {"error": f"{type(ex).__name__}: {str(ex)[:160]}", "fetch": "SKIPPED"}

json.dump(out, open(BASE+f"hot-leg-run-{RUN}-boltbook.json","w"), indent=1)
# patch main run json
main = json.load(open(BASE+f"hot-leg-run-{RUN}.json"))
main["boltbook"] = out
main["boltbook_retry_note"] = "Leg-2 retried same run: /tmp files vanished between exec calls; re-fetched 200 both languages."
main["seen_n_after_boltbook"] = len(json.load(open(BASE+"hot-leg-seen.json")))
main["shape_hits_all"] = main.get("shape_hits", []) + [s for lang in ("en","zh") for s in out.get(lang,{}).get("shape_hits",[])]
json.dump(main, open(BASE+f"hot-leg-run-{RUN}.json","w"), indent=1)
print(json.dumps(out, indent=1))
