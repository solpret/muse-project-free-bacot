#!/usr/bin/env python3
"""Run 1401 new-findings verification (fresh script).
Five contracts found via Boltbook post reads (route 2 deep read), none in
snapshot: Cobalt Agent, NAPPER, DACIT, SYNERGYPASS, DRAGON (0xad0d).
First on-chain read each: free counters, user slot, time views, plus
Sourcify verification + ABI shape (S1/S2/early). Read-only; writes
run-2026-11-12-1401-newfindings.json. No preview/mint."""
import json, subprocess, time, urllib.request, concurrent.futures
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            return {key: (None if (isinstance(it, dict) and "error" in it)
                          else (to_int(it.get("result")) if isinstance(it, dict) else None))
                    for it, key in zip(res, keys)}
        except Exception:
            continue
    return None

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "FREE_SUPPLY()", "FREE_MAX()", "MAX_SUPPLY()", "freeLeft()",
         "freeRemaining()", "agentFreeUsed()", "mintOpen()", "balanceOf(address)",
         "freeClaimed(address)", "freeUsed(address)", "mintedBy(address)",
         "freeMintedBy(address)", "mintStart()", "saleStart()", "START_TIME()",
         "startTime()", "mintOpensAt()", "deadline()", "DEADLINE()", "price()",
         "name()", "symbol()"]
# name()/symbol() return strings, not ints - to_int will fail -> None; harmless.

TARGETS = [
    ("Cobalt Agent", "0x7ef49be2a9ade4fae0888f4065c8f122a146f6d0"),
    ("NAPPER", "0x3964BFc3354C0d18886dcAD52Abc55C689e6A1d4"),
    ("DACIT", "0x90ddd762f407b3edf43f732cd5a68a9e4695a6bd"),
    ("SYNERGYPASS", "0xb8a990e16fd66d398cc27d0c8bdb11524bc0dc8e"),
    ("DRAGON-0xad0d", "0xad0d8ac3d61fc8ab397b7136c69fcbf1281a4998"),
]

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]

def sourcify(addr):
    try:
        req = urllib.request.Request(
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata",
            headers={"User-Agent": "free-bacot/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            meta = json.loads(r.read().decode(errors="replace"))
        abi = meta.get("abi", []) or []
        names = {e.get("name") for e in abi if e.get("type") == "function"}
        lnames = {n.lower() for n in names}
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(lnames & {"quote", "cost", "getquote", "mintcost", "price", "getprice", "mintprice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(lnames & {"agentid", "agentregistry", "registry", "getagentid", "agentgate", "agentidregistry"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in names
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        is_nft = bool(names & {"tokenURI", "ownerOf", "safeTransferFrom"}) or "uri" in names
        free_mint_fn = bool(names & {"freeMint", "mintFree", "claimFree"})
        early_shape = is_nft and (agent_ref or free_mint_fn)
        return {"verified": meta.get("match") or meta.get("status"),
                "verifiedAt": (meta.get("metadata") or {}).get("verifiedAt") or meta.get("verifiedAt"),
                "S1": s1, "S2": s2, "early_shape": early_shape, "n_fns": len(abi),
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_nft": is_nft}
    except Exception as e:
        return {"verified": None, "error": f"{type(e).__name__}: {str(e)[:100]}"}

out = {"started_wib": "2026-11-12 14:01 WIB", "block": get_block(), "reads": {}}
for name, addr in TARGETS:
    v = raw_batch(addr, VIEWS)
    out["reads"][name] = {"address": addr, "views": v,
                          "summary": {k: x for k, x in (v or {}).items() if x is not None}}
    print(name, out["reads"][name]["summary"], flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    for (name, addr), s in zip(TARGETS, ex.map(sourcify, [a for _, a in TARGETS])):
        out["reads"][name]["sourcify"] = s
        print(name, "sourcify:", s, flush=True)
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-12-1401-newfindings.json", "w"), indent=1)
print("BLOCK", out["block"], "ELAPSED", out["elapsed_s"])
