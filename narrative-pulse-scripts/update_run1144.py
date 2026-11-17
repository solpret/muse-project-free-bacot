#!/usr/bin/env python3
"""Update state.json for narrative-pulse run 1144 (2026-11-13 ~19:44 WIB).
Additive only: appends one run entry, one distribution_watch entry,
and appends update text to three existing distribution_watch entries.
Never touches reported_signals or existing runs. Atomic replace."""
import json, os

STATE = os.path.expanduser("~/workspace/narrative-pulse/state.json")

with open(STATE) as f:
    st = json.load(f)

assert isinstance(st, dict)
n_runs_before = len(st.get("runs", []))
n_sig_before = len(st.get("reported_signals", []))

run_entry = {
    "timestamp_wib": "2026-11-13 ~19:44-19:52 WIB",
    "timestamp_utc": "2026-11-13 12:44-12:52 UTC",
    "run_number": 1144,
    "jenis_run": "pulse penuh (jendela alert 18:00-22:00 WIB; run dijadwalkan 19:44 WIB)",
    "sumber_diperiksa": [
        "fast layer: fast_discovery.py exit 0, ~12,7 dtk; 43 token baru first-seen 19:44-19:47 WIB (created 12:28-12:39 UTC / 19:28-19:39 WIB). Mayoritas FDV ~$3,2 rb bernama China; FDV menonjol: KB 0x273073938b5bd1c725bacf7a9550b4d1f4067544 /WBNB ~$228,15 rb, APEB 0xed25bf68b75b070574919cc8712e39af341fcf4a /WBNB ~$225,96 rb, MHT 0x334fd57a0270daadafb6f3ab8f0404764a178dd6 /WBNB ~$194,16 rb, YellowRoom 0x140a367e84e2de833d0637284ccf08adc83c7777 /WBNB ~$116,95 rb, papercat 0xc312736d31428440f35508ef3e39760f38687777 /WBNB ~$101,61 rb — snapshot first-seen saja, BUKAN sinyal, tidak ada yang muncul di sumber narasi run ini",
        "X search: x_narrative.py exit 0 tetapi TIDAK TERSEDIA — X-ERROR HTTP 402 kredit twitterapi.io habis untuk 2 token (KB 0x273073938b5bd1c725bacf7a9550b4d1f4067544 dan 人生曲 0x724013d691dd25006184f6b8b3118b6a6d7f7777); kondisi sudah dilaporkan sekali sebelumnya, tidak dilaporkan ulang; 0 kredit dipakai",
        "BlockBeats flash (browser 19:45-19:49 WIB, en.theblockbeats.news/newsflash): 20 item 17:41-19:34 WIB, TIDAK ADA item memecoin BSC / meme BNB Chain / launchpad; yang terdekat dengan BNB hanyalah airdrop RAVE Binance Alpha (18:16) dan pencantuman Anthropic di pasar pre-market perpetual Binance (18:35) — keduanya bukan memecoin BSC",
        "four.meme Graduated (browser 19:47 WIB): teratas 裤裆里的黑天鹅/NVDAB usia 5 jam MC $115,54K 24H +3.481,43% holders 237 (hanya +2 selama pengamatan) — sudah berlipat, sumber tunggal, BUKAN sinyal entry, dicatat distribution watch run ini; 小瓜 usia 7 jam MC $7,86K 141 holders vol24 $111,77K 24H +141,56% — sama seperti run 1143, BUKAN sinyal; tidak ada graduated baru <5 jam",
        "Genius.fun Graduated (browser 19:47-19:48 WIB): 176 token (tetap), termuda Genius Dog ($GDOG) usia 8 hari MC $5,21K 44 holders — tidak ada kelulusan baru",
        "Log holder Mode B (holder-watchlist.md, run 18:30 WIB): detail GMGN login-gated streak 91, money-flow TIDAK TERVERIFIKASI; saldo on-chain 28/28 tidak berubah vs run 16:30 WIB; Dompet A ok + 旺财 tetap 100% hold; Dompet B hanya Ai Pro yang masih terbuka. Wallet-watchlist tetap KOSONG (belum ada wallet terpantau terverifikasi) — money-flow tidak dapat dikonfirmasi. Kol-ledger: tidak ada seruan KOL baru dengan CA terverifikasi"
    ],
    "sumber_dilewati": [
        "PANews Meme Daily, Odaily headlines, Sharpe.ai, GMGN trending, DexScreener trending (opsional — waktu run dipakai sumber wajib + browser; tidak ada kandidat dari fast layer/sumber wajib yang butuh deep-check)",
        "Binance Square (deep-check saja — tidak ada kandidat)"
    ],
    "hasil": "tidak ada sinyal baru — DIAM ke chat. Tidak ada konvergensi multi-sumber; tidak ada graduation baru + mention awal; X search tidak tersedia (kredit habis)",
    "kredit_x_dipakai": 0
}

st.setdefault("runs", []).append(run_entry)

st.setdefault("distribution_watch", []).append({
    "token": "裤裆里的黑天鹅 / NVDAB (nama saja, CA tidak terverifikasi — four.meme hanya tampil terpotong 0xe6b4...ffff)",
    "status": "distribution watch run narasi 2026-11-13 19:44 WIB (browser 19:47 WIB): four.meme Graduated teratas, MC $115,54K, umur 5 jam, vol 24j $21,05K, holders 237, 24H +3.481,43% — sudah berlipat dalam sehari, BUKAN sinyal entry; holders hanya naik 235→237 selama pengamatan (bukan pertumbuhan holder cepat); sumber tunggal run ini (tidak muncul di BlockBeats, Genius.fun, X, maupun log holder/tier-ab run ini); CA tidak dicatat utuh karena tidak diverifikasi on-chain run ini; tidak dilaporkan ke user"
})

updates = {
    "AICAT": " Update run 1144 (browser 19:47 WIB): masih Graduated four.meme, MC $1,79K, holders 176, 24H +0,11%, umur 9 hari — identik dengan run 1142 ($1,79K/176/+0,11%/9 hari); tetap distribution watch, BUKAN sinyal entry; tidak dilaporkan ke user.",
    "SNDK": " Update run 1144 (browser 19:47 WIB): SNDK 0x9557...ffff MC $2,14K, holders 98, 24H +0,94%, umur 6 hari; SNDK kedua 0xd66b...ffff MC $1,98K, holders 62, 24H -0,78%, umur 7 hari — identik dengan run 1142 ($2,14K/98/+0,94%/6 hari); tetap di lantai pasca-jatuh dari ~$136,59K; tetap distribution watch, BUKAN sinyal entry; tidak dilaporkan ke user.",
}
for e in st.get("distribution_watch", []):
    tok = e.get("token", "")
    if tok in updates:
        e["status"] = e.get("status", "") + updates[tok]
    elif tok.startswith("GM / GREEN MORNING"):
        e["status"] = e.get("status", "") + " Update run 1144 (browser 19:47 WIB): GM = Genius Morning $GM masih On curve di Genius.fun (bukan Graduated), MC $3,46K, holders 6, 24H -3,46%, progres 2,78%, umur 7 hari — identik dengan run 1142 ($3,46K/6/-3,46%/2,78%/7 hari); tetap distribution watch, BUKAN sinyal entry; tidak dilaporkan ke user."

assert len(st["runs"]) == n_runs_before + 1, "runs count mismatch"
assert len(st["reported_signals"]) == n_sig_before, "reported_signals changed!"

tmp = STATE + ".tmp"
with open(tmp, "w") as f:
    json.dump(st, f, indent=1, ensure_ascii=False)
os.replace(tmp, STATE)
print(f"OK run 1144 written: runs {n_runs_before} -> {len(st['runs'])}, "
      f"reported_signals unchanged at {n_sig_before}, "
      f"distribution_watch now {len(st['distribution_watch'])}")
