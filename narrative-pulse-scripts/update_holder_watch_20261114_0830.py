#!/usr/bin/env python3
"""Update holder-watch-state.json untuk run terjadwal 2026-11-14 ~08:30 WIB.
Pola run sebelumnya: backup dulu, tambah entri runs, tambah update_08:35
ke sinyal terbuka 视界之眼 + 爪子, naikkan streak 97 -> 98."""
import json, shutil

P = "/home/hatch/workspace/narrative-pulse/holder-watch-state.json"
shutil.copyfile(P, P + ".bak-run-0830-20261114")

with open(P) as f:
    s = json.load(f)

assert s["unread_detail_streak"] == 97, s["unread_detail_streak"]
assert s["last_run"] == "2026-11-14 06:30 WIB", s["last_run"]
assert len(s["runs"]) == 143, len(s["runs"])

BLOCK = 133456203
ONCHAIN = ("28/28 saldo terverifikasi, 0 BERUBAH vs run 06:30 WIB, 0 gagal baca "
           f"(blok {BLOCK}). Dompet A: ok 840.175,64; wangcai 851.502,39; "
           "shijiezhiyan 467.285,97; zhaozi 213.952,71; lulu 163.065,68; "
           "goerem 195.200,00; jixiang 200.039,83; pituo 242.680,21; "
           "huadiweilao 143.777,03; 1113 153.480,93; lina 228.874,33; "
           "mangxiaoliu 221.568,62; tertutup tetap 0: KIM, MMGA, Kim, "
           "yueqiu-tu, bi-an-bisheng, yangwang, dagou, bi-an-yizhi-zai, "
           "xiaohuangshu, Flap. Dompet B: MSX 0; AiPro 210.844,93; "
           "bi-an-gongzhu 0; True-0x9d46 0; True-0x6406 0; bibi 0. "
           "Kedua kaki Dompet A (ok + wangcai) tetap 100% hold TERKONFIRMASI "
           "on-chain — tetap 2/3.")

s["runs"].append({
    "run": "2026-11-14 08:30 WIB (jadwal) — observasi browser 08:31-08:32 WIB; "
            f"cek on-chain ~08:31 WIB (blok {BLOCK} via bsc-dataseed1.binance.org)",
    "mode": "B (kedua halaman dompet GMGN login-gated; tanpa percobaan login)",
    "gmgn_login_gated": [
        "0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6",
        "0xd392967fc834d718f4f9627fc5552881d1048727",
    ],
    "money_flow_signal": "TIDAK TERVERIFIKASI — detail aktivitas GMGN tidak terbaca; "
                         "bukan klaim tidak ada pembelian baru. Benchmark tetap "
                         "~04:40 WIB 2026-11-06. Streak detail tidak terbaca: 98.",
    "onchain": ONCHAIN,
    "promotion": "TIDAK ADA",
})

def find_signal(token):
    for m in s["money_flow_signals"]:
        if m.get("token") == token:
            return m
    raise SystemExit(f"signal {token} not found")

sj = find_signal("视界之眼")
assert "update_06:35_2026_11_14" in sj
sj["update_08:35_2026_11_14"] = (
    "Masih TERBUKA 100%: saldo on-chain 467.285,97 token TIDAK BERUBAH "
    f"(blok {BLOCK}). GMGN login-gated run ini (08:31 WIB, terkonfirmasi "
    "pengamatan ulang setelah reload) — nilai $ GMGN TIDAK terbarui; saldo "
    "on-chain TIDAK BERUBAH, tidak ada penjualan. Bukan klaim tidak ada "
    "aktivitas baru (detail GMGN tidak terbaca).")

zz = find_signal("爪子")
assert "update_06:35_2026_11_14" in zz
zz["update_08:35_2026_11_14"] = (
    "Masih TERBUKA 100%: saldo on-chain 213.952,71 token TIDAK BERUBAH "
    f"(blok {BLOCK}). GMGN login-gated run ini (08:31 WIB, terkonfirmasi "
    "pengamatan ulang setelah reload) — nilai $ GMGN TIDAK terbarui; saldo "
    "on-chain TIDAK BERUBAH, tidak ada penjualan. Bukan klaim tidak ada "
    "aktivitas baru (detail GMGN tidak terbaca).")

s["unread_detail_streak"] = 98
s["detail_unread_streak"] = 98
s["last_run"] = "2026-11-14 08:30 WIB"
s["last_run_note"] = (
    "GMGN login-gated (streak 98); RPC publik normal — 28/28 saldo "
    f"terverifikasi, 0 berubah, blok {BLOCK} via bsc-dataseed1.binance.org. "
    "Kedua kaki Dompet A tetap 100% hold — tetap 2/3.")

with open(P, "w") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)

with open(P) as f:
    s2 = json.load(f)
assert len(s2["runs"]) == 144
assert s2["unread_detail_streak"] == 98
for tok in ("视界之眼", "爪子"):
    m = next(x for x in s2["money_flow_signals"] if x.get("token") == tok)
    assert "update_08:35_2026_11_14" in m, tok
print("OK state updated; runs:", len(s2["runs"]), "streak:", s2["unread_detail_streak"])
