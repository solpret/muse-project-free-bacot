#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 17:31 WIB into onchain-snapshot.json.
Main re-read ~17:33-17:41 WIB (51 kontrak, 370 eth_call, 277 errors - degradasi
RPC bsc-dataseed berat, nilai lama dipertahankan; blok merge 134680776).
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama;
lastReadBlock/Wib hanya di-update bila new_supply terbaca (bukan None).
Read-only kecuali snapshot + scan-state note.
Temuan run ini: velocity LOLOS 1 (Stromboat totalMinted 481->668, +187,
6.6786/mnt vs prev 3.375 = 1.98x) TAPI free% UNVERIFIED + umur UNVERIFIED +
website gate SUDAH GAGAL -> BUKAN kandidat/strong lead, DIAM; STOCK AGENT
943 (84.9%) + Lumenhold 1281/1500 (85.4%) tetap bukan strong lead (umur/website
UNVERIFIED); Turtle/Lion GAGAL baca run ini (transport), baseline dipertahankan
(44/88 = 50.0%, 42/88 = 47.7%); AgentBadge-ABDG 652->664 (+12, 1.96x tapi <20
token) GAGAL; AgentDrop +2 (2.15x tapi <20) GAGAL; ONI 208 FLAT; HIVE GAGAL
baca (baseline 1267); binanceai TERBACA run ini: launched=0, failed=1,
isRefundPhase=1, totalShares 3110 - tetap pending/refund, sudah dilaporkan
sekali (2026-11-02). DIAM.
BARU: Pocket Ai 0xf9D00B7a2992de00EBc5F9f04BAf95d44C542102 (sweep rute 3/6) -
Sourcify verified, agent-shaped (AGENT_REGISTRY = registry, mintFree/mintPaid,
FREE_PRICE 0, MAX_FREE_PER_WALLET 1), totalMinted 2950/5555, slot user TERBUKA
(freeMintedBy=0), situs https://pocket.agenticwallet.workers.dev/ mencetak
kontrak NFT + token persis; umur launch UNVERIFIED + free% UNVERIFIED (tidak
ada free counter di ABI) + tanpa bukti diskusi X -> watchlist-only-age-unverified,
BUKAN early lead (bukan first-seen minting), BUKAN kandidat/strong lead. DIAM.
agentGTA Arms: belum launch, tanpa alamat kontrak -> run log saja.
Sourcify 4 baru, 0 shape hit. Boltbook EN 45.015 byte (7 alamat) + ZH 43.302
byte (6 alamat), 0 baru. Bridge 0 baru (116/116 in snapshot, 7 same-owner-discarded).
Sweep EN/ZH + Square + Odaily + PANews: tanpa proyek baru <24 jam terkonfirmasi.
Pre-flight Ankr 401 (sejak 9 Nov) - scan leg fast-fail, watermark TETAP
134086385, gap ~590.000+ blok. Track-C 5c: tanpa output scan baru.
TIDAK ada lead/kandidat/eksekusi baru - DIAM."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~17:43 WIB"
BLOCK = 134680776
reread = json.load(open(BASE + "run-2026-11-20-1731-reread.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1731")
snap = json.load(open(BASE + "onchain-snapshot.json"))
interim = json.load(open(BASE + "run-2026-11-20-1731-interim.json"))
vel = interim["velocity"]
def num(d, k):
    x = d.get(k)
    return x if isinstance(x, int) else None
by_addr = {}
for k, v in snap.get("contracts", {}).items():
    if isinstance(v, dict) and isinstance(v.get("address"), str):
        by_addr[v["address"].lower()] = (k, v)
n_upd = 0
n_null = 0
for name, v in vel.items():
    addr = v["address"].lower()
    if addr not in by_addr:
        continue
    sk, sv = by_addr[addr]
    old_sup = v["old_supply"]
    new_sup = v["new_supply"]
    if new_sup is None:
        sv["runNote1731_1120"] = (
            f"Run 1731 (blok ~{BLOCK}): baca GAGAL (transport-degraded, nilai lama "
            f"({old_sup}) dipertahankan, velocity TIDAK dihitung; bukan kandidat/strong lead. DIAM.")
        n_null += 1
        continue
    sv["previousTotalSupply"] = old_sup
    sv["totalSupply"] = new_sup
    if v["delta"] is not None:
        sv["mintedInInterval"] = v["delta"]
        sv["intervalMinutes"] = v["minutes"]
        sv["currentRatePerMin"] = v["rate_per_min"]
    sv["velocityLegPasses"] = bool(v["velocity_pass"])
    if v["free_pct"] is not None:
        sv["freePctInference"] = v["free_pct"]
    sv["lastReadBlock"] = BLOCK
    sv["lastReadWib"] = NOW_WIB
    sv["runNote1731_1120"] = (
        f"Run 1731 (blok ~{BLOCK}, interval ~{v['minutes']} mnt): "
        f"totalSupply {old_sup}->{new_sup} (+{v['delta']}, {v['rate_per_min']}/mnt vs prev {v['prev_rate_per_min']} = {v['ratio']}x) -> velocity "
        f"{'LOLOS' if v['velocity_pass'] else 'GAGAL'}; free% {v['free_pct']}; bal_user {v['balanceOf_user']}; "
        f"status {sv.get('status')}. DIAM.")
    n_upd += 1
# ONI: totalMinted dari reread run ini (208 FLAT vs 1701)
oni = snap.get("contracts", {}).get("ONI", {})
oni_v = reread["reads"].get("ONI", {}).get("views", {})
if oni and num(oni_v, "totalMinted") is not None:
    oni["totalMinted"] = num(oni_v, "totalMinted")
    oni["lastReadBlock"] = BLOCK
    oni["lastReadWib"] = NOW_WIB
    oni["runNote1731_1120"] = (
        f"Run 1731 (blok ~{BLOCK}): totalMinted {oni['totalMinted']} (FLAT vs 1701); "
        f"balanceOf(user)={num(oni_v, 'balanceOf_user')}; free views revert - free% tetap inferensi; "
        f"bukan strong lead/kandidat - baseline tracking saja. DIAM.")
# AgentBadge-ABDG: totalMinted 652->664 (+12) run ini
ab = snap.get("contracts", {}).get("AgentBadge-ABDG", {})
if ab:
    ab["totalMinted"] = 664
    ab["freePctInference"] = round(100 * 664 / 3333, 1)
    ab["lastReadBlock"] = BLOCK
    ab["lastReadWib"] = NOW_WIB
    ab["runNote1731_1120"] = (
        "Run 1731 (blok 134680776, interval ~28 mnt vs run 1701): "
        "totalMinted 652->664 (+12, 0.4286/mnt vs baseline 0.2188/mnt = 1.96x, tapi <20 token) -> velocity GAGAL; "
        "free 664/3333 = 19.9% (<50% dan <70%); balanceOf(user)=0; umur launch tetap UNVERIFIED; "
        "status watchlist-only-age-unverified-2026-11-20. DIAM; tetap di reread set run berikut.")
# Stromboat: velocity LOLOS (+187, 1.98x) tapi BUKAN kandidat/strong lead
sb = snap.get("contracts", {}).get("Stromboat", {})
if sb:
    sb["totalMinted"] = 668
    sb["previousTotalSupply"] = 481
    sb["mintedInInterval"] = 187
    sb["intervalMinutes"] = 28.0
    sb["currentRatePerMin"] = 6.6786
    sb["velocityLegPasses"] = True
    sb["lastReadBlock"] = BLOCK
    sb["lastReadWib"] = NOW_WIB
    sb["runNote1731_1120"] = (
        "Run 1731 (blok 134680776, interval ~28 mnt vs run 1701): totalMinted 481->668 (+187, 6.6786/mnt vs prev 3.375 = 1.98x, >=20 token) "
        "-> velocity LOLOS, TAPI free% UNVERIFIED run ini (freeMinted/FREE_SUPPLY/freeSupply view null/revert; terakhir freeMinted 367/667) + "
        "umur launch UNVERIFIED + website gate SUDAH GAGAL (metode A, tanpa situs proyek) -> BUKAN kandidat (butuh free% >=50% + umur <24 jam "
        "terverifikasi + diskusi X + website) dan BUKAN strong lead (free% >70% tak terverifikasi). Catatan: totalMinted 668 kini MELEBIHI "
        "FREE_SUPPLY terakhir 667 - kemungkinan ada paid mint di antaranya, bukan vonis free pool habis (free counter tak terbaca). "
        "Tidak ada promosi, tidak ada preview/mint. DIAM.")
# binanceai pending claim: TERBACA run ini (launched=0, failed=1, isRefundPhase=1)
pc = snap.get("pending_claims", {}).get("binanceai.fun", {})
bv = reread["reads"]["binanceai-mint"]["views"]
for k in ("launched", "failed", "isRefundPhase", "totalShares", "tokenClaimed_user", "refundClaimed_user"):
    if num(bv, k) is not None:
        pc[k] = num(bv, k)
pc["lastReadWib"] = NOW_WIB
pc["runNote1731"] = (
    f"Run 1731 (blok ~{BLOCK}): launched={bv.get('launched')}, failed={bv.get('failed')}, "
    f"isRefundPhase={bv.get('isRefundPhase')}, totalShares {bv.get('totalShares')}, "
    f"tokenClaimed(user)={bv.get('tokenClaimed_user')}, refundClaimed(user)={bv.get('refundClaimed_user')} - "
    f"tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
# track_c sales re-reads
tc = snap.get("track_c", {})
for key, rkey in (("bsccat", "bsccat-sale"), ("AONE", "AONE-sale")):
    if key in tc and rkey in reread["reads"]:
        fm = num(reread["reads"][rkey]["views"], "freeMinted")
        if fm is not None:
            old_fm = tc[key].get("freeMinted")
            tc[key]["freeMinted"] = fm
            tc[key]["runNote1731_1120"] = (
                f"Run 1731 (blok ~{BLOCK}): freeMinted {old_fm}->{fm} (FLAT). DIAM.")
        else:
            tc[key]["runNote1731_1120"] = (
                f"Run 1731 (blok ~{BLOCK}): freeMinted GAGAL baca (transport error), nilai lama dipertahankan. DIAM.")
# Pocket Ai: BARU dari sweep run ini - tambah ke snapshot sebagai watchlist-only-age-unverified
pocket = {
    "address": "0xf9D00B7a2992de00EBc5F9f04BAf95d44C542102",
    "status": "watchlist-only-age-unverified-2026-11-20",
    "name": "Pocket Ai",
    "kind": "ERC721",
    "totalSupply": None,
    "totalMinted": 2950,
    "MAX_SUPPLY": 5555,
    "FREE_PRICE": 0,
    "PAID_PRICE": 100000000000000,
    "MAX_FREE_PER_WALLET": 1,
    "MAX_PAID_PER_WALLET": 10,
    "AGENT_REGISTRY": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "owner": "0x9aab2a878f40323af113e5528afe74e4b21a0401",
    "token": "0x7D72D6D06d1240F927039fB364e1B55bd4473d80",
    "userBalance": 0,
    "freeMintedBy_user": 0,
    "paidMintedBy_user": 0,
    "website": "https://pocket.agenticwallet.workers.dev/",
    "gateNote": "Situs ditemukan + dibaca langsung (20 Nov 10:34 UTC): situs lengkap (mint/market/tokenomics/burn-claim) yang mencetak kontrak NFT 0xf9D00B7a2992de00EBc5F9f04BAf95d44C542102 + token POCKET 0x7D72D6D06d1240F927039fB364e1B55bd4473d80 + registry persis. Host workers.dev - CATATAN: putusan final AgentPals (14 Nov) menolak host metadata-worker sebagai bukti website, tapi putusan itu soal endpoint JSON metadata tokenURI, bukan situs lengkap; status gate dicatat sebagai website-ditemukan (bukan vonis lolos final) karena item ini watchlist-only dan gate tidak decision-relevant selama umur/free% unverified.",
    "ageNote": "Umur launch UNVERIFIED: tidak ada tanggal launch di situs maupun hasil pencarian; tidak ada launch-time view di kontrak (START_TIME/startTime/mintStart/launchTime revert/tidak ada); totalMinted sudah 2950/5555 + merkle root POCKET di-update 2026-11-20 mencakup 59 paid mint (token #15-#2901) - mint sudah berjalan cukup lama, tidak bisa diklaim <24 jam. Deep-dive: situs dibaca langsung, ABI Sourcify dibaca, supply on-chain dibaca.",
    "xNote": "Diskusi X UNVERIFIED: pencarian hanya mengembalikan situs proyek itu sendiri; tidak ada post/mention X yang terbaca run ini.",
    "freeNote": "Free% UNVERIFIED: ABI tidak punya free counter (tanpa freeMinted/freeClaimed/FREE_SUPPLY/freeSupply/freeLeft) - freeClaimed/freeMinted view revert; totalMinted 2950/5555 = 53.1% total supply BUKAN free% (dilarang substitusi). Slot user TERBUKA: freeMintedBy(user)=0, paidMintedBy(user)=0, balanceOf(user)=0, FREE_PRICE=0.",
    "firstSeenBlock": BLOCK,
    "lastReadBlock": 134681139,
    "lastReadWib": "2026-11-20 ~17:41 WIB",
    "runNote1731_1120": (
        "Run 1731 (blok 134681139): BARU dari sweep rute 3/6 - Pocket Ai, Sourcify verified, agent-shaped "
        "(AGENT_REGISTRY = registry 0x60B9...22F on-chain, mintFree/mintPaid, FREE_PRICE 0, MAX_FREE_PER_WALLET 1); "
        "totalMinted 2950/5555; slot user TERBUKA (freeMintedBy=0); situs workers.dev mencetak kontrak persis. "
        "Umur launch UNVERIFIED + free% UNVERIFIED (tanpa free counter) + diskusi X UNVERIFIED -> watchlist-only-age-unverified-2026-11-20; "
        "BUKAN early lead (bukan first-seen minting), BUKAN kandidat/strong lead. DIAM; masuk reread set run berikut."),
}
snap.setdefault("contracts", {})["Pocket Ai"] = pocket
snap["timestamp_wib"] = NOW_WIB
snap["last_run_wib"] = "free-mint-search 2026-11-20 17:31 WIB"
snap["note"] = (
    "Run 1731: re-read 51 kontrak (370 call, 277 error RPC, blok merge 134680776); "
    "velocity LOLOS 1 (Stromboat totalMinted 481->668, +187, 6.6786/mnt vs prev 3.375 = 1.98x) TAPI free% UNVERIFIED + umur UNVERIFIED + website gate SUDAH GAGAL -> BUKAN kandidat/strong lead, DIAM; "
    "AgentBadge-ABDG 652->664 (+12, 1.96x tapi <20 token) GAGAL; AgentDrop +2 (2.15x tapi <20) GAGAL; "
    "free>70%: STOCK AGENT 84.9% (943/1111, +2) + Lumenhold 85.4% (1281/1500, totalSupply 1286) tetap bukan strong lead (umur/website UNVERIFIED); "
    "Turtle/Lion GAGAL baca run ini (baseline 44/88 = 50.0% + 42/88 = 47.7% dipertahankan); HIVE GAGAL baca (baseline 1267); ONI 208 FLAT; "
    "binanceai TERBACA run ini: launched=0, failed=1, isRefundPhase=1, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM; "
    "bsccat freeMinted 574 FLAT; AONE freeMinted 10000 FLAT (sold out). "
    "BARU: Pocket Ai 0xf9D00B7a2992de00EBc5F9f04BAf95d44C542102 (sweep) - totalMinted 2950/5555, slot user terbuka, situs workers.dev mencetak kontrak persis; umur + free% UNVERIFIED -> watchlist-only-age-unverified, BUKAN early lead/kandidat/strong lead. DIAM. "
    "agentGTA Arms: belum launch, tanpa alamat kontrak -> run log saja. "
    "Pre-flight Ankr 401 (sejak 9 Nov) - scan leg fast-fail, watermark TETAP 134086385, gap ~590.000+ blok. "
    "Sourcify top verifiedAt 2026-11-20T10:36:30Z; 4 baru vs hot-leg-seen/snapshot (0xc6cf59c6: 15 fns, agent_ref tapi tanpa mint/quote/free -> S1/S2 FAIL; 0x8e53B999: 14 fns; 0x814C888C: 13 fns; 0xcC6f0a57: 50 fns - ketiganya tanpa agent_ref) 0 shape hit. "
    "Boltbook EN 45.015 byte (7 alamat full) + ZH 43.302 byte (6 alamat full), 0 baru. "
    "Bridge 0 baru (116/116 in snapshot, 7 same-owner-discarded). "
    "Sweep EN/ZH + Square + Odaily + PANews: tanpa proyek baru <24 jam terkonfirmasi; AI frog berbayar tutup 20 Nov 15:45 UTC (bukan track C); Odaily segar tanpa pengumuman Agent ID; PANews basi 17 Nov; DappBay tanpa Pocket Ai/agentGTA. "
    "TIDAK ada lead/kandidat/eksekusi baru - DIAM.")
snap["runNote1731"] = snap["note"]
snap["runNote1731_scan"] = (
    "Scan leg route 4: pre-flight Ankr getLogs HTTP 401 Unauthorized (exit 1, head 134680028) - fast-fail, "
    "watermark TETAP 134086385, gap ke head ~590.000+ blok dan membesar; blocker kredensial Ankr (custom.ankr) di luar scope job ini. "
    "Track-C 5c: tanpa output scan baru (Ankr 401), tidak ada shape-check backlog run ini.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
# scan-state note (watermark tidak berubah)
st = json.load(open(BASE + "onchain-scan-state.json"))
st["note_1731_scan"] = (
    "Run 1731 (free-mint-search): pre-flight Ankr getLogs HTTP 401 Unauthorized (exit 1, head 134680028) - "
    "scan leg fast-fail; watermark TETAP 134086385, gap ~590.000+ blok; blocker kredensial Ankr di luar scope job ini.")
json.dump(st, open(BASE + "onchain-scan-state.json", "w"), indent=1)
print(f"MERGE OK: velocity updated={n_upd}, null-reads={n_null}, block={BLOCK}")
