# LEG 1 — Scan route 4 + track-C 5c — run 2026-11-08 05:01 WIB

## Preflight — PASS
- Head via fast_rpc batch bsc-dataseed1: 132280470; ankr_getLogs 50 blok: 134 log, 13,2 dtk (<60 dtk). Ankr lewat proxy env yang sudah ada; no_proxy tidak disentuh.

## Scan (onchain_nft_scan.py --blocks 1000 --chunk 50)
- Window: 132279543–132280542 (1000 blok, cap; head saat scan 132280542).
- 20/20 chunk selesai, progres per chunk tercatat di run-2026-11-08-0501-scan-progress.log.
- 40 Ankr calls, 0 error, partial=False. Durasi total ~16 mnt 56 dtk (SCAN_EXIT=0).
- Hasil: 86 kontrak NFT (83 ERC721 + 3 ERC1155), 356 mint NFT, 215 kontrak ERC-20 mint.
- HIVE Agents TIDAK ada di window.
- REWARD (RWD) 0xcfe5e4925a76a3aa11afa79e04c6fad3611cee40 hadir (2 mint, 2 minter) — SUDAH-DITANGANI hot-leg 0319 (strong lead gate-blocked, sudah dilaporkan sekali); tidak dilaporkan ulang, tidak di-preview/mint.
- Registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F hadir 1x — infrastruktur, excluded.
- Top mint di window (semua sudah dikenal, bukan first-seen): NeoTrade Soulbound 67 mint (registry=False, not_verified), HokiCat 45, Voltoad 32.

## Watermark — TIDAK dimajukan kaki ini
- last_scanned_block saat kaki ini mulai: 132275169. Skipped gap kaki ini: 132275170–132279542 (4.373 blok, di luar cap 1000).
- Selama scan berjalan, backfill-parallel memajukan watermark sendiri ke 132280358 (window 132275170–132280358, mtime 22:38 UTC) — gap yang saya lewati sudah ditutup backfill. Script scan tidak menulis state file (terverifikasi via grep: tidak ada referensi scan-state di onchain_nft_scan.py).
- Output scan: onchain-scan-2026-11-08-0501.json.

## Triase first-seen — 0
- first-seen sejati: 0 (semua 86 kontrak sudah ada di onchain-scan-seen.json / onchain-snapshot.json / excluded).
- 0 EARLY lead, 0 strong lead, 0 kandidat dari kaki ini. Tidak ada yang di-append ke onchain-scan-seen.json (tidak ada first-seen baru).
- Detail: run-2026-11-08-0501-triage-scan.json / .log.

## Track-C 5c — 0 hit
- ERC-20 window mint_count >= 10: 35; sudah dicek sebelumnya 32; baru dicek 3; dropped sampling-limit 0.
- 3 baru dicek (semua no-shape, S1=S2=False), sudah di-merge ke track-c-scan-checked.json (total kini 2.942 alamat):
  - 0xdE495519BfFB9C2D3984B19E5F3E648F0e6AD453 — 87 mint, not_verified, registry_bytes=False
  - 0x28383e2aC898d40CEde10BF87688ed061FfD4E52 — 23 mint, not_verified, registry_bytes=True
  - 0x722294F6c97102fB0DDb5b907c8d16BDEAB3f6D9 — 10 mint, verified, tanpa mint/quote/free/gate fns
- 0 sale-shape hit (S1/S2). Detail: run-2026-11-08-0501-5c.json / .log.

## Batasan / catatan
- Sourcify sering error:IncompleteRead / error:RemoteDisconnected pada enrichment (artefak fetch, bukan vonis kontrak) — triase memakai registry_bytes_hit + free_shaped + mint_funcs seperti template 0431.
- READ-ONLY terhadap snapshot/bridge; tidak ada mint/preview/claim; tidak ada laporan chat yang dikirim kaki ini.
- File run kaki ini: run-2026-11-08-0501-{preflight,triage-scan,5c}.{py,json,log}, run-2026-11-08-0501-scan-progress.log, onchain-scan-2026-11-08-0501.json — semua di ~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/.
