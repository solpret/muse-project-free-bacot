#!/usr/bin/env python3
"""Hot-leg triage run 2026-11-11 21:29 WIB.
- Compare run-2026-11-11-2129-reread.json vs 2104 baseline (changes only).
- Shape-check 3 Boltbook-new addresses (legs.py only listed them).
- On-chain triage of 3 early-shape feed contracts (totalSupply/freeMinted/mintOpen/slot).
- Re-read MECHA 0xEEe3, 0x2e50 (freeMintX family), CRTSAINTS 0x2A3d.
Read-only except run-2026-11-11-2129-triage.json + hot-leg-seen.json additions.
"""
import json, re, time, subprocess, urllib.request, concurrent.futures
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-11 21:29 WIB"
t0 = time.time()
out = {"started_wib": TS}
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return "%064x" % n
def to_int(v):
    try:
        return int(v, 16) if v and v != "0x" else None
    except Exception:
        return None

def post_rpc(ep, payload, timeout=25):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)

def batch_call(addr, sigs):
    calls, keys = [], []
    for i, sig in enumerate(sigs):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        elif "(uint256)" in sig and "freeTaken" in sig:
            data = sel(sig); key = base
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
            d = {}
            for item, key in zip(res, keys):
                d[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return d
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

out["block"] = get_block()
print("BLOCK", out["block"], flush=True)

# ---- 1. Compare reread 2129 vs 2114 ----
new_r = json.load(open(BASE + "run-2026-11-11-2129-reread.json"))
old_r = json.load(open(BASE + "run-2026-11-11-2114-reread.json"))
changes, view_notes, batch_fails = [], [], []
for section in ("reread", "track_c"):
    for name, vals in new_r.get(section, {}).items():
        old_vals = old_r.get(section, {}).get(name, {})
        if isinstance(vals, dict) and vals.get("_batch_fail"):
            batch_fails.append(f"{section}:{name} batch_fail")
            continue
        for k, v in vals.items():
            if k in ("address", "_batch_fail"):
                continue
            ov = old_vals.get(k) if isinstance(old_vals, dict) else None
            if isinstance(v, int) and isinstance(ov, int) and v != ov:
                changes.append(f"{section}:{name}.{k}: {ov} -> {v}")
            elif v is None and isinstance(ov, int):
                view_notes.append(f"{section}:{name}.{k}: read FAILED this run (was {ov})")
            elif isinstance(v, int) and ov is None:
                view_notes.append(f"{section}:{name}.{k}: now readable = {v} (was unreadable)")
out["reread_compare"] = {"block_old": old_r.get("block"), "block_new": new_r.get("block"),
                         "changes": changes, "view_notes": view_notes, "batch_fails": batch_fails}
print("CHANGES:", changes or "NONE", flush=True)
print("VIEW_NOTES:", view_notes or "NONE", flush=True)
print("BATCH_FAILS:", batch_fails or "NONE", flush=True)

# ---- 2. Shape-check Boltbook-new addresses ----
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"}
def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    raw = None
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "free-bacot/1.0"})
            with urllib.request.urlopen(req, timeout=25) as r:
                raw = r.read().decode(errors="replace"); break
        except Exception:
            try:
                r = subprocess.run(["curl", "-sL", "--max-time", "25", url],
                                   capture_output=True, text=True, timeout=30)
                if r.stdout and len(r.stdout) > 50:
                    raw = r.stdout; break
            except Exception:
                pass
    if raw is None:
        return {"address": addr, "error": "fetch failed urllib+curl"}
    try:
        meta = json.loads(raw)
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        is_nft = bool(names & {"tokenURI", "ownerOf", "safeTransferFrom"}) or "uri" in names
        early_shape = is_nft and (agent_ref or bool(names & {"freeMint", "mintFree", "claimFree", "mint"}) or any(n.lower().startswith("freemint") for n in names))
        return {"address": addr, "S1": s1, "S2": s2, "early_shape": early_shape,
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token, "is_nft": is_nft, "fn_count": len(names)}
    except Exception as ex:
        return {"address": addr, "error": f"parse: {type(ex).__name__}: {str(ex)[:120]}"}

legs = json.load(open(BASE + "run-2026-11-11-2129-legs.json"))
bb_new = legs.get("boltbook_new", [])
bb_shapes = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    for r in ex.map(fetch_abi, bb_new):
        bb_shapes[r["address"]] = r
out["boltbook_shapes"] = bb_shapes
print("BOLTBOOK SHAPES:", {a: (s.get("S1"), s.get("S2"), s.get("early_shape"), s.get("fn_count"), s.get("error", "")) for a, s in bb_shapes.items()}, flush=True)

# ---- 3. On-chain triage: early-shape feed + sale/early Boltbook-new ----
LEAN = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
        "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
        "freeClaimed(address)"]
triage_addrs = []
for s in legs["feed_shape"]["shapes"]:
    if s.get("early_shape"):
        triage_addrs.append(s["address"])
for a, s in bb_shapes.items():
    if s.get("S1") or s.get("S2") or s.get("early_shape"):
        triage_addrs.append(a)
triage = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for addr, res in zip(triage_addrs, ex.map(lambda a: batch_call(a, LEAN), triage_addrs)):
        triage[addr] = res
out["early_triage"] = triage
print("EARLY TRIAGE:", triage, flush=True)

# ---- 4. Re-read MECHA / 0x2e50 / CRTSAINTS ----
FOCUS = {
    "MECHA": ("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
              ["totalMinted()", "freeClaimed()", "freePoolSize()", "freePerWallet()",
               "maxSupply()", "mintedBy(address)", "freeUsedBy(address)", "balanceOf(address)"]),
    "0x2e50": ("0x2e508C6510d9550031932f0D6Fe691DCe38E66E3",
               ["totalSupply()", "paidMinted()", "mintOpen()", "mintStart()",
               "FIRST_FREE_CAP()", "X_FREE_CAP()", "MAX_SUPPLY()", "balanceOf(address)"]),
    "CRTSAINTS": ("0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F",
                  ["totalSupply()", "paidMinted()", "mintOpen()", "mintStart()",
                   "FIRST_FREE_CAP()", "X_FREE_CAP()", "MAX_SUPPLY()", "balanceOf(address)"]),
}
focus = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
    for name, (addr, sigs) in FOCUS.items():
        focus[name] = {"address": addr, "values": batch_call(addr, sigs)}
out["focus_reread"] = focus
print("FOCUS:", focus, flush=True)

# ---- 5. Threshold watch: Stampooor + AgentPals from reread ----
rr = new_r.get("reread", {})
st = rr.get("Stampooor Stamp Packs", {}) or rr.get("Stampooor", {})
ap = rr.get("AgentPals", {})
watch = []
if isinstance(st.get("freeMinted"), int) and isinstance(st.get("FREE_SUPPLY"), int):
    pct = st["freeMinted"] / st["FREE_SUPPLY"] * 100
    watch.append(f"Stampooor freeMinted {st['freeMinted']}/{st['FREE_SUPPLY']} = {pct:.2f}% (strong-lead needs >70%; slot freeAvailable/mintOpen={st.get('mintOpen')}; gate-blocked, already reported once 19:05)")
if isinstance(ap.get("freeMinted"), int):
    watch.append(f"AgentPals freeMinted {ap.get('freeMinted')}/300, balanceOf_user={ap.get('balanceOf_user')}, hasFreeMinted_user={ap.get('hasFreeMinted_user')}")
out["threshold_watch"] = watch
print("WATCH:", watch, flush=True)

# ---- 5b. Stampooor gate re-check (site was DNS-unreachable; Lanternfield
# precedent: a blocked site can go live — re-verify before concluding blocked).
try:
    gate = json.load(open("/tmp/stamp-gate-2129.json"))
    out["stampooor_gate_recheck"] = gate
    print("STAMPOOOR GATE:", gate, flush=True)
except Exception as e:
    out["stampooor_gate_recheck"] = {"error": str(e)[:120]}
    print("STAMPOOOR GATE READ FAIL", e, flush=True)

# ---- 6. Update hot-leg-seen.json (new feed + boltbook addresses) ----
seen = json.load(open(BASE + "hot-leg-seen.json"))
added = []
feed_shapes = {s["address"]: s for s in legs["feed_shape"]["shapes"]}
for a, s in feed_shapes.items():
    if a in seen or a.lower() in {k.lower() for k in seen}:
        continue
    seen[a] = {"first_seen_wib": TS, "source": "sourcify-feed-2129",
               "note": f"S1={s.get('S1')} S2={s.get('S2')} early={s.get('early_shape')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')} fns={s.get('fn_count')}",
               "status": "SALE-SHAPE" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"}
    added.append(a)
for a, s in bb_shapes.items():
    if a in seen or a.lower() in {k.lower() for k in seen}:
        continue
    if "error" in s:
        continue
    seen[a] = {"first_seen_wib": TS, "source": "boltbook-2129",
               "note": f"S1={s.get('S1')} S2={s.get('S2')} early={s.get('early_shape')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')} fns={s.get('fn_count')}",
               "status": "SALE-SHAPE" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"}
    added.append(a)
if added:
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["seen_added"] = added
out["seen_total"] = len(seen)
print("SEEN ADDED:", len(added), "TOTAL:", len(seen), flush=True)

out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-11-2129-triage.json", "w"), indent=1)
print("TRIAGE DONE in", out["elapsed_s"], "s", flush=True)
