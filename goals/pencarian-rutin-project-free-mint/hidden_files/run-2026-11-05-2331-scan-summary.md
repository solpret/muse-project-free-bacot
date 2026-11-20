# FREE BACOT run 2331 — route 4 on-chain scan + triage + route 5c (Subagent A)

- Run: 2026-11-05 23:31 WIB (scan 23:45–00:04 WIB, ~19 menit; triage s.d. ~00:15 WIB)
- Scan: `python3 onchain_nft_scan.py --chunk 50 --out onchain-scan-2026-11-05-2331.json --blocks 2000`
- Head saat mulai: 131851071 (watermark lama 131842907 → window 8164 blok > cap 2000)
- Window ter-scan: 131849106–131851105 (2000 blok terbaru)
- Gap dilewati: 131842908–131849105 (6198 blok). Gap kumulatif sejak run 1831 ~33.461 blok tak ter-scan.
- Ankr calls: 80 (scan) + 5 (triage mint-tx via ankr_logs module) = 85. Errors: 0.
- Hasil scan: 279 kontrak NFT, 520 kontrak ERC20.
- Dedupe (case-insensitive, seen nested `contracts` + top-level keys + snapshot): 269 sudah di seen, 0 hanya di snapshot, **10 first-seen sejati**.
- Seen file diperbarui (nested `contracts` 9250 → 9260, key lowercase). Watermark diperbarui ke 131851105. Snapshot utama TIDAK ditulis.

## Triage first-seen (10)

**EARLY LEAD — 1:**
- **Moonfall (MOONFALL) 0x4232308c31927e493e96FdB05134Fa39C26c24D0** — 21 mints / 11 minters di window, blok 131849595–131850981. Bytecode (eth_getCode, 21784 bytes) mengandung alamat registry Agent ID 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; mint tx value 0 BNB (gratis); totalSupply()=26, MAX_SUPPLY()=1001 (2,6%); selector mint 0x484b973c ada di code. Caveat: Sourcify NOT verified (404) — nama fungsi mint tak teridentifikasi; umur peluncuran UNVERIFIED (5 mint pra-window, kemungkinan di gap yang dilewati); free-quota views tak diketahui; belum ada cek gate website/X (tugas subagent lain/parent). Early lead TIDAK PERNAH di-preview/mint.

**NOT-EARLY paid-only — 8:**
- Synthetic Ghost 0xA224bb6B4B89D9c22C140Ea8d37D2290E99AECAc — template agent-mint terverifikasi (AGENT_REGISTRY on-chain = registry), PRICE = quote(1) = 0,0005 BNB, 1 mint, tanpa fungsi free.
- Delta Yeti Agent 0x282885b50ee2B8e539d695f859A87B1A18F2B66e — sama, PRICE 0,0005 BNB, 1 mint.
- Void Quokka Agent 0x4D0e44744baF36Ad27f736BA023bdFbB0B9823Eb — sama, PRICE 0,0005 BNB, 1 mint.
- Toucan Play 0x5ABe8974d554Ea0c797fBC4c6B01EA4446616B2f — price() = 0,0002 BNB, 5 mints / 5 minters.
- jelly.exe 0x807E86F6d1bc8fc5E8f53052DAC5d379D4efc120 — price() = 0,0002 BNB, 1 mint.
- Not Financial Advice·39 0x2Fb4598Cc4c0758d9a541CAe813E81f0b138024A — mint tx value 0,001 BNB, 1 mint (minter sama dengan Cope Harder).
- Cope Harder·39 0xD9A49dF66443bA35e7A96bEE63b0B8913F47c22c — mint tx value 0,001 BNB, 1 mint.
- SENSHI 0x759a2c237ee454004aA1029622483954a248c320 — mint tx value ~0,0007 BNB, 1 mint.

**NOT-EARLY shape unverified — 1:**
- BEWORK 0x78eDD42101e889cC3Ce4B24CBb0Fc774082BcAee — mint tx value 0 BNB (free-value) tapi TANPA bukti agent-shape (no registry bytes, Sourcify 404, fungsi mint tak teridentifikasi); 2 mints / 1 minter.

## Route 5c

- ERC20 list 520; mint_count >= 10: 57; sudah terperiksa sebelumnya: 51; baru di-shape-check run ini: 6 (maks 20, urut mint_count desc).
- Keenamnya Sourcify unverified (HTTP 404) → shape tak bisa diuji → bukan lead: 0x4d15572Fb75118171b7D8551C65c6e94570edffD (123), 0xe0b19788F0a2f4FC9559Ce8D805aCDDFd05589ac (118), 0x02B97b6442Ac8f102C1b8622C579097fA41D2951 (80), 0x9287844e11B4aef757B27f58a4eb1CA832D6225c (39), 0xacc22859Aa104fFA2ad0363bc16f421a26DfF957 (27), 0x3241AF2fCB95E26FD42758B8d067A2383fbFb1d5 (12).
- 51 sisanya sudah terperiksa di run sebelumnya (sampling limit — bukan cakupan penuh, tapi tidak ada yang terlewat dari yang belum diperiksa).
- `track-c-scan-checked.json` diperbarui (nested `checked` 1894 → 1900). Tidak ada track-C lead baru.

## File-file run ini

- `onchain-scan-2026-11-05-2331.json` (hasil scan mentah)
- `scan-2331.log` (log scan)
- `run-2026-11-05-2331-scan-firstseen.json` (10 first-seen sejati)
- `run-2026-11-05-2331-scan-triage.json` (klasifikasi 10 kontrak)
- `run-2026-11-05-2331-scan-triage-raw.json` (data mentah triage Sourcify + price)
- `run-2026-11-05-2331-sourcify-retry.json` (hasil retry Sourcify)
- `run-2026-11-05-2331-template-abi.json` (ABI template agent-mint)
- `run-2026-11-05-2331-template-prices.json` (PRICE/quote 3 kontrak template)
- `run-2026-11-05-2331-5c-shape.json` (hasil shape-check 5c)
- `run-2026-11-05-2331-scan-summary.md` (file ini)

## Catatan

- Sourcify sempat flaky selama triage (RemoteDisconnected / IncompleteRead); retry 3x per kontrak; 3 kontrak template akhirnya terverifikasi, Moonfall/NFA39/Cope/jelly tetap 404.
- RPC bsc-dataseed1 sempat 403 (rate limit) pada beberapa eth_call; dialihkan ke bsc.publicnode.com untuk PRICE/quote.
- Tidak ada preview, mint, approve, swap, atau signing apa pun dalam run ini. twitterapi.io tidak dipanggil.
