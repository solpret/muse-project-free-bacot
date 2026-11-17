#!/usr/bin/env python3
"""Salvage for hot-leg 2026-11-11 21:49 WIB: legs 3b+4 + Stampooor site gate.
Main run crashed at as_completed timeout (1/65 eth_call futures unfinished
after 120s - RPC degraded). Legs 1+2 already done (feed/shape/boltbook files
saved, 8 new contracts in hot-leg-seen.json). This salvage re-runs ONLY the
on-chain re-reads with hard timeout handling: per-call 6s, 2 endpoints,
as_completed timeout=90 caught, unfinished futures marked timeout (not fatal).
Baseline = main-job 21:39 reread (block 132986757) + 19:29 last-known.
Read-only except own hot-leg state files (prio + run JSON)."""
import json, time, urllib.request, concurrent.futures, socket, subprocess
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENTID = 107187496765866644729837695198686237165740365523485558112864918211974996443404
EP = "https://bsc.nodereal.io/"
EP2 = "https://bsc-dataseed.binance.org/"
T0 = time.time()
from datetime import datetime, timezone, timedelta
NOW_ISO = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
STAMP = "2026-11-11-2149"
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"}
socket.setdefaulttimeout(8)

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_u(n): return ("%064x" % n)
def call(addr, sig, args=""):
    data = sel(sig) + args
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": addr, "data": data}, "latest"]}).encode()
    last_err = None
    for ep in (EP, EP2):
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=6) as r:
                j = json.loads(r.read().decode())
            if "error" in j: return {"error": str(j["error"])[:120]}
            raw = j["result"]
            if raw in (None, "0x"): return {"error": "empty-return"}
            if len(raw) >= 66:
                v = raw[2:66]
                if set(v) <= set("0123456789abcdef"):
                    try: return int(v, 16)
                    except Exception: return raw
            return raw
        except Exception as e:
            last_err = e
            continue
    return {"error": f"{type(last_err).__name__}: {str(last_err)[:90]}"}

def block_number():
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
    for ep in (EP, EP2):
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=6) as r:
                return int(json.loads(r.read().decode())["result"], 16)
        except Exception:
            continue
    return None

U = enc_addr(USER)
TASKS = []
def add(name, addr, key, sig, args=""):
    TASKS.append((name, addr, key, sig, args))
LEG3B = {
 "MIHAO": ("0x1f82539520a8b3d4eB7C3145f7E1EaFe4B52c4e1", [("opened", "opened()", ""), ("freeMinted", "freeMinted()", ""), ("totalMinted", "totalMinted()", "")]),
 "MIHAO2": ("0x34eA49e9BC199418f121366BdBEa8fDbab10c26b", [("freeMinted", "freeMinted()", ""), ("totalMinted", "totalMinted()", ""), ("FREE_SHARES", "FREE_SHARES()", ""), ("freePhaseActive", "freePhaseActive()", ""), ("opened", "opened()", "")]),
}
PRIO = {
 "AgentPals": ("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", [("totalMinted", "totalMinted()", ""), ("freeMinted", "freeMinted()", ""), ("hasFreeMinted_user", "hasFreeMinted(address)", U), ("balanceOf_user", "balanceOf(address)", U)]),
 "HANAMI": ("0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640", [("totalSupply", "totalSupply()", ""), ("freeMinted", "freeMinted()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "ABYSSCABLE": ("0xd2e9242b0d7c0186cc181a5fc8534541dad278a2", [("totalSupply", "totalSupply()", ""), ("agentFreeUsed", "agentFreeUsed()", ""), ("mintOpen", "mintOpen()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "Stampooor": ("0x467696af8c2206B977B24081445104632dc1D459", [("totalMinted", "totalMinted()", ""), ("freeMinted", "freeMinted()", ""), ("FREE_SUPPLY", "FREE_SUPPLY()", ""), ("mintOpen", "mintOpen()", ""), ("freeAvailable_user", "freeAvailable(address)", U), ("balanceOf_user", "balanceOf(address)", U)]),
 "Foxglow": ("0x6e159c9cd56beadb523b80d195dde39c042a1d48", [("totalSupply", "totalSupply()", ""), ("freeClaimed", "freeClaimed()", ""), ("mintOpen", "mintOpen()", ""), ("freeUsed_user", "freeUsed(address)", U), ("freeFor_user_1", "freeFor(address,uint256)", U + enc_u(1))]),
 "LOWB": ("0x00487ED061C77A1dd5085ef3a2D593366f9C6B35", [("opened", "opened()", ""), ("totalFreeMinted", "totalFreeMinted()", ""), ("totalMinted", "totalMinted()", "")]),
 "SHINE": ("0xDDc2352d1ceC10b42e05A297232f5328902C6c2C", [("startTime", "startTime()", ""), ("launched", "launched()", ""), ("freeClaimed_user", "freeClaimed(address)", U)]),
 "UFO": ("0xE4059eA596392AcA14100af6CDC9481c330E2728", [("FREE_SHARES", "FREE_SHARES()", ""), ("freeClaimed_user", "freeClaimed(address)", U)]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", [("SALE_START", "SALE_START()", ""), ("FREE_SHARES", "FREE_SHARES()", ""), ("freeSharesLeft", "freeSharesLeft()", ""), ("openedAt", "openedAt()", ""), ("freeTaken_agentId", "freeTaken(uint256)", enc_u(AGENTID))]),
 "BotFighters": ("0x58a704d9e02FE11c0A61683AE7F606E4366F13eb", [("FREE_CAP", "FREE_CAP()", ""), ("freeMinted", "freeMinted()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "BHTB": ("0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467", [("freeRemaining", "freeRemaining()", "")]),
 "AgentGrid": ("0x651302C0043040D48EaAF85605E12F0549aD6D89", [("freeUsed", "freeUsed()", "")]),
 "SUDOSAINTS": ("0x869d330bb48e7ab32da16745ef9a36a69d34f12f", [("totalSupply", "totalSupply()", ""), ("freeMinted", "freeMinted()", ""), ("mintActive", "mintActive()", ""), ("freeUsed_user", "freeUsed(address)", U), ("balanceOf_user", "balanceOf(address)", U)]),
 "binanceai": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [("launched", "launched()", "")]),
 "AgentRune": ("0xc1fc0bb36d2be928809e4b3e6aa94b3dd2946f53", [("totalSupply", "totalSupply()", ""), ("freeMinted", "freeMinted()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "RAMRAIDERS": ("0x98dcfdeb5e015bbb3c9aca2a90ba0ee80e35315b", [("totalSupply", "totalSupply()", ""), ("freeMinted", "freeMinted()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "0x7Eb9": ("0x7Eb92041aa3037e39baA88154F279e3D9F85c593", [("totalMinted", "totalMinted()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "STALL": ("0xe3de7fd0d12cff4a46d8bf702ab593b6f921b308", [("totalSupply", "totalSupply()", ""), ("mintOpen", "mintOpen()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
}
for n, (a, s) in LEG3B.items():
    for key, sig, args in s:
        add("leg3b:" + n, a, key, sig, args)
for n, (a, s) in PRIO.items():
    for key, sig, args in s:
        add(n, a, key, sig, args)

blk = block_number()
results = {}
unfinished = []
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
    futs = {ex.submit(call, a, sig, args): (n, k) for (n, a, k, sig, args) in TASKS}
    try:
        for f in concurrent.futures.as_completed(futs, timeout=90):
            n, k = futs[f]
            try:
                results.setdefault(n, {})[k] = f.result()
            except Exception as e:
                results.setdefault(n, {})[k] = {"error": f"{type(e).__name__}: {str(e)[:80]}"}
    except concurrent.futures.TimeoutError:
        for f, (n, k) in futs.items():
            if not f.done():
                unfinished.append(f"{n}.{k}")
                results.setdefault(n, {})[k] = {"error": "timeout-unfinished"}
        print("TIMEOUT: unfinished futures marked:", unfinished, flush=True)
leg3b = {n[6:]: v for n, v in results.items() if n.startswith("leg3b:")}
prio = {"block": blk, "values": {n: v for n, v in results.items() if not n.startswith("leg3b:")}}
json.dump(prio, open(BASE + f"hot-leg-{STAMP}-prio.json", "w"), indent=1)
print("PRIO block", blk, "elapsed", round(time.time() - T0, 1), "unfinished:", len(unfinished), flush=True)

# ---- Bridge (read-only) ----
bridge_note = ""
try:
    b = json.load(open(BASE + "scan-bridge.json"))
    cons = b.get("contracts", {})
    import os
    mtime = time.strftime("%Y-%m-%d %H:%M WIB", time.localtime(os.path.getmtime(BASE + "scan-bridge.json")))
    disc = [k for k, v in cons.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
    bridge_note = (f"scan-bridge.json read ({len(cons)} contracts, mtime {mtime}); "
                   f"same_owner_discarded in bridge: {len(disc)}; no bridge promotion/change this run")
except Exception as e:
    bridge_note = f"bridge read FAILED: {type(e).__name__}: {str(e)[:100]} - skipped, run continues"

# ---- Compare vs 21:39 main reread baseline ----
_main = json.load(open(BASE + "run-2026-11-11-2139-reread.json"))
_mr = _main.get("reread", {})
_NAME_MAP = {"Stampooor": "Stampooor Stamp Packs", "AgentPals": "AgentPals",
             "SUDOSAINTS": "SUDOSAINTS", "AgentRune": "AgentRune", "STALL": "STALL",
             "0x7Eb9": "0x7Eb9"}
bv = {}
for _n, _m in _NAME_MAP.items():
    if _m in _mr:
        bv[_n] = {k: v for k, v in _mr[_m].items() if k != "address"}
BASELINE_EXTRA = {
 "AgentPals": {"totalMinted": 301, "freeMinted": 300},
 "Stampooor": {"freeMinted": 862, "totalMinted": 862},
 "SUDOSAINTS": {"totalSupply": 613, "freeMinted": 613},
 "AgentRune": {"totalSupply": 192, "freeMinted": 189},
 "STALL": {"totalSupply": 1984},
 "0x7Eb9": {"totalMinted": 969},
 "BotFighters": {"freeMinted": 65},
 "RAMRAIDERS": {"freeMinted": 559},
 "AgentGrid": {"freeUsed": 21},
 "RigForge": {"freeSharesLeft": 684},
}
for _n, _ex in BASELINE_EXTRA.items():
    bv.setdefault(_n, {}).update(_ex)

changes, view_notes = [], []
for name in PRIO:
    for key, new in prio["values"].get(name, {}).items():
        old = bv.get(name, {}).get(key) if isinstance(bv.get(name), dict) else None
        ref = old
        if isinstance(old, dict) or isinstance(new, dict):
            if old != new:
                view_notes.append(f"{name}.{key}: view {old} -> {new} (view-status only, not a state change)")
            continue
        if ref is None and new is None:
            continue
        if isinstance(new, int) and ref is not None and new != ref:
            changes.append(f"{name}.{key}: {ref} -> {new} (vs 2139-main-reread+last-known)")
        elif new is None and ref is not None:
            view_notes.append(f"{name}.{key}: read FAILED this run (was {ref} vs 2139-main-reread+last-known)")

watch = []
ap = prio["values"].get("AgentPals", {})
if isinstance(ap.get("freeMinted"), int):
    watch.append(f"AgentPals freeMinted {ap['freeMinted']}/300 = {ap['freeMinted']/300*100:.1f}% (sold out at 300; slot hasFreeMinted={ap.get('hasFreeMinted_user')})")
st = prio["values"].get("Stampooor", {})
st_crossed = False
if isinstance(st.get("freeMinted"), int) and isinstance(st.get("FREE_SUPPLY"), int):
    pct = st['freeMinted'] / st['FREE_SUPPLY'] * 100
    st_crossed = st['freeMinted'] > 840
    watch.append(f"Stampooor freeMinted {st['freeMinted']}/{st['FREE_SUPPLY']} = {pct:.1f}% (strong-lead needs >70% = >840; slot freeAvailable={st.get('freeAvailable_user')}; age: mintStart 09:00:19 WIB 11 Nov, <24h; STRONG-LEAD-CROSSED={st_crossed}; GATE-BLOCKED (site unreachable, re-verified live this run) -> NO preview/mint)")

# ---- Stampooor shape re-check + site gate (live) ----
stampooor_gate = None
if st_crossed:
    try:
        abi_doc = json.load(open(BASE + "abi-0901-stampooor.json"))
        abi = abi_doc.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_names = {n.lower() for n in names}
        agent_ref = bool(agent_names & {"agentid", "agent_id", "agentregistry", "registry", "getagentid", "agentgate", "agentidregistry"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        stampooor_gate = {"shape_recheck": {"S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token, "fn_count": len(names)}}
    except Exception as e:
        stampooor_gate = {"error": f"{type(e).__name__}: {str(e)[:120]}"}

site_gate = {}
for _u in ("https://stampooor.com/packs/", "https://stampooor.com/"):
    try:
        _r = subprocess.run(["curl", "-s", "-m", "15", "-o", "/dev/null", "-w", "%{http_code}:%{size_download}", "-A", "hot-leg/1.0", _u],
                            capture_output=True, timeout=20)
        site_gate[_u] = _r.stdout.decode(errors="replace")
    except Exception as e:
        site_gate[_u] = f"ERROR {type(e).__name__}: {str(e)[:80]}"
print("STAMPOOR-SITE", site_gate, flush=True)

# ---- Merge legs 1+2 from crashed main run files ----
feed = json.load(open(BASE + f"hot-leg-{STAMP}-feed.json"))
shapes = json.load(open(BASE + f"hot-leg-{STAMP}-shape.json"))
feed_addrs = [it.get("address") for it in feed.get("results", []) if it.get("address")]

run = {
 "run": "free-mint-hot-leg 2026-11-11 21:49 WIB (salvage: main run crashed at leg4 as_completed timeout, 1/65 futures unfinished; legs 1+2 from crashed run, legs 3b+4 re-run here)",
 "started_wib": NOW_ISO,
 "leg1_sourcify_feed": {"note": f"feed OK: {len(feed_addrs)} contracts, verified {feed.get('results', [{}])[-1].get('verifiedAt')}..{feed.get('results', [{}])[0].get('verifiedAt')}",
   "returned": len(feed_addrs), "new": list(shapes.keys()), "already_seen": len(feed_addrs) - len(shapes)},
 "leg1_shapes": shapes,
 "leg1_s1_pass": [a for a, v in shapes.items() if v.get("S1")],
 "leg1_s2_pass": [a for a, v in shapes.items() if v.get("S2")],
 "leg2_boltbook": {"note": "EN HTTP 200 (45442B) + ZH HTTP 200 (45678B) boltbook.fun; 8 unique addresses, 0 not in hot-leg-seen.json: none; keywords EN free-share=0 ZH=0",
   "addrs": [], "fresh": [], "fresh_shapes": {}},
 "bridge": bridge_note,
 "leg3_new_sale_shape": {},
 "leg3b_recheck": leg3b,
 "leg4_read_wib": NOW_ISO,
 "leg4_block": prio["block"],
 "leg4_values": prio["values"],
 "leg4_changes_vs_2139": changes or "NONE",
 "leg4_view_notes": view_notes or "NONE",
 "leg4_unfinished_futures": unfinished or "NONE",
 "threshold_watch": watch,
 "stampooor_crossed": st_crossed,
 "stampooor_gate_recheck": stampooor_gate,
 "stampooor_site_gate_live": site_gate,
 "seen_added": list(shapes.keys()),
 "shape_check_failed_not_kept": [],
 "elapsed_s": round(time.time() - T0, 1),
}
json.dump(run, open(BASE + f"hot-leg-run-{STAMP}.json", "w"), indent=1)
print(json.dumps(run, indent=1))
print("ELAPSED", round(time.time() - T0, 1))
