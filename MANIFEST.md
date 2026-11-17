# MANIFEST — muse-project-free-bacot

- **Tanggal:** 17 November 2026
- **Repo publik:** `muse-project-free-bacot` — https://github.com/solpret/muse-project-free-bacot
- **Ukuran:** 271 MB (253.178.443 byte), 15.090 file
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
254 MB dari 271 MB adalah `goals/pencarian-rutin-project-free-mint/
hidden_files/` — ribuan skrip leg per-run (mayoritas varian unik, bukan
duplikat). Itu riwayat metode, bukan tumpukan sampah; snapshot + run-JSON
sudah dibuang (lihat atas).

## Audit rahasia
Bersih (17 Nov 2026, `audit-secret-2026-11-17.txt` di folder induk):
0 private key, 0 sk-, 0 Bearer asli, 0 keypair Solana, 0 file .env —
layak repo publik.
