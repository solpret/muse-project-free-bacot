import json
p='state.json'
s=json.load(open(p))
entry={
 "run_number": 1210,
 "waktu_run": "2026-11-14 11:59 WIB",
 "jenis_run": "pulse penuh (jendela alert 07:00-13:00 WIB; run dijadwalkan 11:59 WIB)",
 "klasifikasi": "tidak ada sinyal",
 "kredit_x_dipakai": 0,
 "sumber_diperiksa": [
  "Fast layer (fast_discovery.py, 12:00 WIB): 60 token, 27 baru first-seen (pool created ~04:42-04:57 UTC / 11:42-11:57 WIB) — snapshot saja, bukan sinyal; FDV baru umumnya ~$3,2K (klon nama China). Terbesar: ELON 0x094c...0548 FDV $2,3 M (artefak/nama lama, bukan token baru), 月亮 0xad07...a75 $135.272, SWJ 0xf11b...7777 $107.134, VENSA 0x3fbe...7777 $60.292, SWJ 0x73dd...7777 $58.224, PM 0x455b...cb41 $496.762, 狗狗币 0xa562...a086 $39.308; tidak satu pun muncul di sumber narasi run ini sebagai token baru (SWJ/klon turunan narasi Huang Renxun yang sudah distribution watch).",
  "X search (x_narrative.py, 12:01 WIB): TIDAK TERSEDIA — HTTP 402 twitterapi.io credits exhausted (2 token dicoba: 0x455b...cb41 PM, 0xf8bf...2161 FWACK); 0 kredit dipakai; sudah dilaporkan sekali hari ini (run 04:00 WIB), tidak dilaporkan ulang; tidak ada X-HIT/X-MISS yang dikarang.",
  "BlockBeats flash (browser live 12:01 WIB, www.theblockbeats.info/newsflash): 10 item terbaru 11:26-12:55 WIB. TIDAK ADA item BSC memecoin/token meme baru. Pasar risk-off: Fear & Greed 12 (kemarin 20), BTC rebound $67.000 (-2,65% 24j, -12% 7 hari), ETF BTC outflow $185,4 jt (7 hari berturut-turut). Satu-satunya sebutan Huang Renxun adalah konteks makro (11:49, Yi Lihua: khawatir insiden Huang Renxun menekan saham AS), bukan peluncuran token. Lainnya: Voorhees beli 2.504 ETH ($4,75 jt); Binance pulihkan penarikan 87 jaringan; peretasan Cursor/Fireworks (kebocoran kunci); identitas whale insider listing HYPE terungkap (floating profit $82 jt -> $42,95 jt).",
  "four.meme Graduated (browser live 12:06 WIB): TIDAK ADA graduasi baru dalam beberapa jam terakhir; terbaru 裤裆里的黑天鹅 / NVDAB $178,6K, holders 411, 24j +5.663,46%, umur 21 jam — sudah berlipat, distribution watch. Tag panas: 正在, 奔涌, 向我, swj, 红果. Hampir lulus >80% (BUKAN sinyal entry, semua kecuali Wiki Cat sudah naik ratusan % 24j): Jacket Life $33,5K progres 92,83%, holders 269, +950,61%, umur 21 jam; PET $38,97K 87,53% (+725,87%, umur a year); X Dog $23,13K 84,40% (+625,39%, 18 jam); pyro $24,08K 82,79% (+580,62%, 9 bulan); Wiki Cat $23K 81,59% (-0,56%, a year). Kontrak hanya tampil terpotong.",
  "Genius.fun (browser live 12:04-12:05 WIB): total Graduated 176, All 21.681; TIDAK ADA graduasi baru dalam beberapa hari — termuda Genius Dog $GDOG 8 hari ($5,1K, holders 44). Top: GSTOCK $3,51 jt (-2,09% 24j), MILAN $101,8K (-8,80%), GCAT $26,57K (+15,80%). Token terbaru di 'All': Chief Everyone Officer $CEO $4,35K, 39 holders, 1 jam, progres 23,04%, 1j -0,81%; duplikat $CEO $3,29K 0 holders; Asian Star $4,09K, 17 holders, 12 jam, progres 7,63%, vol 24j $31,22K jauh di atas MC-nya; token 1-12 jam umumnya hanya 0-6 holders — tidak ada pertumbuhan holder menonjol.",
  "DexScreener BSC trending 6H (browser live 12:05 WIB, opsional): #1 SWJ/NVDAB $513K, 6 jam, 6j +1.378%, vol $2,2 jt, 26.239 txns; #2 AGC $400K +44,25% 24j, 11 hari; #3 ARK $182,9 jt; #4 Jacket/NVDAB $1,9 jt, 24j +2.750%, 6j -17,10%; #5 牛逼 $979K -10,49% 24j. TIDAK ADA token <2 jam yang naik dari basis rendah; termuda SWJ 6 jam sudah +1.378% dan di puncak trending = SUDAH RAMAI / distribution, BUKAN sinyal entry.",
  "Holder Mode B (log run 10:30 WIB, dibaca silang): cek on-chain 28 saldo terverifikasi blok 133472130, 0 berubah; GMGN detail login-gated (streak 99) — money-flow TIDAK TERVERIFIKASI, bukan klaim tidak ada pembelian baru; kandidat fast layer tidak bersilangan dengan log holder.",
  "KOL ledger + wallet-watchlist (dibaca silang): tidak ada seruan KOL baru atas token/narasi di sumber run ini; wallet-watchlist masih kosong (belum ada wallet terpantau terverifikasi) — money-flow tidak dapat dikonfirmasi dari lapisan ini."
 ],
 "sumber_dilewati": "PANews Meme Daily, Odaily headlines, Sharpe.ai BNB meme narrative tracker, GMGN BSC trending — opsional, tidak ada kandidat dari sumber wajib untuk deep-check; Binance Square — hanya deep-check bila ada kandidat, tidak ada kandidat run ini; Jinse flash — sudah dicopot dari sumber wajib (buta 11 run berturut-turut; dilaporkan sekali, jangan laporkan ulang kecuali pulih lalu buta lagi).",
 "hasil": "TIDAK ADA sinyal awal baru. Run diam (silent) sesuai aturan — tidak ada pesan chat. Konvergensi terkuat tetap narasi Huang Renxun/Nvidia (BlockBeats konteks makro + four.meme tag 'swj' + NVDAB Graduated #1 + DexScreener #1 SWJ + #4 Jacket) tapi semua token terkait sudah berlipat ribuan persen dan di puncak perhatian (SWJ +1.378% 6j, NVDAB +5.663% 24j, Jacket Life +950% 24j mendekati graduasi) = SUDAH RAMAI / distribution watch, bukan sinyal entry. Tidak ada graduasi launchpad baru (four.meme 21 jam lalu, Genius.fun 8 hari lalu). Pasar risk-off (Fear & Greed 12). KOL: tidak ada seruan baru (ledger tidak berubah). Wallet: money-flow tidak terverifikasi.",
 "kol_status": "tidak ada",
 "wallet_confirmation_status": "tidak terverifikasi (wallet-watchlist kosong; log holder Mode B 10:30 WIB tanpa perubahan)",
 "reported_signals_count": 24
}
assert len(s.get('reported_signals',[]))==24, "reported_signals berubah!"
before=len(s.get('runs',[]))
s['runs'].append(entry)
# Update singkat distribution_watch SWJ/NVDAB (entri AICAT, tempat update SWJ dicatat run-run sebelumnya)
for dw in s.get('distribution_watch',[]):
    if dw.get('token')=='AICAT':
        dw['status'] += " Update run 1210 (browser 12:05-12:06 WIB): SWJ masih #1 DexScreener BSC trending 6H, MC $513K, 6j +1.378%, vol 24j $2,2 jt, umur 6 jam — sudah berlipat di puncak trending, tetap distribution watch, BUKAN sinyal entry; NVDAB four.meme Graduated #1, MC $178,6K, 24H +5.663,46%, umur 21 jam; Jacket Life mendekati graduasi 92,83% (+950,61% 24j) — sudah berlipat, BUKAN sinyal entry; tidak dilaporkan ke user."
        break
json.dump(s, open(p,'w'), ensure_ascii=False, indent=1)
s2=json.load(open(p))
assert len(s2['runs'])==before+1 and s2['runs'][-1]['run_number']==1210
assert len(s2.get('reported_signals',[]))==24
print('OK run 1210 written; runs total:', len(s2['runs']))
