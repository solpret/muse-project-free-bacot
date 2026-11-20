# Hot-leg run 2026-11-18 02:29 WIB

- Sourcify feed: 20 kontrak, 1 baru vs seen — 0xF3Fba2fa64B178bDBe4AC1564A9fcE8F8a05B191 (top, verifiedAt 2026-11-17T19:30:41Z). Shape-check: S1=false, S2=false, has_mint=false, has_quote=false, free_views=[], agent_ref=false, is_token=false, 34 fns — BUKAN sale shape. Dicatat di hot-leg-seen.json, bukan lead.
- Boltbook EN (45.128 byte, HTTP 200) + ZH (43.455 byte, HTTP 200): 11/11 alamat, 0 baru vs seen. Tidak ada shape-check baru. Figures: PXIO sold out 16.666/16.666; FIND exp39 136/300 (kontrak 0x4158B701EaA30E8FaDBaA526F70780A38318c1C4 sudah dikenal, bukan lead hot-leg).
- Bridge scan: 116 kontrak, 0 di luar snapshot, 7 same_owner_discarded. Tidak ada temuan pelengkap untuk promosi.
- Leg 4 reread: blok 134176049, elapsed 73,5 dtk, 0 chunk error. Satu-satunya perubahan vs 02:24: PunchCard totalSupply/totalMinted 1308→1309 dan freeMinted 1286→1287 (+1) — free 23,2%, slot user terbuka (mintPriceFor 0, mintedCount 0), masih jauh di bawah bar kandidat 50% dan strong lead >70%. Bukan perubahan tier, dicatat di run log saja.
- Threshold check: AGCLUB 59,1%, Matrix 58,9%, PIXELFROGS 15,1%, AgentBubble 84,3% — AgentBubble di atas 70% TAPI launch age masih UNVERIFIED (tidak ada saleStart/mintOpensAt view, dibawa dari run 02:14) → TIDAK ada promosi strong lead. Stromboat flat 142/667 = 21,3%, slot user terbuka. binanceai-mint pending claim tidak berubah (launched 0, failed 1, isRefundPhase 1 — fase refund sudah dilaporkan 2026-11-02). bsccat + pepe tidak berubah.
- Poffzi FCFS: tidak ada proses berjalan (tidak ada sale di-arm).
- Eksekusi: tidak ada — tanpa preview, mint, atau klaim. Diam sesuai aturan (tidak ada lead/kandidat/pending/perubahan tier baru).
- File: hidden_files/hot-leg-run-2026-11-18-0229.json, hidden_files/hot-leg-run-2026-11-18-0229-reread.json, hidden_files/hot-leg-2026-11-18-0229-run.py, boltbook html EN/ZH.
