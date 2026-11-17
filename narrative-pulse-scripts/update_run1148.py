#!/usr/bin/env python3
"""Update state.json for narrative-pulse run 1148 (2026-11-13 ~20:29 WIB).
Additive only: appends one run entry and appends update text to four
existing distribution_watch entries (NVDAB, AICAT, SNDK, xiaogua).
Never touches reported_signals or existing runs. Atomic replace."""
import json, os

STATE = os.path.expanduser("~/workspace/narrative-pulse/state.json")

with open(STATE) as f:
    st = json.load(f)

assert isinstance(st, dict)
n_runs_before = len(st.get("runs", []))
n_sig_before = len(st.get("reported_signals", []))

run_entry = {
    "timestamp_wib": "2026-11-13 ~20:29-20:38 WIB",
    "timestamp_utc": "2026-11-13 13:29-13:38 UTC",
    "run_number": 1148,
    "jenis_run": "pulse penuh (jendela alert 18:00-22:00 WIB; run dijadwalkan 20:29 WIB)",
    "sumber_diperiksa": [
        "fast layer: fast_discovery.py exit 0, ~9,5 dtk; 33 token first-seen dalam 30 menit terakhir (created 20:11-20:27 WIB per output). FDV menonjol: YellowRoom ~$139,8 rb, WHAL\u6708 ~$116,8 rb, \u5927\u5934\u513f\u5b50 ~$109,5 rb, RKNS FDV ~$819 jt (anomali, kemungkinan spoof/harga placeholder), GANG/USDT ~$19,1 rb, \u76ae\u8863 ~$13,9 rb, \u4e2d\u672c\u806a ~$24,7 rb \u2014 snapshot first-seen saja, BUKAN sinyal; tidak ada yang muncul di sumber narasi run ini",
        "X search: x_narrative.py exit 0 tetapi TIDAK TERSEDIA \u2014 X-ERROR HTTP 402 kredit twitterapi.io habis untuk 2 token (0xe4ce6f8caa3a76a53fdad70f2af393c01ecd7777 dan 0x726e05f53e9daf89f063f06b03947f7fd4329935); kondisi sudah dilaporkan sekali di run 1039, tidak dilaporkan ulang; streak gagal 85 run; 0 kredit dipakai",
        "BlockBeats flash (browser 20:33 WIB, en.theblockbeats.news/newsflash): 20 flash terbaru 18:16-20:30 WIB, TIDAK ADA item memecoin BSC / meme BNB Chain / launchpad; yang terdekat dengan BNB hanya Binance-Anthropic perpetual pra-pasar (18:35), penarikan whale BTC dari Binance (18:29), dan penyebutan Binance dalam kasus DOJ (19:15) \u2014 semuanya bukan sinyal memecoin; ticker SNDK di bilah atas adalah saham Sandisk, bukan token; tidak ada callout KOL dengan CA terverifikasi. BlockBeats PULIH setelah gagal dimuat run 1147 (buta run ke-1) \u2014 streak buta reset ke 0",
        "four.meme Graduated (browser ~20:34 WIB): teratas \u88e4\u88c6\u91cc\u7684\u9ed1\u5929\u9e45/NVDAB MC $135,87K, 322 holders, 24H +4.093,23%, umur 6 jam (naik dari $115,54K/237 holders run 1144) \u2014 sudah berlipat, distribution watch; JACKET/NVDAB nama segar $2,21K, 26 holders, 24H -32,17% \u2014 kecil dan melemah, bukan sinyal; \u5c0f\u74dc $7,82K, 139 holders, 24H +140,67% tetapi 1H -10,16% \u2014 mendingin; tidak ada graduasi baru <5 jam (termuda 6 jam); chip trending: jacket, \u76ae\u8863, four, leather, meme \u2014 tema jaket kulit konvergen dengan berita Nvidia/Jensen Huang di BlockBeats, tetapi token terkait sudah berlipat (NVDAB) atau kecil dan melemah (JACKET)",
        "Genius.fun Graduated (browser ~20:34 WIB): total tetap 176, tidak ada lulusan baru; termuda tetap Genius Dog ($GDOG) MC $5,27K, 44 holders, umur 8 hari, 24H -9,10%; di daftar All terlihat genius jacket $GJACKET (pasangan NVDAB, $3,3K, 57 hari, 1 holder, progres 4,28%) \u2014 belum graduated dan sudah tua, token BERBEDA dari JACKET four.meme, jangan dicampur",
        "Log holder Mode B (holder-watchlist.md, run 20:30 WIB): kedua halaman dompet GMGN LOGIN-GATED (Dompet A dan Dompet B, keduanya ~20:35 WIB; masing-masing dimuat ulang sekali, tetap login-gated); money-flow TIDAK TERVERIFIKASI; streak detail tidak terbaca 92; cek saldo on-chain (holder-balance-check-parallel.py, blok 133360466): 28/28 terbaca, 0 gagal, 0 berubah vs run 18:30 WIB; Dompet A ok + \u65fa\u8d22 tetap 100% hold; Dompet B hanya Ai Pro yang masih terbuka. Wallet-watchlist tetap KOSONG (belum ada wallet terpantau terverifikasi) \u2014 money-flow tidak dapat dikonfirmasi. Kol-ledger: tidak ada seruan KOL baru dengan CA terverifikasi"
    ],
    "sumber_dilewati": [
        "PANews Meme Daily, Odaily headlines, Sharpe.ai, GMGN trending, DexScreener trending (opsional \u2014 waktu run dipakai sumber wajib + browser; tidak ada kandidat dari fast layer/sumber wajib yang butuh deep-check)",
        "Binance Square (deep-check saja \u2014 tidak ada kandidat)",
        "GM On curve Genius.fun tidak diverifikasi ulang run ini (hanya $GJACKET yang terlihat di daftar All \u2014 token berbeda)"
    ],
    "hasil": "tidak ada sinyal baru \u2014 DIAM ke chat. Tidak ada konvergensi multi-sumber; konvergensi tema jaket kulit tercatat tetapi token terkait sudah berlipat atau melemah; tidak ada graduation baru <5 jam; X search tidak tersedia (kredit habis); BlockBeats pulih",
    "kredit_x_dipakai": 0
}

st.setdefault("runs", []).append(run_entry)

updates = {
    "NVDAB": " Update run 1148 (browser ~20:34 WIB): masih Graduated teratas four.meme, MC $135,87K (naik dari $115,54K run 1144; sempat $113,24K run 1147), holders 322 (dari 237 run 1144), 24H +4.093,23%, umur 6 jam, vol 24j $31,21K, 1H +186,08% \u2014 sudah berlipat, BUKAN sinyal entry; sumber tunggal run ini (tidak muncul di BlockBeats, Genius.fun, X, maupun log holder/tier-ab run ini); tetap distribution watch; tidak dilaporkan ke user.",
    "AICAT": " Update run 1148 (browser ~20:34 WIB): masih Graduated four.meme, MC $1,79K, holders 176, 24H +0,11%, umur 9 hari, vol 24j hanya $1,97 \u2014 identik dengan run 1147 ($1,79K/176/+0,11%/9 hari); praktis mati/datar; tetap distribution watch, BUKAN sinyal entry; tidak dilaporkan ke user.",
    "SNDK": " Update run 1148 (browser ~20:34 WIB): SNDK 0x9557...ffff MC $2,14K, holders 98, 24H +0,94%, umur 6 hari; SNDK kedua 0xd66b...ffff MC $1,98K, holders 62, 24H -0,78%, umur 7 hari \u2014 identik dengan run 1147 ($2,14K/98/+0,94%/6 hari); tetap di lantai pasca-jatuh dari ~$136,59K; tetap distribution watch, BUKAN sinyal entry; tidak dilaporkan ke user.",
}
for e in st.get("distribution_watch", []):
    tok = e.get("token", "")
    for key, txt in updates.items():
        if key in tok and "QCOM" not in tok:
            e["status"] = e.get("status", "") + txt

# xiaogua: append only to the LATEST entry (last one with token exactly "xiaogua")
xiaogua_idx = [i for i, e in enumerate(st.get("distribution_watch", [])) if e.get("token", "") == "\u5c0f\u74dc"]
if xiaogua_idx:
    i = xiaogua_idx[-1]
    st["distribution_watch"][i]["status"] = st["distribution_watch"][i].get("status", "") + " Update run 1148 (browser ~20:34 WIB): masih Graduated four.meme, MC $7,82K (dari $8,54K run ~1143), holders 139 (dari 146), umur 7 jam, vol 24j $111,92K, 24H +140,67% tetapi 1H -10,16% dan 5M -0,38% \u2014 mendingin setelah naik; BUKAN sinyal entry; tetap distribution watch; tidak dilaporkan ke user."

assert len(st["runs"]) == n_runs_before + 1, "run count mismatch"
assert len(st.get("reported_signals", [])) == n_sig_before, "reported_signals changed!"

tmp = STATE + ".tmp1148"
with open(tmp, "w") as f:
    json.dump(st, f, indent=1, ensure_ascii=False)
os.replace(tmp, STATE)
print(f"OK run 1148 appended: runs {n_runs_before} -> {len(st['runs'])}, reported_signals unchanged at {n_sig_before}")
