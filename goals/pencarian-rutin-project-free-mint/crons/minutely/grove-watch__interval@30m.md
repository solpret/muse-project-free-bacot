---
id: grove-watch
title: Agent Grove phase-2 watch
enabled: false
owner: goal:pencarian-rutin-project-free-mint
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-11-06T19:01:01
  every: 30m
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
PANTAUAN AGENT GROVE FASE 2 (dibuat 2026-11-06 atas perintah user "lakukan saja yang menurutmu terbaik" — usulan perbaikan #1). READ-ONLY TOTAL: hanya eth_call, TIDAK PERNAH preview/mint/approve/swap/sign/tx.

Konteks: Agent Grove 0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c, situs agent-grove.pages.dev (terverifikasi mencetak kontrak persis). Free mint 2.500 pohon dalam 10 fase x 250, jeda 10 jam; maks 1 pohon gratis/wallet selamanya; butuh pegang Binance Agent ID (user: masgayut.ai). Fase 2 dijadwalkan buka 2026-11-06 13.05 WIB tapi per cek 16.46 WIB freeOpen() masih 0 — fase bisa telat berjam-jam dari jadwal situs; freeOpen() on-chain adalah otoritas, bukan jadwal situs. freeClaimed(user)=0 (slot user terbuka). freeMinted() Grove terbaca 2500 dua kali padahal situs bilang 250/2.500 — fungsi itu TIDAK andal, jangan dipakai.

TIAP RUN (30 menit): baca segar via BSC RPC read-only (pakai ~/workspace/fast_exec/fast_rpc.py atau modul Ankr; jangan ketik calldata dengan tangan): freeOpen() + freeClaimed(0xeb237F6f9FB4e826739F0954e9768914F28b2c2E). Catat hasil di state file ~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/grove-watch-state.json (last_check, freeOpen, slot) + observasi singkat di log harian ~/memory/YYYY-MM-DD.md.

- Bila freeOpen()==0: DIAM.
- Bila freeOpen()==1 dan freeClaimed(user)==false: LAPORKAN SEKALI ke chat utama bahwa fase 2 SUDAH BUKA on-chain + slot user masih terbuka, lalu NONAKTIFKAN cron ini sendiri (cron.update id grove-watch, enabled false). Laporan saja — MINT TIDAK diotorisasi job ini; eksekusi tetap wewenang job pencarian rutin 30-menit / parent di bawah gate website + audit + preview bersih.
- Bila freeOpen()==1 tapi freeClaimed(user)==true (slot sudah terpakai): laporkan sekali + nonaktifkan diri.
- Bila baca gagal (RPC error semua): catat di log harian + diam; jangan laporkan sebagai perubahan.

JANGAN menulis snapshot onchain-snapshot.json (milik job pencarian rutin) — hanya state file job ini.
