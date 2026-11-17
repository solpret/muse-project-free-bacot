# Migrasi Scan Tracked Wallet: Ankr → BscScan API

Perintah user 2026-11-14 ~18:46 WIB ("Ya, coba lewat BscScan"). Ankr mati: freemium habis + HTTP 401
sejak 2026-11-09 (29 run gagal berturut-turut, run 141–169). Blockscout BSC API 404; PublicNode
BSC `eth_getLogs` rate-limit (-32005) bahkan di jendela 10 blok. BscScan API key gratis sedang
diminta ke user via Secure Vault (connector `custom.bscscan`, placement `query_param: apikey`,
host `api.bscscan.com`) — key BELUM ada saat migrasi ini ditulis.

## Status

- [x] 2026-11-14 ~18:47 WIB — Pemetaan implementasi saat ini (lihat "Yang ditemukan" di bawah).
- [x] 2026-11-14 ~18:52 WIB — Klien BscScan baru: `custom.bscscan/bin/bscscan.py` + `CONNECTOR.md` + `connector.yaml` (pola ankr.py + dynamic_credentials.py).
- [x] 2026-11-14 ~18:55 WIB — Driver scan baru: `narrative-pulse/tracked-mint-scan-bscscan.py` (kaki BscScan setara kaki Ankr; definisi sinyal TIDAK berubah).
- [x] 2026-11-14 ~18:57 WIB — Uji mock (parsing respons contoh + pacing + logika sinyal + aturan watermark). Semua lolos (22/22, lihat "Uji mock" di bawah).
- [x] 2026-11-14 ~18:59 WIB — Cek key: BELUM ada (authd 403 untuk `custom.bscscan`, sama seperti konektor yang belum terdaftar; mekanisme surrogate terbukti jalan untuk `custom.ankr`). CLI gagal bersih dengan pesan jelas, tanpa bocor URL/key.
- [ ] TES LIVE — menunggu key BscScan dari user. Begitu key tersedia: `txlist` 1 wallet + `getLogs` 1 kontrak jendela kecil, lalu satu run penuh (run 170, catch-up dari blok 132534899).

## Yang ditemukan (implementasi saat ini)

- Cron `tracked-wallet-mint-scan-hourly` (interval 1 jam, timeout 7200 dtk) adalah instruksi prose
  untuk worker agent; TIDAK ada satu skrip scan kanonis. Tiap run, worker menulis skrip
  `tracked-mint-scan-run<N>*.py` baru dan memanggil modul Ankr
  (`custom.ankr/bin/ankr.py`: `ankr_getTransactionsByAddress` sent pass + `ankr_getLogs`
  address-filtered untuk inbound) + `fast_rpc.py` untuk receipt check + tip block.
- State: `~/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json`.
  Watermark TIDAK maju sejak run 141: `last_run.block_start = 132534899`, `block_end = null`.
  Jendela yang belum terpindai kini ~1.002.602 blok (sampai tip ~133537501). JANGAN reset watermark.
- Wallet set (baca segar tiap run): `tier-ab-watch-state.json["wallets"]` = 54 kunci +
  `wallet_confirmation.py TRACKED_WALLETS` = 6 → 55 unik (overlap 5, feed-only AFeng).
  Kecualikan wallet user: 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E dan
  0xcf3c6fc1bf670a8d3f03436395286f86dbee7418.
- Ambang (TIDAK berubah): sinyal Free Bacot >20% = minimal 12 entitas; trigger auto-mint >25% =
  minimal 14 entitas. Hitung ENTITAS; bila linkage belum diketahui, hitung per wallet + catat
  "linkage belum diverifikasi". Tidak ada peta klaster machine-readable di state (rujukan TRIO
  di body adalah historis) — driver menyediakan `ENTITY_CLUSTERS` kosong yang bisa diisi bila
  klaster tercatat kemudian.
- `machine_tokens` di state: daftar token pola mesin (fast-path amendment 2026-11-06) — driver
  menerapkan fast path yang sama: label machine-token tanpa verifikasi penuh, kecuali anomali
  (ukuran buy menyimpang jauh, muncul nama/simbol, website, atau jalur free-mint).
- Format temuan di state (`reported_findings`): `{counts, free_vs_paid, mints: [{call_to,
  kind, mint_contract, name, symbol, time_wib, token_id, tx, ...}]}` — driver baru menulis
  format yang kompatibel supaya dedupe `known_tx` tetap jalan.

## Pemetaan kaki Ankr → BscScan (setara, bukan jiplakan 1:1)

| Kaki lama (Ankr) | Kaki baru (BscScan) | Catatan |
|---|---|---|
| `ankr_getTransactionsByAddress` (sent pass, paginasi mundur) | `txlist` per wallet (`module=account&action=txlist`, `startblock`/`endblock`, `page`/`offset`, `sort=asc`) | BscScan mengembalikan tx dalam jendela langsung; paginasi bila hasil == offset (maks 10.000/call). |
| `ankr_getLogs` address-filtered per kontrak (inbound: Transfer dari zero) | `tokentx` + `tokennfttx` + `token1155tx` per wallet (`module=account`, `startblock`/`endblock`) | Transfer token KE wallet langsung terbaca; mint = `from == 0x0000...0000`. Lebih langsung dari getLogs per kontrak dan menutup inbound leg tanpa enumerasi kontrak dulu. |
| `ankr_getLogs` targeted per kontrak (verifikasi first-mint / inbound retry) | `getLogs` per kontrak (`module=logs&action=getLogs`, `topic0` = Transfer `0xddf252ad...`, `fromBlock`/`toBlock`) | Dipakai hanya untuk kandidat sinyal/trigger (maks 5 kontrak/run) + inbound retry rounds yang masih terbuka. Hasil dibatasi 1.000 log/call — driver membelah jendela bila penuh. |
| `ankr_getTokenHolders` (cross-check holder count) | `tokenholderlist` (`module=token&action=tokenholderlist`) | **Kemungkinan endpoint PRO BscScan** — driver memanggilnya hanya bila diminta eksplisit; error "Pro" dicatat sebagai tidak tersedia, BUKAN kegagalan run. Bukan kaki wajib scan. |

## Aturan BscScan tier gratis (dipatuhi klien)

- Maks 5 req/detik → klien memberi jeda 0,25 dtk antar call (4 req/detik, margin aman).
- Respons "No transactions found" (`status=0`) = hasil kosong, BUKAN error.
- Respons rate-limit ("Max rate limit reached") → retry 1× sesudah jeda 1 dtk; bila masih
  gagal, leg dicatat TIDAK TERVERIFIKASI (bukan 0) dan watermark TIDAK maju.
- "Invalid API Key" → berhenti dengan pesan jelas (key salah/belum aktif), watermark TIDAK maju.
- Per run steady-state (~1.200 blok): 55 wallet × (1 txlist + 3 transfer) = ~220 call + ≤5
  getLogs kandidat ≈ 225 call ≈ 60 dtk pacing. Jauh di bawah batas harian 100.000 call.
- Catch-up run 170 (jendela ~1.002.602 blok): jumlah call SAMA (BscScan memfilter
  `startblock`/`endblock` di sisi server); yang bertambah hanya jumlah record yang dikembalikan
  per call — paginasi menangani bila satu wallet >10.000 record (maks 20 halaman/wallet/leg;
  bila terpotong, wallet itu dicatat TIDAK TERVERIFIKASI dan watermark TIDAK maju).

## File yang dibuat/diubah

- BARU `~/workspace/custom-connectors/custom.bscscan/connector.yaml`
- BARU `~/workspace/custom-connectors/custom.bscscan/CONNECTOR.md`
- BARU `~/workspace/custom-connectors/custom.bscscan/bin/dynamic_credentials.py` (salinan dari ankr)
- BARU `~/workspace/custom-connectors/custom.bscscan/bin/bscscan.py`
- BARU `~/workspace/narrative-pulse/tracked-mint-scan-bscscan.py`
- BARU `~/workspace/narrative-pulse/test-bscscan-migration.py` (uji mock)
- BARU file ini (log migrasi + teks body cron revisi)
- TIDAK ADA file lain yang diubah. State, log, dan body cron TIDAK disentuh oleh migrasi ini
  (body cron revisi di bawah hanya TEKS untuk parent terapkan via `cron.update` sesudah tes live).

## Uji mock (tanpa key) — hasil

`python3 ~/workspace/narrative-pulse/test-bscscan-migration.py` → **22/22 PASS**
(2026-11-14 ~18:57 WIB, diulang ~18:59 WIB sesudah perbaikan pesan error credential):

- Klien: envelope OK → result; "No transactions found" → [] (bukan error); rate-limit →
  1 retry lalu OK; rate-limit 2× → `BscScanRateLimit`; "Invalid API Key" →
  `BscScanAuthError`; endpoint Pro → `BscScanProRequired`; pacing 0,25 dtk antar call
  terukur (0,25 dtk).
- Paginasi: `_paged` berhenti saat batch pendek; flag truncated di 20 halaman;
  `get_logs_all` membelah jendela saat 1.000 log penuh.
- Driver (fixture 55 wallet asli, tip dimock 133539000): kontrak 12 entitas → sinyal;
  14 entitas → trigger; 11 entitas → bukan sinyal; machine-token tanpa nama → fast path;
  machine-token bernama → anomali; 1 wallet gagal → exit 1 + watermark TETAP 132534899;
  run terverifikasi → watermark maju ke tip; transfer dari alamat non-zero → bukan mint.
- Verifikasi tanpa key yang sudah dilakukan: wallet set 55 unik (54 tier-ab + 6 feed,
  overlap 5, wallet user dikecualikan) + tip blok live via fast_rpc (133538539 pada
  ~18:53 WIB) — keduanya dibaca driver langsung dari file/endpoint yang sama dengan
  yang dipakai run produksi.
- CLI tanpa key: `bscscan.py txlist ...` → `ERROR: BscScanError: BscScan credential
  not available (key not yet stored via Secure Vault)` + exit 1, tanpa URL/key di output.

## Tes live (menunggu key) — rencana

1. `python3 ~/workspace/custom-connectors/custom.bscscan/bin/bscscan.py txlist <1 wallet feed> <tip-100> <tip>`
2. `python3 ~/workspace/custom-connectors/custom.bscscan/bin/bscscan.py logs <kontrak USDT> <tip-50> <tip> 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef`
3. Bila keduanya OK: jalankan driver penuh run 170 (dry-run dulu dengan `--dry-run` bila ada,
   lalu run nyata) dan verifikasi watermark maju + temuan ditulis ke state/log seperti format lama.

## TEKS BODY CRON REVISI (untuk parent: terapkan via cron.update SESUDAH tes live lolos)

Gantikan HANYA bagian-bagian ini di body `tracked-wallet-mint-scan-hourly`; semua amendment,
ambang, guard, dan larangan lain TIDAK berubah:

1. AMENDMENT 2026-11-03 ~12:02 WIB (kaki log inbound WAJIB Ankr) → DICABUT dan DIGANTI:

> AMENDMENT 2026-11-14 (migrasi Ankr → BscScan, perintah user "Ya, coba lewat BscScan"):
> Ankr MATI (freemium habis, HTTP 401 sejak 2026-11-09; 29 run gagal). Kaki data job ini
> kini WAJIB pakai BscScan API via modul `~/workspace/custom-connectors/custom.bscscan/bin/bscscan.py`
> (kunci dari connector `custom.bscscan`, JANGAN pernah tulis key di perintah/log).
> Driver kanonis tiap run: `python3 ~/workspace/narrative-pulse/tracked-mint-scan-bscscan.py --run <N>`.
> Driver itu menjalankan sent pass (`txlist` per wallet), inbound leg (`tokentx`/`tokennfttx`/
> `token1155tx` per wallet; mint = transfer dari zero address), paid trend, hitung sinyal
> entitas, dan menulis state + log + bukti run — watermark HANYA maju bila SEMUA leg
> terverifikasi. Bila BscScan mengembalikan rate-limit/invalid-key/error lain, perlakukan
> seperti kegagalan baca Ankr dulu: leg = TIDAK TERVERIFIKASI (bukan 0), watermark TIDAK maju,
> catat + retry run berikutnya; jangan retry agresif. `getLogs` BscScan dipakai hanya untuk
> verifikasi targeted per kontrak (maks 5 kontrak/run). `tokenholderlist` adalah endpoint yang
> kemungkinan PRO — bila ditolak, catat tidak tersedia, BUKAN kegagalan run.

2. METODE, paragraf "Pakai Ankr sebagai MODULE..." → diganti dengan:

> - Pakai BscScan sebagai MODULE (`bscscan.py`, BUKAN URL mentah dengan key): `txlist`
>   per wallet untuk sent pass dan `tokentx`/`tokennfttx`/`token1155tx` per wallet untuk
>   inbound (mint = transfer dari zero address ke wallet). Identifikasi mint baru sama
>   seperti sebelumnya: NFT (ERC-721/1155) dan share sale (ERC-20) — kontrak tujuan,
>   nama/simbol hanya bila terverifikasi on-chain, jumlah, waktu dari block timestamp
>   (bukan hitungan blok), dan gratis vs berbayar (quote/cost dibaca on-chain bila ada;
>   bila tidak terbaca, tulis unverified, jangan tebak).
> - Driver kanonis: `tracked-mint-scan-bscscan.py` (satu skrip tiap run, bukan skrip run<N>
>   baru tiap jam). Bila driver gagal total (exit bukan 0), jalankan langkah manual lama
>   (txlist/getLogs via `bscscan.py` CLI) hanya untuk diagnosis, dan laporkan kegagalannya.

3. METODE, paragraf "Pakai ~/workspace/fast_exec/fast_rpc.py..." → TAMBAHKAN kalimat:

> - Tip blok tetap dibaca via `fast_rpc` (`eth_blockNumber`, batch_race). `fast_rpc`
>   TIDAK dipakai untuk `eth_getLogs` broad (sudah terbukti gagal -32005 tiap run).

4. Tambahkan di akhir bagian METODE:

> - BACKLOG: watermark saat ini 132534899 (jendela ~1.002.602 blok sejak run 141). Run pertama
>   pasca-migrasi (run 170) WAJIB catch-up dari watermark itu lewat `txlist`/transfer BscScan
>   (satu call per wallet sudah mencakup seluruh jendela; paginasi bila >10.000 record).
>   Bila catch-up melebihi satu run, watermark maju per chunk yang SELURUHNYA terverifikasi dan
>   dicatat chunk mana yang sudah selesai — JANGAN pernah lompat watermark ke tip tanpa data.

5. Bagian "Pemulihan" di log/state run 169 yang menyebut `credentials.request_api_access
   reconnect:true for provider ankr` → SUDAH TIDAK BERLAKU (freemium habis, user 2026-11-14
   ~18:44 WIB). Pemulihan kini = BscScan key via Secure Vault (sudah diminta parent).

## HASIL TES LIVE PASCA RE-LINK (14 Nov ~19:35 WIB) — MIGRASI BSC DIBLOKIR

- Re-link selesai: key user terdaftar ulang untuk host api.etherscan.io; BscScan
  TERHUBUNG (koneksi aktif, kredensial tersimpan).
- Tes live via bscscan.py (timeout egress sempat 2x di awal — api.etherscan.io
  sempat tidak merespons 25–30 dtk, lalu pulih; flapping egress VM, bukan API):
  - chainid=1 (Ethereum): **OK, 0 record** di jendela tes → key VALID di V2.
  - chainid=56 (BSC): **"Free API access is not supported for this chain.
    Please upgrade your api plan for full chain coverage."** — dengan key VALID.
- KESIMPULAN: paket gratis Etherscan V2 TIDAK mencakup endpoint data BSC.
  Migrasi scan tracked-wallet ke BscScan **BUNTU** tanpa plan berbayar.
  JANGAN bayar tanpa perintah user.
- Yang TIDAK dilakukan: run 170 TIDAK dijalankan (driver akan gagal di chainid=56
  dengan error yang sama); body cron tracked-wallet-mint-scan-hourly TIDAK di-update
  (teks revisi di atas DIBEKUKAN); watermark tetap 132534899.
- CONNECTOR.md diperbarui 19:35 WIB (host V2, status blokir, chainid=1 sebagai
  proof-command). Driver + konektor tetap tersimpan untuk bila suatu hari ada jalur
  BSC gratis yang terverifikasi.
- ALTERNATIF GRATIS YANG MASIH TERBUKA (belum diuji, butuh keputusan user):
  RPC publik lain untuk eth_getLogs jendela kecil + pacing lambat (PublicNode sudah
  terbukti -32005; endpoint lain belum dicoba), atau menunggu reset kuota Ankr
  (tidak ada bukti akan reset). Scan tracked-wallet tetap MATI sampai ada jalur baru.
