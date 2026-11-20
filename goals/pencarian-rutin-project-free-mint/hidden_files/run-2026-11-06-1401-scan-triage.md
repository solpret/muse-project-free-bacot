# FREE BACOT run 2026-11-06 14:01 WIB — LEG 4 scan + triage + LEG 5c

**HASIL: SCAN GAGAL — triase + leg 5c DILEWATI (tidak ada JSON untuk ditriase).**

## Pre-flight (wajib, fast-fail)
- Script: `run-2026-11-06-1401-preflight.py` (salinan template run 1331, tidak diubah).
- Hasil: **OK, 6,8 dtk** — head 131965546, chunk 50 blok 131965497–131965546, 326 logs.
- Log: `run-2026-11-06-1401-preflight.log`. Ankr lewat proxy env yang sudah ada; no_proxy tidak pernah di-set.

## Scan (route 4)
- Perintah: `timeout 780 python3 -u onchain_nft_scan.py --chunk 50 --blocks 1000 --out onchain-scan-2026-11-06-1401.json`
- Window: **131964584–131965583** (1000 blok, head saat scan 131965583), 20 chunk @ 50 blok.
- Log: `run-2026-11-06-1401-scan.log` (flush per chunk, terverifikasi muncul saat chunk selesai).
- Fase chunk: **SELESAI 20/20** dalam ~5 mnt (mulai 07:04:22 UTC, chunk terakhir 07:09:37 UTC).
  Hitungan akhir dari log: **ERC721 147, ERC1155 4, ERC20-mint 449**.
- Fase enrichment (eth_getCode + Sourcify ABI + name/symbol per kontrak, tanpa progress logging):
  **STALL** — tidak ada output log baru sejak 07:09:37 UTC; proses masih hidup 07:13:12 UTC
  dengan CPU hanya ~2 dtk setelah ~8 mnt 50 dtk elapsed (blocked I/O, pola sama persis dengan
  run 1301 dan 1331). Sesuai instruksi tugas (kill bila enrichment tanpa output >3 menit),
  proses di-kill (SIGTERM) 07:13:25 UTC. **SCAN_EXIT=143. TIDAK ADA JSON yang ditulis**
  (`onchain-scan-2026-11-06-1401.json` tidak ada). Ini kegagalan ke-3 berturut-turut
  di fase enrichment pasca-chunk (1301: SCAN_EXIT=124/timeout 780; 1331: proses hilang
  karena runtime restart setelah ~4 mnt stall; 1401: kill manual setelah 3 mnt 35 dtk stall).
- Baris log terakhir: `chunk 131965534-131965583: ERC721 contracts so far 147, ERC1155 4, ERC20-mint 449`

## Triase first-seen — DILEWATI
Tidak ada output scan (JSON) untuk ditriase. Jumlah true first-seen: **tidak diketahui**
(hanya hitungan kontrak per chunk yang tersisa di log; daftar alamat hilang bersama JSON).
Tidak ada EARLY lead / PAID-ONLY / NOT agent-shaped yang dapat diputuskan dari run ini.
Tidak ada state file yang ditulis oleh worker ini (snapshot, scan-state, scan-seen,
track-c-scan-checked, hot-leg-seen semuanya tidak disentuh).

## Leg 5c — DILEWATI
Tidak ada `erc20_mint_contracts_list` (berasal dari scan JSON) untuk di-shape-check.
Tidak ada alamat baru yang dicatat; file `run-2026-11-06-1401-trackc-5c.json` tidak dibuat
(tidak ada yang bisa dicatat — bukan karena 0 kandidat, melainkan karena inputnya hilang).

## Gap yang belum ter-cover
- Window run ini **131964584–131965583: data HILANG** (hanya hitungan chunk-line yang tersisa;
  alamat kontrak + mint count per kontrak tidak terselamatkan).
- Backfill gap dari watermark bersama 131933548: blok **131933549–131964583 (~31.035 blok)**
  masih belum ter-cover oleh scan utama run ini (backfill paralel terpisah mungkin sudah
  memajukan sebagian — watermark bersama saat run ini dibaca 07:13:41 UTC masih 131933548;
  parent yang memfinalisasi state yang berwenang menyatakan posisi akhirnya).
- Total rentang belum terverifikasi oleh leg ini: 131933549–131965583.

## Catatan untuk parent
- Pola kegagalan kini 3x berturut-turut di fase enrichment yang sama. Rekomendasi yang
  sudah dibawa sejak run 1301 tetap berlaku dan makin mendesak: fase enrichment butuh
  progress logging per kontrak + penulisan partial JSON (atau pemisahan chunk-capture
  dari enrichment) — kalau tidak, setiap stall enrichment terus membuang 1000 blok data
  window yang chunk-nya sudah selesai dengan sukses.
- Tidak ada retry (aturan run-once). Tidak ada preview/mint/transaksi apa pun di run ini.
