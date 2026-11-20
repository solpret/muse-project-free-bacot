# FREE BACOT — pemantauan rutin project free-mint NFT

Goal ID: goal_5b382a7ff282
Goal slug: pencarian-rutin-project-free-mint

## Description
Project ke-2 pengguna setelah MODAL BACOT, dan TERPISAH darinya: FREE BACOT
khusus untuk free-mint NFT (baca + lapor saja), sedangkan MODAL BACOT adalah
live trading memecoin. Tidak ada sinyal FREE BACOT yang mengumpan eksekusi
trading, dan tidak ada sinyal trading yang mengumpan kandidasi FREE BACOT.
MODAL BACOT sendiri mengecualikan semua NFT dari scope trading-nya.

Pencarian rutin setiap 30 menit (cron `free-mint-search`) untuk project
free-mint NFT BARU yang memenuhi semua syarat wajib: free gas-only dengan
kuota gratis terverifikasi untuk wallet pengguna; umur peluncuran
TERVERIFIKASI maksimal 48 jam (bila terverifikasi >48 jam dan belum sold out:
[DIGANTI 2026-11-10 — umur kini KURANG DARI 24 jam, lihat §FILTER UMUR FREE BACOT <24 JAM.]
gugur DAN dihapus dari watchlist aktif); KUOTA FREE-MINT terpenuhi minimal
50% — yang diukur adalah kuota free-nya (freeClaimed/freeLeft/freeSupply vs
alokasi gratis), BUKAN total supply (koreksi pengguna 2026-11-01 ~19:03 WIB;
bila seluruh koleksi gratis, alokasi gratis = total cap; bila kuota gratis
tidak bisa dibedakan on-chain, kaki % = UNVERIFIED dan tidak boleh diganti
dengan % total supply); kecepatan minter MENINGKAT (rate ≥1,5x rate
sebelumnya DAN ≥20 token dalam interval); narasi Binance Agentic Wallet /
.ai Agent ID; sinyal X (diskusi publik terbaca); proyek wajib punya akun X.

Hasil hanya dilaporkan bila ada kandidat baru yang lolos semua syarat
terverifikasi; tidak ada mint, preview, atau eksekusi tanpa persetujuan
eksplisit terpisah dari pengguna. Proyek yang pengguna sebut sendiri tetap
bebas dari tes X + tes umur 48 jam, tapi tetap butuh strict scan + preview
[DIGANTI 2026-11-10 — umur kini KURANG DARI 24 jam, lihat §FILTER UMUR FREE BACOT <24 JAM.]
bersih + kuota gratis terverifikasi. Watchlist aktif dikosongkan 2026-11-01
~18:37 WIB (27 kontrak lama diarsip lalu dihapus permanen atas perintah
pengguna ~18:55 WIB); discovery mengisi ulang dari proyek baru.

AUTO-MINT (otorisasi pengguna 2026-11-01 ~19:09 WIB, perlakuan sama dengan
pra-otorisasi sempit untuk mint gratis user-named): bila kandidat lolos
SEMUA syarat FREE BACOT di atas, run boleh langsung preview + mint TANPA
konfirmasi terpisah, HANYA bila aman: (a) inspeksi situs + verifikasi
on-chain independen selesai; (b) hasil audit Binance diungkap
(hasResult=false diungkap sebagai tidak ada hasil, bukan pass; satu hit
risiko drain spesifik = STOP); (c) kuota gratis terverifikasi on-chain
untuk wallet pengguna (cost/quote = 0); (d) preview bersih (code 000000000,
tanpa error, value 0, tanpa perubahan authority/allowance, tanpa risk).
Bila satu syarat keamanan gagal, atau preview kotor / 351803 / 351805 →
tidak eksekusi, laporkan kandidat + alasan penghambat sekali, dan hentikan
kandidat itu; tanpa fallback berbayar. Bila sesi baw kedaluwarsa → laporkan
gagal, jangan coba login ulang (butuh tap QR pengguna). Setelah auto-mint
berhasil, laporkan tx hash + verifikasi on-chain + cek marketplace dan
rarity pasca-mint sesuai aturan. Otorisasi ini HANYA untuk free mint
kandidat FREE BACOT — bukan approval, listing, transfer, paid mint, swap,
atau signing lain — dan dapat dicabut pengguna kapan saja dengan satu pesan.

TIER EARLY-LEAD (otorisasi pengguna 2026-11-01 ~19:55 WIB): kontrak
agent-mint baru (ERC-721/1155 yang ABI Sourcify-nya atau bytecode-nya
menunjukkan referensi registry Agent ID, AgentGate, atau fungsi
free-mint/konstanta free-supply) yang mint PERTAMANYA terverifikasi
on-chain dalam run, berapa pun % -nya, wajib dilaporkan SEKALI sebagai
EARLY (bukan kandidat) dengan kontrak, waktu pertama terlihat, jumlah
mint/minter bila diketahui, dan status tiap kaki (terverifikasi vs
unverified) dinyatakan jelas, lalu masuk watchlist snapshot untuk
dilacak. Early lead TIDAK PERNAH auto-mint/preview; naik jadi strong
lead bila memenuhi 3 kaki lead kuat, jadi kandidat hanya bila semua
syarat + safety lolos. Bila kemudian sold out, lewat umur, terbukti
berbayar saja, atau terbukti bukan agent-shaped → laporkan sekali +
hapus dari snapshot. Tier ini HANYA untuk kontrak agent-shaped, bukan
untuk semua ERC-721/1155 baru di BSC; kontrak yang sama tidak pernah
dilaporkan ulang sebagai EARLY. Kaki scan on-chain DIPASANG sebagai route 4
di body cron per persetujuan pengguna 2026-11-01 ~20:07 WIB (tap "Tetap
pasang scanner"), berlaku mulai run 20:31 WIB; scan menjadi detektor early
utama, lead Boltbook/web tetap sebagai sumber sekunder. Script:
hidden_files/onchain_nft_scan.py (--chunk 50, --blocks dihitung dari
watermark), dedupe via hidden_files/onchain-scan-seen.json, jendela
watermark di hidden_files/onchain-scan-state.json (scan dari blok terakhir
yang sudah di-scan, cap 2000 blok, gap dicatat, gagal scan tidak memajukan
watermark; hanya endpoint Ankr gratis, tanpa top-up — syarat "selama
gratis", disetujui 20:19 WIB); scan tidak pernah auto-mint/preview sendiri.

## FREE BACOT TRACK B — KLAIM TOKEN GRATIS + AUTO-KLAIM (otorisasi pengguna 2026-11-01 ~20:27 WIB, tap "Auto-klaim bila aman")
Jalur kedua FREE BACOT di samping NFT free-mint: klaim token fungible dari
entitlement free mint/share, dengan biaya nol (gas only). Kriteria kandidat
jalur B: (1) GRATIS — fungsi klaim teridentifikasi, cost/quote 0, tanpa
approval/pembayaran (yang butuh bayar/approval gugur, tidak pernah
dieksekusi); (2) ELIGIBLE — wallet memegang entitlement + belum diklaim
(flag false) + jumlah claimable > 0 terverifikasi on-chain; (3) HOOK LP
JELAS — pair terverifikasi on-chain (token0/token1 cocok), kondisi
launching eksplisit di kontrak (mis. launched()) dan statusnya dibaca tiap
run (pair tak terverifikasi / kondisi launching tak jelas = bukan kandidat);
(4) OPEN — klaim sedang terbuka (launch true); belum terbuka = PENDING,
bukan kandidat; (5) X — wajib punya akun X + bukti diskusi publik, sama
dengan jalur A (proyek yang user sebut sendiri bebas dari tes X + umur,
tapi tetap butuh strict scan + preview bersih + klaim gratis terverifikasi).
Kaki % dan velocity jalur A TIDAK berlaku untuk jalur B; aturan umur 48 jam
[DIGANTI 2026-11-10 — umur kini KURANG DARI 24 jam, lihat §FILTER UMUR FREE BACOT <24 JAM.]
jalur A berlaku untuk jalur B diukur dari PEMBUKAAN KLAIM (launch yang
membuat token bisa diklaim), bukan dari mint awal: klaim yang belum terbuka
dilacak sebagai pending tanpa memandang umur mint; sekali terbuka, harus
diklaim dalam 48 jam sejak dibuka atau dihapus dari tracking (dilaporkan
[DIGANTI 2026-11-10 — umur kini KURANG DARI 24 jam, lihat §FILTER UMUR FREE BACOT <24 JAM.]
sekali). AUTO-KLAIM: bila klaim lolos SEMUA kriteria jalur B + SEMUA guard
safety (inspeksi situs + verifikasi on-chain, audit diungkap, cost 0,
preview bersih 000000000 tanpa authority/allowance/risk, dan perubahan
saldo simulasi cocok dengan jumlah claimable terverifikasi), run boleh
langsung preview + klaim TANPA konfirmasi terpisah. Gagal guard / preview
kotor / 351803 / 351805 → tidak eksekusi, laporkan sekali + alasan, tanpa
fallback berbayar. Revert "not launched / not open" (mis. NOT_LAUNCHED)
BUKAN gagal safety: klaim dicatat sebagai pending dan terus dipantau,
tidak dilaporkan sebagai kegagalan. Sesi baw kedaluwarsa → laporkan gagal,
tanpa login ulang. Setelah auto-klaim berhasil: lapor tx + blok + gas +
verifikasi (receipt + saldo TOKEN sebelum/sesudah + flag claimed true).
Otorisasi ini HANYA untuk klaim token gratis kandidat jalur B — bukan
approval, listing, transfer, paid claim, swap, atau signing lain — dan
dapat dicabut pengguna kapan saja dengan satu pesan. PENDING CLAIM:
entitlement jalur B terverifikasi yang klaimnya belum terbuka dicatat di
snapshot pending_claims dan dicek ulang tiap run; dilaporkan SEKALI sebagai
PENDING CLAIM saat pertama terverifikasi (bukan kandidat); saat terbuka +
lolos semua guard → auto-klaim + lapor tx; saat terbuka tapi gagal guard →
lapor sekali + alasan; saat proyek masuk refund/failed → lapor sekali +
hapus. Pending claim TIDAK PERNAH di-preview/diklaim selagi belum terbuka,
dan tidak pernah dilaporkan ulang sebagai pending. PENDING PERTAMA
(2026-11-01 ~20:28 WIB): binanceai.fun (MINT 0x46cb1D3efd4307506Cda7EbBa5a51be64746739E,
TOKEN 0x209173F09aFbCA053C0de9e9763f503e9fb54a3c, shares 1, tokenClaimed
false, claimable 1.000.000 TOKEN, launched false, pair TOKEN/USDT
0x903ACC22B9BABCD427bfb9AF2C27a27a5aC7c698); watch khusus 1 jam
(binanceai-claim-watch) DINONAKTIFKAN karena diambil alih tracking pending
jalur B rutin (30 menit) — begitu launched + aman, langsung auto-klaim +
lapor tx, bukan sekadar lapor dibuka.

## FREE BACOT TRACK C — PENJUALAN SHARE FUNGIBLE (otorisasi pengguna 2026-11-01 ~22:30 WIB, tap "Ya tambahkan")
Jalur ketiga FREE BACOT di samping NFT free-mint (A) dan klaim entitlement
(B), bermotif long-agent.com yang lolos dari screening rutin karena ia
penjualan share BEP-20, bukan NFT dan bukan klaim entitlement. Rute 5 di
body cron: (5a) poll feed Sourcify yang sama, filter bentuk SALE (mint +
quote/cost + free-share view + registry/AgentGate — ketiganya wajib); (5b)
sweep kata kunci share-sale + direct-fetch /skill.md, /launch.json,
/api/stats, /api/verify; (5c) backlog ERC-20 dari scan (script dipatch
2026-11-01 agar mengeluarkan erc20_mint_contracts_list; mint_count jendela
>= 20, maks 10/run di-shape-check, alamat terperiksa di
hidden_files/track-c-scan-checked.json, sisanya dibuang sebagai sampling
limit yang dinyatakan di run log, bukan cakupan penuh). LEAD track C =
bentuk sale + free pool > 0 + quote user 0 + umur terverifikasi ≤48 jam,
[DIGANTI 2026-11-10 — umur kini KURANG DARI 24 jam, lihat §FILTER UMUR FREE BACOT <24 JAM.]
dilaporkan sekali, TIDAK PERNAH auto-mint/preview. KANDIDAT track C = lead
+ punya akun X + diskusi publik terbaca + pool/slot masih terbuka,
dilaporkan sekali untuk keputusan eksplisit pengguna. TIDAK ADA AUTO-MINT
[DIGANTI 2026-11-01 ~22:41 WIB — auto-mint track C DIBERIKAN, lihat seksi berikut. Larangan di atas tidak berlaku lagi.]
UNTUK TRACK C: otorisasi 19:09 WIB hanya untuk kandidat NFT jalur A;
perpanjangan ke bentuk token fungible butuh otorisasi eksplisit sendiri
yang belum diberikan. Kaki 50% + velocity jalur A TIDAK meng-gate track C
(hanya info). Sold out / lewat umur / paid-only / bukan agent-shaped →
lapor sekali + hapus. Contoh excluded: long-agent.com sale
0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124 (free pool habis 2026-11-01).
Bila eksekusi track C diperintah pengguna, verifikasi = saldo TOKEN/share
sebelum/sesudah + flag gratis; cek marketplace/rarity TIDAK berlaku (bukan
NFT). Berlaku mulai run 23:01 WIB.

## FREE BACOT TRACK C AUTO-MINT (otorisasi pengguna 2026-11-01 ~22:41 WIB, "Jalankan auto mint selama gratis untuk track c")
Menggantikan batas TIDAK-AUTO-MINT sebelumnya: kandidat track C (lead +
akun X + diskusi terbaca + pool/slot terbuka) yang lolos SEMUA kriteria
track C boleh langsung preview + mint TANPA konfirmasi terpisah, HANYA
selama GRATIS dan semua safety lolos: (a) verifikasi on-chain segar
(source/ABI, pool, quote user, umur; inspeksi situs bila ada situs, bila
tidak ada situs maka source + ABI terverifikasi + state on-chain menjadi
basis inspeksi dan laporan wajib menyatakan tidak ada situs ditemukan);
(b) audit Binance diungkap (hasResult=false = tidak ada hasil, bukan
pass; hit risiko spesifik = STOP); (c) cost/quote = 0 segar saat eksekusi,
value 0, tanpa approval/bayar, parameter maxCost/cost-cap diisi 0 bila
fungsi mint memilikinya (agar eksekusi yang sudah tidak gratis revert,
bukan menarik dana); (d) preview bersih 000000000 dengan perubahan saldo
simulasi cocok dengan token yang diharapkan (tokensPerShare x kartu atau
tokensOut dari quote). Gagal guard / preview kotor / 351803 / 351805 →
tidak eksekusi, lapor sekali + alasan, tanpa fallback berbayar. 'Selama
gratis' adalah batas keras: mint track C yang tidak gratis TIDAK PERNAH
dieksekusi di bawah otorisasi ini. Lead tetap TIDAK PERNAH auto-mint/
preview. Setelah berhasil: lapor tx + blok + gas + saldo TOKEN
sebelum/sesudah + freeClaimed true; marketplace/rarity tidak berlaku
(bukan NFT). Dapat dicabut dengan satu pesan. Berlaku mulai run 23:01
WIB.

## FREE BACOT TRACK C SHAPE S2 (ditambahkan 2026-11-01 ~22:52 WIB, "Masukan juga pola seperti ini ke track c")
Bentuk sale kedua di samping S1 (mint + quote + free view + registry):
S2 = single-contract token+sale, bermotif 传火人
0x8b47354E7b76B1970a0D06365c8244a810d37493 (kontrak itu sendiri tokennya:
name/symbol/decimals/totalSupply di kontrak yang sama; mintFree() tanpa
argumen; free views freeClaimed/freeMinted + FREE_SLOTS/FREE_SUPPLY;
agentRegistry; jalur berbayar mintPaid dengan PRICE dalam USDT). Cek gratis
S2: pool terbuka = freeMinted < FREE_SLOTS; slot user =
freeClaimed(user) == false; tidak ada fungsi quote. Guard auto-mint (c)
S2 memakai cek tersebut; guard (d) saldo simulasi harus cocok dengan
FREE_AMOUNT. 传火人 sendiri menjadi contoh excluded (pool gratis habis
2026-11-01: freeMinted 1000/1000, preview 351805) — bila ditemukan lagi,
dicatat excluded, tidak dilaporkan. Berlaku mulai run 23:01 WIB.

## PERBAIKAN DETEKSI + HOT LEG FREE BACOT (ditambahkan 2026-11-01 ~23:00 WIB, tap user "Terapkan deteksi + hot leg 5 menit")
Perbaikan deteksi di cron free-mint-search (jadwal TETAP 30 menit): rute
5c shape-check menjadi paling banyak 20 kontrak per run (sebelumnya 10)
dengan ambang window mint_count >= 10 (sebelumnya >= 20), urut menurun,
tetap lewati/catat via track-c-scan-checked.json; sapuan rute 3/5b
ditambah kata kunci Mandarin ('免费份额', '首个免费', '免费铸造', '免费mint')
di samping kata kunci Inggris, direct-fetch dulu tidak berubah; rute 2
Boltbook membaca front page Inggris DAN Mandarin (?lang=zh) plus author
pages. Kriteria kandidat, guard keamanan, aturan diam, dan semua aturan
lain TIDAK BERUBAH; body terverifikasi byte-identical via diff.
Cron baru free-mint-hot-leg (interval 5 menit, pertama 23:09:38 WIB):
pendamping ringan — poll feed Sourcify recently-verified (limit 20),
front page Boltbook en+zh, shape-check S1/S2 untuk kontrak baru, baca
ulang on-chain snapshot watchlist/track_c/pending_claims secara
read-only. TANPA scan chain-wide Ankr, TANPA layanan berbayar baru,
TANPA top-up; timeout 300 detik, target di bawah 2 menit per run. Hanya
menulis hidden_files/hot-leg-seen.json dan
hidden_files/hot-leg-reported.json sendiri, TIDAK PERNAH menulis ulang
snapshot utama atau seen file utama. Eksekusi HANYA di bawah otorisasi
yang sudah ada (track-A 19:09, track-B 20:27, track-C 22:41) dengan SEMUA
guard tidak berubah; lead tidak pernah di-preview/di-mint. BATAS
DIKETAHUI: hot leg dan job utama dedup secara independen, sehingga
kontrak yang ditemukan hot leg dulu bisa dilaporkan sekali lagi oleh job
utama; eksekusinya sendiri ter-dedup alami oleh state on-chain
(slot/pool yang sudah terpakai).
