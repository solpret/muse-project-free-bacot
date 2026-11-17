#!/usr/bin/env python3
"""Hot-leg run 2026-11-07 02:44 WIB. Legs 1-4 + bridge. Read-only except own hot-leg state files. Never writes main snapshot."""
import json, re, subprocess, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-0244"
NOW = "2026-11-07T02:44:38+07:00"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed.binance.org", "https://rpc.ankr.com/bsc",
        "https://bsc-dataseed-public.bnbchain.org"]
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed", "freeAvailable",
              "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted", "freeCardsRemaining"]
out = {"run": "free-mint-hot-leg 2026-11-07 02:34:38 WIB"}
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
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate", "AGENT_ID"})
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
new_addrs = [a for a in feed_addrs if a not in seen and a.lower() not in EXCLUDED]
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

# ---------- Leg 3 ----------
if sale_shapes:
    if blk is None:
        out["leg3_onchain"] = "SKIPPED - RPC unreachable; sale-shape contract(s) NOT verified on-chain, NOT a lead, NOT previewed/minted; left for main job."
    else:
        out["leg3_onchain"] = "RPC up - on-chain verification of new sale-shape contract(s) required before any report; handled below if applicable."

# ---------- Leg 4: targeted re-read (read-only, 90s deadline) ----------
DEADLINE = time.time() + 90
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def raw(to, data):
    for rpc in RPCS:
        if time.time() > DEADLINE:
            return "deadline"
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r:
                o = json.load(r)
            if "error" in o:
                continue
            v = o.get("result")
            if not v or v == "0x":
                return None
            try:
                return int(v, 16)
            except Exception:
                return v
        except Exception:
            continue
    return None
def call(to, sig, args=""): return raw(to, sel(sig) + args)

NFT_VIEWS = ["totalSupply()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
             "balanceOf(address)", "mintedBy(address)", "freeUsed(address)",
             "claimedFree(address)", "mintOpen()"]
SALE_VIEWS = ["freeClaimed()", "freeSharesRemaining()", "freeLeft(address)",
              "quote(address,uint256)", "mintedBy(address)", "mintOpen()",
              "totalMinted()", "freeMinted()", "totalSupply()"]
ITEMS = {
 "KING Agent": ("0x2A2463d243E5c4dF850e48f350392AD23B494132", NFT_VIEWS),
 "MERGEBORN": ("0x348455be18b700cae8aa425bd84e456e47f16e8b", NFT_VIEWS),
 "Agent Frogs": ("0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31", NFT_VIEWS),
 "Thronemind": ("0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90", NFT_VIEWS),
 "Hashseers": ("0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688", NFT_VIEWS),
 "Layerloom": ("0x1B72ceC52A74537b06F713FCebA0e491f53679aE", NFT_VIEWS),
 "Smeltbots": ("0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e", NFT_VIEWS),
 "Tumblebots": ("0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17", NFT_VIEWS),
 "Forklings": ("0xD7B3FD33e0b465B0e374906F60567D317b758FD8", NFT_VIEWS),
 "Neurolucha": ("0x56eBED63452Bb02B975ceE02949DA3C02466725b", NFT_VIEWS),
 "Driftnauts": ("0x6a926234D3767F2EEb3DB12c1B4C9e2912C5589b", NFT_VIEWS),
 "BNB CACHE Server": ("0x1989058Da9eb7F36E69779fCda0EA04578528570", NFT_VIEWS),
 "Qilingentle-423d": ("0x423d25764E4D3D792C08e04C759cE3b0FcDE8596", NFT_VIEWS),
 "Hivejupiter-8DF7": ("0x8DF74cBe998F8d447E7c77dD5117aFB940605400", NFT_VIEWS),
 "Saturnswarm-238c": ("0x238C995A1376e08395b970870A546C57aE184434", NFT_VIEWS),
 "Boohiveling-c1da": ("0xC1dAf114e377242eEB76d180B24b491758Acb4f7", NFT_VIEWS),
 "Neidroidjuan-758c": ("0x758c9665747466Ff4CBa2a3714CC4e9F7C9324b6", NFT_VIEWS),
 "Servofarmix-f636": ("0xf63623136e5f2a6CD8cE85d9F22Ac46744DF39b6", NFT_VIEWS),
 "PeaFunPod-1901": ("0x25F3EFb465685692EF3DdC47Ed040baF216B5D38", NFT_VIEWS),
 "DeY": ("0xDB062c12bF0a14227e7Fe896a988950b050B51C1", SALE_VIEWS),
 "FANBEIMAO-824d": ("0x824d1e5c1395ed7543854fCd9e4da6D3F358De16", SALE_VIEWS),
 "LuckyBox-LUCK": ("0xd08ef372B52C29255fEd7004f59bF41571451894", SALE_VIEWS),
 "NJAR": ("0x816458b734d17d59058762deaadd9b952bad6985", SALE_VIEWS),
 "Predictagent-PRDICT": ("0x8fF4bd65584882324c44Ee794a23E7791820189b", SALE_VIEWS),
 "CLEPSYDRA": ("0x9e2738B3DD3773c6c71cA24Fbc92660B501C0B6b", SALE_VIEWS),
 "BOMB-sale": ("0xC3f847430D660e5AAbE8D4b2B5792d6Fcbb171F9", SALE_VIEWS),
 "ChimpAgent": ("0x57D41Ff4895A19f518a0Ec3A2Fa56284a85f5689", SALE_VIEWS),
 "ONLYAI-Crystals": ("0x156482ad3f0eebd8e3f70d494ebd1da3f738f5ba", NFT_VIEWS),
 "Sage Trials": ("0xB0d58925E1075c4E4C02B72f4Bbb3656A6f0b3A3", NFT_VIEWS),
 "EARLY LEAD HUNT PASS": ("0x885128Cf234c768F1353e2C1432D55873C6b67dD", NFT_VIEWS),
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
if blk is None:
    out["leg4_reread"] = {"block": None, "status": "SKIPPED - RPC unreachable; no sellout/slot-loss/promotion/change conclusion drawn. Retry next run.", "items_attempted": len(ITEMS)}
else:
    with ThreadPoolExecutor(max_workers=10) as ex:
        leg4 = dict(ex.map(read_item, list(ITEMS.items())))
    out["leg4_reread"] = {"block": int(blk, 16), "via": blk_rpc, "items": leg4}

# ---------- Bridge leg ----------
bridge = json.load(open(f"{BASE}/scan-bridge.json"))
bcontracts = bridge.get("contracts", {})
discarded = [a for a, v in bcontracts.items() if v.get("same_owner_discarded")]
in_snap = [a for a in bcontracts if a.lower() in snap_addr_set]
not_in_snap = [a for a in bcontracts if a.lower() not in snap_addr_set]
snap_text = json.dumps(snap).lower()
in_snap_text = [a for a in not_in_snap if a.lower() in snap_text]
out["bridge_leg"] = {"total": len(bcontracts), "same_owner_discarded": len(discarded),
                     "in_snapshot_addr": len(in_snap), "not_in_snapshot_addr": len(not_in_snap),
                     "not_in_addr_but_in_snapshot_text": len(in_snap_text),
                     "note": "Bridge is read-only for this job; promotions only if a bridge contract already in snapshot newly meets a tier or changes state."}
out["duration_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
print(json.dumps({"leg1_new": new_addrs, "leg1_shapes": shapes, "leg2": out["leg2_boltbook"],
                  "rpc_probe": out["rpc_probe"], "leg4_block": out["leg4_reread"].get("block"),
                  "leg4_status": out["leg4_reread"].get("status", "ok"),
                  "bridge": out["bridge_leg"], "duration_s": out["duration_s"]}, indent=1))
