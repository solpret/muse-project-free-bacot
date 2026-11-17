#!/usr/bin/env python3
"""Hot-leg run 2026-11-05 21:44 WIB. Adapted from 2139 run script.
Leg1 Sourcify feed + shape-check; Leg2 Boltbook EN+ZH; Leg3 verify new sale-shapes
+ AgentGlyph re-check; Leg4 bridge read-only. Writes only its own run files +
hot-leg-seen.json. Never touches main snapshot / scan-seen / track-c-checked /
scan-bridge.json."""
import json, urllib.request, time, subprocess, re
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-05-2144"
NOW = "2026-11-05 21:44 WIB"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: out = json.load(r)
            if "error" in out: return None
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None

# --- Leg 1: Sourcify feed ---
# Feed already fetched this run to /tmp/sourcify-hotleg.json (curl, 20 items)
try:
    feed = json.load(open("/tmp/sourcify-hotleg.json"))
except Exception as e:
    feed = {"error": str(e)[:120]}
json.dump(feed, open(f"{BASE}/run-{TS}-sourcify-feed.json", "w"), indent=1)
addrs = [x["address"] for x in feed.get("results", [])]
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_l = {k.lower(): v for k, v in seen.items()}
new = [a for a in addrs if a.lower() not in seen_l]
excluded = ["0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"]
new_not_excl = [a for a in new if a.lower() not in excluded]
print("FEED", len(addrs), "NEW", len(new), "NEW_NOT_EXCL", len(new_not_excl), flush=True)
FREE = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
        "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed"]

def abi_of(a):
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",
                                     headers={"User-Agent": "curl"})
        with urllib.request.urlopen(req, timeout=15) as r: d = json.load(r)
        return d.get("abi") or d.get("stdJson", {}).get("abi") or []
    except Exception:
        pass
    try:
        out = subprocess.run(["curl", "-s", "--max-time", "15",
                              f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"],
                             capture_output=True, text=True, timeout=20)
        d = json.loads(out.stdout)
        return d.get("abi") or d.get("stdJson", {}).get("abi") or []
    except Exception as e:
        return {"error": str(e)[:80]}

def shape_of(a):
    abi = abi_of(a)
    if isinstance(abi, dict):
        return {"error": abi.get("error", "abi-unavailable"), "S1": False, "S2": False,
                "mint": False, "quote": False, "free": [], "agent": False, "token": False}
    fns = sorted({f.get("name") for f in abi if f.get("type") == "function" and f.get("name")})
    has_mint = any(n.startswith("mint") for n in fns)
    has_quote = "quote" in fns
    free = [f for f in fns if any(x in f for x in FREE)]
    agent = ("agentRegistry" in fns or "AGENT_REGISTRY" in fns or "registry" in fns
             or REG in json.dumps(abi).lower())
    is_token = all(x in fns for x in ["name", "symbol", "decimals", "totalSupply"])
    has_mintfree = "mintFree" in fns
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = is_token and has_mintfree and ("freeClaimed" in fns or "freeMinted" in fns) \
        and ("FREE_SLOTS" in fns or "FREE_SUPPLY" in fns) and agent
    nft = ("ownerOf" in fns or "tokenURI" in fns)
    return {"abi_functions": fns, "S1": s1, "S2": s2, "mint": has_mint,
            "quote": has_quote, "free": free, "agent": agent, "token": is_token, "nft": nft}

shape = {}
with ThreadPoolExecutor(max_workers=5) as ex:
    for a, sh in zip(new_not_excl, ex.map(shape_of, new_not_excl)):
        shape[a] = sh
        print("SHAPE", a, "S1", sh["S1"], "S2", sh["S2"], "mint", sh["mint"], "quote", sh["quote"],
              "free", sh["free"], "agent", sh["agent"], "token", sh["token"], "nft", sh.get("nft"),
              sh.get("error", ""), flush=True)
json.dump(shape, open(f"{BASE}/run-{TS}-sourcify-shape.json", "w"), indent=1)
for a in new:
    if a.lower() in excluded:
        seen[a] = {"first_seen": NOW, "status": "excluded"}
    else:
        sh = shape.get(a, {})
        if sh.get("S1") or sh.get("S2"):
            if sh.get("nft"):
                st = "checked-not-track-c"
                nt = ("S1/S2 literal pass BUT ERC-721 NFT (ownerOf/tokenURI), not a fungible "
                      "share sale, so NOT a track-C lead. NFT early-lead stays with main job; "
                      "never reported/previewed/minted.")
            else:
                st = "sale-shape-NEEDS-VERIFY"
                nt = "SALE SHAPE S1=%s S2=%s" % (sh.get("S1"), sh.get("S2"))
        else:
            st = "checked-not-sale-shape"
            nt = "S1=%s S2=%s mint=%s quote=%s free=%s agent=%s token=%s nft=%s %s" % (
                sh.get("S1"), sh.get("S2"), sh.get("mint"), sh.get("quote"),
                sh.get("free"), sh.get("agent"), sh.get("token"), sh.get("nft"),
                sh.get("error", ""))
        seen[a] = {"first_seen": NOW, "status": st, "note": nt, "source": "sourcify-feed"}
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
print("SEEN-UPDATED", len(new), "total", len(seen), flush=True)

# --- Leg 2: Boltbook EN + ZH ---
bb_new = []
for lang, url in [("en", "https://boltbook.fun/"),
                  ("zh", "https://boltbook.fun/?lang=zh")]:
    fn = f"{BASE}/hot-leg-2139-boltbook-{lang}.html"
    try:
        html = open(fn).read()
    except Exception as e:
        print("BOLTBOOK-FETCH-ERROR", lang, e, flush=True); continue
    if not html.strip():
        print("BOLTBOOK", lang, "EMPTY - skip", flush=True); continue
    addrs = sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", html)))
    kw = {k: html.lower().count(k) for k in ["free share", "first share free", "1 free share",
         "free mint share", "free mint", "免费份额", "首个免费", "免费铸造", "免费mint"]}
    fresh = [a for a in addrs if a.lower() not in {k.lower() for k in seen}]
    print("BOLTBOOK", lang, len(html), "bytes,", len(addrs), "addrs, new-vs-seen:", fresh, kw, flush=True)
    bb_new.extend(fresh)
bb_new = sorted(set(bb_new))
bb_shape = {}
with ThreadPoolExecutor(max_workers=5) as ex:
    for a, sh in zip(bb_new, ex.map(shape_of, bb_new)):
        bb_shape[a] = sh
        print("BOLTBOOK-SHAPE", a, "S1", sh["S1"], "S2", sh["S2"], "mint", sh["mint"], "quote", sh["quote"],
              "free", sh["free"], "agent", sh["agent"], "token", sh["token"], "nft", sh.get("nft"), flush=True)
        seen[a] = {"first_seen": NOW,
                   "status": "sale-shape-NEEDS-VERIFY" if (sh["S1"] or sh["S2"]) and not sh.get("nft") else "checked-not-sale-shape",
                   "note": "S1=%s S2=%s mint=%s quote=%s free=%s agent=%s token=%s nft=%s %s" % (
                       sh["S1"], sh["S2"], sh["mint"], sh["quote"], sh["free"],
                       sh["agent"], sh["token"], sh.get("nft"), sh.get("error", "")),
                   "source": "boltbook-frontpage"}
json.dump(bb_shape, open(f"{BASE}/run-{TS}-boltbook-shape.json", "w"), indent=1)
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
print("BOLTBOOK-SEEN-UPDATED", len(bb_new), "total", len(seen), flush=True)

# --- Leg 3: verify any NEW sale-shape contracts + re-check AgentGlyph (gate-blocked strong lead) ---
to_verify = [a for a, sh in list(shape.items()) + list(bb_shape.items())
             if (sh.get("S1") or sh.get("S2"))]
print("TO-VERIFY-NEW", to_verify, flush=True)
blk = block()
print("BLOCK", blk, flush=True)
for a in to_verify:
    d = {"address": a, "block": blk}
    d["totalSupply"] = call(a, "totalSupply()")
    d["freeClaimed"] = call(a, "freeClaimed()")
    d["freeMinted"] = call(a, "freeMinted()")
    d["freeLeft_user"] = call(a, "freeLeft(address)", enc(USER))
    d["freeUsed_user"] = call(a, "freeUsed(address)", enc(USER))
    d["freeFor_user_1"] = call(a, "freeFor(address,uint256)", enc(USER) + enc_uint(1))
    d["quote_user_1"] = call(a, "quote(address,uint256)", enc(USER) + enc_uint(1))
    d["mintedBy_user"] = call(a, "mintedBy(address)", enc(USER))
    d["balanceOf_user"] = call(a, "balanceOf(address)", enc(USER))
    d["mintOpen"] = call(a, "mintOpen()")
    d["FREE_SUPPLY"] = call(a, "FREE_SUPPLY()")
    d["FREE_SLOTS"] = call(a, "FREE_SLOTS()")
    d["MAX_SUPPLY"] = call(a, "MAX_SUPPLY()")
    print("LEG3", a, d, flush=True)
    json.dump(d, open(f"{BASE}/run-{TS}-leg3-{a[:10]}.json", "w"), indent=1)

# AgentGlyph re-check (already reported blocked 19:52; watch for sellout / slot loss only)
GLYPH = "0x3ef2A97Abf2E43182eACAe323B82d2CAC2132C6A"
g = {"address": GLYPH, "block": blk}
g["totalSupply"] = call(GLYPH, "totalSupply()")
g["freeClaimed"] = call(GLYPH, "freeClaimed()")
g["freeLeft_user"] = call(GLYPH, "freeLeft(address)", enc(USER))
g["freeUsed_user"] = call(GLYPH, "freeUsed(address)", enc(USER))
g["quote_user_1"] = call(GLYPH, "quote(address,uint256)", enc(USER) + enc_uint(1))
g["mintedBy_user"] = call(GLYPH, "mintedBy(address)", enc(USER))
g["mintOpen"] = call(GLYPH, "mintOpen()")
print("GLYPH-RECHECK", g, flush=True)
json.dump(g, open(f"{BASE}/run-{TS}-leg3-glyph.json", "w"), indent=1)

# --- Bridge (read-only) ---
try:
    br = json.load(open(f"{BASE}/scan-bridge.json"))
    cons = br.get("contracts", {})
    snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
    snap_text = json.dumps(snap)
    not_in_snap = [c for c in cons if c.lower() not in snap_text.lower()]
    discarded = [c for c, v in cons.items() if v.get("same_owner_discarded")]
    print("BRIDGE", len(cons), "discarded", len(discarded), "not_in_snapshot", len(not_in_snap), flush=True)
    json.dump({"total": len(cons), "discarded": len(discarded), "not_in_snapshot": len(not_in_snap),
               "not_in_snapshot_list": not_in_snap}, open(f"{BASE}/hot-leg-{TS}-bridge.json", "w"), indent=1)
except Exception as e:
    print("BRIDGE-ERROR", e, flush=True)
print("DONE", flush=True)
