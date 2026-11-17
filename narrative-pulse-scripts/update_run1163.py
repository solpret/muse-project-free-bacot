#!/usr/bin/env python3
"""Update state.json run 1163 (narrative pulse, 2026-11-14 00:14 WIB).
Appends a run entry + NVDAB distribution-watch update; never touches
reported_signals or existing run entries. Run via: python3 update_run1163.py
"""
import json, shutil, sys

STATE = "/home/hatch/workspace/narrative-pulse/state.json"
BAK = "/home/hatch/workspace/narrative-pulse/state.json.bak-run-0014-20261114"

shutil.copyfile(STATE, BAK)
st = json.load(open(STATE))

assert len(st.get("reported_signals", [])) == 24, "reported_signals berubah!"
assert st["runs"][-1].get("run_number") == 1162, "run terakhir bukan 1162!"

run_entry = {
    "timestamp_wib": "2026-11-14 ~00:14-00:22 WIB",
    "timestamp_utc": "2026-11-13 17:14-17:22 UTC",
    "run_number": 1163,
    "jenis_run": "cek ringan (di luar jendela alert 18:00-22:00 WIB; run dijadwalkan 00:14 WIB)",
    "sumber_diperiksa": [
        "fast layer: fast_discovery.py exit 0, ~42,8 dtk; 3 halaman GeckoTerminal BSC new_pools, 38 pool created 17:00-17:09 UTC (00:00-00:09 WIB). FDV menonjol: ハウスコイン 0xdb2c... ~$119,89 rb (vol 24j $270,05 rb), 💥CHAD ~$82,26 rb, GUESS ~$9,53 rb; mayoritas FDV ~$3,2 rb bernama China/Jepang + duplikat (HOUSE, 小房东, 久留美, 星のコイン, XCX, ハウス通貨, HashGlobal) — snapshot first-seen saja, BUKAN sinyal; tidak ada satu pun yang muncul di sumber narasi run ini",
        "X search: x_narrative.py exit 0, 2 token dicoba (ハウスコイン 0xdb2cb3113673c18139784e5eb5f67c3caa177777 dan STAR⭐ 0xe84603bb3554a6ae679540c1d5855b4a8ec56637 — first-seen run 1162) — KEDUANYA X-ERROR HTTP 402 kredit twitterapi.io HABIS ('Credits is not enough'). X search TIDAK TERSEDIA run ini; 0 kredit dipakai. Kondisi ini sudah tercatat sejak 16:01 WIB 13 Nov dan sudah dilaporkan sekali di run 1039, tidak dilaporkan ulang",
        "BlockBeats flash (tugas browser live, 00:17-00:20 WIB; theblockbeats.info tanpa www sempat 404, versi www yang berhasil): 10 flash terbaru 21:37-23:02 WIB semuanya makro — suksesi Huang/Nvidia, likuidasi 24j $1,31 miliar, Hyperliquid OI $16,8 miliar, Coinbase BTC premium negatif 51 hari, IPO Anthropic, BTC ~$68.500 (-4%), Fed Collins — TANPA satu pun item memecoin BSC / meme BNB Chain",
        "four.meme Graduated (tugas browser live, 00:17-00:20 WIB): termuda 9 jam — TIDAK ADA graduasi baru <1 jam. Teratas: 裤裆里的黑天鹅 / NVDAB MC $124,03K, holders 368, umur 9 jam, 24j +3.926,21% lalu 1j -2,98% / 4j -15,30% — sudah berlipat lalu melemah, distribution watch (update dicatat di entri NVDAB run 1162); VIP 人生 MC $2,27K, 24j -91,36%; JACKET / NVDAB MC $2,15K, 24j -34,62%; 小瓜 MC $6,58K, 24j +105,84%; 安全驾驶 MC $2,33K, 24j +0,57%. Tema Nvidia/jaket kulit (NVDAB, JACKET, tag jacket/皮衣/leather) masih menonjol tapi sudah dimainkan",
        "Genius.fun (tugas browser live, 00:17-00:20 WIB): total Graduated tetap 176; termuda Genius Dog ($GDOG) umur 8 hari, MC $5,18K, holders 44, 24j -8,71% — TIDAK ADA graduasi baru <24 jam (berikutnya XSTOCK 14 hari, 大股东 14 hari)",
        "Lapisan wallet: wallet-watchlist masih kosong (belum ada wallet terpantau terverifikasi) sehingga money-flow TIDAK DAPAT dikonfirmasi; log holder Mode B terakhir basi; tier-ab-watch-log terakhir run 98 (~16:57 WIB 13 Nov) login-gated, 0 pembelian baru terverifikasi — money-flow tidak terverifikasi run ini",
        "Lapisan KOL: tidak ada seruan KOL baru yang tampil di sumber narasi run ini; kol-ledger tidak berubah",
    ],
    "sumber_dilewati": [
        "PANews Meme Daily, Odaily, Sharpe.ai, GMGN trending, DexScreener trending — dilewati karena cek ringan di luar jendela alert (hanya BlockBeats + graduasi yang wajib)",
        "Binance Square — deep-check saja bila sudah ada kandidat; tidak ada kandidat run ini",
        "Jinse flash — dicopot dari sumber wajib (buta 11 run berturut-turut)",
    ],
    "hasil": "tidak ada sinyal — DIAM. Tidak ada konvergensi multi-sumber: tidak satu pun token fast layer muncul di BlockBeats / four.meme Graduated / Genius.fun; NVDAB tetap distribution watch (sudah berlipat + melemah); Genius.fun tanpa graduasi baru; X search tidak tersedia sehingga uji konvergensi X tidak bisa berjalan — bukan klaim 'tidak ada sinyal' yang utuh. Tidak ada laporan chat. reported_signals tetap 24.",
    "kredit_x_dipakai": 0,
}

st["runs"].append(run_entry)

# Update entri distribution watch NVDAB run 1162 (yang terbaru, token persis "裤裆里的黑天鹅 / NVDAB")
updated = False
for e in reversed(st.get("distribution_watch", [])):
    if e.get("token") == "裤裆里的黑天鹅 / NVDAB":
        e["status"] += (" Update run 1163 (browser 00:17-00:20 WIB): masih Graduated teratas four.meme, "
                        "MC $124,03K (dari $127,48K run 1162), holders 368 (dari 370), 24j +3.926,21% "
                        "(dari +4.048,77%), 1j -2,98%, 4j -15,30%, umur 9 jam, vol 24j $52,94K — "
                        "sudah berlipat lalu terus melemah; tetap distribution watch, BUKAN sinyal entry; "
                        "tidak dilaporkan ke user.")
        updated = True
        break
assert updated, "entri NVDAB run 1162 tidak ditemukan!"

json.dump(st, open(STATE, "w"), ensure_ascii=False, indent=1)
print("OK: runs =", len(st["runs"]), "| reported_signals =", len(st["reported_signals"]),
      "| NVDAB updated =", updated)

# --- x_narrative_state.json: catat 402 hari ini ---
XSTATE = "/home/hatch/workspace/narrative-pulse/x_narrative_state.json"
xs = json.load(open(XSTATE))
xs.setdefault("usage", {})["2026-11-14"] = {
    "searches": 0,
    "tweets": 0,
    "credits_est": 0,
    "note": "X-ERROR HTTP 402 credits exhausted at 00:15 WIB (2 token dicoba); sudah dilaporkan sekali di run 1039, tidak dilaporkan ulang",
}
json.dump(xs, open(XSTATE, "w"), ensure_ascii=False, indent=1)
print("OK: x_narrative usage 2026-11-14 dicatat")
