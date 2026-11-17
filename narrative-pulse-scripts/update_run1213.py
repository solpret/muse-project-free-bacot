import json
p='state.json'
s=json.load(open(p))
entry={
 "run_number": 1213,
 "waktu_run": "2026-11-14 12:44 WIB",
 "jenis_run": "pulse penuh (jendela alert 07:00-13:00 WIB; run dijadwalkan 12:44 WIB)",
 "klasifikasi": "tidak ada sinyal",
 "kredit_x_dipakai": 0,
 "sumber_diperiksa": [
  "Fast layer (fast_discovery.py, 12:45 WIB): 58 token, 43 baru first-seen (pool created ~05:26-05:42 UTC / 12:26-12:42 WIB) — snapshot saja, bukan sinyal; FDV baru umumnya ~$3,2K (klon nama China). Terbesar: 123 0x9134...b7c6 FDV ~$2,37 T (artefak FDV palsu), TRUMP 0xfe56...3e16 FDV ~$4,97 M (artefak/nama lama, bukan token baru), tinfoil 0xe5a2...7777 $78.596, 一苇渡 0xd61d...7777 $60.953, JinGuiXu 0x3c6a...ff2f $13.557, SPAM 0x1f60...3a2 $8.617; tidak satu pun muncul di sumber narasi run ini sebagai token baru.",
  "X search (x_narrative.py, 12:45 WIB): TIDAK TERSEDIA — HTTP 402 twitterapi.io credits exhausted (2 token dicoba: 0x70ce...7777, 0xb8f0...86cb); 0 kredit dipakai; sudah dilaporkan sekali (run 1039, 12 Nov) untuk episode yang sama, tidak dilaporkan ulang; tidak ada X-HIT/X-MISS yang dikarang.",
  "BlockBeats flash (browser live 12:46-12:48 WIB, en.theblockbeats.news/newsflash): 10 item terbaru 10:54-12:42 WIB. TIDAK ADA item BSC memecoin/token meme baru. Michael Burry tambah short Nasdaq/saham semikonduktor, peringatkan AI boom bisa jadi 'bull market trap', soal kepergian Jensen Huang sarankan investor 'get out' (12:42) — konteks makro/distribusi SWJ/NVDAB, bukan peluncuran token. DI (Decentralized Intelligence) pendanaan baru valuasi $100 jt (OKX Ventures) — bukan memecoin BSC. Trump ke Asia bawa Musk, hindari bahas Nvidia (12:24). Pump.fun transfer 64.666 SOL ke Kraken (kumulatif 5,6 jt SOL ~$887,6 jt). Voorhees beli 2.504 ETH ($4,75 jt). ETF BTC outflow $185,4 jt (hari ke-7). Fear & Greed 12 (kemarin 20). BTC rebound $67.000 (-2,65% 24j). Binance pulihkan penarikan 87 jaringan.",
  "four.meme Graduated (browser live 12:46-12:48 WIB): TIDAK ADA graduasi baru dalam ~2 jam terakhir; termuda 1 hari: 裤裆里的黑天鹅 / NVDAB $192,03K, holders 421, 24j +6.078,24% — sudah berlipat, distribution watch. Tag panas: 正在, 奔涌, 向我, swj, 红果. Lainnya: JACKET/NVDAB $2,08K 31 holder 24j -33,37%; 小瓜 $6,45K 130 holder +106,47% 24j (vol $111,04K jauh di atas MC); VIP 人生 $2,08K 355 holder -92,39%; 安全驾驶 $2,13K; FDC $2,17K; frog $4,81K +34,80%. Holder terbanyak: 红果短剧 1.047 (13 hari), Mai 959 (7 hari), 牛回 950 (12 hari) — semua berumur ≥7 hari, bukan pertumbuhan holder segar.",
  "Genius.fun (browser live 12:46-12:48 WIB): total Graduated 176 (tidak berubah), All 21.681; TIDAK ADA graduasi baru dalam beberapa hari — termuda Genius Dog $GDOG 8 hari ($5,09K, holders 44). Top: GSTOCK $3,51 jt (+1,83% 24j), MILAN $101,94K, GCAT $26,6K. Bagian 'All': Chief Everyone Officer $CEO (pasangan NVDAB) umur 2 jam, $4,18K, 32 holder, progres 20,59% — turunan narasi NVDAB/SWJ, bukan narasi segar; AsianStar 12 jam, $4,09K, 17 holder, progres 7,63%, vol 24j $31,26K.",
  "DexScreener BSC trending 6H (browser live 12:47 WIB, opsional): #1 SWJ/NVDAB $568K, umur 7 jam, 6j +891%, 24j +1.538%, vol $2,3 jt, 3.470 trader — sudah berlipat, distribution watch; #2 AGC $397K 6j -5,49% (11 hari); #3 ARK $183,1 jt; #4 Jacket/NVDAB $2,2 jt, 24j +3.000%, 6j +22,27%; #5 GANG $2,9 jt; #6 JAGENT $2,7 jt; #7 牛逼 $1,0 jt; #8 OLY $116,0 jt. #11 StarsAI $645K umur 1 hari, 6j +88,25%, 24j +79,53% — momentum hari kedua, bukan <2 jam dari basis rendah; #95 比特币 $105K umur 20 jam, 24j +455% — sudah berlipat. TIDAK ADA token <2 jam yang naik dari basis rendah.",
  "Holder Mode B (log run 12:30 WIB, dibaca silang): GMGN detail login-gated (streak 100) — money-flow TIDAK TERVERIFIKASI, bukan klaim tidak ada pembelian baru; cek on-chain 28 saldo terverifikasi blok 133488134, 0 berubah; tidak satu pun CA fast layer run ini muncul di log holder.",
  "KOL ledger + wallet-watchlist (dibaca silang): tidak ada seruan KOL baru atas token/narasi di sumber run ini; wallet-watchlist masih kosong (belum ada wallet terpantau terverifikasi) — money-flow tidak dapat dikonfirmasi dari lapisan ini."
 ],
 "sumber_dilewati": "PANews Meme Daily, Odaily headlines, Sharpe.ai BNB meme narrative tracker, GMGN BSC trending — opsional, tidak ada kandidat dari sumber wajib untuk deep-check; Binance Square — hanya deep-check bila ada kandidat, tidak ada kandidat run ini; Jinse flash — sudah dicopot dari sumber wajib (buta 11 run berturut-turut; dilaporkan sekali, jangan laporkan ulang kecuali pulih lalu buta lagi).",
 "hasil": "TIDAK ADA sinyal awal baru. Run diam (silent) sesuai aturan — tidak ada pesan chat. Konvergensi terkuat tetap narasi Huang Renxun/Nvidia (BlockBeats 12:42 Burry 'get out' soal kepergian Huang + tag '🔥 swj' four.meme + NVDAB Graduated #1 + DexScreener #1 SWJ +891% 6j, MC $568K) tapi semua token terkait sudah berlipat ribuan persen dan di puncak perhatian (SWJ +1.538% 24j umur 7 jam, NVDAB +6.078,24% 24j, Jacket +3.000% 24j) = SUDAH RAMAI / distribution watch, bukan sinyal entry. Tidak ada graduasi launchpad baru (four.meme termuda 1 hari, Genius.fun termuda 8 hari). Pasar risk-off ekstrem (Fear & Greed 12). KOL: tidak ada seruan baru (ledger tidak berubah). Wallet: money-flow tidak terverifikasi.",
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
        dw['status'] += " Update run 1213 (browser 12:46-12:48 WIB): SWJ masih #1 DexScreener BSC trending 6H, MC $568K, 6j +891%, 24j +1.538%, vol $2,3 jt, umur 7 jam — sudah berlipat di puncak trending, tetap distribution watch, BUKAN sinyal entry; NVDAB four.meme Graduated #1, MC $192,03K, holders 421, 24H +6.078,24%, umur 1 hari; Jacket $2,2 jt, 24j +3.000%; BlockBeats 12:42 Burry tambah short Nasdaq/semikonduktor + sarankan 'get out' soal kepergian Huang — konteks makro/distribusi, bukan peluncuran baru; tidak dilaporkan ke user."
        break
json.dump(s, open(p,'w'), ensure_ascii=False, indent=1)
s2=json.load(open(p))
assert len(s2['runs'])==before+1 and s2['runs'][-1]['run_number']==1213
assert len(s2.get('reported_signals',[]))==24
print('OK run 1213 written; runs total:', len(s2['runs']))
