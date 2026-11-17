import json, subprocess
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F".lower()
addrs = {
 "WALL":"0xa804bBBe09fa2F5832d11D09329cc4230D1d7899",
 "ZSEAT":"0xa5c09809ada4969fbe1d67a9034ed9633c98ab87",
 "ElonGai":"0x59F93bBBb14cE948Ee16b261a05Ad4A77711ECf1",
 "WRAITH":"0x4a318eb842c8c95876e895258bc70d0bee767def",
 "AgentChickens":"0x1F0D3ffeEBdDAf2F49ced65A9a92864332e55Ee5",
 "LuckyAgents":"0x0B51Ef6827ab0bc875673d367Dbb78eE1B6Df1Ce",
 "BNAgentFile":"0x6B1719EEFcb271778c40f0CFd71c8651Adbde5d1",
 "PilotBoarding":"0xc267E47F1Ba3B6B2BCbA58f16298c92CaCAF7952",
 "ALIBABA":"0xA2F2ffCA66D324af5ED58e5c98c9D6f544b13303",
 "BHPASS":"0xCd4Af5a9eDE5ef6f5138028AdC9C152a1Acb80ed",
 "PixelSentinels":"0x4e4e43f84E2E80716d03153F3c675e8E715Fa698",
 "GLOOP":"0x183CBb52B3C7BCB2433d50dE0Add99B59f4DE4fE",
}
out={}
for name, addr in addrs.items():
    r = subprocess.run(["curl","-s","--max-time","30",
        f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata"],
        capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except Exception:
        d = {"_error": "bad json"}
    if isinstance(d, dict) and "error" in d:
        out[name] = {"address": addr, "sourcify": "404/unverified", "error": str(d.get("error"))[:100]}
        print(name, "404/unverified")
        continue
    abi = d.get("abi") or []
    names = [f.get("name","") for f in abi if isinstance(f, dict)]
    raw = r.stdout
    out[name] = {"address": addr, "sourcify": d.get("match") or "verified?", "nfns": len(names),
        "fns": names,
        "mint": [n for n in names if "mint" in n.lower() or "claim" in n.lower()],
        "free": [n for n in names if n.startswith("free")],
        "registry_literal": REG in raw.lower(),
        "agent_gate_fn": [n for n in names if "agent" in n.lower()]}
    print(name, out[name]["sourcify"], "nfns", len(names), "mint/claim", out[name]["mint"], "free", out[name]["free"], "reg", out[name]["registry_literal"], "agentfns", out[name]["agent_gate_fn"])
json.dump(out, open("run-2026-11-08-0401-new-sourcify.json","w"), indent=2)
