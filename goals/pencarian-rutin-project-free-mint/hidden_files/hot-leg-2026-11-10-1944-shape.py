import json, subprocess
NEW = ["0xBb90Cc15F7302Bbb7e114a5329d41dBb104F5350",
       "0xA47933CD9bdc92657A21CeAa94d16D2af3cC3E3E",
       "0xe069d6AC5E4a8D6304cFf0d9E23F423aaB6e36Cb",
       "0x020D137f9b9F2A5e33CEd498134ee92bD964D5c1",
       "0x27deBB215B290597de9646CdfC2567755958ebaA"]
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted"]
def get(url):
    p = subprocess.run(["curl","-s","--max-time","20",url], capture_output=True, text=True)
    return p.stdout
out = {}
for addr in NEW:
    abi = None; err = ""
    raw = get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=metadata")
    try:
        m = json.loads(raw)
        abi = (m.get("metadata") or {}).get("output",{}).get("abi")
        if not abi: err = "no-abi-in-metadata"
    except Exception as e:
        err = f"parse:{e}:{raw[:120]}"
    if not abi:
        out[addr] = {"error": err or "abi-unavailable"}
        continue
    fns = [f.get("name") for f in abi if f.get("type")=="function"]
    fnset = set(fns)
    mint = [f for f in fns if f and "mint" in f.lower()]
    quote = [f for f in fns if f and ("quote" in f.lower() or f in ("cost","getCost","mintCost","price"))]
    free = [f for f in FREE_VIEWS if f in fnset]
    agent = [f for f in fns if f and ("agent" in f.lower() or f in ("registry","AGENT_REGISTRY","agentRegistry","AGENT_ID"))]
    token = [f for f in ("name","symbol","decimals","totalSupply") if f in fnset]
    s1 = bool(mint) and bool(quote) and bool(free) and bool(agent)
    s2 = bool(token) and ("mintFree" in fnset) and bool(set(["freeClaimed","freeMinted"]) & fnset) and bool(set(["FREE_SLOTS","FREE_SUPPLY","FREE_SHARES"]) & fnset) and bool(agent)
    out[addr] = {"S1": s1, "S2": s2, "mint": mint, "quote": quote, "free": free,
                 "agent": agent, "token": token, "fns": len(fns)}
json.dump(out, open("hot-leg-2026-11-10-1944-shape.json","w"), indent=1)
for a, r in out.items():
    print(a, "S1=", r.get("S1"), "S2=", r.get("S2"), "mint=", r.get("mint"), "quote=", r.get("quote"), "free=", r.get("free"), "agent=", r.get("agent"), "token=", r.get("token"), r.get("error",""), "fns=", r.get("fns"))
