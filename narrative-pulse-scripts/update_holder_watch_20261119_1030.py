#!/usr/bin/env python3
"""Update holder-watch state + log untuk run terjadwal 2026-11-19 ~10:30 WIB.

Pola run sebelumnya: GMGN login-gated kedua dompet (browser-task
4af26a22-c542-58dc-99e7-c7ad50c5b6b2, observasi 10:31-10:32 WIB, reload
sekali per halaman, dinding tetap); RPC PUBLIK PULIH run ini
(holder-balance-check-parallel.py ~34 dtk, 28/28 via
bsc-dataseed1.binance.org, blok 134431777) — tanpa fallback QuickNode.
Streak detail tidak terbaca: 157 -> 158. Tanpa percobaan login,
tanpa wallet/signing.
"""
import json
import shutil
from pathlib import Path

BASE = Path.home() / "workspace" / "narrative-pulse"
STATE = BASE / "holder-watch-state.json"
LOG = BASE / "holder-watchlist.md"
DAILY = Path.home() / "memory" / "2026-11-19.md"

BLOCK = 134431777
STREAK = 158

# --- backup state ---
shutil.copy2(STATE, BASE / "holder-watch-state.json.bak-run-1030-20261119")

s = json.loads(STATE.read_text())

s["last_run"] = "2026-11-19T10:35:00+07:00"
s["last_run_block"] = BLOCK
s["last_run_unread_streak"] = STREAK
s["last_run_note"] = (
    f"GMGN login-gated (streak {STREAK}); RPC publik PULIH run ini — cek "
    f"on-chain langsung via bsc-dataseed1: 28/28 saldo terverifikasi, 0 berubah "
    f"(blok {BLOCK}), tanpa fallback QuickNode."
)
s["unread_detail_streak"] = STREAK
s["detail_unread_streak"] = STREAK
s["runs"].append({
    "run": "2026-11-19 10:30 WIB",
    "block": BLOCK,
    "gmgn": "login-gated",
    "streak": STREAK,
    "changed": 0,
    "failed_after_retry": 0,
    "rpc_publik": "PULIH (holder-balance-check-parallel.py ~34 dtk, 28/28 via bsc-dataseed1.binance.org)",
    "fallback": "tidak diperlukan",
})

s["money_flow_signals"][1]["update_10:35_2026_11_19"] = (
    "Masih TERBUKA 100%: saldo on-chain 467.285,97 token TIDAK BERUBAH "
    f"(blok {BLOCK}) — terverifikasi via RPC publik yang pulih run ini "
    "(bsc-dataseed1, 28/28, tanpa fallback). GMGN login-gated run ini "
    "(10:31-10:32 WIB, terkonfirmasi pengamatan ulang setelah reload) — nilai "
    "$ GMGN TIDAK terbarui; saldo on-chain TIDAK BERUBAH, tidak ada penjualan. "
    "Bukan klaim tidak ada aktivitas baru (detail GMGN tidak terbaca)."
)

STATE.write_text(json.dumps(s, ensure_ascii=False, indent=1) + "\n")

# --- log run ---
entry = f"""
## Log run terjadwal 2026-11-19 ~10:30 WIB (observasi browser 10:31-10:32 WIB; cek on-chain ~10:31-10:32 WIB, blok {BLOCK} via bsc-dataseed1)
- MODE B: kedua halaman dompet GMGN LOGIN-GATED ("You are not logged in to GMGN", tombol "Log In"; Dompet A 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 dan Dompet B 0xd392967fc834d718f4f9627fc5552881d1048727, terkonfirmasi pengamatan ulang setelah reload sekali), tanpa percobaan login. Fokus = aktivitas wallet beralamat lengkap; cek hold di bawah ini HANYA interim dan BUKAN sinyal arah uang.
- MODE B — AKTIVITAS WALLET sejak benchmark ~04:40 WIB 2026-11-06: TIDAK TERVERIFIKASI di run ini (detail aktivitas GMGN tidak terbaca). Ini BUKAN klaim "tidak ada pembelian baru". Benchmark untuk run berikutnya TETAP ~04:40 WIB 2026-11-06. Streak detail tidak terbaca: {STREAK}.
- MONEY-FLOW SIGNAL: TIDAK ADA yang baru di run ini (tidak ada yang terverifikasi). Data GMGN adalah agregat (data sekunder), bukan bukti on-chain mentah.
- CEK ON-CHAIN READ-ONLY: RPC PUBLIK PULIH run ini — holder-balance-check-parallel.py selesai ~34 dtk (blok {BLOCK} via bsc-dataseed1.binance.org): 28/28 saldo terverifikasi, 0 BERUBAH vs run 08:30 WIB 2026-11-19, 0 gagal baca; fallback QuickNode TIDAK diperlukan. Dompet A: ok 840.175,64; wangcai 851.502,39; shijiezhiyan 467.285,97; zhaozi 213.952,71; lulu 163.065,68; goerem 195.200,00; jixiang 200.039,83; pituo 242.680,21; huadiweilao 143.777,03; 1113 153.480,93; lina 228.874,33; mangxiaoliu 221.568,62; tertutup tetap 0: KIM, MMGA, Kim, yueqiu-tu, bi-an-bisheng, yangwang, dagou, bi-an-yizhi-zai, xiaohuangshu, Flap. Dompet B: MSX 0 (tetap 0 sejak keluar penuh run 04:30 WIB 2026-11-12); AiPro 210.844,93; bi-an-gongzhu 0; True-0x9d46 0; True-0x6406 0; bibi 0. Kedua kaki Dompet A (ok + wangcai) tetap 100% hold TERKONFIRMASI on-chain — tetap 2/3. Jual-vs-transfer MSX, bi-an-gongzhu, dan kedua True Dompet B TETAP BELUM dibedakan (detail GMGN login-gated) — harga/waktu/keuntungan keluar TIDAK dilaporkan, jangan ditebak. Catatan batas: saldo tidak berubah pada token-token terlacak tidak menyingkirkan kemungkinan buy+sell token lain yang tidak terlacak, atau buy token baru yang sudah dijual habis sebelum cek ini — pembeda itu menunggu detail aktivitas GMGN.
- HOLD INTERIM (GMGN): TIDAK TERBACA di run ini — tidak ada angka rank/nilai/% baru yang dilaporkan; status terakhir yang berlaku tetap dari run 08:30 WIB 2026-11-16.
- PROMOSI: TIDAK ADA (tertinggi tetap 0x8e...b8d6 di 2/3; butuh token ketiga + PnL terealisasi 30 hari + keputusan user). Run SENYAP ke chat sesuai aturan.
- TINDAK LANJUT run berikutnya (~12:30 WIB): ulangi Mode B penuh dengan benchmark tetap ~04:40 WIB 2026-11-06; bila halaman kembali login-gated, lanjutkan streak dan andalkan cek on-chain kaki terlacak (pakai holder-balance-check-parallel.py; bila RPC publik gagal total, pakai fallback holder-balance-check-quicknode.py); bila detail GMGN terbaca kembali, bedakan jual-vs-transfer untuk MSX + bi-an-gongzhu Dompet B dan kedua True Dompet B (harga/waktu keluar).
"""
with LOG.open("a") as f:
    f.write(entry)

# --- log harian ---
daily_entry = (
    f"\n- [holder-candidate-watch 10:30 WIB] Mode B: GMGN login-gated kedua dompet "
    f"(observasi 10:31-10:32 WIB, streak detail tidak terbaca {STREAK}); sinyal arah uang "
    f"TIDAK TERVERIFIKASI (bukan klaim tidak ada pembelian baru). RPC publik PULIH "
    f"(parallel ~34 dtk via bsc-dataseed1, tanpa fallback): 28/28 saldo "
    f"terverifikasi, 0 berubah (blok {BLOCK}). Kedua kaki Dompet A tetap 100% "
    f"hold — tetap 2/3. Tanpa promosi; run senyap."
)
with DAILY.open("a") as f:
    f.write(daily_entry)

print(f"OK state+log+diary diperbarui (blok {BLOCK}, streak {STREAK})")
