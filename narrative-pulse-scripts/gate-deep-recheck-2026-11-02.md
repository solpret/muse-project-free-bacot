# Gate Deep Re-check — 21 Lead Terblokir Free Bacot

- **Tanggal re-check:** 2026-11-02 (sesi malam WIB; pembacaan on-chain dari `/tmp/gate21_reads.json`)
- **Perintah:** user menyetujui via widget 2026-11-02 ~19:39 WIB ("Ya, deep re-check 21 lead terblokir")
- **Sifat:** READ-ONLY. Tidak ada preview, mint, approval, listing, transfer, atau perubahan state apa pun.
  Tidak ada file lain yang diubah (snapshot, hot-leg-seen.json, hot-leg-reported.json, MEMORY.md, cron).
- **Daftar target:** seluruh entri `contracts` berstatus `strong-lead-gate-blocked-2026-11-02` di
  `~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json` (21 entri, alamat diambil dari field `address` masing-masing entri).
- **Metode yang dijalankan per lead:** (A) pencarian alamat kontrak mentah, (B) postingan Boltbook + link di dalamnya,
  (C) source/metadata Sourcify, (D) pola situs same-family (.vercel.app / .deed.page / .pages.dev),
  (E) pencatatan deployer group via owner(), (F) twitterapi.io hanya untuk konfirmasi handle yang sudah ditemukan,
  (G) pencarian nama/simbol proyek + cek dokumen agent situs kandidat (/llms.txt, /skill.md, /launch.json) dan kontrak yang tercetak di situs,
  (H) baca + decode contractURI() on-chain, cari external_link/external_url.
- **Standar bukti (ketat):** website dinyatakan DITEMUKAN hanya bila ada URL + bukti itu situs proyek
  (situs menautkan/mencetak kontrak proyek, atau ditautkan dari postingan/listing resmi proyek, atau pola same-family dengan linkage).
  URL tebakan, same-name match saja, dan postingan pihak ketiga tanpa linkage = TIDAK CUKUP.

## Hasil ringkas (di depan, detail per lead di bawah)

- **Website DITEMUKAN: 0 dari 21.**
- **Tetap TIDAK DITEMUKAN (pool masih buka): 16 lead.**
- **SOLD OUT (pool gratis habis; pencarian website tidak lagi relevan): 5 lead** —
  Venusia (318/318), Ghoulito (313/313), Witchibo (316/316), Circuitfox (315/315),
  dan **AgentCoinFlip (1111/1111 — sold out BARU yang belum tercatat di snapshot; terakhir dibaca 583 sebelum re-check ini)**.
- **Tidak ada satu pun lead yang lolos gate website-only sebagai hasil re-check ini.**
  Tidak ada preview/mint yang dilakukan atau direkomendasikan dari laporan ini — eksekusi adalah keputusan parent.

## Catatan metode lintas lead

- **(H) contractURI():** 20 dari 21 berhasil dibaca dan di-decode. 19 berisi base64 JSON dengan HANYA
  name/description/seller_fee_basis_points (500) — tanpa URL apa pun. Satu-satunya yang berisi link adalah
  AgentCoinFlip, dan link itu hanya X (https://x.com/AgentCoinFlip) — X bersifat opsional, bukan gate,
  dan pool-nya pun sudah sold out.
- **(H) AZET — misteri terpecahkan:** contractURI() AZET me-revert `execution reverted: 0x` pada re-check ini,
  dan ABI Sourcify AZET memang TIDAK memuat fungsi contractURI sama sekali. Jadi kegagalan baca AZET
  sebelumnya (2×) adalah **revert karena fungsi tidak ada, bukan RPC burst failure**. Status website AZET
  tetap TIDAK DITEMUKAN (tidak ada metode lain yang menemukan situs), tetapi pertanyaan contractURI-nya
  sudah terjawab: kontrak ini tidak punya contractURI untuk di-decode.
- **(E) Deployer group via owner():** 0x190f = 11 lead (Krakenbo, Venusia, Hydralet, Ghoulito, Neonfawn,
  Nanobee, Griffito, Niuniubo, Witchibo, Circuitfox, Plutoko); 0xd76d = 4 (Jiayoupanda, Glasscore,
  Gourdwitch, Neonpurrix); 0xa054 = 2 (Malabao, Nightsable); 0x8a3b = 1 (NightshadeClub);
  0x3909 = 1 (AZET); AgentCoinFlip = owner() ikut revert (tidak ada fungsi owner di ABI yang terbaca).
  Factory wave tanpa website tetap FAIL sesuai gate — bukan exempt.
- **(C) Sourcify:** ABI berhasil diambil untuk Malabao (exact_match, template factory: freeClaimed,
  FREE_SUPPLY, owner, contractURI), AZET (freeMinted, FREE_SUPPLY, owner, TANPA contractURI),
  AgentCoinFlip (freeMinted, freeRemaining, FREE_SUPPLY, contractURI, exact_match). Untuk 6 lead lain
  (Glasscore, Neonpurrix, Plutoko, Circuitfox, Gourdwitch, AgentCoinFlip) endpoint match summary Sourcify
  dikembalikan dan di-grep URL — tidak ada URL apa pun di dalamnya (Glasscore: exact_match,
  verifiedAt 2026-11-02T09:38:28Z). Source template factory tidak memuat link.
- **(B) Boltbook:** postingan wave Boltbook berhasil di-fetch (HTTP 200, 12.491 byte); link yang
  terekstrak hanya bscscan address, satu token gang.fun, dan x.com/bolt_book — tidak ada situs proyek
  untuk satu pun dari 21 lead. Postingan Boltbook penama per lead sudah tercakup dalam gate notes
  sebelumnya; pencarian web re-check ini tidak menemukan postingan Boltbook penama baru yang membawa
  link situs untuk lead mana pun.
- **(F) twitterapi.io:** TIDAK dijalankan untuk konfirmasi handle — tidak ada handle baru yang ditemukan
  untuk dikonfirmasi (kredit provider dilaporkan habis/402; satu-satunya handle, @AgentCoinFlip, sudah
  diketahui dari contractURI dan tidak mengubah gate karena X opsional dan pool sold out).
- **(D) Same-family:** tidak ditemukan satu pun kandidat situs .vercel.app / .deed.page / .pages.dev
  yang ter-link ke kontrak-kontrak ini.
- **Non-evidence yang sengaja dicatat agar tidak disalahartikan sebagai linkage:**
  Venusia di Bitget ("Venusia (VENUS)") memakai kontrak BERBEDA (0x5a7b…124b945); token "Nightshade"
  di ApeSpace adalah token BERBEDA, bukan NFT BSC ini; hasil "Niubi NIUMOON Ticket" untuk Niuniubo
  adalah kontrak BERBEDA dari 2025; glass.trading untuk Glasscore adalah proyek koin kaca fisik yang
  secara eksplisit menyatakan "not crypto, not an NFT" — bukan proyek GLASS ini.

---

## 1. Malabao (MALABA) — TIDAK DITEMUKAN

- **Kontrak:** `0x2C215262635E66c798c5a1Ba4411fA9F06852bDD`
- **Pool saat dibaca:** freeClaimed 431 / FREE_SUPPLY 844 (totalSupply 431) — masih buka.
- **Deployer group (E):** owner 0xa054… (grup 0xa054).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee_basis_points, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "Malabao" — tidak ada situs proyek.
- **(C):** Sourcify exact_match, template factory, tidak ada URL.
- **Verdict:** TIDAK DITEMUKAN. Metode (A)–(H) dijalankan (F tidak diperlukan — tidak ada handle ditemukan).
  Yang kurang: URL situs proyek dengan bukti linkage ke kontrak ini.

## 2. Nightsable (NIGHTS) — TIDAK DITEMUKAN

- **Kontrak:** `0xc4f2797f050835daf3d24c1764eca60ac4168f21`
- **Pool saat dibaca:** freeClaimed 406 / FREE_SUPPLY 794 (totalSupply 406) — masih buka.
- **Deployer group (E):** owner 0xa054… (grup 0xa054).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "Nightsable" — tidak ada situs proyek.
- **Verdict:** TIDAK DITEMUKAN. Metode (A)–(H) dijalankan (F tidak diperlukan).
  Yang kurang: URL situs proyek dengan bukti linkage.

## 3. NightshadeClub (NSHD) — TIDAK DITEMUKAN

- **Kontrak:** `0x2C027F14d36a080E5e058CF39407EAc2503B90Cc`
- **Pool saat dibaca:** freeClaimed 495 / FREE_SUPPLY 983 (totalSupply 545; selisih = jalur paid) — masih buka.
- **Deployer group (E):** owner 0x8a3b… (bukan grup 0x190f/0xd76d/0xa054).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "NightshadeClub" — tidak ada situs proyek.
  Catatan non-evidence: token "Nightshade" di ApeSpace adalah token berbeda, bukan NFT BSC ini.
- **Verdict:** TIDAK DITEMUKAN. Metode (A)–(H) dijalankan (F tidak diperlukan).
  Yang kurang: URL situs proyek dengan bukti linkage.

## 4. Krakenbo (KRAKENBO) — TIDAK DITEMUKAN

- **Kontrak:** `0x46c1815082ccf1273e3c07548ef2004046Bb7Fc0`
- **Pool saat dibaca:** freeClaimed 463 / FREE_SUPPLY 903 (totalSupply 480) — masih buka.
- **Deployer group (E):** owner 0x190f… (grup 0x190f).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "Krakenbo" — tidak ada situs proyek.
- **Verdict:** TIDAK DITEMUKAN. Metode (A)–(H) dijalankan (F tidak diperlukan).
  Yang kurang: URL situs proyek dengan bukti linkage.

## 5. Jiayoupanda (JIAYOU) — TIDAK DITEMUKAN

- **Kontrak:** `0x520ceb54367B729Dfa0b00E2a4541E6702D5a7E1`
- **Pool saat dibaca:** freeClaimed 521 / FREE_SUPPLY 755 (totalSupply 534) — masih buka.
- **Deployer group (E):** owner 0xd76d… (grup 0xd76d).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "Jiayoupanda" — tidak ada situs proyek.
- **Verdict:** TIDAK DITEMUKAN. Metode (A)–(H) dijalankan (F tidak diperlukan).
  Yang kurang: URL situs proyek dengan bukti linkage.

## 6. AZET (AZET) — TIDAK DITEMUKAN (contractURI terjawab: fungsi tidak ada)

- **Kontrak:** `0xFF8BfeF2c0d16BDa6E8667812bCa35Ecb42A1a37`
- **Pool saat dibaca:** freeMinted 2319 / FREE_SUPPLY 4000 (totalSupply 2331) — masih buka.
- **Deployer group (E):** owner 0x3909… (grup 0x3909).
- **(H):** contractURI() me-revert `execution reverted: 0x` pada re-check ini (retry berjeda sudah dilakukan
  pada pembacaan batch). ABI Sourcify AZET TIDAK memuat fungsi contractURI sama sekali.
  Kesimpulan: kegagalan baca sebelumnya adalah revert fungsi-tidak-ada, BUKAN RPC burst failure.
  Tidak ada contractURI yang bisa di-decode untuk AZET — dan tidak ada metode lain yang menemukan situs.
- **(A)+(G):** pencarian alamat mentah + nama "AZET" — tidak ada situs proyek.
- **(C):** Sourcify ABI: freeMinted, FREE_SUPPLY, owner, TANPA contractURI.
- **Verdict:** TIDAK DITEMUKAN. Metode (A)–(H) dijalankan (H menghasilkan verdict fungsi-tidak-ada, bukan gagal baca).
  Yang kurang: URL situs proyek dengan bukti linkage.

## 7. Venusia (VENUSIA) — SOLD OUT

- **Kontrak:** `0xf621ed47bfce124069ea1d701522ad0c92bfe91d`
- **Pool saat dibaca:** freeClaimed 318 / FREE_SUPPLY 318 (totalSupply 322) — **SOLD OUT, dikonfirmasi re-check ini**
  (sebelumnya sudah dilaporkan sold out oleh hot-leg 19:09).
- **Deployer group (E):** owner 0x190f… (grup 0x190f).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "Venusia" — tidak ada situs proyek; non-evidence: token
  "Venusia (VENUS)" di Bitget memakai kontrak berbeda (0x5a7b…124b945), bukan linkage.
- **Verdict:** SOLD OUT — pencarian website tidak lagi relevan untuk lead ini.

## 8. Hydralet (HYDRALET) — TIDAK DITEMUKAN

- **Kontrak:** `0x429f23778562bc4be82c215ba12180e1ff297e8f`
- **Pool saat dibaca:** freeClaimed 284 / FREE_SUPPLY 344 (totalSupply 290) — masih buka.
- **Deployer group (E):** owner 0x190f… (grup 0x190f).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "Hydralet" — tidak ada situs proyek.
- **Verdict:** TIDAK DITEMUKAN. Metode (A)–(H) dijalankan (F tidak diperlukan).
  Yang kurang: URL situs proyek dengan bukti linkage.

## 9. Gongxibao (GONGXIBAO) — TIDAK DITEMUKAN

- **Kontrak:** `0xd8501c1ff155466854ba037a9ecf8031da290be7`
- **Pool saat dibaca:** freeClaimed 200 / FREE_SUPPLY 327 (totalSupply 206) — masih buka.
- **Deployer group (E):** owner 0x190f… (grup 0x190f).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "Gongxibao" — tidak ada situs proyek.
- **Verdict:** TIDAK DITEMUKAN. Metode (A)–(H) dijalankan (F tidak diperlukan).
  Yang kurang: URL situs proyek dengan bukti linkage.

## 10. Ghoulito (GHOULITO) — SOLD OUT

- **Kontrak:** `0x0e13e8fd65452cd2b7238695a0a7dd9297383af9`
- **Pool saat dibaca:** freeClaimed 313 / FREE_SUPPLY 313 (totalSupply 319) — **SOLD OUT, dikonfirmasi re-check ini**
  (sebelumnya sudah dilaporkan sold out oleh hot-leg 19:29).
- **Deployer group (E):** owner 0x190f… (grup 0x190f).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "Ghoulito" — tidak ada situs proyek.
- **Verdict:** SOLD OUT — pencarian website tidak lagi relevan untuk lead ini.

## 11. Neonfawn (NEONFAWN) — TIDAK DITEMUKAN

- **Kontrak:** `0x2a93fafca568a6ee7d8213f9b31f41ed71d51f55`
- **Pool saat dibaca:** freeClaimed 256 / FREE_SUPPLY 310 (totalSupply 262) — masih buka.
- **Deployer group (E):** owner 0x190f… (grup 0x190f).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "Neonfawn" — tidak ada situs proyek.
- **Verdict:** TIDAK DITEMUKAN. Metode (A)–(H) dijalankan (F tidak diperlukan).
  Yang kurang: URL situs proyek dengan bukti linkage.

## 12. Nanobee (NANOBEE) — TIDAK DITEMUKAN

- **Kontrak:** `0x4cd813ad6c3c2cc740d48f357d7e0f0e053449f1`
- **Pool saat dibaca:** freeClaimed 198 / FREE_SUPPLY 330 (totalSupply 204) — masih buka.
- **Deployer group (E):** owner 0x190f… (grup 0x190f).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "Nanobee" — tidak ada situs proyek.
- **Verdict:** TIDAK DITEMUKAN. Metode (A)–(H) dijalankan (F tidak diperlukan).
  Yang kurang: URL situs proyek dengan bukti linkage.

## 13. Griffito (GRIFFITO) — TIDAK DITEMUKAN

- **Kontrak:** `0x3a8b62d76900145Cb574315e01215c3b294ea402`
- **Pool saat dibaca:** freeClaimed 268 / FREE_SUPPLY 341 (totalSupply 269) — masih buka.
- **Deployer group (E):** owner 0x190f… (grup 0x190f).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "Griffito" — tidak ada situs proyek.
- **Verdict:** TIDAK DITEMUKAN. Metode (A)–(H) dijalankan (F tidak diperlukan).
  Yang kurang: URL situs proyek dengan bukti linkage.

## 14. Niuniubo (NIUNIUBO) — TIDAK DITEMUKAN

- **Kontrak:** `0x200aC8776A5351C29c4D854012ffC1794a7DfA79`
- **Pool saat dibaca:** freeClaimed 247 / FREE_SUPPLY 318 (totalSupply 248) — masih buka.
- **Deployer group (E):** owner 0x190f… (grup 0x190f).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "Niuniubo" — tidak ada situs proyek.
  Catatan non-evidence: hasil "Niubi NIUMOON Ticket" adalah kontrak berbeda dari 2025, bukan linkage.
- **Verdict:** TIDAK DITEMUKAN. Metode (A)–(H) dijalankan (F tidak diperlukan).
  Yang kurang: URL situs proyek dengan bukti linkage.

## 15. Witchibo (WITCHIBO) — SOLD OUT

- **Kontrak:** `0x30e2ED57e433671907d7AEB01a7E7514e17FD649`
- **Pool saat dibaca:** freeClaimed 316 / FREE_SUPPLY 316 (totalSupply 317) — **SOLD OUT, dikonfirmasi re-check ini**
  (sebelumnya sudah dilaporkan sold out oleh hot-leg 19:14).
- **Deployer group (E):** owner 0x190f… (grup 0x190f).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "Witchibo" — tidak ada situs proyek.
- **Verdict:** SOLD OUT — pencarian website tidak lagi relevan untuk lead ini.

## 16. Circuitfox (CIRCUITFOX) — SOLD OUT

- **Kontrak:** `0xD12B23694A910dBC74EF50aDBaC6aB4F6b34F55C`
- **Pool saat dibaca:** freeClaimed 315 / FREE_SUPPLY 315 (totalSupply 316) — **SOLD OUT, dikonfirmasi re-check ini**
  (sebelumnya sudah dilaporkan sold out oleh hot-leg 19:14).
- **Deployer group (E):** owner 0x190f… (grup 0x190f).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "Circuitfox" — tidak ada situs proyek.
- **Verdict:** SOLD OUT — pencarian website tidak lagi relevan untuk lead ini.

## 17. Plutoko (PLUTOKO) — TIDAK DITEMUKAN

- **Kontrak:** `0xF5Cf199D08A7B9bFE5C1Fc44ef5eabdae4314A56`
- **Pool saat dibaca:** freeClaimed 196 / FREE_SUPPLY 348 (totalSupply 197) — masih buka.
- **Deployer group (E):** owner 0x190f… (grup 0x190f).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "Plutoko" — tidak ada situs proyek.
- **(C):** Sourcify match summary di-grep URL — tidak ada URL.
- **Verdict:** TIDAK DITEMUKAN. Metode (A)–(H) dijalankan (F tidak diperlukan).
  Yang kurang: URL situs proyek dengan bukti linkage.

## 18. Glasscore (GLASS) — TIDAK DITEMUKAN

- **Kontrak:** `0xe2826b507Da79a642aa1fce108Aa8dD11cE67e3f`
- **Pool saat dibaca:** freeClaimed 1394 / FREE_SUPPLY 1926 (totalSupply 1401) — masih buka.
- **Deployer group (E):** owner 0xd76d… (grup 0xd76d).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "Glasscore" — tidak ada situs proyek.
  Catatan non-evidence: glass.trading adalah proyek koin kaca fisik yang secara eksplisit menyatakan
  "Glass is not crypto, not an NFT, and not an investment product" — BUKAN proyek GLASS ini, bukan linkage.
- **(C):** Sourcify exact_match (verifiedAt 2026-11-02T09:38:28Z), match summary di-grep URL — tidak ada URL.
- **Verdict:** TIDAK DITEMUKAN. Metode (A)–(H) dijalankan (F tidak diperlukan).
  Yang kurang: URL situs proyek dengan bukti linkage.
  (Catatan: order mint Glasscore oleh user sudah DIBATALKAN 2026-11-02 ~18:40 — re-check ini tidak mengubah status itu.)

## 19. Gourdwitch (GOURD) — TIDAK DITEMUKAN

- **Kontrak:** `0x30405B8442Cf2F1C488F256A8DF12e1A2e22E581`
- **Pool saat dibaca:** freeClaimed 1418 / FREE_SUPPLY 1672 (totalSupply 1425) — masih buka.
- **Deployer group (E):** owner 0xd76d… (grup 0xd76d).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "Gourdwitch" — tidak ada situs proyek.
- **(C):** Sourcify match summary di-grep URL — tidak ada URL.
- **Verdict:** TIDAK DITEMUKAN. Metode (A)–(H) dijalankan (F tidak diperlukan).
  Yang kurang: URL situs proyek dengan bukti linkage.

## 20. Neonpurrix (NEONP) — TIDAK DITEMUKAN

- **Kontrak:** `0xd2136C5aF996D264414cbF981E7B1804ba80177C`
- **Pool saat dibaca:** freeClaimed 1458 / FREE_SUPPLY 1797 (totalSupply 1465) — masih buka.
- **Deployer group (E):** owner 0xd76d… (grup 0xd76d).
- **(H):** contractURI base64 JSON ter-decode penuh — hanya name/description/seller_fee, tanpa URL.
- **(A)+(G):** pencarian alamat mentah + nama "Neonpurrix" — tidak ada situs proyek.
- **(C):** Sourcify match summary di-grep URL — tidak ada URL.
- **Verdict:** TIDAK DITEMUKAN. Metode (A)–(H) dijalankan (F tidak diperlukan).
  Yang kurang: URL situs proyek dengan bukti linkage.

## 21. AgentCoinFlip (ACFNFT) — SOLD OUT (baru; X ditemukan tapi bukan gate)

- **Kontrak:** `0xc4194c557Fc04cC4867F4DD10da9c7B358333AFd`
- **Pool saat dibaca:** freeMinted 1111 / FREE_SUPPLY 1111 (totalSupply 1139) — **SOLD OUT.
  Ini sold out BARU: pembacaan snapshot terakhir (19:27 WIB) masih mencatat 583; re-check ini membaca 1111/1111.**
- **Deployer group (E):** owner() ikut revert (tidak ada fungsi owner pada ABI yang terbaca) — grup tidak tercatat.
- **(H):** contractURI ter-decode (format JSON utf8, bukan base64):
  `{"name":"AgentCoinFlip","description":"AgentCoinFlip: 1,777 fully on-chain pixel coins on BNB Chain. X: @AgentCoinFlip","external_link":"https://x.com/AgentCoinFlip"}`.
  Satu-satunya external_link di seluruh 21 lead — dan itu HANYA X. X bersifat opsional, bukan gate,
  sehingga kalaupun pool masih buka, bukti ini saja TIDAK meloloskan gate website-only.
- **(A)+(G):** pencarian alamat mentah + nama "AgentCoinFlip" — tidak ada situs proyek.
- **(C):** Sourcify exact_match; ABI memuat freeMinted, freeRemaining, FREE_SUPPLY, contractURI.
- **X handle (opsional, bukan gate):** https://x.com/AgentCoinFlip (dari contractURI sendiri).
- **Verdict:** SOLD OUT — pencarian website tidak lagi relevan untuk lead ini, dan bukti X saja tidak meloloskan gate.

---

## Ringkasan akhir

| Status | Jumlah | Daftar |
|---|---|---|
| Website DITEMUKAN | **0** | — |
| Tetap TIDAK DITEMUKAN (pool buka) | **16** | Malabao (431/844), Nightsable (406/794), NightshadeClub (495/983), Krakenbo (463/903), Jiayoupanda (521/755), AZET (2319/4000), Hydralet (284/344), Gongxibao (200/327), Neonfawn (256/310), Nanobee (198/330), Griffito (268/341), Niuniubo (247/318), Plutoko (196/348), Glasscore (1394/1926), Gourdwitch (1418/1672), Neonpurrix (1458/1797) |
| SOLD OUT | **5** | Venusia (318/318), Ghoulito (313/313), Witchibo (316/316), Circuitfox (315/315), AgentCoinFlip (1111/1111 — baru) |

**Kesimpulan plainly: TIDAK ADA website proyek yang ditemukan untuk satu pun dari 21 lead.**
Semua 16 lead yang pool-nya masih buka tetap TERBLOKIR gate website-only. Satu-satunya external_link
yang ditemukan di seluruh re-check (X AgentCoinFlip) bukan website dan tidak meloloskan gate.
Temuan sampingan: (1) misteri contractURI AZET terjawab — fungsi tidak ada di ABI, bukan RPC burst;
(2) AgentCoinFlip sold out 1111/1111, belum tercatat di snapshot.
Tidak ada preview/mint/eksekusi yang dilakukan. Keputusan lebih lanjut ada di parent.
