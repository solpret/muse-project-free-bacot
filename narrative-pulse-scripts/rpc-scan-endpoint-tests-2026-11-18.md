# Re-probe RPC Publik BSC — 18 Nov 2026 ~05:47 WIB

Perintah user 18 Nov ~05:44 WIB ("Cari RPC lain sekarang") — bloXroute 403
persisten >4 jam, run 208+209 gagal total. Uji ulang 14 Nov + kandidat baru
(Lava, Alchemy demo, Blockscout REST, host alt bloXroute). Metode: curl,
eth_blockNumber lalu eth_getLogs jendela 200 blok filter driver (Transfer,
from=zero, to=[AFeng]). Hasil mentah:
~/workspace/narrative-pulse/rpc-probe-2026-11-18.json. Skrip:
~/workspace/narrative-pulse/rpc-probe-2026-11-18.py.

## Hasil: TIDAK ADA pengganti yang layak untuk driver

| Endpoint | blockNumber | eth_getLogs (200 blok) |
|---|---|---|
| bloXroute bsc.rpc.blxrbdn.com (re-probe) | OK | **403 Forbidden** "Request forbidden by administrative rules" — MASIH diblokir |
| bloXroute alt host bsc.blxrbdn.com | mati | — |
| dataseed binance.org / bnbchain.org / dataseed1/2 bnbchain.org / defibit / ninicoin | OK | **-32005 limit exceeded** (semua) |
| publicnode bsc + bsc-rpc (baru bisa blockNumber, 14 Nov 403) | OK | **-32005 Rate limit exceeded** (minta token personal) |
| blastapi public | OK | **-32000 rate-limited** (minta akun Alchemy gratis) |
| blockpi public | — | **Apikey not found** (publik key dicabut) |
| drpc.org | — | rate limit endpoint publik |
| 1rpc.io/bnb | — | usage limit |
| meowrpc | OK | **eth_getLogs is not supported** |
| llamarpc binance | mati | — |
| omniatech | 521 | — |
| onfinality public | OK | **-32029 Too Many Requests** (minta API key) |
| therpc.io | 301 | — |
| ankr public (tanpa key) | — | **401 Unauthorized** (butuh API key) |
| lava.build | — | **endpoint discontinued** |
| alchemy demo | mati | — |
| 48.club | OK | **OK, 0 log — tapi jendela 10 blok** (max ~20 blok, bukan kandidat driver) |
| Blockscout REST bnb-smart-chain | — | **503 Service Unavailable** |

## Kesimpulan

- **Satu-satunya getLogs yang sukses: 48.club, jendela 10 blok.** Untuk chunk
  driver 2000 blok butuh ~100 panggilan per chunk (×2 topik) — 1 jendela 4 jam
  ≈ 3.200 panggilan, rawan 429. Sudah dinilai tidak layak 14 Nov; tetap
  tidak layak.
- **bloXroute 403 belum pulih** (sejak 15 Nov flaky, 18 Nov 01:06–05:47
  persisten total). eth_blockNumber tetap hidup — blokirnya setingkat metode
  getLogs.
- **Jalur gratis yang tersisa butuh daftar akun (langkah tangan user):**
  API key gratis Ankr / Alchemy / OnFinality / Allnodes-publicnode. Bukan
  BscScan (kunci BscScan ditunda sampai ada payout — jangan ditawarkan).
- Watermark scan tetap **134132541**; gap kini >62.000 blok dan membesar.
  Run 210 (09:05 WIB) tanpa perubahan akan memakai bloXroute lagi.
