---
id: btc-agent-watch
title: Pantau + auto-mint free mint BTC Agent (btc-agent.fun)
enabled: false
owner: goal:pencarian-rutin-project-free-mint
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-11-14T20:18:46
  every: 2m
timeout_secs: 600
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
PANTAU + AUTO-MINT FREE MINT BTC AGENT (btc-agent.fun) — dibuat 14 Nov 2026 ~20:16 WIB atas perintah user (tap "Ya, pantau + mint otomatis saat buka" 14 Nov ~20:13 WIB). Otorisasi: pantau sampai sale buka, lalu mint gratis SEKALI untuk wallet agent bila semua guard lolos. Ini proyek yang user sebut sendiri — aturan umur routine-search (<24 jam) TIDAK berlaku di sini.

FAKTA TERVERIFIKASI (14 Nov 2026 ~20:10–20:16 WIB; jangan pakai angka lain, baca segar tiap run):
- Situs btc-agent.fun/#mint mencetak kontrak persis (GATE WEBSITE LOLOS): Mint 0x133D81871f5C9881d4aE09b0492d6f061a54361a, Token 0x28ee3dbf9f9d2d20bc0f98061f675a207b196621, Registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, USDT 0x55d398326f99059fF775485246999027B3197955.
- Aturan sale: 2.100份 total, 210份 pertama GRATIS (mintFree() no-arg, tanpa bayar, calldata 0x8ab53447), lalu 2,1 USDT/份，1份 per Agent ID, 5.000 token/份. Hanya wallet Binance pemegang Agent ID.
- State awal (blok 133550123, 20:16 WIB): started()=false (BELUM BUKA), launched()=false, failed()=false, freeMinted()=0/210, paidMinted()=0, freeDone(agent)=false, registry balanceOf(agent)=1, token totalSupply 21.000.000, decimals 18. Saldo BNB wallet agent 0,0001464 (TURUN dari ~0,00062 pagi hari — cukup untuk beberapa mint gas-only ~0,000015/mint, tapi tipis; cek segar tiap run).
- Audit Binance 14 Nov ~20:12 WIB: kontrak MINT hasResult=false (TIDAK ADA HASIL — laporkan sebagai tidak ada hasil, bukan lolos); kontrak TOKEN riskLevel 2 LOW, satu-satunya temuan CAUTION kode belum terverifikasi, TIDAK ADA RISK hit, riskAlert null.
- Wallet eksekusi: agent/baw wallet 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E (baw terkunci ke wallet ini). Skrip watch: ~/workspace/btc-agent-watch/watch.py. State: ~/workspace/btc-agent-watch/state.json.

TIAP RUN (interval 2 menit — kuota gratis cuma 210份 FCFS, jadi interval pendek):
1. Jalankan `python3 ~/workspace/btc-agent-watch/watch.py` — SATU JSON-RPC batch (eth_blockNumber + started/launched/failed/freeMinted/paidMinted/freeDone + saldo BNB). JANGAN pakai fast_rpc.py (flaky: semua endpoint OSError lewat proxy); skrip memakai urllib polos + fallback endpoint (bsc-dataseed.binance.org utama). Bila skrip keluar bukan 0 (semua endpoint gagal) → catat di log harian, DIAM, JANGAN PERNAH eksekusi dari data basi/gagal. Baca state.json segar.
2. Terminal tanpa eksekusi (laporkan SEKALI ke chat utama + NONAKTIFKAN cron ini sendiri via cron.update id btc-agent-watch, enabled false):
   - failed()=true → sale gagal/refund phase; jangan mint.
   - freeDone(agent)=true → sudah termint (mis. user mint manual di tempat lain); jangan mint ulang.
   - freeMinted()>=210 → fase gratis habis tanpa slot user.
3. Bila started()=false → DIAM (state sudah diperbarui skrip). Tidak ada laporan.
4. Bila started()=true DAN freeMinted()<210 DAN freeDone(agent)=false → JALUR EKSEKUSI (di run yang sama, secepatnya):
   a. Audit Binance SEGAR (curl, skill query-token-audit: POST https://web3.binance.com/bapi/defi/v1/public/wallet-direct/security/token/audit, binanceChainId 56) untuk kontrak MINT dan kontrak TOKEN. BERHENTI (tanpa eksekusi, laporkan sekali + nonaktifkan cron) bila: ada risk item isHit=true dengan riskType RISK, atau riskAlert non-null. hasResult=false pada kontrak MINT = tidak ada hasil — diungkapkan, TIDAK menghentikan (perluasan pre-auth user 2026-11-03).
   b. Jalankan watch.py SEKALI LAGI tepat sebelum preview — state harus tetap started=true, freeMinted<210, freeDone=false, failed=false. Bila berubah → batalkan jalur eksekusi run ini, kembali ke langkah 2/3.
   c. Cek baw: `baw wallet settings --json` → devMode.enabled harus true; sesi harus CONNECTED. Bila devMode mati/kedaluwarsa ATAU sesi tidak CONNECTED → laporkan SEKALI (minta user aktifkan Developer Mode di Binance App / sign-in ulang) + JANGAN nonaktifkan cron; catat reported_devmode di state.json agar tidak diulang tiap 2 menit. Bila saldo BNB < 0,00003 → laporkan SEKALI (gas tidak cukup) + JANGAN nonaktifkan cron; catat reported_low_gas di state.json; lewati preview selama saldo rendah.
   d. Catat saldo token agent SEBELUM eksekusi (satu eth_call balanceOf token — pakai pola curl batch seperti skrip watch.py).
   e. Preview: `baw contract-call preview --binanceChainId 56 --from 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E --to 0x133D81871f5C9881d4aE09b0492d6f061a54361a --value 0 --inputData 0x8ab53447 --json`. Preview BERSIH berarti SEMUA terpenuhi: success=true, simulationCode 000000000, simulationErrorDetail null, value 0, authorityChanges kosong, allowanceChanges kosong, TIDAK ADA risk item riskType RISK, dan perubahan saldo = +5.000 token (5.000 x 10^18). Bila preview 351803 (risk blocked) ATAU kotor karena risk/authority/allowance/value bukan 0 → laporkan sekali + nonaktifkan cron. Bila preview 351805 dengan pesan gas/saldo → laporkan sekali + JANGAN nonaktifkan cron (tunggu run berikut; catat di state.json).
   f. Execute: `baw contract-call execute --requestId <id dari preview> --json`. Satu broadcast saja; JANGAN PERNAH retry sesudah execute, apa pun hasilnya. Bila BROADCASTED → catat txHash. Bila PENDING_CONFIRMATION → laporkan sekali (user harus konfirmasi di Binance App) + nonaktifkan cron (eksekusi sudah di tangan user; jangan eksekusi ulang). Bila execute error → laporkan sekali + nonaktifkan cron, tanpa retry.
   g. Verifikasi: `python3 ~/workspace/btc-agent-watch/watch.py --receipt <txHash>` — ulangi beberapa kali sampai receipt muncul (maks ~60 detik). WAJIB: receipt_status=1, freeDone=true, saldo token agent naik TEPAT 5.000 token dari saldo pra-eksekusi. Bila receipt_status=1 tapi verifikasi lain gagal → laporkan apa adanya + nonaktifkan cron (jangan retry).
   h. Laporkan SEKALI ke chat utama: sale buka + mint sukses, tx hash, blok, gas used, verifikasi on-chain (receipt status 1, saldo token sebelum/sesudah, freeDone=true), audit segar (mint: tidak ada hasil / token: riskLevel + temuan). Catatan: mint ini menghasilkan token FUNGIBLE (5.000 BTC Agent), BUKAN NFT — standing post-mint marketplace check + rarity check berlaku untuk NFT saja (AGENTS.md), jadi TIDAK dijalankan di sini; nyatakan itu di laporan.
   i. NONAKTIFKAN cron ini sendiri (cron.update id btc-agent-watch, enabled false) sesudah laporan sukses.

CATATAN STATE & LOG: state ditulis skrip watch.py ke ~/workspace/btc-agent-watch/state.json (jangan tulis snapshot job lain). Observasi singkat tiap perubahan material ke log harian ~/memory/YYYY-MM-DD.md. Jangan edit MEMORY.md.

LARANGAN MENGIKAT: TIDAK PERNAH approvals, paid mint (mintPaid), swap, transfer, atau signing lain. TIDAK PERNAH eksekusi saat started()=false, dari data basi/gagal, atau saat freeMinted()>=210. TIDAK PERNAH retry sesudah execute. TIDAK PERNAH pakai layanan berbayar baru. Bila sesi baw kedaluwarsa → laporkan sekali, JANGAN coba re-login sendiri (renewal butuh tap QR user).
