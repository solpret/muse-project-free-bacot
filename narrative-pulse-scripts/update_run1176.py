#!/usr/bin/env python3
"""Update state.json run 1176 (narrative pulse, 2026-11-14 03:29 WIB).
Appends a run entry; never touches reported_signals or existing run entries.
Run via: python3 update_run1176.py
"""
import json, shutil

STATE = "/home/hatch/workspace/narrative-pulse/state.json"
BAK = "/home/hatch/workspace/narrative-pulse/state.json.bak-run-0329-20261114"

shutil.copyfile(STATE, BAK)
st = json.load(open(STATE))

assert len(st.get("reported_signals", [])) == 24, "reported_signals berubah!"
assert st["runs"][-1].get("run_number") == 1175, "run terakhir bukan 1175!"

run_entry = {
    "timestamp_wib": "2026-11-14 ~03:30-03:38 WIB",
    "timestamp_utc": "2026-11-13 20:30-20:38 UTC",
    "run_number": 1176,
    "jenis_run": "cek ringan (di luar jendela alert 07:00-13:00/18:00-22:00 WIB; run dijadwalkan 03:29 WIB)",
    "sumber_diperiksa": [
        "fast layer: fast_discovery.py exit 0, 80,9 dtk; halaman 1 dan 3 GeckoTerminal BSC new_pools GAGAL (timeout) — data sebagian, hanya 19 token terbaca. 10 baru, 9 sudah pernah terlihat; pool created 20:12-20:20 UTC (03:12-03:20 WIB). Baru: GTAI 0xdcb3c54abcbd099211f46231f6473f17b555ffff FDV $3.208,63; RIRACOON 0x4881263a28e067c3ecb1c875357bd410fa16dd79 FDV $45,24; PERKBAR 0x79384cd51af99e24c3b135b58f984e2b9ddfffff FDV $3.084,69; PEP 0xd2716fd6df43022723e6f0ff1c9a3eab0b909b6f FDV $189,14; ハウス 0x1084a341babdedea02dcbc818a4ae8a3bec37777 FDV $0,37; MEMEHUNT 0x28c2e6fbd54657b02be1d6fe72160843f64cffff FDV $3.225,91; wFOREST 0x10ccb6f54f1871bd28ef0900a3772b0845bc229d FDV $644,21 M (angka absurd, pool fee 0,01% — data rusak, abaikan); GME 0x7d0e895bceec5f86365e9842b9ca08f327487777 FDV $0,77; Z&M 0xeee0d91f49970ae66babeb6be766a9d8a304ffff FDV $3.226,06; ASSISTANT 0x81275bb9335f913a719f5dcb1ca201878f0bffff FDV $3.235,58. Snapshot first-seen saja, BUKAN sinyal; tidak satu pun muncul di sumber narasi run ini",
        "X search: x_narrative.py exit 0 — X-ERROR kedua token yang dicoba (💥ELO 0x6cb6eba1f85d0d804bf8115046696b3b2cdf2aaa dan 0xe9840d02be14a2a9081009b94fb3ffc0ca3234ba), keduanya HTTP 402 kredit twitterapi.io HABIS; X search TIDAK TERSEDIA run ini; 0 kredit dipakai. TIDAK DILAPORKAN ULANG: laporan buta SEKALI sudah disampaikan di run 1039 (12 Nov 17:14 WIB) untuk episode 402 yang sama dan berkelanjutan sejak 12 Nov ~16:20 WIB — aturan body 'laporkan sekali, lalu terus pantau'",
        "BlockBeats flash (browser live 03:33-03:37 WIB, en.theblockbeats.news/newsflash): 8 flash terbaru terbaca, semuanya makro — suksesi CEO Nvidia (Arm CEO Rene Haas 36%), likuidasi 24j $1,3 miliar (>150 rb orang), Hyperliquid OI rekor $16,8 miliar, Coinbase BTC premium negatif 51 hari, IPO Anthropic seret likuiditas, BTC ~$68.500 (analis: bila < $69.000 bisa uji $65.000), HSBC downgrade Nvidia ke Hold (target $365 -> $170). TANPA satu pun item memecoin BSC / meme BNB Chain. KOREKSI: item 'Hakimi naik ~40% ke MC $27,5 jt' yang sempat muncul di cuplikan pencarian teks TIDAK DITEMUKAN di flash live 14 Nov — pencarian 'Hakimi' di BlockBeats menunjukkan hasil terbaru 6 Sep 2026 (perpetual Bitget); Hakimi memang token BSC menurut item lama Mei 2026 (MC ~$18 jt), tapi tidak ada item kenaikan 14 Nov yang terverifikasi — cuplikan tadi berasal dari crawl basi, BUKAN sinyal. Streak buta BlockBeats run 1174-1175 berakhir: flash terbaca lagi run ini",
        "four.meme Graduated (browser live ~03:34 WIB, four.meme/en?listedPancake=true): terbaca normal; TIDAK ADA graduasi baru <3 jam — umur termuda 13 jam. Teratas: 裤裆里的黑天鹅 / NVDAB MC $125,94K, holders 368, 24j +3.932,42% tapi 1j -1,60% / 5m -0,26% — sama persis dengan run 1175, gelombang lama jaket kulit/Nvidia yang sudah berlipat lalu mendingin, tetap distribution watch (tidak ada perubahan, entri distribution watch tidak disentuh); VIP 人生 MC $2,08K, 1 hari, 24j -92,01%; JACKET / NVDAB MC $2,05K, 13 jam, 24j -34,53%; 小瓜 MC $7,98K, 14 jam, 24j +146,43% tapi 1j +15,48% — lonjakan volatil perputaran tinggi, BUKAN sinyal awal bersih (sama seperti run 1175); 安全驾驶 MC $2,13K, 2 hari, 24j -2,31%",
        "Genius.fun Graduated (browser live ~03:35 WIB, genius.fun): terbaca; total 176 (tetap); lulusan termuda 8 hari (Genius Dog $GDOG MC $5,21K, holders 44, 24j -8,71%) — TIDAK ADA graduasi baru <24 jam; berikutnya XSTOCK 14 hari MC $2,71K, 大股东 14 hari MC $2,56K",
        "Silang wallet: grep 10 CA fast layer baru di holder-watchlist.md dan tier-ab-watch-log.md = NOL kecocokan. wallet-watchlist masih KOSONG (belum ada wallet terpantau terverifikasi) — money-flow tidak dapat dikonfirmasi lewat lapisan wallet. Log holder Mode B terakhir ditulis 02:37 WIB 14 Nov (run 1175: GMGN login-gated streak 95, RPC publik gagal total, blok terakhir terverifikasi 133360221) — money-flow TIDAK TERVERIFIKASI run ini",
        "Lapisan KOL: tidak ada seruan KOL baru yang tampil di sumber narasi run ini; kol-ledger tidak berubah (terakhir ditulis 09:39 WIB 12 Nov)",
    ],
    "sumber_dilewati": [
        "PANews Meme Daily, Odaily headlines, Sharpe.ai, GMGN BSC trending, DexScreener BSC trending/new pairs, Binance Square — cek ringan di luar jendela alert; hanya dibuka bila ada kandidat dari fast layer/sumber wajib, tidak ada",
        "Jinse flash — dicopot dari sumber wajib (buta 11 run berturut-turut)",
    ],
    "hasil": "tidak ada sinyal — DIAM. Tidak ada konvergensi multi-sumber: tidak satu pun token fast layer muncul di sumber narasi; BlockBeats terbaca lagi (streak buta berakhir) dan isinya makro semua; dugaan item Hakimi 14 Nov TIDAK terverifikasi di flash live (crawl basi); NVDAB tetap distribution watch tanpa perubahan; Genius.fun tanpa graduasi baru. X search tidak tersedia (402, sudah dilaporkan sekali di run 1039 — tidak diulang). Tidak ada laporan chat. reported_signals tetap 24.",
    "kredit_x_dipakai": 0,
}

st["runs"].append(run_entry)

json.dump(st, open(STATE, "w"), ensure_ascii=False, indent=1)
print("OK: runs =", len(st["runs"]), "| reported_signals =", len(st["reported_signals"]))

# --- x_narrative_state.json: catat percobaan 402 hari ini (tambah ke note 2026-11-14) ---
XSTATE = "/home/hatch/workspace/narrative-pulse/x_narrative_state.json"
xs = json.load(open(XSTATE))
u = xs.setdefault("usage", {}).setdefault("2026-11-14", {
    "searches": 0, "tweets": 0, "credits_est": 0, "note": "",
})
u["note"] = (u.get("note", "") + " | Run 1176 ~03:32 WIB: 2 token dicoba (ELO 0x6cb6..., 0xe984...), keduanya HTTP 402 credits exhausted; 0 kredit dipakai.").strip(" |")
json.dump(xs, open(XSTATE, "w"), ensure_ascii=False, indent=1)
print("OK: x_narrative usage 2026-11-14 diperbarui")
