import json
p='state.json'
s=json.load(open(p))
entry={
 "run_number": 1215,
 "waktu_run": "2026-11-14 13:14 WIB",
 "jenis_run": "cek ringan (di luar jendela alert 07:00-13:00 WIB; run dijadwalkan 13:14 WIB)",
 "klasifikasi": "tidak ada sinyal",
 "kredit_x_dipakai": 0,
 "sumber_diperiksa": [
  "Fast layer (fast_discovery.py, 13:15 WIB): 25 baru first-seen (pool created ~05:57-06:12 UTC / 12:57-13:12 WIB) — snapshot saja, bukan sinyal; FDV baru umumnya ~$3,2K (klon nama China: 黄仁勋 x3, SWJ x2, MOCO x2, CAPYRON, rodak, glory, dll). Terbesar: AFX 0x97aa...778a FDV ~$448.243, 大佬凤凰 0x8755...575d ~$356.410 (vol24 $88.138), 资本金融🐱 0x555e...869c ~$315.471, APE 0x5a9b...984e ~$230.853 (vol24 tertinggi $134.987), 现金牛 0x6eb0...b1c ~$87.390, PEPE 0x122b...7777 ~$86.975; tidak satu pun muncul di sumber narasi run ini sebagai token baru.",
  "X search (x_narrative.py, 13:15 WIB): TIDAK TERSEDIA — HTTP 402 twitterapi.io credits exhausted (2 token dicoba: APE 0x5a9b...984e, 大佬凤凰 0x8755...575d); 0 kredit dipakai; sudah dilaporkan sekali (run 1039, 12 Nov) untuk episode yang sama, tidak dilaporkan ulang; tidak ada X-HIT/X-MISS yang dikarang.",
  "BlockBeats flash (browser live 13:16-13:17 WIB): blockbeats.info/flash GAGAL DIMUAT — DNS tidak ter-resolve (DNS_PROBE_STARTED, 3x percobaan dengan dan tanpa www). Fallback en.theblockbeats.news/newsflash dibaca via text fetch 13:17 WIB (06:17 UTC): item teratas Michael Burry soal kepergian Jensen Huang — sarankan investor 'get out', bandingkan puncak Nasdaq dengan dot-com 2000, peringatkan AI boom bisa jadi 'bull trap', sebut CoreWeave/Nebius/TSMC bisa kena imbas — konteks makro/distribusi SWJ/NVDAB yang sudah dikenal run 1213/1214, bukan peluncuran token baru; TIDAK ADA flash BSC meme baru yang terlihat. Keterbatasan: fetch hanya menampilkan item teratas, bukan daftar 10 item penuh — sisi flash tidak terverifikasi penuh run ini (bukan 4 run berturut-turut buta; run 1209-1214 BlockBeats terbaca lewat jalur Inggris).",
  "four.meme Graduated (browser live 13:16-13:17 WIB): TIDAK ADA graduasi baru dalam 2 jam terakhir; termuda 1 hari: 裤裆里的黑天鹅 / NVDAB $176,35K, holders 431, 24H +5.574,13%, vol 24j $81,34K — sudah berlipat, distribution watch (mendingin dari $206,88K run 1214). Lainnya: JACKET/NVDAB $2,08K 31 holder 24j -33,37%; 小瓜 $6,2K 129 holder +96,58% 24j; VIP 人生 $2,08K 355 holder -92,39%; 安全驾驶 $2,13K; FDC $2,17K; frog $4,81K +34,80%; NB $1,98K; 真诚 $2K. SNDK dan AICAT masih di daftar (~$2K, 7-10 hari) — di lantai pasca-jatuh, bukan sinyal.",
  "Genius.fun (browser live 13:16-13:17 WIB): total Graduated 176 (tidak berubah); TIDAK ADA graduasi baru — 10 besar berumur 51-57 hari. Top: GSTOCK $3,32M (-0,76% 24j), MILAN $102,6K, GCAT $26,72K. On-curve termuda: Chief Everyone Officer $CEO umur 2 jam, $4,12K, 29 holder, progres 19,84%, pasangan NVDAB — BELUM graduated, turunan narasi NVDAB/SWJ; AsianStar 13 jam; Gull Thicket $GLTHK 5 jam; genius jacket $GJACKET 57 hari.",
  "Holder Mode B (log run 12:30 WIB, dibaca silang): GMGN detail login-gated (streak 100) — money-flow TIDAK TERVERIFIKASI, bukan klaim tidak ada pembelian baru; cek on-chain 28 saldo terverifikasi blok 133488134, 0 berubah; tidak satu pun CA fast layer run ini muncul di log holder.",
  "KOL ledger + wallet-watchlist (dibaca silang): tidak ada seruan KOL baru atas token/narasi di sumber run ini; wallet-watchlist masih kosong (belum ada wallet terpantau terverifikasi) — money-flow tidak dapat dikonfirmasi dari lapisan ini."
 ],
 "sumber_dilewati": "PANews Meme Daily, Odaily headlines, Sharpe.ai BNB meme narrative tracker, GMGN BSC trending, DexScreener BSC trending — opsional, tidak ada kandidat dari sumber wajib untuk deep-check; Binance Square — hanya deep-check bila ada kandidat, tidak ada kandidat run ini; Jinse flash — sudah dicopot dari sumber wajib (buta 11 run berturut-turut; dilaporkan sekali, jangan laporkan ulang kecuali pulih lalu buta lagi).",
 "hasil": "TIDAK ADA sinyal awal baru. Run diam (silent) sesuai aturan — tidak ada pesan chat. Narasi terkuat tetap Huang Renxun/Nvidia (BlockBeats Burry 'get out' soal kepergian Huang + NVDAB Graduated #1 + klon SWJ/黄仁勋 baru di fast layer) tapi semua token terkait sudah berlipat ribuan persen dan di puncak perhatian (NVDAB +5.574,13% 24j, MC $176,35K — mendingin dari $206,88K run 1214) = SUDAH RAMAI / distribution watch, bukan sinyal entry. Tidak ada graduasi launchpad baru (four.meme termuda 1 hari, Genius.fun Graduated termuda 8 hari). BlockBeats live gagal DNS tapi fallback Inggris terbaca — sisi flash tidak terverifikasi penuh run ini. KOL: tidak ada seruan baru (ledger tidak berubah). Wallet: money-flow tidak terverifikasi.",
 "kol_status": "tidak ada",
 "wallet_confirmation_status": "tidak terverifikasi (wallet-watchlist kosong; log holder Mode B 12:30 WIB tanpa perubahan)",
 "reported_signals_count": 24
}
assert len(s.get('reported_signals',[]))==24, "reported_signals berubah!"
before=len(s.get('runs',[]))
s['runs'].append(entry)
# Update singkat distribution_watch SWJ/NVDAB (entri AICAT, tempat update SWJ dicatat run-run sebelumnya)
for dw in s.get('distribution_watch',[]):
    if dw.get('token')=='AICAT':
        dw['status'] += " Update run 1215 (browser 13:16-13:17 WIB): NVDAB four.meme Graduated #1, MC $176,35K (dari $206,88K run 1214 — mendingin), holders 431, 24H +5.574,13%, umur 1 hari — sudah berlipat, tetap distribution watch, BUKAN sinyal entry; BlockBeats (fallback Inggris, blockbeats.info DNS gagal) item teratas Burry 'get out' soal kepergian Huang — konteks makro/distribusi, bukan peluncuran baru; CEO $4,12K on-curve Genius.fun (2 jam, progres 19,84%, pasangan NVDAB) turunan narasi yang sama, belum graduated; tidak dilaporkan ke user."
        break
json.dump(s, open(p,'w'), ensure_ascii=False, indent=1)
s2=json.load(open(p))
assert len(s2['runs'])==before+1 and s2['runs'][-1]['run_number']==1215
assert len(s2.get('reported_signals',[]))==24
print('OK run 1215 written; runs total:', len(s2['runs']))
