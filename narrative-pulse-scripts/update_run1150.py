import json

PATH = "/home/hatch/workspace/narrative-pulse/state.json"

with open(PATH, encoding="utf-8") as f:
    s = json.load(f)

n_before = len(s["runs"])
sig_before = len(s.get("reported_signals", []))

entry = {
    "timestamp_wib": "2026-11-13 ~20:59-21:05 WIB",
    "timestamp_utc": "2026-11-13 13:59-14:05 UTC",
    "run_number": 1150,
    "jenis_run": "pulse penuh (jendela alert 18:00-22:00 WIB; run dijadwalkan 20:59 WIB)",
    "sumber_diperiksa": [
        "fast layer: fast_discovery.py exit 0, ~28,8 dtk; 54 token, 38 baru first-seen (created 20:44-20:57 WIB / 13:44-13:57 UTC). FDV menonjol: Yellow Pow ~$103,7 rb, Buffape ~$94,2 rb, GPTR ~$323,4 rb, 苹果人生 ~$17,5 rb, ELON/TRUMP FDV miliaran (anomali, kemungkinan placeholder); mayoritas FDV ~$3,2 rb bernama China + duplikat (洋葱, 希加加, 蛙妃, 黄鲸, PIKA, Rocket) — snapshot first-seen saja, BUKAN sinyal; tidak ada yang muncul di sumber narasi run ini",
        "X search: x_narrative.py exit 0 tetapi TIDAK TERSEDIA — X-ERROR HTTP 402 kredit twitterapi.io habis untuk 2 token (0xe4ce6f8caa3a76a53fdad70f2af393c01ecd7777 dan 0x3af23abc33da341a13232e33af0a27220b905309); sudah dilaporkan sekali di run 1039, tidak dilaporkan ulang; 0 kredit dipakai",
        "BlockBeats flash (browser 21:01-21:05 WIB): halaman /flash HTTP 404 dua kali (21:02 dan 21:04 WIB); beranda berhasil dimuat, flash dibaca dari kolom \"最新快讯\" beranda (21:04 WIB), 8 item terbaru, TIDAK ADA item memecoin BSC baru dalam 30-60 menit terakhir. Narasi dominan: pengunduran diri Jensen Huang/Nvidia, PPI AS 6,5%, BTC >$70.000. Satu artikel meme soal Pump.fun — bukan BSC. Tidak ada callout KOL dengan CA terverifikasi",
        "four.meme Graduated (browser ~21:04 WIB): teratas 裤裆里的黑天鹅/NVDAB MC $138,15K, 331 holders, 24H +4.148,75%, umur 6 jam (dari $136,84K/325/+4.101,05% run 1149) — sudah berlipat, distribution watch; JACKET/NVDAB $2,21K, 26 holders, 24H -32,17% — identik run 1149; 小瓜 $6,76K, 135 holders, 24H +107,54% tetapi 1H -13,77%/4H -34,09% — jatuh cepat; frog $5,11K, 166 holders, 24H +26,23% tetapi sumber tunggal; tidak ada graduasi baru <1 jam (termuda 6 jam); tag trending: jacket, 皮衣, four, leather, meme — klaster jacket/皮衣 sejalan narasi Huang/Nvidia. Catatan daftar umum: 币安股票/USDT umur 24 mnt, MC $7,01K, 1j +120,72%, progres 43,89% — BELUM graduated, sumber tunggal, sudah +120% dalam 1 jam, BUKAN sinyal",
        "Genius.fun Graduated (browser ~21:04 WIB): total tetap 176, TIDAK ADA lulusan baru <24 jam; termuda 51 hari; teratas GSTOCK $3,51 jt, 8.825 holders, 24H +1,26%, vol 24j $33,63K; momentum 24j positif yang menonjol hanya Genius Cat +14,17%; on-curve terbaru 牛逼 (1 jam, 1 holder) dan 天才交易员 (1 jam, 0 holder)",
        "Log holder Mode B (holder-watchlist.md, run 20:30 WIB): kedua halaman dompet GMGN LOGIN-GATED; money-flow TIDAK TERVERIFIKASI; streak detail tidak terbaca 92; cek on-chain 28/28 saldo terlacak, 0 berubah vs run 18:30 WIB; Dompet A ok + 旺财 tetap 100% hold (2/3); Dompet B hanya Ai Pro yang masih terbuka",
        "Tier-ab log run 97 (19:53 WIB): 0/54 halaman GMGN termuat publik, LOGIN-GATED, INCOMPLETE; 0 pembelian baru terverifikasi; BUKAN klaim tidak ada pembelian",
    ],
    "sumber_dilewati": [
        "Jinse flash (dicopot dari sumber wajib — buta 11 run berturut-turut; sudah dilaporkan sekali)",
        "Binance Square (deep-check saja bila ada kandidat — tidak ada kandidat run ini)",
        "PANews Meme Daily, Odaily headlines, Sharpe.ai, GMGN BSC trending, DexScreener BSC trending (opsional — waktu tidak tersisa; browser selesai 21:05 WIB)",
    ],
    "hasil": "tidak ada sinyal awal baru — DIAM (run senyap, tidak ada pesan chat). NVDAB tetap distribution watch (sudah tercatat, update di distribution_watch). Tidak ada konvergensi multi-sumber; money-flow tidak terkonfirmasi (wallet-watchlist kosong by design; log holder Mode B login-gated).",
    "kredit_x_dipakai": 0,
    "catatan_tindak_lanjut": "Pantau 币安股票/USDT (on-curve four.meme 43,89%, umur 24 mnt, 1j +120,72%) di run berikutnya bila graduate — sumber tunggal run ini, BUKAN sinyal. X search tetap tidak tersedia (HTTP 402, kredit twitterapi.io habis; sudah dilaporkan sekali di run 1039, tidak dilaporkan ulang) — isi ulang kredit butuh keputusan user. BlockBeats /flash HTTP 404 dua kali run ini; bila terulang, baca flash dari kolom beranda seperti run ini.",
}

s["runs"].append(entry)

# Update distribution_watch NVDAB entry (append-only)
nvdab_update = (
    " Update run 1150 (browser 21:01-21:05 WIB): masih Graduated teratas four.meme, "
    "MC $138,15K (dari $136,84K run 1149), holders 331 (dari 325), 24H +4.148,75% "
    "(dari +4.101,05%), 1H -11,79%, 4H +246,96% — tetap sudah berlipat, sumber tunggal, "
    "tetap distribution watch, BUKAN sinyal entry; tidak dilaporkan ke user."
)
found = False
for e in s.get("distribution_watch", []):
    if isinstance(e, dict) and "NVDAB" in e.get("token", ""):
        e["status"] = e.get("status", "") + nvdab_update
        found = True
        break
assert found, "NVDAB distribution_watch entry not found"

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)

# Verify
with open(PATH, encoding="utf-8") as f:
    s2 = json.load(f)
assert len(s2["runs"]) == n_before + 1, "runs count mismatch"
assert s2["runs"][-1]["run_number"] == 1150
assert len(s2.get("reported_signals", [])) == sig_before, "reported_signals changed!"
print("OK: runs", n_before, "->", len(s2["runs"]), "| reported_signals unchanged:", sig_before)
