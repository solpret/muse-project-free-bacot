#!/usr/bin/env python3
"""Append run 1195 entry + distribution-watch updates to narrative-pulse state.json.
Guards: backs up first; verifies runs count and last run_number before writing;
never touches reported_signals."""
import json, shutil, sys

P = "/home/hatch/workspace/narrative-pulse/state.json"
shutil.copyfile(P, P + ".bak-run-1195-20261114")

with open(P) as f:
    s = json.load(f)

runs = s.get("runs", [])
assert len(runs) == 1194, f"unexpected runs count {len(runs)}"
last = runs[-1]
assert last.get("run_number", 1194) == 1194 or "08:00" in str(last.get("waktu_run", "")), "last run mismatch"
assert len(s.get("reported_signals", [])) == 24, "reported_signals changed unexpectedly"

entry = {
    "run_number": 1195,
    "waktu_run": "2026-11-14 08:15 WIB",
    "jenis_run": "pulse penuh (jendela alert 07:00-13:00 WIB; run dijadwalkan 08:14 WIB)",
    "sumber_diperiksa": [
        "Fast layer (fast_discovery.py): 62 token baru first-seen dalam 30 menit terakhir — snapshot saja, bukan sinyal; FDV terbesar: UDORA 0xd2a4...10ba ~$9,57 jt, FORTCAT 0x42a3...de6 ~$2,06 jt, BEAR 0x78c3...de31 ~$440 rb, POP🌟 0x4fb2...6641 ~$386 rb",
        "X search (x_narrative.py): TIDAK TERSEDIA — HTTP 402 twitterapi.io credits exhausted (2 token dicoba: BEAR 0x78c3..., POP🌟 0x4fb2...); 0 kredit dipakai; sudah dilaporkan sekali di run 1039, tidak dilaporkan ulang",
        "BlockBeats flash (en.theblockbeats.news/newsflash, browser 08:16-08:17 WIB): 10 item terbaru 14 Nov — didominasi suksesi CEO Nvidia (petisi kembalikan Jensen Huang >11.000 tanda tangan; dewan belum resmi dekati kandidat; peluang CEO Arm 36%), likuidasi >$1,3 miliar/24j (158.996 orang), Hyperliquid OI rekor $16,8 miliar. TIDAK ADA satu pun item BSC/BNB/memecoin. 'SNDK' yang muncul adalah saham SanDisk (SNDK.O -5,59%), bukan token meme.",
        "four.meme Graduated (browser 08:16-08:17 WIB): teratas 裤裆里的黑天鹅/NVDAB MC $138,62K, 383 holder, +4.387,37% 24j, umur 17 jam, vol 24j $57,41K; JACKET/NVDAB $2,05K, 28 holder, -34,53%, 18 jam; 小瓜 $6,71K, 132 holder, +109,94%, 19 jam, vol 24j $113,67K; AICAT $1,79K, 176 holder, +0,11%, 10 hari (identik run 1185); SNDK $2,14K/98/+0,94% dan SNDK kedua $1,98K/62/-0,78% (identik run 1185). GM, FAGENT, JAGENT tidak terlihat di halaman 1.",
        "Genius.fun (browser 08:16-08:17 WIB): total Graduated 176, All 21.679; TIDAK ADA graduasi baru <24 jam (termuda Genius Dog $GDOG 8 hari, $5,15K, 44 holder, -8,71%); top MC Gstock $GSTOCK $3,51 jt, 8.816 holder, -10,74%; Genius Morning $GM $6,97K, 1.067 holder, -1,12%, 56 hari (sudah distribution watch). On-curve: klaster duplikat AsianStar/Asian Star 7-8 jam, MC ~$3,78K, progres <8% (satu entri vol $31,92K, 18 holder), $gAI 7 jam vol $9,61K, genius jacket $GJACKET pasangan NVDAB (57 hari, progres 8,27%, 3 holder).",
        "Holder Mode B (log 06:30 WIB, dibaca silang): cek on-chain 28 saldo terverifikasi blok 133440173, 0 berubah; GMGN detail login-gated (streak 97) — money-flow TIDAK TERVERIFIKASI run ini; tidak ada pembelian awal baru yang terkonfirmasi untuk token fast layer mana pun",
        "Tier-ab (log run 100, 07:53-07:54 WIB, dibaca silang): 0/54 halaman GMGN terbaca (login-gated sejak wallet pertama); 0 pembelian baru terverifikasi; flag klaster run 49 tidak bisa diverifikasi ulang",
        "KOL ledger + wallet-watchlist (dibaca silang): tidak ada seruan KOL baru di sumber run ini; wallet-watchlist masih kosong (belum ada wallet terpantau terverifikasi) sehingga money-flow tidak dapat dikonfirmasi",
    ],
    "sumber_dilewati": "PANews Meme Daily, Odaily headlines, Sharpe.ai, GMGN BSC trending, DexScreener trending/new pairs — opsional, tidak ada kandidat dari sumber wajib untuk deep-check; Binance Square — hanya deep-check bila ada kandidat, tidak ada kandidat run ini; Jinse flash — sudah dicopot dari sumber wajib (buta 11 run).",
    "hasil": "TIDAK ADA sinyal awal baru. Run diam (silent) sesuai aturan — tidak ada pesan chat. Konvergensi tema Nvidia/NVDAB lintas sumber (BlockBeats suksesi CEO Nvidia + NVDAB teratas four.meme + GJACKET pasangan NVDAB di Genius.fun) TAPI token utama sudah +4.387,37% dalam 24 jam (MC $138,62K) = SUDAH RAMAI/distribution watch, bukan sinyal entry; klaster AsianStar duplikat = pola peniru, bukan konvergensi bersih; 小瓜 +109,94% sumber tunggal; tidak satu pun token fast layer muncul di 2+ sumber narasi; X search tidak tersedia (kredit habis, sudah dilaporkan sekali di run 1039); money-flow tidak terverifikasi (Mode B login-gated, tier-ab 0/54); wallet-watchlist masih kosong.",
    "kredit_x_dipakai": 0,
    "reported_signals_count": 24,
}
runs.append(entry)

dw = s["distribution_watch"]

def find_dw(pred):
    for e in dw:
        if pred(e):
            return e
    raise SystemExit("distribution_watch entry not found")

# NVDAB latest entry (token contains NVDAB, most recent by run ~06:06 WIB)
nvdab = find_dw(lambda e: e.get("token", "").startswith("裤裆里的黑天鹅 / $NVDAB") and "06:06" in e.get("status", ""))
nvdab["status"] += (" Update run 1195 (browser 08:16-08:17 WIB): masih Graduated teratas four.meme, MC $138,62K (dari $128,14K run ~06:06 WIB), "
    "holders 383 (dari 378), 24H +4.387,37%, umur 17 jam, vol 24j $57,41K — sudah berlipat ribuan persen, tetap distribution watch, BUKAN sinyal entry; "
    "konvergensi tema dengan BlockBeats (suksesi CEO Nvidia mendominasi flash) + GJACKET pasangan NVDAB di Genius.fun, tapi narasi sudah dimainkan; tidak dilaporkan ke user.")

# 小瓜 latest entry (run 1178 update inside entry starting with 小瓜, status contains 03:44)
xiaogua = find_dw(lambda e: e.get("token", "") == "小瓜" and "03:44" in e.get("status", ""))
xiaogua["status"] += (" Update run 1195 (browser 08:16-08:17 WIB): masih Graduated four.meme, MC $6,71K (dari $8,08K run 1178), holders 132, "
    "24H +109,94%, umur 19 jam, vol 24j $113,67K — sudah naik >2x, sumber tunggal, BUKAN sinyal entry; tidak dilaporkan ke user.")

aicat = find_dw(lambda e: e.get("token", "") == "AICAT")
aicat["status"] += (" Update run 1195 (browser 08:16-08:17 WIB): masih Graduated four.meme, MC $1,79K, holders 176, 24H +0,11%, umur 10 hari — "
    "identik dengan run 1185 ($1,79K/176/+0,11%); tetap distribution watch, BUKAN sinyal entry; tidak dilaporkan ke user.")

snd = find_dw(lambda e: e.get("token", "") == "SNDK")
snd["status"] += (" Update run 1195 (browser 08:16-08:17 WIB): masih Graduated four.meme, MC $2,14K, holders 98, 24H +0,94%, umur 6 hari; "
    "SNDK kedua 0xd66b...ffff MC $1,98K, holders 62, 24H -0,78%, umur 8 hari — identik dengan run 1185 ($2,14K/98/+0,94%); "
    "tetap di lantai pasca-jatuh dari ~$136,59K; tetap distribution watch, BUKAN sinyal entry; tidak dilaporkan ke user.")

dw.append({
    "token": "AsianStar / Asian Star (klaster duplikat, CA tidak terverifikasi)",
    "status": "distribution watch run narasi 1195 (browser 08:16-08:17 WIB): klaster token duplikat AsianStar/Asian Star di Genius.fun On-curve, umur 7-8 jam, MC ~$3,78K, progres bonding curve <8% (satu entri vol $31,92K, 18 holder; entri lain $1,99K/$1,75K/$1,09K) — banyak token duplikat bernama sama, pola peniru, BUKAN konvergensi bersih; belum graduated, sumber tunggal (hanya Genius.fun); CA tidak dicatat karena tidak diverifikasi on-chain run ini; tidak dilaporkan ke user",
})

with open(P, "w") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)

# verify
with open(P) as f:
    s2 = json.load(f)
assert len(s2["runs"]) == 1195 and s2["runs"][-1]["run_number"] == 1195
assert len(s2["reported_signals"]) == 24
assert len(s2["distribution_watch"]) == 92
print("OK run 1195 written; runs:", len(s2["runs"]), "signals:", len(s2["reported_signals"]), "dw:", len(s2["distribution_watch"]))
