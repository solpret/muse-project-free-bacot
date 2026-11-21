---
id: scan-gap-watch
title: Scan gap watch (backfill on-demand)
enabled: false
owner: goal:pencarian-rutin-project-free-mint
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-11-06T19:01:03
  every: 30m
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
SCAN GAP WATCH — BACKFILL ON-DEMAND (dibuat 2026-11-06 atas perintah user "lakukan saja yang menurutmu terbaik" — usulan perbaikan #2). READ-ONLY TOTAL. JANGAN mengaktifkan backfill sendiri.

AMENDEMEN 2026-11-07 ~23:33 WIB (user tap "Ya, perbarui tulisannya"): premis lama bahwa backfill DINONAKTIFKAN (2026-11-06 17:09 WIB) SUDAH TIDAK BERLAKU — user menyalakan lagi cron free-mint-backfill pada 2026-11-07 ~21:32 WIB dan backfill AKTIF sejak itu (terverifikasi parent 23:32 WIB: enabled=true, run terakhir sukses). Job ini TIDAK BOLEH lagi menyatakan backfill nonaktif dari ingatan/tulisan lama. Status backfill WAJIB diverifikasi segar tiap run lewat cron.status free-mint-backfill (enabled + last run + next run), dan laporan memakai status hasil verifikasi itu. Bila status tidak bisa diverifikasi, tulis "status backfill tidak terverifikasi run ini", jangan tebak.

TIAP RUN (30 menit): baca ~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-scan-state.json (watermark last_scanned_block; saat dibuat: 131989172 = head, gap 0) + head blok BSC saat ini via RPC read-only (eth_blockNumber). gap = head - watermark.
- Bila gap <= 4000: DIAM (dan bila flag laporan aktif padahal gap sudah < 4000, hapus flag itu).
- Bila gap > 4000 dan belum pernah dilaporkan untuk watermark ini (cek state file ~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/scan-gap-watch-state.json): LAPORKAN SEKALI ke chat utama: besar gap, watermark, head, dan status backfill hasil verifikasi segar (aktif + run terakhir, atau nonaktif — hanya bila benar-benar nonaktif, tambahkan bahwa gap perlu diaktifkan manual). Catat watermark + waktu laporan di state file. JANGAN mengaktifkan backfill sendiri.
- Bila gap > 4000 tapi sudah dilaporkan untuk watermark ini: DIAM.
- Bila baca gagal: catat di log harian ~/memory/YYYY-MM-DD.md + diam.

Observasi run masuk ke log harian. Jangan menulis snapshot/seen/state job lain.
