import json
p='state.json'
s=json.load(open(p))
entry={
 "run_number": 1208,
 "waktu_run": "2026-11-14 11:30 WIB",
 "jenis_run": "pulse penuh (jendela alert 07:00-13:00 WIB; run dijadwalkan 11:29 WIB)",
 "klasifikasi": "tidak ada sinyal",
 "kredit_x_dipakai": 0,
 "sumber_diperiksa": [
  "Fast layer (fast_discovery.py, 11:30 WIB): 57 token, 28 baru first-seen (pool created ~04:03-04:28 UTC / 11:03-11:28 WIB) — snapshot saja, bukan sinyal; FDV baru umumnya ~$3,2K (klon nama China). Terbesar: RAYC 0x1aaa...d49 FDV $51,9 jt (TIDAK terkonfirmasi — artefak, lihat verifikasi browser di bawah), MOON 0x35c5...d23 $216.111, SWJ 0x73f7...7777 $133.481, 牛逼 0x18f9...6088 $79.681, tinfoil 0xece1...7777 $71.994, SWJ 0xae1c...7777 $59.339; tidak satu pun muncul di sumber narasi run ini sebagai token baru (SWJ/NVDAB sudah distribution watch).",
  "X search (x_narrative.py, 11:31 WIB): TIDAK TERSEDIA — HTTP 402 twitterapi.io credits exhausted (2 token dicoba: 0x0fbb...6047, MOON 0x35c5...d23); 0 kredit dipakai; sudah dilaporkan sekali hari ini (run 04:00 WIB), tidak dilaporkan ulang; tidak ada X-HIT/X-MISS yang dikarang.",
  "BlockBeats flash (browser live 11:32-11:35 WIB, www.theblockbeats.info/newsflash — domain tanpa www tampil Not Found, blockbeats.info gagal DNS): 10 item terbaru 09:51-11:30 WIB. TIDAK ADA item BSC memecoin/token meme baru. Pasar bearish/panik: Fear & Greed 12 (kemarin 20), BTC rebound $67.000 (-2,65% 24j, -12% 7 hari), ETH ~$1.900-an. Narasi Huang Renxun/Nvidia mendominasi beranda (HSBC pangkas NVDA ke Hold target $365->170, petisi pengembalian >11.000 tanda tangan, akun Polymarket 'orang dalam Nvidia' bangkrut) — lanjutan narasi yang sama, sudah distribution watch sejak run 1197.",
  "four.meme Graduated (browser ~11:33 WIB): TIDAK ADA graduasi <2 jam (terbaru 21 jam). Teratas: 裤裆里的黑天鹅/NVDAB MC $202,86K, 21 jam, 415 holder, 24H +6.447,94% (naik dari $172,81K run 1207) — tetap distribution watch. Tag panas: swj, 红果. SWJ belum graduated (SWJ/NVDAB $4,93K 5 jam, 8 holder; SWJ/BNB $3,11K 5 jam). SNDK $2,14K 7 hari +0,94% 24H. FDC $2,17K 3 hari -14,72% (sudah reported_signal). frog $4,81K 3 hari +34,80% (sudah reported_signal).",
  "Genius.fun Graduated (browser ~11:33 WIB): total 176, TIDAK ADA graduasi <2 jam (termuda 51 hari, GPU $9,82K). Teratas GSTOCK $3,36 jt -15,95% 24H, MILAN $101,2K, GCAT $26,41K. Trending #1 CEO vol $15,26K. Live terbaru: Chief Everyone Officer $CEO/NVDAB MC $4,34K, 41 holder, 1H -44,58%, progres 23,16%, umur 1 jam + klon kedua $3,29K 0 holder 57 menit — belum graduated, banyak klon, konvergensi lemah, BUKAN sinyal.",
  "DexScreener BSC trending 6H (browser ~11:34 WIB, vol BSC 24j $2,41 miliar): #1 SWJ/NVDAB MC $455K, 6 jam, vol $2,2 jt, 6H +1.213%, 1H -8,26% (mendingin); #2 AGC $393K +38,30% 24H; #4 Jacket/NVDAB $2,0 jt +2.755% 24H. Tidak ada token <6 jam di 10 besar; termuda SWJ tepat 6 jam.",
  "Verifikasi RAYC 0x1aaafebb2247616a8f290115df8d63acaac47d49 (browser): FDV $51,9 jt TIDAK terkonfirmasi — artefak. DexScreener: likuiditas $0, FDV $0, pair 5 hari, Go+ 3 masalah. GeckoTerminal: harga $0,2777 (=0,006967 LUSD) menyiratkan LUSD ~$39,85 — salah penetapan harga quote pada pool nyaris tanpa likuiditas (cadangan 2.443 RAYC + 16,83 LUSD, keduanya ~$0); vol 24j $5,85, 1 tx. Klaim 'pool dibuat 04:05 UTC hari ini' bertentangan dengan umur 5 hari di kedua sumber. BUKAN sinyal; dicatat agar tidak diulang sebagai kandidat.",
  "Holder Mode B (log run 10:30 WIB, dibaca silang): cek on-chain 28 saldo terverifikasi blok 133472130, 0 berubah; GMGN detail login-gated (streak 99) — money-flow TIDAK TERVERIFIKASI, bukan klaim tidak ada pembelian baru; kandidat fast layer tidak bersilangan dengan log holder.",
  "KOL ledger + wallet-watchlist (dibaca silang): tidak ada seruan KOL baru atas token/narasi di sumber run ini; wallet-watchlist masih kosong (belum ada wallet terpantau terverifikasi) — money-flow tidak dapat dikonfirmasi dari lapisan ini."
 ],
 "sumber_dilewati": "PANews Meme Daily, Odaily headlines, Sharpe.ai BNB meme narrative tracker, GMGN BSC trending — opsional, tidak ada kandidat dari sumber wajib untuk deep-check; Binance Square — hanya deep-check bila ada kandidat, tidak ada kandidat run ini; Jinse flash — sudah dicopot dari sumber wajib (buta 11 run berturut-turut; dilaporkan sekali, jangan laporkan ulang kecuali pulih lalu buta lagi).",
 "hasil": "TIDAK ADA sinyal awal baru. Run diam (silent) sesuai aturan — tidak ada pesan chat. Konvergensi terkuat tetap narasi Huang Renxun/Nvidia (BlockBeats + four.meme tag 'swj' + DexScreener #1 SWJ + NVDAB Graduated #1) tapi token terkait sudah di puncak perhatian dan mendingin (SWJ 1H -8,26%, NVDAB +6.447% 24H) = SUDAH RAMAI / distribution watch, bukan sinyal entry. CEO (Genius live 1 jam, -44,58% 1H, klon) bukan sinyal. RAYC terbukti artefak FDV, bukan token baru. KOL: tidak ada seruan baru (ledger tidak berubah). Wallet: money-flow tidak terverifikasi.",
 "kol_status": "tidak ada",
 "wallet_confirmation_status": "tidak terverifikasi (wallet-watchlist kosong; log holder Mode B 10:30 WIB tanpa perubahan)",
 "reported_signals_count": 24
}
assert len(s.get('reported_signals',[]))==24, "reported_signals berubah!"
before=len(s.get('runs',[]))
s['runs'].append(entry)
json.dump(s, open(p,'w'), ensure_ascii=False, indent=1)
s2=json.load(open(p))
assert len(s2['runs'])==before+1 and s2['runs'][-1]['run_number']==1208
assert len(s2.get('reported_signals',[]))==24
print('OK run 1208 written; runs total:', len(s2['runs']))
