#!/usr/bin/env python3
"""Merge run 2026-11-10 03:01 WIB. Reloads snapshot fresh, applies reread +
triage + discovery findings. Writes snapshot. Scan FAILED (preflight Ankr 401,
4th consecutive) -> watermark NOT advanced. No execution in this run
(no preview/mint/claim).
Velocity baseline: FROZEN 0231 snapshot (run-2026-11-10-0301-baseline-snapshot.json)
so a concurrent 0331 merge cannot corrupt the interval math. Skip-if-fresher:
a contract whose live lastReadBlock is newer than this run's block is skipped.
"""
import json, shutil
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB)
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M WIB")
INTERVAL = 74.3  # (132651254 - 132641351) * 0.45 / 60
NEW_BLOCK = 132651254

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0301-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
base = json.load(open(f"{BASE}/run-2026-11-10-0301-baseline-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-10-0301-reread.json"))
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
        note = f"Run 0301 (blok {NEW_BLOCK}, {NOW_STR}): totalSupply None (degradasi eth_call, nilai lama dipertahankan); "
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
        note = f"Run 0301 (blok {NEW_BLOCK}, {NOW_STR}): totalSupply {prev_sup}->{new_sup} (+{minted if minted is not None else '?'}), velocity {'LOLOS' if vpass else 'GAGAL'}; "
    for k in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if r.get(k) is not None:
            live[k] = r[k]
    if r.get("balanceOf_user") is not None:
        live["balanceOf_user"] = r["balanceOf_user"]
    if r.get("freeClaimed_user") is not None:
        live["freeClaimed_user"] = r["freeClaimed_user"]
    live["lastReadBlock"] = NEW_BLOCK; live["lastReadWib"] = NOW_STR
    live["runNote0301_1110"] = note + f"free={live.get('freeClaimed')}/{live.get('FREE_SUPPLY')}; bal_user={live.get('balanceOf_user')}; status {live.get('status')}."
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
    live["runNote0301_1110"] = f"Run 0301: freeMinted={live.get('freeMinted')}, totalSupply={live.get('totalSupply')} (blok {NEW_BLOCK})."
    tc_updated += 1

# --- Adventure Agent AI: EARLY LEAD (Boltbook ZH front page, first-seen this run) ---
C["Adventure Agent"] = {
    "address": "0x7635ef16370ef490298649a188c9205d1d7fda67",
    "status": "early-lead-reported-2026-11-10",
    "name": "Adventure Agent AI", "symbol": "ADVAGENT", "kind": "ERC721",
    "totalSupply": None, "totalMinted": 459, "freeMinted": 459,
    "FREE_SUPPLY": 2000, "freeLeft": 1542,
    "MAX_FREE_PER_WALLET": 1, "MAX_PAID_PER_WALLET": 5, "paidMinted": 0,
    "mintOpen": None, "balanceOf_user": 0, "freeClaimed_user": 0,
    "AGENT_ID_REGISTRY": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "registry_bytes": False,
    "registryNote": "registry_bytes FALSE adalah false negative: AGENT_ID_REGISTRY() on-chain = registry resmi 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (triage2 run 0301); alamat disimpan via constructor/storage, bukan literal bytecode.",
    "factory": "0x8ae963cd0d203a55791494158463ba5f8a567f8f",
    "advToken": "0x95ad3b9b02c424af94bc3ed417467e174d93f08f",
    "poolWallet": "0xa93a09a764dc618505b33c5b3e08473852a7e0ee",
    "sourcify": "verified", "verifiedAt": "2026-11-09T19:22:07Z", "code_len": 13252,
    "firstSeenWib": "2026-11-10 03:31 WIB",
    "firstSeenSource": "Boltbook front page ZH run 0301 (post nanomind.ai /p/-3lHGkK48hNJ, 'just now': 'Adventure Agent AI: 381/2,000 free minted - mintFree(job) passes simulation, 1,620 free left'; first post, not a recheck)",
    "lastReadBlock": NEW_BLOCK, "lastReadWib": NOW_STR,
    "xVerified": False, "websiteVerified": False,
    "websiteNote": "Situs advagent.xyz ditemukan via tokenURI(1) (https://advagent.xyz/assets/meta/1.json) tapi TIDAK BISA DIAKSES run ini (curl: empty reply; text-fetch: HTTP 403) - belum terverifikasi apakah mencetak kontrak persis. Metode G (pencarian nama) nihil; metode J: ABI tanpa fungsi site/URL; metode H: tidak ada contractURI(). Coba lagi run berikut.",
    "launchNote": "Launch time UNVERIFIED: tidak ada waktu launch dinyatakan proyek; first-mint event belum dikoroborasi (Ankr getLogs 401); penyebutan publik pertama = postingan Boltbook ~03:31 WIB; verifiedAt 02:22 WIB adalah waktu verifikasi Sourcify, BUKAN launch time.",
    "velocityVerified": False, "velocityNote": "Baseline run 0301: totalMinted/freeMinted 459 (22,95% dari 2000); tidak ada rate sebelumnya, velocity belum terhitung. Postingan menyebut 381 saat ditulis (~03:31 WIB) -> +78 mint dalam ~30 menit pertama terpantau.",
    "freePctNote": "459/2000 = 22,95% - di bawah 25% strong lead dan di bawah 50% kandidat. 0 paid mints (totalMinted = freeMinted).",
    "mintFn": "mintFree(uint8) - mengambil job id (uint8); postingan menyebut 'passes simulation'.",
    "userSlotNote": "Slot tampak terbuka: freeClaimed(user)=0, balanceOf(user)=0, MAX_FREE_PER_WALLET=1, freeLeft()=1542 - quote belum terverifikasi (tidak ada fungsi quote; early lead TIDAK PERNAH di-preview).",
    "runNote0301_1110": "Run 0301 EARLY LEAD (dilaporkan sekali): agent-shaped TERKONFIRMASI (AGENT_ID_REGISTRY() = registry resmi + mintFree + FREE_SUPPLY 2000); first mints terverifikasi on-chain run ini (459 free); free 22,95% (<25% strong lead); umur UNVERIFIED; website UNVERIFIED (advagent.xyz via tokenURI, tidak bisa diakses run ini); X belum ditemukan. TIDAK PERNAH preview/mint sebagai early lead. Factory/advToken/poolWallet TIDAK ada di same-owner-discards.",
}
# --- Track-C 0x38491597: watchlist-only, NOT LAUNCHED ---
TC["0x38491597"] = {
    "sale": "0x3849159784aa47Fe76117103904204D9f5D153E7",
    "token": "0xc6d4ec8cb889afba9f251606001457644e260f7d",
    "status": "watchlist-only-not-launched-2026-11-10",
    "saleShape": "PASS (S1): mint(uint256,address) payable + quote(address,uint256)->(uint256,uint256,uint256) + freeSharesRemaining/freeSharesClaimed(address) + AGENT_ID_REGISTRY()=registry resmi 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; 70 fungsi, Sourcify verified (ABI diambil via curl setelah 4x IncompleteRead urllib)",
    "FREE_SHARES": 777, "TOTAL_SHARES": 7777, "totalShares": 9, "totalPaidShares": 0,
    "freeSharesRemaining": 768, "publicFreeRemaining": 768,
    "TOKENS_PER_SHARE": 50000000000000000000000000, "PRICE_PER_SHARE": 2000000000000000,
    "PAID_SHARES": 7000, "LP_TOKEN_RESERVE": 262500000000000000000000000000,
    "launched": 0, "launchPending": 0, "saleClockStart": 0,
    "launchNote": "BELUM LAUNCH: launched()=0, launchPending()=0, saleClockStart()=0 - belum ada pembukaan sale, umur TIDAK BISA diverifikasi; BUKAN lead/kandidat; TIDAK PERNAH preview/mint selagi belum launch. Pantau: bila launched=1 / saleClockStart>0, verifikasi umur dari pembukaan sale.",
    "owner": "0x918e4d71337b117c1baee0729d7f371c1fbddc93",
    "ownerNote": "Owner TIDAK ada di same-owner-discards.",
    "userSlot": {"hasAgentId": 1, "freeSharesClaimed": False, "sharesMinted": 0,
                 "paidSharesMinted": 0, "quote_user_1": [1, 0, 0],
                 "quoteNote": "quote(user,1)=[1,0,0] dibaca mentah: 1 free share, cost 0 (tuple ke-3 = 0, arti belum dipetakan pasti); slot tampak terbuka tapi sale belum launch."},
    "totalPaidIn": 0, "adminBurnMinted": 0,
    "firstSeenWib": "2026-11-10 03:17:53 WIB",
    "firstSeenSource": "Sourcify recently-verified feed run 0301 (verifiedAt 2026-11-09T20:17:53Z); 5a run 0301: S1=True S2=False",
    "discussionNote": "Belum ada bukti diskusi publik (tidak ada di front page Boltbook run ini; belum dicari di X).",
    "websiteNote": "Website belum dicari (sale belum launch; gate menyusul bila launch terverifikasi).",
    "lastReadBlock": NEW_BLOCK, "lastReadWib": NOW_STR,
    "runNote0301_1110": "Run 0301 watchlist-only-not-launched: S1 lolos + free pool 768/777 + slot user tampak terbuka (quote [1,0,0]) TAPI launched=0/saleClockStart=0 - belum launch, bukan lead. Dicatat di track_c untuk dipantau pembukaannya.",
}
# --- HAMMER: checked-not-lead-paid-only (sweep + triage run 0301) ---
EX["HAMMER"] = {
    "address": "0xa9e6f0e6935662aa30f578884662738f05d1c1e4",
    "symbol": "HAMMER", "track": "A", "status": "excluded-paid-2026-11-10",
    "note": "Boltbook recheck post cskh.ai run 0301 (348/44,444, klaim '44,096 free left') TAPI on-chain: PRICE()=0,0004 BNB, mint(uint256) saja, tanpa free view/fungsi free; mint(1) revert 'price is 0.0004 BNB each' (triage run 0231); re-konfirmasi run 0301: totalSupply 349, MAX_SUPPLY 44444, mintOpen 1, bal user 0. Paid-only, BUKAN lead; tidak masuk watchlist aktif.",
}
# --- AgentForge + PocketDragons: age >48h (sweep run 0301) ---
EX["AgentForge"] = {
    "address": "0xf11ea7f1a9768bce1622c9a04f00d5f7da1e8c16",
    "symbol": "AGENTFORGE", "track": "A", "status": "excluded-age-over-48h-2026-11-10",
    "note": "Binance Square post 2026-10-27 (AgentForge free NFT mint, PRICE=0, total 3.333) - proyek ~14 hari, lewat 48 jam; bukan kandidat; tidak pernah masuk snapshot; dicatat dari sweep run 0301.",
}
EX["PocketDragons"] = {
    "address": "0x2cff830264343f29d4924160096f1271a8a14ace",
    "symbol": "POCKETDRAGONS", "track": "A", "status": "excluded-age-over-48h-2026-11-10",
    "note": "Binance Square post 2026-10-24 (PocketDragons free mint, first per wallet free, total 7.000) - proyek ~17 hari, lewat 48 jam; bukan kandidat; tidak pernah masuk snapshot; dicatat dari sweep run 0301.",
}
# --- YAMA: gate methods L + M completed (website gate FAILED definitively) ---
if isinstance(TC.get("YAMA"), dict):
    y = TC["YAMA"]
    y["websiteGate"] = (y.get("websiteGate", "") +
        " TAMBAHAN run 0301 (L+M): (L) BscScan via live browser 03:34-03:42 WIB (task 7825adad): halaman token 0xa84ea20a667b3b1859ab9a9984ff5f03d8688ae2 tab Info KOSONG ('Click here to update the token information'); halaman sale 0x86d779fc4d83044cceccb53639f9a98e367d6e46 tanpa tab Info, tanpa Website/Sosial; token YAMA PROJECT, MAX TOTAL SUPPLY 1.269.000.000, Holders 1.269, Transfers 1.273; Contract Creator sale 0x2193d6e0468ac747823e7e876f1acd34ffe43a67 = first minter (koroborasi halaman benar; sub-laporan Cloudflare sempat blokir sebelum environment diganti, laporan utama dari halaman termuat utuh - diterima mengikuti preseden PIXEL MONSTERS run 0231). (M) site:pages.dev/vercel/surge/deed + pencarian alamat mentah: nihil (hanya same-name tidak terkait). GATE GAGAL DEFINITIF (A/B/C/G/H/I/J/L/M nihil; K butuh auth). Status tetap lead-reported-gate-blocked; TIDAK preview/mint. Deadline umur 48 jam ~15:18 WIB 2026-11-10.")
    y["runNote0301_1110"] = "Run 0301 YAMA: metode L + M selesai - gate website GAGAL definitif; tetap lead-reported-gate-blocked, tanpa preview/mint; deadline umur ~15:18 WIB."

s["runNote0301_1110"] = (
    f"Run 0301 (2026-11-10 {NOW_STR}): reread 630 kontrak + 90 track_c (blok {NEW_BLOCK}, interval 74,3 mnt; "
    f"proses reread awal mati ~03:47 WIB setelah 320 kontrak, di-resume dan selesai; degraded reads={degraded}, skipped-fresher={skipped_fresher}). "
    f"Velocity LOLOS: {vel_pass if vel_pass else '[]'} - AGENT CORE (+215, 14,66x) promotion-discarded-same-owner, TIDAK dipromosikan. "
    "Sold-out baru: []. Free>=25% / >=50% crossing baru: []. Slot berubah: []. "
    "1 EARLY LEAD BARU: Adventure Agent (dilaporkan sekali). 1 track-C watchlist-only-not-launched: 0x38491597 (S1 lolos tapi launched=0). "
    "Sakura +47 (854->901, free 896/6000=14,9%, velocity belum terhitung - tanpa prev rate, tetap early-lead). "
    "YAMA: gate L+M selesai, GAGAL definitif, tetap lead-reported-gate-blocked. "
    "HAMMER tetap paid-only (dicatat excluded-paid); AgentForge + PocketDragons dicatat excluded-age-over-48h. "
    "binanceai tetap closed-refund-phase-2026-11-07 (tidak dibaca ulang; pending_claims kosong)."
)
s["runNote0301_1110_scan"] = (
    "Scan run 0301 FAST-FAIL: preflight pertama gagal di head() dataseed timeout; retry (head 132648436) Ankr ankr_getLogs "
    "HTTP 401 Unauthorized dalam 14,2 dtk (ke-4 kalinya berturut-turut: run 0001, 0201, 0231, 0301). Watermark TIDAK dimajukan "
    "(tetap 132512564, gap ~139.000 blok); backfill terpisah yang menutup gap. Scan leg gagal cepat sesuai amendemen 2026-11-06; route lain tetap jalan."
)
s["runNote0301_1110_discovery"] = (
    "Discovery run 0301: Boltbook front page en (45.433 byte) + zh (45.641 byte) dibaca langsung ~03:30 WIB; "
    "13-14 alamat/halaman; baru vs seen+snapshot: Adventure Agent 0x7635ef16 (EARLY LEAD) + HAMMER 0xa9e6f0e6 (paid-only, sudah diketahui run 0231) + "
    "0x8269Ea16 (chrome footer halaman, bukan proyek). Sourcify feed ~03:30 WIB: 20 alamat (verifiedAt 20:02-20:29Z), 20 baru vs snapshot+seen dihitung sebelum 5a; 5a: 1 S1 pass (0x38491597). "
    "Sweep web (EN+ZH): MOLT AGENT free pool habis (sudah diketahui); VISION sudah di track_c (watchlist-only-age-unverified, situs vision-vsn.pages.dev tercatat); "
    "JOLT claim season tutup 9 Nov (sudah diketahui); HOPKIN sudah di snapshot (watchlist-only, butuh puzzle + posting X); FUIN ONI/CHASTLE/OAGENT berbayar - bukan kandidat; "
    "AgentForge + PocketDragons dicatat excluded-age-over-48h. Route 6: Odaily (255.000 byte) + PANews (119.240 byte) tanpa item Agent ID free-mint baru; DappBay tidak dipakai. "
    "Bridge: tidak berubah sejak 8 Nov (116 kontrak, 8 tidak ada di snapshot - semua temuan lama Nov 3-8, tanpa promosi). "
    "Hot leg: entri terbaru 03:33 WIB semua S1=S2=False; tidak ada track-C lead baru dari hot leg."
)
s["runNote0301_1110_5a"] = (
    "5a run 0301: feed 20 alamat (verifiedAt 20:02-20:29Z); 10 baru di-shape-check (10 dilewati hot-leg-seen); "
    "1 S1 PASS: 0x38491597 (mint + quote + freeSharesClaimed/freeSharesRemaining + hasAgentId; 70 fungsi); 0 S2 pass. "
    "Triage lanjutan membuktikan sale BELUM LAUNCH (launched=0, saleClockStart=0, totalShares 9, free 768/777) -> watchlist-only-not-launched, BUKAN lead."
)
s["runNote0301_1110_binanceai"] = (
    "binanceai: TIDAK dibaca ulang run 0301 (pending_claims kosong; status closed-refund-phase-2026-11-07). "
    "Bacaan terakhir triage run 0201 blok 132639870: launched()=0, failed()=1, isRefundPhase()=1, totalShares()=3110 - tetap refund, tidak ada perubahan."
)
s["last_run_wib"] = NOW_STR
s["last_run_note"] = s["runNote0301_1110"]
json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGED updated={updated} degraded={degraded} skipped_fresher={skipped_fresher} tc_updated={tc_updated} vel_pass={vel_pass}")
print("NOW:", NOW_STR)
