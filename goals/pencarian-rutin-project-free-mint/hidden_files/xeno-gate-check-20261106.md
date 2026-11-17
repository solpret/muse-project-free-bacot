# Xeno Garden Direct — website gate check (read-only)

- Tanggal: 2026-11-06 ~18.30–18.45 WIB
- Kontrak: `0x759C09378dBFf2d6AAC0261Ad1f92f9d230669f5` (BSC, BEP-721)
- Nama on-chain: Xeno Garden Direct, simbol XENO, totalMinted 1 / MAX_SUPPLY 10000
- Owner: `0x66bfd4a0c3838fa73b787d5a74d18cc94f39bb18`
- Free path (sudah terverifikasi sebelumnya): freeMintRemaining(user)=10, priceForSerial(1..3)=0
- **HASIL: WEBSITE TIDAK DITEMUKAN.** Gate website GAGAL. Tidak ada eksekusi apa pun yang dilakukan (read-only).

## Metode yang sudah dicoba (sebelum tugas ini)

- (A) Pencarian web alamat kontrak persis — hanya noise (proyek XENO lain: PROJECT XENO game, XEN crypto, Xenobunny).
- (G) Pencarian web nama "Xeno Garden Direct" / "Xeno Garden" — hanya noise, tidak ada situs proyek.
- (C) Sourcify metadata/sources kontrak — TIDAK ADA URL apa pun di dokumen.
- (J) Grep ABI (51 fungsi) — TIDAK ADA contractURI / fungsi site / URL; hanya tokenURI, renderer, evolutionRouteAt, grow, evolve, lives, seedReady, guardian.

## Metode yang dicoba dalam tugas ini

### 1. (I) tokenURI token yang sudah ter-mint — BERHASIL DIBACA, TIDAK ADA URL

- `tokenURI(0)`: revert (custom error 0x7e273289) — token 0 tidak ada, wajar (hanya token 1 ter-mint).
- `tokenURI(1)`: terbaca via bsc-dataseed1.bnbchain.org — `data:application/json;base64,...`, decode:
  - name: `霜冠夜羽`
  - description: "Botanical V8. Evolve once the token seed is ready, at most five lifetime steps. No yield or value is promised."
  - image: `data:image/svg+xml;base64,...` (SVG inline, bukan URL)
  - attributes: GenomeCode 1237, EditionRank 0, BaseLayers 1, EvolutionCount 0, EvolutionRemaining 5, RouteHistory 0, Morphology 1, LeafGene 1, PetalGene 1, VeinGene 0, Palette 2, CrestGene 0, SeedReady "true"
  - **external_url: null, website: null, external_link: null — TIDAK ADA URL apa pun di metadata.**
- Metadata lengkap tersimpan di `/tmp/xeno_token1_meta.json`.

### 2. renderer() — BERHASIL DIBACA, TIDAK ADA URL

- `renderer()` = `0x42400e4170d1af2c3839986f97ecdae1e7e77499` (kontrak renderer terpisah).
- Sourcify kontrak renderer: exact_match, verifiedAt 2026-11-04T15:42:10Z; fungsi hanya `metadata()` dan `specimenName()`; **TIDAK ADA URL di dokumen Sourcify**.
- `metadata()` di renderer: revert (`execution reverted: 0x`) pada 2 percobaan di semua RPC — tidak bisa dibaca, bukan bukti ada/tidak ada URL.
- `specimenName()`: revert juga.
- Kesimpulan: jalur renderer tidak menghasilkan URL.

### 3. (B) Boltbook EN + ZH — TIDAK ADA SEBUTAN

- boltbook.fun EN (45.698 byte) dan ?lang=zh (46.369 byte), dibaca 2026-11-06 ~18.40 WIB.
- **0 hit "xeno"** di kedua halaman. Tidak ada postingan, tidak ada tautan.

### 4. (M) Search-engine site: filters — TIDAK ADA HASIL

- `site:pages.dev "xeno garden"` — no results.
- `site:vercel.app "xeno garden" NFT` — no results.
- `site:deed.page "xeno garden"` — no results.
- `site:surge.sh "Xeno Garden Direct"` — no results.

### 5. Owner/deployer — TIDAK ADA SITUS TERKAIT

- Pencarian alamat owner `0x66bfd4a0c3838fa73b787d5a74d18cc94f39bb18` — hanya noise (explorer/Threads tidak terkait).
- Tidak ada domain yang ditebak dari host metadata (tidak ada host metadata sama sekali — metadata token sepenuhnya inline base64).

## Sisa yang BELUM dicoba (butuh live browser — untuk parent)

- (L) BscScan token-info via live browser: kolom website/sosial di halaman token BscScan `0x759C09378dBFf2d6AAC0261Ad1f92f9d230669f5` — text-fetch BscScan 403, jadi hanya bisa dibaca lewat browser live.
- (K) GitHub code search butuh auth — tidak dicoba (limitasi tercatat).
- (N) Registry-profile hop tidak berlaku — kontrak TIDAK punya referensi registry Agent ID (bukan agent-shaped).

## Verdict

**Website TIDAK DITEMUKAN setelah metode A, B, C, G, H (tidak ada contractURI di ABI), I, J, M + owner search.** Satu-satunya metode yang tersisa adalah (L) BscScan via live browser. Selama tidak ada website terverifikasi yang mencetak kontrak persis, gate website GAGAL dan Xeno Garden Direct TIDAK boleh di-preview/di-mint di bawah aturan FREE BACOT.
