# Discovery run Free Bacot 2026-11-10 09:31 WIB (tag 0931) — ringkasan leg discovery (READ-ONLY)

Tidak ada preview/mint/claim/swap/sign. Snapshot/seen/bridge tidak ditulis oleh leg ini.

## 1. Boltbook route 2 — HTTP 200, dua halaman tersimpan
- EN: run-2026-11-10-0931-boltbook-en.html (45.362 byte)
- ZH: run-2026-11-10-0931-boltbook-zh.html (45.400 byte)
- Alamat unik: EN 14, ZH 12, gabungan 14. Baru vs front page run 0901: 10 alamat.
- **0 alamat BARU vs snapshot + onchain-scan-seen.json + hot-leg-seen.json.**
  - 0x4ca7... = SEVENFOLD (sudah di snapshot; watchlist-only run 0901).
  - 0x4d90... = THYRK (sudah di snapshot; early lead).
  - Sisanya sudah di snapshot/seen/hot-leg-seen.

## 2. Sourcify feed route 5a — HTTP 200
- Feed: run-2026-11-10-0931-sourcify-feed.json (20 kontrak, verifiedAt 2026-11-10T02:33:27Z s.d. 02:43:04Z).
- **20 kontrak BARU vs feed run 0901** (jendela feed bergeser penuh dalam 30 mnt).
- ABI diambil via `?fields=abi`. Shape-check 20 kontrak:
  - Batch pertama (5 worker, timeout 30 dtk): 15 OK, 0 S1/S2; 5 timeout (URLError timed out) — Sourcify lambat run ini.
  - Retry 5 timeout (sekuensial, timeout 60 dtk): 5/5 berhasil, 0 S1/S2.
  - **Total: 20/20 dicek, 0 S1, 0 S2.** File: run-2026-11-10-0931-feed-shape.json + -retry.json.
  - 4 dari 5 retry adalah template yang sama (agentIds, mintWithAgentTokenId, costOf, price) — mint + quote ADA tapi TANPA free view dan TANPA agent_ref di ABI → bukan S1; kemungkinan paid-only factory family, bukan lead.
  - 1 retry (0x94F8...) = token pajak/dividen (tanpa mint) → NO-HIT.
  - 8 dari 20 sudah dicoba hot-leg 0934 (semua timeout di sana juga); retry run ini menyelesaikan semuanya.

## 3. Route 6b Odaily + PANews — HTTP 200, 0 hit
- run-2026-11-10-0931-odaily.html (259.440 byte), run-2026-11-10-0931-panews.html (124.912 byte).
- Grep "free mint" / "Agent ID" / "免费铸造" / "免费份额" / "agentid": **0 hit di keduanya.**

## 4. Route 3 sweep (browser.search, EN + ZH)
- MOLT AGENT 0x4B8150f1a258cD3CE2300fAf682432c52ca48Fc1 (thecolony.ai): sudah dikenal; free pool HABIS (dilaporkan backfill 05:10 WIB 10 Nov). Bukan baru.
- AgentVOLT (agentvolt.site): NFT 0xe0deb1a792eebd9cba7fd74b70a283bfa2630771 — free mint ENDED (5.000/5.000, 100%), sudah di snapshot (bridge + round 1). Bukan baru.
- Cilok Cats: sudah di snapshot sebagai checked-not-lead-age-excluded (run 1501, 2026-11-02); gate 10 BNB deadline 4 Nov sudah lewat. Bukan baru.
- Lenx Agent Pass 0x6e252e3a3584bd6a64c103e4edfa761f6335980f: sudah di snapshot, SOLD OUT (dilaporkan run 0901). Bukan baru.
- AGC (vctria.com): sudah dikenal, scope Modal Bacot. Bukan lead Free Bacot.
- AGENT MAO: paused (situs 530), sudah dikenal. Bukan baru.
- **Tidak ada proyek/kontrak baru yang agent-shaped dari sweep ini.**

## 5. Bridge scan-bridge.json (read-only, tidak ditulis)
- mtime TIDAK BERUBAH: 2026-11-08 18:21:53 UTC — sama seperti run 0901/0831.
- 116 kontrak; same_owner_discarded=true: **7** (sama seperti run 0901).
- 8 kontrak tidak di snapshot (sama seperti run 0901): Ore (paid ERC20), 2x ETHBack_Dividen_Tracker, Ikigai (ERC20, 1 entity), AGC (ERC20), Krillfarm (same_owner_discarded), Panda Emoji Pack (ERC20), Unnamed ERC20 — semuanya "finding", TIDAK ada yang memenuhi tier Free Bacot.
- **0 promosi bridge.**

## 6. SEVENFOLD website — TERVERIFIKASI run ini (methods H/I/G)
- contractURI() = https://sevenfold-genesis.pages.dev/meta/collection.json (external_link = site yang sama); tokenURI(1) = https://sevenfold-genesis.pages.dev/meta/unrevealed.json.
- /llms.txt (801 byte, HTTP 200) mencetak: "Contract address: 0x4ca724a354db4f743607ecc1a5f117b2e617c8ae" — kontrak sale persis.
- /agent.json (47.538 byte, HTTP 200) mencetak: contract 0x4ca724a354db4f743607ecc1a5f117b2e617c8ae + token MORROW 0x1f4e976b899df67cB4F69BB21aFa0Aee274153Fe + canonicalSite + mint function + free routes.
- Front page HTML (34.918 byte) sendiri TIDAK mencetak alamat kontrak (SPA JS) — tapi /llms.txt + /agent.json di host yang sama mencetaknya → website evidence per strict print standard.
- /skill.md gagal (000); /launch.json mengembalikan SPA HTML; /api/stats + /api/verify kosong (200 0B).
- X account proyek masih UNVERIFIED (opsional, tidak pernah memblokir).
- **Gate SEVENFOLD kini LOLOS; tinggal kaki 25% (free 700/3000 = 23,3% saat prio6).**
- File: run-2026-11-10-0931-sevenfold-*.json/.html/.txt/.py.
