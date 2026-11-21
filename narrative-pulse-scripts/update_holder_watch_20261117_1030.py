#!/usr/bin/env python3
"""Update holder-watch state + log untuk run terjadwal 2026-11-17 ~10:30 WIB.

Pola run sebelumnya: GMGN login-gated kedua dompet (browser-task
38e8a692-11ba-532a-b4c7-d7bdba7d55bc, 10:31-10:32 WIB, observasi 10:31 WIB,
reload sekali per halaman, dinding tetap); cek on-chain paralel 28/28,
0 berubah, blok 134047985 via bsc-dataseed1.binance.org. Streak detail
tidak terbaca: 133 -> 134. Tanpa percobaan login, tanpa wallet/signing.
"""
import json
import shutil
from pathlib import Path

BASE = Path.home() / "workspace" / "narrative-pulse"
STATE = BASE / "holder-watch-state.json"
LOG = BASE / "holder-watchlist.md"
DAILY = Path.home() / "memory" / "2026-11-17.md"

BLOCK = 134047985
STREAK = 134

# --- backup state ---
shutil.copy2(STATE, BASE / "holder-watch-state.json.bak-run-1030-20261117")

s = json.loads(STATE.read_text())

s["last_run"] = {
    "time": "2026-11-17 ~10:30 WIB",
    "gmgn": "login-gated kedua dompet (10:31-10:32 WIB, browser-task:38e8a692-11ba-532a-b4c7-d7bdba7d55bc)",
    "onchain_block": BLOCK,
    "balances_checked": 28,
    "balances_changed": 0,
    "balances_failed": 0,
    "streak_unread_detail": STREAK,
    "money_flow_signal_new": False,
}
s["last_run_note"] = (
    f"GMGN login-gated (streak {STREAK}); 28/28 saldo terverifikasi on-chain, "
    f"0 berubah (blok {BLOCK} via bsc-dataseed1.binance.org). "
    "Kedua kaki Dompet A tetap 100% hold — tetap 2/3."
)
s["unread_detail_streak"] = STREAK
s["detail_unread_streak"] = STREAK

s["money_flow_signals"][1]["update_10:35_2026_11_17"] = (
    "Masih TERBUKA 100%: saldo on-chain 467.285,97 token TIDAK BERUBAH "
    f"(blok {BLOCK}). GMGN login-gated run ini (10:31 WIB) — nilai $ GMGN "
    "TIDAK terbarui; saldo on-chain TIDAK BERUBAH "
    f"(blok {BLOCK}), tidak ada penjualan. Bukan klaim tidak ada aktivitas "
    "baru (detail GMGN tidak terbaca)."
)
s["money_flow_signals"][3]["update_10:35_2026_11_17"] = (
    "Masih TERBUKA 100%: saldo on-chain 213.952,71 token TIDAK BERUBAH "
    f"(blok {BLOCK}). GMGN login-gated run ini (10:31 WIB) — nilai $ GMGN "
    "TIDAK terbarui; saldo on-chain TIDAK BERUBAH "
    f"(blok {BLOCK}), tidak ada penjualan. Bukan klaim tidak ada aktivitas "
    "baru (detail GMGN tidak terbaca)."
)

STATE.write_text(json.dumps(s, ensure_ascii=False, indent=1) + "\n")

# --- log run ---
entry = f"""
## Log run terjadwal 2026-11-17 ~10:30 WIB (observasi browser 10:31-10:32 WIB; cek on-chain ~10:31 WIB, blok {BLOCK})
- MODE B: kedua halaman dompet GMGN LOGIN-GATED ("You are not logged in to GMGN", tombol "Log In"; Dompet A 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 dan Dompet B 0xd392967fc834d718f4f9627fc5552881d1048727, terkonfirmasi pengamatan ulang setelah reload sekali), tanpa percobaan login. Fokus = aktivitas wallet beralamat lengkap; cek hold di bawah ini HANYA interim dan BUKAN sinyal arah uang.
- MODE B — AKTIVITAS WALLET sejak benchmark ~04:40 WIB 2026-11-06: TIDAK TERVERIFIKASI di run ini (detail aktivitas GMGN tidak terbaca). Ini BUKAN klaim "tidak ada pembelian baru". Benchmark untuk run berikutnya TETAP ~04:40 WIB 2026-11-06. Streak detail tidak terbaca: {STREAK}.
- MONEY-FLOW SIGNAL: TIDAK ADA yang baru di run ini (tidak ada yang terverifikasi). Data GMGN adalah agregat (data sekunder), bukan bukti on-chain mentah.
- CEK ON-CHAIN READ-ONLY (holder-balance-check-parallel.py, blok {BLOCK} via bsc-dataseed1.binance.org): 28/28 saldo terverifikasi, 0 BERUBAH vs run 08:30 WIB 2026-11-17, 0 gagal baca. Dompet A: ok 840.175,64; wangcai 851.502,39; shijiezhiyan 467.285,97; zhaozi 213.952,71; lulu 163.065,68; goerem 195.200,00; jixiang 200.039,83; pituo 242.680,21; huadiweilao 143.777,03; 1113 153.480,93; lina 228.874,33; mangxiaoliu 221.568,62; tertutup tetap 0: KIM, MMGA, Kim, yueqiu-tu, bi-an-bisheng, yangwang, dagou, bi-an-yizhi-zai, xiaohuangshu, Flap. Dompet B: MSX 0 (tetap 0 sejak keluar penuh run 04:30 WIB 2026-11-12); AiPro 210.844,93; bi-an-gongzhu 0; True-0x9d46 0; True-0x6406 0; bibi 0. Kedua kaki Dompet A (ok + wangcai) tetap 100% hold TERKONFIRMASI on-chain — tetap 2/3. Jual-vs-transfer MSX, bi-an-gongzhu, dan kedua True Dompet B TETAP BELUM dibedakan (detail GMGN login-gated) — harga/waktu/keuntungan keluar TIDAK dilaporkan, jangan ditebak. Catatan batas: saldo tidak berubah pada token-token terlacak tidak menyingkirkan kemungkinan buy+sell token lain yang tidak terlacak, atau buy token baru yang sudah dijual habis sebelum cek ini — pembeda itu menunggu detail aktivitas GMGN.
- HOLD INTERIM (GMGN): TIDAK TERBACA di run ini — tidak ada angka rank/nilai/% baru yang dilaporkan; status terakhir yang berlaku tetap dari run 08:30 WIB 2026-11-16.
- PROMOSI: TIDAK ADA (tertinggi tetap 0x8e...b8d6 di 2/3; butuh token ketiga + PnL terealisasi 30 hari + keputusan user). Run SENYAP ke chat sesuai aturan.
- TINDAK LANJUT run berikutnya (~12:30 WIB): ulangi Mode B penuh dengan benchmark tetap ~04:40 WIB 2026-11-06; bila halaman kembali login-gated, lanjutkan streak dan andalkan cek on-chain kaki terlacak (pakai holder-balance-check-parallel.py); bila detail GMGN terbaca kembali, bedakan jual-vs-transfer untuk MSX + bi-an-gongzhu Dompet B dan kedua True Dompet B (harga/waktu keluar).
"""
with LOG.open("a") as f:
    f.write(entry)

# --- log harian ---
daily_entry = (
    f"\n- [holder-candidate-watch 10:30 WIB] Mode B: GMGN login-gated kedua dompet "
    f"(observasi 10:31-10:32 WIB, streak detail tidak terbaca {STREAK}); sinyal arah uang "
    f"TIDAK TERVERIFIKASI (bukan klaim tidak ada pembelian baru). On-chain 28/28 "
    f"saldo, 0 berubah, blok {BLOCK}. Dompet A tetap 2/3 (ok + wangcai 100% hold). "
    "Promosi: tidak ada. Run senyap ke chat.\n"
)
with DAILY.open("a") as f:
    f.write(daily_entry)

print("state + log + daily updated; streak", STREAK, "block", BLOCK)
