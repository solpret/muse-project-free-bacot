#!/usr/bin/env python3
"""free-mint-hot-leg run 2026-11-10 04:04 WIB (scheduled 04:04:38 WIB).
Leg 1: Sourcify feed (20 contracts, browser-fetched, crawled 03:42 WIB;
  curl feed timed out 8s this run). Leg 2: Boltbook EN+ZH via browser fetch
  (crawled 03:48/03:49 WIB; curl to boltbook.fun timed out 0 bytes).
  Front-page addresses extracted from the browser text; full-post addresses
  for ADVAGENT/VISION/Cuprihive/WNO/HACKED/YAMA/PXMON/BDPASS/ONLYAI were
  truncated in the excerpt and NOT recovered this run (gap for next run).
Leg 3: on-chain verify for any new sale-shape (pool/slot; age via first-mint
  corroboration only - getLogs dead, so age-unverified -> watchlist-only).
Leg 4: re-read 48-item set vs 03:04 baseline (nodereal RPC, batched eth_call).
Bridge leg: read-only scan-bridge.json cross-check vs snapshot + promo flags.
Priority queue: Roguefall (new Boltbook lead) first, then feed #6-#13 new,
  then feed #14-#20 abi-unavailable retries, then 03:29 shape timeouts
  (cap leg-1 shape loop at 75s elapsed; leftovers carry to next run).
Writes only own run JSON + hot-leg-seen.json. No preview/mint unless a
  sale-shape passes ALL guards - none expected; any sale-shape found is
  watchlist-only pending age/site."""
import json, re, subprocess, time
from datetime import datetime, timedelta, timezone
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
T0 = time.time()
NOW_WIB = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
RUN = "free-mint-hot-leg 2026-11-10 04:04 WIB (scheduled 04:04:38 WIB)"
log = {"run": RUN, "run_wib": NOW_WIB}

def elapsed(): return round(time.time() - T0, 1)

def curl(url, timeout=10, data=None):
    cmd = ["curl", "-sS", "--max-time", str(timeout), url]
    if data is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "--data", data]
    p = subprocess.run(cmd, capture_output=True, timeout=timeout + 5)
    return p.stdout

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedTotal"]
MINT_FNS = ["mint", "mintFree", "claimFree", "claim"]
QUOTE_FNS = ["quote", "cost", "PRICE", "price"]
AGENT_MARKERS = ["agentRegistry", "registry", "AGENT_ID", "AgentGate",
                 "agentGate", "isAgent", "hasAgentId", "agentIdRequired"]
TOKEN_FNS = ["name", "symbol", "decimals", "totalSupply"]

def find_abi(obj):
    if isinstance(obj, list) and obj and all(
            isinstance(x, dict) and x.get("type") in ("function", "event", "constructor", "error")
            for x in obj if isinstance(x, dict)):
        return obj
    if isinstance(obj, dict):
        for v in obj.values():
            a = find_abi(v)
            if a is not None:
                return a
    if isinstance(obj, list):
        for v in obj:
            a = find_abi(v)
            if a is not None:
                return a
    return None

def code_has_registry(addr, rpc):
    try:
        payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [addr, "latest"]})
        raw = curl(rpc, timeout=8, data=payload)
        code = json.loads(raw).get("result", "")
        return REGISTRY[2:].lower() in (code or "").lower()
    except Exception:
        return None

def shape_check(addr, rpc):
    abi = None; err = None
    try:
        raw = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", 6)
        abi = find_abi(json.loads(raw))
        if abi is None:
            err = "v2-no-abi"
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
    names = set(); fns = []
    if abi:
        for fn in abi:
            if isinstance(fn, dict) and fn.get("type") == "function":
                names.add(fn.get("name", "")); fns.append(fn.get("name", ""))
    code_reg = None
    if not abi and rpc:
        code_reg = code_has_registry(addr, rpc)
    has_mint = bool(names & set(MINT_FNS))
    has_quote = bool(names & set(QUOTE_FNS))
    free_found = [f for f in FREE_VIEWS if f in names]
    has_agent = any(m.lower() in n.lower() for n in names for m in AGENT_MARKERS) or code_reg is True
    is_token = bool(names & set(TOKEN_FNS))
    s1 = has_mint and has_quote and bool(free_found) and has_agent
    s2 = is_token and ("mintFree" in names) \
        and (("freeClaimed" in names or "freeMinted" in names) or bool(free_found)) \
        and any(x in names for x in ["FREE_SLOTS", "FREE_SUPPLY"]) and has_agent
    return {"address": addr, "S1": bool(s1), "S2": bool(s2), "mint": bool(has_mint),
            "quote": bool(has_quote), "free": free_found, "agent": bool(has_agent),
            "token": bool(is_token), "abi_err": err, "code_registry": code_reg,
            "fns": sorted(fns)}

seen = json.load(open(BASE + "hot-leg-seen.json"))
reported = json.load(open(BASE + "hot-leg-reported.json"))
snap = json.load(open(BASE + "onchain-snapshot.json"))
bridge = json.load(open(BASE + "scan-bridge.json"))
discards = json.load(open(BASE + "same-owner-discards.json"))
log["seen_total_start"] = len(seen)

# --- Leg 1: feed (browser-fetched, crawled 03:42 WIB; curl feed timed out) ---
FEED_FALLBACK = [
    ("0xC076aD3F73c4E9C03055c0784e531448cc686f92", "2026-11-09T20:40:48Z"),
    ("0x26D126FDfb87E709490c45DF961342d0D74F79c6", "2026-11-09T20:40:46Z"),
    ("0xc713f600321bf76cb0364828403a7a27991366EA", "2026-11-09T20:40:42Z"),
    ("0x336ABDa83B385e1B9C75855810cB6769561F5533", "2026-11-09T20:39:30Z"),
    ("0x107723eF8451F363b5F8F2A5550c7a8AcF92FED1", "2026-11-09T20:39:26Z"),
    ("0x7BBE6b713D8CD6851338fe3987015DC93E1a190C", "2026-11-09T20:29:40Z"),
    ("0x5d918dCD6eA84a4e058869813A433780c333dc40", "2026-11-09T20:29:02Z"),
    ("0x1F8a0184939D4EE3DFbbBc30Aa0cAa1a8e97E160", "2026-11-09T20:27:13Z"),
    ("0x8B791769F6fda3f184638f9F4A2217572714F3b7", "2026-11-09T20:18:08Z"),
    ("0x284c81624945F1f0fC3D92F1CA5D88012132441F", "2026-11-09T20:18:00Z"),
    ("0x3849159784aa47Fe76117103904204D9f5D153E7", "2026-11-09T20:17:53Z"),
    ("0xc6D4ec8CB889aFBa9f251606001457644E260f7D", "2026-11-09T20:17:28Z"),
    ("0xe53Ef05e15784Be3479aA46890C204da0Ce34DE9", "2026-11-09T20:17:22Z"),
    ("0x0c264628BaE45a1E4753F771661E78542aE67584", "2026-11-09T20:14:38Z"),
    ("0xa0738f6f1449b41AD232Fb4FDDa9380949672BeA", "2026-11-09T20:14:36Z"),
    ("0x80c5d63aDF7C78C4D891A1c6D55FB3d83114F6ea", "2026-11-09T20:14:26Z"),
    ("0x7eD5Ff47A4C3a94D9b8B61B4c6aD488edaa6d384", "2026-11-09T20:14:05Z"),
    ("0x085b3e9C8416B686e9Af19a05EDe90CeEcd30AE4", "2026-11-09T20:14:05Z"),
    ("0x3a0EDDC21AbFf1C735A1e2472c04eDc9ec9ba6EA", "2026-11-09T20:14:02Z"),
    ("0xce4A9CC83A09Ec4474e261698535E9BA1BD7F1fC", "2026-11-09T20:13:06Z"),
]
feed_addrs = [a for a, _ in FEED_FALLBACK]
feed_ok = False
try:
    raw = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 12)
    j = json.loads(raw)
    fresh = [r["address"] for r in j.get("results", [])]
    if len(fresh) >= 10:
        feed_addrs = fresh
        feed_ok = True
        log["leg1_feed"] = {"n": len(fresh), "source": "curl-fresh",
                            "verifiedAt_range": f"{j['results'][-1]['verifiedAt']}..{j['results'][0]['verifiedAt']}"}
    else:
        log["leg1_feed"] = {"n": len(feed_addrs), "source": "browser-fallback-crawled-0342",
                            "error": "curl feed <10 results"}
except Exception as e:
    log["leg1_feed"] = {"n": len(feed_addrs), "source": "browser-fallback-crawled-0342",
                        "error": f"curl feed failed: {type(e).__name__}: {e}"}

RPCS = ["https://bsc.nodereal.io/", "https://bsc-dataseed1.bnbchain.org",
        "https://bsc-dataseed.bnbchain.org", "https://bsc-rpc.publicnode.com",
        "https://rpc.ankr.com/bsc"]
rpc_working = None
for ep in RPCS:
    try:
        raw = curl(ep, timeout=8, data='{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}')
        blk = json.loads(raw).get("result")
        if blk:
            rpc_working = ep
            log["rpc"] = {"endpoint": ep, "block": int(blk, 16)}
            break
    except Exception:
        continue
if not rpc_working:
    log["rpc"] = {"endpoint": None, "error": "all 5 RPC endpoints failed eth_blockNumber (8s each)"}

# --- shape-check queue (priority order) ---
TIMEOUTS_0329 = ["0xE4F26812f2eF6C0a7d27C0Fa97f75266b9e6430C",
                 "0x149f4191d4d2e12051FE7db40B060B6b930870e5",
                 "0x17851B15052FF88232e3773253875481cfA9cB0f",
                 "0xE1Ee6D8A5b5A8f9C59167DBb2d82e719C4a5e6eA",
                 "0x35864d3103eF0767e5cCc163bFe6C0da2811c828",
                 "0x36DB4d5214bc960D5495b085953eacdE5983C083",
                 "0x3d89FfdbBC676bA33B01f02449759ABd11b946eA",
                 "0xE6c8dAc5B15005926d5891F96E89C14ec143232A",
                 "0x2B18E242834E59512aca1E931438FA1685F3C5A2",
                 "0x974ff9dc210798e60d2430CCb6069DF3a66ae398",
                 "0xCf60fE48669B2D5ab7A60fD8C5F02104d7f4Ac16",
                 "0x1407c5E72dB514e50B9D162eF9Efff83Ba5E5348",
                 "0x48E4374f15CAc92A518E3E3D30B13dE0BC1cEA75",
                 "0xc4fC3150945875502cA2183bDE277813eEc8F096",
                 "0x651B49f4C14dAAf270274a6C682f0d65F27eF6CD",
                 "0x2403ba50cc25dc4A8Ff9D518452A33C8205836eA",
                 "0x95972735b5Ab59Cb5E82f057958A36E8BB9940Ef",
                 "0x404056Ab781D713B8f5Dc55F5B9592962B187099",
                 "0x34D8A2debE49DCCa0f7cC77d74163cFB94Cc19F5",
                 "0xB3f66517bEC4cC5A8E799dB2dDA4C810BefCc917",
                 "0xDBAD9E797157F76B2122c69C01BAC47541A3e62C",
                 "0x2E8B7e47424876B29fa2276025dE03F812813b03",
                 "0x7635Ef16370ef490298649A188c9205D1d7FDA67"]
BOLTBOOK_NEW = ["0x5fe03829a2f94a8ba3906459258b1305f0e68934"]  # Roguefall RFALL, post ~03:40 WIB

def seen_status(addr):
    e = seen.get(addr) or seen.get(addr.lower())
    if isinstance(e, dict):
        return e.get("status", ""), e.get("note", "")
    return ("", "")

def snap_lookup(addr):
    al = addr.lower()
    for sec in ("contracts", "track_c", "pending_claims"):
        for k, v in snap.get(sec, {}).items():
            if isinstance(k, str) and k.lower() == al:
                return f"{sec}/{k}"
            if isinstance(v, dict):
                for f in ("address", "sale", "token"):
                    if isinstance(v.get(f), str) and v[f].lower() == al:
                        return f"{sec}/{k} via {f}"
    return None

queue = []
for a in BOLTBOOK_NEW:
    queue.append((a, "boltbook-new"))
for a in feed_addrs:
    if a.lower() == REGISTRY.lower():
        continue
    if a.lower() in EXCLUDED:
        queue.append((a, "excluded"))
        continue
    st, note = seen_status(a)
    if st in ("checked-not-sale-shape", "checked-not-track-c") and "<redacted>" not in note:
        continue
    queue.append((a, "feed-new-or-retry"))
for a in TIMEOUTS_0329:
    st, note = seen_status(a)
    if st in ("checked-not-sale-shape", "checked-not-track-c") and "<redacted>" not in note:
        continue
    queue.append((a, "retry-0329-timeout"))

log["leg1"] = {"feed_n": len(feed_addrs), "feed_fresh_curl": feed_ok,
               "shape_queue": [f"{a}({why})" for a, why in queue],
               "excluded_in_feed": [a for a in feed_addrs if a.lower() in EXCLUDED]}

shapes = []
sale_shapes = []
for addr, why in queue:
    if elapsed() > 75:
        log.setdefault("shape_timeouts", []).append(addr)
        continue
    if why == "excluded":
        seen[addr] = {"first_seen_wib": NOW_WIB, "note": "Excluded example rediscovered in feed - recorded, NOT reported.",
                      "source": "sourcify-feed", "status": "excluded"}
        shapes.append({"address": addr, "status": "excluded"})
        continue
    s = shape_check(addr, rpc_working)
    shapes.append(s)
    if s.get("abi_err") and not s.get("fns"):
        status = "checked-abi-unavailable"
        note = (f"S1={s['S1']} S2={s['S2']} mint={s['mint']} quote={s['quote']} free={s['free']} "
                f"agent={s['agent']} token={s['token']} abi_err={s['abi_err']} code_registry={s['code_registry']} "
                f"(ABI unreachable this run - shape UNVERIFIED, not a lead, never previewed/minted)")
    else:
        is_nft = bool(set(s.get("fns", [])) & {"ownerOf", "tokenURI"})
        note = (f"S1={s['S1']} S2={s['S2']} mint={s['mint']} quote={s['quote']} free={s['free']} "
                f"agent={s['agent']} token={s['token']} fns={len(s.get('fns', []))}")
        if (s["S1"] or s["S2"]) and is_nft:
            status = "checked-not-track-c"
            note += " (ERC-721 NFT: S1 literal pass, not a fungible share sale; NFT early-lead stays with main job)"
        elif s["S1"] or s["S2"]:
            status = "sale-shape"
            sale_shapes.append(s)
        else:
            status = "checked-not-sale-shape"
    prev = seen.get(addr) or seen.get(addr.lower()) or {}
    first = prev.get("first_seen_wib") if isinstance(prev, dict) and prev.get("first_seen_wib") else NOW_WIB
    seen[addr] = {"first_seen_wib": first,
                  "note": (f"[{why}] " if why in ("retry-0329-timeout", "feed-new-or-retry") else "") + note,
                  "source": "boltbook-frontpage" if why == "boltbook-new" else "sourcify-feed",
                  "status": status}
    print(addr, status, flush=True)
log["leg1_shapes"] = shapes
log["leg1_sale_shapes"] = sale_shapes

# --- Leg 2: Boltbook EN+ZH (browser-fetched; curl timed out 0 bytes) ---
BOLTBOOK_ADDRS = {
    "0x2728c134D79D34A977d6D35D8A3014AbB5C97ed4": "HOPKIN Genesis, 4,429/10,000 (post ~03:44 WIB)",
    "0xf4bacf30fb8f69373f63d99c657f53dd7774af1d": "ACORE, 811/2,000, mintOpen true (post 'Three live free lanes')",
    "0x728095ab0bd71636db5da4e2a6d7f5cc73729fc0": "MALTA token (already minted 2026-11-09)",
    "0xc205f8c74733d914776d66cbc4cf10bf701d96aa": "Bubblebruin BBRUIN, 2,356/7,777 (in snapshot)",
    "0x5fe03829a2f94a8ba3906459258b1305f0e68934": "Roguefall RFALL, 529/4,000, freeMint() sims clean (post ~03:40 WIB)",
    "0x7020368e5421008b92C16798589ac6d91812307e": "COSO v2 sale, freeMinted 593/1,000, 407 left",
    "0x57cc350b844484eac0de444526d295c90f9ccbb5": "BAHUANG2, 0 free (10.4%) recheck 03:42 (in snapshot)",
    "0xacc6e2f1aae42b2e5ff2758ff078e4b1bfac7db1": "Aura Agents AURA (in snapshot)",
    "0xf2705a84602369069782624279837a08bdbbf6d6": "Sakura, 895/6,992 free 12.8% (in snapshot, early lead reported 03:25 by main job)",
    "0xa069401266707e1318bdff45b3f1f61e52d1ae48": "Brinedroid BRNDR, freeClaimed 1,228/2,222 - SAME-OWNER-DISCARDED, never promote/report",
}
bb = {"en_crawled": "2026-11-09 20:48 UTC (03:48 WIB)", "zh_crawled": "2026-11-09 20:49 UTC (03:49 WIB)",
      "curl": "FAILED - timeout 8s, 0 bytes (both EN+ZH); read via browser fetch instead",
      "addrs": {}, "unrecovered_post_addrs": ["ADVAGENT (gated, post 'Three live free lanes')",
      "VISION (shares, same post)", "Cuprihive + WNO (post 'Wilds')", "HACKED (post ~03:47 WIB)",
      "YAMA / PXMON / BDPASS / 4Agent (post 'YAMA narik balik')", "ONLYAI (post 2,065 +52)"],
      "note": "Full-post addresses truncated in front-page excerpt; not recovered this run - gap for next run/main job."}
for a, desc in BOLTBOOK_ADDRS.items():
    st, _ = seen_status(a)
    sl = snap_lookup(a)
    bb["addrs"][a] = {"desc": desc, "hotleg_seen_status": st or "(not in hot-leg seen)",
                      "in_snapshot": sl}
log["leg2_boltbook"] = bb

# --- Leg 3: sale-shape verification ---
log["leg3_new_sale_shapes"] = sale_shapes
if not sale_shapes:
    log["leg3_verify"] = "None - no new sale-shape contract"
else:
    disc_addrs = set()
    d = discards if isinstance(discards, dict) else {}
    for k, v in d.items():
        if isinstance(k, str) and k.startswith("0x"):
            disc_addrs.add(k.lower())
        if isinstance(v, dict):
            for f in ("address", "contract"):
                if isinstance(v.get(f), str):
                    disc_addrs.add(v[f].lower())
    def sel(sig):
        k = keccak.new(digest_bits=256); k.update(sig.encode())
        return "0x" + k.hexdigest()[:8]
    def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
    def call1(to, data, ep):
        payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": to, "data": data}, "latest"]})
        try:
            raw = curl(ep, timeout=8, data=payload)
            r = json.loads(raw).get("result")
            return int(r, 16) if isinstance(r, str) and r.startswith("0x") else None
        except Exception:
            return None
    log["leg3_detail"] = []
    for s in sale_shapes:
        addr = s["address"]
        det = {"address": addr, "S1": s["S1"], "S2": s["S2"],
               "in_same_owner_discards": addr.lower() in disc_addrs,
               "in_snapshot": snap_lookup(addr),
               "age": "UNVERIFIED (getLogs dead - first-mint corroboration unavailable this run)",
               "verdict": "watchlist-only - age unverified, never lead, never previewed/minted"}
        if addr.lower() in disc_addrs:
            det["verdict"] = "BLOCKED - same-owner-discarded, never promote/report as lead"
        elif rpc_working:
            pool = {}
            for fn in ["freeSharesRemaining", "freeClaimed", "freeMinted", "freeMintedTotal",
                       "FREE_SUPPLY", "FREE_SLOTS", "totalSupply", "totalMinted"]:
                v = call1(addr, sel(f"{fn}()"), rpc_working)
                if v is not None:
                    pool[fn] = v
            slot = {}
            for fn in ["freeClaimed", "mintedBy", "freeLeft", "freeUsed"]:
                v = call1(addr, sel(f"{fn}(address)") + enc_addr(USER), rpc_working)
                if v is not None:
                    slot[fn + "_user"] = v
            bal = call1(addr, sel("balanceOf(address)") + enc_addr(USER), rpc_working)
            if bal is not None:
                slot["balanceOf_user"] = bal
            det["pool_reads"] = pool
            det["slot_reads"] = slot
        log["leg3_detail"].append(det)

# --- Bridge leg (read-only) ---
snap_addrs = set()
for sec in ("contracts", "track_c", "pending_claims"):
    for k, v in snap.get(sec, {}).items():
        if isinstance(k, str) and k.startswith("0x") and len(k) == 42:
            snap_addrs.add(k.lower())
        if isinstance(v, dict):
            for f in ("address", "sale", "token"):
                a = v.get(f)
                if isinstance(a, str) and a.startswith("0x"):
                    snap_addrs.add(a.lower())
bcontracts = bridge.get("contracts", {}) if isinstance(bridge, dict) else {}
b_disc = sum(1 for ent in bcontracts.values()
             if isinstance(ent, dict) and ent.get("same_owner_discarded"))
b_not_in_snap = [a for a in bcontracts if a.lower() not in snap_addrs]
log["bridge_leg"] = {"total": len(bcontracts), "same_owner_discarded": b_disc,
                     "in_snapshot_addr": len(bcontracts) - len(b_not_in_snap),
                     "not_in_snapshot_addr": len(b_not_in_snap),
                     "not_in_snapshot": b_not_in_snap,
                     "note": "Bridge read-only; contracts not in snapshot are recorded for the main 30-min job only. Promotion check via leg4 promo flags below."}

# --- Leg 4: re-read 48-item set vs 03:04 baseline ---
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_uint(n): return format(n, "064x")
NOARG = ["totalSupply", "totalMinted", "totalMints", "freeMinted", "freeClaimed",
         "freeMintedTotal", "freeLeft", "freeUsed", "FREE_CAP", "FREE_SUPPLY",
         "FREE_SHARES", "FREE_QUOTA", "FREE_PER_WALLET", "remainingFree",
         "MAX_SUPPLY", "MAX_FREE", "sharesMinted", "sold", "phase", "launched",
         "soldOut", "closed", "finalized", "mintOpen", "mintActive",
         "totalSkunksMinted", "freeSkunksClaimed", "freeSkunksRemaining",
         "freeRemaining", "mintCount", "MAX_MINTS", "opened", "openedAt", "saleActive",
         "soldShares", "publicMinted", "launchTime", "totalShares", "totalFreeShares",
         "mintingOpen", "TOTAL_SHARES", "MAX_FREE_SHARES", "SALE_START", "isSaleEnded",
         "remaining", "mintEnd", "mintStart", "SALE_END", "startTime",
         "freeWindowOpen", "agentFreeUsed", "AGENT_FREE_CAP", "paidMinted"]
ADDRARG = ["balanceOf", "mintedBy", "freeClaimed", "freeLeft", "freeUsed",
           "freeCount", "freeMinted", "mintedCount", "freeAvailable",
           "hasMinted", "quotaOf", "freeTakenBy", "priceFor", "freeClaimedBy",
           "freeUsedByWallet", "hasFreeMinted", "freeAllowance", "maxShares", "remainingShares"]
ADDRUINT = ["quote", "freeFor"]
def calldata(field):
    if field in ("address", "_batch_fail"): return None
    if field.endswith("_user1"):
        fn = field[:-6]
        if fn in ADDRUINT: return sel(f"{fn}(address,uint256)") + enc_addr(USER) + enc_uint(1)
        return None
    if field.endswith("_user"):
        fn = field[:-5]
        if fn in ADDRARG: return sel(f"{fn}(address)") + enc_addr(USER)
        return None
    if field in NOARG: return sel(f"{field}()")
    return None
def run_batch(calls, ep):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)])
    p = subprocess.run(["curl", "-s", "--max-time", "30", "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "--data", payload],
                       capture_output=True, text=True)
    try: return json.loads(p.stdout)
    except Exception: return {"_curl_error": p.stdout[:200] + p.stderr[:200]}
def decode(r):
    if not isinstance(r, str) or not r.startswith("0x"): return None
    try: return int(r, 16)
    except Exception: return None

leg4 = {"status": "SKIPPED"}
if rpc_working:
    try:
        prev = json.load(open(BASE + "hot-leg-2026-11-10-0304-reread.json"))
        items = prev["items"]
        jobs = []
        for name, entry in items.items():
            for field in entry:
                data = calldata(field)
                if data: jobs.append((name, field, entry["address"], data))
        try:
            raw = curl(rpc_working, timeout=10, data='{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}')
            block = int(json.loads(raw)["result"], 16)
        except Exception:
            block = None
        results, failed = {}, []
        for i in range(0, len(jobs), 25):
            chunk = jobs[i:i + 25]
            resp = run_batch([(to, data) for (_, _, to, data) in chunk], rpc_working)
            if isinstance(resp, dict) and "_curl_error" in resp:
                for (name, field, to, data) in chunk:
                    results[(name, field)] = None; failed.append((name, field))
                continue
            if isinstance(resp, dict): resp = [resp]
            for j, item in enumerate(resp):
                name, field, to, data = chunk[j]
                if isinstance(item, dict) and "result" in item:
                    results[(name, field)] = decode(item["result"])
                else:
                    results[(name, field)] = None; failed.append((name, field))
        reread = {"block": block, "items": {}, "duration_sec": elapsed()}
        read_failed2 = []
        for name, entry in items.items():
            row = {"address": entry["address"]}
            for field in entry:
                if field == "address": continue
                v = results.get((name, field))
                if v is None:
                    row[field] = entry.get(field)
                    read_failed2.append((name, field))
                else:
                    row[field] = v
            reread["items"][name] = row
        reread["read_failed"] = [{"item": n, "field": f} for n, f in read_failed2]
        diffs = []
        for name, row in reread["items"].items():
            base = items.get(name, {})
            for field, val in row.items():
                if field == "address": continue
                old = base.get(field)
                if old is None and val is None: continue
                if old != val: diffs.append({"item": name, "field": field, "old": old, "new": val})
        reread["diffs_vs_0304"] = diffs
        json.dump(reread, open(BASE + "hot-leg-2026-11-10-0404-reread.json", "w"), indent=1)
        sc = snap.get("contracts", {}) or {}
        st = snap.get("track_c", {}) or {}
        flags = []
        for name, entry in reread["items"].items():
            meta = sc.get(name) or st.get(name) or {}
            status = (meta.get("status") or "") if isinstance(meta, dict) else ""
            free = entry.get("freeMinted", entry.get("freeClaimed", entry.get("freeMintedTotal")))
            cap = entry.get("FREE_CAP", entry.get("FREE_SUPPLY", entry.get("FREE_SHARES",
                  entry.get("FREE_QUOTA", entry.get("MAX_SUPPLY")))))
            if isinstance(free, int) and isinstance(cap, int) and cap > 0:
                pct = free / cap
                user_open = entry.get("freeClaimed_user") in (0, False, None) or entry.get("balanceOf_user") == 0
                if free >= cap:
                    flags.append({"item": name, "flag": "sellout?", "pct": round(pct, 4), "free": free, "cap": cap, "snap_status": status})
                elif pct >= 0.25 and user_open:
                    flags.append({"item": name, "flag": "promo-candidate-check", "pct": round(pct, 4), "free": free, "cap": cap, "snap_status": status})
        bridge_in_snap_flags = [f for f in flags
                                if any(f["item"].lower() == a.lower() or
                                       (isinstance(snap.get("contracts", {}).get(f["item"]), dict) and
                                        snap["contracts"][f["item"]].get("sale", "").lower() == a.lower())
                                       for a in bcontracts if a.lower() in snap_addrs)]
        leg4 = {"status": "OK", "block": block, "prev_block": prev.get("block"), "rpc": rpc_working,
                "items_n": len(items), "changes": diffs,
                "failed_call_idx": [{"item": n, "field": f} for n, f in failed],
                "read_failed": reread["read_failed"],
                "promo_flags": flags,
                "bridge_promo_flags": bridge_in_snap_flags,
                "mode": "chunked eth_call batches of <=25 (read-only); null reads keep baseline, never a change"}
    except Exception as e:
        leg4 = {"status": "ERROR", "error": f"{type(e).__name__}: {e}"}
else:
    leg4 = {"status": "SKIPPED", "reason": "BSC RPC unreachable (5 endpoints, eth_blockNumber 8s each)",
            "baseline": "hot-leg-2026-11-10-0304-reread.json - NOT re-read this run"}
log["leg4"] = leg4
pend = snap.get("pending_claims", {}) or {}
log["pending_claims"] = "snapshot pending_claims empty - nothing to re-read" if not pend else f"{len(pend)} pending claims present"
log["duration_s"] = elapsed()
log["seen_total_end"] = len(seen)
log["outcome"] = "SILENT - no new lead/candidate/promotion/change; no execution" if not sale_shapes and not [f for f in (leg4.get("promo_flags") or []) if f["flag"] == "sellout?"] else "SEE flags/sale-shapes - review before reporting"

with open(BASE + "hot-leg-run-2026-11-10-0404.json", "w") as f:
    json.dump(log, f, indent=2, ensure_ascii=False)
with open(BASE + "hot-leg-seen.json", "w") as f:
    json.dump(seen, f, indent=2, ensure_ascii=False)
print(json.dumps(log, indent=2, ensure_ascii=False))
print("ELAPSED", elapsed())
