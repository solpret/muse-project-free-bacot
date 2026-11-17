# FCFS CEPAT — poller rapat + eksekutor pre-warm (generik, config-driven)

Dibangun 14 Nov 2026 ~21:06–21:13 WIB atas perintah user ("Ya, bangun
versi cepatnya untuk sale FCFS berikutnya"). Pelajaran dari BTC Agent:
kuota gratis 210 habis <7 menit (kemungkinan ~1 menit) di antara dua cek
watch 2-menitan — padahal bacaan sudah satu batch (~1 dtk). Kekalahan
bukan di bacaan, melainkan (1) deteksi 2 menit terlalu jarang, (2)
rantai eksekusi berurutan (audit segar → baca ulang → cek sesi baw →
preview → eksekusi) terlalu lambat.

## File

| File | Isi |
|---|---|
| `fcfs_fast.py` | Alat utama (poller + pre-warm + eksekusi berguard) |
| `fcfs_fast.config.example.json` | Template config untuk sale berikutnya |
| `btc-agent-dryrun.json` | Config TEST read-only (kontrak BTC Agent, sale sudah selesai) |
| `fcfs_fast_state_<sale>.json` | State runtime (ditulis alat; last poll, pre-warm cache, events, terminal) |
| `fcfs_fast_<sale>.log` | Log append per sale |
| `FCFS_FAST.md` | Dokumen ini |

## Cara kerja

1. **Poller rapat** — loop kontinu, interval default 12 dtk (config
   `poll_interval_s`). Tiap poll SATU JSON-RPC batch: eth_blockNumber +
   eth_getBalance(agent) + semua `poll_calls` di config. Transport
   urllib polos + fallback 5 endpoint (fast_rpc.py TIDAK dipakai —
   flaky OSError lewat proxy). Bila batch gagal total: state lama
   dipertahankan, TIDAK ADA eksekusi dari data basi.
2. **Pre-warm** — sekali di awal + tiap `prewarm_interval_s` (default
   300 dtk): audit Binance untuk tiap kontrak di `audit_contracts` +
   cek sesi baw (`wallet status` + `wallet settings` → CONNECTED +
   devMode). Saldo BNB sudah ada di tiap poll. Saat trigger terdeteksi,
   yang tersisa hanya: baca-ulang verifikasi (~1 dtk) + preview +
   eksekusi. Bila cache pre-warm basi saat trigger, audit/sesi di-fetch
   segar dulu (safety di atas speed) dan latensi ekstra dicatat.
3. **Trigger** — semua kondisi di `trigger` terpenuhi dari data poll
   segar + sisa kuota > 0 + saldo BNB ≥ `min_bnb_wei`.
4. **Eksekusi (live saja)** — audit (cache segar / fetch segar) →
   sesi → baca-ulang → preview → execute SEKALI (tanpa retry) →
   verifikasi receipt (status 1 + freeDone=true + delta saldo token
   tepat `expected_delta_raw`). Kondisi terminal menghentikan loop:
   sukses / kuota habis / sale failed / slot sudah terpakai / audit
   RISK / preview kotor / 351803 / execute error / PENDING_CONFIRMATION.
5. **Mode tunggu (`--wait-until`, prosedur A+C 15 Nov 2026)** — loop
   di-start LANGSUNG saat keputusan dibuat dengan waktu buka sale;
   sebelum waktu itu loop hanya poll (trigger TIDAK dievaluasi, tanpa
   preview/execute), sesudahnya live penuh. Kondisi terminal (kuota
   habis / gagal / slot terpakai) tetap dicek tiap poll selama
   menunggu. State mencatat `waiting` + `wait_until` agar watchdog
   tahu loop yang menunggu itu SEHAT.

## Guard (tidak ada yang dilonggarkan)

- Hanya GRATIS: value 0; calldata di config harus sudah mengunci
  maxCost/cost-cap ke 0 bila fungsi mint punya parameter itu.
- Audit: hasResult=false = TIDAK ADA HASIL, bukan lolos (tidak
  menghentikan); RISK hit atau riskAlert non-null = STOP; kegagalan
  API audit = STOP.
- Preview bersih: success=true, simulationCode 000000000, tanpa error,
  value 0, tanpa authority/allowance changes, tanpa RISK, perubahan
  saldo sesuai harapan. Kode simulasi dibaca dari
  `data.simulationResult.simulationCode` (bentuk baru, live 16 Nov
  2026) atau `data.simulationCode` (bentuk lama); risiko dibaca dari
  `data.risks` (baru) dan `data.riskItems` (lama). Struktur preview
  tak dikenal = kotor (fail closed). Kode 351805 (gas/saldo/revert)
  = BUKAN terminal, kembali polling; 351803 = terminal.
- Website gate HARUS terverifikasi SEBELUM arm
  (`website_gate_verified=true` + URL + bukti di config).
- TIDAK PERNAH retry sesudah execute. TIDAK PERNAH paid mint.
- Mode live butuh DUA syarat: config `dry_run:false` DAN flag `--live`.
  Default = dry-run (poll + pre-warm saja, tanpa preview/execute).

## Cara meng-arm untuk sale berikutnya (PROSEDUR A+C, 15 Nov 2026)

1. Salin `fcfs_fast.config.example.json` → mis. `sale-baru.json`.
   Isi dari sumber TERVERIFIKASI: alamat kontrak, selector view
   (`started`, `failed`, free-minted, free-done + `{user}` untuk
   argumen alamat), calldata free-mint, kuota gratis total,
   `expected_delta_raw` (jumlah token mentah yang diterima),
   `token_contract` (untuk verifikasi delta saldo), kontrak audit.
2. Verifikasi website gate DULU (situs mencetak kontrak persis),
   lalu isi `website_gate_verified=true`, `website_url`,
   `website_evidence`.
3. Sanity check (read-only):
   `python3 fcfs_fast.py --config sale-baru.json --once`
4. Uji loop dry-run beberapa menit:
   `python3 fcfs_fast.py --config sale-baru.json --dry-run --duration-s 300`
5. Arm live — LANGSUNG saat keputusan dibuat (JANGAN via runonce cron):
   tulis pointer `armed-sale.json` (`sale_name`, `config`, `armed_at`,
   `wait_until` = waktu buka ISO 8601) LALU start loop saat itu juga:
   `nohup python3 fcfs_fast.py --config sale-baru.json --live --wait-until <waktu buka ISO 8601> > fcfs_fast_<sale>.nohup.log 2>&1 &`
   Loop hidup sejak sekarang, poll saja sampai waktu buka, live
   sesudahnya. Alasan: blackout throttle 15 Nov 2026 (18:45–20:54 WIB,
   287 run di-skip) membuktikan satu eksekusi cron bisa di-skip
   diam-diam — arming yang selamat hanya yang selesai SEBELUM blackout.
6. Verifikasi 1 menit pasca-arming (WAJIB, prosedur C): cek `pgrep -f
   fcfs_fast.py` + `fcfs_fast_state_<sale>.json` (last_poll_at segar,
   prewarm.session.ok=true, waiting=true bila sebelum buka). Bila
   proses tidak hidup → start via exec saat itu juga (exec kebal
   throttle cron).
7. Sesudah terminal: baca log + state; laporan mint (bila sukses)
   mengikuti pola lama (tx hash, blok, gas, verifikasi on-chain).

## Angka terukur (14 Nov 2026, dry-run live vs kontrak BTC Agent)

- `--selftest`: 27/27 checks PASS (config, trigger, parsing audit,
  parsing preview incl. bentuk gagal nyata, batch `{user}`, +
  10 cek `--wait-until` baru: parsing ISO+07:00/Z/epoch/naive,
  invalid ditolak, `is_waiting`, `terminal_from_poll`).
- Uji `--wait-until` (15 Nov 2026, config btc-agent-dryrun):
  `--once` + wait masa depan → MENUNGGU, state `waiting=true`,
  trigger TIDAK dievaluasi walau kondisi trigger terpenuhi di data
  poll; `--once` + wait masa lalu → "sudah lewat — live langsung",
  trigger dievaluasi normal; uji transisi offline (poll fake,
  wait 4 dtk, durasi 12 dtk) → 2 baris MENUNGGU lalu 5× TRIGGER
  TERDETEKSI sesudah wait berakhir.
- `--once`: poll 1,12 dtk (blok 133557326; started=true,
  freeMinted=210, paidMinted=1890, freeDone=false, BNB 0,0001464);
  pre-warm audit mint hasResult=false, audit token riskLevel 2 LOW
  (1 hit CAUTION), sesi CONNECTED + devMode aktif.
- Loop dry-run 60 dtk: 6 poll, kadens ~12 dtk, tiap batch 0,93–2,28
  dtk; blok maju konsisten (~24–28 blok/12 dtk); trigger terdeteksi
  tiap poll (config test) dan DICATAT TANPA eksekusi.
- Probe preview nyata (simulasi saja, tanpa broadcast): ~2,0 dtk,
  gagal dengan `error.code 351805` "execution reverted: CLOSED"
  (sale sudah tutup) — bentuk ini dipakai untuk memperbaiki parser:
  kode error top-level kini dikenali (sebelumnya parser hanya
  membaca `data.simulationCode`).
- Penolakan live-mode: `--live` dengan config dry_run=true DITOLAK
  ("MODE LIVE DITOLAK") — guard arming bekerja.

## Batas jujur

- **Loop mati bila VM restart.** Watchdog cron `fcfs-fast-watchdog`
  (2-menitan, dibuat 14 Nov 2026 ~21:16 WIB) menyalakan ulang dari
  pointer `armed-sale.json`; restart memakai flag arming yang sama
  (termasuk `--wait-until` bila ada di pointer). Hati-hati: restart
  harus memakai state yang sama agar tidak double-execute (alat
  sendiri punya pengaman `executed` per proses, tapi antar-proses
  mengandalkan `freeDone`/kuota di chain).
- **Blackout throttle runtime (15 Nov 2026, 18:45–20:54 WIB)** bisa
  men-skip SEMUA run cron selama ~2 jam — termasuk runonce arming
  dan run watchdog. Karena itu arming TIDAK PERNAH lagi via runonce
  cron (prosedur A+C): loop di-start langsung via exec saat keputusan
  dibuat. Loop yang sudah berjalan (proses nohup) tidak peduli
  scheduler sama sekali; satu-satunya jendela rawan adalah bila
  blackout + pergantian VM bertepatan di menit-menit akhir sebelum
  buka sehingga watchdog tidak bisa me-restart loop yang mati.
- **Status cron menipu:** run yang di-skip throttle tercatat
  `status="succeeded"` + `last_success_at` terisi. Untuk job
  kritis-waktu, yang menentukan adalah `cron.runs` (`started_at` ≠
  null) + bukti kerja nyata (proses/state file).
- **Preview + execute baw adalah bottleneck sisa.** Keduanya tidak
  bisa di-batch: preview ~2 dtk (gagal cepat; sukses bisa lebih
  lama), execute + konfirmasi broadcast butuh waktu Binance-side
  yang tidak terukur di sini (belum pernah dieksekusi lewat alat
  ini — jalur live BELUM teruji end-to-end; uji pertama harus pada
  sale nyata dengan pemantauan ketat).
- **Pre-warm awal ~8 dtk** (2 audit + 2 panggilan baw). Arm jauh
  sebelum jam buka; jangan arm di menit pembukaan.
- **Deteksi terburuk ≈ interval poll + durasi poll** (~13–14 dtk
  pada 12 dtk). Bila kuota habis lebih cepat dari
  deteksi+preview+execute, tetap kalah — alat ini memperkecil
  jendela, bukan menghilangkannya.
- **Egress VM bisa spike** (riwayat: batch 2,7–6,6 dtk saat bagus,
  12–28 dtk saat jelek). Endpoint fallback menahan satu endpoint
  mati, bukan semua jalur lambat.
- **Sesi baw / devMode bisa kedaluwarsa** di tengah menunggu
  (sesi saat ini berakhir 2026-11-16, devMode 2026-11-21).
  Pre-warm mendeteksinya lebih awal dan mencatatnya; bila sesi mati
  saat trigger, alat kembali polling (bukan terminal) — tapi slot
  bisa habis selagi menunggu user memperbarui sesi.
- **Bentuk output preview sukses TERVERIFIKASI live 16 Nov 2026
  ~23:00 WIB (Poffzi) — dan risiko yang ditulis di sini BENAR-BENAR
  TERJADI.** Preview sukses baw ternyata memakai struktur BARU:
  `data.{requestId, parsedTx, simulationResult, risks, tokenInfos,
  requireConfirmation, expiresAt, gasLimit}` dengan kode di
  `data.simulationResult.simulationCode` dan perubahan saldo di
  `data.simulationResult.balanceChanges`. Parser lama tidak
  mengenalinya → fail-closed → loop Poffzi TERMINAL 23:00:22 WIB,
  11 detik sesudah trigger (98 slot tersisa saat itu), TIDAK ADA
  mint yang dieksekusi; kuota 100/100 habis ~23:20 WIB, saldo agent
  0. Parser diperbaiki malam itu juga (mendukung bentuk baru +
  lama, risiko dari `data.risks` + `data.riskItems`), selftest
  31/31 PASS. Pelajaran: bentuk sukses HARUS diuji dari sampel
  nyata sebelum sale berikutnya — jangan andalkan asumsi body cron
  lama; bila baw mengubah format lagi, log akan menunjukkan kunci
  baru dan parser diperbaiki dari log tersebut.
