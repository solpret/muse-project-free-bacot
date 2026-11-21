# MANIFEST — muse-project-free-bacot

- **Tanggal:** 21 November 2026
- **Repo publik:** `muse-project-free-bacot` — https://github.com/solpret/muse-project-free-bacot
- **Ukuran:** 166 MB (174.142.129 byte), 16.829 file
- **Cakupan:** Project Free Bacot — pencarian rutin free-mint NFT (track A),
  klaim token gratis (track B), share sale fungible (track C), eksekusi
  FCFS + auto-sell, dan AGC.

## Isi

| Bagian | Isi |
|---|---|
| `goals/pencarian-rutin-project-free-mint/` | Goal utama: GOAL.md, files/, crons/, briefs/, agent_notes/, references/, hidden_files/ (skrip leg per-run — riwayat metode) |
| `goals/agc-daily-claim-and-swap/` | Klaim + swap harian AGC (Mode A refund, Mode B LP) |
| `goals/colo-mint/`, `goals/safu-bots-3073-mint-and-listing/`, `goals/agentsestates-4611-listing/`, `goals/unlisted-nft-floor-minus-5-listings/`, `goals/unlisted-nft-transfer-to-second-wallet/` | Goal mint/listing NFT terkait |
| `narrative-pulse-scripts/` | Skrip tracked-wallet scan (.py/.sh/.md saja, tanpa data/state) |
| `fast_exec/` | FCFS loop (`fcfs_fast.py`), `fast_rpc.py`, auto-sell Stars, watchdog |
| `asset-sell-watch/` | Watch penjualan aset + pending swaps |
| `nft-rarity-inventory.md` | Inventaris rarity NFT yang sudah dicek |
| `analysis/` | 12 file analisis root: screening-routes, floor/venue/reprice check, rarity, Boltbook templates, wallet3 airdrop check, chip404 route research |
| `skills/` | free-mint-discovery, deep-screening-tools, early-project-screening, fastmint-fcfs |

## Yang sengaja TIDAK ikut
- `hidden_files/`: snapshot (`onchain-snapshot.json`), run-JSON historis,
  log, DB, file >1 MB — dibuang. Yang ikut hanya *.py/*.sh/*.json/*.md <1 MB.
- `fast_exec/`: *.log, *.bak, state runtime (`*state*.json`,
  `armed-*.json`), file *.env — dibuang.
- File bersama (AGENTS.md, MEMORY.md, CHALLENGE.md, skills/connectors
  bersama) TIDAK disalin ke sini — lihat `common/` di repo
  `muse-project-common`.

## Catatan ukuran
154,3 MB dari 174,1 MB adalah `goals/pencarian-rutin-project-free-mint/
hidden_files/` — ribuan skrip leg per-run (mayoritas varian unik, bukan
duplikat). Itu riwayat metode, bukan tumpukan sampah; snapshot + run-JSON
sudah dibuang (lihat atas). Ukuran turun dari 300 MB (20 Nov) karena
pembersihan live: range backfill lama + snapshot onchain-scan + run-output
asset-sell-watch lama ikut terhapus (1.912 file).

## Pembaruan 2026-11-21 (sejak 20 Nov)
- 501 file baru, 21 berubah, 1.912 dihapus (2.434 path).
- Baru: 434 file hidden_files/ goal utama (236 skrip leg .py, 121 runlog
  .md, 77 JSON ringkasan 20–21 Nov) + 48 file asset-sell-watch
  (pending_check 20–21 Nov) + 15 skrip narrative-pulse + state AGC/Agio.
- Cron free-mint-search pindah minutely @30m → hourly @2h (perintah user
  20 Nov, hemat Ankr); file cron lama dihapus, file baru ditambah.
- Dihapus mengikuti live: 1.183 file hidden_files/ (range backfill lama
  ~731, snapshot onchain-scan 283, .bak state ~130 — efek skip ~623.854
  blok backfill basi 20 Nov) + 728 file asset-sell-watch (run-output lama:
  pending_check/targeted/sale_state/dead-sweep-check) + cron lama di atas.
- State ringkasan baru yang ikut: `hot-leg-reported.json`,
  `trackc-*-candidates.json`, `trackc-check-*-results.json`,
  `onchain-scan-state.json` (update).
- Tetap dibuang mengikuti kebijakan 20 Nov: 30.386 file live —
  26.579 JSON/log intermediate run-per-run hidden_files (reread/sourcify/
  feed/probe/bridge/verify, 1,2 GB), 3.749 file scan-runs/data/state
  narrative-pulse, 17 file log/bak/state/armed/env fast_exec, 26 file
  .log/.txt AGC, 13 file .env/cache/log skills, 3 file .log
  asset-sell-watch. State >1 MB (`hot-leg-seen.json` 5,4 MB,
  `registry-watch-state.json` 12,6 MB, `onchain-scan-seen.json` 1,06 MB)
  juga tidak ikut.
- Pemecahan repo: TIDAK diperlukan — tree 166 MB < ~900 MB; tidak ada
  file >90 MB (terbesar di commit ini 765 KB).

## Pembaruan 2026-11-20 (sejak 17 Nov)
- Goal baru: `goals/agio-free-mint-watch/` (192K) dan
  `goals/pxio-miner-auto-claim/` (12K).
- 16 file berubah: state asset-sell-watch + fast_exec, cron free-mint
  (search/hot-leg), GOAL.md pencarian rutin, `nft-rarity-inventory.md`
  (BAISHOU 19 Nov: 168.000.000 token, tx terverifikasi).
- 3.149 file baru, mayoritas skrip leg per-run 18–19 Nov di hidden_files/
  (riwayat metode) + state ringkasan (onchain-scan, registry-watch,
  grove-watch, scan-gap-watch).
- Dibersihkan mengikuti kebijakan 17 Nov (bukan karena batas repo):
  ~21.000 JSON dump run-per-run hot-leg (321 MB) + snapshot/log/DB +
  state runtime fast_exec — dibuang; hanya skrip leg (.py/.sh/.md) +
  JSON ringkasan yang ikut.
- Pemecahan repo: TIDAK diperlukan — tree 300 MB < ~900 MB; tidak ada
  file >90 MB.

## Audit rahasia
Bersih (20 Nov 2026, `audit-secret-2026-11-20.txt` di folder induk,
ripgrep 14.1.0, 16 pola): 0 private key, 0 sk-, 0 Bearer asli,
0 keypair Solana, 0 file .env — layak repo publik.

Audit 21 Nov 2026 (522 file berubah): 0 private key, 0 sk-, 0 Bearer,
0 keypair Solana, 0 file .env, 0 token/API-key — dan email pribadi
diredaksi 43× di `narrative-pulse-scripts/holder-watchlist.md`
(baru muncul di versi 21 Nov; 0 di HEAD) menjadi
`[email-pribadi-diredaksi]` sebelum push; file live tidak diubah.
Catatan: alamat wallet agent sudah ada di 7.759 file tracked di HEAD
(publik sejak backup sebelumnya; dipakai sebagai target query di skrip
probe) — kemunculan di 230 file commit ini adalah alamat yang sama,
bukan paparan baru; redaksi sepihak di file baru saja tidak menutup
paparan itu dan akan merusak skrip. Keputusan soal alamat wallet
diserahkan ke koordinator (redaksi repo-wide atau pengecualian eksplisit).
