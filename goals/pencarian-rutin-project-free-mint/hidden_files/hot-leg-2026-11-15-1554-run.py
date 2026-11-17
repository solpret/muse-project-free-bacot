#!/usr/bin/env python3
"""Hot-leg run 2026-11-15 15:54 WIB. Legs (1) Sourcify feed, (2) Boltbook en+zh,
(3) shape-check new contracts S1/S2, (4) light re-read of live snapshot items
(Matrix Agents, ONI, binanceai pending claim), bridge read-only.
Read-only except hot-leg-seen.json (own file) + this run log. No preview/mint."""
import json, re, time, urllib.request, concurrent.futures, subprocess
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = "2026-11-15T15:54+07:00"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124",
            "0x8b47354E7b76B1970a0D06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
t0 = time.time()

def get(url, timeout=20):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout),
                        "-A", "hot-leg/1.0", url],
                       capture_output=True, text=True, timeout=timeout + 10)
    if r.returncode != 0:
        raise RuntimeError(f"curl rc={r.returncode}: {r.stderr[:120]}")
    return r.stdout

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower(): v for k, v in seen.items()}

# (1) Sourcify feed
feed = json.loads(get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"))
results = feed.get("results", [])
feed_addrs = [r["address"] for r in results]
feed_new = [a for a in feed_addrs if a.lower() not in seen_l and a not in EXCLUDED
            and a.lower() != REG.lower()]

# (2) Boltbook en + zh
def boltbook(lang_url):
    html = get(lang_url)
    addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    return len(html), addrs
en_bytes, en_addrs = boltbook("https://boltbook.fun/")
zh_bytes, zh_addrs = boltbook("https://boltbook.fun/?lang=zh")
bb_addrs = sorted(set(en_addrs) | set(zh_addrs))
bb_new = [a for a in bb_addrs if a.lower() not in seen_l and a not in EXCLUDED]

# (3) shape-check new contracts
def shape(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        meta = json.loads(get(url, timeout=15))
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId",
                                  "agentGate", "AgentGate"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = (is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"})
              and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref)
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
                "is_token": is_token, "n_fns": len(names), "status": "checked",
                "verifiedAt": next((r.get("verifiedAt") for r in results
                                    if r["address"].lower() == addr.lower()), None)}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}",
                "verifiedAt": None}

targets = feed_new + [a for a in bb_new if a.lower() not in {x.lower() for x in feed_new}]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    shape_out = list(ex.map(shape, targets))

# (4) light re-read: live snapshot items only (main job re-read 37 items at 15:04,
# block 133700946; hot-leg re-checks the 3 live ones for 5-min changes)
from Crypto.Hash import keccak
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        elif isinstance(a, str) and a.startswith("0x"):
            d += enc_u(int(a, 16))
        else:
            d += enc_u(int(a))
    return d
U = [USER]
LEG4 = {
 "Matrix Agents": ("0x1F669b714337F3C2585072c53fdDD89581F928fF", [
    ("totalSupply", "totalSupply()", []), ("freeMinted", "freeMinted()", []),
    ("freeRemaining", "freeRemaining()", []), ("mintOpen", "mintOpen()", [])]),
 "ONI": ("0x99d01eD93829DBB0EEc11F3a733388c789dA6caD", [
    ("totalMinted", "totalMinted()", []), ("freeClaimed_user", "freeClaimed(address)", U),
    ("freeClaimedOf_user", "freeClaimedOf(address)", U),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "AgentBubble": ("0x0D72970046c056Db90888351b739246F468BFf0B", [
    ("totalSupply", "totalSupply()", []), ("freeMinted", "freeMinted()", []),
    ("mintOpen", "mintOpen()", [])]),
 "BinanceAI-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched", "launched()", []), ("failed", "failed()", []),
    ("isRefundPhase", "isRefundPhase()", []), ("totalShares", "totalShares()", []),
    ("tokenClaimed_user", "tokenClaimed(address)", U)]),
}
leg4_out = {"reads": {}, "block": None, "error": None}
try:
    payload = []
    idx = 0
    mapping = []
    for name, (addr, views) in LEG4.items():
        leg4_out["reads"][name] = {"address": addr, "views": {}}
        for vn, sig, args in views:
            payload.append({"jsonrpc": "2.0", "id": idx, "method": "eth_call",
                            "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
            mapping.append((name, vn))
            idx += 1
    payload.append({"jsonrpc": "2.0", "id": idx, "method": "eth_blockNumber", "params": []})
    out = subprocess.run(["curl", "-sL", "--max-time", "60", "-X", "POST",
                          "https://bsc-dataseed.binance.org/",
                          "-H", "Content-Type: application/json",
                          "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=70).stdout
    resp = json.loads(out)
    by_id = {r.get("id"): r for r in resp} if isinstance(resp, list) else {}
    for i, (name, vn) in enumerate(mapping):
        r = by_id.get(i, {})
        leg4_out["reads"][name]["views"][vn] = to_int(r.get("result")) if r.get("result") else None
    blk = by_id.get(idx, {}).get("result")
    leg4_out["block"] = int(blk, 16) if blk else None
except Exception as ex:
    leg4_out["error"] = f"{type(ex).__name__}: {str(ex)[:150]}"

# bridge (read-only)
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    b_contracts = bridge.get("contracts", bridge) if isinstance(bridge, dict) else bridge
    if isinstance(b_contracts, dict):
        b_list = list(b_contracts.keys())
        b_disc = sum(1 for v in b_contracts.values()
                     if isinstance(v, dict) and v.get("same_owner_discarded"))
    else:
        b_list, b_disc = b_contracts, 0
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for coll in ("contracts", "track_c", "pending_claims"):
        c = snap.get(coll, {})
        if isinstance(c, dict):
            snap_addrs |= {k.lower() for k in c.keys()}
            snap_addrs |= {(v.get("address") or "").lower() for v in c.values()
                           if isinstance(v, dict)}
        elif isinstance(c, list):
            snap_addrs |= {x.get("address", "").lower() for x in c if isinstance(x, dict)}
    not_in_snap = [a for a in b_list if a.lower() not in snap_addrs]
    bridge_out = {"contracts": len(b_list), "same_owner_discarded": b_disc,
                  "not_in_snapshot": len(not_in_snap),
                  "not_in_snapshot_list": not_in_snap}
except Exception as ex:
    bridge_out = {"error": f"{type(ex).__name__}: {str(ex)[:120]}"}

# update seen (own file only)
added = []
for a in targets:
    if a.lower() not in seen_l:
        seen[a] = NOW
        added.append(a)
if added:
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"))

out = {"run": "free-mint-hot-leg 2026-11-15T15:54+07:00", "started_wib": NOW,
       "sourcify_feed": {"total": len(results), "new": len(feed_new),
                         "new_contracts": feed_new,
                         "top": feed_addrs[0] if feed_addrs else None,
                         "top_verifiedAt": results[0].get("verifiedAt") if results else None},
       "boltbook_en": {"bytes": en_bytes, "full_address_contracts": len(en_addrs),
                       "new": len([a for a in en_addrs if a.lower() not in seen_l]),
                       "new_contracts": [a for a in en_addrs if a.lower() not in seen_l]},
       "boltbook_zh": {"bytes": zh_bytes, "full_address_contracts": len(zh_addrs),
                       "new": len([a for a in zh_addrs if a.lower() not in seen_l]),
                       "new_contracts": [a for a in zh_addrs if a.lower() not in seen_l]},
       "shape_check_targets": targets, "shape_check": shape_out,
       "shape_hits": [o["address"] for o in shape_out if o.get("S1") or o.get("S2")],
       "leg4_reread": leg4_out,
       "bridge": bridge_out,
       "seen_added": added, "seen_n": len(seen), "seen_n_prev": len(seen) - len(added),
       "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "hot-leg-run-2026-11-15-1554.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in
                  ("sourcify_feed", "boltbook_en", "boltbook_zh", "shape_hits",
                   "leg4_reread", "bridge", "seen_added", "seen_n", "elapsed_s")}, indent=1))
print("SHAPE:", json.dumps(shape_out, indent=1))
