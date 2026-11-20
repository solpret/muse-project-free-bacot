# free-mint-hot-leg run 2026-11-17 20:09 WIB (18.7 dtk, block 134125187)

- Leg 1 Sourcify feed: 20 kontrak, 3 baru (0x33366F55..., 0x3d8b7808..., 0x96e48E7E...). Shape-check S1/S2: ketiganya false (tidak ada free view / quote; 0x3d8b7808 punya agent_ref tapi tanpa free view) — dicatat di hot-leg-seen.json, bukan lead.
- Leg 2 Boltbook EN (44.628 B, HTTP 200) + ZH (43.269 B, HTTP 200): 0 alamat baru. Figur: BUBB first mint free 1.986/2.222, PXIO Miners 13.907/16.666, ORBITJANITOR 1.067/4.444, MINE 961/8.888 — semua sudah dikenal, bukan lead baru.
- Leg 3: 0 shape hit. 0 kandidat / 0 eksekusi / 0 preview.
- Leg 4 re-read (read-only, batch RPC): 0 chunk error. Diff vs 1839 (file reread 1939 tidak ada — run 19:39 hanya menghasilkan runlog, tanpa reread json): kenaikan kecil biasa — AgentBubble freeMinted 1836→1841, Matrix 584→585, PunchCard freeMinted 1167→1216 (21,9% dari MAX_SUPPLY), RigForge freeSharesLeft 632→627, RAVE/MORFO/CPASS/Kryntar/SPARKS/BoldLeonidas/AgentNOVA +1–5. bsccat dan pepe tanpa perubahan. Tidak ada sellout, slot hilang, atau pending-claim terbuka.
- Threshold check: PunchCard 21,9%, AGCLUB 58,8%, Matrix 58,5%, PIXELFROGS 15,1% — tidak ada yang >70% → tidak ada promosi strong lead.
- Bridge: 116 kontrak, 0 di luar snapshot, 7 same_owner_discarded — tidak ada temuan pelengkap.
- CAT402: sudah sellout, dilaporkan run 19:44 (free 73→100/100, pool 0). Gate-blocked strong lead habis tanpa mint. Tidak dilaporkan ulang.
- Poffzi FCFS: tidak ada proses (informasional; sale sudah selesai 16 Nov).
- Main snapshot, scan seen file, track-c-scan-checked file TIDAK disentuh (read-only).
