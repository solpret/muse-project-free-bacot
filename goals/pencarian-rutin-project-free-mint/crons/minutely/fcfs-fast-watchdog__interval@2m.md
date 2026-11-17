---
id: fcfs-fast-watchdog
title: Watchdog FCFS cepat (nyalakan ulang poller bila mati)
enabled: true
owner: goal:pencarian-rutin-project-free-mint
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-11-14T21:18:54
  every: 2m
timeout_secs: 300
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
WATCHDOG FCFS CEPAT — dibuat 2026-11-14 ~21:16 WIB atas perintah user ("Ya, pasang watchdog FCFS"). Tugas: jaga loop poller fcfs_fast.py tetap hidup saat ada sale yang di-arm live; bila loop mati atau macet, nyalakan lagi. Watchdog ini TIDAK PERNAH meng-arm sale sendiri, TIDAK PERNAH menulis file pointer arm, TIDAK PERNAH mengubah config, TIDAK PERNAH mengeksekusi mint.

AMENDEMEN 2026-11-15 (A+C, perintah user "Ya, terapkan A+C sekarang"): pointer armed-sale.json boleh membawa field opsional `wait_until` (ISO 8601 waktu buka sale); restart memakai flag arming yang sama (termasuk --wait-until bila ada di pointer). Loop yang sedang MENUNGGU (state.waiting=true) dengan last_poll_at segar adalah SEHAT.

ALAT: ~/workspace/fast_exec/fcfs_fast.py (poller 12 dtk + pre-warm, config-driven). Dokumen: ~/workspace/fast_exec/FCFS_FAST.md. State loop: ~/workspace/fast_exec/fcfs_fast_state_<sale_name>.json (field last_poll_at, terminal=null sampai terminal, live, waiting, wait_until). State watchdog: ~/workspace/fast_exec/fcfs-watchdog-state.json (catat last_restart_at + last_report_at).

TIAP RUN (2 menit), urutan cek:
1. Baca file pointer ~/workspace/fast_exec/armed-sale.json. Bila file TIDAK ADA / kosong / tidak berisi config path → TIDAK ADA sale yang di-arm → DIAM, jangan lakukan apa pun, jangan kirim pesan. (Saat ini belum ada sale yang di-arm — watchdog diam sampai langkah arming sale berikutnya menulis pointer ini.) Pointer boleh juga membawa `wait_until` — waktu buka sale (ISO 8601) — untuk restart; lihat langkah 6.
2. Bila pointer ada: baca config di path absolut yang ditunjuk pointer. WAJIB: config ada, dry_run=false, website_gate_verified=true. Bila salah satu tidak terpenuhi → JANGAN restart; catat satu baris ke log watchdog ~/workspace/fast_exec/fcfs-watchdog.log dan DIAM (chat tidak perlu tahu — loop memang tidak boleh jalan live tanpa itu; alat sendiri juga menolak --live bila dry_run=true).
3. Baca state loop fcfs_fast_state_<sale_name>.json. Bila field terminal terisi (sukses / kuota habis / sale failed / slot terpakai / diblokir audit / preview kotor) → sale SELESAI → DIAM.
4. Cek proses hidup: pgrep -f "fcfs_fast.py.*--config <config>". Bila proses ADA dan last_poll_at segar (<120 detik) → loop SEHAT → DIAM. Loop yang sedang MENUNGGU (state `waiting=true`) dengan last_poll_at segar adalah SEHAT — jangan restart.
5. Bila proses ADA tapi last_poll_at basi >120 detik → loop MACET (wedged di luar eksekusi; eksekusi selalu didahului poll segar) → kill PID itu, lalu lanjut ke langkah 6.
6. Bila proses TIDAK ADA: bila state file belum ada DAN armed_at di pointer <120 detik lalu → loop baru di-arm, beri waktu → DIAM. Selain itu (tidak ada proses + last_poll_at basi >60 detik, atau tidak ada state sama sekali setelah 120 detik) → RESTART: nohup python3 ~/workspace/fast_exec/fcfs_fast.py --config <config> --live [--wait-until <wait_until dari pointer bila ada>] > ~/workspace/fast_exec/fcfs_fast_<sale_name>.nohup.log 2>&1 & — lalu tunggu 5 detik dan verifikasi proses hidup via pgrep. Bila wait_until sudah lewat, alat otomatis live langsung — aman. Bila tidak ada proses + tidak ada state file sama sekali dan armed_at sudah lewat >120 detik → ini arming yang tidak pernah start (atau loop mati sebelum sempat menulis state) → RESTART juga, bukan diam.
7. Sesudah restart BERHASIL: catat ke fcfs-watchdog-state.json (last_restart_at + hitung restart). Laporkan ke chat utama HANYA bila last_report_at >30 menit lalu (atau belum pernah lapor): "Loop FCFS <sale_name> mati/macet dan sudah dinyalakan lagi (jam matinya dari last_poll_at terakhir)". Bila restart GAGAL (proses tidak hidup sesudah 5 detik) → laporkan SEKALI ke chat utama + catat ke log watchdog. Bila restart berhasil tapi laporannya sudah dikirim <30 menit lalu → restart saja, DIAM (jangan spam chat bila loop terus mati).

LARANGAN: jangan pernah restart dalam mode dry-run; jangan pernah spawn loop kedua selagi satu masih hidup dan sehat; jangan pernah menulis armed-sale.json atau mengubah config sale; jangan pernah menyentuh MEMORY.md (observasi ke fcfs-watchdog.log saja).
