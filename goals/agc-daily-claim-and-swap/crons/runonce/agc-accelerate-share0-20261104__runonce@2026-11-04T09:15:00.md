---
id: agc-accelerate-share0-20261104
title: 'AGC percepat: klaim+jual share #0'
enabled: true
owner: goal:agc-daily-claim-and-swap
mode: task
schedule:
  kind: runonce
  timezone: Asia/Jakarta
  at: 2026-11-04T09:15:00
timeout_secs: 1800
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
PERCEPATAN KLAIM+JUAL AGC MODE A SHARE #0 — atas perintah user 2026-11-03 (tap "Ya, percepat: kedua share selesai besok"). Job sekali jalan ini HANYA mempercepat satu klaim yang sudah diotorisasi job harian; ia TIDAK mengubah job harian agc-auto-claim-daily (tetap jalan 09:37 WIB sebagai backup dan untuk reward vested).

Kontrak: AGCMinter 0x6288DFe86f22B53eEB6886aE2D78941de7483743, token AGC 0x63dea5aCdbE1F27c968907D08610A5f0A0284bA6, BSC chain 56. Router PCS V2 0x10ED43C718714eb63d5aA57B78B54704E256024E, WBNB 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c. Wallet: 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E (wallet utama saja). baw: /home/hatch/workspace/.baw-cli/bin/baw (path absolut; preview kedaluwarsa ~5 menit, jadi preview + eksekusi harus berurutan rapat untuk tiap transaksi). Calldata SELALU dibangun dengan eth_abi (venv ~/workspace/.abi-venv/bin/python), jangan hand-type selector/calldata.

TARGET: posisi Mode A index 0 — minted 2026-11-03 09:08:04 WIB, 1 share, deposit 0,002 BNB, 280.000 AGC, jatuh tempo 2026-11-04 09:08:04 WIB (time + REFUND_DELAY 86.400 detik).

LANGKAH:
1. Cek sesi baw (status + devMode enabled). Bila sesi kedaluwarsa -> laporkan SEKALI bahwa sesi kedaluwarsa dan job ini berhenti (jangan coba login ulang; job harian tetap menjadi backup), lalu berhenti.
2. Baca segar freePositions(wallet, 0, 10) + block time saat ini. Verifikasi: posisi index 0 masih claimed=false DAN sudah lewat jatuh temponya (time + 86.400 <= block time). Bila posisi sudah claimed=true -> laporkan SEKALI "share #0 sudah diklaim sebelumnya" dan BERHENTI tanpa transaksi apa pun (tidak ada swap). Bila belum jatuh tempo -> laporkan SEKALI dan BERHENTI tanpa transaksi (jangan retry; job harian tetap backup).
3. Catat saldo BNB dan saldo AGC wallet SEBELUM klaim.
4. Audit Binance untuk kontrak minter (POST https://web3.binance.com/bapi/defi/v1/public/wallet-direct/security/token/audit, header source: agent, body {binanceChainId: "56", contractAddress: minter, requestId: uuid baru}) dan untuk token AGC dengan cara yang sama. Ungkapkan hasilnya di laporan: hasResult=false berarti TIDAK ADA HASIL, bukan pass. Hit risiko spesifik (isHit dengan riskType RISK, atau riskAlert non-null) pada kontrak mana pun -> BERHENTI total, laporkan sekali dengan alasannya, jangan eksekusi, jangan retry, jangan cari jalur lain.
5. Klaim via claimFree([]) (array kosong = dari cursor, seperti job harian; pada jam ini hanya share #0 yang matang, jadi hanya dia yang terklaim — tetapi verifikasi lewat posisi, bukan asumsi). Preview baw bersih WAJIB (simulationCode 000000000, simulationErrorDetail null, value 0, authorityChanges kosong, allowanceChanges kosong, risks kosong). Preview kotor, 351803, atau 351805 -> BERHENTI, laporkan sekali dengan alasannya, jangan retry. Eksekusi hanya dari preview bersih itu; verifikasi receipt status 1 + posisi index 0 claimed=true + refund 0,002 BNB diterima + saldo AGC bertambah.
6. SWAP hanya delta AGC hasil klaim ini = (saldo AGC sesudah klaim) - (saldo AGC sebelum klaim). Bila delta <= 0 -> tidak ada swap, laporkan klaim saja. Bila delta > 0: kutip segar router getAmountsOut(delta, [AGC, WBNB]); syarat: kutip > 0 DAN kutip >= 2x estimasi biaya gas; bila tidak terpenuhi -> TAHAN AGC di wallet, laporkan sekali dengan alasannya, berhenti (job harian tetap backup). amountOutMin = 95% dari kutip. Bila allowance AGC -> router < delta: approve EXACT delta ke router (preview bersih dulu). Swap via swapExactTokensForETHSupportingFeeOnTransferTokens(delta, amountOutMin, [AGC, WBNB], wallet, deadline = block.timestamp + 1200), value 0, preview bersih wajib seperti di atas (perubahan balance/allowance hanya yang diharapkan). Eksekusi, verifikasi receipt status 1 + BNB diterima. Bila preview kotor, revert, 351803, atau 351805 -> laporkan sekali, AGC tetap di wallet, jangan retry.
7. LAPORAN SEKALI ke chat utama: tx hash tiap langkah + jumlah (refund BNB, AGC diklaim, BNB hasil swap) + verifikasi on-chain. Bila tidak ada eksekusi apa pun (sudah diklaim / belum matang / sesi mati / audit hit), laporan sekali itu tetap disampaikan dengan alasannya.

LARANGAN: TIDAK ADA MINT apa pun. Jangan klaim reward Mode B vested (claimReward) dan jangan tarik LP (withdrawLP) — itu pekerjaan job harian. Jangan sentuh posisi pool, jangan sentuh saldo AGC dari sumber lain, jangan kirim ke wallet lain. Jangan edit MEMORY.md; cukup tambahkan satu baris hasil ke ~/workspace/goals/agc-daily-claim-and-swap/hidden_files/accelerate-20261104.log.
