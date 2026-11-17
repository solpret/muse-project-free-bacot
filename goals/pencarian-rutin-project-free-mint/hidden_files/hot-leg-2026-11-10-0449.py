#!/usr/bin/env python3
"""free-mint-hot-leg run 2026-11-10 04:39 WIB (scheduled 04:39:38 WIB).
Leg 1: Sourcify feed (20 contracts; curl-fresh attempted, fallback = 0439
  feed verifiedAt 2026-11-09T21:11:48Z..21:41:07Z). Leg 2: Boltbook EN via
  browser fetch (same crawl 21:41 UTC / 04:41 WIB as 0439 - no new EN posts)
  + ZH via curl (pending at build; 0439 ZH was 200, 45,927B); EN curl 302 0B.
  New Boltbook names: Brinedroid (same-owner-discarded, no promo), COSO v2
  (age-excluded), JINLI 0x0f45 (= snapshot Jinli Agents, gate-failed strong
  lead), NULLRAID phase 2 PAID (not free), DUMP/SEAT sellouts (no new addr),
  Deltavane 1,417 (age-unverified watchlist). Leg 3: on-chain verify for any
  new sale-shape. Leg 4: re-read 48-item set vs 04:39 baseline (nodereal
  RPC, batched eth_call). Bridge leg: read-only scan-bridge.json cross-check.
  Boltbook EN browser fetch this run = same crawl 21:41 UTC as 04:39 (no new
  EN posts); ZH curl pending at script build. Leg 3: on-chain verify for any
  new sale-shape (pool/slot; age via first-mint corroboration only - getLogs
  dead, so age-unverified -> watchlist-only). Priority queue: Boltbook-new
  first, then feed new, then 0439 shape timeouts (cap leg-1 shape loop at
  75s elapsed; leftovers carry to next run).
Writes only own run JSON + hot-leg-seen.json. No preview/mint unless a
  sale-shape passes ALL guards - none expected; any sale-shape found is
  watchlist-only pending age/site."
"""
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
RUN = "free-mint-hot-leg 2026-11-10 04:49 WIB (scheduled 04:49:38 WIB)"
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

# Pre-seed: Boltbook names already known via snapshot/main job (no shape-check, no report)
PRESEED = {
    "0x0f45b52f80a3a42e56e66cd8cfd1a65895c34496": {
        "status": "snapshot-known-gate-failed",
        "note": "JINLI = snapshot contracts/Jinli Agents, strong-lead-2026-11-08-gate-failed; Boltbook ZH post 04:26 WIB totalSupply 357 flat 71 min; no new gate evidence, never re-reported, never previewed/minted",
        "source": "boltbook-zh"},
    "0xdec01cdfb41e7871fb7ca7b12b1572ce292743c0": {
        "status": "checked-paid-phase",
        "note": "NULLRAID = snapshot contracts/NULLRAID First Breach; Boltbook EN post #0 04:41 WIB: phase 2 is a PAID tranche (price 0.001 BNB, phaseCap 2,222) - not free; never lead/preview/mint",
        "source": "boltbook-en"},
    "0xfcfdc06c85877d3f2d316595882e1aa9e7f2eebc": {
        "status": "snapshot-known-age-unverified",
        "note": "Deltavane = snapshot contracts/Deltavane, watchlist-only-age-unverified-2026-11-10; Boltbook ZH post 04:26 WIB totalSupply 1,417; no promotion, never previewed/minted",
        "source": "boltbook-zh"},
}
for _a, _e in PRESEED.items():
    if _a not in seen and _a.lower() not in seen:
        seen[_a] = {"first_seen_wib": NOW_WIB, **_e}

log["seen_total_start"] = len(seen)

# --- Leg 1: feed (curl-fresh 04:43 WIB; fallback = same 0439 feed) ---
FEED_FALLBACK = [
    ("0x32DA4C6D624B7b6f085a7B2830bFe11C5F326FeC", "2026-11-09T21:41:07Z"),
    ("0x79FC51B4E21eEF051c5e21c3b20a79C2B1565E66", "2026-11-09T21:39:55Z"),
    ("0xf7Ba0abEd6308101455946AFebaD8698BD060A6C", "2026-11-09T21:39:54Z"),
    ("0xcfBf797e448AeeE38ed4F17bd974fCBa46a436eA", "2026-11-09T21:39:49Z"),
    ("0x01BC85A97cfDF7224D6BfC890A8e4C82732B4C40", "2026-11-09T21:34:54Z"),
    ("0x4D59ddd61622Ed74D05A70A8F56Ab96EFE1FEf3C", "2026-11-09T21:34:53Z"),
    ("0xFf0C7Eb14b16046698629e38070b9c424e0316Ea", "2026-11-09T21:34:43Z"),
    ("0x8a011d1e4F7aBa040f35De466C2Fb9AA39187BCc", "2026-11-09T21:28:17Z"),
    ("0x8Da25aCbb37De1e7098dd632A576b1180A8676ea", "2026-11-09T21:24:53Z"),
    ("0xbA358723b4732FCa963d7e7f0021489e5D6a9670", "2026-11-09T21:24:53Z"),
    ("0xf0Ac10736Ae7F50b36F3Bdc357380310F168f303", "2026-11-09T21:24:52Z"),
    ("0x185d72dA51C6E24CFA44C73F956fE5e1A1a76323", "2026-11-09T21:24:47Z"),
    ("0xfC033C70B5Fd11d5a982803D28f66dB5e4d3c6C7", "2026-11-09T21:20:21Z"),
    ("0x2A218Cb874eF875597eA6132fbbb4E1532Fd1dE9", "2026-11-09T21:20:19Z"),
    ("0x439fe0b6a3E84Fdb44dB73F3c8C63b4eb200d6Ea", "2026-11-09T21:20:09Z"),
    ("0x603fC44Bf08DB7CC544Ca92da83B64631247A208", "2026-11-09T21:14:50Z"),
    ("0x91Ba42baeD064C461c4D049032e8580A4195E6dc", "2026-11-09T21:14:44Z"),
    ("0x5847aA9818E3a090DA5f2918776Fc16ffAA68201", "2026-11-09T21:14:39Z"),
    ("0x383529EEEd0f252a22fc0a9E68230a238428936C", "2026-11-09T21:13:53Z"),
    ("0x6Cb1892AFb0697f1b02Da002e57dC331c7B6e6EA", "2026-11-09T21:11:48Z")
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
        log["leg1_feed"] = {"n": len(feed_addrs), "source": "fallback-0439-curl-feed",
                            "error": "curl feed <10 results"}
except Exception as e:
    log["leg1_feed"] = {"n": len(feed_addrs), "source": "fallback-0439-curl-feed",
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
TIMEOUTS_0439 = [
                 "0xbA358723b4732FCa963d7e7f0021489e5D6a9670",
                 "0xf0Ac10736Ae7F50b36F3Bdc357380310F168f303",
                 "0x185d72dA51C6E24CFA44C73F956fE5e1A1a76323",
                 "0xfC033C70B5Fd11d5a982803D28f66dB5e4d3c6C7",
                 "0x2A218Cb874eF875597eA6132fbbb4E1532Fd1dE9",
                 "0x439fe0b6a3E84Fdb44dB73F3c8C63b4eb200d6Ea",
                 "0x603fC44Bf08DB7CC544Ca92da83B64631247A208",
                 "0x91Ba42baeD064C461c4D049032e8580A4195E6dc",
                 "0x5847aA9818E3a090DA5f2918776Fc16ffAA68201",
                 "0x6Cb1892AFb0697f1b02Da002e57dC331c7B6e6EA",
                 "0xe08Bca151a1c9Eb80D700F41d274dEF231281fA6",
                 "0xE0568959967325Fe5B88CFb9189b4fbbF03e43F7",
                 "0x08d1129E78DC99A180b0178A7e1f67B6b76916Ea",
                 "0x97117e89a9045bfd3e87cB9C6d556B93227276EA",
                 "0x7Ba21D5fEbF8bbF2383EDc7eDa6e5A6c539Df703",
                 "0x978b656E2cc410f4678292bA0924014Bf2B5CE13",
                 "0x30dfDfAEF88d3E21754048fb7e2ec1Fe81a9e6eA",
                 "0x35849C970854e25179158c40C06f43D37f962A59",
                 "0xE4F26812f2eF6C0a7d27C0Fa97f75266b9e6430C",
                 "0x149f4191d4d2e12051FE7db40B060B6b930870e5",
                 "0x17851B15052FF88232e3773253875481cfA9cB0f",
                 "0xE1Ee6D8A5b5A8f9C59167DBb2d82e719C4a5e6eA",
                 "0x35864d3103eF0767e5cCc163bFe6C0da2811c828",
                 "0x36DB4d5214bc960D5495b085953eacdE5983C083",
                 "0x3d89FfdbBC676bA33B01f02449759ABd11b946eA",
                 "0xE6c8dAc5B15005926d5891F96E89C14ec143232A",
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
BOLTBOOK_NEW = []  # no new unrecorded Boltbook contract this run; JINLI/NULLRAID pre-seeded in seen below  # Neurolucha NLUCHA, old wake-up +319  # Roguefall RFALL, post ~03:40 WIB

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
for a in TIMEOUTS_0439:
    st, note = seen_status(a)
    if st in ("checked-not-sale-shape", "checked-not-track-c") and "<redacted>" not in note:
        continue
    queue.append((a, "retry-0439-timeout"))

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
                  "note": (f"[{why}] " if why in ("retry-0439-timeout", "feed-new-or-retry") else "") + note,
                  "source": "boltbook-frontpage" if why == "boltbook-new" else "sourcify-feed",
                  "status": status}
    print(addr, status, flush=True)
log["leg1_shapes"] = shapes
log["leg1_sale_shapes"] = sale_shapes

# --- Leg 2: Boltbook EN (browser-fetched 04:41 WIB) + ZH (curl 200) ---
BOLTBOOK_ADDRS = {
    "0xdec01cdfb41e7871fb7ca7b12b1572ce292743c0": "NULLRAID, phase 2 PAID tranche price 0.001 BNB phaseCap 2,222 - NOT free (post #0)",
    "0x1Aa9797cC762b838388566Daa45A56b1709F4Bbe": "WAR3, 3,298/7,777, pace stalled, poster holds #2284 + 10,000 WW3 no pool (post #1; in snapshot, minted-by-user)",
    "0x6a4847cb5f658943222fbd23d2520049f824789d": "Ghostling, totalSupply 4,108 = freeClaimed 4,108, +277 since 2026-11-08 (post #5; age-excluded, no promo)",
    "0xa069401266707e1318bdff45b3F1F61E52D1AE48": "Brinedroid BRNDR, 1,247/2,222, 2 free/wallet, lane woke up (post #6; snapshot same-owner-discarded, NEVER promote)",
    "0x7020368e5421008b92C16798589ac6d91812307e": "COSO v2, freeMinted 601/1,000 +89 since 02:30, 399 left (post #11; track_c age-excluded-2026-11-10, no promo)",
    "0x5fe03829a2f94a8ba3906459258b1305f0e68934": "Roguefall RFALL, 655-658/4,000, freeMinted 654, paid 1 (posts #12/#16; NFT, not track-c)",
    "0xf4bacf30fb8f69373f63d99c657f53dd7774af1d": "ACORE, 916/2,000, pace ~0.7/min burst-pause (post #13; in snapshot AGENT CORE)",
    "0x92473d34f017A342ccBc4119B6EF0EF00dAa4Ee8": "Riddle Run, 2 free riddle mints, whitelist-gated sign-in (post #17; in snapshot)",
    "0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9": "Pacture, sharesMinted 10,164 flat 3h38m, freeMinted 7,700 = MAX_FREE exhausted (post #18; free-sellout already reported 2026-11-05, user slot used)",
    "0x43F046F5C49E54D42913743a8fd2D146CE494C4C": "MIZUKAIRO, 1,379/5,555, mint(1) value 0 passes both RPCs (post #19; NFT, not in snapshot)",
    "0xbb31450432e85968ab700b946bcd2f34898356cb": "Night Court COURT, totalSupply 188/1,111, mintOpen 1, 1 free/wallet (post #21; ABI unavailable)",
    "0x83DecF8076D04D59da771DA6bB298132164be55B": "Skyagent SKYAG, 3,088/3,333, free 2/wallet value 0, owner withdraw()+setMintOpen() (post #22; in snapshot)",
    "0x56ebed63452bb02b975cee02949da3c02466725b": "Neurolucha NLUCHA, 792/4,000, +319 since 19:50 UTC (post #23; ABI unavailable)",
    "0x0f45b52f80a3a42e56e66cd8cfd1a65895c34496": "JINLI, totalSupply 357 flat 71 min (ZH post ~04:26 WIB; snapshot Jinli Agents gate-failed strong lead)",
    "0xfcfdc06c85877d3f2d316595882e1aa9e7f2eebc": "Deltavane, totalSupply 1,417 (ZH post ~04:26 WIB; snapshot age-unverified watchlist-only)",
    "0xcc844748c64b9b8e45ac4504553c9757c7cdb7e0": "Marbleworks MWORKS, freeMinted 1,111/1,111 CLOSED (posts #10/#24; in snapshot, sellout already flagged, user minted)",
}
bb = {"en_crawled": "2026-11-09 21:41 UTC (04:41 WIB)", "zh_crawled": "2026-11-09 21:41 UTC (04:41 WIB)",
      "curl": "EN 302 0B, ZH 200 45,927B via curl; EN front page read via browser fetch instead",
      "addrs": {}, "unrecovered_post_addrs": ["DUMP 650/650 + SEAT 5,000/5,000 sellouts (EN post #20, no addresses in excerpt; SEAT-f11e already sold-out-2026-11-07 in snapshot)",
      "NUSA sale 0x7D08...687c (carried from 04:24 run, address truncated)",
      "Agent Island sim reverts despite open counters (post #11, no address in excerpt)",
      "Pirate blind-box post #14 (paid 0.0002 BNB, not free - no address needed)"],
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

# --- Leg 4: re-read 48-item set vs 04:39 baseline ---
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
        prev = json.load(open(BASE + "hot-leg-2026-11-10-0449-reread.json"))
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
        reread["diffs_vs_0439"] = diffs
        json.dump(reread, open(BASE + "hot-leg-2026-11-10-0449-reread.json", "w"), indent=1)
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
            "baseline": "hot-leg-2026-11-10-0449-reread.json - NOT re-read this run"}
log["leg4"] = leg4
pend = snap.get("pending_claims", {}) or {}
log["pending_claims"] = "snapshot pending_claims empty - nothing to re-read" if not pend else f"{len(pend)} pending claims present"
log["duration_s"] = elapsed()
log["seen_total_end"] = len(seen)
log["outcome"] = "SILENT - no new lead/candidate/promotion/change; no execution" if not sale_shapes and not [f for f in (leg4.get("promo_flags") or []) if f["flag"] == "sellout?"] else "SEE flags/sale-shapes - review before reporting"

with open(BASE + "hot-leg-run-2026-11-10-0449.json", "w") as f:
    json.dump(log, f, indent=2, ensure_ascii=False)
with open(BASE + "hot-leg-seen.json", "w") as f:
    json.dump(seen, f, indent=2, ensure_ascii=False)
print(json.dumps(log, indent=2, ensure_ascii=False))
print("ELAPSED", elapsed())
