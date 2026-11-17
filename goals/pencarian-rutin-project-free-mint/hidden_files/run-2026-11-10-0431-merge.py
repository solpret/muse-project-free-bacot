#!/usr/bin/env python3
"""Merge run 2026-11-10 04:31 WIB. Reloads snapshot fresh, applies reread +
triage + discovery findings. Writes snapshot. Scan FAILED (preflight Ankr 401,
6th consecutive) -> watermark NOT advanced. ONE execution in this run:
Adventure Agent #554 free mint (strong-lead direct mint, all guards passed).
Velocity baseline: FROZEN 0401 snapshot (run-2026-11-10-0431-baseline-snapshot.json)
so a concurrent hot-leg merge cannot corrupt the interval math. Skip-if-fresher:
a contract whose live lastReadBlock is newer than this run's block is skipped.
"""
import json, shutil
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB)
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M WIB")
INTERVAL = 30.0  # (132659645 - 132655642) * 0.45 / 60
NEW_BLOCK = 132659645

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0431-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
base = json.load(open(f"{BASE}/run-2026-11-10-0431-baseline-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-10-0431-reread.json"))
C = s["contracts"]; TC = s.get("track_c", {}); EX = s.get("excluded", {})
BC = base["contracts"]; BTC = base.get("track_c", {})
updated = 0; degraded = 0; skipped_fresher = 0; vel_pass = []
for name, e in list(BC.items()):
    live = C.get(name)
    if live is None:
        continue
    if isinstance(live.get("lastReadBlock"), int) and live["lastReadBlock"] > NEW_BLOCK:
        skipped_fresher += 1
        continue
    r = rr["reread"].get(name)
    if r is None:
        continue
    prev_sup = e.get("totalSupply"); new_sup = r.get("totalSupply")
    if new_sup is None:
        degraded += 1
        note = f"Run 0431 (blok {NEW_BLOCK}, {NOW_STR}): totalSupply None (degradasi eth_call, nilai lama dipertahankan); "
    else:
        minted = None; rate = None; ratio = None; vpass = False
        if prev_sup is not None and isinstance(prev_sup, int) and isinstance(new_sup, int) and prev_sup < 10_000_000:
            minted = new_sup - prev_sup
            rate = minted / INTERVAL
            prev_rate = float(e.get("currentRatePerMin") or e.get("previousRatePerMin") or 0) or 0.0
            if prev_rate > 0:
                ratio = rate / prev_rate
            vpass = bool(minted >= 20 and prev_rate > 0 and ratio is not None and ratio >= 1.5)
            if vpass:
                vel_pass.append((name, minted, round(rate, 4), round(prev_rate, 4), round(ratio, 2)))
            live["previousTotalSupply"] = prev_sup; live["mintedInInterval"] = minted
            live["intervalMinutes"] = INTERVAL; live["currentRatePerMin"] = rate
            live["previousRatePerMin"] = prev_rate; live["velocityRatio"] = ratio
            live["velocityLegPasses"] = vpass
        live["totalSupply"] = new_sup
        note = f"Run 0431 (blok {NEW_BLOCK}, {NOW_STR}): totalSupply {prev_sup}->{new_sup} (+{minted if minted is not None else '?'}), velocity {'LOLOS' if vpass else 'GAGAL'}; "
    for k in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if r.get(k) is not None:
            live[k] = r[k]
    if r.get("balanceOf_user") is not None:
        live["balanceOf_user"] = r["balanceOf_user"]
    if r.get("freeClaimed_user") is not None:
        live["freeClaimed_user"] = r["freeClaimed_user"]
    live["lastReadBlock"] = NEW_BLOCK; live["lastReadWib"] = NOW_STR
    live["runNote0431_1110"] = note + f"free={live.get('freeClaimed')}/{live.get('FREE_SUPPLY')}; bal_user={live.get('balanceOf_user')}; status {live.get('status')}."
    updated += 1

tc_updated = 0
for name, e in list(BTC.items()):
    if not isinstance(e, dict):
        continue
    live = TC.get(name)
    if not isinstance(live, dict):
        continue
    r = rr["track_c"].get(name)
    if r is None:
        continue
    if r.get("freeMinted") is not None:
        live["freeMinted"] = r["freeMinted"]
    if r.get("totalSupply") is not None:
        live["totalSupply"] = r["totalSupply"]
    live["runNote0431_1110"] = f"Run 0431: freeMinted={live.get('freeMinted')}, totalSupply={live.get('totalSupply')} (blok {NEW_BLOCK})."
    tc_updated += 1

# --- Adventure Agent AI: PROMOTED early -> strong lead -> MINTED BY USER (#554) ---
if isinstance(C.get("Adventure Agent"), dict):
    aa = C["Adventure Agent"]
    aa["status"] = "minted-by-user-2026-11-10"
    aa["freeMinted"] = 555; aa["freeLeft"] = 1445; aa["totalMinted"] = 555
    aa["balanceOf_user"] = 1; aa["freeClaimed_user"] = 1
    aa["advBalance_user"] = 100000000000000000000
    aa["mintedTokenId"] = 554; aa["mintedRarity"] = "Common"; aa["mintedJob"] = "Warrior"
    aa["mintTx"] = "0x0bdb0e16ee7e5ed45af8e7e21b050c4aa25d4998358518013bc2c98168dab991"
    aa["mintBlock"] = 132664145; aa["mintGasUsed"] = 223234
    aa["websiteVerified"] = True; aa["xVerified"] = True
    aa["xHandle"] = "@ADV_Agent_Ai"
    aa["websiteNote"] = ("TERVERIFIKASI run 0431 (metode G + I): tokenURI(1) -> https://advagent.xyz/assets/meta/1.json "
        "(external_url https://advagent.xyz); www.advagent.xyz HTTP 200 (SPA shell, title 'Adventure Agent AI'); "
        "JS bundle /assets/index-Y-5J4Pxb.js (541.170 byte) MENCETAK kontrak persis 0x7635ef16370ef490298649a188c9205d1d7fda67 "
        "dan registry resmi 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F. Situs tertaut dari tokenURI + postingan TG proyek. "
        "Root advagent.xyz masih curl HTTP 000 (hanya www yang merespons).")
    aa["xNote"] = ("X @ADV_Agent_Ai terverifikasi run 0431 (fxtwitter user endpoint): nama 'Adventure Agent Ai', "
        "deskripsi 'Fantasy Adventure RPG for AI Agents only | Mint your hero, battle monsters, farm $ADV on BSC', "
        "website http://advagent.xyz, dibuat Mon Nov 09 16:37:43 UTC 2026 (= 23:37 WIB 9 Nov), 1 tweet, 0 follower. "
        "Linkage dua arah: situs menautkan X, X menautkan situs.")
    aa["launchNote"] = ("Launch time TERVERIFIKASI run 0431: postingan Telegram resmi t.me/AdventureAgentAI msg 5, "
        "2026-11-09T20:05:51Z = 2026-11-10 03:05:51 WIB: 'ADVENTURE AGENT AI IS LIVE! ... MINT IS OPEN (BSC). "
        "FREE: 2,000 slots - 1/wallet, +100 $ADV', mencetak kontrak NFT 0x7635ef16370ef490298649a188c9205d1d7fda67, "
        "$ADV 0x95ad3b9b02c424af94bc3ed417467e174d93f08f, situs advagent.xyz, X @ADV_Agent_Ai. "
        "Kanal TG tertaut dari JS bundle situs. Umur saat mint ~2,5 jam (<=48 jam). "
        "Binary-search first-mint block GAGAL (archive state tidak tersedia: dataseed 'missing trie node', "
        "publicnode butuh token) - tidak lagi diperlukan setelah pengumuman TG.")
    aa["freePctNote"] = ("555/2000 = 27,75% pasca-mint (539/2000 = 26,95% saat re-read run 0431, blok 132659645; "
        "505->539, +34 dalam interval 30,0 mnt). Kaki strong lead: umur TERVERIFIKASI <=48 jam + free >=25% + slot terbuka -> STRONG LEAD, lalu MINTED.")
    aa["velocityNote"] = ("Run 0431: freeMinted 505->539 (+34, 1,13/mnt); velocity totalSupply tidak terhitung (totalSupply() None).")
    aa["marketplaceNote"] = ("Market proyek sendiri ADA: AdventureMarketplace 0x9d4f73c7c92bb4f680c770d0ed3c71527297a256 "
        "(dari JS bundle situs, footer + halaman Market; fee 5%; code 3.854 byte on-chain; TIDAK terverifikasi Sourcify "
        "sehingga listings tidak bisa dibaca on-chain). Listing live TIDAK terverifikasi (UI situs menampilkan 'No listings "
        "on the Marketplace contract yet' saat kosong) -> BUKAN venue live; TIDAK auto-list (tidak ada floor live terbaca).")
    aa["runNote0431_1110"] = ("Run 0431 STRONG-LEAD DIRECT MINT BERHASIL: mintFree(0) job Warrior, token #554 Common Warrior "
        "(100 HP/9 ATK/4 DEF) + 100 $ADV. Tx 0x0bdb0e16ee7e5ed45af8e7e21b050c4aa25d4998358518013bc2c98168dab991, blok 132664145, "
        "receipt status 1, gas 223.234. Verifikasi: ownerOf(554)=agent wallet, freeClaimed(user)=1, bal=1, freeMinted 555, "
        "saldo ADV 100. Audit Binance: hasResult=false (TIDAK ADA HASIL, bukan pass). Preview bersih 000000000 "
        "(+1 NFT #554, +100 ADV, tanpa authority/allowance/risk). Discards: kontrak/factory/advToken/poolWallet TIDAK ada "
        "di same-owner-discards. baw CONNECTED, devMode aktif s.d. 16 Nov.")
# --- Sakura: update reread run 0431 ---
if isinstance(C.get("Sakura"), dict):
    sk = C["Sakura"]
    sk["totalSupply"] = 964; sk["freeMinted"] = 959
    sk["lastReadBlock"] = NEW_BLOCK; sk["lastReadWib"] = NOW_STR
    sk["runNote0431_1110"] = ("Run 0431: totalSupply 928->964, freeMinted 923->959 (959/6000 = 15,98%, masih <25%); "
        "velocity LOLOS (+36, 1,9x) tapi velocity saja bukan promosi; umur terverifikasi; slot belum terverifikasi; "
        "website belum ditemukan -> tetap early-lead-reported, bukan strong lead.")
# --- AgentX: SOLD OUT 2500/2500 -> pindah ke excluded, hapus dari contracts ---
if isinstance(C.get("AgentX"), dict):
    ax = C.pop("AgentX")
    ax["status"] = "sold-out-2026-11-10"
    ax["soldOutNote"] = ("Run 0431 (blok 132659645): totalSupply 2493->2500 = MAX_SUPPLY 2500 -> SOLD OUT. "
        "Sebelumnya watchlist-only-age-unverified-0301 (website UNVERIFIED, free% UNVERIFIED). "
        "Tidak pernah dilaporkan sebagai lead ke chat; perubahan dicatat di sini, dihapus dari contracts.")
    EX["AgentX"] = ax
# --- Golden Agents: velocity pass, tetap early lead ---
if isinstance(C.get("Golden Agents"), dict):
    C["Golden Agents"]["runNote0431_1110"] = ("Run 0431: totalSupply 706->770 (+64, velocity LOLOS 11,31x) TAPI free% UNVERIFIED "
        "(tanpa free view) + website UNVERIFIED -> velocity saja bukan promosi; tetap early-lead-2026-11-09. "
        "Umur terverifikasi <=48 jam (first mint blok 132445024 ~02:00 WIB 9 Nov; deadline ~02:00 WIB 11 Nov).")
# --- MONOLITH: +7, tetap early lead ---
if isinstance(C.get("MONOLITH"), dict):
    C["MONOLITH"]["runNote0431_1110"] = ("Run 0431: totalSupply 621->628 (+7, velocity GAGAL); free% UNVERIFIED; slot UNVERIFIED; "
        "umur ~37 jam (first observed mint 2026-11-08 17:32 WIB, deadline 48 jam ~17:32 WIB hari ini) -> tetap early-lead-reported-2026-11-08.")
# --- Track-C 0x38491597: still NOT LAUNCHED ---
if isinstance(TC.get("0x38491597"), dict):
    t = TC["0x38491597"]
    t["freeSharesRemaining"] = 766; t["publicFreeRemaining"] = 766
    t["totalShares"] = 11
    t["launched"] = 0; t["launchPending"] = 0; t["saleClockStart"] = 0
    t["lastReadBlock"] = 132661837; t["lastReadWib"] = NOW_STR
    t["runNote0431_1110"] = ("Run 0431 re-check (blok 132661837): MASIH BELUM LAUNCH (launched=0, launchPending=0, saleClockStart=0); "
        "freeSharesRemaining 767->766, totalShares 10->11 (1 share diklaim pihak lain); freeSharesClaimed(user)=0. "
        "Tetap watchlist-only-not-launched, BUKAN lead; TIDAK preview/mint.")
# --- YAMA: no change ---
if isinstance(TC.get("YAMA"), dict):
    TC["YAMA"]["runNote0431_1110"] = ("Run 0431: tidak ada perubahan - gate website GAGAL definitif (run 0301, metode L+M); "
        "tetap lead-reported-gate-blocked; TIDAK preview/mint; deadline umur 48 jam ~15:18 WIB 2026-11-10.")
# --- Grove watch: degraded read ---
if isinstance(C.get("Grove"), dict):
    C["Grove"]["runNote0431_1110"] = ("Run 0431 grove-check: DEGRADED (block null, freeOpen null, freeClaimed_user 0 - RPC gagal baca); "
        "tidak ada perubahan yang bisa diverifikasi; nilai lama dipertahankan.")

s["runNote0431_1110"] = (
    f"Run 0431 (2026-11-10 {NOW_STR}): reread 631 kontrak + 91 track_c (blok {NEW_BLOCK}, interval 30,0 mnt; "
    f"reread selesai 702,2 dtk via exec terkelola; degraded reads={degraded}, skipped-fresher={skipped_fresher}). "
    f"Velocity LOLOS: {vel_pass if vel_pass else '[]'} - Golden Agents (+64, ~11,3x) early-lead, free% UNVERIFIED + website UNVERIFIED, TIDAK dipromosikan; "
    "Sakura (+36, ~1,9x) early-lead, free 959/6000=15,98% (<25%), TIDAK dipromosikan. "
    "EKSEKUSI: Adventure Agent AI PROMOSI early->strong lead (umur TERVERIFIKASI via TG 03:05:51 WIB + free 26,95% + slot terbuka + website TERVERIFIKASI) "
    "dan MINTED #554 Common Warrior + 100 $ADV (tx 0x0bdb0e16..., blok 132664145, status 1). "
    "AgentX SOLD OUT 2500/2500 -> dipindah ke excluded. Sold-out baru lain: []. Free>=25% / >=50% crossing baru: [] "
    "(Adventure Agent sudah dihitung sebagai promosi+mint). Slot berubah: [Adventure Agent freeClaimed 0->1 (minted)]. "
    "0x38491597 tetap watchlist-only-not-launched (launched=0; free 767->766, totalShares 10->11). "
    "MONOLITH +7 (621->628, deadline umur ~17:32 WIB). YAMA: tanpa perubahan, gate gagal definitif, deadline umur ~15:18 WIB. "
    "Grove check degraded (tidak ada perubahan terverifikasi). binanceai tetap closed-refund-phase-2026-11-07 (tidak dibaca ulang; pending_claims kosong)."
)
s["runNote0431_1110_scan"] = (
    "Scan run 0431 FAST-FAIL: preflight (head 132659644) Ankr ankr_getLogs "
    "HTTP 401 Unauthorized dalam 8,2 dtk (ke-6 kalinya berturut-turut: run 0001, 0201, 0231, 0301, 0401, 0431; outage sejak 2026-11-09 ~13:33 WIB). Watermark TIDAK dimajukan "
    "(tetap 132512564, gap ~147.080 blok); backfill terpisah yang menutup gap. Scan leg gagal cepat sesuai amendemen 2026-11-06; route lain tetap jalan."
)
s["runNote0431_1110_discovery"] = (
    "Discovery run 0431: Boltbook front page en (45.133 byte) + zh (45.358 byte) dibaca langsung ~05:05 WIB; "
    "15 alamat/halaman; baru vs snapshot+seen: hanya pair BOLT/WBNB 0x0d2f626b (bukan proyek) + footer 0x8269Ea16 (bukan proyek). "
    "KIJIN 0x62518895 sudah di snapshot (early-lead); ACORE sudah di snapshot (AGENT CORE); COSO v2 post menyebut RFALL/ACORE/ADVAGENT/VISION/JINMA "
    "(semua sudah di snapshot/track_c/excluded). "
    "Sweep web (EN+ZH): tanpa proyek baru - AirdropBuzz (MALTA/YAMA sudah diketahui; NAOMI/IAO MINING/PUNK HOOD/Polka Agents tidak terverifikasi independen, bukan launch baru), "
    "Substack '22 projects' (13 hari), AgentForge (27 Okt, sudah diketahui), Laser Agents (25 Okt, excluded per body), daftar @congge918 26 Okt (sudah diketahui). "
    "Route 6: Odaily (250.879 byte) + PANews (118.521 byte) tanpa item Agent ID free-mint baru; DappBay tidak dipakai. "
    "Bridge: tidak berubah sejak 8 Nov 18:21 (116 kontrak; 3 tidak ada di snapshot - PANBA 0x493d51ca free ERC20 finding Nov 4, "
    "0x636fdfa9 + 0xf75cf7f9 PAID - tanpa promosi; 7 same_owner_discarded tidak pernah dipromosikan). "
    "Hot leg 0439: SILENT (review log hot-leg-run-2026-11-10-0439.json)."
)
s["runNote0431_1110_5a"] = (
    "5a run 0431: feed SEGAR via curl (20 alamat, verifiedAt 21:11-21:41Z = 04:11-04:41 WIB); SEMUA 20 sudah di-shape-check hot leg "
    "(10 checked-not-sale-shape, 10 checked-abi-unavailable - termasuk 5 transport-error run 0401 yang kini berstatus abi-unavailable di hot-leg-seen); "
    "0 S1 pass, 0 S2 pass; tidak ada yang perlu di-shape-check ulang run ini."
)
s["runNote0431_1110_binanceai"] = (
    "binanceai: TIDAK dibaca ulang run 0431 (pending_claims kosong; status closed-refund-phase-2026-11-07). "
    "Bacaan terakhir triage run 0201 blok 132639870: launched()=0, failed()=1, isRefundPhase()=1, totalShares()=3110 - tetap refund, tidak ada perubahan."
)
s["last_run_wib"] = NOW_STR
s["last_run_note"] = s["runNote0431_1110"]
json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGED updated={updated} degraded={degraded} skipped_fresher={skipped_fresher} tc_updated={tc_updated} vel_pass={vel_pass}")
print("NOW:", NOW_STR)
print("contracts:", len(C), "track_c:", len(TC), "excluded:", len(EX))
