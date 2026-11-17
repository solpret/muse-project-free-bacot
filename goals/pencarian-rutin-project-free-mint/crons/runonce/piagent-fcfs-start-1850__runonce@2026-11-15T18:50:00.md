---
id: piagent-fcfs-start-1850
title: 'Piagent FCFS: nyalakan loop live 18:50 WIB'
enabled: true
owner: goal:pencarian-rutin-project-free-mint
mode: task
schedule:
  kind: runonce
  timezone: Asia/Jakarta
  at: 2026-11-15T18:50:00
timeout_secs: 600
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","provider":"main","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
NYALAKAN LOOP FCFS PIAGENT (live) — satu kali, 15 Nov 2026 ~18:50 WIB. Sale Piagent (piagent.vip) buka 19:00 WIB; config sudah terverifikasi (selftest 17/17 PASS + --once PASS 16:20 WIB: audit PiToken LOW 0 hit, sesi baw CONNECTED + devMode s.d. 17 Nov, trigger freeLeft=1 terdeteksi, BNB 0,000114).

1. Tulis file pointer ~/workspace/fast_exec/armed-sale.json berisi JSON: {"sale_name": "piagent", "config": "/home/hatch/workspace/fast_exec/piagent.json", "armed_at": "<waktu sekarang dalam ISO +07:00>"}.
2. Jalankan loop live dari direktori ~/workspace/fast_exec: nohup python3 /home/hatch/workspace/fast_exec/fcfs_fast.py --config /home/hatch/workspace/fast_exec/piagent.json --live > /home/hatch/workspace/fast_exec/fcfs_fast_piagent.nohup.log 2>&1 &
3. Tunggu ~10 detik, verifikasi: proses hidup (pgrep -f "fcfs_fast.py.*--config piagent.json") DAN state file ~/workspace/fast_exec/fcfs_fast_state_piagent.json ada dengan last_poll_at segar (<60 detik).
4. Bila loop hidup → laporkan SEKALI ke chat utama: loop FCFS piagent live jalan, mulai 18:50 WIB, sale buka 19:00 WIB. Preview pra-buka akan gagal 351805 NotStarted — itu NORMAL dan bukan terminal, jangan laporkan sebagai masalah.
5. Bila loop TIDAK hidup sesudah 2x percobaan → laporkan SEKALI ke chat utama bahwa loop gagal dinyalakan + 20 baris terakhir log. JANGAN mengubah config, JANGAN menulis ulang armed-sale.json dengan isi lain, JANGAN mengeksekusi mint manual.
Larangan: jangan pernah menjalankan loop kedua bila satu sudah hidup; jangan menyentuh MEMORY.md. Watchdog fcfs-fast-watchdog (tiap 2 menit) akan menjaga loop tetap hidup sesudah ini; tugas ini hanya menyalakannya sekali.
