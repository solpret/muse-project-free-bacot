#!/usr/bin/env python3
"""Update holder-watch-state.json untuk run terjadwal 2026-11-15 ~18:30 WIB.
Pola run sebelumnya: tambah kunci update_18:35_2026_11_15 pada dua sinyal
terbuka Dompet A (视界之眼, 爪子), perbarui field top-level (last_run,
streak, last_run_note) dan tambah entri runs. Backup dulu.
GMGN: kedua halaman dompet login-gated (18:31 WIB, tugas browser
browser-task:40f0995e-3d63-581e-9df1-3920e7cacbc7, 18:30-18:31 WIB);
cek on-chain: 28/28, 0 berubah, blok 133728008 via bsc-dataseed1.
KOREKSI: run 16:30 WIB sebelumnya memperbarui sinyal + watchlist (streak
114, blok 133712081) tetapi TIDAK memperbarui field top-level state
(last_run tetap 14:30, streak 113) dan TIDAK menambah entri runs — entri
runs 16:30 di-backfill di sini dari entri watchlist.md agar urutan lengkap."""
import json
import shutil

STATE = "/home/hatch/workspace/narrative-pulse/holder-watch-state.json"
BAK = "/home/hatch/workspace/narrative-pulse/holder-watch-state.json.bak-run-1830-20261115"

shutil.copyfile(STATE, BAK)
s = json.load(open(STATE))

BLOCK = 133728008
ONCHAIN = ("28/28 saldo terverifikasi, 0 BERUBAH vs run 16:30 WIB, 0 gagal baca "
           "(blok 133728008). Dompet A: ok 840.175,64; wangcai 851.502,39; "
           "shijiezhiyan 467.285,97; zhaozi 213.952,71; lulu 163.065,68; "
           "goerem 195.200,00; jixiang 200.039,83; pituo 242.680,21; "
           "huadiweilao 143.777,03; 1113 153.480,93; lina 228.874,33; "
           "mangxiaoliu 221.568,62; tertutup tetap 0: KIM, MMGA, Kim, "
           "yueqiu-tu, bi-an-bisheng, yangwang, dagou, bi-an-yizhi-zai, "
           "xiaohuangshu, Flap. Dompet B: MSX 0 (tetap 0 sejak keluar penuh "
           "run 04:30 WIB 2026-11-12); AiPro 210.844,93; bi-an-gongzhu 0 "
           "(tetap 0 sejak keluar penuh run 04:30 WIB 2026-11-12); "
           "True-0x9d46 0; True-0x6406 0; bibi 0. "
           "Kedua kaki Dompet A (ok + wangcai) tetap 100% hold TERKONFIRMASI "
           "on-chain — tetap 2/3.")

def sig_update(balance):
    return (f"Masih TERBUKA 100%: saldo on-chain {balance} token TIDAK BERUBAH "
            f"(blok {BLOCK}). GMGN login-gated run ini (18:31 WIB) — nilai $ GMGN "
            "TIDAK terbarui; saldo on-chain TIDAK BERUBAH, tidak ada penjualan. "
            "Bukan klaim tidak ada aktivitas baru (detail GMGN tidak terbaca).")

for sig in s["money_flow_signals"]:
    if sig.get("token") == "视界之眼":
        sig["update_18:35_2026_11_15"] = sig_update("467.285,97")
    elif sig.get("token") == "爪子":
        sig["update_18:35_2026_11_15"] = sig_update("213.952,71")

# Backfill entri runs 16:30 yang terlewat pada run sebelumnya.
if not any("2026-11-15 16:30" in r.get("run", "") for r in s.get("runs", [])):
    s.setdefault("runs", []).append({
        "run": "2026-11-15 16:30 WIB (jadwal) — observasi browser 16:32 WIB; cek on-chain ~16:33 WIB (blok 133712081 via bsc-dataseed1.binance.org)",
        "mode": "B (kedua halaman dompet GMGN login-gated; tanpa percobaan login)",
        "gmgn_login_gated": ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6",
                             "0xd392967fc834d718f4f9627fc5552881d1048727"],
        "money_flow_signal": ("TIDAK TERVERIFIKASI — detail aktivitas GMGN tidak terbaca; "
                              "bukan klaim tidak ada pembelian baru. Benchmark tetap "
                              "~04:40 WIB 2026-11-06. Streak detail tidak terbaca: 114."),
        "onchain": ("28/28 saldo terverifikasi, 0 BERUBAH vs run 14:30 WIB, 0 gagal baca "
                    "(blok 133712081). Dompet A: ok 840.175,64; wangcai 851.502,39; "
                    "shijiezhiyan 467.285,97; zhaozi 213.952,71; lulu 163.065,68; "
                    "goerem 195.200,00; jixiang 200.039,83; pituo 242.680,21; "
                    "huadiweilao 143.777,03; 1113 153.480,93; lina 228.874,33; "
                    "mangxiaoliu 221.568,62; tertutup tetap 0: KIM, MMGA, Kim, "
                    "yueqiu-tu, bi-an-bisheng, yangwang, dagou, bi-an-yizhi-zai, "
                    "xiaohuangshu, Flap. Dompet B: MSX 0; AiPro 210.844,93; "
                    "bi-an-gongzhu 0; True-0x9d46 0; True-0x6406 0; bibi 0. "
                    "Kedua kaki Dompet A (ok + wangcai) tetap 100% hold TERKONFIRMASI "
                    "on-chain — tetap 2/3."),
        "promotion": "TIDAK ADA",
    })

s["unread_detail_streak"] = 115
s["detail_unread_streak"] = 115
s["last_run"] = "2026-11-15 18:30 WIB"
s["next_benchmark"] = "~04:40 WIB 2026-11-06"
s["last_run_note"] = ("GMGN login-gated (streak 115); RPC publik normal — 28/28 saldo "
                      "terverifikasi, 0 berubah, blok 133728008 via "
                      "bsc-dataseed1.binance.org. Kedua kaki Dompet A tetap 100% "
                      "hold — tetap 2/3.")

s.setdefault("runs", []).append({
    "run": "2026-11-15 18:30 WIB (jadwal) — observasi browser 18:31 WIB (browser-task:40f0995e-3d63-581e-9df1-3920e7cacbc7, 18:30-18:31 WIB); cek on-chain ~18:31 WIB (blok 133728008 via bsc-dataseed1.binance.org)",
    "mode": "B (kedua halaman dompet GMGN login-gated; tanpa percobaan login)",
    "gmgn_login_gated": ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6",
                         "0xd392967fc834d718f4f9627fc5552881d1048727"],
    "money_flow_signal": ("TIDAK TERVERIFIKASI — detail aktivitas GMGN tidak terbaca; "
                          "bukan klaim tidak ada pembelian baru. Benchmark tetap "
                          "~04:40 WIB 2026-11-06. Streak detail tidak terbaca: 115."),
    "onchain": ONCHAIN,
    "promotion": "TIDAK ADA",
})

with open(STATE, "w") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
    f.write("\n")

print("state updated: streak=115, block=133728008, backup=", BAK)
