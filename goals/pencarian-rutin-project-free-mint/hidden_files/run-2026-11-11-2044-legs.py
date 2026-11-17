#!/usr/bin/env python3
"""Hot-leg run 2026-11-11 20:44 WIB: Sourcify feed poll + shape-check,
Boltbook EN+ZH front pages, bridge comparison (read-only), binanceai
track-B re-check, RIGFORGE re-check (openedAt / freeSharesLeft / freeBooked).
Read-only except run-2026-11-11-2044-feed*.json and run-2026-11-11-2044-legs.json.
Never writes snapshot/seen/state.
"""
import json, re, time, urllib.request, concurrent.futures

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-11 20:44 WIB"
t0 = time.time()
out = {"started_wib": TS}

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

def get(url, timeout=25, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "free-bacot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode(errors="replace")

# --- 1. Sourcify feed ---
try:
    feed_raw = get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc")
    feed = json.loads(feed_raw)
    json.dump(feed, open(BASE + "run-2026-11-11-2044-feed.json", "w"), indent=1)
    items = feed.get("results", [])
    out["feed"] = {"n": len(items), "newest_verifiedAt": items[0].get("verifiedAt") if items else None,
                   "oldest_verifiedAt": items[-1].get("verifiedAt") if items else None}
except Exception as e:
    out["feed"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
    items = []

seen = set()
try:
    hl = json.load(open(BASE + "hot-leg-seen.json"))
    if isinstance(hl, dict):
        seen |= {k.lower() for k in hl.keys()}
    elif isinstance(hl, list):
        seen |= {str(x).lower() for x in hl}
except Exception:
    pass
for _prevf in ("run-2026-11-11-2029-feed.json", "run-2026-11-11-2031-feed.json"):
    try:
        prev = json.load(open(BASE + _prevf))
        for it in prev.get("results", []):
            seen.add(str(it.get("address", "")).lower())
    except Exception:
        pass
new_addrs = [it.get("address") for it in items if str(it.get("address", "")).lower() not in seen and it.get("address")]
json.dump(new_addrs, open(BASE + "run-2026-11-11-2044-feed-new.json", "w"), indent=1)
out["feed_new"] = new_addrs

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        meta = json.loads(get(url, timeout=25))
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply", "balanceOf"}) and "totalSupply" in names
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        is_nft = bool(names & {"tokenURI", "ownerOf", "safeTransferFrom"}) or "uri" in names
        free_mint_fn = bool(names & {"freeMint", "mintFree", "claimFree", "mint"}) or any(n.lower().startswith("freemint") for n in names)
        early_shape = is_nft and (agent_ref or free_mint_fn)
        return {"address": addr, "S1": s1, "S2": s2, "early_shape": early_shape,
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token, "is_nft": is_nft,
                "fn_count": len(names)}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

shapes = []
if new_addrs:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        shapes = list(ex.map(fetch_abi, new_addrs))
out["feed_shape"] = {"s1_pass": [s["address"] for s in shapes if s.get("S1")],
                     "s2_pass": [s["address"] for s in shapes if s.get("S2")],
                     "early_shape": [s["address"] for s in shapes if s.get("early_shape")],
                     "shapes": shapes}
print("FEED", out["feed"], "NEW", new_addrs, "S1", out["feed_shape"]["s1_pass"],
      "S2", out["feed_shape"]["s2_pass"], "EARLY", out["feed_shape"]["early_shape"], flush=True)

# --- 2. Boltbook EN + ZH (urllib fails w/ RemoteDisconnected since 15:31; curl fallback) ---
import subprocess as _sp
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
    html = None
    try:
        html = get(url, timeout=30)
    except Exception as e:
        try:
            r = _sp.run(["curl", "-sL", "--max-time", "30", url], capture_output=True, text=True, timeout=35)
            if r.stdout and len(r.stdout) > 1000:
                html = r.stdout
                print(f"BOLTBOOK {lang}: urllib fail ({e}); curl OK", flush=True)
        except Exception as e2:
            print(f"BOLTBOOK {lang}: curl also fail {e2}", flush=True)
    if html:
        addrs = sorted(set(a for a in ADDR_RE.findall(html)))
        out[f"boltbook_{lang}"] = {"bytes": len(html), "addrs": addrs, "n": len(addrs)}
        open(BASE + f"run-2026-11-11-2044-boltbook-{lang}.html", "w").write(html)
        print(f"BOLTBOOK {lang}: {len(html)} bytes, {len(addrs)} addrs", flush=True)
    else:
        out[f"boltbook_{lang}"] = {"bytes": 0, "error": "urllib+curl failed", "addrs": []}
        print(f"BOLTBOOK {lang}: FAIL", flush=True)

try:
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = {str((v or {}).get("address", "")).lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
    snap_addrs |= {str((v or {}).get("address") or (v or {}).get("sale") or "").lower() for v in snap.get("track_c", {}).values() if isinstance(v, dict)}
except Exception:
    snap_addrs = set()
bb_new = []
for lang in ("en", "zh"):
    for a in out.get(f"boltbook_{lang}", {}).get("addrs", []):
        if a.lower() not in seen and a.lower() not in snap_addrs and a not in bb_new:
            bb_new.append(a)
out["boltbook_new"] = bb_new
print("BOLTBOOK NEW:", bb_new, flush=True)

# --- 3. Bridge comparison (read-only) ---
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = bridge.get("contracts", {})
    snap_addrs_l = {str((v or {}).get("address", "")).lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
    not_in_snap = [a for a in bcontracts if a.lower() not in snap_addrs_l]
    discarded = [a for a in bcontracts if bcontracts[a].get("same_owner_discarded")]
    out["bridge"] = {"total": len(bcontracts), "not_in_snapshot": not_in_snap,
                     "same_owner_discarded": discarded,
                     "mtime": "2026-11-08 18:21 (stale, last write)"}
    print("BRIDGE total", len(bcontracts), "not_in_snapshot", len(not_in_snap), "discarded", len(discarded), flush=True)
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
    print("BRIDGE FAIL", e, flush=True)

# --- 4. binanceai track-B re-check + RIGFORGE re-check (eth_call via curl) ---
import subprocess
from Crypto.Hash import keccak
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENT = "masgayut.ai"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]

def eth_call(to, data):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
               "params": [{"to": to, "data": data}, "latest"]}
    for ep in EPS:
        try:
            r = subprocess.run(["curl", "-sL", "--max-time", "25", "-X", "POST", ep,
                                "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                               capture_output=True, text=True, timeout=30)
            res = json.loads(r.stdout)
            if "result" in res:
                return res["result"]
        except Exception:
            continue
    return None

def to_int(v):
    try:
        return int(v, 16) if v and v != "0x" else None
    except Exception:
        return None

BIN_MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
val = eth_call(BIN_MINT, sel("launched()"))
out["binanceai"] = {"launched_raw": val, "launched": (to_int(val) == 1) if val else None}
print("BINANCEAI launched:", out["binanceai"], flush=True)

RIG_SALE = "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d"
rig = {}
rig["freeSharesLeft"] = to_int(eth_call(RIG_SALE, sel("freeSharesLeft()")))
rig["openedAt"] = to_int(eth_call(RIG_SALE, sel("openedAt()")))
rig["freeClaimed"] = to_int(eth_call(RIG_SALE, sel("freeClaimed()")))
# freeTaken(agentId string) -> keccak256("masgayut.ai") as bytes32 arg: use string arg encoding
import hashlib
def enc_str(s):
    b = s.encode()
    return ("0x" + hashlib.sha3_256(b).hexdigest()[:64]) if False else None
# agentId is string param: ABI-encode dynamic string: offset 32, length, data padded
def enc_dyn_string(s):
    b = s.encode()
    pad = (32 - len(b) % 32) % 32
    return (32).to_bytes(32, "big").hex() + len(b).to_bytes(32, "big").hex() + b.hex() + "00" * pad
rig["freeTaken_agentId"] = to_int(eth_call(RIG_SALE, sel("freeTaken(string)") + enc_dyn_string(AGENT)))
rig["freeBooked_user"] = to_int(eth_call(RIG_SALE, sel("freeBooked(address)") + enc(USER)))
rig["sharesLeftFor_agentId"] = to_int(eth_call(RIG_SALE, sel("sharesLeftFor(string)") + enc_dyn_string(AGENT)))
out["rigforge"] = rig
print("RIGFORGE:", rig, flush=True)

out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-11-2044-legs.json", "w"), indent=1)
print("LEGS DONE in", out["elapsed_s"], "s", flush=True)
