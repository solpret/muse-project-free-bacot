---
id: pxio-auto-claim
title: PXIO auto-claim mining (tiap 30 menit, klaim bila ≥100 PXIO)
enabled: false
owner: goal:pxio-miner-auto-claim
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-11-17T11:29:57
  every: 30m
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
PXIO AUTO-CLAIM MINING (dibuat 2026-11-17 atas perintah user "Ya buatkan auto claim sesuai jadwal"). Tujuan: klaim $PXIO hasil mining OTOMATIS sebelum Storage penuh, supaya mining tidak pernah berhenti. HANYA claim — tidak pernah mint, list, swap, approve, atau transaksi lain.

KONTEKS (terverifikasi 17 Nov 2026):
- Mining: PxioMiningV2 0xaf86f162299916Da344ef536Fc50f40cBa2bF703 (BSC chain 56). Token $PXIO: 0x870aD5f304871eC0c63BE1e976406e0b095A32CD. Wallet agent (baw): 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E. Miner: #5672 Laborer (10/jam) + #6359 Priest (35/jam). Rate saat dibuat: 45 $PXIO/jam, cap Storage 150 $PXIO, storage penuh ~3 jam 20 menit sesudah claim.
- Fungsi: state(address user) selector 0x31e658a5 → (started bool, lastTime uint64, amount uint256, rate uint256, cap uint256, nextRate uint256, nextCap uint256, claimed uint256). Semua amount/rate/cap dalam wei (18 desimal). claim() selector 0x4e71d92d, value 0, gas ~180k–220k.
- Alat baca: python3 ~/workspace/fast_exec/fcfs_read.py <calls.json> (calls.json = list {"to","data"}; pakai endpoint batch bawaan skrip itu). Alat eksekusi: ~/workspace/.baw-cli/bin/baw contract-call preview / execute --json. Audit: curl Binance https://web3.binance.com/bapi/defi/v1/public/wallet-direct/security/token/audit (binanceChainId 56, contractAddress PxioMiningV2, requestId = uuid baru via python3 -c 'import uuid; print(uuid.uuid4())' — uuidgen TIDAK ada di VM).
- State file job ini: ~/workspace/pxio-auto-claim/state.json (last check, last claim tx, last failure report). Buat foldernya bila belum ada. JANGAN tulis ke MEMORY.md.

TIAP RUN (tiap 30 menit):
1. Baca state(wallet agent) + saldo BNB wallet agent. Bila bacaan gagal, catat di state file + diam (coba lagi run berikut; jangan laporkan kegagalan baca sekali jalan).
2. Bila started=false → laporkan SEKALI ke chat utama bahwa mining belum dimulai (lalu diam sampai started=true lagi; jangan klaim).
3. Bila rate=0 atau amount=0 → diam (tidak ada yang bisa diklaim).
4. KEPUTUSAN KLAIM: klaim HANYA bila amount ≥ 100 $PXIO (100e18 wei) ATAU amount ≥ 80% dari cap (baca cap live — cap bisa berubah bila Storage di-upgrade). Bila belum mencapai ambang → DIAM (tanpa laporan chat).
5. Bila ambang tercapai, jalankan pengaman SEBELUM eksekusi, berurutan:
   a. Saldo BNB: estimasi gas = 250.000 × gas price live; saldo harus ≥ estimasi + margin. Bila kurang → STOP, laporkan SEKALI ke chat utama bahwa auto-claim dijeda karena BNB kurang (sertakan saldo + estimasi gas), dan jangan ulangi laporan yang sama lebih dari 1× sehari (catat waktu laporan di state file).
   b. Audit Binance atas PxioMiningV2: hasResult=false = TANPA HASIL (bukan lolos, hanya dilaporkan sebagai tanpa hasil). Bila ada RISK hit spesifik (isHit + riskType RISK, atau riskAlert non-null) → STOP, laporkan sekali, JANGAN eksekusi.
   c. Preview claim() via baw (value 0, inputData 0x4e71d92d). Eksekusi HANYA bila preview BERSIH: simulationCode 000000000 (di data.simulationResult.simulationCode — bentuk baru; bentuk lama di data.simulationCode juga diterima), tanpa error, value 0, tanpa authority/allowance changes, tanpa risks. Bila preview kotor / kode 351803 / 351805 → STOP, laporkan sekali + alasannya, JANGAN retry di run yang sama. Bila sesi baw expired/logout → laporkan sekali, JANGAN coba re-login (renewal butuh tap QR user).
6. Eksekusi: baw contract-call execute --requestId <id preview> --json. Bila preview kedaluwarsa (execute gagal karena expired) → buat preview baru SEKALI dan eksekusi; bila gagal lagi → laporkan sekali + berhenti.
7. Verifikasi sesudah eksekusi: baca receipt (status harus 1) + baca ulang state() (amount harus reset mendekati 0, claimed bertambah, rate = nextRate sebelumnya) + balanceOf PXIO wallet agent. Catat tx hash, blok, gas, jumlah $PXIO yang diterima di state file.
8. LAPORAN: laporkan SEKALI ke chat utama tiap klaim yang berhasil (tx hash, blok, gas BNB, $PXIO diterima, rate mining sekarang, perkiraan Storage penuh berikutnya). Diam bila tidak ada klaim. Jangan laporkan cek rutin yang tidak menghasilkan klaim.

LARANGAN: tidak pernah mint NFT, tidak pernah listing, tidak pernah swap $PXIO, tidak pernah approve, tidak pernah kirim $PXIO/BNB ke mana pun. Nilai claim() selalu 0 (hanya gas). Jangan klaim bila amount di bawah ambang. Jangan retry eksekusi yang hasilnya tidak pasti tanpa verifikasi on-chain dulu (cek receipt + state sebelum mengulang apa pun).
