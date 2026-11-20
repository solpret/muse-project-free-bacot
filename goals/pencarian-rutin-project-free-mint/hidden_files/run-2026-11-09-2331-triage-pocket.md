# Triase Pocket Ai — run 2331 (parent, 2026-11-09 ~23:45 WIB)

Koreksi atas laporan discovery: Pocket Ai BUKAN baru — sudah di snapshot
(contracts["Pocket Ai"], status early-lead-backfill, dilaporkan sekali
2026-11-07 ~11:10 WIB). Discovery subagent salah menyatakan "tidak ada di
snapshot".

## Fakta segar run 2331
- Kontrak: 0xf9D00B7a2992de00EBc5F9f04BAf95d44C542102
- Post Boltbook baru: zeeke.ai /p/deuKVHCRDbzL — mintFree() value 0, gas only,
  1/wallet; totalMinted 1.406; situs https://pocket.agenticwallet.workers.dev;
  X @Agentic_Pocket.
- Sourcify: rc=400, match null, verifiedAt null — TIDAK terverifikasi.
  Klaim post "exact_match" SALAH. Free path tetap UNVERIFIED (tanpa ABI,
  free views/quote tidak bisa dibaca).
- Website: TERVERIFIKASI BARU — pocket.agenticwallet.workers.dev rc=200,
  4.794.824 byte, mencetak alamat kontrak persis 3x, judul
  "Pocket Ai — NFT Marketplace · BSC", "5,555 NFTs on BNB Chain".
  (Sebelumnya website unverified; ini fakta gate baru.)
- X @Agentic_Pocket: dinyatakan di post, belum diverifikasi independen
  sebagai milik proyek (X hanya bukti tambahan, bukan gate).
- Umur: first mint terverifikasi on-chain 2026-11-07 10:41:45 WIB
  (blok 132130472, backfill) → umur ~60,8 jam pada 23:31 WIB 2026-11-09,
  >48 jam. Belum sold out (1.406/5.555). Free-quota reading: TIDAK BISA
  dibaca (Sourcify 400, tanpa ABI).
- Owner 0x9aab2a878f40323af113e5528afe74e4b21a0401 tidak di
  same-owner-discards.json; alamat kontrak juga tidak ada di discards.

## Keputusan (menunggu hasil re-read Rute 1 untuk angka segar)
- BUKAN kandidat (umur >48 jam, free% unverified, velocity gagal).
- BUKAN strong lead (free% unverified).
- Age rule body: umur terverifikasi >48 jam + belum sold out → hapus dari
  watchlist aktif + laporkan sekali sebagai age-exclusion, dengan bukti
  (launch time source, free-quota reading, waktu baca). Run 2231/2301
  menahan Pocket Ai/Night Bandits Club/King's Game sebagai age-watch
  ("free-quota gagal baca / launchNote tidak tegas / status non-aktif").
  Keputusan akhir sesudah re-read segar: bila re-read mengonfirmasi masih
  minting + umur >48 jam, terapkan age-exclusion + hapus dari snapshot
  (konsisten dengan body); bila re-read gagal baca (None seperti run-run
  sebelumnya), pertahankan keputusan run 2231/2301 dan catat alasannya.
- Night Bandits Club + King's Game: periksa dengan kriteria yang sama
  dari hasil re-read (umur + sold-out + free-quota).
