import json, shutil
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
# backups
for f in ["onchain-snapshot.json","onchain-scan-state.json"]:
    shutil.copy(f"{BASE}/{f}", f"{BASE}/{f}.bak-20261106-0431")
# --- scan state: FAILURE, watermark NOT advanced (next run retries same window) ---
st=json.load(open(f"{BASE}/onchain-scan-state.json"))
st["note_0431_scan_failed"]=(
 "Run 0431: SCAN GAGAL/STALL. Percobaan 1: chunk 1 selesai (18 ERC721/1 ERC1155/22 ERC20-mint) lalu CRASH "
 "IndexError di fallback TransferSingle (topic_filter[1] pada filter 1-elemen) saat kedua panggilan Ankr gagal "
 "(proxy tunnel error) - bug diperbaiki (guard len>1). Percobaan 2 (setelah fix): proses hidup 13 mnt, 3 dtk CPU, "
 "0 byte log, 0 chunk selesai, 3 socket ESTAB ke proxy tanpa respons - Ankr/proxy stall; direct ankr_getLogs test "
 "selesai 0,7 dtk di saat yang sama, jadi stall spesifik ke koneksi scan. Proses di-kill 05:14 WIB. "
 "Watermark TIDAK dimajukan (tetap 131888994); seen file TIDAK berubah; 5c dilewati (tanpa output scan). "
 "Window yang belum ter-scan: 131888995-131892758+ (gap 131888995-131890718 = 1724 blok dilewati cap 2000).")
st["last_scan_failed_wib"]="2026-11-06 run 0431"
json.dump(st, open(f"{BASE}/onchain-scan-state.json","w"), indent=1)
# --- snapshot: reread-only changes; None never overwrites ---
s=json.load(open(f"{BASE}/onchain-snapshot.json"))
r=json.load(open(f"{BASE}/run-2026-11-06-0431-reread-lean.json"))
def upd(name, **kw):
    e=s["contracts"].setdefault(name,{})
    for k,v in kw.items():
        if v is not None: e[k]=v
    return e
# Tumblebots: only real new reading this run
upd("Tumblebots", freeMinted=653, balanceOf_user=0)
s["contracts"]["Tumblebots"]["run0431_velocity"]=(
 "FAIL: freeMinted 650->653 (+3, <20 token dalam interval) -> velocity GAGAL. Status tidak berubah.")
s["contracts"]["Tumblebots"]["previousTotalSupply"]=650
s["contracts"]["Tumblebots"]["mintedInInterval"]=3
# MILLION: balanceOf fresh 0; all supply views None (RPC fail, NOT zero) - keep old
s["contracts"].setdefault("MILLION",{})["run0431_note"]=(
 "Run 0431: balanceOf(user)=0 (fresh read). SEMUA supply view tetap None (totalSupply/totalMinted/freeMinted/"
 "freeClaimed/agentRegistry = None) - degradasi RPC, BUKAN nol; nilai lama dipertahankan (totalMinted 14 saat "
 "triage 0331). Tidak ada promosi: free pool, user slot, website, X tetap UNVERIFIED. Tetap "
 "early-lead-reported-2026-11-06-run0331, TIDAK pernah di-preview/di-mint.")
# HIVE: all reads None this run - keep 1253, velocity NOT computed
s["contracts"]["HIVE Agents"]["run0431_velocity"]=(
 "Run 0431: SEMUA view gagal baca (totalSupply/totalMinted/freeClaimed/freeMinted/balanceOf = None) - degradasi "
 "RPC, BUKAN nol; nilai lama (1253) dipertahankan, velocity TIDAK dihitung. balanceOf(user) lama 1 dipertahankan. "
 "Minted-by-user; tetap dipantau.")
s["contracts"]["HIVE Agents"]["lastReadWib"]="2026-11-06 run 0431"
s["contracts"]["HIVE Agents"]["lastReadBlock"]=131888994
# Track-C run notes (no changes; reads None or unchanged - record explicitly)
t=s.setdefault("track_c",{})
notes0431={
 "DROID":"Run 0431: opened=0, semua view None kecuali totalMinted lama 584 dipertahankan - tetap watchlist-only-age-slot-unverified.",
 "IMARS":"Run 0431: opened=1, freeMinted 300/300 (pool gratis habis), totalMinted 624 - tetap watchlist-only-not-open.",
 "OSK":"Run 0431: opened=0, totalMinted 2278 - tetap watchlist-only-not-open.",
 "NIULAI":"Run 0431: launched=0, phase=4 - tetap watchlist-only-not-open.",
 "SENBAZURU-b215":"Run 0431: opened=1, hasFreeShare(user)=1 (sudah diklaim user); tidak berubah.",
 "QAGENT-2":"Run 0431: freeClaimed(user)=1 (sudah diklaim); tidak berubah.",
 "SAFUAI":"Run 0431: opened=1 (recovered read run 0401 dipertahankan); status checked-not-a-lead tidak berubah.",
 "ShibAgent-R2":"Run 0431: launched=0, phase=1; umur ~24,6 jam (start 2026-11-05 05:22 WIB) masih <=48 jam; sesi baw NOT_LOGGED_IN (sudah dilaporkan) - TIDAK ada preview/mint.",
 "DeY":"Run 0431: semua view None; umur ~36 jam (start 2026-11-04 16:46 WIB) masih <=48 jam - TIDAK di-age-exclude.",
 "FANBEIMAO-824d":"Run 0431: semua view None; umur ~33 jam (start 2026-11-04 20:00 WIB) masih <=48 jam - TIDAK di-age-exclude.",
 "NJAR":"Run 0431: umur ~13 jam (saleStart 2026-11-05 16:00 WIB) masih <=48 jam - TIDAK di-age-exclude.",
 "Predictagent-PRDICT":"Run 0431: umur ~7 jam (first Transfer 2026-11-05 21:49 WIB) masih <=48 jam - TIDAK di-age-exclude.",
 "LuckyBox-LUCK":"Run 0431: umur ~13 jam (start 2026-11-05 15:59 WIB) masih <=48 jam - TIDAK di-age-exclude.",
}
for k,v in notes0431.items():
    if k in t and isinstance(t[k], dict):
        t[k]["run0431"]=v
s["last_run_wib"]="2026-11-06 run 0431"
s["last_run"]=("Run 0431: SILENT (tidak ada kandidat/strong lead/early lead/track-C baru, tidak ada age-exclusion, "
 "tidak ada klaim). Scan GAGAL (stall proxy/Ankr, watermark tidak dimajukan). Re-read: hanya Tumblebots +3; "
 "semua view lain None (degradasi RPC).")
s["runNote0431"]=("Run 0431 (blok head 131892718, watermark scan tetap 131888994): re-read 21 NFT + 18 track-C (408 dtk, "
 "block() None - degradasi RPC); HIVE semua view None (nilai lama 1253 dipertahankan, velocity TIDAK dihitung); "
 "Tumblebots freeMinted 650->653 (+3, velocity FAIL); MILLION balanceOf 0, supply views tetap None. Track-C: "
 "tidak ada perubahan; DeY ~36 jam, FANBEIMAO ~33 jam, ShibAgent-R2 ~24,6 jam, NJAR ~13 jam, Predictagent ~7 jam, "
 "LuckyBox-LUCK ~13 jam - semua masih <=48 jam, TIDAK ada age-exclusion. Boltbook 0 hits (newest 2026-11-05T09:20:52Z). "
 "Sourcify feed 1 baru, 0 sale shape. 5c dilewati (tanpa output scan). Bridge 113 kontrak, 0 not in snapshot. "
 "Binanceai tetap refund/failed (launched 0, failed 1, isRefundPhase 1). Scan: percobaan 1 crash IndexError "
 "(bug diperbaiki), percobaan 2 stall 13 mnt 0 chunk - GAGAL, watermark tidak dimajukan. Web sweep + Square + "
 "Odaily/PANews: hanya item dikenal (AGENT MAO, Ptah, daftar 8 offers, Subsonic Tribe/BNBmeme sudah excluded).")
json.dump(s, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
print("SNAPSHOT UPDATED; track_c", len(t), "items; watermark stays 131888994")
