# free-mint-hot-leg run 2026-11-18 04:24 WIB — runlog

- Elapsed 151,9 dtk (melewati target <2 mnt — feed 5 kontrak baru + leg 4 diperluas 5 item baru), blok 134191951. Tanpa eksekusi (read-only; tanpa preview/mint/klaim).
- Leg 1 Sourcify feed: 20 kontrak, 5 BARU (top terverifikasi 2026-11-17T21:28:25Z):
  0xbc9D18408CEe5Ef510a5016e64C383D55CcF2f83 (mint ada, tanpa quote/free/agent, 8 fn),
  0x0e4D042F2dBdeF32496ABAf1E455D6431727B610 (tanpa mint/quote/free/agent, token, 10 fn),
  0xEd4E75162063788314b312ff8Cdad602c449f620 (mint ada, tanpa quote/free/agent, 8 fn),
  0xc579A233cB9d2544c67CEC0710b086b72537FcbB (tanpa mint/quote/free/agent, 32 fn),
  0x1243B23E052089708E49527AffcEf27b991f7777 (ERC-20 biasa, tanpa mint/quote/free/agent, 22 fn).
  Semuanya BUKAN S1/S2. Dicatat di hot-leg-seen.json (16148 -> 16154) sebagai checked-not-sale-shape.
  Leg 3: tidak ada hit S1/S2, tidak ada verifikasi on-chain lanjutan.
- Leg 2 Boltbook EN+ZH (boltbook.fun): HTTP 200 keduanya (EN 44.425 byte, ZH 42.774 byte),
  1 alamat "baru" di tiap halaman: 0x269299d3bd13c7e92c2ba740eac0501527869424 — TERVERIFIKASI
  artefak regex: 66-char tx hash 0x269299d3...4053abae92208fbda6bad5756 ada di HTML; dicatat
  di hot-leg-seen.json sebagai checked-not-contract, TIDAK pernah shape-check. 0 lead baru.
- Leg 4 re-read vs run 0419 (149 calls, 0 chunk error, 0 null yang butuh retry): sebagian besar
  "perubahan" vs 0419 adalah pemulihan null RPC run 0419 ke nilai 0414 (AGCLUB, Ledgera,
  BoldLeonidas, RaceAgents, CPASS, Stromboat, binanceai-mint, bsccat) — BUKAN perubahan state.
  Perubahan nyata terverifikasi: AgentNOVA totalSupply 750 -> 751 (+1 mint). Tidak ada yang
  melewati ambang tier.
- Item baru di focus set run ini (baseline pertama, tanpa pembanding 0419):
  Lumenhold freeClaimed 1248/1500 = 83,2% (snapshot 04:01: 1246 -> +2), totalSupply 1253;
  STOCK AGENT freeLeft 565/1111 = 49,1% free (snapshot 04:01 totalSupply 543 -> 546), slot user
  terbuka (quote 0, freeMintedByWallet 0, balance 0); ARKT totalMinted 323 FLAT, hasClaimed(user) 0;
  AgentEcho totalSupply 284 (snapshot 04:01: 281 -> +3); Kageveil totalSupply/normalMinted 39 FLAT.
- Threshold: PunchCard 23,3%, AGCLUB 59,3%, Matrix 59,2%, PIXELFROGS 15,1%, STOCK AGENT 49,1%
  (<50% kandidat, <70% strong lead), Lumenhold 83,2% dan AgentBubble 84,4% TAPI umur launch
  keduanya masih UNVERIFIED (Lumenhold: velocity gagal + tanpa situs; AgentBubble: tanpa
  saleStart/mintOpensAt view, dibawa dari run 0204) -> TIDAK ada promosi strong lead.
- Verifikasi pasca-run (batch kecil 6 calls, 2 endpoint, keduanya sepakat):
  DRAGON freeMinted 1000 / totalMinted 1005 / mintOpen revert / balanceOf(user) 1 — SAMA dengan
  0414; null di batch utama 0419 + 0424 = artefak drop batch RPC, BUKAN perubahan state.
  Ledgera totalSupply 2709 / freeClaimed 2702 — SAMA dengan 0414; klaim verifikasi pasca-run 0419
  ("2717") TIDAK terreproduksi di 2 endpoint -> nilai 2717 itu bacaan salah, Ledgera FLAT sejak 0414.
- Pending klaim binanceai.fun: launched=0, failed=1, isRefundPhase=1, totalShares 3110,
  tokenClaimed(user)=0 — tanpa perubahan; sudah dilaporkan sekali 2026-11-02, DIAM.
- bsccat: freeMinted 520 (tidak berubah sejak 0414); view lain revert seperti sebelumnya.
  pepe: tanpa perubahan (freeMinted 500, soldShares 501, hasMinted(user) 1).
- Bridge scan (read-only): 116 kontrak, 0 di luar snapshot, 7 same-owner-discarded.
  Tidak ada kontrak bridge yang baru memenuhi tier / promosi / perubahan.
- Poffzi FCFS: tidak ada proses berjalan (NO PROCESS FOUND).
- Hasil: TIDAK ADA lead/kandidat/pending/perubahan/promosi baru -> DIAM (tanpa laporan chat).
- File run: hot-leg-2026-11-18-0424-run.py, hot-leg-run-2026-11-18-0424.json,
  hot-leg-run-2026-11-18-0424-reread.json, hot-leg-2026-11-18-0424-boltbook-en/zh.html.
