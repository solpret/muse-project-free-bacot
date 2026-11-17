import json, subprocess, concurrent.futures
FEED = ['0x76C92703766261a06fEB805583eF9a4839a2c960','0x561DFe8E082B3704E7B7194cD20753df0f7D1e8f','0x6B2bc86427697c850Ee661Bb480560f068E3aC8d','0x1E0fcC192A6e9E42dd6D8D4f8E50cA9af009f27E','0x9dA9e4823A19044Ea202a946691214b5212fD26c','0xD2278D1F4AA25AC524c1DCC465499BBaE9D9f88E','0xa68971B586D2059e15863a4Be806EdB1B89BbBf9','0xADC1A55331611234Ab43b20157C469592718747D','0xe0E68DAaa465986409FcC221626dec30BDf4F758','0x5937bb74E2f0e4e914B782bD1638Ac88C8C490f9','0x124501Acb079e326215cc400FA7452344d0bd48C','0x53F365D65024089697920AEa8c77eca8B96E346f','0x8E68B9CD6eb80fbACd5616cC2ECFB448989B8b7A','0xB20278cEB2279E3eB9B10b6403AE5A1FD4Fd75f0','0xf52A46054919ae8f81a3ecC186CaDAB2DCcDF94C','0x94F8F6F4Da3Dfd0549DE5c3422A4FfB41Aba673e','0x136AC70EE85529ef961ccC7076de77e4e929D6dF','0x09e664F447D854b0C413f63E4D6e78070B411AeB','0x4F8cbCD1F336D873CAEC5e479ecc689624107037']
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
def shape_from_abi(addr, abi):
    fns = {}
    for e in abi:
        if e.get("type") == "function":
            fns.setdefault(e["name"], []).append(e)
    names = set(fns)
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
    free_views = sorted(names & FREE_VIEWS)
    agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
    is_token = bool(names & {"name","symbol","decimals","totalSupply"})
    mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
    s1 = has_mint and has_quote and bool(free_views) and agent_ref
    s2 = (is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref)
    return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
            "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names)}
def check(addr):
    try:
        r = subprocess.run(["curl","-sS","-m","55","https://sourcify.dev/server/v2/contract/56/"+addr+"?fields=abi"], capture_output=True, timeout=60)
        if r.returncode != 0 or not r.stdout:
            return {"address": addr, "error": f"curl rc={r.returncode}"}
        meta = json.loads(r.stdout.decode())
        return shape_from_abi(addr, meta.get("abi", []))
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {str(e)[:80]}"}
# first contract already downloaded to /tmp/abi-test.json
res = [shape_from_abi("0x587185544fc1911292191685e4EC5Ab4B7De4228", json.load(open("/tmp/abi-test.json")).get("abi", []))]
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    res += list(ex.map(check, FEED))
json.dump(res, open("hot-leg-2026-11-10-0949-shape-curl2.json","w"), indent=1)
for r in res:
    print(r.get("address"), "S1=",r.get("S1"),"S2=",r.get("S2"),"mint=",r.get("has_mint"),"quote=",r.get("has_quote"),"free=",r.get("free_views"),"agent=",r.get("agent_ref"),"token=",r.get("is_token"), r.get("error",""))
