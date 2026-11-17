# Uji RPC Publik BSC Gratis untuk Scan Mint Tracked-Wallet — 14 Nov 2026

Perintah user 14 Nov ~20:20 WIB ("Ya, coba RPC publik lain untuk scan").
Tujuan: gantikan Ankr (401 sejak 9 Nov) + BscScan (free Etherscan V2 tidak
mencakup BSC chain 56) sebagai sumber `eth_getLogs` untuk scan mint
tracked-wallet. Semua uji: curl/JSON-RPC polos dari VM, tanpa key, tanpa
signup, tanpa bayar. Filter uji = filter ASLI driver (Transfer topic0 +
from=zero topic1 + to=AFeng 0xbf004bff64725914ee36d03b87d6965b0ced4903 topic2
— sama seperti tes fallback run 169).

## Hasil: SATU endpoint jalan — bloXroute

**https://bsc.rpc.blxrbdn.com** (bloXroute, public, tanpa key) — SATU-SATUNYA
yang melayani `eth_getLogs`:

| Uji | Hasil |
|---|---|
| `eth_blockNumber` | OK, ~0,9 dtk, head ~133.552.000 |
| `eth_getLogs` 50 blok, filter driver | OK, 3,41 dtk, 0 log (AFeng tidak mint di jendela itu) |
| `eth_getLogs` 1000 blok, filter driver | OK, 25,61 dtk, 0 log |
| `eth_getLogs` 1000 blok, topic array 55 wallet | OK, 18,31 dtk, 0 log |
| `eth_getLogs` 500 blok, topic array 55 wallet | OK, 24,62 dtk, 0 log |
| `eth_getLogs` TransferSingle 1000 blok, 55 wallet | OK, 26,18 dtk / 12,02 dtk (single-wallet), 0 log |
| Sanity broad topic0-only 1 blok | OK, 10,04 dtk, **489 log** (log benar-benar mengalir) |
| Kontrol positif addr=USDT topic0-only 10 blok | OK, 17,46 dtk, **834 log** |
| Pacing 10× `getLogs` 50 blok berurutan | Semua OK, 1,2–16,1 dtk, **tanpa 429** |
| `eth_call` USDT `name()` | OK, 0,65 dtk → "Tether USD" |
| `eth_getBlockByNumber` (timestamp) | OK, cocok dengan jam dinding |
| `eth_getTransactionByHash` tx ~3 jam | OK (AGC claim #35, block 133527431, value 0) |
| `eth_getTransactionByHash` tx ~7,4 jam | OK (AGC claim #34, block 133495118) |
| `eth_getTransactionByHash` tx ~11,4 jam | **NULL** (claim #33) — indeks tx dangkal |
| `eth_getTransactionByHash` tx ~15/19/23 jam & 6–11 hari | **NULL** — indeks tx hanya ~7–11 jam ke belakang |
| Kontrol positif mekanik | From-zero log nyata di blok 133552035 di-query ulang dengan filter driver `[T,0,to]` → **1 log, same-tx-match=1**, kontrak 0xe07150dd3a870ff0115fc4e3c80529f92e294d89 — jalur filter terbukti mengembalikan mint asli |
| Scan broad from-zero 5000 blok terakhir | ~6.000 log/1000 blok; **0 mint ke tracked wallet** dalam 5000 blok (~37 menit) — normal, mint ke 55 wallet spesifik itu jarang |

## Tabel kegagalan (semua endpoint lain)

| Endpoint | `eth_blockNumber` | `eth_getLogs` | Error verbatim |
|---|---|---|---|
| bsc-dataseed.binance.org | OK ~2,2 dtk | GAGAL | `{"code": -32005, "message": "limit exceeded"}` — bahkan jendela **1 blok**, bahkan **dengan address filter** (USDT) |
| bsc-dataseed1/2/3/4.defibit.io | OK ~0,8–1,5 dtk | GAGAL | `{"code": -32005, "message": "limit exceeded"}` (50 blok; 1/5/10 blok juga gagal di dataseed1) |
| bsc-dataseed1/2.ninicoin.io | OK ~1,4 dtk | GAGAL | `{"code": -32005, "message": "limit exceeded"}` |
| bsc-dataseed.bnbchain.org | OK ~1,9 dtk | GAGAL | `{"code": -32005, "message": "limit exceeded"}` |
| bsc-dataseed1/2.bnbchain.org | OK ~1,0 dtk | GAGAL | `{"code": -32005, "message": "limit exceeded"}` |
| binance.llamarpc.com | GAGAL | — | `URLError: Remote end closed connection without response` (2×, retry juga) |
| 1rpc.io/bnb | GAGAL | — | `HTTP 403: error code: 1010` (Cloudflare) |
| bsc.meowrpc.com | GAGAL | — | `HTTP 403: error code: 1010` (Cloudflare) |
| endpoints.omniatech.io/v1/bsc/mainnet/public | GAGAL | — | `RemoteDisconnected: Remote end closed connection without response` |
| bnb.api.onfinality.io/public | GAGAL | — | `HTTP 429: {"code":-32029,"message":"Too Many Requests, Please apply an OnFinality API key or contact us to receive a higher rate limit"}` |
| bsc-mainnet.public.blastapi.io | GAGAL | — | `HTTP 403: error code: 1010` (Cloudflare) |
| bnb-mainnet.public.blastapi.io | GAGAL | — | `URLError: Remote end closed connection without response` |
| bsc.blockpi.network/v1/rpc/public | GAGAL | — | `HTTP 403: error code: 1010` (Cloudflare) |
| bsc.drpc.org | GAGAL | — | `HTTP 403: error code: 1010` (Cloudflare) |
| bsc-pokt.nodies.app | GAGAL | — | Timeout 15 dtk; retry: `HTTP 403: The network of this endpoint requires a paid subscription plan. Subscribe at https://nodies.app to get access.` |
| rpc.therpc.io/bsc | GAGAL | — | Timeout 15 dtk; retry: non-JSON (2185 bytes, halaman error) |
| bsc-rpc.publicnode.com | GAGAL | — | `HTTP 403: error code: 1010` (Cloudflare) |
| bsc.publicnode.com | GAGAL | — | `HTTP 403: error code: 1010` (Cloudflare) |
| bsc.rpc.blxrbdn.com | OK | — | (lihat tabel sukses di atas — bukan kegagalan) |
| rpc-bsc.48.club | OK ~0,5–1,5 dtk (flaky: 1× head=None) | SEBAGIAN | 50 blok: `{"code": -32000, "message": "invalid block range params"}` lalu `HTTP 429`; 20 blok OK 0,84 dtk; 10/1 blok OK ~0,6–0,8 dtk — max ~20 blok + 429 gampang = **tidak dipakai** (cadangan pun tidak layak: 8000 blok/jam butuh ~400 call) |
| rpc.ankr.com/bsc (tanpa key, 1×) | GAGAL | — | `{"code": -32000, "message": "Unauthorized: You must authenticate your request with an API key. Create an account on https://www.ankr.com/rpc/ and generate your personal API key for free."}` — 401 terkonfirmasi |

## Yang disambungkan

- **Driver baru:** `~/workspace/narrative-pulse/tracked-mint-scan-rpc.py`
  (py_compile OK; `eth_getLogs` chunk 1000 blok, topic array 55 wallet,
  Transfer + TransferSingle; per mint: `eth_getTransactionByHash` untuk
  value gratis/berbayar + `eth_getBlockByNumber` untuk timestamp +
  `eth_call` nama/simbol; verifikasi targeted maks 5 kontrak; ambang sinyal
  TIDAK berubah: >20% = min 12 entitas, trigger >25% = min 14 entitas;
  driver HANYA flag, tidak eksekusi).
- **Kebijakan gap:** watermark 132534899, gap ~1,02 juta blok. Bila gap
  >40.000 blok (≈5 jam — di bawah batas indeks tx ~7 jam yang terbukti),
  run mulai dari tip-2000 dan gap dicatat hilang di state/log/findings.
  Gap ≤40.000 blok di-scan penuh. TIDAK ada backfill raksasa.
- **Batas yang dicatat jujur di driver + body cron:**
  (1) sent-pass `txlist` TIDAK BISA direplikasi RPC mana pun (tidak ada
  metode txlist) — paid trend kini dari nilai tx mint saja; tren pure-buy
  (swap) = TIDAK TERVERIFIKASI, bukan 0.
  (2) Indeks tx bloXroute dangkal (~7 jam OK, ~11 jam NULL) — bila tx mint
  tidak terbaca, free/paid = unverified, TIDAK PERNAH default gratis
  (driver mencatat `tx_lookup_failed` + `free_unverified_mints`).
  (3) 48.club tidak dipakai (max ~20 blok + 429).
- **Body cron** `tracked-wallet-mint-scan-hourly` di-update (amendment
  2026-11-14 ~20:50 WIB di atas; menggantikan amendment Ankr 2026-11-03
  ~12:02; revisi BscScan dibekukan) + baca-balik via `cron.view`
  terverifikasi. Jadwal tetap 1 jam, timeout 7200 dtk, run berikut
  21:05:21 WIB.
- **Uji kering driver (run 170 --dry-run, jendela live 1003 blok):**
  status OK, 55 wallet, 0 mint baru, 0 chunk gagal, JSON
  `scan-runs/run170-rpc-findings.json` valid; state/log TIDAK ditulis
  (dry-run). Durasi ~58 dtk.

## Run live pasca-migrasi (run 170)

- Manual `cron.run` 14 Nov ~20:44 WIB (run_id 9d37c5ef-17e3-4fe6-9e1b-ed5cd33f6cc9):
  status QUEUED — antre di belakang satu run terjadwal yang sedang jalan.
- Run terjadwal 20:05 WIB (run_id da6e1781-ad54-40fa-b3a9-d0bd1e4c4a88)
  baru MULAI 20:45:34 WIB (catchup terlambat) dan masih RUNNING saat doc ini
  ditulis (~20:55 WIB). Run ini mulai SETELAH body cron di-update (~20:43 WIB),
  jadi kemungkinan memakai body baru (driver RPC) — belum bisa dipastikan dari
  luar; konfirmasi dari handoff hasil run. Bila run itu yang menjadi run 170
  (driver menghitung run_no dari state: 169 → 170), maka manual run di belakangnya
  menjadi run 171.
- HASIL LIVE: MENUNGGU handoff run — update doc ini begitu hasilnya tiba
  (watermark maju ke tip + state/log ditulis = scan HIDUP; bila gagal,
  catat error verbatim di sini).

## File terkait

- Driver: `~/workspace/narrative-pulse/tracked-mint-scan-rpc.py`
- Skrip uji (ephemeral, /tmp): `rpc_scan_test.py`, `rpc_scan_test2.py`,
  `rpc_scan_test3.py`, `rpc_scan_test4.py`, `rpc_positive_control.py`,
  `rpc_positive_control2.py` (+ log + JSON hasil masing-masing).
- State/log: `tracked-wallet-mint-scan-state.json`,
  `tracked-wallet-mint-scan-log.md`, `scan-runs/run170-rpc-findings.json`.
- Dokumen migrasi lama (BscScan, dibekukan): `scan-bscscan-migration.md`.
