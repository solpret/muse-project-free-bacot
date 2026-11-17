#!/usr/bin/env python3
"""Update state.json run 1178 (narrative pulse, 2026-11-14 03:59 WIB).
Appends a run entry + brief updates to the two run-1177 distribution entries;
never touches reported_signals or existing run entries.
Run via: python3 update_run1178.py
"""
import json, shutil

STATE = "/home/hatch/workspace/narrative-pulse/state.json"
BAK = "/home/hatch/workspace/narrative-pulse/state.json.bak-run-0359-20261114"

shutil.copyfile(STATE, BAK)
st = json.load(open(STATE))

assert len(st.get("reported_signals", [])) == 24, "reported_signals berubah!"
assert st["runs"][-1].get("run_number") == 1177, "run terakhir bukan 1177!"

run_entry = {
    "timestamp_wib": "2026-11-14 ~04:00-04:12 WIB",
    "timestamp_utc": "2026-11-13 21:00-21:12 UTC",
    "run_number": 1178,
    "jenis_run": "cek ringan (di luar jendela alert 07:00-13:00/18:00-22:00 WIB; run dijadwalkan 03:59 WIB)",
    "sumber_diperiksa": [
        "fast layer: fast_discovery.py exit 0, 50,9 dtk; 3 halaman GeckoTerminal BSC new_pools terbaca; 60 token, 59 baru, 1 sudah pernah terlihat; pool created 20:24-20:58 UTC (03:24-03:58 WIB). Terbesar FDV: SMSTR 0x153bd9aa55cf4dd3d72b0ee46d324eeb14df20ea $1,05 jt; 比特🐼 0x8af7a4c4b36180e6e7795bf533b23a3ebb137a33 $311,98K; PIR 0x2ef12e9624bf8fa7825583aa5dc8d90eb0085344 $245,86K; ハウス 0xedbe3136b2c683f6f750154696129be1bd577777 $147,81K; SHI 0xaf57e72766a960421f52afa033870fc85ed9fa63 $137,28K; BRACKET 0xa07fcc8e4ffb951dbe743269e6882e91d2017777 $87,76K. Mayoritas klon FDV ~$3,2 rb + duplikat nama China (ハウス x5, 币安人生 x2, 雪眉娘 x2, BBTB x2, MIST x2). Angka FDV absurd (HB BTC $23,6 Miliar, JNK $12,76 Miliar, ELON $3,98 Miliar) = data rusak/spoof, abaikan. Snapshot first-seen saja, BUKAN sinyal; tidak satu pun muncul di sumber narasi run ini. Catatan: 币安人生 muncul 2x di fast layer — peringatan token palsu SlowMist sudah ada di distribution watch, tidak ada tindakan baru",
        "X search: x_narrative.py exit 0 — X-ERROR kedua token yang dicoba (PIR 0x2ef12e9624bf8fa7825583aa5dc8d90eb0085344 dan 比特🐼 0x8af7a4c4b36180e6e7795bf533b23a3ebb137a33), keduanya urlopen timed out; X search TIDAK TERSEDIA run ini; 0 kredit dipakai. Bukan 402 kali ini (run 1177: 402 kredit habis) — penyebab timeout tidak terverifikasi, jangan disimpulkan kredit habis",
        "BlockBeats flash: GAGAL DIMUAT (browser 04:01-04:03 WIB, 3 percobaan ke blockbeats.info/flash dan www.blockbeats.info/flash, error DNS_PROBE_STARTED) — tidak ada flash yang terbaca run ini. CATATAN: mirror yang berhasil di run 1176/1177 (en.theblockbeats.news/newsflash) TIDAK dicoba run ini — jadi ini kegagalan cek, bukan bukti buta; flash terbaru terakhir terverifikasi tetap 00:19 Beijing 14 Nov (run 1177). Tidak ada streak buta 4 run (1176-1177 terbaca)",
        "four.meme Graduated (browser 04:01-04:03 WIB, four.meme/en?listedPancake=true): terbaca; teratas: 裤裆里的黑天鹅 / NVDAB MC $125,94K, holders 368, vol 24j $54,4K, 24H +3.932,42%, umur 13 jam — angka SAMA PERSIS dengan run 1177 (kemungkinan data four.meme stagnan/cache, atau token memang datar); 小瓜 MC $8,08K (dari $7,98K run 1177), holders 139, vol 24j $114,53K, 24H +149,38%, umur 15 jam; JACKET MC $2,05K, 28 holders, 24H -34,53%. KOREKSI terhadap klaim browser: ini BUKAN graduasi baru — ketiganya sudah tercatat di distribution watch sejak 13 Nov (小瓜 sejak 13:29 WIB, 黑天鹅 sejak 21:14 WIB) dan sudah tampil di run 1177 dengan angka yang sama/hampir sama. Tetap distribution watch, BUKAN sinyal entry. SNDK MC $2,14K/holders 98/24H +0,94%/umur 6 hari dan AICAT MC $1,79K/holders 176/24H +0,11%/umur 9 hari tidak berubah dari run 1177",
        "Genius.fun Graduated (browser 04:01-04:03 WIB, genius.fun): terbaca; total 176 (tetap); 10 teratas umur 51-57 hari (GSTOCK $3,6 jt, MILAN $104,9K, GCAT $27,41K, 天才 $24,95K, GF $18,59K, VC $18,21K, GCAT $11,42K, GSTONK $11,3K, GPU $9,46K, 超级智能 $8,59K) — TIDAK ADA graduasi baru <24 jam. Genius Morning $GM tetap On curve MC $3,47K, holders 6, umur 7 hari, BUKAN Graduated (tidak dicampur)",
        "Silang wallet: wallet-watchlist masih KOSONG (belum ada wallet terpantau terverifikasi) — money-flow tidak dapat dikonfirmasi lewat lapisan wallet. Log holder Mode B terakhir ditulis 02:37 WIB 14 Nov (GMGN login-gated, RPC publik gagal total, blok terakhir terverifikasi 133360221); tier-ab run 99 (03:53-03:54 WIB) INCOMPLETE login-gated, 0 pembelian baru terverifikasi — money-flow TIDAK TERVERIFIKASI run ini",
        "Lapisan KOL: tidak ada seruan KOL baru yang tampil di sumber narasi run ini; kol-ledger tidak berubah (terakhir ditulis 09:39 WIB 12 Nov)",
    ],
    "sumber_dilewati": [
        "PANews Meme Daily, Odaily headlines, Sharpe.ai, GMGN BSC trending, DexScreener BSC trending/new pairs, Binance Square — cek ringan di luar jendela alert; hanya dibuka bila ada kandidat dari fast layer/sumber wajib, tidak ada",
        "Jinse flash — dicopot dari sumber wajib (buta 11 run berturut-turut)",
    ],
    "hasil": "tidak ada sinyal — DIAM. Tidak ada konvergensi multi-sumber: tidak satu pun token fast layer muncul di sumber narasi; BlockBeats tidak tercek run ini (hanya /flash yang dicoba, mirror /newsflash tidak dicoba — bukan bukti tidak ada flash); klaim browser soal 'graduasi baru' TERKOREKSI — 黑天鹅/小瓜/JACKET sudah tercatat sejak 13 Nov dan angkanya identik dengan run 1177; Genius.fun tanpa graduasi baru; X search tidak tersedia (timeout, 0 kredit). Tidak ada laporan chat. reported_signals tetap 24.",
    "kredit_x_dipakai": 0,
}

st["runs"].append(run_entry)

# --- update singkat entri distribution watch run 1177 (黑天鹅 + 小瓜) ---
dw = st.get("distribution_watch", [])
n_updated = 0
for e in dw:
    tok = e.get("token", "")
    status = e.get("status", "")
    if tok == "裤裆里的黑天鹅 / NVDAB" and status.startswith("distribution watch run narasi 2026-11-14 03:44 WIB"):
        e["status"] = status + " Update run 1178 (browser 04:01-04:03 WIB): masih Graduated teratas four.meme, MC $125,94K, holders 368, vol 24j $54,4K, 24H +3.932,42%, umur 13 jam — SAMA PERSIS dengan run 1177 (kemungkinan data four.meme stagnan/cache); tetap distribution watch, BUKAN sinyal entry; tidak dilaporkan ke user."
        n_updated += 1
    elif tok == "小瓜" and status.startswith("distribution watch run narasi 2026-11-14 03:44 WIB"):
        e["status"] = status + " Update run 1178 (browser 04:01-04:03 WIB): masih Graduated four.meme, MC $8,08K (dari $7,98K run 1177), holders 139, vol 24j $114,53K, 24H +149,38%, umur 15 jam — tidak berubah berarti; tetap distribution watch, BUKAN sinyal entry; tidak dilaporkan ke user."
        n_updated += 1
assert n_updated == 2, f"entri distribution watch run 1177 ter-update: {n_updated}, harus 2!"

json.dump(st, open(STATE, "w"), ensure_ascii=False, indent=1)
print("OK: runs =", len(st["runs"]), "| reported_signals =", len(st["reported_signals"]), "| dw updated =", n_updated)

# --- x_narrative_state.json: catat percobaan timeout hari ini ---
XSTATE = "/home/hatch/workspace/narrative-pulse/x_narrative_state.json"
xs = json.load(open(XSTATE))
u = xs.setdefault("usage", {}).setdefault("2026-11-14", {
    "searches": 0, "tweets": 0, "credits_est": 0, "note": "",
})
u["note"] = (u.get("note", "") + " | Run 1178 ~04:02 WIB: 2 token dicoba (PIR 0x2ef12e..., 比特🐼 0x8af7a4...), keduanya urlopen timed out (bukan 402); 0 kredit dipakai.").strip(" |")
json.dump(xs, open(XSTATE, "w"), ensure_ascii=False, indent=1)
print("OK: x_narrative usage 2026-11-14 diperbarui")
