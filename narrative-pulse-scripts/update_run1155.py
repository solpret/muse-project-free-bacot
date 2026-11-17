import json

PATH = "/home/hatch/workspace/narrative-pulse/state.json"

with open(PATH, encoding="utf-8") as f:
    s = json.load(f)

n_before = len(s["runs"])
sig_before = len(s.get("reported_signals", []))

entry = {
    "timestamp_wib": "2026-11-13 ~22:14-22:20 WIB",
    "timestamp_utc": "2026-11-13 15:14-15:20 UTC",
    "run_number": 1155,
    "jenis_run": "cek ringan (di luar jendela alert 18:00-22:00 WIB; run dijadwalkan 22:14 WIB)",
    "sumber_diperiksa": [
        "fast layer: fast_discovery.py exit 0, ~33,5 dtk; 56 token, 31 baru first-seen (created 14:54-15:10 UTC / 21:54-22:10 WIB). FDV menonjol: SABKCAT ~$65,83 jt (anomali, kemungkinan placeholder), CRO 0x6dc0... ~$106,81 rb, ChatGPT ~$103,93 rb, EX ~$339,70 rb, AR 0xe201... ~$70,27 rb; mayoritas FDV ~$3,2 rb bernama China + duplikat (暴力拉盘 x3, AR x3, Rufus x2, 羊羊有余 x2, CRO x2) — snapshot first-seen saja, BUKAN sinyal; tidak ada yang muncul di sumber narasi run ini",
        "X search: x_narrative.py exit 0, 2 token dicoba (0x924a076b3f4cb621266deae1750528d092e6700c dan 0x5e8c3bda24c74ca43ee0b86becfebab956bb7777) — KEDUANYA X-ERROR HTTP 402 credits exhausted; X search TIDAK TERSEDIA (kredit habis sejak 16:01 WIB hari ini, sudah dilaporkan sekali di run 1039, tidak dilaporkan ulang). 0 kredit dipakai run ini. Tidak ada hasil discussion yang dikarang.",
        "BlockBeats flash (browser.open en.theblockbeats.news/newsflash, crawl 15:17 UTC / 22:17 WIB): item terbaru — saham semikonduktor AS jatuh (AMD -9,2%, Philadelphia Semiconductor Index -5%), Fed Goolsbee hawkish (inflasi belum ke target 2%), OpenAI ChatGPT Wallet, Bybit WSOT 2026, parlemen AS vs Jensen Huang. TIDAK ADA satu pun item meme/BSC/BNB/four.meme/Genius.fun. Tidak ada callout KOL dengan CA terverifikasi",
        "four.meme Graduated (browser 22:17-22:20 WIB, https://four.meme/en?listedPancake=true, urut Creation Time): teratas NVDAB MC $122,53K (turun dari $138,15K run 1150), 366 holders (dari 331), 24H +3.849,89% (dari +4.148,75%), 1H -14,99%, 4H +223,81% — sudah berlipat, distribution watch; 小瓜 $6,48K, 135 holders, 24H +101,40%, vol 24j $112,89K (~17x MCAP) — anomali volume, sumber tunggal, BUKAN sinyal; VIP 人生 $2,26K, 354 holders, 24H -91,15%; JACKET/NVDAB $2,15K, 25 holders, 24H -34,62%; sisanya MC $1,95K-5,04K, 24H -6% s.d. +23%; tidak ada graduasi baru <1 jam yang teridentifikasi (situs tidak menampilkan jam graduasi; termuda 7 jam, NVDAB); tidak ada early mention di halaman detail NVDAB (Comments 'No comments yet'); riwayat pertumbuhan holder tidak dipublikasikan",
        "Log holder Mode B (holder-watchlist.md, run 20:30 WIB — terakhir): kedua halaman dompet GMGN LOGIN-GATED; money-flow TIDAK TERVERIFIKASI; streak detail tidak terbaca 92; cek on-chain 28/28 saldo terlacak, 0 berubah vs run 18:30 WIB; Dompet A ok + 旺财 tetap 100% hold (2/3); Dompet B hanya Ai Pro yang masih terbuka",
        "Tier-ab log run 97 (19:53 WIB): 0/54 halaman GMGN termuat publik, LOGIN-GATED, INCOMPLETE; 0 pembelian baru terverifikasi; BUKAN klaim tidak ada pembelian",
    ],
    "sumber_dilewati": [
        "Jinse flash (dicopot dari sumber wajib — buta 11 run berturut-turut; sudah dilaporkan sekali)",
        "Binance Square (deep-check saja bila ada kandidat — tidak ada kandidat run ini)",
        "Genius.fun Graduated (cek ringan di luar jendela alert; data terakhir run 1150: total 176, tidak ada lulusan baru <24 jam)",
        "PANews Meme Daily, Odaily headlines, Sharpe.ai, GMGN BSC trending, DexScreener BSC trending (opsional — cek ringan di luar jendela alert)",
    ],
    "hasil": "tidak ada sinyal awal baru — DIAM (run senyap, tidak ada pesan chat). NVDAB tetap distribution watch (sudah berlipat; MC turun dari run 1150). Tidak ada konvergensi multi-sumber; money-flow tidak terkonfirmasi (wallet-watchlist kosong by design; log holder Mode B login-gated).",
    "kredit_x_dipakai": 0,
    "catatan_tindak_lanjut": "Pantau 小瓜 di run berikutnya (vol 24j ~17x MCAP) hanya sebagai observasi, BUKAN sinyal. X search tetap tidak tersedia (HTTP 402, kredit twitterapi.io habis; sudah dilaporkan sekali di run 1039, tidak dilaporkan ulang) — isi ulang kredit butuh keputusan user. Run Mode B berikutnya ~22:30 WIB.",
}

s["runs"].append(entry)

# Update distribution_watch NVDAB entry (append-only)
nvdab_update = (
    " Update run 1155 (browser 22:17-22:20 WIB): masih Graduated teratas four.meme, "
    "MC $122,53K (turun dari $138,15K run 1150), holders 366 (dari 331), 24H +3.849,89% "
    "(dari +4.148,75%), 1H -14,99%, 4H +223,81% — tetap sudah berlipat, sumber tunggal, "
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
assert s2["runs"][-1]["run_number"] == 1155
assert len(s2.get("reported_signals", [])) == sig_before, "reported_signals changed!"
print("OK: runs", n_before, "->", len(s2["runs"]), "| reported_signals unchanged:", sig_before)
