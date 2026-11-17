#!/usr/bin/env python3
"""Update holder-watch state for run 2026-11-14 ~12:30 WIB.
- Backup state -> holder-watch-state.json.bak-run-1230-20261114
- Append run record (streak detail tidak terbaca: 100)
- Add update_12:35_2026_11_14 to the two open signals (视界之眼, 爪子)
"""
import json, shutil, sys

STATE = "/home/hatch/workspace/narrative-pulse/holder-watch-state.json"
BAK = STATE + ".bak-run-1230-20261114"
BLOCK = 133488134

shutil.copy2(STATE, BAK)
s = json.load(open(STATE, encoding="utf-8"))

run_record = {
    "run": "2026-11-14 12:30 WIB (jadwal) — observasi browser 12:31-12:32 WIB; cek on-chain ~12:31 WIB (blok 133488134 via bsc-dataseed1.binance.org)",
    "mode": "B (kedua halaman dompet GMGN login-gated; tanpa percobaan login)",
    "gmgn_login_gated": [
        "0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6",
        "0xd392967fc834d718f4f9627fc5552881d1048727",
    ],
    "money_flow_signal": "TIDAK TERVERIFIKASI — detail aktivitas GMGN tidak terbaca; bukan klaim tidak ada pembelian baru. Benchmark tetap ~04:40 WIB 2026-11-06. Streak detail tidak terbaca: 100.",
    "onchain": "28/28 saldo terverifikasi, 0 BERUBAH vs run 10:30 WIB, 0 gagal baca (blok 133488134). Dompet A: ok 840.175,64; wangcai 851.502,39; shijiezhiyan 467.285,97; zhaozi 213.952,71; lulu 163.065,68; goerem 195.200,00; jixiang 200.039,83; pituo 242.680,21; huadiweilao 143.777,03; 1113 153.480,93; lina 228.874,33; mangxiaoliu 221.568,62; tertutup tetap 0: KIM, MMGA, Kim, yueqiu-tu, bi-an-bisheng, yangwang, dagou, bi-an-yizhi-zai, xiaohuangshu, Flap. Dompet B: MSX 0; AiPro 210.844,93; bi-an-gongzhu 0; True-0x9d46 0; True-0x6406 0; bibi 0. Kedua kaki Dompet A (ok + wangcai) tetap 100% hold TERKONFIRMASI on-chain — tetap 2/3.",
    "promotion": "TIDAK ADA",
}
s.setdefault("runs", []).append(run_record)

tmpl = ("Masih TERBUKA 100%: saldo on-chain {bal} token TIDAK BERUBAH (blok {blk}). "
        "GMGN login-gated run ini (12:31 WIB, terkonfirmasi pengamatan ulang setelah reload) — "
        "nilai $ GMGN TIDAK terbarui; saldo on-chain TIDAK BERUBAH, tidak ada penjualan. "
        "Bukan klaim tidak ada aktivitas baru (detail GMGN tidak terbaca).")
targets = {
    "视界之眼": "467.285,97",
    "爪子": "213.952,71",
}
done = []
for sig in s["money_flow_signals"]:
    tok = sig.get("token", "")
    if tok in targets:
        sig["update_12:35_2026_11_14"] = tmpl.format(bal=targets[tok], blk=BLOCK)
        done.append(tok)
if sorted(done) != sorted(targets):
    print("PERINGATAN: sinyal tidak lengkap:", done, file=sys.stderr)
    sys.exit(1)

json.dump(s, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# verify reload
s2 = json.load(open(STATE, encoding="utf-8"))
print("runs:", len(s2["runs"]), "| last run:", s2["runs"][-1]["run"][:40])
print("updated signals:", done)
