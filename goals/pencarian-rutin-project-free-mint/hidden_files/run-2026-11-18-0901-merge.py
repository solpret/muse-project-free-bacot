#!/usr/bin/env python3
"""Merge run 2026-11-18 09:01 WIB re-read into onchain-snapshot.json (read-only legs only).
Never writes scan-bridge.json. No preview/mint/claim.
Velocity computed vs run 0831 (block 134224438 -> 134228447, ~30.1 min)."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-0901-reread.json"))
catch = json.load(open(f"{HF}/run-2026-11-18-0901-catchup.json"))
reads = reread["reads"]
for n, v in catch.items():
    reads.setdefault(n, {"address": "", "views": {}})["views"].update(v)
NOW = "2026-11-18 ~09:01 WIB"
BLOCK = reread["block"]
PREV_BLOCK = 134224438
INTERVAL_MIN = (BLOCK - PREV_BLOCK) * 0.45 / 60.0

addr2key = {}
for _k, _v in snap.get("contracts", {}).items():
    if isinstance(_v, dict) and _v.get("address"):
        addr2key[_v["address"].lower()] = _k


def upd(name, fields):
    e = snap["contracts"].get(name)
    if e is None:
        _a = reads.get(name, {}).get("address", "").lower()
        _k = addr2key.get(_a)
        if _k:
            e = snap["contracts"][_k]
    if e is None:
        print("MISS", name)
        return
    v = reads.get(name, {}).get("views", {})
    for f in fields:
        val = v.get(f)
        if isinstance(val, int):
            e[f] = val
    e["lastReadWib"] = NOW
    e["lastReadBlock"] = BLOCK


upd("HIVE Agents", ["totalSupply", "balanceOf_user"])
upd("Bubblebruin", ["totalSupply", "freeClaimed", "balanceOf_user"])
upd("CAT402", ["freeCatsClaimed"])
upd("JADE", ["freeClaimed", "totalSupply", "mintOpen", "mintedBy_user", "balanceOf_user"])
upd("AgentBubble", ["freeMinted", "totalSupply", "totalMinted", "MAX_SUPPLY", "mintOpen", "balanceOf_user"])
upd("DRAGON", ["freeMinted", "totalMinted", "balanceOf_user"])
upd("Matrix", ["freeMinted", "freeRemaining", "totalSupply", "mintOpen"])
upd("AGCLUB", ["totalMinted", "freeMinted", "FREE_CAP", "mintOpen", "balanceOf_user"])
upd("BNBG", ["totalMinted"])
upd("SPARKS", ["totalSupply"])
upd("Ledgera", ["freeClaimed", "totalSupply", "mintOpen", "freeUsed_user", "balanceOf_user"])
upd("BoldLeonidas", ["totalSupply", "mintOpen", "balanceOf_user"])
upd("RaceAgents", ["totalSupply", "freeMinted", "mintOpen"])
upd("CPASS", ["totalMinted", "mintOpen", "balanceOf_user"])
upd("REOPIR", ["freeClaimed", "totalSupply", "mintOpen"])
upd("RAVE", ["totalMinted", "freeMinted", "mintOpen"])
upd("MORFO", ["totalMinted", "mintOpen"])
upd("PIXELFROGS", ["totalSupply", "freeMinted", "freeLeft", "mintOpen", "freeClaimed_user"])
upd("Flare-bd6f", ["totalSupply"])
upd("PunchCard", ["totalSupply", "totalMinted", "freeMinted", "paidMinted", "MAX_SUPPLY", "mintOpen", "mintedCount_user", "balanceOf_user"])
upd("XCOPY", ["totalSupply", "totalMinted"])
upd("ARKYN", ["totalMinted"])
upd("Mine Card", ["totalSupply", "totalMinted"])
upd("ALIEN", ["totalSupply"])
upd("Kitebots", ["totalSupply", "freeMinted"])
upd("EIM", ["totalMinted", "mintOpen"])
upd("Lumenhold", ["totalSupply", "freeClaimed"])
upd("PXIO Miners", ["totalSupply"])
upd("FrieAgent-B751", ["totalSupply"])
upd("FrieAgent-c64d", ["totalSupply"])
upd("Abyssora", ["totalSupply"])
upd("HANAMI", ["totalSupply", "freeMinted"])
upd("Zephyra", ["totalMinted"])
upd("AgentNOVA", ["totalSupply"])
upd("ONI", ["totalMinted", "totalSupply"])
upd("HAPPE", ["totalMinted", "freeMinted"])
upd("Kryntar", ["totalMinted"])
upd("Pengu", ["totalMinted", "freeMinted"])
upd("STOCK AGENT", ["totalSupply", "freeLeft", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "freeMintedByWallet_user", "balanceOf_user"])
upd("THYRK", ["totalSupply", "freeMinted", "MAX_SUPPLY", "freeUsed_user", "balanceOf_user"])
upd("ADRAW", ["freeMinted", "balanceOf_user", "hasClaimedFree_user"])
upd("AgentEcho", ["totalSupply", "mintOpen", "MAX_SUPPLY", "mintedBy_user", "balanceOf_user"])
upd("ARKT", ["totalSupply", "totalMinted", "MAX_SUPPLY", "hasClaimed_user", "balanceOf_user"])
upd("Stromboat", ["totalMinted", "freeMinted", "paidMinted", "mintOpen", "freeMintedBy_user", "balanceOf_user"])
upd("Kageveil Genesis", ["totalSupply", "normalMinted", "mintOpen", "mintClosed", "balanceOf_user"])
upd("Foundry Faces", ["totalMinted"])
upd("Compasyn", ["totalSupply", "freeClaimed", "mintedBy_user", "balanceOf_user"])
jv = reads.get("JADE", {}).get("views", {})
if isinstance(jv.get("cost_user_1"), int):
    snap["contracts"]["JADE"]["cost_user_1"] = jv["cost_user_1"]
pc = reads.get("PunchCard", {}).get("views", {})
if isinstance(pc.get("mintPriceFor_user_1"), int):
    snap["contracts"]["PunchCard"]["mintPriceFor_user_1"] = pc["mintPriceFor_user_1"]

# ---- velocity: computed by the parent from pre-merge snapshot values + reread;
# the merge only persists fresh reads above (previousTotalSupply in the snapshot
# is stale by construction and is NOT used here). ----

# ---- Track B pending claim re-read ----
bna = reads.get("binanceai-mint", {}).get("views", {})
pc_entry = snap.get("pending_claims", {}).get("binanceai.fun")
if pc_entry is not None:
    for f in ("launched", "failed", "isRefundPhase", "totalShares", "tokenClaimed_user"):
        if isinstance(bna.get(f), int):
            pc_entry[f] = bna[f]
    pc_entry["lastReadWib"] = NOW
    pc_entry["runNote0901"] = (
        "Run 0901 (blok %s): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 "
        "- tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM." % BLOCK
    )

# ---- Track C: RigForge re-read ----
rg = reads.get("RigForge", {}).get("views", {})
rf = (snap.get("track_c", {}) or {}).get("RigForge")
if isinstance(rf, dict):
    for f in ("freeSharesLeft", "openedAt", "freeClaimed"):
        if isinstance(rg.get(f), int):
            rf[f] = rg[f]
    rf["runNote0901"] = (
        "Run 0901 (blok %s): openedAt 0, freeSharesLeft 624, freeClaimed 376 "
        "- belum dibuka. DIAM." % BLOCK
    )

# ---- ARKT-claim-62a7 ----
ac = snap["contracts"].get("ARKT-claim-62a7")
if isinstance(ac, dict):
    acv = reads.get("ARKT-claim-62a7", {}).get("views", {})
    for _f in ("totalSupply", "totalMinted", "paused", "hasClaimed_user"):
        if isinstance(acv.get(_f), int):
            ac[_f] = acv[_f]
    ac["lastReadWib"] = NOW
    ac["lastReadBlock"] = BLOCK
    ac["runNote0901"] = (
        "Run 0901: totalSupply 3 flat, totalMinted 3, hasClaimed(user) 0 - tanpa perubahan. "
        "Early lead sudah dilaporkan sekali run 0331; tanpa perubahan."
    )

# ---- ARKT NFT (key "方舟门票 (ARKT)") ----
arktn = snap["contracts"].get("方舟门票 (ARKT)")
if isinstance(arktn, dict):
    arv = reads.get("ARKT", {}).get("views", {})
    for _f in ("totalSupply", "totalMinted", "MAX_SUPPLY", "hasClaimed_user", "balanceOf_user"):
        if isinstance(arv.get(_f), int):
            arktn[_f] = arv[_f]
    arktn["lastReadWib"] = NOW
    arktn["lastReadBlock"] = BLOCK

# ---- ADRAW note ----
ad = snap["contracts"].get("ADRAW")
if isinstance(ad, dict):
    ad["runNote0901"] = (
        "Run 0901 (blok %d): freeMinted 307->309 (post junn1.ai 09:03 WIB sebut 308/1000, "
        "mintFreeTicket() value 0 lolos, 'jangan pakai mint(1), itu revert'); totalSupply/mintOpen "
        "tetap revert (non-standard); hasClaimedFree(user)=0, balance 0. FreePct ~30,9pct (<50pct/<70pct), "
        "umur UNVERIFIED (periodStart 15:12 WIB 17 Nov - 15:12 WIB 20 Nov, first-mint belum "
        "dikoroborasi) -> tetap watchlist-only, BUKAN promosi/kandidat. DIAM." % BLOCK
    )

# ---- NEW: AlphaPulse Genesis Badge V1 (watchlist-only, age unverified) ----
# Triage run 0901: Boltbook post junn1.ai 2026-11-18T02:03:39Z; live probe blok 134228701:
# totalSupply/totalMinted 29, MAX_SUPPLY 10000, mintOpen 1, balanceOf(user) 0;
# agentRegistry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (live); bytecode mint() 0x1249c58b
# + agentRegistry() + mintOpen() selectors IN CODE; Sourcify UNVERIFIED (no ABI);
# free views (freeMinted/freeClaimed/freeLeft/FREE_SUPPLY) + cost/quote ALL revert -> free% UNVERIFIED.
# First-mint getLogs BLOCKED (bsc-dataseed/dataseed1/dataseed2 'limit exceeded' even 5k-block
# ranges; Ankr 401) + BscScan text fetch 403 -> launch age UNVERIFIED (first-seen job
# 17 Nov 13:29 WIB = upper bound launch; age >= ~19,5 jam, bisa >24 jam; V2 sudah tutup).
# NOT an early lead: first mints NOT verified on-chain in this run + not newly detected
# (first seen 17 Nov 13:29, hot-leg-seen checked-not-sale-shape on empty ABI).
# NOT a candidate/strong lead: 29/10000 = 0,29% (jauh di bawah 50%/70%), umur + free% UNVERIFIED,
# website gate UNVERIFIED (AlphaPulse APLS share sale tercatat PAID-ONLY 1 USDT/share; badge ini
# kontrak/produk berbeda, situs badge belum terverifikasi). NEVER preview/mint.
snap["contracts"]["AlphaPulse Genesis Badge V1"] = {
    "address": "0xE09Ab25732b1e1FdA7ad4d551EEA0aAC65aD0711",
    "status": "watchlist-only-age-unverified-2026-11-18",
    "name": "AlphaPulse Genesis Badge V1",
    "kind": "ERC721",
    "totalSupply": 29,
    "totalMinted": 29,
    "MAX_SUPPLY": 10000,
    "mintOpen": 1,
    "balanceOf_user": 0,
    "agentRegistry_live": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "freePctNote": "29/10000 = 0,29% total-supply; free% UNVERIFIED (no free views on-chain, semua revert).",
    "firstSeenWib": "2026-11-17 13:29 WIB (hot-leg-seen, Boltbook front page)",
    "firstSeenBlock": None,
    "source": "boltbook-junn1-recheck-2026-11-18-0903",
    "launchNote": "Launch age UNVERIFIED. First-mint getLogs BLOCKED (public RPC 'limit exceeded', Ankr 401); BscScan 403. First-seen job 17 Nov 13:29 WIB = upper bound launch -> umur >= ~19,5 jam, bisa >24 jam. V2 sudah tutup (per post junn1.ai).",
    "gateNote": "Website UNVERIFIED (AlphaPulse APLS share sale tercatat PAID-ONLY; badge V1 situs belum terverifikasi). X: junn1.ai recheck post (bukan akun proyek).",
    "lastReadBlock": 134228701,
    "lastReadWib": NOW,
}

snap["checkedNotAgentShaped0901_1118"] = {
    "sourcify_0901": "Feed top BERUBAH vs 0831 (verifiedAt top 2026-11-18T02:04:35Z): 1 kontrak baru vs hot-leg 0859. 0x6E0517d503d8b876FAaD288CA0277754941c0865 (exact_match, 9 fns: allowance/approve/balanceOf/decimals/name/symbol/totalSupply/transfer/transferFrom - plain ERC-20, tanpa mint/quote/free views/agent ref, registry-bytes NO) -> checked-not-agent-shaped. Hot-leg 0859 sudah shape-check 0x0226C9833B6d35E11d81BeD8Cb561Cd040477777 + 0x8cDe184BCb65E261a2fE82D502Bb17C4D9c364c3 (keduanya S1/S2 False, is_token True, tanpa mint/quote/free/agent) -> checked-not-sale-shape, tidak diulang run ini.",
    "boltbook_new_0901": "Boltbook EN+ZH (44.332/42.720 byte, HTTP 200): 9+8 alamat. 1 tampak-baru 0xE09Ab25732b1e1FdA7ad4d551EEA0aAC65aD0711 = AlphaPulse Genesis Badge V1 (post junn1.ai 02:03:39Z: 'mint() value 0 lolos, 29/10.000, mintOpen 1, 1 badge per wallet Agent ID, klaim 25 APLS/hari setelah Register; V2 sudah tutup') -> DITRIAGE run ini: agent-shaped (agentRegistry() live = registry 0x60B9...022F; bytecode mint()/agentRegistry()/mintOpen() IN CODE; Sourcify unverified) TAPI BUKAN early lead (first mints tidak terverifikasi on-chain run ini - getLogs rate-limited + Ankr 401; first-seen job 17 Nov 13:29) dan BUKAN kandidat/strong (0,29%, umur + free% UNVERIFIED, website UNVERIFIED) -> ditambahkan ke snapshot sbg watchlist-only-age-unverified, TIDAK dilaporkan sebagai lead, TIDAK di-preview/di-mint. 0xcb3f162f513f36a6bb4e754acf69501d621ef1d7 = prefix tx hash PEARL (false positive regex, sama spt 0831). 0x1c759C4e075103b5B250DB5114B832b17B99C456 + 0x4142045F58D319F133AC33BB7922Fb211595B67c + 0xE09A... = rotasi front page; 0x1c75/0x4142 tanpa konteks free-mint di teks (post PEARL/SNAKE/STOCK follow-up), bukan lead.",
    "alphapulse_probe_0901": "Probe blok 134228701: totalSupply 29, totalMinted 29, MAX_SUPPLY 10000, mintOpen 1, balanceOf(user) 0; agentRegistry() = registry; freeMinted/freeClaimed/freeLeft/freeRemaining/FREE_SUPPLY/cost/quote/mintedBy/freeMintedByWallet SEMUA revert; name()/symbol() empty; codelen 21564; registry-bytes False (alamat registry tidak sbg konstanta bytecode). First-mint getLogs: 0 log DITEMUKAN ADALAH INVALID - semua panggilan error ('limit exceeded' bsc-dataseed/1/2, 'missing trie node' utk getCode historis, Ankr 401); BscScan text fetch 403. Launch age tetap UNVERIFIED.",
}
snap["last_run"] = (
    "free-mint-search 2026-11-18 09:01 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, "
    "0 track-B dibuka, 0 track-C lead; 1 watchlist-only baru (AlphaPulse Genesis Badge V1) - TIDAK dilaporkan sbg lead"
)
snap["last_run_wib"] = "2026-11-18 ~09:01 WIB"
snap["runNote0901_1118"] = (
    "Run 0901 (blok re-read 134228447, interval ~30,1 mnt vs 0831): 0 kandidat, 0 strong lead, "
    "0 early lead baru, 0 track-B dibuka, 0 track-C lead. Scan FAST-FAIL (Ankr 401 ke-50 "
    "berturut-turut main job, elapsed 1,4 dtk, head 134228403; watermark tetap 134086385; "
    "gap ~142.062 blok). Re-read 212 calls, 0 chunk error. Velocity: TIDAK ADA yang lolos "
    "(maks +18 <20: Mine Card 1194->1212, Stromboat totalMinted 249->267; SPARKS +3 rasio 3,33x "
    "tapi <20; STOCK +8 0,80x; ARKYN +12 <20; EIM 611->630 +19 <20; lainnya flat/+0..+3). "
    "AgentBubble 85,0% (freeMinted 1888/2222) + Lumenhold 83,5% (freeClaimed 1252/1500) di atas 70% "
    "TAPI umur UNVERIFIED - BUKAN strong lead. STOCK AGENT 56,2% (624/1111, freeLeft 487, slot user "
    "terbuka quote 0); Matrix 61,0% (610/1000), AGCLUB 59,3% (527/888) di bawah 70%. PunchCard 23,4% "
    "(1302/5555). HIVE flat 1263, Bubblebruin flat 2620 (freeClaimed 2614/7777=33,6%). THYRK slot user "
    "sudah terpakai. JADE cost user 0,0005 BNB (bukan gratis). CAT402 sold out (100/100). PIXELFROGS "
    "mintOpen 0. DRAGON free pool habis 1000/1000, bal 1. ARKT flat 323/1000, hasClaimed 0. "
    "ARKT-claim-62a7 totalSupply 3 flat, hasClaimed 0. ADRAW freeMinted 307->309 (post junn1 sebut "
    "308/1000), tetap watchlist-only-age-unverified. bsccat freeMinted 523->524; pepe free pool habis "
    "500/500 + user sudah mint. Sourcify feed top BERUBAH (verifiedAt 02:04:35Z): 1 baru 0x6E05... "
    "(plain ERC-20) -> checked-not-agent-shaped; hot-leg 0859 0x0226/0x8cDe S1/S2 False. Boltbook "
    "EN+ZH (44.332/42.720 byte, HTTP 200): 9+8 alamat, 1 tampak-baru AlphaPulse Badge V1 0xE09A... "
    "(29/10000, mintOpen 1, agentRegistry live = registry) -> DITRIAGE: BUKAN early lead (first mints "
    "tidak terverifikasi run ini; first-seen 17 Nov 13:29), BUKAN kandidat/strong (0,29%, umur + free% "
    "UNVERIFIED, website UNVERIFIED) -> watchlist-only-age-unverified, TIDAK dilaporkan sbg lead, "
    "TIDAK di-preview/di-mint. 0xcb3f... = prefix tx hash PEARL (false positive). Sweep EN+ZH: 0 baru "
    "(Oathbots 28 Okt age-excluded, Agentic Gangster 9 Nov free sold out, LeadLoop/NEXUS/AgentForge/"
    "AGENTID 25-27 Okt, First-Dollar Grove 8 Nov, Subsonic Tribe 26 Okt, Laser Agents 25 Okt, AGENT "
    "COSMOS 5 Nov, Bitcoin Frogs age-excluded + pool habis, ORBITA sale CLOSED 1000/1000, UFO window "
    "tutup 12 Nov, NEBULA minted-by-user, NOVRA 7 Nov di track_c, Agent Koi 25 Okt - semuanya "
    "berumur >24 jam / pool habis / sudah dikenal). Odaily newsflash (270.886 byte) + PANews (118.561 "
    "byte), keduanya HTTP 200: 0 hit Agent ID/free-mint/free-share. Bridge: 116 kontrak, 0 not in "
    "snapshot, 7 same-owner discarded. binanceai.fun pending claim tetap refund phase (launched 0, "
    "failed 1, isRefundPhase 1, tokenClaimed 0). RigForge belum dibuka (openedAt 0, freeSharesLeft 624, "
    "freeClaimed 376)."
)

st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_0901_scan"] = (
    "Run 2026-11-18 09:01 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal "
    "deterministik HTTP 401 Unauthorized (elapsed 1,4 dtk, head 134228403); 401 auth-wide, gagal total ke-50 "
    "berturut-turut main job. Watermark TETAP 134086385; "
    "gap ~142.062 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan). "
    "Tambahan: eth_getLogs publik bsc-dataseed/1/2 'limit exceeded' utk first-mint check E09A (5k-blok range)."
)
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)

json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot updated; contracts:", len(snap["contracts"]))
