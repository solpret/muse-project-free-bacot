# HACKED max free mint — catatan persiapan (2026-11-05 ~00:38 WIB)

Kontrak NFT: 0xCD355D1191Ce9849B3A935C821A66d9DF37cFE77 (Sourcify exact_match, sumber: src/HackedPassV2.sol).
Status: MENUNGGU keputusan user soal override gate (widget diajukan 00:37 WIB). JANGAN eksekusi sebelum user mengetuk override.

## Koreksi penting: max free BUKAN 10
- Laporan STOP 00:37 WIB menyebut "max free mint = 10" berdasarkan remainingFor=10. ITU SALAH.
- remainingFor = HARD_MAX (10) − minted = batas TOTAL semua jalur per wallet, BUKAN jatah free.
- Jatah free sebenarnya (dari sumber): freeAi = 2, freeV2 = 4, satu kali klaim (freeDone diset true).
- claimFree(bytes32[] proof): allow = 4 bila proof Merkle V2 valid, else 2 bila isAiHolder, else revert BadProof.
- User adalah AI holder (isAiHolder true, dibaca on-chain) → claimFree([]) dengan proof kosong:
  _isV2([]) = false (proof.length == 0), lalu isAiHolder = true → allow = 2.
- Jadi MAX FREE MINT yang bisa dieksekusi = 2 NFT via claimFree([]), value 0, tanpa approval.
- Jalur V2 (4 NFT) butuh Merkle proof untuk alamat user terhadap v2Root (25 alamat) — proof itu tidak tersedia on-chain dan tidak boleh ditebak; jangan klaim V2 tanpa proof dari proyek.
- Jalur bayar (claimPublic 0,0014 BNB, buyExtra 0,002 BNB) TIDAK termasuk — user memesan free saja, tanpa fallback berbayar.
- Prasyarat saat eksekusi: totalSupply + 2 ≤ 4444 (saat cek: 1328 + 2), freeDone masih false, preview bersih (000000000, value 0, tanpa perubahan authority/allowance). Token ID hasil = log Transfer di receipt (bukan tebakan).

## Gate website: GAGAL (sudah dilaporkan ke user 00:37 WIB)
- Homepage hackedai.fun + /llms.txt hanya mencetak kontrak curve (0x8869…) dan token (0xfa7f…); nol penyebutan NFT; metadata /nft/1.json tanpa external_url/kontrak.
- Linkage yang ada: baseURI kontrak = https://hackedai.fun/nft/ (on-chain), nama sama, gerbang Agent ID sama, link dari user sendiri.
- Audit Binance: hasResult=false (dilaporkan sebagai tidak ada hasil), tanpa hit RISK, tanpa riskAlert — tidak memblokir.
- Kontrak tidak ada di same-owner-discards.json.
- Override (bila user mengetuk) hanya berlaku untuk mint ini saja, bukan izin permanen.

## HASIL — DIEKSEKUSI 2026-11-05 ~00:41 WIB
- User mengetuk override gate kasus ini saja 00:38 WIB → preview ketiga bersih penuh (requestId 3c0d20c4c5624c459a38aca961ae1a7b, simulationCode 000000000, tanpa authority/allowance/risk, +1 ERC721 #1391/#1392 simulasi) → execute sekali (orderId 26110400002020196607, BROADCASTED).
- Tx 0xf5ab9a18ffabb8c4f887e6409a0a0b8d1f64b59214278c66a397a5fc082db192, block 131666334, receipt 1; log Transfer: #1395 dan #1396 ke wallet utama (ID simulasi TIDAK berlaku — receipt yang berlaku). Gas 154088 (~0,00001449 BNB ≈ 0,0104 USDT @ 714,16 CoinGecko 2026-11-05).
- Pasca-mint: minted(user) 2, freeDone true, jatah free HABIS (satu kali klaim). Tidak di-list (tidak ada market proyek sendiri live terverifikasi). Rarity + daftar NFT diperbarui; MEMORY.md diperbarui.
