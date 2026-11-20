# Hot-leg run 2026-11-18 02:09 WIB

- Sourcify feed: 20 kontrak, 2 baru vs seen (top 0x712f69345343B8b7414a24178373f9E647f51564, verifiedAt 2026-11-17T19:10:08Z; kedua 0x1D73dceCC18F9F604989AbC53632CDDE7b5dF35E). Shape-check: S1 false, S2 false untuk keduanya — bukan sale shape (token, tanpa mint/quote/free view/agent ref). Dicatat di hot-leg-seen.json (total seen 16093).
- Boltbook EN (44.014 byte) + ZH (42.170 byte): 4–5 alamat, 0 baru.
- Bridge scan: 116 kontrak, 0 di luar snapshot, 7 same_owner_discarded. Tidak ada temuan pelengkap untuk promosi.
- Leg 4 reread: blok 134173166, elapsed 21,2 dtk, 0 chunk error. Perubahan vs 02:04: AGCLUB freeMinted 524→525 (+1), PunchCard freeMinted 1284→1285 (+1), Stromboat freeMinted 104→116 (+12 dalam 5 menit; totalMinted 104→116).
- Stromboat (0xC3CB4dF5256c8429Eab306E924BF6E3E6c72163d): freeMinted 116/667 = 17,4%, totalMinted 116, paidMinted 0, mintOpen 1, slot user masih terbuka (freeMintedBy 0, balanceOf 0). Velocitas naik vs run 02:04 (+2/5 mnt) tapi masih jauh di bawah bar kandidat track-A 50% dan strong lead >70%. Gate website sudah dinilai GAGAL di run 01:49 (metode A: pencarian alamat kontrak tanpa situs proyek). Tetap watchlist-only per body leg (3): TIDAK dilaporkan sebagai lead, TIDAK di-preview/di-mint.
- Threshold check: PunchCard free 23,1% (slot user terbuka, mintPriceFor 0, mintedCount 0), AGCLUB 59,1%, Matrix 58,9%, PIXELFROGS 15,1%, AgentBubble 84,3% — AgentBubble di atas 70% TAPI launch age masih UNVERIFIED (tidak ada saleStart/mintOpensAt view, dibawa dari run 02:04) → TIDAK ada promosi strong lead. binanceai-mint pending claim tidak berubah (launched 0, failed 1, isRefundPhase 1 — fase refund sudah dilaporkan 2026-11-02). bsccat + pepe tidak berubah.
- Poffzi FCFS: tidak ada proses berjalan (tidak ada sale di-arm).
- Eksekusi: tidak ada — tanpa preview, mint, atau klaim. Diam sesuai aturan (tidak ada lead/kandidat/pending/perubahan tier baru; perubahan Stromboat/AGCLUB/PunchCard dicatat di run log saja).
- File: hidden_files/hot-leg-run-2026-11-18-0209.json, hidden_files/hot-leg-run-2026-11-18-0209-reread.json, hidden_files/hot-leg-2026-11-18-0209-run.py, boltbook html EN/ZH.
