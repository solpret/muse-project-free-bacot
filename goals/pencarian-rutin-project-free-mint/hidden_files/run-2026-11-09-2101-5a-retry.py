#!/usr/bin/env python3
"""Run 2101 route 5a retry: 13 Sourcify IncompleteRead errors, sequential via curl.
Read-only except run-2026-11-09-2101-5a.json update. Also triages the S1 hit
0x5f76cAb7B054e088563D5098E17bD0dc430e61aE (views only)."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
        "https://bsc-dataseed.binance.org/"]
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "FREE_SLOTS", "FREE_SUPPLY", "freeClaimCount", "freeMintsLeft"]

def fetch_abi_curl(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    for attempt in range(3):
        try:
            out = subprocess.run(["curl", "-sL", "--max-time", "30", "-A", "curl/8", url],
                                 capture_output=True, text=True, timeout=35).stdout
            d = json.loads(out)
            return d.get("abi"), d.get("verifiedAt")
        except Exception as e:
            time.sleep(3)
    return {"_error": "curl-failed-3x"}, None

def shape(addr):
    abi, verified_at = fetch_abi_curl(addr)
    if not isinstance(abi, list):
        return {"address": addr, "error": str(abi), "verifiedAt": verified_at}
    fns = {}
    for f in abi:
        if f.get("type") == "function":
            fns.setdefault(f.get("name"), []).append(f)
    names = set(fns)
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = any("quote" in n.lower() or n in ("cost", "price", "getPrice", "mintPrice") for n in names)
    free = [n for n in FREE_VIEWS if n in names]
    src = json.dumps(abi).lower()
    agent = ("60b9262456de011f7d15a54cdd8c48baaa8b022f" in src or "agentid" in src
             or "agentgate" in src or "agentregistry" in src or "registry" in names)
    tokenish = bool({"name", "symbol", "decimals", "totalSupply"} <= names)
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = tokenish and ("mintFree" in names or "mintfree" in [n.lower() for n in names]) and bool(free) and agent
    return {"address": addr, "verifiedAt": verified_at, "S1": s1, "S2": s2,
            "mint": has_mint, "quote": has_quote, "free": free, "agent": agent,
            "token": tokenish, "fns": sorted(names)}

out = json.load(open(f"{BASE}/run-2026-11-09-2101-5a.json"))
errs = [a for a, s in out["5a"].items() if "error" in s]
print("RETRY", len(errs), flush=True)
for a in errs:
    s = shape(a)
    out["5a"][a] = s
    print("retry", a, "S1", s.get("S1"), "S2", s.get("S2"), "mint", s.get("mint"),
          "quote", s.get("quote"), "free", s.get("free"), "agent", s.get("agent"),
          "err", s.get("error"), flush=True)
    with open(f"{BASE}/run-2026-11-09-2101-5a.json", "w") as f:
        json.dump(out, f, indent=1)

# --- triage S1 hit 0x5f76cAb7...: on-chain views ---
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return None if v in (None, "0x") else int(v, 16)
    except Exception: return None
def rpc(method, params, timeout=20):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    for u in RPCS:
        try:
            req = urllib.request.Request(u, data=body, headers={"Content-Type": "application/json"})
            import urllib.request as _u
            with _u.urlopen(req, timeout=timeout) as r:
                o = json.load(r)
            if "error" in o: continue
            return o["result"]
        except Exception: continue
    return None
def call(addr, sig, arg=None):
    data = sel(sig) + (enc(arg) if arg else "")
    v = rpc("eth_call", [{"to": addr, "data": data}, "latest"])
    return to_int(v)

HIT = "0x5f76cAb7B054e088563D5098E17bD0dc430e61aE"
views = {}
for sig in ["name()", "symbol()", "decimals()", "totalSupply()", "freeUsed()", "FREE_SUPPLY()",
            "FREE_SHARES()", "freeSharesRemaining()", "freeMinted()", "totalMinted()",
            "mintPrice()", "price()", "launched()", "launchTime()", "opened()"]:
    views[sig] = call(HIT, sig)
for sig in ["freeClaimed(address)", "freeUsed(address)", "hasMinted(address)", "balanceOf(address)",
            "freeSharesClaimed(address)"]:
    views[sig + "_user"] = call(HIT, sig, USER)
for sig in ["quote(address,uint256)", "cost(uint256)"]:
    try:
        if "(address" in sig:
            d = sel(sig) + enc(USER) + "1".rjust(64, "0")
            views[sig + "_user1"] = to_int(rpc("eth_call", [{"to": HIT, "data": d}, "latest"]))
        else:
            views[sig] = call(HIT, sig)
    except Exception as e:
        views[sig] = f"ERR {e}"
for sig in ["agentRegistry()", "registry()", "AGENT_ID()", "agentId()"]:
    views[sig] = call(HIT, sig)
out["s1_hit_views"] = {"address": HIT, "views": views}
with open(f"{BASE}/run-2026-11-09-2101-5a.json", "w") as f:
    json.dump(out, f, indent=1)
print("HIT views:", json.dumps(views), flush=True)
print("5A-RETRY DONE", flush=True)
