---
id: bobbie-listing-watch
title: Pantau finalize BOBBIE + listing 0,0075 BNB
enabled: false
owner: goal:pencarian-rutin-project-free-mint
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-11-07T21:03:03
  every: 30m
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
Pantau finalisasi BOBBIE lalu listing otomatis BOBBIE #4023 di market proyek sendiri. Perintah user 2026-11-07 ~20:30 WIB (tap "Ya, pantau BOBBIE dan listing 0,05 BNB sesudah finalize") + RALAT user 2026-11-07 ~20:32 WIB: harga listing 0,0075 BNB (bukan 0,05). Harga ralat ini yang berlaku.

FAKTA TERVERIFIKASI (jangan ditebak ulang):
- NFT BOBBIE 0x3BF121dC4c5a1Ba567F3eE801d0e447601726207, tokenId 4023, tier Epic, milik agent wallet 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E (ownerOf terverifikasi).
- Market proyek sendiri BobbieMarketV4 0xfA239D919Db60E1b497E9E8CA26CA79689a180AF, terverifikasi Sourcify exact_match. Fungsi: list(id, price) nonpayable; listings(tokenId) -> seller, price, version, benefits, ownershipVersion; MIN_PRICE 0,001 ether; paused() view. Fee jual 10%: seller dapat 90% (0,00675 BNB bila terjual di 0,0075), treasury 10%.
- list() mensyaratkan: whenNotPaused + saleReady (nft.saleFinalized() true DAN !cancelled), price >= MIN_PRICE, ownerOf(id) == msg.sender, DAN approved (isApprovedForAll ATAU getApproved(id) == market).
- Status terakhir dicek 2026-11-07 ~20:31 WIB: saleFinalized() = false, cancelled() = false, market paused() = false, listings(4023) kosong (seller 0), getApproved(4023) = 0, isApprovedForAll(user, market) = false. Mint berakhir Senin 2026-11-16 14:40:09 WIB (mintEndsAt on-chain 1794814809); finalisasi wewenang owner proyek sesudah itu, waktunya tidak diketahui.
- Harga listing: 0,0075 BNB = 7500000000000000 wei. Sudah di atas MIN_PRICE 0,001 BNB.

TIAP RUN (read-only dulu):
1. Baca segar on-chain (fast_rpc / dataseed, fallback antar RPC bila 403/timeout; gagal baca = tidak terverifikasi, bukan fakta negatif): NFT saleFinalized(), cancelled(), ownerOf(4023); market paused(), listings(4023). Simpan state di ~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/bobbie-listing-watch-state.json (terakhir dicek, saleFinalized, listing aktif/tidak).
2. Bila listings(4023) sudah aktif dengan seller = agent wallet dan price = 7500000000000000: DIAM (sudah ter-listing, jangan list ulang, jangan ubah harga).
3. Bila saleFinalized() masih false: DIAM (jangan laporkan tiap run). Jangan kirim approval/list apa pun — list() akan revert MintNotFinalized dan transfer masih terkunci (TransfersLocked).
4. Bila ownerOf(4023) bukan lagi agent wallet: laporkan sekali ke chat utama bahwa token sudah tidak di wallet agent (sertakan owner baru bila terbaca) lalu DIAM di run berikutnya.

SAAT saleFinalized() == true (dan !cancelled, market tidak paused, owner masih agent, listing belum aktif):
Eksekusi listing otomatis di market proyek sendiri, dua langkah, masing-masing dengan preview bersih via baw SEBELUM eksekusi:
(a) Approve SATU token saja: approve(market, 4023) di kontrak NFT — JANGAN setApprovalForAll. Preview bersih (code 000000000, tanpa error, value 0, tanpa perubahan authority/allowance selain approval token ini ke market, tanpa risk hit). Bila preview kotor / 351803 / 351805: STOP, laporkan sekali + alasannya, jangan paksa.
(b) list(4023, 7500000000000000) di market 0xfA239D919Db60E1b497E9E8CA26CA79689a180AF, value 0. Preview bersih dengan syarat sama. Bila preview kotor: STOP, laporkan sekali + alasannya.
(c) Verifikasi pasca: listings(4023) seller = agent wallet, price = 7500000000000000, version >= 1; receipt tiap tx status 1. Laporkan SEKALI ke chat utama: tx hash + blok + gas tiap langkah, verifikasi listing aktif, harga 0,0075 BNB, fee 10% (net penjual 0,00675 BNB bila terjual). Sesudah sukses, run berikutnya DIAM (listing sudah aktif) — parent yang menonaktifkan job ini sesudah laporan sukses tersampaikan.
- Bila market paused saat finalize: laporkan sekali + alasannya, jangan paksa, pantau lanjut.
- Bila sesi baw kedaluwarsa (sesi tercatat berakhir 2026-11-09 ~10:18 WIB — SEBELUM finalize 16 Nov): laporkan sekali ke chat utama bahwa eksekusi butuh QR re-sign-in baw oleh user, JANGAN coba re-login sendiri. Pantau lanjut (read-only) sampai sesi pulih.
- JANGAN EVER: beli, transfer, cancel listing orang lain, placeOffer/acceptOffer, listing di Element secara otomatis (Element butuh connect manual wallet user + API key — bila own market gagal, siapkan detail listing manual Element + laporkan, jangan klaim sudah ter-listing), atau listing di harga selain 0,0075 BNB tanpa perintah baru user.
- Gas dari BNB native. Jangan sentuh draft email. Jangan ubah harga, token, atau market tanpa perintah user.
