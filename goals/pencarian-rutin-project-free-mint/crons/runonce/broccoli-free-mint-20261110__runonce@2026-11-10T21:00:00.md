---
id: broccoli-free-mint-20261110
title: Mint gratis Broccoli (1 lot) saat launch 21:00 WIB
enabled: true
owner: goal:pencarian-rutin-project-free-mint
mode: task
schedule:
  kind: runonce
  timezone: Asia/Jakarta
  at: 2026-11-10T21:00:00
timeout_secs: 1800
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
Eksekusi mint gratis BROCCOLI (Broccoli Agent) — SATU KALI, saat launch 2026-11-10 21:00 WIB.

OTORISASI: user 2026-11-10 ~18:47 WIB mengetuk "Ya, lanjut mint gratis Broccoli jam 21:00" — ini override kasus-spesifik yang diinformasikan atas hit RISK audit Binance "Contract Not Renounced". Berlaku HANYA untuk satu panggilan mintFree() gratis ini (value 0, 1 lot = 30.000.000 BROCCOLI). BUKAN otorisasi untuk mint berbayar, switch, swap, approve, atau transaksi lain apa pun.

Kontrak token+mint (Sourcify terverifikasi): 0xc438821D5937E5246a50f877311a74e40f82eB87. Wallet agent: 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E. MINT_START 1794319200 = 2026-11-10 21:00 WIB. Free pool 500 lot, slot user masih kosong (freeMintedByWallet=0, totalMinted=0 saat verifikasi 18:44 WIB). Gate website LOLOS (broccoliagent.com mencetak kontrak persis). Audit Binance: riskLevel 2 LOW, 1 hit RISK "Contract Not Renounced" — SUDAH diungkapkan ke user dan di-override eksplisit untuk mint gratis ini saja.

LANGKAH: jalankan `python3 ~/workspace/broccoli-mint/mint_free.py` (skrip menunggu block.timestamp >= MINT_START, lalu cek slot gratis, cek agentId, preview via baw, eksekusi hanya bila preview bersih, verifikasi receipt + saldo on-chain, dan menulis hasil ke ~/workspace/broccoli-mint/result-2026-11-10.json). JANGAN ubah skrip, JANGAN eksekusi manual di luar skrip, JANGAN ulangi bila skrip sudah menulis status "minted" (cek file hasil dulu sebelum tindakan apa pun).

LAPORAN ke chat utama, SEKALI, berdasarkan file hasil:
- Bila status "minted": laporkan tx hash, blok, gas, saldo 30.000.000 BROCCOLI terverifikasi, dan bahwa pair PCS V2 0xAEEaE4C5D55487C3438e036Af94C657A7eBaF8D8 belum dibuka (pool buka saat sell-out) — jadi koin ditahan dan didaftarkan ke pending swap.
- Bila status lain ("free_sold_out", "already_minted", "preview_dirty", "execute_failed", "receipt_failed", "verify_mismatch", "not_started", "agent_id_mismatch", "preview_balance_mismatch"): laporkan SEKALI status + alasannya dari file hasil, tanpa retry berbayar dan tanpa eksekusi alternatif.
- Bila skrip gagal total (tidak ada file hasil): laporkan kegagalan + output skrip, tanpa mengulang eksekusi.
