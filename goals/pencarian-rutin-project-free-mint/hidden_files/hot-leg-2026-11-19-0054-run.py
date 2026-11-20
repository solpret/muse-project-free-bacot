#!/usr/bin/env python3
"""hot-leg run 2026-11-19 00:54 WIB (adapted from 0039 template).
Leg 1: Sourcify feed via browser.open this run - SAME 20 contracts as 0039
(verifiedAt 2026-11-18T17:16:16Z..17:40:43Z, page crawled 17:41 UTC), all
already in hot-leg-seen.json, 0 new, 0 shape hits. Leg 2: Boltbook EN+ZH
front pages + posts PARUS / KOAI / Board Pulse read via browser.open this
run - every recoverable full address already in seen (PARUS watchlist-only
since 14 Nov, now age-excluded >24h; AGB/MOSS/AGENTONE/LIFTDAEMON/NJAR/KOAI
all checked-not-sale-shape). Leg 3: none - no borderline new sale-shape
contract; 0xAF436d25 PAID-ONLY verdict from 0039 stands.
Bridge leg read-only. Leg 4 reread focus set (same ITEMS as 0039).
Read-only except hot-leg-seen.json notes and this run's own outputs.
No preview/mint. No snapshot rewrite."""
import json, time, subprocess
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
T0 = time.time()
from datetime import datetime, timezone, timedelta
NOW = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
RUN = "free-mint-hot-leg 2026-11-19 00:54 WIB"
out = {"run": RUN, "started_wib": NOW}

# --- Leg 1: Sourcify feed (via browser.open this run) ---
FEED = ["0x34F49Fb4612c790ae8e037d344bd516EEfe6D7BE",
 "0x51Cb8e758fe97361A6CE9485C46A3DB3A763aD53",
 "0x07409d37ae90790E5104D982B8A3873712bFED71",
 "0xed0Be12F8E817e1241a3E6a0Ce1Bfec4B8d036EA",
 "0xC463960af285b7EDA0909D362Ae31783597C2076",
 "0x30C3ddb389705DEbe8eB7Fe1fdEaa98efE432926",
 "0xc3c60E780aD565A960eD214420DA46C923F9aF2E",
 "0x78f94Ab5615dD4835dE12e6F85098D7f5Ef85E42",
 "0x33E08b7A9399677b93445B7d525c4769554c28Cd",
 "0x7CDEf7a952a5B9b9931B68dc6AE742067030F7bE",
 "0x8C83AA6854b20f8D90485275F32e62fb4751ec7F",
 "0xAF436d2540e242533FBa3663e773fc0C57b97a8C",
 "0x3ABE7a3eFE18545971D19Fac8366D9425c026024",
 "0x1D1e01C88C59dbf067edd49B1311B10d05413811",
 "0x78C73Cbf086c7A65281a176d44c6366DbAdD7777",
 "0x6BE9e81145628a42Bd9BC005960Ce96D8B73409c",
 "0x1d3665da429D876f66e63e782BBdF7e22EbFbB0d",
 "0x35a038D698bf4d5766754f048a2427D74E9Cf85c",
 "0x0Cbbb46A4054586EfD43e3F42e334A2bAb8eE6EA",
 "0xAfBc1f54153CDa524347105CbaA7E0E38c45c6Ea"]
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
new = [a for a in FEED if a.lower() not in seen_l and a.lower() != REGISTRY.lower()]
out["sourcify_feed"] = {"total": len(FEED), "new": len(new), "new_contracts": new,
    "top": FEED[0], "top_verifiedAt": "2026-11-18T17:40:43Z",
    "verifiedAt_range": "2026-11-18T17:16:16Z..17:40:43Z",
    "fetch": "browser.open this run (VM curl sourcify.dev timed out 20/20 at 15s)"}

# --- Leg 2: Boltbook EN+ZH (via browser.open this run, full pages) ---
# Full contract addresses recoverable from the reads (ALL already in seen):
BB_ADDRS = ["0xB8b7eF8D49981F8987Dfc271DCa50E24ce87AbEb",  # PARUS (seen 14 Nov, watchlist-only)
            "0x0b0b8dF4D7df0B2cDd00877B476a447a8A1824ee",  # Nightjar NJAR (seen 5 Nov, plain token)
            "0x42c9ED912025DF33cA1676AAD4651cDdeD3F09ED",  # AgentGate Badge AGB (seen 18 Nov 18:43)
            "0xaE9d85E78a609f185B4682d87Da12d13B03cf8d8",  # Hivebyte (leg-4 focus set)
            "0x5b49B06a2E25FcE0BCa865Be70F3C62b6319367a",  # Mossminds MOSS (seen 5 Nov)
            "0x9B0c237A123277fCf8768550Bbdd7767C73Cf5D3",  # AGENTONE Hero (seen 18 Nov 18:26)
            "0xbd1a0Bf361C6B369979028a3FA98adDe3C9C4eEc",  # LIFTDAEMON OPER (seen 16 Nov)
            "0x26ad277193ff31bd086a47bf7b1d25a93573c989",  # AgentQuest Badge (seen 0039)
            "0x2296367F74b2Ec266CF4667d98501Ae7110f5a58",  # Pickhash (already seen)
            "0x2f9d7672f393d6c0482e60ce10cada28b201b721"]  # PONK (already seen)
bb_new = [a for a in BB_ADDRS if a.lower() not in seen_l]
out["boltbook_en"] = {"bytes": "read via browser.open (179 lines)",
    "full_address_contracts": len(BB_ADDRS), "addresses": BB_ADDRS, "new": len(bb_new),
    "new_contracts": bb_new,
    "notes": "EN+ZH same post set. PARUS post (free mint + season claim, 882/10,000, freeRemaining 1,118 at 09:00 WIB 18 Nov): contract seen since 14 Nov 19:24, launch 14 Nov 19:22:56 WIB -> age ~4d6h >24h AGE-EXCLUDED this run; free 44.1% <50% anyway. KOAI Genesis post: NO contract address in post (7,000/10,000 claimed); KOAI already checked-not-sale-shape (seen note, RPC probes block 131740747). Board Pulse 17:45 UTC: AGB 264/10,000 mint() PASS sim but checked-not-sale-shape (seen 18 Nov 18:43); Hivebyte in leg-4 focus set; MOSS 1,333/4,000 freeMint() PASS sim but checked-not-sale-shape (seen 5 Nov); AGENTONE Hero 22,864 0-BNB sim REVERT (not free); LIFTDAEMON 512/9,999 0-BNB sim REVERT (not free). ZH-only rechecks: QUBITFOX free window ENDED (firstFreeUsed 507/2,000, mintEnd passed); GLOOP sold out 8 Nov; BUBB 2,202/2,222 (20 seats, age-excluded in snapshot). No new contract needs a shape check.",
    "fetch": "browser.open this run"}
out["boltbook_zh"] = {"same_posts_as_en": True, "fetch": "browser.open this run (178 lines)"}

# --- Shape verdicts (from browser.open ABI reads this run, 00:46-00:47 WIB) ---
# S1 = mint + quote/cost + free-share view + agent/registry ref; S2 = token+sale single contract.
def V(s1, s2, mint, quote, free, agent, token, note):
    return {"S1": s1, "S2": s2, "has_mint": mint, "has_quote": quote,
            "free_views": free, "agent_ref": agent, "is_token": token,
            "status": "checked", "note": note}
SHAPE = {
 "0x34F49Fb4612c790ae8e037d344bd516EEfe6D7BE": V(False, False, False, False, [], True, False, "AgentGig gig marketplace (register/gigs, no mint/quote/free)"),
 "0x51Cb8e758fe97361A6CE9485C46A3DB3A763aD53": V(False, False, False, False, [], True, False, "agent check-in/vault (checkIn/deposit, no mint/quote/free)"),
 "0x07409d37ae90790E5104D982B8A3873712bFED71": V(False, False, False, False, [], False, False, "coin vault/bridge claim (claimNative/claimToken, no mint/quote/free/agent)"),
 "0xed0Be12F8E817e1241a3E6a0Ce1Bfec4B8d036EA": V(False, False, False, False, [], False, True, "plain ERC20 bridge token (bridgeMint minter-only, no free view)"),
 "0xC463960af285b7EDA0909D362Ae31783597C2076": V(False, False, True, False, [], True, False, "AGENT-SHAPED NFT mint (mint+registry+mintedBy, NO quote, NO free-share view) - not S1/S2; early-lead detection stays with main-job scan leg"),
 "0x30C3ddb389705DEbe8eB7Fe1fdEaa98efE432926": V(False, False, False, False, [], True, False, "agent check-in/profile (checkIn/endorse, no mint/quote/free)"),
 "0xc3c60E780aD565A960eD214420DA46C923F9aF2E": V(False, False, False, False, [], False, False, "USDT-generator toy contract, no mint/quote/free/agent"),
 "0x78f94Ab5615dD4835dE12e6F85098D7f5Ef85E42": V(False, False, False, False, [], False, True, "plain ERC20, no mint fn at all"),
 "0x33E08b7A9399677b93445B7d525c4769554c28Cd": V(False, False, True, False, [], True, False, "agent drops (claim/dropId, createDrop; claim counts as mint-word, NO quote, NO free view) - not a sale"),
 "0x7CDEf7a952a5B9b9931B68dc6AE742067030F7bE": V(False, False, False, False, [], True, False, "agent check-in/vault, same ABI as 0x51Cb8e75"),
 "0x8C83AA6854b20f8D90485275F32e62fb4751ec7F": V(False, False, False, False, [], True, False, "AgentIDWall message board (post/getMessage, no mint/quote/free)"),
 "0xAF436d2540e242533FBa3663e773fc0C57b97a8C": V(False, False, True, True, [], True, False, "SHARE-SALE PATTERN (mint+costOf/bnbQuote+registrar+pair+refund+TOTAL_SHARES) but NO free-share view in ABI - leg3 probe below settles paid-only vs free"),
 "0x3ABE7a3eFE18545971D19Fac8366D9425c026024": V(False, False, True, False, [], False, True, "dividend ERC20 (mint(to,amount) minter-only, no quote/free/agent) - not a sale shape"),
 "0x1D1e01C88C59dbf067edd49B1311B10d05413811": V(False, False, False, False, [], False, True, "plain ERC20, no mint fn at all"),
 "0x78C73Cbf086c7A65281a176d44c6366DbAdD7777": V(False, False, False, False, [], False, True, "ERC20 with tax/team controls, no mint/quote/free/agent"),
 "0x6BE9e81145628a42Bd9BC005960Ce96D8B73409c": V(False, False, False, False, [], True, False, "agent badge claim NFT (claimBadge, agentIdRegistry, NO mint/quote/free view) - not a sale shape"),
 "0x1d3665da429D876f66e63e782BBdF7e22EbFbB0d": V(False, False, True, False, [], True, False, "AgentClaimHub (claim(campaignId), claim counts as mint-word, NO quote, NO free view) - generic claim distributor, not a sale"),
 "0x35a038D698bf4d5766754f048a2427D74E9Cf85c": V(False, False, False, False, [], False, False, "coin vault/bridge claim, same ABI as 0x07409d37"),
 "0x0Cbbb46A4054586EfD43e3F42e334A2bAb8eE6EA": V(False, False, False, False, [], False, True, "plain ERC20 bridge token, same ABI as 0xed0Be12F"),
 "0xAfBc1f54153CDa524347105CbaA7E0E38c45c6Ea": V(False, False, False, False, [], False, True, "plain ERC20 bridge token, same ABI as 0xed0Be12F"),
 "0x26ad277193ff31bd086a47bf7b1d25a93573c989": V(False, False, True, False, [], True, False, "AgentQuest Badge (Boltbook): soulbound quest-badge ERC721, claim(questId)/claimAll, agentId+curated; NO quote, NO free-share view - NOT a sale shape; gas-only quest claim per Boltbook post, not reported as lead"),
 "0x2296367F74b2Ec266CF4667d98501Ae7110f5a58": V(False, False, True, True, [], True, False, "Pickhash (Boltbook 00:54): freeMint()+quote+agentRegistry present but NO free-share VIEW in strict list; 3,292/7,777=42.3% (<50%), first seen 2026-11-14 -> age >24h; NOT candidate, NOT strong lead"),
}
targets = new + bb_new
out["shape_check_targets"] = targets
out["shape_check"] = [dict({"address": a}, **SHAPE[a]) for a in targets if a in SHAPE]
out["shape_hits"] = [a for a in targets if a in SHAPE and (SHAPE[a]["S1"] or SHAPE[a]["S2"])]
out["seen_added"] = targets

# --- RPC helpers (same as 0039 template) ---
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42: d += enc_addr(a)
        elif isinstance(a, str) and a.startswith("0x"): d += enc_u(int(a, 16))
        else: d += enc_u(int(a))
    return d
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def post_rpc(ep, payload, timeout=60):
    o = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(o)

# --- Leg 3: no probe this run ---
# No borderline new sale-shape contract: feed 0 new, Boltbook 0 new.
# 0xAF436d25 PAID-ONLY verdict (costOf(1)=1 BNB) from run 0039 stands.
leg3 = {"note": "no borderline new sale-shape contract this run - no probe needed",
        "0xAF436d2540e242533FBa3663e773fc0C57b97a8C": "PAID-ONLY verdict stands (run 0039: costOf(1)=1e18 wei)"}
out["leg3"] = leg3

# --- Seen updates (new + Pickhash note refresh) ---
for a in targets:
    if a in SHAPE:
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed" if a in new else "boltbook",
                   "status": SHAPE[a]["status"],
                   "note": f"S1={SHAPE[a]['S1']} S2={SHAPE[a]['S2']} mint={SHAPE[a]['has_mint']} quote={SHAPE[a]['has_quote']} free={SHAPE[a]['free_views']} agent={SHAPE[a]['agent_ref']} token={SHAPE[a]['is_token']} :: {SHAPE[a]['note']}"}
if "0x2296367F74b2Ec266CF4667d98501Ae7110f5a58" in seen:
    seen["0x2296367F74b2Ec266CF4667d98501Ae7110f5a58"]["note"] = SHAPE["0x2296367F74b2Ec266CF4667d98501Ae7110f5a58"]["note"]
    seen["0x2296367F74b2Ec266CF4667d98501Ae7110f5a58"]["status"] = "checked"
# PARUS age-exclusion (launch 2026-11-14 19:22:56 WIB, age ~4d6h > 24h)
_pk = "0xB8b7eF8D49981F8987Dfc271DCa50E24ce87AbEb"
if _pk in seen:
    seen[_pk]["status"] = "age-excluded"
    seen[_pk]["note"] = seen[_pk].get("note", "") + " | Run 0054: AGE-EXCLUDED - launch 2026-11-14 19:22:56 WIB, age ~4d6h >24h; free 882/2000=44.1% (Boltbook recheck 09:00 WIB 18 Nov) <50% anyway; no promotion, no preview/mint."
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["seen_n"] = len(seen)

# --- Bridge leg (read-only) ---
try:
    br = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = br.get("contracts", {})
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    def _addr_vals(section, fields):
        o = set()
        for v in (snap.get(section) or {}).values():
            if isinstance(v, dict):
                for f in fields:
                    x = v.get(f)
                    if isinstance(x, str) and x.startswith("0x") and len(x) == 42:
                        o.add(x.lower())
        return o
    snap_addrs = (_addr_vals("contracts", ["address", "sale", "contract"])
                  | _addr_vals("track_c", ["sale", "address", "token", "contract"])
                  | _addr_vals("pending_claims", ["address", "sale", "mint"]))
    outside, discarded = [], 0
    for addr, info in bcontracts.items():
        if info.get("same_owner_discarded"):
            discarded += 1
            continue
        if addr.lower() not in snap_addrs:
            outside.append(addr)
    out["bridge_scan"] = {"total": len(bcontracts), "not_in_snapshot": len(outside),
                          "not_in_snapshot_list": outside, "same_owner_discarded": discarded}
except Exception as e:
    out["bridge_scan"] = {"error": f"{type(e).__name__}: {e}"}

# --- Leg 4: reread focus set (same ITEMS as 0039) ---
V = lambda name, sig, args=None: (name, sig, args or [])
ITEMS = {
 "JADE": ("0x1b8894391a3dcfe7e248c321103265ab52e273e0",
    [V("cost_user_1","cost(address,uint256)",[USER,1]), V("freeClaimed","freeClaimed()"),
     V("totalSupply","totalSupply()"), V("mintOpen","mintOpen()"),
     V("mintedBy_user","mintedBy(address)",[USER]), V("balanceOf_user","balanceOf(address)",[USER])]),
 "AgentBubble": ("0x0d72970046c056db90888351b739246f468bff0b",
    [V("freeMinted","freeMinted()"), V("totalSupply","totalSupply()"), V("totalMinted","totalMinted()"),
     V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",[USER])]),
 "DRAGON": ("0xfc191b76041498b14dcae3c802af3389c74263e6",
    [V("freeMinted","freeMinted()"), V("totalMinted","totalMinted()"), V("mintOpen","mintOpen()"),
     V("balanceOf_user","balanceOf(address)",[USER])]),
 "Matrix": ("0x1F669b714337F3C2585072c53fdDD89581F928fF",
    [V("freeMinted","freeMinted()"), V("freeRemaining","freeRemaining()"), V("totalSupply","totalSupply()"),
     V("mintOpen","mintOpen()")]),
 "AGCLUB": ("0x67270bb351515abf3089ca5420456897363f5e75",
    [V("totalMinted","totalMinted()"), V("freeMinted","freeMinted()"), V("FREE_CAP","FREE_CAP()"),
     V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",[USER])]),
 "BNBG": ("0x1595013dfc8c6b3f4b172254bf09bdaf1421002b", [V("totalMinted","totalMinted()")]),
 "SPARKS": ("0xd52fd117c4b47d03e4e16e778871f09faa5a024b", [V("totalSupply","totalSupply()")]),
 "Ledgera": ("0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d",
    [V("freeClaimed","freeClaimed()"), V("totalSupply","totalSupply()"), V("mintOpen","mintOpen()"),
     V("freeUsed_user","freeUsed(address)",[USER]), V("balanceOf_user","balanceOf(address)",[USER])]),
 "BoldLeonidas": ("0x84bcb8c16566e81ce902530c9da1e3de291f9941",
    [V("totalSupply","totalSupply()"), V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",[USER])]),
 "RaceAgents": ("0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f",
    [V("totalSupply","totalSupply()"), V("freeMinted","freeMinted()"), V("mintOpen","mintOpen()")]),
 "CPASS": ("0x5877d2bb9f226cc3e438f4d656caeb27deafc576",
    [V("totalMinted","totalMinted()"), V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",[USER])]),
 "REOPIR": ("0x12f65bc14037ccdf3f97afc0e67a0e4aca3cf5b9",
    [V("freeClaimed","freeClaimed()"), V("totalSupply","totalSupply()"), V("mintOpen","mintOpen()")]),
 "RAVE": ("0x7c40B78992d86EDfFB5553C74dB5EF427100bb95",
    [V("totalMinted","totalMinted()"), V("freeMinted","freeMinted()"), V("mintOpen","mintOpen()")]),
 "MORFO": ("0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186",
    [V("totalMinted","totalMinted()"), V("mintOpen","mintOpen()")]),
 "AgentNOVA": ("0x43462d7f269fde4914b03e1e07067a61b62b9540", [V("totalSupply","totalSupply()")]),
 "Zephyra": ("0x00a9791be6317d6e3a6c60f75a706c870d882048", [V("totalMinted","totalMinted()")]),
 "Pengu": ("0x5AEc03C90656743475810926B2B2bd443D5c26a4",
    [V("totalMinted","totalMinted()"), V("freeMinted","freeMinted()")]),
 "Kryntar": ("0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe",
    [V("totalMinted","totalMinted()"), V("standardRemaining","standardRemaining()"),
     V("legendaryRemaining","legendaryRemaining()"), V("mintOpen","mintOpen()")]),
 "ONI": ("0x99d01eD93829DBB0EEc11F3a733388c789dA6caD",
    [V("totalMinted","totalMinted()"), V("totalSupply","totalSupply()")]),
 "HAPPE": ("0x72c14121681F1133545947B0735563835CC07B67",
    [V("totalMinted","totalMinted()"), V("freeMinted","freeMinted()")]),
 "PIXELFROGS": ("0x454054e55FA2D7Ba37df7F3ceA269696f19037dF",
    [V("totalSupply","totalSupply()"), V("freeMinted","freeMinted()"), V("freeLeft","freeLeft()"),
     V("mintOpen","mintOpen()"), V("freeClaimed_user","freeClaimed(address)",[USER])]),
 "Flare-bd6f": ("0xbd6ff7ed8fe96b79cb3cbf9dc32656ff7a98a599", [V("totalSupply","totalSupply()")]),
 "PunchCard": ("0x1d4ef0587dd3ff3875a141d4711c60bca40587c4",
    [V("totalSupply","totalSupply()"), V("totalMinted","totalMinted()"), V("freeMinted","freeMinted()"),
     V("paidMinted","paidMinted()"), V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"),
     V("mintPriceFor_user_1","mintPriceFor(address,uint256)",[USER,1]),
     V("mintedCount_user","mintedCount(address)",[USER]), V("balanceOf_user","balanceOf(address)",[USER])]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
    [V("freeSharesLeft","freeSharesLeft()"), V("openedAt","openedAt()"), V("freeClaimed","freeClaimed()"),
     V("freeBooked_user","freeBooked(address)",[USER])]),
 "STOCKAGENT": ("0xba7068233da805bdebcc167be361c219002e6b7f",
    [V("totalSupply","totalSupply()"), V("freeLeft","freeLeft()"), V("FREE_SUPPLY","FREE_SUPPLY()"),
     V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"),
     V("quote_user_1","quote(address,uint256)",[USER,1]),
     V("freeMintedByWallet_user","freeMintedByWallet(address)",[USER]), V("balanceOf_user","balanceOf(address)",[USER])]),
 "Lumenhold": ("0x9701980b0afd825134390ee46fb3bd675a2f356f",
    [V("totalSupply","totalSupply()"), V("freeClaimed","freeClaimed()"), V("FREE_SUPPLY","FREE_SUPPLY()"),
     V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",[USER]),
     V("mintedBy_user","mintedBy(address)",[USER])]),
 "ALIEN": ("0xf5767ac3beb8bbfaf4596dfc1925fc5aca779dcb",
    [V("totalSupply","totalSupply()"), V("FREE_SUPPLY","FREE_SUPPLY()"), V("MAX_SUPPLY","MAX_SUPPLY()"),
     V("mintOpen","mintOpen()"), V("isFreePhase","isFreePhase()"), V("balanceOf_user","balanceOf(address)",[USER])]),
 "ARKT": ("0xf91b1ebbcb2b038107ed10b4cb163ed51ce39037",
    [V("totalMinted","totalMinted()"), V("totalSupply","totalSupply()"), V("MAX_SUPPLY","MAX_SUPPLY()"),
     V("mintOpen","mintOpen()"), V("hasClaimed_user","hasClaimed(address)",[USER]), V("balanceOf_user","balanceOf(address)",[USER])]),
 "AgentEcho": ("0xff2dac2389a6a9593209b6008d5ffa9e73aa19c2",
    [V("totalSupply","totalSupply()"), V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"),
     V("balanceOf_user","balanceOf(address)",[USER])]),
 "Kageveil": ("0xf79860f419be7b604d909e254785400d9edbd9d0",
    [V("normalMinted","normalMinted()"), V("totalSupply","totalSupply()"), V("MAX_SUPPLY","MAX_SUPPLY()"),
     V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",[USER])]),
 "ADRAW": ("0xdc167f998341aa37d734de94db2108f0983bf2a7",
    [V("freeMinted","freeMinted()"), V("totalSupply","totalSupply()"), V("balanceOf_user","balanceOf(address)",[USER]),
     V("hasClaimedFree_user","hasClaimedFree(address)",[USER])]),
 "Stromboat": ("0xC3CB4dF5256c8429Eab306E924BF6E3E6c72163d",
    [V("totalMinted","totalMinted()"), V("freeMinted","freeMinted()"), V("paidMinted","paidMinted()"),
     V("mintOpen","mintOpen()"), V("freeMintedBy_user","freeMintedBy(address)",[USER]),
     V("balanceOf_user","balanceOf(address)",[USER])]),
 "ClafEye": ("0x1c759C4e075103b5B250DB5114B832b17B99C456",
    [V("totalSupply","totalSupply()"), V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"),
     V("balanceOf_user","balanceOf(address)",[USER]), V("costFor_user_1","costFor(address,uint256)",[USER,1])]),
 "DGF": ("0x01f9CA4ff95d49594cC8B6591022186dc5C1Bc72",
    [V("totalMinted","totalMinted()"), V("totalSupply","totalSupply()"), V("mintOpen","mintOpen()"),
     V("balanceOf_user","balanceOf(address)",[USER])]),
 "Hivebyte": ("0xaE9d85E78a609f185B4682d87Da12d13B03cf8d8",
    [V("totalSupply","totalSupply()"), V("freeClaimed","freeClaimed()"), V("FREE_SUPPLY","FREE_SUPPLY()"),
     V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",[USER])]),
 "AgentPepe": ("0xA34C9D34b2Ee93b8059d0ED5302ae595c446423d",
    [V("totalMinted","totalMinted()"), V("totalSupply","totalSupply()"), V("MAX_SUPPLY","MAX_SUPPLY()"),
     V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",[USER])]),
 "AlphaPulse": ("0xE09Ab25732b1e1FdA7ad4d551EEA0aAC65aD0711",
    [V("totalSupply","totalSupply()"), V("totalMinted","totalMinted()"), V("MAX_SUPPLY","MAX_SUPPLY()"),
     V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",[USER])]),
 "THYRK": ("0x4d90ffc3075fb8897edff6d7c6269c906664a20e",
    [V("totalSupply","totalSupply()"), V("freeMinted","freeMinted()"), V("MAX_SUPPLY","MAX_SUPPLY()"),
     V("balanceOf_user","balanceOf(address)",[USER])]),
 "E5F8": ("0xe5f8f8c424821908752332d527428258EcfC245b",
    [V("totalMinted","totalMinted()"), V("totalSupply","totalSupply()"), V("mintOpen","mintOpen()")]),
 "XCOPY": ("0x3fbec44c7c845374267b06033940abe45c63edfa",
    [V("totalSupply","totalSupply()"), V("totalMinted","totalMinted()"), V("MAX_SUPPLY","MAX_SUPPLY()"),
     V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",[USER])]),
 "EIM": ("0x1fccfab61461c4b5c4d1b16580d12a7e32012baa",
    [V("totalMinted","totalMinted()"), V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"),
     V("balanceOf_user","balanceOf(address)",[USER])]),
 "ARKTclaim": ("0x62a7AC33ca463331858693b8Aa05B16688bA29E0",
    [V("totalSupply","totalSupply()"), V("totalMinted","totalMinted()"), V("balanceOf_user","balanceOf(address)",[USER])]),
 "Vitaliq": ("0xad0d78689d047bb9a32f5bf93438373a73da68ec",
    [V("totalSupply","totalSupply()"), V("totalMinted","totalMinted()"), V("mintOpen","mintOpen()"),
     V("balanceOf_user","balanceOf(address)",[USER])]),
 "ARKT8334": ("0x8334C7d0e8aF217EEA5251A0A181e628971535e1",
    [V("totalSupply","totalSupply()"), V("totalMinted","totalMinted()"), V("mintOpen","mintOpen()")]),
 "binanceai-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
    [V("launched","launched()"), V("failed","failed()"), V("isRefundPhase","isRefundPhase()"),
     V("totalShares","totalShares()"), V("tokenClaimed_user","tokenClaimed(address)",[USER])]),
}
BSCCAT = ("0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A",
    [V("totalMinted","totalMinted()"), V("soldShares","soldShares()"), V("freeMinted","freeMinted()"),
     V("freeClaimed","freeClaimed()"), V("freeSharesLeft","freeSharesLeft()"), V("FREE_SHARES","FREE_SHARES()"),
     V("FREE_SUPPLY","FREE_SUPPLY()"), V("totalShares","totalShares()"), V("totalSupply","totalSupply()"),
     V("mintOpen","mintOpen()"), V("opened","opened()"), V("poolOpen","poolOpen()"), V("isPoolOpen","isPoolOpen()"),
     V("launched","launched()"), V("hasMinted_user","hasMinted(address)",[USER]),
     V("freeClaimed_user","freeClaimed(address)",[USER]), V("freeUsed_user","freeUsed(address)",[USER]),
     V("freeLeft_user","freeLeft(address)",[USER]), V("mintedBy_user","mintedBy(address)",[USER]),
     V("quote_user_1","quote(address,uint256)",[USER,1]), V("cost_user_1","cost(address,uint256)",[USER,1]),
     V("costOf_1","costOf(uint256)",[1]), V("bnbQuote_1","bnbQuote(uint256)",[1]),
     V("token","token()"), V("TOKEN","TOKEN()"), V("balanceOf_user","balanceOf(address)",[USER])])
PEPE = ("0x7E920e9e4Ad8E4497aEa7EB9bAF60Cd6c6C8D980",
    [V("freeMinted","freeMinted()"), V("soldShares","soldShares()"), V("FREE_SHARES","FREE_SHARES()"),
     V("opened","opened()"), V("costOf_1","costOf(uint256)",[1]), V("hasMinted_user","hasMinted(address)",[USER])])

def read_views(addr, views):
    calls, meta = [], []
    for key, sig, args in views:
        calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        meta.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            o = {}
            for it, key in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    o[key] = None
                else:
                    r = it["result"]
                    if key in ("token", "TOKEN"):
                        o[key] = "0x" + r[-40:] if len(r) >= 42 else r
                    else:
                        o[key] = to_int(r[:66]) if len(r) >= 66 else r
            return o, ep
        except Exception:
            continue
    return None, None

def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=60)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16)
        except Exception: continue
    return None

def chunked(items, n=4):
    items = list(items.items())
    for i in range(0, len(items), n):
        yield items[i:i+n]

reads, ok, chunk_errors = {}, 0, []
LEG4_DEADLINE = 200
for ci, ch in enumerate(chunked(ITEMS, 4)):
    if time.time() - T0 > LEG4_DEADLINE:
        print(f"chunk {ci+1} SKIPPED deadline ({time.time()-T0:.0f}s)", flush=True)
        chunk_errors.append([n for n, _ in ch] + ["deadline-skipped"])
        for n, _ in ch: reads[n] = {"address": ITEMS[n][0], "views": None}
        continue
    calls, meta = [], []
    for name, (addr, views) in ch:
        for key, sig, args in views:
            calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                          "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
            meta.append((name, key))
    got = None
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=20)
            if isinstance(res, list) and len(res) == len(calls):
                got = (res, ep); break
        except Exception as e:
            print("  chunk ep", ep, "exc", str(e)[:100], flush=True); continue
    names = [n for n, _ in ch]
    if got is None:
        print(f"chunk {ci+1} FAIL {names}", flush=True)
        chunk_errors.append(names)
        for n in names: reads[n] = {"address": ITEMS[n][0], "views": None}
        continue
    res, ep = got
    o = {}
    for it, (name, key) in zip(res, meta):
        if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
            o.setdefault(name, {})[key] = None
        else:
            r = it["result"]
            o.setdefault(name, {})[key] = to_int(r[:66]) if len(r) >= 66 else r
    ok += sum(1 for n in names if o.get(n) is not None)
    for n in names: reads[n] = {"address": ITEMS[n][0], "views": o.get(n)}
    print(f"chunk {ci+1} OK via {ep} ({time.time()-T0:.0f}s) {names}", flush=True)
    time.sleep(1)

if time.time() - T0 > LEG4_DEADLINE:
    bsccat_views, bsccat_ep = None, "deadline-skipped"
    pepe_views, pepe_ep = None, "deadline-skipped"
else:
    bsccat_views, bsccat_ep = read_views(BSCCAT[0], BSCCAT[1])
    pepe_views, pepe_ep = read_views(PEPE[0], PEPE[1])
blk = block_number()
reread = {"started_wib": NOW, "reads": reads, "reads_ok": ok, "reads_total": len(ITEMS),
          "bsccat": {"address": BSCCAT[0], "views": bsccat_views},
          "pepe": pepe_views, "errors": chunk_errors,
          "n_calls": sum(len(v) for _, v in ITEMS.values()) + len(BSCCAT[1]) + len(PEPE[1]),
          "elapsed_s": round(time.time() - T0, 1), "block": blk}
json.dump(reread, open(BASE + "hot-leg-run-2026-11-19-0054-reread.json", "w"), indent=1)
out["leg4_reread_file"] = "hot-leg-run-2026-11-19-0054-reread.json"
out["leg4_rpc_note"] = "chunked direct JSON-RPC batches of 4 items (no fast_rpc race - timed out + 429 on 0324 run); focus set same as 0039"
out["leg4_block"] = blk
out["leg4_chunk_errors"] = chunk_errors

# --- Diff vs 0039 reread ---
try:
    prev = json.load(open(BASE + "hot-leg-run-2026-11-19-0039-reread.json"))
    prev_reads = prev.get("reads", {})
    if not isinstance(prev_reads, dict): prev_reads = {}
    changes = []
    for name, item in reads.items():
        pv = (prev_reads.get(name) or {}).get("views") or {}
        cv = item.get("views") or {}
        diff = {}
        for k in set(list(pv.keys()) + list(cv.keys())):
            if pv.get(k) != cv.get(k):
                diff[k] = {"prev": pv.get(k), "now": cv.get(k)}
        if diff:
            changes.append({"item": name, "type": "value-change", "diff": diff})
    out["leg4_changes_vs_0039"] = changes
    pb = (prev.get("bsccat") or {}).get("views") or {}
    cb = bsccat_views or {}
    out["bsccat_changes_vs_0039"] = {k: {"prev": pb.get(k), "now": cb.get(k)}
                                     for k in set(list(pb.keys()) + list(cb.keys())) if pb.get(k) != cb.get(k)}
    pp = prev.get("pepe") or {}
    out["pepe_changes_vs_0039"] = {k: {"prev": pp.get(k), "now": (pepe_views or {}).get(k)}
                                   for k in set(list(pp.keys()) + list((pepe_views or {}).keys()))
                                   if pp.get(k) != (pepe_views or {}).get(k)}
except Exception as e:
    out["leg4_changes_vs_0039"] = {"error": f"{type(e).__name__}: {e}"}

# --- Threshold check (strong lead >70% + age <24h + slot open) ---
tc = {"notes": "Strong-lead bar >70% + age <24h + slot open. AgentBubble is age-excluded-2026-11-18 in main snapshot, so its >70% free% does NOT promote it. bsccat website gate PASS carried from 0239 run - site NOT re-read this run."}
try:
    pc = (reads.get("PunchCard") or {}).get("views") or {}
    if pc.get("freeMinted") is not None and pc.get("MAX_SUPPLY"):
        tc["PunchCard_free_pct"] = round(100 * pc["freeMinted"] / pc["MAX_SUPPLY"], 1)
    tc["PunchCard_slot"] = {"mintPriceFor_user_1": pc.get("mintPriceFor_user_1"),
                            "mintedCount_user": pc.get("mintedCount_user"),
                            "balanceOf_user": pc.get("balanceOf_user"),
                            "mintOpen": pc.get("mintOpen")}
    ag = (reads.get("AGCLUB") or {}).get("views") or {}
    if ag.get("freeMinted") is not None and ag.get("FREE_CAP"):
        tc["AGCLUB_free_pct"] = round(100 * ag["freeMinted"] / ag["FREE_CAP"], 1)
    mx = (reads.get("Matrix") or {}).get("views") or {}
    if mx.get("freeMinted") is not None and mx.get("freeRemaining") is not None:
        tc["Matrix_free_pct"] = round(100 * mx["freeMinted"] / (mx["freeMinted"] + mx["freeRemaining"]), 1)
    sa = (reads.get("STOCKAGENT") or {}).get("views") or {}
    if sa.get("freeLeft") is not None and sa.get("FREE_SUPPLY"):
        tc["STOCKAGENT_free_pct"] = round(100 * (sa["FREE_SUPPLY"] - sa["freeLeft"]) / sa["FREE_SUPPLY"], 1)
    tc["STOCKAGENT"] = {k: sa.get(k) for k in ("totalSupply","freeLeft","FREE_SUPPLY","mintOpen","quote_user_1","freeMintedByWallet_user","balanceOf_user")}
    lu = (reads.get("Lumenhold") or {}).get("views") or {}
    if lu.get("freeClaimed") is not None and lu.get("FREE_SUPPLY"):
        tc["Lumenhold_free_pct"] = round(100 * lu["freeClaimed"] / lu["FREE_SUPPLY"], 1)
    tc["Lumenhold"] = {k: lu.get(k) for k in ("totalSupply","freeClaimed","FREE_SUPPLY","mintOpen","balanceOf_user","mintedBy_user")}
    al = (reads.get("ALIEN") or {}).get("views") or {}
    if al.get("totalSupply") is not None and al.get("FREE_SUPPLY"):
        tc["ALIEN_free_pct"] = round(100 * al["totalSupply"] / al["FREE_SUPPLY"], 1)
    tc["ALIEN"] = {k: al.get(k) for k in ("totalSupply","FREE_SUPPLY","mintOpen","isFreePhase","balanceOf_user")}
    ar = (reads.get("ARKT") or {}).get("views") or {}
    tc["ARKT"] = {k: ar.get(k) for k in ("totalMinted","totalSupply","MAX_SUPPLY","mintOpen","hasClaimed_user","balanceOf_user")}
    ab = (reads.get("AgentBubble") or {}).get("views") or {}
    if ab.get("freeMinted") is not None and ab.get("MAX_SUPPLY"):
        tc["AgentBubble_free_pct"] = round(100 * ab["freeMinted"] / ab["MAX_SUPPLY"], 1)
    tc["AgentBubble"] = {k: ab.get(k) for k in ("freeMinted","totalSupply","totalMinted","MAX_SUPPLY","mintOpen","balanceOf_user")}
    bn = (reads.get("binanceai-mint") or {}).get("views") or {}
    tc["binanceai_pending"] = {k: bn.get(k) for k in ("launched","failed","isRefundPhase","totalShares","tokenClaimed_user")}
    hb = (reads.get("Hivebyte") or {}).get("views") or {}
    if hb.get("freeClaimed") is not None and hb.get("FREE_SUPPLY"):
        tc["Hivebyte_free_pct"] = round(100 * hb["freeClaimed"] / hb["FREE_SUPPLY"], 1)
    tc["Hivebyte"] = {k: hb.get(k) for k in ("totalSupply","freeClaimed","FREE_SUPPLY","MAX_SUPPLY","mintOpen","balanceOf_user")}
    pf = (reads.get("PIXELFROGS") or {}).get("views") or {}
    if pf.get("freeMinted") is not None and pf.get("freeLeft") is not None:
        tc["PIXELFROGS_free_pct"] = round(100 * pf["freeMinted"] / (pf["freeMinted"] + pf["freeLeft"]), 1)
except Exception as e:
    tc["error"] = f"{type(e).__name__}: {e}"
out["threshold_check"] = tc

# --- Poffzi FCFS process check ---
try:
    r = subprocess.run(["pgrep", "-af", "fcfs"], capture_output=True, text=True)
    out["poffzi_fcfs"] = r.stdout.strip() if r.stdout.strip() else "NO PROCESS FOUND"
except Exception as e:
    out["poffzi_fcfs"] = f"check error: {e}"

out["elapsed_s"] = round(time.time() - T0, 1)
out["overrun_note"] = "Legs 1-2 via browser.open (feed cached 17:41 UTC, same 20 as 0039); no ABI fetches needed - 0 new contracts."
out["executions"] = "none - no preview, no mint, no claim (this script is read-only)"
json.dump(out, open(BASE + "hot-leg-run-2026-11-19-0054.json", "w"), indent=1)
print("DONE ok", ok, "/", len(ITEMS), "block", blk, "elapsed", round(time.time() - T0, 1))
