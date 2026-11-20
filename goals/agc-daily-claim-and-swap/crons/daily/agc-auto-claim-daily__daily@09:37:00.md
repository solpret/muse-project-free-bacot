---
id: agc-auto-claim-daily
title: 'AGC harian: klaim saja (tanpa jual)'
enabled: true
owner: goal:agc-daily-claim-and-swap
mode: task
schedule:
  kind: daily
  timezone: Asia/Jakarta
  time: 09:37:00
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
PERUBAHAN 2026-11-05 (perintah user: satukan klaim Mode B; Mode A tetap sesuai jadwal matang): job ini TIDAK LAGI mengklaim reward Mode B (claimReward) — klaim reward Mode B hanya lewat job agc-modeb-claim-4h tiap 4 jam. Job ini tetap mengklaim refund Mode A yang jatuh tempo (claimFree) dan tarik LP Mode B yang sudah >= 14 hari (withdrawLP).

RANTAI OTOMATIS AGC HARIAN — dibuat atas perintah user 2026-11-03: pertama "Klaim otomatis saja" + "Tarik LP juga",
lalu "Eksekusi swap ke bnb langsung setelah semua claim tersebut berhasil dan tambah 1 share untuk mode A", lalu
DIBATALKAN langkah mint-nya 2026-11-03 ("Batalkan tambah 1 share, claim lalu swap saja").
PERUBAHAN 2026-11-04 (perintah user "tugas terjadwal AGC claim saja jangan jual AGC"): LANGKAH SWAP DIHAPUS TOTAL.
Job ini sekarang HANYA KLAIM — AGC hasil klaim TETAP di wallet, tidak pernah di-swap ke BNB DI JOB INI (job lain / perintah langsung user di luar job ini tidak dicakup larangan ini), tidak pernah di-approve
ke router untuk dijual.
URUTAN TIAP RUN: klaim yang jatuh tempo saja. TIDAK ADA SWAP, TIDAK ADA MINT OTOMATIS APA PUN (baik Mode A
maupun Mode B). Mint masa depan tetap manual atas perintah user di chat.

Kontrak: AGCMinter 0x6288DFe86f22B53eEB6886aE2D78941de7483743, token AGC 0x63dea5aCdbE1F27c968907D08610A5f0A0284bA6,
BSC chain 56.
Wallet: 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E (wallet utama saja; posisi kontrak dicatat per msg.sender).
baw: /home/hatch/workspace/.baw-cli/bin/baw (path absolut; preview kedaluwarsa ~5 menit, jadi preview + eksekusi harus
berurutan rapat untuk tiap transaksi).

LANGKAH 1 — KLAIM (baca-saja dulu, lalu eksekusi bila jatuh tempo):
1a. Baca pending(wallet) di minter (selector 0x5eebea20 + alamat): freeBnb, freeAgc, rewardVested, lpWithdrawable. Juga
    baca saldo BNB dan saldo AGC wallet SEBELUM klaim. Bila semua nilai pending nol -> DIAM, tidak ada laporan, tidak
    ada transaksi, rantai berhenti di sini.
1b. GUARD NILAI: lewati claimReward bila rewardVested < 10.000 AGC (nilainya di bawah ~0,0002 BNB, lebih kecil dari gas;
    biarkan menumpuk sampai run berikutnya). Guard ini TIDAK berlaku untuk claimFree (refund 0,002 BNB selalu jauh di atas
    gas) dan withdrawLP (selalu substansial). Catatan: sejak perubahan 2026-11-05, claimReward tidak lagi dieksekusi
    job ini (lihat kepala body); guard ini hanya relevan sebagai bacaan pending.
1c. Untuk TIAP jenis klaim yang jatuh tempo dan lolos guard, jalankan secara terpisah: (i) audit Binance untuk kontrak
    minter (POST https://web3.binance.com/bapi/defi/v1/public/wallet-direct/security/token/audit, header source: agent
    dan User-Agent: binance-web3/1.4 (Skill), body {binanceChainId: "56", contractAddress: minter, requestId: uuid baru};
    ungkapkan hasilnya: hasResult=false berarti TIDAK ADA HASIL, bukan pass; hit risiko spesifik (isHit dengan riskType
    RISK, atau riskAlert non-null) -> BERHENTI untuk klaim itu, laporkan sekali, jangan eksekusi); (ii) preview baw bersih
    WAJIB (simulationCode 000000000, simulationErrorDetail null, value 0, authorityChanges kosong, allowanceChanges
    kosong, risks kosong; preview kotor, 351803, atau 351805 -> BERHENTI untuk klaim itu, laporkan sekali dengan
    alasannya, jangan retry dengan jalur lain, jangan akali); (iii) eksekusi hanya dari preview bersih itu dan verifikasi
    receipt status 1 + perubahan posisi/saldo on-chain.
1d. Jenis klaim job ini (calldata dibangun dengan eth_abi, jangan hand-type selector): claimFree([]) untuk refund Mode A (array
    kosong = dari cursor, maks 50 posisi; ulangi maks 3x dalam run yang sama selama pending masih menunjukkan
    freeBnb/freeAgc matang > 0); withdrawLP([]) untuk LP Mode B berumur
    >= 14 hari (mengembalikan AGC + BNB + sisa reward). claimReward([]) untuk reward Mode B vested TIDAK dilakukan
    job ini sejak 2026-11-05 — itu pekerjaan job agc-modeb-claim-4h.
1e. TIAP KLAIM BERDIRI SENDIRI: klaim yang jatuh tempo DAN lolos guard pada run ini dieksekusi + diverifikasi satu
    per satu. Bila SATU klaim GAGAL (audit hit, preview kotor, 351803, 351805, receipt gagal) -> laporkan sekali dengan
    alasannya untuk klaim itu saja; klaim lain yang jatuh tempo tetap dijalankan. Tidak ada langkah lanjutan apa pun
    setelah klaim: AGC hasil klaim TETAP di wallet.

LAPORAN: gabungkan semua klaim yang sukses dalam run ini ke dalam SATU laporan dengan tx hash tiap langkah +
jumlah (BNB/AGC diterima). Diam hanya bila tidak ada satu pun yang jatuh tempo.
SESI: baw kedaluwarsa -> laporkan SEKALI bahwa sesi kedaluwarsa dan eksekusi berhenti sampai user memperbarui lewat tap
QR di aplikasi Binance; JANGAN mencoba login ulang dari cron. Catat status "expiry reported" di
~/workspace/agc-claim-auto/state.json dan DIAM pada run berikutnya selama sesi masih mati; hapus penanda itu begitu
sesi hidup kembali dan rantai berjalan lagi.
Jadwal yang diharapkan: run harian sekitar 09:37 WIB; rantai pertama yang lengkap diperkirakan 2026-11-04 (klaim refund
Mode A 0,002 BNB + 280.000 AGC yang matang 09:08:04 WIB + reward vested di atas ambang).
Tarik LP pertama jatuh tempo 2026-11-17 ~09:11 WIB dan akan masuk rantai hari itu.
Pekerjaan ini TIDAK mencakup mint apa pun, TIDAK mencakup swap/jual AGC apa pun, dan TIDAK menggantikan pengingat
lain yang masih aktif kecuali dinyatakan di chat.
