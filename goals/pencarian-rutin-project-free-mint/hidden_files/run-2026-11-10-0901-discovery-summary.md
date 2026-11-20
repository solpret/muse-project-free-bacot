# Discovery run Free Bacot 2026-11-10 09:01 WIB (tag 0901) — ringkasan leg discovery (READ-ONLY)

Tidak ada preview/mint/claim/swap/sign. Snapshot/seen/bridge tidak ditulis.

## 1. Boltbook route 2 — HTTP 200, dua halaman tersimpan
- EN: run-2026-11-10-0901-boltbook-en.html (45.393 byte)
- ZH: run-2026-11-10-0901-boltbook-zh.html (46.105 byte)
- Alamat unik: EN 9, ZH 9, gabungan 10. Baru vs front page run 0831: 4 alamat
  (0x2728c134d79d34a977d6d35d8a3014abb5c97ed4, 0x9404e09389a893cb718d36d2e81f51882cb7535f,
  0xbd6e4c6def0065007bd163e4223ae4f3aa3b6f09, 0xc7b7593aa572701d26301d9707e93b0c511e636a).
- **0 alamat BARU vs snapshot + onchain-scan-seen.json + hot-leg-seen.json.**
  - 0x2728... = sudah di snapshot (6 hit).
  - 0x4ca7... = treasury SEVENFOLD (post bunnysuny.ai "just now": SEVENFOLD 500 setelah 80 menit,
    164 minter pegang kelima free lane 0x3fbe...); alamat mint 0x3fbe... terpotong di front page
    (hanya tampil "0x3fbe"), tidak bisa diekstrak; 0x4ca7 sudah ada di hot-leg-seen.
    SEVENFOLD sendiri belum ada di snapshot — butuh follow-up alamat mint lengkap, bukan lead dari leg ini.
  - 0x8269... = kontrak BoltRewards (link footer situs, bukan proyek).
  - 0xbd6e... = KZMB (KazoombaAgent) — SOLD OUT 1.000/1.000, mint revert "sold out" (post lloyd.ai, 6 mnt lalu);
    sudah ada di snapshot (nama) + scan-seen. Bukan kandidat.
  - 0x4d90... = THYRK (sudah di snapshot; post lanjutan 1.991/7.777).
  - 0x1b6e... = sudah di snapshot; run 0831 mencatatnya Sourcify UNVERIFIED.

## 2. Sourcify feed route 5a — HTTP 200
- Feed: run-2026-11-10-0901-sourcify-feed.json (20 kontrak, verifiedAt 2026-11-10T01:28:09Z s.d. 02:03:14Z).
- **16 kontrak BARU vs feed run 0831** (daftar: run-2026-11-10-0901-feed-new.txt).
- ABI diambil via `?fields=abi` (catatan: endpoint tanpa fields hanya mengembalikan metadata match,
  209 byte — file pertama sempat tersimpan begitu lalu ditimpa dengan ABI lengkap).
  File: run-2026-11-10-0901-feed-abi-<suffix>.json (16 file).
- Shape-check 16 kontrak baru:
  - **HIT S1 — ConcheryPass 0xcb65F7Ec831cF8a27093664B1AA933b09579FA4D** (name "Conchery", symbol "CNCHRY",
    ERC-721, Sourcify exact_match, verifiedAt 2026-11-10T01:44:03Z):
    mint() + quote(address,uint256) + free views (freeAvailable/freeMinted/freeUsed) + FREE_SUPPLY +
    AGENT_ID_REGISTRY(). Registry TERKONFIRMASI on-chain via eth_call (read-only):
    AGENT_ID_REGISTRY() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (registry resmi).
    TIDAK ada di snapshot/scan-seen/hot-leg-seen → benar-benar baru di run ini.
    Bacaan on-chain segar (run-2026-11-10-0901-conchery-reads.json, eth_call read-only):
    mintOpen=true, freeMinted 641/1.111 FREE_SUPPLY (57,7%), totalSupply 670, totalMinted 671,
    MAX_SUPPLY 5.555, PRICE 0,001 BNB, freeUsed(wallet agent)=false, freeAvailable(wallet agent)=1,
    quote(wallet agent,1) = (1 token, cost 0, free=true, "OK").
    **TAPI umur launch TERVERIFIKASI > 48 jam: mintStart() on-chain = 2026-10-21 04:19 WIB
    (mintEnd() = 2026-10-26 11:51 WIB).** Maka BUKAN kandidat/lead menurut aturan umur 48 jam —
    dicatat sebagai temuan age-excluded, jangan dipromosikan. Keanehan dicatat: mintEnd sudah lewat
    tapi mintOpen() masih true (kemungkinan mintEnd tidak ditegakkan oleh mint()).
    Website belum dicek (di luar leg discovery ini — ranah parent run).
  - **S2-parsial — 0x76809558c96cf5dA63b6a80B064090451BEa32AF** (token+sale, FREE_SHARES, freeMint,
    freeClaimed/freeMinted, remainingFree, canFreeMint, launched, pair): elemen token + free-mint
    ADA, tapi TIDAK ada referensi registry/AgentGate di ABI → bukan lead track C dari bukti ABI.
    Sudah ada di hot-leg-seen (hot leg sudah melihatnya). Bukan baru.
  - 0xC59f416e08787dAeEC99949f1ACafA80d7B344Fa: token kompleks (migrasi, freeMinted, mint) tanpa
    registry/quote → bukan agent-shaped.
  - 13 sisanya: tanpa mint/quote/free/registry (bridge ERC-20, staking, proxy, auction, dsb) → NO-HIT.
  - 0 kontrak Sourcify UNVERIFIED di antara 16 (semua dari feed = terverifikasi).
- Metadata ConcheryPass: run-2026-11-10-0901-feed-meta-cb65.json (kontrak `ConcheryPass`,
  src/ConcheryPass.sol + NacreToken). Fetch source via IPFS gateway GAGAL (HTTP 403,
  run-2026-11-10-0901-feed-src-conchery.sol hanya 25 byte) — tidak di-retry agresif; registry
  sudah terkonfirmasi via eth_call jadi tidak menghalangi.

## 3. Route 6b Odaily + PANews — HTTP 200, 0 hit
- run-2026-11-10-0901-odaily.html (259.485 byte), run-2026-11-10-0901-panews.html (121.447 byte).
- Grep "free mint" / "Agent ID" / "AgentID" / "免费铸造" / "免费份额": **0 hit di keduanya.**

## 4. Route 3 sweep (browser.search, EN + ZH)
- NOVRA 0x75Ac13cF23a8dccC703D1496138251FD7f247890 (thecolony.ai): sudah di snapshot (8 hit);
  AirdropBuzz menyatakan alokasi gratis NOVRA sudah habis. Bukan baru.
- Razor Agent (razoragent.fun): NOT DEPLOYED, genesis belum mulai — upcoming saja, tanpa kontrak.
- AgentID ETH (agentideth.com): Ethereum L1, di luar scope BSC.
- AGENT MAO: sudah dikenal, situs 530/paused. Bukan baru.
- Lenx Agent Pass 0x6e252e3a3584bd6a64c103e4edfa761f6335980f: sudah di snapshot + seen. Bukan baru.
- Black Hole 0xC84E8281153387e9f35c99cE316075E3c38Dd388, AGENT ID card 0x486d0947cAa3d70c19e38f6C789489d39291E9e7,
  Subsonic Tribe 0x65DDB3E337c12E5964ead6Cb9b6469203EF4caf1: sudah di snapshot. Bukan baru.
- UMBRA Agents 0x9C0309dC71F89d7f4F0b55d934213C28F10C9e23 (post 27 Okt, ~14 hari lalu): TIDAK ada di
  snapshot/seen/hot — tapi umurnya sudah jauh > 48 jam dari sumber post, jadi bukan lead baru;
  dicatat saja sebagai proyek lama yang belum terlacak.
- Laser Agents 0x3ed6b33f9ea597a6f210b5e70029ddd92e93ae85: sudah di daftar excluded. Bukan baru.
- **Tidak ada proyek/kontrak baru yang agent-shaped dari sweep ini.**

## 5. Bridge scan-bridge.json (read-only, tidak ditulis)
- mtime TIDAK BERUBAH: 2026-11-08 18:21:53 UTC — sama seperti catatan run 0831.
- 116 kontrak; same_owner_discarded=true: **7** (sama seperti run 0831).
- Metode hitung "tidak di snapshot": substring terhadap teks snapshot = **2** alamat
  (0x636fdfa9bc3db42c690c09e87b9017d05b36c743 — Unnamed ERC20, first_seen run-70;
  0xf75cf7f9be878cf487d5aeacd5560d96737b63f8 — ETHBack_Dividen_Track, first_seen run-123;
  keduanya gate website_no_pointer_found, sudah dikenal sejak 6–8 Nov, bukan temuan baru).
  Catatan: angka "8" di run 0831 tidak bisa direproduksi dengan metode ini; flag
  in_freebacot_snapshot=false di bridge sendiri = 109 (flag bridge basi sejak 8 Nov, bukan perubahan).
  Tidak ada perubahan vs run 0831: bridge tidak berubah, tidak ada temuan pelengkap scan baru.

## Kesimpulan
- **Tidak ada kandidat lead baru yang lolos untuk dipromosikan dari leg discovery run ini.**
- Satu temuan bentuk S1 baru (ConcheryPass) gugur di kaki umur (launch terverifikasi 2026-10-21, >48 jam).
- Satu observasi follow-up: SEVENFOLD (treasury 0x4ca7...) — alamat mint 0x3fbe... terpotong di front page Boltbook.
- File-file lain ber-prefix run-2026-11-10-0901- di direktori ini (grove-check, preflight, reread, special2)
  BUKAN dari pekerja leg discovery ini — ditulis paralel oleh worker run utama.
