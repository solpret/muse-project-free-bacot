# Investigasi Insiden Piagent — Loop FCFS Tidak Sempat Jalan

> Status: DRAFT berjalan (checkpoint 1, ditulis 15 Nov 2026 ~21:28 WIB).
> Metode: READ-ONLY. Tidak ada cron/config/pointer/state yang diubah, tidak ada
> loop yang di-start, tidak ada re-arm. Semua fakta di bawah dikutip dengan sumbernya.
> Bedakan FAKTA (dengan sumber) dari INFERENSI (ditandai).

## 1. Ringkasan eksekutif

- Sale Piagent buka 19:00 WIB 15 Nov 2026, 1.000 kursi gratis habis <10 menit.
- Loop FCFS seharusnya nyala 18:50 WIB via runonce cron `piagent-fcfs-start-1850`.
  Cron itu TIDAK PERNAH mengeksekusi: catatan run menunjukkan
  `result_summary = "Skipped this scheduled run because safety throttling is
  temporarily active"`, `started_at_utc = null`, tapi `status = "succeeded"`.
- Akibatnya `armed-sale.json` tidak pernah ditulis, loop tidak pernah start, dan
  watchdog FCFS (yang hanya menjaga bila pointer ada) diam sepanjang malam —
  benar menurut bodinya, tapi buta terhadap kegagalan arming.
- Parent menyalakan loop manual 19:09:29 WIB; poll pertama 19:09:36 WIB
  (blok 133733148): `freeSold = 1000/1000` — terminal "kuota gratis habis".
  Tidak ada transaksi, tidak ada uang keluar.
- **Bukti baru investigasi ini:** throttling TIDAK terisolasi ke satu cron.
  Dua watchdog ber-cadence 2 menit (FCFS dan ingest Solana) sama-sama tidak
  mencatat satu run pun selama ~2 jam (18:44/18:45 → 20:53/20:55 WIB).
  Sementara itu proses yang mereka jaga (daemon ingest PID 6543) TETAP HIDUP
  dan menulis data sampai 20:15:22 WIB — jadi kekosongan itu bukan karena VM
  mati, melainkan karena run cron tidak dieksekusi/dicatat.
- **Pergantian VM TERPISAH** terjadi 20:14:58 WIB (boot time terverifikasi) —
  membunuh daemon ingest dan service systemd unsolvable-live; keduanya
  dipulihkan watchdog ~20:55–20:57 WIB sesudah run cron kembali jalan.
  Pergantian VM ini terjadi 85 menit SESUDAH arming Piagent gagal dan BUKAN
  penyebabnya.

## 2. Timeline terverifikasi

Semua jam WIB (UTC+7) kecuali dinyatakan lain.

| Jam (WIB) | Peristiwa | Sumber |
|---|---|---|
| 15 Nov 16:20:23 | Dry-run `--once` piagent: trigger terdeteksi (freeSold 0/1000), tanpa eksekusi | `~/workspace/fast_exec/fcfs_fast_piagent.log` |
| 15 Nov 17:32:23 | Daemon ingest Solana restart #20 (PID 6543) connect, NEW mengalir | `ingest-watchdog.log` + `ingest-watchdog-state.json` |
| 15 Nov 18:43 | Baris log TERAKHIR watchdog ingest Solana sebelum kekosongan (SEHAT, PID 6543) | `~/workspace/solana-trading/infra/ingest-watchdog.log` |
| 15 Nov 18:44:54 | Baris log TERAKHIR watchdog FCFS sebelum kekosongan ("armed-sale.json TIDAK ADA -> DIAM") | `~/workspace/fast_exec/fcfs-watchdog.log` |
| 15 Nov 18:50:00 | `piagent-fcfs-start-1850` terjadwal | `cron.runs` (run_id bf4ec072-dfa2-4336-a6eb-f81089ae2a14) |
| 15 Nov 18:50:09 | Run dicatat selesai: status `succeeded`, `started_at_utc = null`, `result_summary = "Skipped this scheduled run because safety throttling is temporarily active."` | `cron.runs` (record yang sama) |
| 15 Nov 19:00 | Sale Piagent buka (1.000 kursi gratis) | Fakta awal terverifikasi parent |
| 15 Nov 19:09:29 | Parent menulis `armed-sale.json` manual + start loop `--live` manual | `armed-sale.json` (`armed_at 2026-11-15T19:10:00+07:00`); `fcfs_fast_piagent.log` |
| 15 Nov 19:09:36 | Poll #1 loop: blok 133733148, `freeLeft=1, freeSold=1000`, BNB 0,000106696217850609 → terminal "kuota gratis habis" | `fcfs_fast_state_piagent.json` + `fcfs_fast_piagent.log` |
| 15 Nov 20:14:58 | **Pergantian VM (boot)** — `uptime -s` | `uptime -s` / `who -b` (dijalankan 21:27 WIB) |
| 15 Nov ~20:15:22 | NEW terakhir daemon ingest; daemon mati diam-diam ~20:15:25 WIB | `ingest-watchdog-state.json` (`restart_reason` #21) |
| 15 Nov 20:15 | State unsolvable-live basi (last_poll_at 13:15:04 UTC) — service mati bersama VM | `live-state.json` + ringkasan watchdog 20:55 WIB |
| 15 Nov 20:53–20:57 | Run cron kembali tercatat: watchdog ingest restart #21 (PID 6146, 20:56:19 WIB); service unsolvable-live aktif lagi (ActiveEnterTimestamp 13:55:47 UTC = 20:55:47 WIB, MainPID 5981, NRestarts=0) | `ingest-watchdog.log`; `systemctl show unsolvable-live`; `live-watchdog-state.json` (last_restart_at 20:56:56) |
| 15 Nov 20:55 → | Watchdog FCFS kembali mencatat run tiap ~2 menit (state terminal piagent → DIAM) | `fcfs-watchdog.log` |
| 15 Nov 21:27:37 | Investigasi ini berjalan; VM up 1:12 (boot 13:14:58 UTC) | `uptime` |

## 3. Bukti per pertanyaan investigasi

### 3.1 Catatan run persis cron `piagent-fcfs-start-1850` (FAKTA)

Sumber: `cron.runs` (id `piagent-fcfs-start-1850`, limit 5) + `cron.status`
(ditarik 15 Nov 2026 ~21:27 WIB).

- `run_id`: bf4ec072-dfa2-4336-a6eb-f81089ae2a14
- `scheduled_for_local`: Sun 2026-11-15 18:50:00 WIB
- `scheduled_for_utc`: 1794743400
- `started_at_utc`: **null** (tidak pernah start)
- `finished_at_utc`: 1794743409 (= 18:50:09 WIB — 9 detik sesudah jadwal)
- `status`: **`succeeded`**
- `result_summary`: **"Skipped this scheduled run because safety throttling is temporarily active."**
- `error_text`: null
- `trigger_reason`: scheduled
- `cron.status`: `enabled: false` (runonce terpakai), `last_run_at_local` 18:50:09 WIB,
  `last_status: "succeeded"`, `last_success_at_local` 18:50:09 WIB,
  `next_run_at_local: null`, `in_flight: false`, `consecutive_failures: 0`,
  `schedule: runonce@2026-11-15T18:50:00, timezone Asia/Jakarta`.

**Anomali pencatatan (FAKTA):** run yang tidak pernah mengeksekusi dicatat
`status = "succeeded"` DAN `last_success_at` terisi. Artinya pengecekan
"apakah cron jalan?" yang hanya membaca status/last_success akan menjawab
"sudah jalan" — padahal tidak. Ini yang membuat kegagalan tidak ketahuan
sampai pengecekan latar ~19:08 WIB.

### 3.2 Apakah throttling runtime-wide atau terisolasi? (FAKTA + INFERENSI)

**FAKTA — kekosongan run dua watchdog independen:**

- **fcfs-fast-watchdog** (interval 2 menit): baris log terakhir sebelum
  kekosongan 18:44:54 WIB; baris berikutnya 20:55 WIB. Kekosongan
  **~2 jam 10 menit** — padahal pada cadence 2 menit seharusnya ~65 run
  tercatat. Sebelumnya log menunjukkan run tiap ~2 menit nyaris tanpa jeda
  (jeda terpanjang lain hari itu: 14:56:54 → 15:30:54 WIB, 34 menit).
  Sumber: `~/workspace/fast_exec/fcfs-watchdog.log` (dibaca penuh).
- **solana-ingest-watchdog** (interval 2 menit): baris log terakhir sebelum
  kekosongan 18:43 WIB; baris berikutnya 20:57 WIB (restart #21). Kekosongan
  **~2 jam 10 menit**. Sumber: `~/workspace/solana-trading/infra/ingest-watchdog.log`
  (30 baris terakhir) + `ingest-watchdog-state.json` (`restart_reason` #21
  mencatat sendiri: "tidak ada run watchdog tercatat 18:45-20:53 WIB (~2 jam),
  kemungkinan run cron ter-skip/throttle runtime").
- **Daemon ingest PID 6543 tetap hidup selama kekosongan**: NEW token terakhir
  sebelum mati tercatat 20:15:22 WIB; pools.db-wal segar tiap cek sampai
  18:43 WIB. Sumber: `ingest-watchdog-state.json`.

**INFERENSI (kuat, tapi bukan bukti langsung):** dua job independen
ber-cadence sama yang berhenti mencatat run pada menit yang sama (~18:44),
sementara proses yang mereka jaga tetap hidup, + satu runonce di 18:50 yang
dicatat "Skipped ... safety throttling" → throttling terjadi di **lapisan
scheduler runtime**, bukan di masing-masing job. Ini runtime-wide untuk
setidaknya jendela ~18:44–20:53 WIB.

**HASIL LENGKAP (ditarik dari `scheduler.job_runs` via muse.db, 15 Nov ~21:30 WIB):**

Jendela blackout yang terukur: **18:45:39 → 20:54:31 WIB (2 jam 8 mnt 52 dtk).**
- Run terakhir yang DIEKSEKUSI sebelum blackout: `unsolvable-live-watchdog`
  11:45:03 UTC (18:45:03 WIB, started, summary null); `fcfs-fast-watchdog`
  11:44:54 UTC (18:44:54 WIB, baris log terakhir).
- Run pertama yang DI-SKIP: `solana-ingest-watchdog` 11:45:39 UTC (18:45:39 WIB).
- Run pertama yang DIEKSEKUSI sesudah blackout: `flap-sh-safety-watch`
  13:54:31 UTC (20:54:31 WIB); `free-mint-hot-leg` 13:54:38 UTC;
  `fcfs-fast-watchdog` 13:54:54 UTC; `unsolvable-live-watchdog` 13:55:03 UTC;
  `solana-ingest-watchdog` 13:55:39 UTC.

Agregat jendela 18:44–20:53 WIB (scheduled_for_utc 1794743040–1794750780):
**30 job, ~290 run terjadwal, 287 di-skip (tidak pernah start), 0 failed.**

| Job | Run | Di-skip |
|---|---|---|
| fcfs-fast-watchdog | 65 | 64 (1 sempat jalan 18:44:54, sebelum blackout) |
| solana-ingest-watchdog | 64 | 64 |
| unsolvable-live-watchdog | 64 | 63 (1 sempat jalan 18:45:03) |
| free-mint-hot-leg | 26 | 25 |
| paper-trading-solana-15m | 9 | 9 |
| agent-registry-watch | 9 | 9 |
| paper-trading-m3-solana-15m | 8 | 8 |
| free-mint-backfill | 7 | 7 |
| free-mint-search | 4 | 4 (19:01, 19:31, 20:01, 20:31) |
| grove-watch, flap-sh-safety-watch, heartbeat, bobbie-listing-watch, gate-blocked-recheck, scan-gap-watch | 4 masing-masing | 4 masing-masing |
| pending-coin-swap-watch | 3 | 3 |
| termix-hosting-loop, asset-sell-watch, agc-chart-watch, hive-launch-watch, agio-free-mint-watch | 2 masing-masing | 2 masing-masing |
| tracked-wallet-mint-scan-hourly | 1 | 1 (run 19:05) |
| square-daily-draft | 1 | 1 (19:37 WIB) |
| project-recap-2h | 1 | 1 (20:19 WIB) |
| piagent-fcfs-start-1850 | 1 | 1 (18:50 WIB) |
| relay-deepread-watchdog, holder-candidate-watch | 1 masing-masing | 1 masing-masing |

**Pengecualian — job yang TETAP JALAN selama blackout (FAKTA):**
`deterministic-doctor` (2 run, 0 skip, contoh 12:00:00 UTC = 19:00 WIB,
summary `{"results":[]}`), `feed-pulse-19` (2 run, 0 skip),
`feed-pulse-20` (1 run, 0 skip). Ketiganya adalah job sistem runtime.
Artinya throttle mengenai **dispatch kerja agen**, bukan scheduler secara total.

**Preseden (FAKTA):** sebelum blackout ini sudah ada **496 run ter-skip**
("Skipped ... safety throttling") dengan yang paling awal tercatat
**8 Nov 2026 21:55:31 WIB** — mekanismenya bukan hal baru. NAMUN untuk
`fcfs-fast-watchdog` sendiri, sebelum 18:45:39 WIB 15 Nov: **643 run
dieksekusi berturut-turut tanpa satu skip pun** (max gap antar run
dieksekusi = 120,0 detik = persis cadencenya). Jadi blackout kontinu
2 jam 9 menit ini **belum pernah terjadi sebelumnya** untuk job itu;
yang historis normal adalah skip satuan yang tersebar (tidak terlihat
pada job ber-cadence 2 menit).

**KESIMPULAN 3.2:** throttling **runtime-wide** (semua job agen, semua
cadence, 100% run di jendela) — BUKAN terisolasi ke cron Piagent.
Cron Piagent hanya satu dari 287 korban; ia yang paling mahal karena
runonce-nya tidak punya kesempatan kedua dan jendelanya (sale 10 menit)
lebih pendek dari blackout-nya.

### 3.3 Apa arti "safety throttling" menurut dokumentasi? (FAKTA)

- `~/docs/scheduling-and-watching.md` — **TIDAK menyebut "safety throttling"
  sama sekali.** Dokumen ini justru menyatakan "Background work runs reliably"
  dan "Check the run history, not the schedule" — yang terakhir ini tepat
  menjadi pelajaran insiden (jadwal/status menipu, riwayat run yang benar).
  Dokumen juga mencatat: "If Muse restarts during a run, the run resumes
  when it safely can" — tidak ada ketentuan tentang run yang di-skip
  sebelum start.
- `~/docs/chat/scheduling-and-watching.md` — **juga TIDAK menyebut "safety
  throttling".** Yang ada: "schedules can run late", "Both mechanisms poll.
  Changes can be missed between checks", dan bagian "Recovery after
  replacement" (runtime mengelola recovery untuk saved jobs/crons; program
  kustom butuh jalur startup sendiri). Tidak ada mitigasi terdokumentasi
  untuk blackout throttle berjam-jam, dan tidak ada ketentuan bahwa run
  yang di-skip akan dijadwalkan ulang / catch-up.
- **INFERENSI:** "safety throttling is temporarily active" adalah mekanisme
  runtime yang tidak terdokumentasi di docs yang tersedia untuk agen. Tidak
  ada cara agen-side untuk mengetahui kapan ia aktif, berapa lama, atau
  job mana yang kena — selain membaca `cron.runs` sesudah kejadian.

### 3.4 Watchdog FCFS memang tidak punya apa-apa untuk dijaga (FAKTA)

- `armed-sale.json` saat ini: `{"sale_name": "piagent", "config":
  "/home/hatch/workspace/fast_exec/piagent.json", "armed_at":
  "2026-11-15T19:10:00+07:00"}` — ditulis parent SECARA MANUAL ~19:10 WIB
  (mtime file 12:09 UTC = 19:09 WIB). Sebelum itu file TIDAK ADA: seluruh
  baris log watchdog 14 Nov 23:09 UTC s.d. 15 Nov 18:44:54 WIB berbunyi
  "armed-sale.json TIDAK ADA -> tidak ada sale di-arm -> DIAM".
- `fcfs-watchdog-state.json`: **tidak ada** (probe baca gagal di run-run
  watchdog — konsisten: tidak pernah ada restart yang dicatat).
- State loop `fcfs_fast_state_piagent.json`: `started_at 2026-11-15 19:09:29 WIB`,
  `live: true`, `terminal: "terminal: kuota gratis habis"`, `last_poll`
  blok 133733148, `freeSold: 1000`, `checked_at 19:09:36 WIB`. Pre-warm
  audit: PiToken riskLevel 1 LOW hit 0; PiGenesis hasResult=false; sesi
  connected=True devMode=True, session_expires 2026-11-17T12:09:15+00:00.
- Log loop `fcfs_fast_piagent.log`: hanya dua sesi — dry-run `--once`
  16:20:23–16:20:32 WIB (trigger terdeteksi, freeSold 0) dan live
  19:09:29–19:09:36 WIB (poll #1 langsung terminal). **Tidak ada sesi
  18:50 WIB.** Ini mengonfirmasi dari sisi alat bahwa cron 18:50 tidak
  pernah menjalankan apa pun.

### 3.5 Pergantian VM (FAKTA)

- `uptime -s`: **2026-11-15 13:14:58 UTC = 20:14:58 WIB**. `who -b`:
  system boot Nov 15 13:15 UTC. Saat dicek 14:27:37 UTC (21:27:37 WIB),
  uptime 1:12.
- Service `unsolvable-live`: ActiveState=active, MainPID=5981, NRestarts=0,
  ActiveEnterTimestamp Sun 2026-11-15 13:55:47 UTC (= 20:55:47 WIB) —
  konsisten dengan pemulihan watchdog 20:56 WIB, BUKAN dengan start lama.
- **INFERENSI:** pergantian VM terjadi 20:14:58 WIB — 85 menit sesudah
  arming Piagent gagal (18:50) dan 75 menit sesudah sale buka (19:00).
  Ia menjelaskan kematian daemon ingest (~20:15:25) dan service unsolvable
  (state basi 20:15), tapi TIDAK menjelaskan kekosongan run cron 18:44–20:53
  (daemon PID 6543 hidup melewati 18:44–20:15; bila VM diganti ~18:44,
  PID itu sudah mati saat itu — faktanya ia menulis NEW sampai 20:15:22).
  Jadi ada DUA kegagalan independen yang tumpang tindih waktunya:
  (a) throttle scheduler ~18:44–20:53 WIB, (b) pergantian VM 20:14:58 WIB.

## 4. Akar penyebab (draf awal — digantikan §5 final)

1. **Penyebab langsung kegagalan Piagent:** runonce cron 18:50 WIB di-skip
   runtime ("safety throttling"), tanpa eksekusi dan tanpa catch-up, dengan
   status menipu "succeeded".
2. **Penyebab lolosnya deteksi:** tidak ada verifikasi pasca-arming. Satu-satunya
   mekanisme pengaman (watchdog FCFS) baru aktif bila pointer ada — dan pointer
   hanya ditulis oleh run yang di-skip itu. Rantai dependensi: cron → pointer →
   watchdog → loop. Putusnya mata rantai pertama membuat seluruh rantai diam.
3. **Faktor pemberat:** status "succeeded" pada run yang di-skip membuat
   pengecekan cepat (`cron.status`) tidak bisa membedakan sukses vs skip;
   hanya `cron.runs` + `started_at = null` yang membongkarnya.
4. **Bukan penyebab:** pergantian VM 20:14:58 WIB (terlalu telat); kode
   fcfs_fast.py (dry-run 16:20 lolos 17/17 selftest + trigger terdeteksi);
   audit/sesi (pre-warm 19:09 bersih, sesi hidup); jaringan (poll 19:09
   berhasil 0,9 dtk).

## 5. Akar penyebab (final)

1. **Penyebab langsung kegagalan Piagent:** runonce cron 18:50 WIB di-skip
   runtime ("safety throttling"), tanpa eksekusi dan tanpa catch-up, dengan
   status menipu "succeeded".
2. **Penyebab lolosnya deteksi:** tidak ada verifikasi pasca-arming. Satu-satunya
   mekanisme pengaman (watchdog FCFS) baru aktif bila pointer ada — dan pointer
   hanya ditulis oleh run yang di-skip itu. Rantai dependensi: cron → pointer →
   watchdog → loop. Putusnya mata rantai pertama membuat seluruh rantai diam.
3. **Faktor pemberat:** status "succeeded" pada run yang di-skip membuat
   pengecekan cepat (`cron.status` / `last_success_at`) tidak bisa membedakan
   sukses vs skip; hanya `cron.runs` (`started_at = null` +
   `result_summary = "Skipped..."`) yang membongkarnya.
4. **Konteks yang memperparah:** blackout throttle 2 jam 9 menit (18:45:39–
   20:54:31 WIB) menutupi SELURUH jendela sale Piagent (19:00–19:10 WIB) —
   bahkan seandainya arming dijadwalkan ulang ke 19:00 atau 19:05, ia tetap
   akan di-skip. Satu-satunya arming yang selamat adalah arming yang
   SELESAI SEBELUM 18:45 WIB.
5. **Bukan penyebab:** pergantian VM 20:14:58 WIB (85 menit sesudah arming
   gagal; menjelaskan kematian daemon ingest + service unsolvable, bukan
   kegagalan Piagent); kode fcfs_fast.py (dry-run 16:20 lolos 17/17 selftest
   + trigger terdeteksi; poll manual 19:09 berhasil 0,9 dtk); audit/sesi
   (pre-warm 19:09 bersih, sesi hidup sampai 17 Nov); jaringan (poll berhasil).

## 6. Kerugian ikutan blackout (di luar Piagent — FAKTA)

Semua run di bawah ini tercatat "Skipped ... safety throttling" (sumber:
`scheduler.job_runs`). Dampaknya diam sesuai bodi masing-masing job, tapi
tercatat di sini sebagai kerugian nyata jendela yang sama:

- **free-mint-search** 19:01 / 19:31 / 20:01 / 20:31 WIB: 4 run hilang.
  Snapshot Free Bacot membeku di 18:31 WIB sampai run 21:01 WIB menulis lagi
  (last_run_wib ~21:01 WIB, run-0631). Artinya tidak ada pencarian rutin
  selama ~2,5 jam — kandidat free mint yang muncul di jendela itu tidak
  terdeteksi oleh kaki pencarian utama.
- **free-mint-hot-leg**: 25 run hilang (18:49–20:49 WIB). Pembacaan kuota
  watchlist (Matrix, AGCLUB, GUARD, dll.) berhenti; GUARD melewati deadline
  umur 24 jam (~19:19–19:23 WIB) tanpa pembacaan.
- **tracked-wallet-mint-scan-hourly** run 19:05 WIB: hilang. Ini ikut
  memperbesar gap yang akhirnya di-skip run 191 (46.121 blok, ~15:11–21:00 WIB).
- **project-recap-2h** 20:19 WIB: hilang — tidak ada rekap 2-jam yang
  seharusnya terbit ~20:19 WIB.
- **square-daily-draft** 19:37 WIB: hilang — draf Binance Square harian
  15 Nov tidak dibuat (agenda 19:37 WIB di rekap 18:19).
- **paper-trading-solana-15m / paper-trading-m3-solana-15m**: 9 + 8 run hilang.
  Posisi M3 round 2 (entry 18:09 WIB) tidak termonitor selama blackout —
  exit ladder tidak dievaluasi ~2 jam. (Tidak ada klaim kerugian di sini:
  posisi masih terbuka sesudahnya; hanya monitoring yang bolong.)
- **agent-registry-watch**: 9 run hilang (18:52–20:37 WIB). Mint Agent ID
  baru di jendela itu tidak terpantau; watermark tertahan.
- **termix-hosting-loop**: 2 run hilang — agen masgayut.agent tidak
  dimonitor ~2 jam (tidak ada order masuk yang tercatat sesudahnya; tidak
  ada klaim order hilang, hanya monitoring bolong).
- **agc-chart-watch, agio-free-mint-watch, hive-launch-watch, grove-watch,
  bobbie-listing-watch, gate-blocked-recheck, flap-sh-safety-watch,
  pending-coin-swap-watch, asset-sell-watch, free-mint-backfill,
  scan-gap-watch, heartbeat**: semua run di jendela hilang (2–7 run/job).
- **Tidak terdampak:** klaim AGC Mode B #42 (21:21 WIB) — sesudah blackout
  berakhir 20:54 WIB.

## 7. Evaluasi desain arming saat ini + opsi pengerasan

**Desain saat ini:** satu runonce cron = single point of failure tanpa
self-check. Rantai: cron (18:50) → tulis `armed-sale.json` → watchdog
(2-menitan) → loop. Kelemahan struktural:
- (a) Start loop bergantung pada SATU eksekusi cron yang terjadwal —
  runonce yang di-skip = hilang permanen (job disabled, tanpa catch-up).
- (b) Watchdog buta sebelum pointer ada — tidak ada yang mengawasi
  kegagalan arming itu sendiri.
- (c) `cron.status`/`last_success_at` tidak membedakan skip vs sukses.
- (d) Blackout 15 Nov (2 jam 9 menit) LEBIH PANJANG dari jendela sale
  (10 menit) — segala bentuk start yang bergantung pada eksekusi cron
  DI DALAM jendela sale akan gagal bila blackout menutupinya. Satu-satunya
  arming yang selamat adalah yang selesai SEBELUM blackout mulai.
- (e) Fakta penyeimbang: throttle hanya memblokir dispatch cron — exec
  langsung oleh agen yang sedang aktif TIDAK terblokir (terbukti: start
  manual loop 19:09:29 WIB berhasil di tengah blackout). Dan loop yang
  sudah berjalan (proses nohup) tidak peduli scheduler sama sekali.

### Opsi A — Arm loop langsung saat keputusan dibuat + mode --wait-until [REKOMENDASI UTAMA]

- **Apa yang berubah:** (1) Saat sale terverifikasi + diputuskan di-arm,
  parent LANGSUNG menulis `armed-sale.json` DAN men-start `fcfs_fast.py`
  saat itu juga via exec (bukan via cron). (2) `fcfs_fast.py` mendapat mode
  tunggu: flag `--wait-until <waktu buka>` — sebelum waktu buka, loop hanya
  polling nilai trigger (cheap read, TANPA preview/execute); sesudah waktu
  buka, beralih ke mode live penuh. (3) Watchdog FCFS menjaga loop sejak
  armed (mungkin perlu penyesuaian kecil: bila `armed_at` di masa depan dan
  loop belum jalan, jangan anggap gagal).
- **Biaya/risiko:** loop berjalan berjam-jam sebelum buka (poll 12 detik
  ≈ 300 poll/jam; tiap poll satu batch JSON-RPC — murah, tapi menambah
  beban egress; bila egress flapping, poll gagal sesekali — loop sudah
  menangani retry). Perlu perubahan kode `fcfs_fast.py` (mode tunggu) +
  perubahan prosedur arming. Risiko baru: loop yang sudah jalan berjam-jam
  bisa mati karena pergantian VM — tapi watchdog (bila tidak ter-throttle)
  me-restart-nya, dan jendela pemulihan berjam-jam, bukan 10 menit.
  Mode tunggu butuh selftest sebelum dipakai live.
- **Mode kegagalan tersisa:** (a) blackout throttle + pergantian VM yang
  bertepatan di menit-menit akhir sebelum buka sehingga watchdog tidak bisa
  me-restart loop yang mati — probabilitas jauh lebih kecil daripada
  single-point runonce; (b) bug pada mode tunggu itu sendiri; (c) parent
  tidak ada di turn saat keputusan dibuat sehingga arming tertunda.
- **Mengapa memperbaiki insiden 15 Nov:** loop sudah hidup sejak ~16:20 WIB
  (saat verifikasi selesai), jadi blackout 18:45–20:54 tidak relevan — loop
  adalah proses nohup biasa yang tidak peduli scheduler. Poll pertama
  sesudah 19:00 akan langsung mengeksekusi.

### Opsi B — Tulis pointer saat keputusan dibuat; watchdog yang men-start loop saat waktunya tiba (ganti runonce dengan guard persisten)

- **Apa yang berubah:** (1) `armed-sale.json` ditulis segera sesudah sale
  diputuskan (bukan di menit arming). (2) Bodi watchdog FCFS diperluas: bila
  pointer ada, `armed_at` sudah lewat, dan tidak ada proses loop + belum
  terminal → START loop (langkah 6 sudah melakukan ini bila state file ada;
  perluasan: berlaku juga bila state file belum ada dan `armed_at` sudah
  lewat). Runonce cron dihapus. (3) Verifikasi parent pasca-arming (opsi C)
  tetap berlaku.
- **Biaya/risiko:** rendah — tanpa perubahan `fcfs_fast.py`; hanya perubahan
  bodi watchdog + prosedur arming.
- **Mode kegagalan tersisa:** start loop TETAP bergantung pada eksekusi cron
  (watchdog 2-menitan). Bila blackout throttle mencakup momen arming —
  seperti 15 Nov (blackout 18:45–20:54 mencakup seluruh jendela sale
  19:00–19:10) — loop tetap tidak start. **Opsi ini TIDAK memperbaiki
  insiden 15 Nov bila blackout-nya selama itu.** Ia memperbaiki single-skip
  (satu run ter-skip → run 2 menit berikut men-start), bukan blackout
  berkepanjangan.
- **Penilaian:** berguna sebagai lapisan pertahanan, tapi TIDAK cukup
  sendirian. Nilai sebenarnya adalah "tulis pointer lebih awal" — bagian
  yang juga dipakai opsi A.

### Opsi C — Verifikasi parent-side pasca-arming + fallback exec (prosedural, tanpa kode baru)

- **Apa yang berubah:** prosedur tetap: setiap kali arming dijadwalkan/
  dilakukan, parent WAJIB memverifikasi dalam ~1 menit bahwa proses loop
  hidup (pgrep) + state segar (last_poll_at < 120 dtk). Bila tidak hidup →
  parent men-start loop langsung via exec (nohup --live) saat itu juga.
  Exec TIDAK terpengaruh throttle cron (terbukti 19:09 WIB).
- **Biaya/risiko:** nol biaya kode; bergantung pada parent yang sedang
  aktif di turn arming. Pada 15 Nov, pengecekan latar baru terjadi 19:08
  (18 menit sesudah arming, 8 menit sesudah sale buka; kuota sudah habis).
  Jadi opsi ini hanya bekerja bila verifikasi dilakukan dalam 1–2 menit
  sesudah arming.
- **Mode kegagalan tersisa:** parent tidak aktif di menit arming; VM
  replacement membunuh loop manual (watchdog me-restart bila tidak
  ter-throttle).
- **Penilaian:** wajib sebagai pelengkap A/B (murah, sudah menjadi pelajaran
  yang dicatat user 15 Nov ~19:11 WIB), tapi bukan perbaikan struktural
  sendirian.

### Opsi D — Loop sebagai systemd service (dicatat, tidak direkomendasikan sebagai perbaikan utama)

- Service systemd (seperti `unsolvable-live`) membuat loop tidak bergantung
  pada run agen; tapi start service tetap butuh exec/systemd di saat arming,
  dan unit di /etc hilang tiap pergantian VM (watchdog mencipta ulang).
  Membantu ketahanan proses, bukan masalah skip arming. Tidak memperbaiki
  insiden ini.

### Rekomendasi

**A + C, dengan elemen B (tulis pointer saat keputusan dibuat) sebagai
bagian dari A.** Urutan kerja:
1. Implementasi `--wait-until` di `fcfs_fast.py` + selftest, dan ubah prosedur
   arming menjadi "arm langsung" — SEBELUM FCFS berikutnya di-arm.
2. Verifikasi 1-menit pasca-arming sebagai aturan prosedur tetap (parent
   cek pgrep + state; bila mati, start via exec saat itu juga).
3. Perluasan watchdog (start saat `armed_at` lewat + tidak ada proses) sebagai
   jaring pengaman untuk kematian loop pra-buka.
4. Aturan membaca status cron untuk job kritis-waktu: JANGAN PERNAH simpulkan
   "jalan" dari `cron.status`/`last_success_at` — yang menentukan adalah
   `cron.runs` (`started_at` ≠ null) + bukti kerja nyata (proses/state file).
   Run yang di-skip tercatat "succeeded" — perilaku runtime ini tidak bisa
   diubah dari sisi agen.

## 8. Kesimpulan

- **Akar penyebab:** runonce arming 18:50 WIB di-skip oleh throttle
  scheduler runtime, dalam blackout **runtime-wide 18:45:39–20:54:31 WIB
  (2 jam 9 menit)** yang men-skip 287 dari ~290 run terjadwal di 30 job
  (0 failed; hanya job sistem runtime yang tetap jalan). Status "succeeded"
  yang menipu + tidak adanya verifikasi pasca-arming membuat kegagalan
  tidak ketahuan sampai 19:08 WIB — sesudah kuota 1.000 kursi habis
  (<10 menit sesudah buka 19:00 WIB).
- **Bukan penyebab:** pergantian VM 20:14:58 WIB (terlalu telat; menjelaskan
  kematian daemon ingest + service unsolvable, bukan Piagent), kode
  fcfs_fast.py, audit, sesi baw, atau jaringan.
- **Preseden:** skip throttle sudah terjadi 496× sebelumnya (sejak 8 Nov),
  tapi blackout kontinu selama ini belum pernah terjadi untuk
  fcfs-fast-watchdog (643 run dieksekusi tanpa putus sebelumnya, max gap
  120 detik).
- **Perbaikan yang diusulkan:** arm loop langsung saat keputusan dibuat
  (mode --wait-until) + verifikasi 1-menit pasca-arming + perluasan watchdog.
  Tanpa itu, FCFS berikutnya tetap bergantung pada satu eksekusi cron di
  dalam jendela sale — dan blackout berikutnya yang menutupi jendela itu
  akan mengulang kegagalan yang sama persis.
- **Batas investigasi:** "safety throttling" tidak terdokumentasi di
  `~/docs/scheduling-and-watching.md` maupun `~/docs/chat/scheduling-and-watching.md`;
  penyebab internal throttle (beban runtime? kebijakan?) tidak dapat
  ditentukan dari sisi agen. Tidak ada data yang menunjukkan throttle
  dipicu oleh beban kerja user sendiri vs kondisi runtime global.

---
*Investigasi selesai 15 Nov 2026 ~21:35 WIB. Semua perubahan file: hanya
laporan ini (read-only terhadap semua sistem lain).*
