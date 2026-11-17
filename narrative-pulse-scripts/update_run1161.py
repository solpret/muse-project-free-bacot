#!/usr/bin/env python3
"""Append run 1161 entry to state.json runs + update NVDAB/GSTOCK distribution watch.
Guards: last run must be 1160; reported_signals count must stay 24."""
import json

PATH = "/home/hatch/workspace/narrative-pulse/state.json"

with open(PATH, encoding="utf-8") as f:
    s = json.load(f)

assert s["runs"][-1]["run_number"] == 1160, s["runs"][-1]["run_number"]
assert len(s.get("reported_signals", [])) == 24, len(s.get("reported_signals", []))

run = {
    "timestamp_wib": "2026-11-13 ~23:44-23:52 WIB",
    "timestamp_utc": "2026-11-13 16:44-16:52 UTC",
    "run_number": 1161,
    "jenis_run": "cek ringan (di luar jendela alert 18:00-22:00 WIB; run dijadwalkan 23:44 WIB)",
    "sumber_diperiksa": [
        "fast layer: fast_discovery.py exit 0, ~62,9 dtk; SEMUA 3 halaman GeckoTerminal BSC new_pools TIMEOUT (FAIL) — 0 token, 0 baru, 0 sudah pernah terlihat; snapshot first-seen kosong run ini, BUKAN bukti tidak ada token baru (hanya fast layer buta); heartbeat state.json 2026-11-13T23:46:18+07:00",
        "X search: x_narrative.py exit 0, 2 token dicoba (0x48c201c81f1606d45de666041dee87b995c324c1 dan 0x0952d33625cddd6b28da3a5938f0de7ba310d6ad — first-seen run 1160, created 23:24-23:29 WIB) — KEDUANYA X-ERROR HTTP 402 kredit twitterapi.io HABIS ('Credits is not enough'). X search TIDAK TERSEDIA run ini; 0 kredit dipakai. Kondisi ini sudah tercatat sejak 16:01 WIB dan sudah dilaporkan sekali di run 1039 — TIDAK dilaporkan ulang; JANGAN mengarang hasil discussion",
        "BlockBeats flash (browser 23:47-23:50 WIB, halaman benar /newsflash — /en/flash 404): 10 flash terbaru 22:23-23:42 WIB; 23:42 Hyperliquid OI akhir Q3 $16,8 M rekor; 23:31 premi BTC Coinbase negatif 51 hari berturut-turut; 23:17 IPO Anthropic / mundurnya Huang Renxun / ekspektasi kenaikan suku bunga The Fed menekan BTC; 23:04 analis BTC bila kehilangan $69 rb bisa uji $65 rb; 22:58 HSBC turunkan rating Nvidia ke 'Hold', target $365 jadi $170; 22:37 pasar kripto turun menyeluruh (BTC $68.515,90 -4,00% 24j, ETH $1.925,97 -3,56% 24j, funding rate bearish) — TIDAK ADA satu pun item memecoin BSC / meme BNB Chain; konteks pasar bearish untuk BTC",
        "four.meme Graduated (browser 23:47-23:50 WIB): TIDAK ADA graduasi berumur <1 jam — termuda 9 jam. 10 teratas: NVDAB 裤裆里的黑天鹅 MC $129,63K, holders 370, umur 9 jam, 24H +4.129,41% (1j -7,54%, 4j +21,53% — SUDAH BERLIPAT, distribution watch, sudah dicatat run 1159/1160: turun dari $131,7K/+4.184,47% run 1160); VIP 人生 $2,26K/354/1 hari/24H -91,15%; JACKET $2,15K/25/10 jam/24H -34,62%; 小瓜 $6,3K/133/11 jam/24H +96,13%; 安全驾驶 $2,33K/73/1 hari/24H +0,57%; FDC $2,49K/69/2 hari/24H -2,96%; frog $5,04K/166/2 hari/24H +23,17%; NB $2,05K/86/3 hari/24H -0,45%; 真诚 $2K/91/4 hari/24H -1,71%; NB $1,95K/57/4 hari/24H -6,24%. SNDK 2 kontrak ($2,14K/98/6 hari/+0,94% dan $1,98K/62/7 hari/-0,78%) dan AICAT ($1,79K/176/9 hari/+0,11%) identik dengan run sebelumnya — membeku di lantai",
        "Genius.fun Graduated (browser 23:47-23:50 WIB): total tetap 176; TIDAK ADA graduate baru <24 jam di 10 teratas berdasar MC — termuda 51 hari (GPU $9,48K). Teratas: GSTOCK $3,37 jt/8.819/-15,10% (Trending #1, SUDAH RAMAI — distribution watch); MILAN $100,35K/1.253/-12,25%; GCAT $27,09K/1.659/+14,17%. Genius Morning $GM masih On curve (MC $3,45K, 6 holders, umur 7 hari, 24H 0,00%, progres 2,78%) — bukan Graduated. Batas baca: penilaian 'tidak ada graduate baru' dari 10 teratas saja, bukan seluruh 176 baris; umur token tampil, bukan stempel waktu graduasi",
        "silang wallet: fast layer 0 token run ini (buta total) sehingga tidak ada CA untuk disilang; wallet-watchlist.md masih KOSONG (belum ada wallet terverifikasi) — lapisan wallet TIDAK DAPAT mengonfirmasi money-flow; log holder Mode B terakhir run 22:30 WIB: money-flow TIDAK TERVERIFIKASI (GMGN login-gated streak 93; cek on-chain 28 saldo GAGAL TOTAL karena semua endpoint RPC timeout) — status ini tidak berubah run ini (bukan run holder, tidak ada cek ulang)",
    ],
    "sumber_dilewati": [
        "Jinse flash (dicopot dari sumber wajib — buta 11 run berturut-turut)",
        "PANews Meme Daily, Odaily, Sharpe.ai, GMGN trending, DexScreener trending (opsional — cek ringan di luar jendela alert)",
        "Binance Square (deep-check saja bila sudah ada kandidat — tidak ada kandidat run ini)",
        "KOL-ledger: tidak ada seruan KOL baru di sumber yang diperiksa run ini",
    ],
    "hasil": "TIDAK ADA SINYAL BARU — run diam. Tidak ada token yang sama muncul di >=2 sumber: tema 'jacket'/NVDAB hanya kemiripan nama lintas sumber (JACKET/NVDAB di four.meme vs genius jacket $GJACKET On curve di Genius.fun, MC $3,23K/2 holders/57 hari; NVDAB vs berita saham Nvidia di BlockBeats; SNDK saham vs token meme) — BUKAN konvergensi. NVDAB tetap distribution watch (+4.129,41% 24j — makin jauh dari base rendah, BUKAN sinyal awal). Tidak ada graduasi baru di kedua launchpad; $GM datar On curve; SNDK/AICAT membeku di lantai. Fast layer buta total + X search tidak tersedia run ini, jadi uji konvergensi multi-sumber tidak bisa berjalan penuh — TAPI ketiga sumber browser terbaca lengkap dan tidak menunjukkan narasi BSC baru, jadi run ini LENGKAP untuk cek ringan (bukan 'tidak lengkap'). Tidak dilaporkan ke user.",
    "kredit_x_dipakai": 0,
    "x_search_status": "tidak tersedia — HTTP 402 kredit twitterapi.io habis (sejak 16:01 WIB; sudah dilaporkan sekali di run 1039)",
}

s["runs"].append(run)

# Update NVDAB token entry in distribution_watch (per-run update pattern)
updated = []
for e in s.get("distribution_watch", []):
    tok = e.get("token", "")
    if tok.startswith("NVDAB /"):
        e["status"] += (" Update run 1161 (browser 23:47-23:50 WIB): masih Graduated teratas four.meme, "
                        "MC $129,63K (dari $131,7K run 1160), holders 370, 24H +4.129,41% (dari +4.184,47%), "
                        "1j -7,54% — sudah berlipat, tetap distribution watch, BUKAN sinyal entry; tidak dilaporkan ke user.")
        updated.append("NVDAB")
    if "GSTOCK" in json.dumps(e, ensure_ascii=False) and "Genius" in json.dumps(e, ensure_ascii=False):
        pass  # GSTOCK covered below if no dedicated entry exists

# GSTOCK: add dedicated distribution_watch entry if none exists yet
if not any("GSTOCK" in json.dumps(e, ensure_ascii=False) for e in s.get("distribution_watch", [])):
    s["distribution_watch"].append({
        "token": "Gstock $GSTOCK (Genius.fun Graduated, CA tidak dicatat — tidak diverifikasi on-chain run ini)",
        "status": ("distribution watch run narasi 2026-11-13 23:44 WIB (browser 23:47-23:50 WIB): Genius.fun Graduated "
                   "Trending #1, MC $3,37 jt, holders 8.819, umur 57 hari, 24H -15,10%, vol 24j $25K — SUDAH RAMAI / "
                   "kapitalisasi besar dan sedang turun, BUKAN sinyal entry; tidak dilaporkan ke user"),
    })
    updated.append("GSTOCK-new")

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)

# Verify
with open(PATH, encoding="utf-8") as f:
    s2 = json.load(f)
print("runs:", len(s2["runs"]), "last run:", s2["runs"][-1]["run_number"])
print("reported_signals:", len(s2.get("reported_signals", [])))
print("updated distribution_watch:", updated)
print("OK")
