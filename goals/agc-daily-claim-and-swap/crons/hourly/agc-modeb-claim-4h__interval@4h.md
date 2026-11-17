---
id: agc-modeb-claim-4h
title: 'AGC Mode B: klaim tiap 4 jam'
enabled: true
owner: goal:agc-daily-claim-and-swap
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-11-03T21:21:40
  every: 4h
timeout_secs: 1800
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
KLAIM MODE B AGC TIAP 4 JAM — KLAIM SAJA, TANPA SWAP. Atas perintah user 2026-11-03 (pesan "Claim mode B koin AGC setiap 4 jam di poolnya", menegaskan pilihan klaim-saja dari pertanyaan sebelumnya). Job ini HANYA mengklaim reward vested Mode B yang sudah terakumulasi di pool; ia TIDAK men-swap, TIDAK mint, dan TIDAK mengubah job harian agc-auto-claim-daily (09:37 WIB) — AGC hasil klaim menumpuk di wallet sampai user perintahkan lain.

Kontrak: AGCMinter 0x6288DFe86f22B53eEB6886aE2D78941de7483743, token AGC 0x63dea5aCdbE1F27c968907D08610A5f0A0284bA6, BSC chain 56. Wallet: 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E (wallet utama saja). baw: /home/hatch/workspace/.baw-cli/bin/baw (path absolut; preview kedaluwarsa ~5 menit, jadi preview + eksekusi harus berurutan rapat). Calldata SELALU dibangun dengan eth_abi (venv ~/workspace/.abi-venv/bin/python), jangan hand-type selector/calldata. State file job ini: ~/workspace/goals/agc-daily-claim-and-swap/hidden_files/agc-claim-4h-state.json (hanya penanda sesi-kedaluwarsa-dilaporkan).

TIAP RUN, urut:
1. Cek sesi baw (status + devMode enabled). Bila sesi kedaluwarsa -> laporkan SEKALI ke chat utama bahwa sesi kedaluwarsa dan job ini berhenti sementara, catat penanda di state file, lalu berhenti. Selama penanda aktif dan sesi masih mati, run berikutnya DIAM (tidak melapor lagi). Bila sesi hidup kembali, hapus penanda. JANGAN pernah mencoba login ulang dari cron (renewal butuh QR tap user).
2. Baca segar pending(wallet) dari minter. Bila rewardVested < 10.000 AGC -> DIAM, tidak ada klaim, tidak ada laporan (guard yang sama dengan job harian; vesting berjalan ~5.100 AGC/jam sehingga jeda 4 jam normal menghasilkan ~20.400 AGC). Bila rewardVested >= 10.000 AGC, lanjut.
3. Catat saldo AGC wallet SEBELUM klaim.
4. Audit Binance untuk kontrak minter dan token AGC (POST https://web3.binance.com/bapi/defi/v1/public/wallet-direct/security/token/audit, header source: agent, body {binanceChainId: "56", contractAddress, requestId: uuid baru}). Ungkapkan hasilnya di laporan: hasResult=false berarti TIDAK ADA HASIL, bukan pass. Hit risiko spesifik (isHit dengan riskType RISK, atau riskAlert non-null) pada kontrak mana pun -> BERHENTI run ini, laporkan sekali dengan alasannya, jangan eksekusi, jangan retry, jangan cari jalur lain.
5. Klaim via claimReward([]) (array kosong = dari cursor). Preview baw bersih WAJIB (simulationCode 000000000, simulationErrorDetail null, value 0, authorityChanges kosong, allowanceChanges kosong, risks kosong; satu-satunya perubahan yang diharapkan = saldo AGC bertambah). Preview kotor, 351803, atau 351805 -> BERHENTI, laporkan sekali dengan alasannya, jangan retry. Eksekusi hanya dari preview bersih itu; verifikasi receipt status 1 + delta saldo AGC sama dengan rewardVested yang dibaca di langkah 2 (dalam toleransi pembulatan vesting antar blok).
6. LAPORAN SEKALI ke chat utama untuk tiap klaim yang berhasil: tx hash + jumlah AGC diklaim + verifikasi on-chain. Bila tidak ada klaim (guard langkah 2), DIAM.

LARANGAN: TIDAK ADA MINT apa pun. Jangan klaim refund Mode A (claimFree) — itu pekerjaan job harian dan job percepatan. Jangan tarik LP Mode B (withdrawLP) — LP baru jatuh tempo 2026-11-17 ~09:11 WIB dan itu pekerjaan job harian. Jangan swap AGC ke BNB di job ini. Jangan sentuh saldo AGC dari sumber lain, jangan kirim ke wallet lain. Jangan edit MEMORY.md. Tumpang-tindih dengan job harian TIDAK masalah: claimReward([]) hanya mengklaim vested yang ada saat itu, jadi tidak ada klaim ganda.
