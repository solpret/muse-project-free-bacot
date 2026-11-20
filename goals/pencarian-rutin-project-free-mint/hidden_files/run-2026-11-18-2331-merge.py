#!/usr/bin/env python3
"""Merge run 2026-11-18 23:31 WIB re-read into onchain-snapshot.json (lean merge).
Driver run-2026-11-18-2331.py completed exit 0 in 180.8s (no SIGTERM).
Reread via Quicknode tunnel: 311 calls, 2 chunk errors 429 (calls 75-79 =
PunchCard freeMinted/paidMinted/MAX_SUPPLY/mintOpen/mintPriceFor; calls 215-219 =
Velko Rig quote/mintedBy/balance + Crown totalSupply/totalMinted) - nulls are
read failures, never overwrites. Block 134344503 (prev main 2301: 134340498).
Interval 30.0 min wall-clock vs run 2301.
Outcome: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU,
0 track-B dibuka, 0 track-C lead BARU. 0 perubahan status reportable.
Boltbook EN+ZH HTTP 200 (45.274/43.548 byte, 10 alamat, free_kw 3) - 2 alamat
BARU vs snapshot+seen (0x42c9, 0x9b0c) ditriase run ini; 0x2997 sudah dicek
12 Nov (Sourcify 404); 0x5191 checked-not-sale-shape 23:00; 0xdf6b = alamat
TANPA CODE (bukan kontrak).
Sourcify feed OK (20 alamat; shape-check 8 baru incl. df6b - semua S1=false,
S2=false, 0 sale-shape; 12 sisanya sudah di hl_seen/snapshot).
Scan leg FAST-FAIL pre-flight HTTP 401 (Ankr outage sejak 2026-11-09 berlanjut);
watermark TETAP 134086385. Read-only except snapshot. None/err values NEVER overwrite.
Sweep legs 3/5b/6 (subagent): 0 proyek baru terverifikasi <24 jam; 1 nama segar
UNVERIFIED - Agent Vein ($VEIN, agent-miner-vein.vercel.app, token
0x17ccdcd9763e824a59c78f60c10e6976d5663479, klaim situs free 176/1000) -
verifikasi on-chain parent run ini: core() -> sale 0x869d0edf28cc79b16c1b6f8fb3b399edcbe539f6,
S1 FALSE (tanpa mint/quote/free view, tanpa registry bytes; semua free/quote view
revert), umur UNVERIFIED, gate website sale UNVERIFIED (situs hanya mencetak
token, bukan sale) -> BUKAN lead/kandidat; dicatat track_c checked-not-sale-shape.
Notes resolved by contract ADDRESS."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-2331-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-2301-reread.json"))
triage = json.load(open(f"{HF}/run-2026-11-18-2331-triage.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-18 ~23:31 WIB"
BLOCK = reread.get("block")
INTERVAL_MIN = 30.0
print(f"block {BLOCK} interval {INTERVAL_MIN} min (wall-clock)")
addr2key = {}
for _k, _v in snap.get("contracts", {}).items():
    if isinstance(_v, dict) and isinstance(_v.get("address"), str):
        addr2key[_v["address"].lower()] = _k
updated, missed, vel_pass, deltas = [], [], [], {}
for name, d in reads.items():
    addr = d.get("address", "")
    key = addr2key.get(addr.lower()) if isinstance(addr, str) else None
    if key is None:
        missed.append(name); continue
    e = snap["contracts"][key]
    v = d.get("views", {})
    for f, val in v.items():
        if isinstance(val, int):
            e[f] = val
    pv = prev_reads.get(name, {}).get("views", {})
    fresh = v.get("totalSupply"); pval = pv.get("totalSupply"); view = "totalSupply"
    if not isinstance(fresh, int):
        fresh = v.get("totalMinted"); pval = pv.get("totalMinted"); view = "totalMinted"
    if isinstance(fresh, int) and isinstance(pval, int):
        minted = fresh - pval
        deltas[name] = minted
        rate = minted / INTERVAL_MIN if INTERVAL_MIN > 0 else 0.0
        prev_rate = e.get("currentRatePerMin")
        ratio = (rate / prev_rate) if isinstance(prev_rate, (int, float)) and prev_rate else None
        vel = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        if vel:
            vel_pass.append((name, minted, round(rate, 4), round(ratio, 2)))
        e["previousTotalSupply"] = pval; e["mintedInInterval"] = minted
        e["intervalMinutes"] = round(INTERVAL_MIN, 1)
        e["currentRatePerMin"] = round(rate, 4); e["previousRatePerMin"] = prev_rate
        e["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        e["velocityLegPasses"] = vel; e["supplyView"] = view
    e["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        e["lastReadBlock"] = BLOCK
    updated.append((name, key))
print(f"updated {len(updated)} entries; missed (not in snapshot): {missed}")
print("velocity PASS:", vel_pass)
print("deltas:", dict(sorted(deltas.items(), key=lambda kv: -kv[1])[:12]))

def note_by_name(plan_name, text):
    d = reads.get(plan_name)
    if not d:
        print("NOTE MISS (no read)", plan_name); return
    key = addr2key.get(d.get("address", "").lower())
    if key is None:
        print("NOTE MISS (no snapshot key)", plan_name); return
    snap["contracts"][key]["runNote2331_1118"] = text

note_by_name("STOCK AGENT", "Run 2331 (blok 134344503, interval ~30 mnt vs 2301): totalSupply 813->815 (+2), freeLeft 298->296 (FREE_SUPPLY 1111, inferred free 815/1111 = 73,4% - INFERENSI totalSupply saja; freeMinted/freeClaimed revert = BUKAN counter terverifikasi, umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. mintOpen 1, quote_user_1 0, freeMintedByWallet(user)=0 (slot terbuka), balanceOf(user)=0. Velocity GAGAL (+2 <20).")
note_by_name("Lumenhold", "Run 2331: freeClaimed 1259/1500 = 83,9% FLAT, totalSupply 1264 FLAT -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note_by_name("Ledgera", "Run 2331: freeClaimed 2707/5000 = 54,1% FLAT, totalSupply 2714 FLAT -> velocity GAGAL. Umur/website/X UNVERIFIED -> BUKAN kandidat dan BUKAN strong lead (54,1% <70%).")
note_by_name("Vitaliq Scans", "Run 2331: totalSupply err (revert - fungsi tidak ada), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~16,5 jam, TERVERIFIKASI <24 jam; deadline age-exclusion ~07:00 WIB 19 Nov), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note_by_name("HIVE Agents", "Run 2331: totalSupply 1264 FLAT vs 2301, balanceOf(user)=1, minted-by-user. DIAM.")
note_by_name("CAT402", "Run 2331: freeCatsClaimed 100/100 SOLD OUT (sudah diketahui). DIAM.")
note_by_name("Bubblebruin", "Run 2331: totalSupply 2627 FLAT, freeClaimed 2621/7777 = 33,7% -> velocity GAGAL. Minted-by-user, bukan kandidat. DIAM.")
note_by_name("DGF CARD", "Run 2331: totalMinted 1678->1680 (+2) -> velocity GAGAL. freeMinted/mintOpen revert. Tetap EARLY LEAD.")
note_by_name("THE WALL", "Run 2331: totalSupply 5521->5525 (+4) -> velocity GAGAL; free views revert. Bukan kandidat.")
note_by_name("Mine Card", "Run 2331: totalSupply/totalMinted 1388->1390 (+2) -> velocity GAGAL. Bukan kandidat.")
note_by_name("EIM", "Run 2331: totalMinted 804->807 (+3) -> velocity GAGAL (<20). Bukan kandidat.")
note_by_name("AgentNOVA", "Run 2331: totalSupply 804->809 (+5) -> velocity GAGAL. Bukan kandidat.")
note_by_name("ARKYN", "Run 2331: totalMinted 2303->2306 (+3) -> velocity GAGAL. Bukan kandidat.")
note_by_name("REOPIR", "Run 2331: totalSupply/freeClaimed 595->598 (+3) -> velocity GAGAL. Bukan kandidat.")
note_by_name("Compasyn", "Run 2331: totalSupply 1097->1103 (+6, MAKS run ini), freeClaimed 1092->1098 -> velocity GAGAL (<20). Bukan kandidat.")
note_by_name("PunchCard", "Run 2331: totalSupply 1362 FLAT; freeMinted/paidMinted/MAX_SUPPLY/mintOpen/mintPriceFor BACA GAGAL (chunk 429 calls 75-79) - nilai lama dipertahankan, BUKAN perubahan. Velocity GAGAL. Bukan kandidat.")
note_by_name("MORFO", "Run 2331: totalMinted 1134->1135 (+1) -> velocity GAGAL. Bukan kandidat.")
note_by_name("PIXELFROGS", "Run 2331: totalSupply 456 FLAT, freeMinted 454, freeLeft 2546, mintOpen 0 -> velocity GAGAL. Bukan kandidat.")
note_by_name("Flare-bd6f", "Run 2331: totalSupply 4900 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("Stromboat", "Run 2331: totalMinted 335 FLAT, freeMinted 335, paidMinted 0 -> velocity GAGAL. Bukan kandidat.")
note_by_name("Kitebots", "Run 2331: totalSupply 1481 FLAT, freeMinted 1481 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("Kryntar", "Run 2331: totalMinted 1384 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("Pengu", "Run 2331: totalMinted 139 FLAT, freeMinted 139 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("XCOPY", "Run 2331: totalSupply/totalMinted 465 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("ADRAW", "Run 2331: freeMinted 326 FLAT, balanceOf(user)=0, hasClaimedFree(user)=0; totalSupply err (revert). Bukan kandidat.")
note_by_name("AgentEcho", "Run 2331: totalSupply 416->417 (+1), mintOpen 1, AGENT_ID 552192074493313695968015109214105588393044541999, mintedBy 0, balance 0. Bukan kandidat.")
note_by_name("Abyssora", "Run 2331: totalSupply err (revert - fungsi tidak ada) -> BACA GAGAL, nilai lama dipertahankan. Bukan kandidat.")
note_by_name("Kageveil Genesis", "Run 2331: totalSupply 49 FLAT, normalMinted 49, mintOpen 1, mintClosed 0; balanceOf 0. Bukan kandidat.")
note_by_name("Foundry Faces", "Run 2331: totalMinted 2209->2211 (+2) -> velocity GAGAL. Bukan kandidat.")
note_by_name("ALIEN", "Run 2331: totalSupply 508 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("AgentPepe", "Run 2331 (pertama di PLAN re-read): totalMinted 2129->2131 (+2), mintOpen 1, balanceOf(user)=0. Umur + free% + agent-shape tetap UNVERIFIED -> tetap watchlist-only-age-unverified, BUKAN lead/kandidat.")
note_by_name("Hivebyte", "Run 2331 (pertama di PLAN re-read): totalSupply 327->332 (+5), freeClaimed 323->328/2000 = 16,4% TERVERIFIKASI, mintOpen 1, balanceOf(user)=0. Umur + situs + agent-shape tetap UNVERIFIED -> tetap watchlist-only-age-unverified, BUKAN lead/kandidat.")
note_by_name("E5F8", "Run 2331: PERUBAHAN NON-REPORTABLE - mintOpen 0 -> 1 (terbuka), TAPI totalMinted tetap 1 (hanya owner test mint, tanpa public mint baru), totalSupply revert, MAX_SUPPLY 3333, balanceOf(user)=0. Status diubah watchlist-only-mint-open-no-public-mint-2026-11-18. Umur/free%/website tetap UNVERIFIED -> BUKAN lead/kandidat; bukan tipe perubahan reportable (sellout/slot-loss/age-exclusion/claim-open).")
note_by_name("ARKT-8334", "Run 2331: PERUBAHAN NON-REPORTABLE - totalSupply/totalMinted 0 -> 2 (FIRST MINTS terverifikasi on-chain run ini), mintOpen revert, balanceOf(user)=0. Agent-shape UNVERIFIED: Sourcify 36 fns (agentId/claim/hasClaimed/mintedTo/setAgentId, verifiedAt 2026-11-18T07:44:51Z) TAPI tanpa registry bytes 0x60B926... di code, tanpa AgentGate, tanpa free-mint fn/free-supply constant (kontrak claim + claimSigner EIP-712, bukan free-mint) -> BUKAN early lead. Status diubah watchlist-only-first-mints-2026-11-18.")
note_by_name("PUNNY", "Run 2331: freeMinted 379/999 = 37,94% FLAT, totalMinted 379 FLAT, mintClosed=1 (age-exclusion sudah dilaporkan 20:34; entri sudah dihapus dari snapshot - note ini miss bila key tidak ada).")

# ---- E5F8 / ARKT-8334 status updates ----
e5 = snap["contracts"].get("E5F8-0xe5f8")
if isinstance(e5, dict):
    e5["status"] = "watchlist-only-mint-open-no-public-mint-2026-11-18"
    e5["mintOpen"] = 1
    print("E5F8 status updated: mintOpen 0->1, totalMinted still 1")
a8334 = snap["contracts"].get("ARKT-8334")
if isinstance(a8334, dict):
    a8334["status"] = "watchlist-only-first-mints-2026-11-18"
    a8334["totalSupply"] = 2
    a8334["totalMinted"] = 2
    a8334["agentShapeNote"] = ("Run 2331: agent-shape UNVERIFIED - Sourcify 36 fns incl agentId/claim/"
        "hasClaimed/mintedTo/setAgentId (verifiedAt 2026-11-18T07:44:51Z) TAPI tanpa registry bytes "
        "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F di code, tanpa AgentGate, tanpa free-mint fn/free-supply "
        "constant (kontrak claim + claimSigner EIP-712). First mints 0->2 terverifikasi run ini. BUKAN early lead.")
    print("ARKT-8334 status updated: first mints 0->2, agent-shape unverified")

# ---- AONE track-C: still SOLD OUT (already reported at 2131) ----
aone = snap.setdefault("track_c", {}).get("AONE")
if isinstance(aone, dict):
    aone["freeMinted"] = 10000
    aone["FREE_TOTAL"] = 10000
    aone["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        aone["lastReadBlock"] = BLOCK
    aone["note2331"] = ("Run 2331 (blok 134344503): freeMinted tetap 10000/10000 = FREE POOL SOLD OUT "
        "(sudah dilaporkan sekali di run 2131; kuota user sudah 0 - minted-by-user 18:17 WIB). "
        "Tidak dilaporkan ulang. Entry dipertahankan dengan status minted-by-user.")
    print("AONE updated: still SOLD OUT 10000/10000")
else:
    print("AONE MISSING from track_c!")

# ---- RigForge track-C: still not open ----
rf = snap.setdefault("track_c", {}).get("RigForge")
if isinstance(rf, dict):
    rf["freeSharesLeft"] = 621
    rf["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        rf["lastReadBlock"] = BLOCK
    rf["note2331"] = ("Run 2331 (blok 134344503): freeSharesLeft 621 (turun dari 637 di run 1631), "
        "openedAt tetap 0 (belum buka), freeClaimed 379. Tetap belum buka; bukan lead/kandidat.")
    print("RigForge updated: freeSharesLeft 621, openedAt 0")

# ---- bsccat / PEPE track-C re-reads ----
bs = snap.setdefault("track_c", {}).get("bsccat")
if isinstance(bs, dict):
    fm = reread["bsccat"]["views"].get("freeMinted")
    if isinstance(fm, int):
        bs["freeMinted"] = fm
    bs["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        bs["lastReadBlock"] = BLOCK
    bs["note2331"] = ("Run 2331: freeMinted 545 (539 di 2301 saat baca gagal 429; 544 di hot-leg 2309) - "
        "naik +1, status tetap watchlist-only-age-unverified. Bukan lead/kandidat.")
    print("bsccat updated: freeMinted 545")
pe = snap.setdefault("track_c", {}).get("PEPE")
if isinstance(pe, dict):
    fm = reread["pepe"].get("freeMinted")
    if isinstance(fm, int):
        pe["freeMinted"] = fm
    pe["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        pe["lastReadBlock"] = BLOCK
    pe["note2331"] = ("Run 2331: freeMinted 500 FLAT; soldShares 501, FREE_SHARES 500, "
        "hasMinted_user 1, minted-by-user-2026-11-16. DIAM.")
    print("PEPE updated: freeMinted 500 FLAT")

# ---- Track-B pending: binanceai.fun (re-read via leg4) ----
bc = snap.setdefault("pending_claims", {}).get("binanceai.fun")
if isinstance(bc, dict):
    bc["lastReadWib"] = NOW
    bc["runNote2331"] = ("Run 2331 (blok 134344503): launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 - tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund 2026-11-02). DIAM.")
    print("binanceai note updated")

# ---- NEW entries this run (triage, snapshot + runlog only, NO chat report) ----
snap["contracts"]["Boltbook-0x42c9"] = {
    "address": "0x42c9ed912025df33ca1676aad4651cdded3f09ed",
    "status": "watchlist-only-age-unverified-2026-11-18",
    "kind": "ERC721",
    "totalMinted": 258, "mintOpen": 1, "balanceOf_user": 0, "userBalance": 0,
    "launchNote": "Launch time UNVERIFIED (tidak dinyatakan di post Boltbook; koroborasi first-mint on-chain terblokir: Ankr getLogs 401; Sourcify verifiedAt 2026-11-18T11:26:08Z BUKAN launch time). First-seen Boltbook front page run 2331 (juga di hot-leg 2314; ABSENT dari hot-leg-seen.json - hot-leg '0 new' terlewat).",
    "freePctNote": "Free% UNVERIFIED: totalSupply/freeMinted/freeClaimed/FREE_SUPPLY/MAX_SUPPLY semua revert (view tidak ada di kontrak); totalMinted 258 BUKAN % kuota gratis.",
    "agentShapeNote": "Agent-shape SEBAGIAN: Sourcify verified 26 fns incl agentID/hasAgentID/hasClaimed/claimed/mint/mintOpen/totalMinted/metadataURI/maxSupply; TAPI tanpa registry bytes 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F di code (11.386 byte) dan tanpa free view. First mints BUKAN run ini (totalMinted sudah 258) -> BUKAN early lead. Website/X UNVERIFIED.",
    "websiteNote": "Website UNVERIFIED - tidak ditemukan run ini.",
    "xVerified": False, "velocityVerified": False, "velocityLegPasses": False,
    "supplyView": "totalMinted", "freePctVerified": None,
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "firstSeen": "run 2331 via Boltbook front page EN+ZH + parent on-chain triage",
}
snap["contracts"]["checked-0x9b0c-2331"] = {
    "address": "0x9b0c237a123277fcf8768550bbdd7767c73cf5d3",
    "status": "checked-not-agent-shaped-2026-11-18",
    "kind": "ERC721",
    "totalSupply": 22864, "totalMinted": 22864, "balanceOf_user": 2, "userBalance": 2,
    "launchNote": "First-seen Boltbook front page run 2331 (juga di hot-leg 2314; ABSENT dari hot-leg-seen.json). Sourcify verifiedAt 2026-11-18T11:00:17Z (BUKAN launch time).",
    "agentShapeNote": "BUKAN agent-shaped: Sourcify verified 20 fns (arena/forge/forgeCards/website/tokenURI/totalMinted/totalSupply) - tanpa registry bytes, tanpa fungsi agent/registry/AgentGate, tanpa free-mint fn/free view. SUDAH DIMILIKI user (balanceOf=2) -> excluded anyway. Fungsi website() di ABI belum dibaca (di luar scope - bukan agent-shaped).",
    "websiteNote": "Website UNVERIFIED (fungsi website() ada di ABI, belum dibaca - bukan kandidat).",
    "xVerified": False, "velocityVerified": False, "velocityLegPasses": False,
    "supplyView": "totalSupply", "freePctVerified": None,
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "firstSeen": "run 2331 via Boltbook front page EN+ZH + parent on-chain triage",
}
snap["contracts"]["checked-0xdf6b-2331"] = {
    "address": "0xdf6bede5287207e3def3dcbe142e202e2c0d5645",
    "status": "checked-not-a-contract-2026-11-18",
    "totalSupply": None,
    "launchNote": "Alamat tercetak di front page Boltbook EN+ZH (run 2314 + 2331) TAPI eth_getCode = 0x (TANPA CODE - bukan kontrak, semua eth_call mengembalikan 0x); Sourcify tanpa ABI (n_fns 0, verifiedAt null); shape S1/S2 false. BUKAN kontrak mint - kemungkinan alamat wallet di postingan, bukan proyek.",
    "agentShapeNote": "BUKAN agent-shaped (bukan kontrak).",
    "websiteNote": "Website UNVERIFIED - tidak ada kontrak untuk di-gate.",
    "xVerified": False, "velocityVerified": False, "velocityLegPasses": False,
    "supplyView": None, "freePctVerified": None,
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "firstSeen": "run 2331 via Boltbook front page EN+ZH + parent on-chain triage (eth_getCode)",
}
print("NEW entries added: Boltbook-0x42c9 (watchlist-only) + checked-0x9b0c (not-agent-shaped) + checked-0xdf6b (not-a-contract)")

# ---- Agent Vein track-C: checked, NOT sale-shape ----
snap.setdefault("track_c", {})["Agent Vein"] = {
    "address": "0x869d0edf28cc79b16c1b6f8fb3b399edcbe539f6",
    "token": "0x17ccdcd9763e824a59c78f60c10e6976d5663479",
    "status": "checked-not-sale-shape-2026-11-18",
    "website": "https://agent-miner-vein.vercel.app",
    "websiteNote": "Situs dibaca subagent sweep 23:35 WIB: mencetak TOKEN 0x17ccdcd9763e824a59c78f60c10e6976d5663479; alamat SALE 0x869d0edf28cc79b16c1b6f8fb3b399edcbe539f6 TIDAK tercetak di situs (/skill.md + /llms.txt dibaca) -> gate website untuk SALE UNVERIFIED.",
    "saleShapeNote": ("Run 2331 parent on-chain: token.core() -> sale 0x869d0edf28cc79b16c1b6f8fb3b399edcbe539f6 "
        "(code 2.230 byte, tanpa registry bytes); Sourcify verified TAPI n_fns 0 (verifiedAt 2026-11-11T04:19:23Z, tanpa ABI); "
        "semua view sale revert (freeSharesRemaining/FREE_SHARES_TOTAL/freeShareClaimedBy/quote) -> S1 FALSE "
        "(tanpa mint/quote/free view, tanpa agent_ref). BUKAN sale-shape terverifikasi."),
    "launchNote": ("Launch time UNVERIFIED: situs tidak menyatakan tanggal; snapshot situs bergerak 0/1.000 "
        "(COMING SOON) -> 6/1.000 LIVE -> 176/1.000 LIVE pada 23:35 WIB (klaim situs: 1 share gratis/wallet "
        "Agent ID, 5.000 VEIN/share, 0/40.000 share berbayar) - fase gratis BARU dibuka tapi umur <24 jam "
        "tidak bisa dibuktikan; koroborasi first-mint on-chain terblokir (Ankr 401)."),
    "xVerified": False, "velocityVerified": False,
    "freePctVerified": None,
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "firstSeen": "run 2331 via sweep subagent (site) + parent on-chain verification (core()->sale)",
}
print("Agent Vein added to track_c as checked-not-sale-shape")

snap["last_run_wib"] = NOW
snap["last_run"] = ("free-mint-search 2026-11-18 23:31 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; "
    "0 perubahan status reportable; velocity 0 LOLOS (maks +6 Compasyn). STOCK AGENT +2 (inferred 73,4%) - tetap EARLY LEAD; "
    "Lumenhold 83,9% FLAT tapi umur UNVERIFIED; Vitaliq umur ~16,5 jam terverifikasi <24 jam (deadline ~07:00 WIB 19 Nov). "
    "Boltbook EN+ZH OK 200 (10 alamat); 2 alamat baru ditriase (0x42c9 watchlist-only, 0x9b0c bukan agent-shaped, user sudah pegang 2); "
    "0xdf6b TANPA CODE (bukan kontrak). Sourcify feed 20, shape-check 8 baru, 0 sale-shape. "
    "Perubahan non-reportable: E5F8 mintOpen 0->1 (totalMinted tetap 1, tanpa public mint); ARKT-8334 first mints 0->2 (agent-shape unverified). "
    "Agent Vein (sweep): sale-shape GAGAL (S1 false, semua view revert), umur + gate sale UNVERIFIED -> dicatat track_c, BUKAN lead. "
    "Sweep: 0 proyek baru terverifikasi <24 jam; YAMA age-excluded, LIFTDAEMON free lane mati, Agentic Gangster free habis. "
    "Scan leg FAST-FAIL Ankr 401; watermark TETAP 134086385.")
snap["runNote2331_1118"] = (
    "Run 2331 (interval ~30 mnt vs 2301; blok 134344503): "
    "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead BARU. "
    "0 perubahan status reportable. "
    "Driver selesai exit 0 dalam 180,8 dtk (tanpa SIGTERM). "
    "Scan leg FAST-FAIL: Ankr pre-flight GAGAL HTTP 401 Unauthorized dalam 6,9 dtk (outage Ankr sejak 2026-11-09 berlanjut); watermark TETAP 134086385; gap ~258.118 blok (head 134344503) dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan). "
    "Reread Quicknode 311 calls, 2 chunk error 429 (calls 75-79 = PunchCard freeMinted/paidMinted/MAX_SUPPLY/mintOpen/mintPriceFor null; calls 215-219 = Velko Rig quote/mintedBy/balance + Crown totalSupply/totalMinted null - nilai lama dipertahankan, BUKAN perubahan). "
    "Velocity: 0 LOLOS - maks +6 Compasyn, +5 AgentNOVA, +4 THE WALL, +3 REOPIR/ARKYN/EIM, +2 Matrix/Mine Card/STOCK AGENT/Foundry Faces/DGF CARD, +1 AGCLUB/MORFO - semua <20 token. "
    "STOCK AGENT totalSupply 813->815 (+2), freeLeft 298->296, inferred free 815/1111 = 73,4% (INFERENSI totalSupply, freeMinted/freeClaimed revert; umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. "
    "Di atas 70% TAPI umur UNVERIFIED -> BUKAN strong lead: Lumenhold freeClaimed 1259/1500 = 83,9% FLAT. "
    "Ledgera 54,1% FLAT, Bubblebruin 33,7% FLAT, CAT402 sold out 100/100, HIVE 1264 FLAT (minted-by-user), THE WALL 5525 (+4), DGF CARD 1680 (+2), THYRK freeMinted 4318/7777 = 55,5% (<70%). "
    "Vitaliq Scans: genesisStart 07:00 WIB (umur ~16,5 jam TERVERIFIKASI <24 jam; deadline age-exclusion ~07:00 WIB 19 Nov), free%/website UNVERIFIED -> tetap EARLY LEAD. "
    "AONE freeMinted tetap 10000/10000 SOLD OUT (sudah dilaporkan 2131 - tidak dilaporkan ulang). RigForge freeSharesLeft 621, openedAt tetap 0 (belum buka). "
    "bsccat freeMinted 545 (+1 vs hot-leg 2309); PEPE freeMinted 500 FLAT (minted-by-user). "
    "Boltbook EN+ZH HTTP 200 (45.274/43.548 byte, 10 alamat, free_kw 3) - leg OK kembali sesudah 502 di 2301. 2 alamat BARU vs snapshot+seen ditriase parent on-chain: 0x42c9 (totalMinted 258, mintOpen 1, agentID/hasAgentID ada, tanpa registry bytes, tanpa free view, umur+free% UNVERIFIED -> watchlist-only-age-unverified, BUKAN early lead karena first mint bukan run ini); 0x9b0c (totalSupply 22864, 20 fns arena/forge/website, tanpa agent/free view -> BUKAN agent-shaped; user SUDAH pegang 2 -> excluded). 0x2997 sudah dicek 12 Nov (Sourcify 404); 0x5191 checked-not-sale-shape 23:00. 0xdf6b = TANPA CODE (eth_getCode 0x, bukan kontrak; Sourcify n_fns 0) -> checked-not-a-contract. "
    "Sourcify feed OK via tunnel (20 alamat; shape-check 8 baru incl. df6b - semua S1=false, S2=false, 0 sale-shape; 0xdCa8 agent_ref=true tapi tanpa mint/quote/free view). "
    "Perubahan NON-REPORTABLE (snapshot + runlog saja): E5F8 mintOpen 0->1, totalMinted tetap 1 (hanya owner test mint, tanpa public mint baru); ARKT-8334 totalSupply/totalMinted 0->2 (first mints terverifikasi) TAPI agent-shape UNVERIFIED (Sourcify 36 fns agentId/claim, tanpa registry bytes, tanpa free view; kontrak claim EIP-712) -> BUKAN early lead. "
    "Agent Vein (nama segar dari sweep subagent): token 0x17ccdcd9763e824a59c78f60c10e6976d5663479, situs agent-miner-vein.vercel.app (klaim free 176/1000 LIVE); verifikasi on-chain parent: core() -> sale 0x869d0edf28cc79b16c1b6f8fb3b399edcbe539f6, S1 FALSE (code 2.230 byte, tanpa registry bytes; Sourcify n_fns 0; semua free/quote view revert), umur UNVERIFIED, gate website sale UNVERIFIED (situs hanya mencetak token) -> BUKAN lead/kandidat; dicatat track_c checked-not-sale-shape. "
    "Bridge read-only: 116 kontrak, 0 baru, 7 same-owner-discarded - tidak berubah, tanpa promosi/perubahan. "
    "BinanceAI pending: launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, DIAM. "
    "Sweep rute 3/5b/6 (subagent): 0 proyek baru terverifikasi <24 jam; Binance Square tanpa post baru ~1 jam; Odaily-PANews tanpa item Agent ID/free-mint; DappBay tanpa listing Agent Vein (absen bukan bukti). "
    "LAPORAN: DIAM (tidak ada kandidat/lead/perubahan reportable baru)."
)
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT SAVED")
