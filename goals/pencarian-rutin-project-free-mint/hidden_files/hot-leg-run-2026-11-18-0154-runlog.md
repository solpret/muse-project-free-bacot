# Hot-leg run 2026-11-18 01:54 WIB

- Sourcify feed: 20 kontrak, 7 baru vs seen (top 0x045BC69EBFFEc8FFb2398e4aCeb25A0C285c1917, verifiedAt 2026-11-17T18:56:07Z). Shape-check ketujuhnya: S1 false, S2 false semua — bukan sale shape. Dicatat di hot-leg-seen.json (total seen 16077).
- Boltbook EN (44.776 byte) + ZH (43.097 byte): 8 alamat, 0 baru.
- Bridge scan: 116 kontrak, 0 di luar snapshot, 7 same_owner_discarded. Tidak ada temuan pelengkap untuk promosi.
- Leg 4 reread: blok 134171480, elapsed 42,1 dtk, 0 chunk error. Perubahan vs 01:49: RaceAgents totalSupply/freeMinted 633→634 (+1); Stromboat freeMinted 84→92 (+8 dalam 5 menit, totalMinted 84→92).
- Stromboat (0xC3CB4dF5256c8429Eab306E924BF6E3E6c72163d): freeMinted 92/667 = 13,8%, totalMinted 92, paidMinted 0, mintOpen 1, slot user masih terbuka (freeMintedBy 0, balanceOf 0). Velocitas melambat vs run 01:49 (+67/5 mnt) dan masih jauh di bawah bar kandidat track-A 50% dan strong lead >70%. Gate website sudah dinilai GAGAL di run 01:49 (metode A: pencarian alamat kontrak tanpa situs proyek). Tetap watchlist-only per body leg (3): TIDAK dilaporkan sebagai lead, TIDAK di-preview/di-mint.
- Threshold check: PunchCard free 23,1% (slot user terbuka, mintPriceFor 0, mintedCount 0), AGCLUB 59,0%, Matrix 58,9%, PIXELFROGS 15,1%, AgentBubble 84,3% — AgentBubble di atas 70% TAPI launch age masih UNVERIFIED (tidak ada saleStart/mintOpensAt view, dibawa dari run 01:49) → TIDAK ada promosi strong lead. binanceai-mint pending claim tidak berubah (launched 0, failed 1, isRefundPhase 1 — fase refund sudah dilaporkan 2026-11-02). bsccat + pepe tidak berubah.
- Poffzi FCFS: tidak ada proses berjalan (tidak ada sale di-arm).
- Eksekusi: tidak ada — tanpa preview, mint, atau klaim. Diam sesuai aturan (tidak ada lead/kandidat/pending/perubahan tier baru; perubahan Stromboat + RaceAgents dicatat di run log saja, mengikuti preseden run 01:49).
- File: hidden_files/hot-leg-run-2026-11-18-0154.json, hidden_files/hot-leg-run-2026-11-18-0154-reread.json, hidden_files/hot-leg-2026-11-18-0154-run.py, boltbook html EN/ZH.
