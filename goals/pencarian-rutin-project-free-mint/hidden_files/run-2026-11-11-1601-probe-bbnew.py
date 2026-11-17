#!/usr/bin/env python3
"""Probe new Boltbook address 0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640
(found by hot-leg 15:59 EN+ZH front pages). Sourcify ABI + shape test,
on-chain views, owner vs same-owner-discards, Boltbook post context.
Read-only."""
import json, re, subprocess, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
out = {"address": ADDR, "source": "boltbook-front-en+zh hot-leg 15:59"}

def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode(errors="replace")

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

def eth_call(to, data):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
               "params": [{"to": to, "data": data}, "latest"]}
    for ep in EPS:
        try:
            r = subprocess.run(["curl", "-sL", "--max-time", "25", "-X", "POST", ep,
                                "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                               capture_output=True, text=True, timeout=30)
            res = json.loads(r.stdout)
            if "result" in res: return res["result"]
            if "error" in res: return {"error": res["error"]}
        except Exception:
            continue
    return None

# 1. Sourcify metadata + ABI
try:
    meta = json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi"))
    abi = meta.get("abi", [])
    out["sourcify"] = {"verified": True, "name": meta.get("name"), "match": meta.get("match")}
    names = {e["name"] for e in abi if e.get("type") == "function"}
    fns = {}
    for e in abi:
        if e.get("type") == "function": fns.setdefault(e["name"], []).append(e)
    FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
                  "freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
    free_views = sorted(names & set(FREE_VIEWS))
    agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
    is_token = bool(names & {"name","symbol","decimals","totalSupply","balanceOf"}) and "totalSupply" in names
    mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
    s1 = has_mint and has_quote and bool(free_views) and agent_ref
    s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
    is_nft = bool(names & {"tokenURI","ownerOf","safeTransferFrom"}) or "uri" in names
    free_mint_fn = bool(names & {"freeMint","mintFree","claimFree","mint"}) or any(n.lower().startswith("freemint") for n in names)
    out["shape"] = {"S1": s1, "S2": s2, "early_shape": bool(is_nft and (agent_ref or free_mint_fn)),
                    "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                    "agent_ref": agent_ref, "is_token": is_token, "is_nft": is_nft, "fn_count": len(names),
                    "fn_names": sorted(names)}
except Exception as e:
    out["sourcify"] = {"verified": False, "error": f"{type(e).__name__}: {str(e)[:150]}"}

# 2. on-chain views
views = {}
for sig in ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
            "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "owner()"]:
    r = eth_call(ADDR, sel(sig))
    views[sig.split("(")[0]] = to_int(r) if isinstance(r, str) else r
for sig in ["balanceOf(address)", "freeClaimed(address)"]:
    r = eth_call(ADDR, sel(sig) + enc(USER))
    views[sig.split("(")[0] + "_user"] = to_int(r) if isinstance(r, str) else r
out["views"] = views

# 3. owner vs discards
try:
    disc = json.load(open(BASE + "same-owner-discards.json"))
    disc_addrs = set()
    def walk(o):
        if isinstance(o, dict):
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
        elif isinstance(o, str) and re.fullmatch(r"0x[0-9a-fA-F]{40}", o or ""):
            disc_addrs.add(o.lower())
    walk(disc)
    owner = views.get("owner")
    out["discards"] = {"owner": owner, "owner_discarded": (str(owner).lower() in disc_addrs) if owner else None,
                       "discard_count": len(disc_addrs)}
except Exception as e:
    out["discards"] = {"error": str(e)[:120]}

# 4. Boltbook post context: find surrounding text near the address in saved html
for lang in ("en", "zh"):
    try:
        html = open(BASE + f"hot-leg-2026-11-11-1559-boltbook-{lang}.html").read()
        idx = html.lower().find(ADDR.lower())
        if idx >= 0:
            ctx = re.sub(r"<[^>]+>", " ", html[max(0, idx-1500):idx+500])
            ctx = re.sub(r"\s+", " ", ctx)
            out[f"boltbook_{lang}_context"] = ctx[:1200]
        else:
            out[f"boltbook_{lang}_context"] = "address not found in saved html"
    except Exception as e:
        out[f"boltbook_{lang}_context"] = f"error: {e}"

json.dump(out, open(BASE + "run-2026-11-11-1601-probe-bbnew.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:4000])
