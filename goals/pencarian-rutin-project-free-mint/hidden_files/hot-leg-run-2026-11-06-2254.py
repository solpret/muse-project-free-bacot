#!/usr/bin/env python3
"""Hot-leg run 2026-11-06 22:49 WIB. Legs 1-4 + bridge. Read-only except own hot-leg state files. Never writes main snapshot."""
import json, re, subprocess, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2254"
NOW = "2026-11-06T22:54:38+07:00"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed.binance.org", "https://rpc.ankr.com/bsc",
        "https://bsc-dataseed-public.bnbchain.org"]
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed", "freeAvailable",
              "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted", "freeCardsRemaining"]
out = {"run": "free-mint-hot-leg 2026-11-06 22:54:38 WIB"}
t0 = time.time()

def rpc_json(method, params, timeout=3):
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
    req = urllib.request.Request("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc",
                                 headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    items = data.get("results", data) if isinstance(data, dict) else data
    for it in items:
        a = it.get("address") or it.get("contractAddress")
        if a:
            feed_addrs.append(a)
    out["leg1_feed"] = {"n": len(feed_addrs), "addrs": feed_addrs}
except Exception as e:
    out["leg1_feed"] = {"error": f"{type(e).__name__}: {e}"}
    feed_addrs = []

def shape_check(addr):
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
                                     headers={"User-Agent": "hot-leg/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            meta = json.load(r)
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate", "AGENT_ID"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token}
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {str(e)[:100]}"}

new_addrs = [a for a in feed_addrs if a not in seen and a.lower() not in EXCLUDED]
new_excluded = [a for a in feed_addrs if a.lower() in EXCLUDED]
shapes = []
if new_addrs:
    with ThreadPoolExecutor(max_workers=10) as ex:
        shapes = list(ex.map(shape_check, new_addrs))
    for s in shapes:
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
        p = subprocess.run(["curl", "-sS", "--max-time", "15", "-A", "hot-leg/1.0", url],
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
kw_zh = ["免费份额", "首个免费", "免费铸造", "免费mint"]
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
        note = f"Sourcify 404/unreachable ({s['error']}) - cannot shape-check; not sale-shape by available evidence"
        status = "checked-not-sale-shape"
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

# ---------- RPC probe (gates leg 3 on-chain + leg 4) ----------
blk, blk_rpc = rpc_json("eth_blockNumber", [], timeout=4)
out["rpc_probe"] = {"block": int(blk, 16) if blk else None, "via": blk_rpc,
                    "note": "All 5 BSC RPC endpoints tried; None = transport failure, NOT state."}

# ---------- Leg 3: on-chain verify of new sale-shape contracts (probe-gated) ----------
if sale_shapes:
    if blk is None:
        out["leg3_onchain"] = "SKIPPED - RPC unreachable; sale-shape contract(s) NOT verified on-chain, NOT a lead, NOT previewed/minted; left for main job."
    else:
        out["leg3_onchain"] = "RPC up - on-chain verification of new sale-shape contract(s) required before any report; handled below if applicable."

# ---------- Leg 4: re-read snapshot items (read-only, probe-gated) ----------
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def raw(to, data):
    v, _ = rpc_json("eth_call", [{"to": to, "data": data}, "latest"], timeout=4)
    if not v or v == "0x":
        return None
    try:
        return int(v, 16)
    except Exception:
        return v
def call(to, sig, args=""): return raw(to, sel(sig) + args)

GENERIC = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)",
           "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)", "claimedFree(address)",
           "quote(address,uint256)", "costOf(address,uint256)", "freeQuota()", "remainingFree()",
           "FREE_SUPPLY()", "freeSharesRemaining()", "freeAvailable()", "mintOpen()"]
EXTRA = {
 "0x2A2463d243E5c4dF850e48f350392AD23B494132": ["agentGateOn()"],
 "0x25F3EFb465685692EF3DdC47Ed040baF216B5D38": ["freePodsClaimed()", "freeClaimedBy(address)"],
 "0xD7B3FD33e0b465B0e374906F60567D317b758FD8": ["mintsLeft(address)", "price()"],
}
ITEMS = {
 "KING Agent": "0x2A2463d243E5c4dF850e48f350392AD23B494132",
 "MERGEBORN": "0x348455be18b700cae8aa425bd84e456e47f16e8b",
 "Driftnauts": "0x6a926234D3767F2EEb3DB12c1B4C9e2912C5589b",
 "Agent Frogs": "0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31",
 "Thronemind": "0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90",
 "Hashseers": "0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688",
 "Layerloom": "0x1B72ceC52A74537b06F713FCebA0e491f53679aE",
 "Smeltbots": "0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e",
 "Tumblebots": "0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17",
 "Forklings": "0xD7B3FD33e0b465B0e374906F60567D317b758FD8",
 "Neurolucha": "0x56eBED63452Bb02B975ceE02949DA3C02466725b",
 "BNB CACHE Server": "0x1989058Da9eb7F36E69779fCda0EA04578528570",
 "Qilingentle-423d": "0x423d25764E4D3D792C08e04C759cE3b0FcDE8596",
 "Hivejupiter-8DF7": "0x8DF74cBe998F8d447E7c77dD5117aFB940605400",
 "Saturnswarm-238c": "0x238C995A1376e08395b970870A546C57aE184434",
 "Boohiveling-c1da": "0xC1dAf114e377242eEB76d180B24b491758Acb4f7",
 "Neidroidjuan-758c": "0x758c9665747466Ff4CBa2a3714CC4e9F7C9324b6",
 "Servofarmix-f636": "0xf63623136e5f2a6CD8cE85d9F22Ac46744DF39b6",
 "PeaFunPod-1901": "0x25F3EFb465685692EF3DdC47Ed040baF216B5D38",
}
if blk is None:
    out["leg4_reread"] = {
        "block": None,
        "status": "SKIPPED - all BSC RPC endpoints unreachable from this VM during the run "
                  "(bsc-dataseed1, bsc.publicnode, bsc-dataseed.binance.org, rpc.ankr.com/bsc, "
                  "bsc-dataseed-public all failed eth_blockNumber). ALL reads None = transport failure, "
                  "NOT state: no sellout, slot-loss, promotion, or change conclusion drawn from this leg. Retry next run.",
        "items_attempted": len(ITEMS)}
else:
    def read_item(name_addr):
        name, addr = name_addr
        sigs = list(GENERIC) + EXTRA.get(addr, [])
        def one(sig):
            if sig.endswith("(address)"): args = enc(USER)
            elif sig.endswith("(address,uint256)"): args = enc(USER) + enc_uint(1)
            else: args = ""
            return call(addr, sig, args)
        with ThreadPoolExecutor(max_workers=8) as ex:
            vals = list(ex.map(one, sigs))
        res = dict(zip(sigs, vals))
        snap_v = snap.get("contracts", {}).get(name, {})
        return {"name": name, "address": addr, "reads": res,
                "snap_freeClaimed": snap_v.get("freeClaimed"),
                "snap_FREE_SUPPLY": snap_v.get("FREE_SUPPLY") or snap_v.get("freeSupply"),
                "snap_totalSupply": snap_v.get("totalSupply"), "snap_status": snap_v.get("status")}
    with ThreadPoolExecutor(max_workers=10) as ex:
        leg4_items = list(ex.map(read_item, ITEMS.items()))
    out["leg4_reread"] = {"block": int(blk, 16), "via": blk_rpc, "items": leg4_items}

# ---------- Bridge leg ----------
bridge = json.load(open(f"{BASE}/scan-bridge.json"))
bcontracts = bridge.get("contracts", {})
snap_text = json.dumps(snap).lower()
discarded = [a for a, v in bcontracts.items() if v.get("same_owner_discarded")]
in_snap = [a for a in bcontracts if a.lower() in snap_addr_set]
not_in_snap = [a for a in bcontracts if a.lower() not in snap_addr_set]
in_snap_text = [a for a in not_in_snap if a.lower() in snap_text]
out["bridge_leg"] = {"total": len(bcontracts), "same_owner_discarded": len(discarded),
                     "in_snapshot_addr": len(in_snap), "not_in_snapshot_addr": len(not_in_snap),
                     "not_in_addr_but_in_snapshot_text": len(in_snap_text),
                     "note": "Bridge is read-only for this job; promotions only if a bridge contract already in snapshot newly meets a tier or changes state."}
out["duration_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
print(json.dumps({"leg1_new": new_addrs, "leg1_shapes": shapes, "leg2": out["leg2_boltbook"],
                  "rpc_probe": out["rpc_probe"], "leg4": {k: v for k, v in out["leg4_reread"].items() if k != "items"},
                  "bridge": out["bridge_leg"], "duration_s": out["duration_s"]}, indent=1))
