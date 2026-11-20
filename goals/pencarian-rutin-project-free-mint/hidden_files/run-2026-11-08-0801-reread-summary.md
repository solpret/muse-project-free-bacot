# ROUTE 1 — Run 2026-11-08 08:01 WIB — re-read + velocity + age sweep

- **Block read:** 132302277 (baseline run 0731: 132298298; interval 3.979 blok ≈ 29,84 mnt @ 0,45 dtk/blok)
- **Re-read:** 460 kontrak + 70 track_c, selesai 741,5 dtk, tanpa gagal total (log: run-2026-11-08-0801-reread.log)
- **File:** run-2026-11-08-0801-reread.json

## Velocity

- **Pass: 1 — Lambdwyn** (0xCa7A3faa22AC4ABBf5528B41AC7d12B28651AA6B): 494 → 519 (+25 token, 0,8377/mnt, rasio 1,57x vs 0,5333/mnt run 0731). **BUKAN promosi**: free% UNVERIFIED (tidak ada free counter / FREE_SUPPLY di snapshot maupun bacaan segar), umur launch UNVERIFIED, status watchlist-only-scan-2026-11-03. Tetap watchlist.
- **Tidak ada item baru melewati 25% (strong-lead) atau 50% (kandidat)** free% terverifikasi vs run 0731.
- **Near-miss (perhatian parent, bukan pass):** BOT-UNIT +104 token tapi rasio 1,47x (di bawah 1,5x); Butterfli-c698 freePct 53,96% terverifikasi tapi hanya +14 token (<20); AgentVOLT (round 1) rasio 1,99x tapi +18 token (<20); Jinli Agents +31 token, freePct 14,86%, tanpa rate sebelumnya (rasio None).
- **Dafeiyu (early lead baru run 0731):** baseline PERTAMA tercatat — totalSupply 388 (was 178 saat verifikasi ~07:46 WIB, +210 sejak itu, tapi tanpa baseline run 0731 jadi belum ada rate/rasio). free% tetap UNVERIFIED (freeClaimed() revert; FREE_SUPPLY 666 tanpa free counter). Slot: balanceOf(user)=0; freeClaimed(user) None (artefak batch, bukan perubahan — snapshot tetap "slot open by read").
- **HokiKoi (early lead baru run 0731):** TIDAK TERBACA run ini (seluruh batch gagal, _batch_v2=false; totalSupply/totalMinted/freeMinted semua None = artefak baca, BUKAN perubahan). Nilai snapshot dipertahankan: totalMinted 21, freeMinted 21/111 = 18,92%, slot open (freeCount(user)=0). Baseline velocity BELUM tercatat — butuh bacaan sukses di run berikutnya.

## Sellout / slot

- **Sellout baru: 0.** Total sold out tetap 35, sama persis dengan run 0731 (tidak ada yang baru, tidak ada yang lepas).
- **Perubahan slot user: 0** (balanceOf_user / freeClaimed(user) tidak ada yang berubah di mana pun).
- **track_c:** 0 perubahan nilai (freeSharesRemaining / freeMinted / balance / freeClaimed user) vs run 0731; tidak ada free pool yang baru 0.

## Age sweep

- **REMOVE: 0.** Tidak ada item terverifikasi >48 jam yang belum sold out.
- Kept (sudah sold out / minted-by-user / same-owner-discarded): 56. Launch age UNVERIFIED: 399 kontrak (tetap di watchlist, tidak pernah dibuang diam-diam).
- GHOSTLING + VOLTOAD sudah dihapus dari snapshot di run 0731 (age-excluded) — tidak muncul lagi di sweep ini.

## Tidak terbaca (nilai snapshot dipertahankan, bukan perubahan)

- totalSupply+totalMinted None: 109 kontrak (was 108 di run 0731; satu-satunya yang baru tidak terbaca = HokiKoi, batch gagal total).
- track_c totalSupply None: 32 dari 70.
- Free views (freeClaimed/freeMinted/FREE_SUPPLY/MAX_SUPPLY/mintOpen) sering None di batch — artefak degradasi batch-revert yang sudah dikenal, BUKAN nol dan BUKAN perubahan.

## Perhatian parent

- **Sesi baw LOGOUT lebih awal (~08:15–08:19 WIB, 5× NOT_LOGGED_IN 10003000; cek sukses terakhir 08:14:54 WIB)** — tercatat di MEMORY.md selama run ini. Bila ada kandidat/lead yang perlu dieksekusi, baw butuh QR re-sign-in dulu; run ini sendiri read-only jadi tidak terdampak.
- Lambdwyn velocity pass tanpa free% terverifikasi → tidak ada promosi; bila free counter-nya bisa dibaca di run berikut dan ≥25%, baru jadi strong lead.
- HokiKoi butuh satu bacaan sukses untuk baseline velocity (run ini gagal total).

## File yang ditulis (hidden_files/)

- run-2026-11-08-0801-reread.py / .log / .json
- run-2026-11-08-0801-velocity.py / .log / .json
- run-2026-11-08-0801-age-sweep.py / .log / .json
- run-2026-11-08-0801-reread-summary.md (file ini)

Snapshot / scan-state / scan-seen TIDAK disentuh (read-only, sesuai tugas).
