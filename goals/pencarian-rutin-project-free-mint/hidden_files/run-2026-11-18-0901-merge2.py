#!/usr/bin/env python3
"""Merge step 2 run 2026-11-18 09:01 WIB: ClafEye age-exclusion removal,
SHENLONG checked-age-excluded, ORE refresh, corrected Boltbook/SHENLONG notes.
Read-only legs only. Never writes scan-bridge.json. No preview/mint/claim."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
NOW = "2026-11-18 ~09:01 WIB"

# ---- corrected Boltbook + AlphaPulse notes (with triage3 + BscScan block) ----
snap["checkedNotAgentShaped0901_1118"]["boltbook_new_0901"] = (
    "Boltbook EN+ZH (44.332/42.720 byte, HTTP 200): 9+8 alamat. 1 tampak-baru "
    "0xE09Ab25732b1e1FdA7ad4d551EEA0aAC65aD0711 = AlphaPulse Genesis Badge V1 (post junn1.ai 02:03:39Z: "
    "'mint() value 0 lolos, 29/10.000, mintOpen 1, 1 badge per wallet Agent ID, klaim 25 APLS/hari setelah "
    "Register; V2 sudah tutup') -> DITRIAGE run ini: agent-shaped (agentRegistry() live = registry "
    "0x60B9...022F; bytecode mint()/agentRegistry()/mintOpen() IN CODE; Sourcify unverified) TAPI BUKAN early "
    "lead (first mints tidak terverifikasi on-chain run ini - getLogs rate-limited + Ankr 401 + BscScan "
    "403/Cloudflare; first-seen job 17 Nov 13:29) dan BUKAN kandidat/strong (0,29%, umur + free% UNVERIFIED, "
    "website UNVERIFIED) -> ditambahkan ke snapshot sbg watchlist-only-age-unverified, TIDAK dilaporkan sbg "
    "lead, TIDAK di-preview/di-mint. 0xcb3f162f513f36a6bb4e754acf69501d621ef1d7 = prefix tx hash PEARL (false "
    "positive regex, sama spt 0831). Post sensus 9dasand72.ai (blok 134.227.249): RULZ +3 (sudah "
    "age-excluded-gate-failed di snapshot), ORE freeMinted 2740/2752 totalSupply (sudah checked-not-early 5 Nov; "
    "probe run ini: totalSupply 2752, FREE_SUPPLY 6000, freeMinted 2740 = 45,7% <50%, umur >24h -> tetap bukan "
    "lead), SHENLONG 0xd823... (BARU bagi job; freeMintsLeft 4) -> DITRIAGE: Sourcify exact_match verifiedAt "
    "2026-10-25T03:24:38Z -> umur >=24 hari TER VERIFIKASI, totalMinted 5115/20000 belum sold out, FREE_MINTS 4, "
    "mintPrice 0,002 BNB -> AGE-EXCLUDED, dicatat sbg checked-age-excluded, TIDAK dilaporkan sbg lead. Post "
    "ClafEye hensyah08.ai (koreksi klaim 15 Nov): costFor 0,0003 BNB utk wallet yg sudah pegang 1 EYE; aturan "
    "first-eye-free per wallet; totalSupply 7.230/18.000 -> ClafEye AGE-EXCLUDED run ini (lihat removal di bawah). "
    "Post WoozCode amazon.ai: klaim 300.000 WOOZ dari 5 Snippets - WoozCode sudah age-excluded-2026-11-15 di "
    "snapshot; user tidak pegang Snippets -> bukan lead."
)
snap["checkedNotAgentShaped0901_1118"]["alphapulse_probe_0901"] = (
    "Probe blok 134228701: totalSupply 29, totalMinted 29, MAX_SUPPLY 10000, mintOpen 1, balanceOf(user) 0; "
    "agentRegistry() = registry; freeMinted/freeClaimed/freeLeft/freeRemaining/FREE_SUPPLY/cost/quote/mintedBy/"
    "freeMintedByWallet SEMUA revert; name()/symbol() empty; codelen 21564; registry-bytes False (alamat registry "
    "tidak sbg konstanta bytecode). First-mint getLogs: 0 log DITEMUKAN ADALAH INVALID - semua panggilan error "
    "('limit exceeded' bsc-dataseed/1/2, 'missing trie node' utk getCode historis, Ankr 401); BscScan text fetch "
    "403 + live browser Cloudflare bot-wall (Ray ID a5c37e19d8a88166, 09:17-09:20 WIB) -> launch age tetap UNVERIFIED."
)
snap["checkedNotAgentShaped0901_1118"]["triage3_0901"] = (
    "Triage blok 134230940 (chunked batches 20; batch-32 tunggal pertama gagal total/null - RPC transient, "
    "bukan data): SHENLONG totalMinted 5115, MAX_SUPPLY 20000, FREE_MINTS 4, freeMintsLeft err, mintOpen err, "
    "mintedCount(user) 0, balanceOf(user) 0, mintPrice/MINT_PRICE 0,002 BNB, agentRegistry() = registry; Sourcify "
    "exact_match verifiedAt 2026-10-25T03:24:38Z (63 fns: mint/freeMintsLeft/agentRegistry/FREE_MINTS/MAX_SUPPLY/"
    "totalMinted/summon/stake/claim) -> umur >=24 hari, AGE-EXCLUDED. ORE totalSupply 2752, MAX_SUPPLY 10000, "
    "FREE_SUPPLY 6000, freeMinted 2740 (45,7%), mintOpen 1, balanceOf(user) 0. ClafEye totalSupply 7231, MAX_SUPPLY "
    "18000, balanceOf(user) 0, mintedBy(user) 0, costFor(user,1) = 0 (slot user MASIH TERBUKA)."
)

# ---- ClafEye AGE-EXCLUSION REMOVAL (live-verified this run) ----
if "Claf Eye" in snap.get("contracts", {}):
    del snap["contracts"]["Claf Eye"]
    print("REMOVED Claf Eye (age-excluded)")
else:
    print("Claf Eye ALREADY-GONE")
snap["removed0901_claf_eye"] = (
    "AGE-EXCLUDED run 0901: launch <= 2026-11-10T06:46:32Z (Sourcify verifiedAt) + EYE #4720 (hensyah08) + "
    "#710 (ace3) minted free 10 Nov + job early-lead report 10 Nov ~14:31 WIB (totalSupply 611->2730 live) -> "
    "umur >= 7 hari 19 jam (>=24 jam) terverifikasi; live read run ini blok 134230940: totalSupply 7231/18000, "
    "belum sold out. Slot user MASIH TERBUKA (costFor(user,1)=0, balance 0) - user masih bisa mint free eye "
    "sendiri bila mau, tapi item ini tidak lagi dilacak rutin. Dihapus dari snapshot, dilaporkan sekali."
)

# ---- SHENLONG: checked-age-excluded (new to job, triaged this run) ----
snap["contracts"]["SHENLONG"] = {
    "address": "0xd823a14507af2507a670fac4ed08316db7dca553",
    "status": "checked-age-excluded-2026-11-18",
    "name": "SHENLONG",
    "kind": "ERC721",
    "totalSupply": None,
    "totalMinted": 5115,
    "MAX_SUPPLY": 20000,
    "FREE_MINTS": 4,
    "mintPrice": 2000000000000000,
    "balanceOf_user": 0,
    "mintedCount_user": 0,
    "agentRegistry_live": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "firstSeenWib": "2026-11-18 ~08:51 WIB (sensus Boltbook 9dasand72.ai, blok 134.227.249)",
    "source": "boltbook-sensus-2026-11-18",
    "launchNote": "Umur >=24 hari TER VERIFIKASI: Sourcify exact_match verifiedAt 2026-10-25T03:24:38Z -> launch <= 25 Okt. totalMinted 5115/20000 belum sold out -> AGE-EXCLUDED. BUKAN lead, TIDAK di-preview/di-mint.",
    "freePctNote": "FREE_MINTS() = 4 (konstanta); freeMintsLeft() revert (kemungkinan butuh argumen); sensus sebut freeMintsLeft 4 - semantik free pool belum pasti, tapi umur sudah menggugurkan.",
    "lastReadBlock": 134230940,
    "lastReadWib": NOW,
}

# ---- ORE value refresh (already checked-not-early, no tier change) ----
ore = snap["contracts"].get("Ore Raiders SHIP (checked-2026-11-05)")
if isinstance(ore, dict):
    ore["totalSupply"] = 2752
    ore["freeMinted"] = 2740
    ore["lastReadWib"] = NOW
    ore["lastReadBlock"] = 134230940
    ore["runNote0901"] = (
        "Run 0901 (blok 134230940): totalSupply 2752, freeMinted 2740/6000 FREE_SUPPLY = 45,7% (<50%/<70%), "
        "mintOpen 1, balanceOf(user) 0. Dikenal sejak 5 Nov (voucher-gated, tanpa registry ref) -> umur >24h. "
        "Tetap checked-not-early, BUKAN lead/kandidat. DIAM."
    )

snap["last_run"] = (
    "free-mint-search 2026-11-18 09:01 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, "
    "0 track-B dibuka, 0 track-C lead; 1 REMOVAL age-excluded (ClafEye) - dilaporkan sekali; "
    "1 watchlist-only baru (AlphaPulse Genesis Badge V1) - TIDAK dilaporkan sbg lead"
)
snap["runNote0901_1118"] = (
    "Run 0901 (blok re-read 134228447, interval ~30,1 mnt vs 0831): 0 kandidat, 0 strong lead, "
    "0 early lead baru, 0 track-B dibuka, 0 track-C lead. REMOVAL 1x AGE-EXCLUDED: ClafEye (launch <= 10 Nov "
    "13:46 WIB terverifikasi via Sourcify verifiedAt 2026-11-10T06:46:32Z + EYE #4720/#710 minted free 10 Nov + "
    "job early-lead report 10 Nov; live read blok 134230940: totalSupply 7231/18000 belum sold out; slot user "
    "MASIH TERBUKA costFor(user,1)=0) - dihapus dari snapshot, dilaporkan sekali. Scan FAST-FAIL (Ankr 401 ke-50 "
    "berturut-turut main job, elapsed 1,4 dtk, head 134228403; watermark tetap 134086385; gap ~142.018 blok). "
    "Re-read 212 calls, 0 chunk error. Velocity: TIDAK ADA yang lolos (maks +18 <20: Mine Card 1194->1212, "
    "Stromboat totalMinted 249->267; SPARKS +3 rasio 3,33x tapi <20; STOCK +8 0,80x; ARKYN +12 <20; EIM 611->630 "
    "+19 <20; lainnya flat/+0..+3). AgentBubble 85,0% (freeMinted 1888/2222) + Lumenhold 83,5% (freeClaimed "
    "1252/1500) di atas 70% TAPI umur UNVERIFIED - BUKAN strong lead. STOCK AGENT 56,2% (624/1111, freeLeft 487, "
    "slot user terbuka quote 0); Matrix 61,0% (610/1000), AGCLUB 59,3% (527/888) di bawah 70%. PunchCard 23,4% "
    "(1302/5555). HIVE flat 1263, Bubblebruin flat 2620 (freeClaimed 2614/7777=33,6%). THYRK slot user sudah "
    "terpakai. JADE cost user 0,0005 BNB (bukan gratis). CAT402 sold out (100/100). PIXELFROGS mintOpen 0. "
    "DRAGON free pool habis 1000/1000, bal 1. ARKT flat 323/1000, hasClaimed 0. ARKT-claim-62a7 totalSupply 3 flat, "
    "hasClaimed 0. ADRAW freeMinted 307->309 (post junn1 sebut 308/1000), tetap watchlist-only-age-unverified. "
    "bsccat freeMinted 523->524; pepe free pool habis 500/500 + user sudah mint. Sourcify feed top BERUBAH "
    "(verifiedAt 02:04:35Z): 1 baru 0x6E05... (plain ERC-20) -> checked-not-agent-shaped; hot-leg 0859 0x0226/0x8cDe "
    "S1/S2 False. Boltbook EN+ZH (44.332/42.720 byte, HTTP 200): 9+8 alamat, 1 tampak-baru AlphaPulse Badge V1 "
    "0xE09A... (29/10000, mintOpen 1, agentRegistry live = registry) -> DITRIAGE: BUKAN early lead (first mints "
    "tidak terverifikasi run ini; first-seen 17 Nov 13:29), BUKAN kandidat/strong (0,29%, umur + free% UNVERIFIED, "
    "website UNVERIFIED) -> watchlist-only-age-unverified, TIDAK dilaporkan sbg lead, TIDAK di-preview/di-mint. "
    "0xcb3f... = prefix tx hash PEARL (false positive). Sensus 9dasand72.ai: SHENLONG 0xd823... BARU -> AGE-EXCLUDED "
    "(verifiedAt 25 Okt, umur >=24 hari, totalMinted 5115/20000); ORE tetap checked-not-early (45,7%, umur >24h); "
    "RULZ sudah age-excluded-gate-failed; ClafEye -> removal di atas. Sweep EN+ZH: 0 baru (Oathbots 28 Okt "
    "age-excluded, Agentic Gangster 9 Nov free sold out, LeadLoop/NEXUS/AgentForge/AGENTID 25-27 Okt, First-Dollar "
    "Grove 8 Nov, Subsonic Tribe 26 Okt, Laser Agents 25 Okt, AGENT COSMOS 5 Nov, Bitcoin Frogs age-excluded + pool "
    "habis, ORBITA sale CLOSED 1000/1000, UFO window tutup 12 Nov, NEBULA minted-by-user, NOVRA 7 Nov di track_c, "
    "Agent Koi 25 Okt - semuanya berumur >24 jam / pool habis / sudah dikenal). Odaily newsflash (270.886 byte) + "
    "PANews (118.561 byte), keduanya HTTP 200: 0 hit Agent ID/free-mint/free-share. Bridge: 116 kontrak, 0 not in "
    "snapshot, 7 same-owner discarded. binanceai.fun pending claim tetap refund phase (launched 0, failed 1, "
    "isRefundPhase 1, tokenClaimed 0). RigForge belum dibuka (openedAt 0, freeSharesLeft 624, freeClaimed 376)."
)

st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_0901_scan"] = (
    "Run 2026-11-18 09:01 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal "
    "deterministik HTTP 401 Unauthorized (elapsed 1,4 dtk, head 134228403); 401 auth-wide, gagal total ke-50 "
    "berturut-turut main job. Watermark TETAP 134086385; "
    "gap ~142.018 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan). "
    "Tambahan: eth_getLogs publik bsc-dataseed/1/2 'limit exceeded' utk first-mint check E09A (5k-blok range); "
    "BscScan text fetch 403 + live browser Cloudflare bot-wall (Ray ID a5c37e19d8a88166)."
)
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)

json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot updated; contracts:", len(snap["contracts"]))
