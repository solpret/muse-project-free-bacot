#!/usr/bin/env python3
"""Merge run 2026-11-18 23:01 WIB re-read into onchain-snapshot.json (lean merge).
Driver run-2026-11-18-2301.py completed exit 0 in 140.8s (no SIGTERM).
Reread via Quicknode tunnel: 285 calls, 3 chunk errors 429 (calls 215-219,
235-239, 255-259 - rate limit 15/s) - nulls are read failures, never
overwrites. Block 134340498 (prev 2231: 134336331). Interval 30.0 min wall-clock.
Outcome: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU,
0 track-B dibuka, 0 track-C lead BARU. 0 perubahan status.
Boltbook EN+ZH BOTH HTTP 502 (6.402/6.403 byte error page, 0 alamat) - leg
GAGAL transport, BUKAN 0 alamat baru. Sourcify feed OK (20 alamat;
shape-check 20 incl. 11 retry dari hot-leg 2254 - SEMUA berhasil dicek
(2301 fix: carry-forward bypass filter hl_seen), semua S1=false, S2=false,
0 sale-shape; 0xd0bc juga false).
Scan leg FAST-FAIL pre-flight HTTP 401 (Ankr outage sejak 2026-11-09 berlanjut);
watermark TETAP 134086385. Read-only except snapshot. None/err values NEVER overwrite.
New watchlist-only entries (sweep finds, parent-verified on-chain): AgentPepe
(site verified, age UNVERIFIED) + Hivebyte (free 323/2000 = 16,15%, age + website
UNVERIFIED). Neither is a candidate/strong/early lead - snapshot + runlog only.
Notes resolved by contract ADDRESS."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-2301-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-2231-reread.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-18 ~23:01 WIB"
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
    snap["contracts"][key]["runNote2301_1118"] = text

note_by_name("STOCK AGENT", "Run 2301 (blok 134340498, interval ~30 mnt vs 2231): totalSupply 810->813 (+3), freeLeft 301->298 (FREE_SUPPLY 1111, inferred free 813/1111 = 73,2% - INFERENSI totalSupply saja; freeMinted/freeClaimed revert = BUKAN counter terverifikasi, umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. FREE_SUPPLY 1111 + MAX_SUPPLY 2222 + mintOpen 1 + quote_user_1 0 terbaca lagi (null di 2231); freeMintedByWallet(user)=0 (slot terbuka), balanceOf(user)=0. Velocity GAGAL (+3 <20). 70% crossing sudah dilaporkan 18:44 - tidak dilaporkan ulang.")
note_by_name("Lumenhold", "Run 2301: freeClaimed 1259/1500 = 83,9% FLAT, totalSupply 1264 FLAT -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note_by_name("Ledgera", "Run 2301: freeClaimed 2707/5000 = 54,1% FLAT, totalSupply 2714 FLAT -> velocity GAGAL. Umur/website/X UNVERIFIED -> BUKAN kandidat dan BUKAN strong lead (54,1% <70%).")
note_by_name("Vitaliq Scans", "Run 2301: totalSupply err (revert - fungsi tidak ada), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~16 jam, TERVERIFIKASI <24 jam), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note_by_name("HIVE Agents", "Run 2301: totalSupply 1264 FLAT vs 2231, balanceOf(user)=1, minted-by-user. DIAM.")
note_by_name("CAT402", "Run 2301: freeCatsClaimed 100/100 SOLD OUT (sudah diketahui). DIAM.")
note_by_name("Bubblebruin", "Run 2301: totalSupply 2627 FLAT, freeClaimed 2621/7777 = 33,7% -> velocity GAGAL. Minted-by-user, bukan kandidat. DIAM.")
note_by_name("DGF CARD", "Run 2301: totalMinted 1676->1678 (+2) -> velocity GAGAL. freeMinted/mintOpen revert. Tetap EARLY LEAD.")
note_by_name("THE WALL", "Run 2301: totalSupply 5520->5521 (+1) -> velocity GAGAL; free views revert. Bukan kandidat.")
note_by_name("Mine Card", "Run 2301: totalSupply 1387->1388 (+1) -> velocity GAGAL. Bukan kandidat.")
note_by_name("EIM", "Run 2301: totalMinted 800->804 (+4) -> velocity GAGAL (<20). Bukan kandidat.")
note_by_name("AgentNOVA", "Run 2301: totalSupply 804 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("ARKYN", "Run 2301: totalMinted 2300->2303 (+3) -> velocity GAGAL. Bukan kandidat.")
note_by_name("REOPIR", "Run 2301: totalSupply 594->595 (+1), freeClaimed 594->595 -> velocity GAGAL. Bukan kandidat.")
note_by_name("SPARKS", "Run 2301: totalSupply 1216->1217 (+1) -> velocity GAGAL. Bukan kandidat.")
note_by_name("PunchCard", "Run 2301: totalSupply 1361->1362 (+1), freeMinted 1339->1340 -> velocity GAGAL. Bukan kandidat.")
note_by_name("MORFO", "Run 2301: totalMinted 1134 FLAT, mintOpen 1 -> velocity GAGAL. Bukan kandidat.")
note_by_name("PIXELFROGS", "Run 2301: totalSupply 456 FLAT, freeMinted 454, freeLeft 2546, mintOpen 0 -> velocity GAGAL. Bukan kandidat.")
note_by_name("Flare-bd6f", "Run 2301: totalSupply 4900 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("Stromboat", "Run 2301: totalMinted 335 FLAT, freeMinted 335, paidMinted 0 -> velocity GAGAL. Bukan kandidat.")
note_by_name("Compasyn", "Run 2301: totalSupply 1097 FLAT, freeClaimed 1092 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("Kitebots", "Run 2301: totalSupply 1481 FLAT, freeMinted 1481 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("Kryntar", "Run 2301: totalMinted 1378->1384 (+6, MAKS run ini) -> velocity GAGAL (<20). Bukan kandidat.")
note_by_name("Pengu", "Run 2301: totalMinted 139 FLAT, freeMinted 139 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("XCOPY", "Run 2301: totalSupply 464->465 (+1), totalMinted 464->465 -> velocity GAGAL. Bukan kandidat.")
note_by_name("ADRAW", "Run 2301: freeMinted 326 terbaca lagi (null di 2231), balanceOf(user)=0, hasClaimedFree(user)=0; totalSupply err (revert). Bukan kandidat.")
note_by_name("AgentEcho", "Run 2301: totalSupply 415->416 (+1), mintOpen 1, AGENT_ID 552192074493313695968015109214105588393044541999, mintedBy 0, balance 0. Bukan kandidat.")
note_by_name("Abyssora", "Run 2301: totalSupply err (revert - fungsi tidak ada) -> BACA GAGAL, nilai lama dipertahankan. Bukan kandidat.")
note_by_name("Kageveil Genesis", "Run 2301: totalSupply 49 FLAT, normalMinted 49, mintOpen 1, mintClosed 0; balanceOf 0. Bukan kandidat.")
note_by_name("Foundry Faces", "Run 2301: totalMinted 2209 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("ALIEN", "Run 2301: totalSupply 506->508 (+2) -> velocity GAGAL. Bukan kandidat.")
note_by_name("PUNNY", "Run 2301: freeMinted 379/999 = 37,94% FLAT, totalMinted 379 FLAT, mintClosed=1 (age-exclusion sudah dilaporkan 20:34). Tetap EARLY LEAD / bukan kandidat. (Catatan: entri PUNNY sudah dihapus dari snapshot [age-excluded 2031] - note ini miss bila key tidak ada.)")

# ---- AONE track-C: still SOLD OUT (already reported at 2131) ----
aone = snap.setdefault("track_c", {}).get("AONE")
if isinstance(aone, dict):
    aone["freeMinted"] = 10000
    aone["FREE_TOTAL"] = 10000
    aone["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        aone["lastReadBlock"] = BLOCK
    aone["note2301"] = ("Run 2301 (blok 134340498): freeMinted tetap 10000/10000 = FREE POOL SOLD OUT "
        "(sudah dilaporkan sekali di run 2131; kuota user sudah 0 - minted-by-user 18:17 WIB). "
        "Tidak dilaporkan ulang. Entry dipertahankan dengan status minted-by-user.")
    print("AONE updated: still SOLD OUT 10000/10000")
else:
    print("AONE MISSING from track_c!")

# ---- bsccat / PEPE track-C re-reads ----
bs = snap.setdefault("track_c", {}).get("bsccat")
if isinstance(bs, dict):
    fm = reread["bsccat"]["views"].get("freeMinted")
    if isinstance(fm, int):
        bs["freeMinted"] = fm
    bs["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        bs["lastReadBlock"] = BLOCK
    bs["note2301"] = ("Run 2301: freeMinted BACA GAGAL (chunk 429) - nilai lama 539 dipertahankan, "
        "bukan perubahan. Status tetap watchlist-only-age-unverified. Bukan lead/kandidat.")
    print("bsccat updated: freeMinted read FAILED (429), kept 539")
pe = snap.setdefault("track_c", {}).get("PEPE")
if isinstance(pe, dict):
    fm = reread["pepe"].get("freeMinted")
    if isinstance(fm, int):
        pe["freeMinted"] = fm
    pe["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        pe["lastReadBlock"] = BLOCK
    pe["note2301"] = ("Run 2301: freeMinted 500 FLAT; soldShares 501, FREE_SHARES 500, "
        "hasMinted_user 1, minted-by-user-2026-11-16. DIAM.")
    print("PEPE updated: freeMinted 500 FLAT")

# ---- Track-B pending: binanceai.fun (re-read via leg4) ----
bc = snap.setdefault("pending_claims", {}).get("binanceai.fun")
if isinstance(bc, dict):
    bc["lastReadWib"] = NOW
    bc["runNote2301"] = ("Run 2301 (blok 134340498): launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 - tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund 2026-11-02). DIAM.")
    print("binanceai note updated")

# ---- NEW watchlist-only entries (sweep finds, parent-verified on-chain this run) ----
snap["contracts"]["AgentPepe"] = {
    "address": "0xA34C9D34b2Ee93b8059d0ED5302ae595c446423d",
    "status": "watchlist-only-age-unverified-2026-11-18",
    "name": "AgentPepe", "symbol": "APEPE", "kind": "ERC721",
    "totalMinted": 2129, "MAX_SUPPLY": 6666, "mintOpen": 1,
    "balanceOf_user": 0, "userBalance": 0,
    "token": "0x95805acAE9125Caf9E26Bb08ca272e6D9dBc3F9A",
    "claim": "0x49e6bD4C0c7728c947F899F5e21a7A1D3B6e8584",
    "website": "https://agentpepe.fun/",
    "websiteVerified": True,
    "websiteNote": "Parent-verified run 2301: front page HTTP 200 (12.490 byte) mencetak kontrak persis NFT 0xA34C9D34b2Ee93b8059d0ED5302ae595c446423d + token 0x95805acAE9125Caf9E26Bb08ca272e6D9dBc3F9A + claim 0x49e6bD4C0c7728c947F899F5e21a7A1D3B6e8584; /skill.md 404 (bukan sumber bukti). Judul: AGENTPEPE - Every Agent Deserves a Pepe; koleksi 6.666 frog agents.",
    "launchNote": "Launch time UNVERIFIED (tidak ada tanggal di situs/skill.md/pencarian; petunjuk saja: pool $APEPE dibuka 17 Nov -> kemungkinan sudah >24 jam, BUKAN verifikasi; koroborasi first-mint on-chain terblokir: Ankr getLogs 401). Situs menulis MINT IS OPEN tapi counter situs 0 minted - counter situs SALAH/stale, chain: totalMinted 2129.",
    "freePctNote": "Free% UNVERIFIED: totalSupply/freeMinted/freeClaimed/freeLeft/FREE_SUPPLY/mintStart/freeSupply semua revert (view tidak ada di kontrak); totalMinted 2129/6666 = 31,9% dari total cap BUKAN % kuota gratis.",
    "agentShapeNote": "Agent-shape UNVERIFIED: eth_getCode tanpa registry bytes 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; Sourcify belum dicek run ini; skill.md mengklaim mintFree(answer) + gate Agent ID (klaim situs, bukan ABI terverifikasi). BUKAN early lead (tanpa bukti agent-shape).",
    "xVerified": False, "velocityVerified": False, "velocityLegPasses": False,
    "supplyView": "totalMinted", "freePctVerified": None,
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "firstSeen": "run 2301 via sweep (subagent) + parent on-chain verification",
}
snap["contracts"]["Hivebyte"] = {
    "address": "0xaE9d85E78a609f185B4682d87Da12d13B03cf8d8",
    "status": "watchlist-only-age-unverified-2026-11-18",
    "name": "Hivebyte", "symbol": "HIVEBYTE", "kind": "ERC721",
    "totalSupply": 327, "freeClaimed": 323, "FREE_SUPPLY": 2000, "MAX_SUPPLY": 2000,
    "mintOpen": 1, "balanceOf_user": 0, "userBalance": 0,
    "freePctVerified": 16.15,
    "freePctNote": "VERIFIED free counter: freeClaimed 323/2000 = 16,15% (di bawah 50% kandidat dan 70% strong lead).",
    "launchNote": "Launch time UNVERIFIED (tidak dinyatakan di post Boltbook; koroborasi first-mint on-chain terblokir: Ankr getLogs 401). First-seen Boltbook post hari ini blok 134340047 (totalSupply 326/2000 saat itu; parent re-read 327).",
    "websiteNote": "Website UNVERIFIED - tidak ditemukan (sweep + pencarian).",
    "agentShapeNote": "Agent-shape UNVERIFIED: Sourcify UNVERIFIED (sweep); eth_getCode tanpa registry bytes 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; sim mint(1) 0 BNB untuk wallet Agent ID (klaim post Boltbook, bukan bukti ABI). BUKAN early lead (tanpa bukti agent-shape).",
    "xVerified": False, "velocityVerified": False, "velocityLegPasses": False,
    "supplyView": "totalSupply",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "firstSeen": "run 2301 via Boltbook post (sweep subagent) + parent on-chain verification",
}
print("NEW entries added: AgentPepe + Hivebyte (watchlist-only-age-unverified)")

snap["last_run_wib"] = NOW
snap["last_run"] = ("free-mint-search 2026-11-18 23:01 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; "
    "0 perubahan status; STOCK AGENT +3 (inferred 73,2%) - tetap EARLY LEAD; Lumenhold 83,9% FLAT tapi umur UNVERIFIED; "
    "Boltbook EN+ZH GAGAL 502 (leg gagal, bukan 0 baru); Sourcify feed 20 shape-check (incl. 11 retry hot-leg 2254, semua berhasil) 0 sale-shape. "
    "Baru watchlist-only: AgentPepe (situs terverifikasi, umur UNVERIFIED) + Hivebyte (free 16,15%, umur + situs UNVERIFIED). "
    "Sweep: 0 proyek baru terverifikasi <24 jam; YAMA age-excluded (~5 hari), LIFTDAEMON free lane mati, Agentic Gangster free habis.")
snap["runNote2301_1118"] = (
    "Run 2301 (interval ~30 mnt vs 2231; blok 134340498): "
    "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead BARU. "
    "0 perubahan status. "
    "Driver selesai exit 0 dalam 140,8 dtk (tanpa SIGTERM). "
    "Scan leg FAST-FAIL: Ankr pre-flight GAGAL HTTP 401 Unauthorized dalam 1,2 dtk (outage Ankr sejak 2026-11-09 berlanjut); watermark TETAP 134086385; gap ~254.113 blok (head 134340498) dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan). "
    "Reread Quicknode 285 calls, 3 chunk error 429 (calls 215-219, 235-239, 255-259 - rate limit 15/dtk; bsccat freeMinted null, Crown totalSupply/totalMinted null, Velko Rig/Longge sebagian null - nilai lama dipertahankan, BUKAN perubahan; APGB V1 totalSupply/totalMinted 34 terbaca lagi; ADRAW freeMinted 326 terbaca lagi). "
    "Velocity: 0 LOLOS - maks +6 Kryntar, +4 EIM, +3 ARKYN/STOCK AGENT, +2 ALIEN/DGF CARD, +1 belasan kontrak - semua <20 token. "
    "STOCK AGENT totalSupply 810->813 (+3), freeLeft 301->298, inferred free 813/1111 = 73,2% (INFERENSI totalSupply, freeMinted/freeClaimed revert; umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. freeMintedByWallet(user)=0 (slot terbuka), quote 0. "
    "Di atas 70% TAPI umur UNVERIFIED -> BUKAN strong lead: Lumenhold freeClaimed 1259/1500 = 83,9% FLAT. "
    "Ledgera 54,1% FLAT, Bubblebruin 33,7% FLAT, CAT402 sold out 100/100, HIVE 1264 FLAT (minted-by-user), THE WALL 5521 (+1), DGF CARD 1678 (+2). "
    "Vitaliq Scans: genesisStart 07:00 WIB (umur ~16 jam TERVERIFIKASI <24 jam), free%/website UNVERIFIED -> tetap EARLY LEAD. "
    "PUNNY freeMinted 379/999 = 37,94% FLAT, mintClosed=1 (age-exclusion sudah dilaporkan 20:34; entri sudah dihapus dari snapshot). "
    "AONE freeMinted tetap 10000/10000 SOLD OUT (sudah dilaporkan 2131 - tidak dilaporkan ulang). "
    "bsccat freeMinted BACA GAGAL 429 (nilai lama 539 dipertahankan); PEPE freeMinted 500 FLAT (minted-by-user). "
    "Boltbook EN+ZH KEDUANYA HTTP 502 (6.402/6.403 byte error page, 0 alamat) - LEG GAGAL transport, bukan 0 alamat baru; hot-leg 2254 juga EN timeout - Boltbook sedang degradasi. "
    "Sourcify feed OK via tunnel (20 alamat; shape-check 20 incl. 11 retry dari hot-leg 2254 - SEMUA berhasil dicek berkat 2301 fix carry-forward bypass filter hl_seen; semua S1=false, S2=false, 0 sale-shape; 0xd0bc juga false). "
    "Bridge read-only: 116 kontrak, 0 baru, 7 same-owner-discarded - tidak berubah, tanpa promosi/perubahan. "
    "BinanceAI pending: launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, DIAM. "
    "BARU watchlist-only (sweep + verifikasi on-chain parent): AgentPepe 0xA34C9D34b2Ee93b8059d0ED5302ae595c446423d - situs agentpepe.fun TERVERIFIKASI mencetak 3 kontrak persis, totalMinted 2129/6666, mintOpen 1, umur UNVERIFIED + free% UNVERIFIED (semua free view revert) + agent-shape UNVERIFIED (tanpa registry bytes) -> BUKAN lead/kandidat, hanya snapshot + runlog. "
    "Hivebyte 0xaE9d85E78a609f185B4682d87Da12d13B03cf8d8 - totalSupply 327, freeClaimed 323/2000 = 16,15% TERVERIFIKASI, mintOpen 1, umur + situs + agent-shape UNVERIFIED (Sourcify unverified, tanpa registry bytes) -> BUKAN lead/kandidat, hanya snapshot + runlog. "
    "Sweep rute 3/5b/6 (subagent): 0 proyek baru terverifikasi <24 jam; item segar lain unverified (Agent Mint Pass / RONAGENT / MOSSMINDS nama saja, RONIN + DinoAgent lama, PACTA nama saja); YAMA age-excluded (~5 hari, jam ke-121); LIFTDAEMON free lane mati ~19:00 WIB; Agentic Gangster free habis 111/111. "
    "LAPORAN: DIAM (tidak ada kandidat/lead/perubahan baru)."
)
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT SAVED")
