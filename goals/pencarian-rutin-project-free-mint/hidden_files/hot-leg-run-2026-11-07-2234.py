#!/usr/bin/env python3
"""Hot-leg run 2026-11-07 22:19 WIB. Legs 1-4 + bridge. Read-only except own hot-leg state files. Never writes main snapshot."""
import json, re, subprocess, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-2234"
NOW = "2026-11-07T22:35:00+07:00"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
# RPC degradation (verified 22:29 run): Ankr public RPC now Unauthorized/API-key-required;
# publicnode rate-limited -32005. Working: dataseed endpoints only (slow).
RPCS = ["https://bsc-dataseed.binance.org", "https://bsc-dataseed1.bnbchain.org",
        "https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed3.bnbchain.org"]
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed", "freeAvailable",
              "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted", "freeCardsRemaining"]
out = {"run": "free-mint-hot-leg 2026-11-07 22:34:38 WIB"}
t0 = time.time()

def rpc_json(method, params, timeout=4):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                o = json.load(r)
            if "error" in o:
                continue
            return o.get("result"), rpc
        except Exception:
            continue
    return None, None

# ---------- Leg 1: Sourcify feed ----------
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
feed_addrs = []
try:
    cp = subprocess.run(["curl", "-sS", "--max-time", "25", "-A", "hot-leg/1.0",
                         "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"],
                        capture_output=True, text=True, timeout=30)
    data = json.loads(cp.stdout)
    items = data.get("results", data) if isinstance(data, dict) else data
    for it in items:
        a = it.get("address") or it.get("contractAddress")
        if a:
            feed_addrs.append(a)
    out["leg1_feed"] = {"n": len(feed_addrs), "addrs": feed_addrs}
    json.dump(data, open(f"{BASE}/hot-leg-{TS}-feed.json", "w"), indent=1)
except Exception as e:
    out["leg1_feed"] = {"error": f"{type(e).__name__}: {e}"}
    feed_addrs = []

def shape_check(addr):
    try:
        p = subprocess.run(["curl", "-sS", "--max-time", "20", "-A", "hot-leg/1.0",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                           capture_output=True, text=True, timeout=25)
        if p.returncode != 0:
            return {"address": addr, "error": f"curl rc={p.returncode}: {p.stderr.strip()[:100]}"}
        meta = json.loads(p.stdout)
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate", "AGENT_ID", "agentIdRegistry", "isAgent"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token}
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {str(e)[:100]}"}

RETRY_ADDRS = [a for a, v in seen.items() if isinstance(v, dict) and v.get("status") == "shape-check-failed-transport"]
retries = list(RETRY_ADDRS)
new_addrs = [a for a in feed_addrs if a not in seen and a.lower() not in EXCLUDED and a.lower() != REG.lower()]
for a in retries:
    if a not in new_addrs:
        new_addrs.append(a)
if retries:
    out["leg1_retry"] = {"addrs": retries, "reason": "shape-check failed on transport in earlier runs; retry this run"}
new_excluded = [a for a in feed_addrs if a.lower() in EXCLUDED]
shapes = []
if new_addrs:
    with ThreadPoolExecutor(max_workers=10) as ex:
        shapes = list(ex.map(shape_check, new_addrs))
    for s in shapes:
        if s.get("error"):
            seen[s["address"]] = {"first_seen_wib": seen.get(s["address"], {}).get("first_seen_wib", NOW),
                "note": f"shape-check failed on transport ({s.get('error')}) - NOT verified as not-sale-shape; retry next run",
                "source": seen.get(s["address"], {}).get("source", "sourcify-feed"), "status": "shape-check-failed-transport"}
            continue
        seen[s["address"]] = {"first_seen_wib": NOW,
            "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')}",
            "source": "sourcify-feed", "status": "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "sale-shape"}
    json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
out["leg1"] = {"new": new_addrs, "new_excluded_rediscovered": new_excluded, "shapes": shapes,
               "seen_total": len(seen)}
sale_shapes = [s for s in shapes if s.get("S1") or s.get("S2")]
out["leg3_new_contracts"] = "None - no new sale-shape contract" if not sale_shapes else sale_shapes

# ---------- Leg 2: Boltbook EN + ZH ----------
def fetch_boltbook(url):
    try:
        p = subprocess.run(["curl", "-sS", "-L", "--max-time", "15", "-A", "hot-leg/1.0", url],
                           capture_output=True, text=True, timeout=20)
        return p.stdout or "", p.returncode
    except Exception as e:
        return "", f"ERR {e}"

en, en_rc = fetch_boltbook("https://boltbook.fun/?lang=en")
zh, zh_rc = fetch_boltbook("https://boltbook.fun/?lang=zh")
addr_re = re.compile(r"0x[a-fA-F0-9]{40}")
en_addrs = sorted(set(addr_re.findall(en)))
zh_addrs = sorted(set(addr_re.findall(zh)))
all_addrs = sorted(set(en_addrs) | set(zh_addrs))
kw_en = ["free share", "first share free", "1 free share", "free mint share"]
kw_zh = ["\u514d\u8d39\u4efd\u989d", "\u9996\u4e2a\u514d\u8d39", "\u514d\u8d39\u94f8\u9020", "\u514d\u8d39mint"]
text_low = (en + zh).lower()
kw_hits = {k: text_low.count(k.lower()) for k in kw_en + kw_zh if k.lower() in text_low}
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addr_set = {v.get("address", "").lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
for v in snap.get("track_c", {}).values():
    if isinstance(v, dict):
        for k in ("sale", "token", "address"):
            if v.get(k):
                snap_addr_set.add(str(v[k]).lower())
new_bolt = [a for a in all_addrs if a not in seen]
new_bolt_not_snap = [a for a in all_addrs if a.lower() not in snap_addr_set and a not in seen]
bolt_shapes = {}
for a in new_bolt_not_snap:
    s = shape_check(a)
    if s.get("error"):
        note = f"shape-check failed on transport ({s['error']}) - NOT verified as not-sale-shape; retry next run"
        status = "shape-check-failed-transport"
    else:
        note = (f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} "
                f"free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')}")
        status = "sale-shape" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"
    bolt_shapes[a] = note
    seen[a] = {"first_seen_wib": NOW, "note": note, "source": "boltbook-en" if a in en_addrs else "boltbook-zh",
               "status": status}
in_snap_bolt = [a for a in new_bolt if a.lower() in snap_addr_set]
for a in in_snap_bolt:
    bolt_shapes[a] = "already in snapshot"
if new_bolt:
    json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
out["leg2_boltbook"] = {"en_bytes": len(en), "en_rc": en_rc, "zh_bytes": len(zh), "zh_rc": zh_rc,
                        "en_addrs": len(en_addrs), "zh_addrs": len(zh_addrs), "unique_addrs": len(all_addrs),
                        "keyword_hits": kw_hits, "new_vs_seen": new_bolt, "new_vs_snapshot": new_bolt_not_snap,
                        "shape_check": bolt_shapes, "seen_total": len(seen)}

# ---------- RPC probe ----------
blk, blk_rpc = rpc_json("eth_blockNumber", [], timeout=4)
out["rpc_probe"] = {"block": int(blk, 16) if blk else None, "via": blk_rpc,
                    "note": "All 5 BSC RPC endpoints tried; None = transport failure, NOT state."}

# ---------- Leg 3 (light): pool/slot views only for new sale-shapes; age NOT attempted via slow getLogs ----------
import sys as _sys; _sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
LEG4_EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
            "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/",
            "https://rpc.ankr.com/bsc"]
DEADLINE = time.time() + 120
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def raw(to, data):
    if time.time() > DEADLINE:
        return "deadline"
    for ep in LEG4_EPS:
        if time.time() > DEADLINE:
            return "deadline"
        try:
            v = _fast_single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
            if v is None or v == "0x":
                return None
            try:
                return int(v, 16)
            except Exception:
                return v
        except Exception:
            continue
    return None
def call(to, sig, args=""): return raw(to, sel(sig) + args)

if sale_shapes and blk is not None:
    leg3 = {}
    for s in sale_shapes:
        a = s["address"]
        d = {"S1": s.get("S1"), "S2": s.get("S2")}
        for sig, key in [("freeClaimed()", "freeClaimed"), ("freeMinted()", "freeMinted"),
                         ("freeSharesRemaining()", "freeSharesRemaining"), ("freeLeft(address)", "freeLeft_user"),
                         ("quote(address,uint256)", "quote_user1"), ("freeFor(address)", "freeFor_user"),
                         ("mintOpen()", "mintOpen"), ("totalSupply()", "totalSupply"),
                         ("balanceOf(address)", "balanceOf_user"), ("freeUsed()", "freeUsed")]:
            if sig.startswith("quote("):
                d[key] = call(a, sig, enc(USER) + enc_uint(1))
            elif "address" in sig:
                d[key] = call(a, sig, enc(USER))
            else:
                d[key] = call(a, sig)
        d["age"] = "UNVERIFIED this run (getLogs age check skipped for speed; watchlist-only until verified)"
        leg3[a] = d
    out["leg3_verify"] = leg3
elif sale_shapes:
    out["leg3_verify"] = "SKIPPED - RPC unreachable; new sale-shape(s) NOT verified, NOT a lead, NOT previewed/minted."

# ---------- Leg 4: re-read (read-only) ----------
NFT_VIEWS = ["totalSupply()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
             "balanceOf(address)", "mintedBy(address)", "freeUsed(address)",
             "claimedFree(address)", "mintOpen()"]
SALE_VIEWS = ["freeClaimed()", "freeSharesRemaining()", "freeLeft(address)",
              "quote(address,uint256)", "mintedBy(address)", "mintOpen()",
              "totalMinted()", "freeMinted()", "totalSupply()", "balanceOf(address)",
              "freeFor(address)"]
LEAD_VIEWS = ["totalMints()", "MAX_MINTS()", "freeLeft(address)", "quote(address,uint256)",
              "mintedBy(address)", "mintOpen()", "totalSupply()", "balanceOf(address)"]
ITEMS = {
 "Orchidia": ("0x09bcdd97186f6f37521bd1b281d329e48ac54b89", NFT_VIEWS),
 "Agent Goats": ("0x0E9E0a3B46dC0d36A1Ab64f553Dd8A0693E6aAa6", NFT_VIEWS),
 "Tacotron": ("0x05debe4445232205ae7e79d02cb5de5aa0641eff", NFT_VIEWS),
 "Agent Frogs": ("0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31", NFT_VIEWS),
 "Wuyuhive": ("0x250e800025a9a7861970e253bab6975a57f80567", NFT_VIEWS),
 "Thronemind": ("0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90", NFT_VIEWS),
 "Ink Koi": ("0xbd4B4e7189ae9356514664146b0eD683601200A9", NFT_VIEWS),
 "Night Bandits Club": ("0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf", NFT_VIEWS),
 "ADCHAR": ("0x6E8b05C2dD1C625D839f33f60B837d9AF25E6044", NFT_VIEWS),
 "Saturnagent": ("0xef870a9b4a529373fb2e174b59ca7a66eb018074", SALE_VIEWS),
 "Lumenhold": ("0x9701980b0afd825134390ee46fb3bd675a2f356f", SALE_VIEWS),
 "Horus AI": ("0x794ad67a5590c7e5848e49181297f9cc7c6ce00e", NFT_VIEWS),
 "AURISLE": ("0xC52a979C20C5a43e5Be4Ffa6d1A4DD50069D5E2D", NFT_VIEWS),
 "DinoAgent": ("0xcE19D6A5FF15e088D4bf23614242927139084895", NFT_VIEWS),
 "Tri333": ("0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f", NFT_VIEWS),
 "LOCKSMITH": ("0x05e8738290be6639fD0f7236ebF444E5466D3164", NFT_VIEWS),
 "AgentBook": ("0xEECaCBE6eAC6D6F2a38e8daA9049C7AA08aD43b0", SALE_VIEWS),
 "CipherAgent": ("0x158b5e25015758a94703A27c152889451E5d52E5", LEAD_VIEWS),
 "MarsAgent": ("0x2231FdAe405c33dc4993f8C577c453802FF1AcE9", LEAD_VIEWS),
 "HUNT PASS": ("0x885128Cf234c768F1353e2C1432D55873C6b67dD", NFT_VIEWS),
 "King's Game": ("0x9eA27f3F0919DaF6a4401CFd09563162d395061D", NFT_VIEWS),
 "Paw Gang": ("0x587C303982187Ec578dF309d27670327b13202F8", NFT_VIEWS),
 "fab7dd20-variant": ("0xfab7dd20e8816e10227C1222bd4Bd446FecF1B72",
    ["totalSupply()", "freeMinted()", "FREE_SHARES()", "freeClaimed(address)", "balanceOf(address)", "startTime()"]),
}
def read_item(args):
    name, (addr, views) = args
    d = {"address": addr}
    for sig in views:
        key = sig.split("(")[0]
        if sig.startswith("quote("):
            v = call(addr, sig, enc(USER) + enc_uint(1)); key += "_user1"
        elif "address" in sig:
            v = call(addr, sig, enc(USER)); key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    snap_v = snap.get("contracts", {}).get(name, {}) or snap.get("track_c", {}).get(name, {})
    d["snap"] = {k: snap_v.get(k) for k in ("freeClaimed", "FREE_SUPPLY", "freeSupply", "totalSupply", "status", "freeMinted", "totalMinted") if snap_v.get(k) is not None}
    return name, d
DEADLINE = time.time() + 120
# PRIORITY: Tri333 25% threshold watch (was 552/2222 = 24.8% at 22:19, needs 556).
# Read FIRST, sequentially, so its threshold status is determined even if bulk leg4 hits the deadline.
TRI = "0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f"
tri_prio = {}
if blk is not None:
    tri_prio = {
        "freeClaimed": call(TRI, "freeClaimed()"),
        "freeMinted": call(TRI, "freeMinted()"),
        "FREE_CAP": call(TRI, "FREE_CAP()"),
        "totalSupply": call(TRI, "totalSupply()"),
        "freeCount_user": call(TRI, "freeCount(address)", enc(USER)),
        "balanceOf_user": call(TRI, "balanceOf(address)", enc(USER)),
        "mintOpen": call(TRI, "mintOpen()"),
    }
    fc = tri_prio.get("freeClaimed")
    cap = tri_prio.get("FREE_CAP")
    if isinstance(fc, int) and isinstance(cap, int) and cap:
        tri_prio["pct"] = round(fc / cap * 100, 2)
        tri_prio["threshold_25pct_crossed"] = fc >= 556
out["leg4_priority_tri333"] = tri_prio
if blk is None:
    out["leg4_reread"] = {"block": None, "status": "SKIPPED - RPC unreachable; no sellout/slot-loss/promotion/change conclusion drawn. Retry next run.", "items_attempted": len(ITEMS)}
else:
    with ThreadPoolExecutor(max_workers=20) as ex:
        leg4 = dict(ex.map(read_item, list(ITEMS.items())))
    out["leg4_reread"] = {"block": int(blk, 16), "via": blk_rpc, "items": leg4}
    # cfe5 (new S1 from 2219, watchlist-only) growth check
    out["cfe5_watch"] = {
        "totalSupply": call("0xcfE5E4925A76A3AA11aFA79e04c6fad3611cee40", "totalSupply()"),
        "freeMinted": call("0xcfE5E4925A76A3AA11aFA79e04c6fad3611cee40", "freeMinted()"),
        "balanceOf_user": call("0xcfE5E4925A76A3AA11aFA79e04c6fad3611cee40", "balanceOf(address)", enc(USER)),
    }

# ---------- Pending claims ----------
out["pending_claims"] = snap.get("pending_claims") or "snapshot pending_claims empty at run start - nothing to re-read"

# ---------- Bridge leg (read-only) ----------
import os
bridge = json.load(open(f"{BASE}/scan-bridge.json"))
bcontracts = bridge.get("contracts", {})
discarded = [a for a, v in bcontracts.items() if v.get("same_owner_discarded")]
in_snap = [a for a in bcontracts if a.lower() in snap_addr_set]
not_in_snap = [a for a in bcontracts if a.lower() not in snap_addr_set]
snap_text = json.dumps(snap).lower()
in_snap_text = [a for a in not_in_snap if a.lower() in snap_text]
mtime = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(os.path.getmtime(f"{BASE}/scan-bridge.json")))
out["bridge_leg"] = {"total": len(bcontracts), "same_owner_discarded": len(discarded),
                     "in_snapshot_addr": len(in_snap), "not_in_snapshot_addr": len(not_in_snap),
                     "not_in_addr_but_in_snapshot_text": len(in_snap_text), "mtime": mtime,
                     "note": "Bridge is read-only for this job; promotions only if a bridge contract already in snapshot newly meets a tier or changes state."}
out["duration_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
print(json.dumps({"leg1_new": new_addrs, "leg1_shapes": shapes, "leg2": out["leg2_boltbook"],
                  "rpc_probe": out["rpc_probe"], "leg3_verify": out.get("leg3_verify"),
                  "leg4_priority_tri333": out.get("leg4_priority_tri333"),
                  "leg4_block": out["leg4_reread"].get("block"),
                  "leg4_status": out["leg4_reread"].get("status", "ok"),
                  "cfe5_watch": out.get("cfe5_watch"),
                  "bridge": out["bridge_leg"], "pending_claims": out["pending_claims"],
                  "duration_s": out["duration_s"]}, indent=1, default=str))
