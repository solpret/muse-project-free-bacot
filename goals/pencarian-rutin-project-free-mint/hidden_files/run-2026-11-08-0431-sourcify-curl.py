import json, subprocess, re
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F".lower()
feed = json.load(open("run-2026-11-08-0431-sourcify.json"))
out=[]
for item in feed.get("results", []):
    addr = item["address"]
    r = subprocess.run(["curl","-s","--max-time","30",
        f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata"],
        capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except Exception:
        d = {"_error": "bad json: "+r.stdout[:120]}
    abi = d.get("abi") or []
    names = [f.get("name","") for f in abi if isinstance(f, dict)]
    raw = r.stdout
    mint = any(n=="mint" for n in names)
    quote = any(n in names for n in ("quote","cost","costFor","getCost"))
    free = [n for n in names if n.startswith("free") or n in ("freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed")]
    s1 = mint and quote and free and (REG in raw.lower())
    s2 = all(n in names for n in ("name","symbol","decimals","totalSupply")) and any(n in names for n in ("mintFree","freeMint")) and any(n in names for n in ("freeClaimed","freeMinted")) and (REG in raw.lower() or "agentRegistry" in names)
    agent_shape = (REG in raw.lower()) or any(("gate" in n.lower() or "registry" in n.lower()) and "agent" in n.lower() for n in names)
    out.append({"address": addr, "verifiedAt": item.get("verifiedAt"), "match": item.get("match"),
                "fns": names, "mint": mint, "quote": quote, "free_fns": free,
                "S1": bool(s1), "S2": bool(s2), "agent_shape": bool(agent_shape),
                "registry_literal": REG in raw.lower()})
json.dump(out, open("run-2026-11-08-0431-sourcify-shape.json","w"), indent=2)
print("checked", len(out), "S1", sum(o["S1"] for o in out), "S2", sum(o["S2"] for o in out), "agent", sum(o["agent_shape"] for o in out))
for o in out:
    print(o["address"], "mint", o["mint"], "quote", o["quote"], "free", o["free_fns"], "agent", o["agent_shape"], "nfns", len(o["fns"]))
