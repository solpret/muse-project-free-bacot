#!/usr/bin/env python3
"""Snapshot + seen/state update run 0131 (2026-11-06 01:31 WIB).
Route 1: reread block 131867112, interval 38.07 min vs run 0101 (block 131862037).
Route 4: scan window 131864899-131866898 (2000 blok, cap), head 131866898,
gap dilewati 131861763-131864898 (3136 blok). 234 NFT + 415 ERC-20, 80 Ankr calls, 0 errors.
First-seen: 5 (semua registry=True). Triase:
- AgentX: EARLY LEAD (first mint 2026-11-06 01:21:38 WIB, 359 mints/359 minters,
  sample tx value 0, quote(user,1)=0, MAX_SUPPLY 2500, owner 0x87d10c... BUKAN grup
  same-owner 0x293f/0x1103/0xd76d/0xa054/0x1e1e; Sourcify ABI gagal dicek run ini
  (retry-exhausted) - bentuk agent via registry-bytes scan + bukti on-chain; ABI re-cek run berikut).
- HI-SCORE: watchlist-only (price 0.001 BNB, sample tx value 0 - free lane unverified).
- Gale Oracle Agent / Sigma Bear Agent / Syntax Grid: PAID-ONLY (sample mint tx 0.0081 BNB,
  totalSupply 3333 pre-mint, minter sama 0xe9d9dec36ce804e44fdd5e19f09e2364cbf64ed5).
Web legs: Believe BNB (track C) shape UNVERIFIED (Sourcify retry-exhausted, sale views None,
believebnb.xyz HTML tidak mencetak kontrak) -> track_c watchlist-only; AETHER age-excluded
(first mint 2026-11-01 23:47:37 WIB, >48h; quote(user,1)=0.000145 BNB, bukan 0);
ONLYAI Crystals upcoming (totalSupply 0, buka 2026-11-07 01:00 WIB).
0 kandidat, 0 strong lead baru/promosi, 0 lead/kandidat track-C baru, 0 pending claim baru/dibuka.
"""
import json, shutil

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
BLOCK = 131867112
INTERVAL_MIN = 38.07
RUN = "2026-11-06 run 0131"

snap = json.load(open(HF + "onchain-snapshot.json"))
seen = json.load(open(HF + "onchain-scan-seen.json"))
state = json.load(open(HF + "onchain-scan-state.json"))
scan = json.load(open(HF + "onchain-scan-2026-11-06-0131.json"))
reread_old = json.load(open(HF + "reread-2026-11-06-0101.json"))["contracts"]
reread = json.load(open(HF + "run-2026-11-06-0131-reread.json"))["contracts"]
verify = json.load(open(HF + "verify-2026-11-06-0131.json"))["items"]

shutil.copy(HF + "onchain-snapshot.json", HF + "onchain-snapshot-0131.bak.json")
shutil.copy(HF + "onchain-scan-seen.json", HF + "onchain-scan-seen-0131.bak.json")
shutil.copy(HF + "onchain-scan-state.json", HF + "onchain-scan-state-0131.bak.json")

# --- seen file: append the 5 first-seen ---
added = 0
for c in scan["contracts"]:
    a = c["address"]
    if a.lower() not in {k.lower() for k in seen["contracts"]}:
        seen["contracts"][a] = c.get("first_block")
        added += 1
json.dump(seen, open(HF + "onchain-scan-seen.json", "w"), indent=1)

# --- scan state: advance watermark ONLY on success (0 errors) ---
state.update({
    "last_scanned_block": scan["to_block"],
    "last_scan_window_from": scan["from_block"],
    "last_scan_window_to": scan["to_block"],
    "last_scan_wib": RUN,
    "ankr_calls": scan.get("ankr_calls"),
    "errors": scan.get("errors", []),
    "nft_contracts": len(scan["contracts"]),
    "erc20_mint_contracts": scan.get("erc20_mint_contracts"),
    "skipped_gap": "131861763-131864898 (3136 blok, window dari watermark 131861762 ke head scan 131866898 = 5136 blok > cap 2000; scan menutup 2000 blok terbaru 131864899-131866898)",
    "note": ("Scan run 0131 SUKSES (80 panggilan Ankr, 0 error). 5 first-seen registry=True: "
             "AgentX (EARLY LEAD, first mint 01:21:38 WIB, 359 mints free), HI-SCORE (watchlist-only, "
             "price 0.001 BNB), Gale Oracle Agent / Sigma Bear Agent / Syntax Grid (paid-only 0.0081 BNB). "
             "Gap kumulatif sejak run 1831 ~43.200 blok tak ter-scan. Rantai 0,45 dtk/blok - 30 mnt = ~4000 blok, "
             "cap 2000 hanya menutup ~15 mnt; watermark tertinggal ~2000 blok/run (keputusan parent pending)."),
    "last_scan_window": "131864899-131866898",
    "ankr_calls_last_scan": scan.get("ankr_calls"),
    "errors_last_scan": scan.get("errors", []),
    "scan_started_wib": "2026-11-06 01:44",
    "scan_finished_wib": "2026-11-06 01:58",
    "head_at_scan_start": 131866837,
})
json.dump(state, open(HF + "onchain-scan-state.json", "w"), indent=1)

# --- route 1: generic reread update for snapshot contracts matching reread labels ---
def velocity(old_ts, new_ts, prev_rate):
    if old_ts is None or new_ts is None:
        return None, "baca gagal (None) - nilai lama dipertahankan, velocity TIDAK dihitung"
    d = new_ts - old_ts
    rate = d / INTERVAL_MIN
    if prev_rate is None:
        return False, f"+{d} dalam {INTERVAL_MIN} mnt = {rate:.3f}/mnt vs prev None = baseline pertama, rasio belum terhitung -> velocity TIDAK lulus run ini"
    if prev_rate == 0:
        return False, f"+{d} dalam {INTERVAL_MIN} mnt = {rate:.3f}/mnt vs prev 0.0 = tidak terhitung -> velocity GAGAL"
    ratio = rate / prev_rate
    ok = ratio >= 1.5 and d >= 20
    return ok, f"+{d} dalam {INTERVAL_MIN} mnt = {rate:.3f}/mnt vs prev {prev_rate} = {ratio:.2f}x -> velocity {'LULUS' if ok else 'GAGAL'}"

for label, new in reread.items():
    if label not in snap["contracts"]:
        continue
    e = snap["contracts"][label]
    old = reread_old.get(label, {})
    old_ts = old.get("totalSupply")
    new_ts = new.get("totalSupply")
    # konvensi run 0101: bandingkan vs currentRatePerMin (rate interval sebelumnya),
    # lalu geser: previousRatePerMin = rate lama, currentRatePerMin = rate baru.
    # (KOREKSI BUG 0101: totalSupply kini ikut diperbarui ke bacaan baru.)
    prev_rate = e.get("currentRatePerMin")
    ok, note = velocity(old_ts, new_ts, prev_rate)
    if new_ts is not None:
        e["previousTotalSupply"] = old_ts
        e["totalSupply"] = new_ts
        e["mintedInInterval"] = (new_ts - old_ts) if old_ts is not None else None
        e["intervalMinutes"] = INTERVAL_MIN
        if ok is not None:
            new_rate = round((new_ts - old_ts) / INTERVAL_MIN, 4) if old_ts is not None else None
            e["previousRatePerMin"] = prev_rate
            e["currentRatePerMin"] = new_rate
            e["velocityLegPasses"] = bool(ok)
        e["lastReadBlock"] = BLOCK
        e["lastReadWib"] = RUN
    if new.get("freeMinted") is not None:
        e["freeMinted"] = new["freeMinted"]
    if new.get("freeClaimed") is not None:
        e["freeClaimed"] = new["freeClaimed"]
    if new.get("balanceOf_user") is not None:
        e["balanceOf_user"] = new["balanceOf_user"]
    e["runNote0131"] = f"Run 0131 (blok {BLOCK}): totalSupply {old_ts}->{new_ts}; {note}."
    if label in ("Cuprihive", "Skyagent", "Rookling", "Night Shift"):
        e["runNote0131"] += " Age-excluded, bacaan hanya konfirmasi, tanpa laporan ulang."
    if label == "BINANCEAI-mint":
        e["runNote0131"] = ("Run 0131: launched=False, isRefundPhase=True, tokenClaimed(user)=False - "
                            "tetap refund/failed; pending_claims tetap kosong {}.")
    if label == "Agent Grove":
        e["runNote0131"] = ("Run 0131: FREE_SUPPLY 2500, freeOpen=False (fase 2 dibuka 13:05 WIB hari ini, "
                            "belum dibuka) - tetap upcoming.")
    if label == "WHALE":
        e["runNote0131"] += " Deadline umur 2026-11-06 17:33 WIB."
    if label == "Flyingsquirrelai":
        e["runNote0131"] += " totalSupply terbaca aneh (975e21, format token-amount) - bukan hitungan NFT; diabaikan."
    if label == "Agent Wallet":
        e["runNote0131"] = "Run 0131: semua view gagal baca (None, bukan perubahan)."

# --- track_c reread notes ---
tc = snap.setdefault("track_c", {})
tc_notes = {
    "LuckyBox-LUCK": "Run 0131: totalSupply 545->580 (+35 mint pihak lain); status tetap track-c-lead-gate-blocked (dilaporkan hot-leg 16:15 WIB 2026-11-05); umur: first mint 2026-11-05 15:59:44 WIB, ~34 jam, masih <=48 jam sampai ~15:59 WIB hari ini; tanpa perubahan status.",
    "NJAR": "Run 0131: giftsClaimed 569 flat vs run 0101; status tetap track-c-lead-gate-blocked.",
    "DROID": "Run 0131: semua view gagal baca (None, bukan perubahan).",
    "OSK": "Run 0131: opened=False, tanpa perubahan status.",
    "IMARS": "Run 0131: opened=True + pool gratis habis (diketahui), tanpa perubahan status.",
    "NIULAI": "Run 0131: launched=False, phase 4, freeClaimed 4444; tanpa perubahan status.",
    "DeY": "Run 0131: totalSupply terbaca (base units), balanceOf(user)=0; tanpa perubahan status.",
    "FANBEIMAO-824d": "Run 0131: semua view gagal baca (None) - BUKAN perubahan, retry run berikut.",
    "Nvagent-NVGT": "Run 0131: totalSupply terbaca (base units), mintOpen=True, quote(user,1)=0; tanpa perubahan status.",
    "Nvagent-NVGT-28Fe": "Run 0131: totalSupply terbaca (base units), mintOpen=True, quote(user,1)=0; tanpa perubahan status.",
    "Hongbao-HONGBAO": "Run 0131: freeClaimed 7, mintOpen=True; tanpa perubahan status.",
    "Soarm-SOARM": "Run 0131: semua view gagal baca (None) - BUKAN perubahan, retry run berikut.",
    "Pacture": "Run 0131: freeClaimed(user)=1 (sudah diklaim) - tanpa perubahan.",
    "Ikigai-Ihigi": "Run 0131: freeMinted 273 (sama) - tanpa perubahan.",
    "KillZero-K0-sale": "Run 0131: launched=False - tetap belum dibuka.",
    "960E-sale": "Run 0131: semua view gagal baca (None) - BUKAN perubahan, retry run berikut.",
    "CHTCI": "Run 0131: totalSupply terbaca (base units), mintOpen=True - tanpa perubahan status.",
}
for k, note in tc_notes.items():
    if k in tc:
        tc[k]["runNote0131"] = note
# PRDICT not in track_c dict; note it in contracts if present
if "PRDICT-sale" in snap["contracts"]:
    snap["contracts"]["PRDICT-sale"]["runNote0131"] = "Run 0131: totalMints 158 flat vs run 0101; tanpa perubahan status."

# --- new entries ---
snap["contracts"]["AgentX"] = {
    "address": "0x59D96D8B4B82Abb350868E897F25F8e021360823",
    "name": "AgentX", "symbol": "AGX", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-06",
    "totalSupply": 399, "MAX_SUPPLY": 2500,
    "firstSeenBlock": 131864930, "firstMintBlock": 131863885,
    "firstMintWib": "2026-11-06 01:21:38 WIB",
    "window_mints": 137, "window_minters": 137,
    "scan_log_count": 359, "scan_minters": 359,
    "quote_user_1": 0, "mintedBy_user": 0,
    "owner": "0x87d10c4edbc616894173c958e17999af4e5a3b17",
    "lastReadBlock": BLOCK, "lastReadWib": RUN,
    "baselineNote": ("EARLY lead dilaporkan sekali run 0131. First mint 01:21:38 WIB (Ankr getLogs, "
        "0 log sebelum blok itu back to 130000000); 359 mint/359 minter terverifikasi on-chain; "
        "sample mint tx value 0 (0x3f3ab3aa..., 0xdf2c1447...); quote(user,1)=0; MAX_SUPPLY 2500 -> "
        "399/2500 = 16,0% (inference totalSupply, BUKAN freeClaimed view - kontrak tidak expose "
        "freeClaimed/freeMinted/FREE_SUPPLY) < 25% strong leg. Umur terverifikasi ~55 mnt saat lapor. "
        "X: diskusi Boltbook front page (post free auto-mint #54) - X account sendiri UNVERIFIED. "
        "CATATAN: satu penulis Boltbook melaporkan value-0 sim-nya revert - kemungkinan wallet-nya sudah "
        "pakai free slot (bukan bukti lane tutup); quote(user)=0 untuk wallet user. Sourcify ABI gagal "
        "dicek run ini (retry-exhausted) - bentuk agent via registry-bytes scan + bukti on-chain; "
        "ABI + sim mint dicek ulang run berikut. Owner 0x87d10c... BUKAN grup same-owner "
        "(0x293f/0x1103/0xd76d/0xa054/0x1e1e). TIDAK PERNAH auto-mint/preview sebagai early lead; "
        "promosi ke strong lead bila 3 kaki terpenuhi."),
}
snap["contracts"]["HI-SCORE"] = {
    "address": "0xA74081fd9bc9623A2d9321223C35b41016A7fd65",
    "name": "HI-SCORE", "symbol": "HISCORE", "kind": "ERC721",
    "status": "watchlist-only-2026-11-06",
    "totalSupply": 15, "firstSeenBlock": 131865618, "firstMintBlock": 131862160,
    "firstMintWib": "2026-11-06 01:08:42 WIB", "scan_log_count": 13, "scan_minters": 10,
    "price": 1000000000000000,
    "lastReadBlock": BLOCK, "lastReadWib": RUN,
    "baselineNote": ("First-seen scan run 0131. price()=0.001 BNB TAPI sample mint tx value 0 (2 tx) - "
        "free lane UNVERIFIED (bisa jadi free lane + paid lane, atau mint gratis awal). Sourcify ABI "
        "gagal dicek run ini (retry-exhausted). BUKAN early lead (paid-suspect); perlu cek ABI + sim "
        "mint run berikut. Bila terbukti paid-only -> watchlist-only-paid-only."),
}
for name, addr, first_wib, first_block in [
    ("Gale Oracle Agent", "0x41F2AADB4c89BCC8e0950fC52e82c01aE690C0A6", "2026-11-06 01:31:58 WIB", 131865263),
    ("Sigma Bear Agent", "0x84f7747b0a8dfAf636b06087c635eCB7A2a49791", "2026-11-06 01:37:15 WIB", 131865967),
    ("Syntax Grid", "0xB4266952FeE991D0cC83321343d0EF7e43b7Ab47", "2026-11-06 01:42:28 WIB", 131866662),
]:
    snap["contracts"][name] = {
        "address": addr, "name": name, "kind": "ERC721",
        "status": "watchlist-only-paid-only-2026-11-06",
        "totalSupply": 3333, "MAX_SUPPLY": 3333,
        "firstSeenBlock": first_block, "firstMintBlock": first_block, "firstMintWib": first_wib,
        "scan_log_count": 1, "scan_minters": 1,
        "lastReadBlock": BLOCK, "lastReadWib": RUN,
        "baselineNote": ("First-seen scan run 0131, PAID-ONLY: sample mint tx value 0x1c6bf52634000 "
            "(0.0081 BNB); totalSupply 3333 pre-mint (1 log di jendela); minter sama "
            "0xe9d9dec36ce804e44fdd5e19f09e2364cbf64ed5 untuk ketiganya (satu operator, template sama). "
            "BUKAN early lead. Log-only."),
    }
snap["contracts"]["ONLYAI-Crystals"] = {
    "address": "0x156482ad3f0eebd8e3f70d494ebd1da3f738f5ba",
    "name": "ONLYAI Crystals", "kind": "ERC721",
    "status": "watchlist-only-upcoming-2026-11-06",
    "totalSupply": 0,
    "mintStartWib": "2026-11-07 01:00 WIB",
    "lastReadBlock": BLOCK, "lastReadWib": RUN,
    "baselineNote": ("Boltbook front page ZH run 0131 (post teratas): NFT 5.555, totalSupply masih 0, "
        "buka 2026-11-07 01:00 WIB (6 Nov 18:00 UTC); first mint free per Agent. UPCOMING, BUKAN lead/kandidat."),
}
# SoulAgent / RigOrb / Tigora / MORPHA / Brinedroid / DEWATA updates
sa = snap["contracts"]["SoulAgent"]
sa.update({"totalSupply": 1034, "lastReadBlock": BLOCK, "lastReadWib": RUN,
           "runNote0131": "Run 0131: totalSupply 719 (run 1931) -> 1034 (+315, ~0,8/mnt); 1034/5555 = 18,6% < 25% strong leg -> BUKAN strong lead; umur first-seen 2026-11-05, X unverified; tetap early-lead-reported, tanpa promosi."})
rb = snap["contracts"]["RigOrb-539e"]
rb.update({"totalSupply": 1298, "lastReadBlock": BLOCK, "lastReadWib": RUN,
           "runNote0131": "Run 0131: totalSupply 1200 (run 1931) -> 1298 (+98); 1298/10000 = 13,0% < 25% strong leg -> BUKAN strong lead; tetap early-lead-reported, tanpa promosi."})
tg = snap["contracts"]["Tigora-E8c4"]
tg.update({"lastReadBlock": BLOCK, "lastReadWib": RUN,
           "runNote0131": "Run 0131: totalSupply gagal baca (None, nilai lama 619 dipertahankan); Boltbook front page ~01:46 WIB menyebut free mint #745 (bacaan snippet, bukan RPC) - dicatat, bukan nilai terverifikasi; tetap watchlist-only."})
mo = snap["contracts"]["MORPHA"]
mo.update({"totalSupply": 207, "lastReadBlock": BLOCK, "lastReadWib": RUN,
           "runNote0131": "Run 0131: totalSupply 156 (run 2331) -> 207; Sourcify not_verified; penulis Boltbook: 'every mint sim still reverts' - bukan free-mintable; tetap watchlist-only-unverified-shape."})
br = snap["contracts"]["Brinedroid"]
br.update({"totalSupply": 1017, "freeClaimed": 1012, "lastReadBlock": BLOCK, "lastReadWib": RUN,
           "runNote0131": "Run 0131: totalSupply 432 (run 0101 2026-11-04) -> 1017, freeClaimed 1012/2222 = 45,5%, quote(user,1)=0; TAPI status tetap same-owner-discarded - TIDAK PERNAH dipromosikan; log-only."})
dw = snap["contracts"]["Dewata"]
dw.update({"lastReadBlock": BLOCK, "lastReadWib": RUN,
           "runNote0131": ("Run 0131: totalSupply gagal baca (None); first mint terverifikasi on-chain blok 131835456 = "
             "2026-11-05 21:48:22 WIB -> umur ~28 jam, VERIFIED <=48 jam; Sourcify not_verified (bentuk agent tetap "
             "unverified; run 0101: 'tanpa Agent ID gate' vs klaim Boltbook 'Agent ID-gated' - konflik belum selesai, "
             "perlu ABI). Subagent: 263/3333, free lane terbuka, mint(1) 0 BNB sim bersih ~01:36 WIB (belum diverifikasi "
             "independen run ini). Tetap watchlist-only, BUKAN lead/kandidat.")})
# Believe BNB -> track_c watchlist-only-unverified
tc["BelieveBNB"] = {
    "sale": "0x2d15595d2e6EfB1c1EBf938Cd7Fd0f57d11C6b86",
    "token": "0x5e1A6b3041873b05d21C24Cce8c1af763846BeA7",
    "symbol": "BELIEVE", "track": "C",
    "status": "watchlist-only-unverified-2026-11-06",
    "site": "https://believebnb.xyz/",
    "x": "https://x.com/believebnbc",
    "boltbook": "https://boltbook.fun/p/nsLp3wqBdmF6?lang=en",
    "note": ("Temuan Boltbook run 0131: first share free (gas only), lalu ladder 353-tier dari 0.002 BNB; "
        "1 share = 50.000.000 token; pool buka di 10.000 share; 1.036/10.000 minted saat dicek ~01:44 WIB. "
        "VERIFIKASI RUN 0131 GAGAL LENGKAP: Sourcify ABI sale retry-exhausted (rate-limit), semua sale views None, "
        "fetch believebnb.xyz (200, 1381 byte, JS app) TIDAK mencetak alamat kontrak di HTML -> bentuk SALE (S1) "
        "UNVERIFIED, free pool + user quote UNVERIFIED, umur sale UNVERIFIED (token first mint 2026-11-05 20:37:18 WIB "
        "bukan pembukaan sale). BUKAN track-C lead/kandidat; dicek ulang run berikut. Bila Sourcify pulih dan bentuk "
        "S1 + pool + quote + umur terverifikasi -> evaluasi lead sesuai aturan."),
    "lastReadWib": RUN,
}
# AETHER -> excluded (age > 48h)
snap.setdefault("excluded", {})["AETHER-9265"] = {
    "address": "0x926504d174e99DB699141049b3Dd94dF501ff813",
    "symbol": "AETHER", "track": "A",
    "status": "excluded-age-over-48h-2026-11-06",
    "note": ("Situs aetheragent.site terverifikasi mencetak kontrak (fetch 200, 308.785 byte, prints_contract=True) "
        "dan Boltbook menyebut first 400 mint FREE - TAPI umur LEWAT: first mint on-chain blok 131083556 = "
        "2026-11-01 23:47:37 WIB (~4,4 hari saat run) > 48 jam, belum sold out (totalSupply 431). "
        "quote(user,1)=144922388336611 wei (~0.000145 BNB, bukan 0) -> free lane kemungkinan sudah lewat/tutup. "
        "Age rule excludes it; BUKAN lead/kandidat, TIDAK di-preview/di-mint."),
}

snap["last_run"] = "2026-11-06-0131"
snap["last_run_wib"] = RUN
snap["last_run_note"] = ("Run 0131 SILENT kecuali 1 EARLY LEAD baru: AgentX (first mint 01:21:38 WIB, 359 mint free, "
    "quote(user,1)=0). 0 kandidat, 0 strong lead baru/promosi, 0 lead/kandidat track-C, 0 pending claim baru/dibuka. "
    "Bridge TIDAK BERUBAH (113 kontrak, 7 same_owner_discarded; mtime 2026-11-04 17:40 UTC). "
    "Sourcify flaky run ini (banyak retry-exhausted via urllib; curl fallback di shape-check bekerja).")

json.dump(snap, open(HF + "onchain-snapshot.json", "w"), indent=1)
print("seen added:", added, "| snapshot contracts:", len(snap["contracts"]), "| track_c:", len(snap["track_c"]))
print("wrote onchain-snapshot.json + onchain-scan-seen.json + onchain-scan-state.json")
