#!/usr/bin/env python3
"""fcfs_fast.py — poller FCFS cepat + eksekutor pre-warm untuk sale free-mint.

Pelajaran dari BTC Agent (14 Nov 2026): kuota gratis 210 habis <7 menit
(kemungkinan ~1 menit) di antara dua cek watch 2-menitan. Watch lama SUDAH
pakai satu JSON-RPC batch (~1 dtk) — kekalahan bukan di bacaan, melainkan
(1) deteksi 2 menit terlalu jarang, (2) rantai eksekusi berurutan (audit
segar -> baca ulang -> cek sesi baw -> preview -> eksekusi) terlalu lambat.

Alat ini menutup kedua lubang itu:
  1. Poller rapat: loop kontinu interval ~10-15 dtk, SATU JSON-RPC batch
     per poll (blok + saldo BNB + semua view sale). Transport urllib polos
     + fallback endpoint (fast_rpc.py TIDAK dipakai — flaky OSError lewat
     proxy, terbukti 12-14 Nov 2026).
  2. Pre-warm: audit Binance + sesi baw/devMode dicek SEBELUM sale buka
     dan di-refresh berkala (cadence lebih lambat), supaya saat pembukaan
     terdeteksi yang tersisa hanya: baca-ulang verifikasi (~1 dtk) +
     preview + eksekusi. Bila cache pre-warm basi saat trigger, audit/sesi
     di-fetch segar dulu (safety di atas speed) dan latensi ekstra dicatat.

GUARD YANG DIPERTAHANKAN (tidak ada yang dilonggarkan):
  - Hanya GRATIS: value 0; bila fungsi mint punya parameter maxCost/cost-cap,
    calldata di config HARUS sudah mengunci 0 (alat tidak pernah menaikkan).
  - Audit Binance diungkapkan: hasResult=false = TIDAK ADA HASIL, bukan
    lolos (tidak menghentikan, sesuai perluasan pre-auth 2026-11-03);
    RISK hit (isHit + riskType RISK) atau riskAlert non-null = STOP.
    Kegagalan API audit (error/timeout) = STOP (strict-scan).
  - Preview bersih: success=true, simulationCode 000000000,
    simulationErrorDetail null, value 0, authorityChanges kosong,
    allowanceChanges kosong, tanpa item riskType RISK, perubahan saldo
    sesuai harapan (expected_delta_raw). Bila struktur preview tidak
    dikenali -> dianggap kotor (fail closed).
  - Website gate HARUS sudah terverifikasi SEBELUM alat di-arm
    (website_gate_verified=true + URL + bukti di config). Tanpa itu mode
    live DITOLAK.
  - JANGAN PERNAH retry sesudah execute. JANGAN PERNAH paid mint.
  - TIDAK PERNAH eksekusi dari data basi/gagal: bila batch poll gagal,
    state terakhir dipertahankan dan loop lanjut tanpa eksekusi.

KEAMANAN MODE: default = dry-run (poll + pre-warm saja, TIDAK PERNAH
preview/execute). Mode live butuh DUA syarat sekaligus: config
"dry_run": false DAN flag CLI --live. Tanpa keduanya, trigger hanya
dicatat.

Pakai:
  python3 fcfs_fast.py --config sale.json --once
      # satu poll + satu pre-warm, cetak, keluar (sanity check arming)
  python3 fcfs_fast.py --config sale.json --dry-run --duration-s 300
      # loop dry-run 5 menit (poll + pre-warm; trigger hanya dicatat)
  python3 fcfs_fast.py --config sale.json --live
      # ARMED: loop sampai kondisi terminal (sukses / kuota habis /
      # gagal / sudah klaim / audit RISK / preview kotor / execute error)
  python3 fcfs_fast.py --config sale.json --live --wait-until 2026-11-16T19:00:00+07:00
      # ARMED LANGSUNG saat keputusan dibuat (prosedur A+C, 15 Nov 2026):
      # loop hidup sejak sekarang, poll saja sampai waktu buka, live
      # sesudahnya. JANGAN arm via runonce cron — blackout throttle
      # 15 Nov 2026 (18:45-20:54 WIB, 287 run di-skip) membuktikan satu
      # eksekusi cron bisa di-skip diam-diam. --wait-until menerima ISO
      # 8601 (dengan zona waktu, atau naive = WIB) atau epoch detik;
      # nilai di masa lalu = live langsung. Selama menunggu, trigger
      # TIDAK dievaluasi (tanpa preview/execute), tapi kondisi terminal
      # (kuota habis / gagal / slot terpakai) tetap dicek tiap poll.
  python3 fcfs_fast.py --selftest
      # uji offline: validasi config, evaluasi trigger, parsing audit
      # dan preview dari fixture, parsing --wait-until — tanpa jaringan.

Loop ini MATI bila VM restart — watchdog cron fcfs-fast-watchdog
(2-menitan) menyalakan ulang dari pointer armed-sale.json; restart
memakai flag yang sama dengan arming awal (termasuk --wait-until bila
ada di pointer). Lihat FCFS_FAST.md untuk prosedur arming.

Read-only kecuali di jalur eksekusi live: poll + audit + cek sesi adalah
baca saja. Preview adalah simulasi (tidak broadcast). Hanya `execute`
yang menyiarkan transaksi — dan itu terjadi SATU kali, tanpa retry.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone

WIB = timezone(timedelta(hours=7))
BAW = os.path.expanduser("~/workspace/.baw-cli/bin/baw")
AUDIT_URL = ("https://web3.binance.com/bapi/defi/v1/public/wallet-direct/"
             "security/token/audit")

ENDPOINTS = [
    "https://bsc-dataseed.binance.org/",
    "https://bsc-dataseed1.bnbchain.org/",
    "https://bsc-dataseed2.bnbchain.org/",
    "https://bsc-dataseed1.defibit.io/",
    "https://bsc.drpc.org/",
]
RPC_TIMEOUT = 10
AUDIT_TIMEOUT = 20
BAW_TIMEOUT = 120


def _now_wib():
    return datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S WIB")


def parse_wait_until(value):
    """Parse --wait-until: ISO 8601 (dengan zona waktu, atau naive =
    WIB) atau epoch detik. Kembalikan epoch int; raise ValueError bila
    tidak dikenali."""
    s = str(value).strip()
    if s.isdigit():
        return int(s)
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(f"--wait-until tidak dikenali: {value!r} "
                         f"(pakai ISO 8601, mis. 2026-11-16T19:00:00+07:00, "
                         f"atau epoch detik)")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=WIB)
    return int(dt.timestamp())


def is_waiting(wait_until_epoch, now=None):
    """True bila masih sebelum waktu buka (mode tunggu aktif)."""
    if wait_until_epoch is None:
        return False
    return int(now or time.time()) < wait_until_epoch


def terminal_from_poll(cfg, poll):
    """Kondisi terminal dari poll segar (kuota habis / gagal / slot
    terpakai). Kembalikan string terminal atau None. Dipakai di jalur
    live maupun jalur tunggu (--wait-until) — sale yang sudah habis
    sebelum waktu buka tidak perlu ditunggu."""
    rem = free_remaining(cfg, poll)
    vals = poll["values"]
    if rem is not None and rem <= 0:
        return "terminal: kuota gratis habis"
    if vals.get("failed") is True:
        return "terminal: sale failed/refund phase"
    if vals.get("freeDone") is True:
        return "terminal: slot user sudah terpakai"
    return None


def _arg_addr(a):
    return a[2:].lower().rjust(64, "0")


def _u256(hexstr):
    if hexstr is None or hexstr == "0x":
        return None
    return int(hexstr, 16)


class Log:
    """Tulis ke stdout + file log (append)."""

    def __init__(self, path=None):
        self.path = path
        self.fh = None
        if path:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            self.fh = open(path, "a", encoding="utf-8")

    def write(self, msg):
        line = f"[{_now_wib()}] {msg}"
        print(line, flush=True)
        if self.fh:
            self.fh.write(line + "\n")
            self.fh.flush()

    def close(self):
        if self.fh:
            self.fh.close()


def _post_json(url, payload, headers=None, timeout=10):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers=headers or {"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def rpc_batch(batch):
    """Satu batch ke endpoint pertama yang menjawab.

    Kembalikan (hasil_list, endpoint, elapsed_s) atau raise IOError.
    """
    last_err = None
    for url in ENDPOINTS:
        t0 = time.time()
        try:
            out = _post_json(url, batch, timeout=RPC_TIMEOUT)
            if not isinstance(out, list):
                raise IOError(f"{url}: respons bukan list: {str(out)[:120]}")
            return out, url, round(time.time() - t0, 2)
        except Exception as e:  # noqa: BLE001 — coba endpoint berikut
            last_err = f"{url}: {type(e).__name__}: {str(e)[:100]}"
    raise IOError("semua endpoint RPC gagal: " + (last_err or "?"))


# ---------------------------------------------------------------- config

REQUIRED_STR = ["sale_name", "agent_wallet", "mint_contract",
                "free_calldata"]
REQUIRED_INT = ["free_total", "poll_interval_s", "prewarm_interval_s"]


def load_config(path):
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    for k in REQUIRED_STR:
        v = cfg.get(k)
        if not isinstance(v, str) or not v:
            raise ValueError(f"config: '{k}' wajib string non-kosong")
    for k in REQUIRED_INT:
        if not isinstance(cfg.get(k), int) or cfg[k] <= 0:
            raise ValueError(f"config: '{k}' wajib integer > 0")
    for a in ("agent_wallet", "mint_contract"):
        if not cfg[a].startswith("0x") or len(cfg[a]) != 42:
            raise ValueError(f"config: '{a}' bukan alamat 0x 42 karakter")
    if not cfg["free_calldata"].startswith("0x"):
        raise ValueError("config: 'free_calldata' harus 0x-prefixed hex")
    calls = cfg.get("poll_calls")
    if not isinstance(calls, list) or not calls:
        raise ValueError("config: 'poll_calls' wajib list non-kosong")
    for c in calls:
        if not c.get("label") or not c.get("to") or not c.get("data"):
            raise ValueError(f"config: poll_call tidak lengkap: {c}")
        if not c["to"].startswith("0x") or not c["data"].startswith("0x"):
            raise ValueError(f"config: poll_call bukan hex: {c}")
    cfg.setdefault("chain_id", "56")
    cfg.setdefault("min_bnb_wei", 30000000000000)  # 0,00003 BNB
    cfg.setdefault("audit_ttl_s", 600)
    cfg.setdefault("audit_contracts", [cfg["mint_contract"]])
    cfg.setdefault("dry_run", True)
    cfg.setdefault("expected_delta_raw", None)
    cfg.setdefault("website_gate_verified", False)
    cfg.setdefault("website_url", "")
    cfg.setdefault("website_evidence", "")
    cfg.setdefault("session_grace_s", 120)
    return cfg


def validate_live(cfg):
    """Tolak mode live bila guard arming tidak lengkap."""
    problems = []
    if not cfg.get("website_gate_verified"):
        problems.append("website_gate_verified=false — gate website belum "
                        "terverifikasi; verifikasi situs (mencetak kontrak "
                        "persis) SEBELUM arm.")
    if not cfg.get("website_url"):
        problems.append("website_url kosong.")
    if cfg.get("dry_run", True):
        problems.append("config dry_run=true — set false untuk live.")
    return problems


# ---------------------------------------------------------------- poll

def build_poll_batch(cfg):
    """eth_blockNumber + eth_getBalance + semua poll_calls, SATU batch."""
    user = cfg["agent_wallet"]
    batch = [
        {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [],
         "id": 0},
        {"jsonrpc": "2.0", "method": "eth_getBalance",
         "params": [user, "latest"], "id": 100},
    ]
    for i, c in enumerate(cfg["poll_calls"], start=1):
        data = c["data"].replace("{user}", _arg_addr(user))
        batch.append({"jsonrpc": "2.0", "method": "eth_call",
                      "params": [{"to": c["to"], "data": data}, "latest"],
                      "id": i})
    return batch


def decode_poll(cfg, out):
    by_id = {x.get("id"): x for x in out if isinstance(x, dict)}
    block = _u256(by_id.get(0, {}).get("result"))
    bnb_raw = _u256(by_id.get(100, {}).get("result"))
    vals = {}
    for i, c in enumerate(cfg["poll_calls"], start=1):
        entry = by_id.get(i, {})
        if "error" in entry:
            raise IOError(f"{c['label']}: RPC error {entry['error']}")
        raw = _u256(entry.get("result"))
        if raw is None:
            raise IOError(f"{c['label']}: hasil kosong")
        kind = c.get("kind", "uint")
        vals[c["label"]] = bool(raw) if kind == "bool" else raw
    if block is None or bnb_raw is None:
        raise IOError(f"hasil blok/saldo kosong (block={block})")
    return {"block": block, "bnb_balance_raw": bnb_raw,
            "bnb_balance": bnb_raw / 10**18, "values": vals}


def poll_once(cfg):
    """Satu poll batch. Kembalikan dict state poll (tanpa menulis file)."""
    t0 = time.time()
    batch = build_poll_batch(cfg)
    out, endpoint, rpc_s = rpc_batch(batch)
    dec = decode_poll(cfg, out)
    dec["checked_at"] = _now_wib()
    dec["checked_at_epoch"] = int(t0)
    dec["endpoint"] = endpoint
    dec["elapsed_s"] = round(time.time() - t0, 2)
    dec["rpc_s"] = rpc_s
    return dec


def free_remaining(cfg, poll):
    """Sisa kuota gratis dari label free (default 'freeMinted')."""
    label = cfg.get("free_label", "freeMinted")
    minted = poll["values"].get(label)
    if minted is None:
        return None
    return cfg["free_total"] - minted


def trigger_met(cfg, poll):
    """True bila SEMUA kondisi trigger terpenuhi dari data poll segar."""
    trig = cfg.get("trigger", {})
    for label, want in trig.items():
        got = poll["values"].get(label)
        if got is None:
            return False, f"trigger: label '{label}' tidak ada di poll"
        if got != want:
            return False, f"trigger: {label}={got} (mau {want})"
    rem = free_remaining(cfg, poll)
    if rem is None:
        return False, "trigger: free label tidak terbaca"
    if rem <= 0:
        return False, f"trigger: kuota gratis habis ({rem})"
    bnb = poll.get("bnb_balance_raw")
    if bnb is not None and bnb < cfg["min_bnb_wei"]:
        return False, (f"trigger: saldo BNB {bnb} < minimum "
                       f"{cfg['min_bnb_wei']}")
    return True, f"trigger OK (sisa gratis {rem}, BNB {poll['bnb_balance']})"


# ---------------------------------------------------------------- audit

def fetch_audit(contract, chain_id="56"):
    """Satu POST audit Binance. Kembalikan ringkasan (tidak pernah raise
    untuk hasResult=false — itu 'tidak ada hasil', bukan error)."""
    payload = {"binanceChainId": str(chain_id),
               "contractAddress": contract,
               "requestId": str(uuid.uuid4())}
    headers = {"Content-Type": "application/json",
               "source": "agent",
               "Accept-Encoding": "identity",
               "User-Agent": "binance-web3/1.4 (Skill)"}
    try:
        resp = _post_json(AUDIT_URL, payload, headers=headers,
                          timeout=AUDIT_TIMEOUT)
    except Exception as e:  # noqa: BLE001 — kegagalan API = STOP
        return {"contract": contract, "ok": False,
                "error": f"{type(e).__name__}: {str(e)[:200]}",
                "fetched_at": int(time.time())}
    data = resp.get("data") or {}
    hits = []
    risk_alert = data.get("riskAlert")
    for item in data.get("riskItems") or []:
        for d in item.get("details") or []:
            if d.get("isHit"):
                hits.append({"id": item.get("id"),
                             "title": d.get("title"),
                             "riskType": d.get("riskType")})
    return {"contract": contract, "ok": True,
            "hasResult": bool(data.get("hasResult")),
            "riskLevel": data.get("riskLevel"),
            "riskLevelEnum": data.get("riskLevelEnum"),
            "risk_hits": hits, "riskAlert": risk_alert,
            "fetched_at": int(time.time())}


def audit_is_blocking(summary):
    """True bila audit ini MENGHENTIKAN eksekusi.

    hasResult=false TIDAK menghentikan (diungkapkan sebagai tidak ada
    hasil). Yang menghentikan: kegagalan API, RISK hit, riskAlert.
    """
    if not summary.get("ok"):
        return True, f"audit API gagal: {summary.get('error')}"
    for h in summary.get("risk_hits") or []:
        if h.get("riskType") == "RISK":
            return True, f"audit RISK hit: {h.get('id')} / {h.get('title')}"
    if summary.get("riskAlert") is not None:
        return True, f"audit riskAlert non-null: {summary['riskAlert']}"
    return False, "audit tidak memblokir"


# ---------------------------------------------------------------- baw

def baw_json(args, timeout=BAW_TIMEOUT):
    """Jalankan baw <args> --json, kembalikan dict hasil."""
    cmd = [BAW] + args + ["--json"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"{type(e).__name__}: {str(e)[:200]}"}
    try:
        out = json.loads(p.stdout)
    except Exception:  # noqa: BLE001
        return {"ok": False, "error": "output baw bukan JSON",
                "raw": (p.stdout + p.stderr)[:300]}
    out["ok"] = bool(p.returncode == 0 and out.get("success", True))
    return out


def session_check():
    """Status sesi + devMode. Read-only."""
    st = baw_json(["wallet", "status"])
    se = baw_json(["wallet", "settings"])
    connected = (st.get("data") or {}).get("status") == "CONNECTED"
    dm = (se.get("data") or {}).get("devMode") or {}
    return {"connected": connected,
            "devmode_enabled": bool(dm.get("enabled")),
            "devmode_expires": dm.get("expiresAt"),
            "session_expires": (se.get("data") or {}).get("sessionExpireTime"),
            "ok": connected and bool(dm.get("enabled")),
            "error": None if (connected and dm.get("enabled"))
            else f"status={st.get('data')} devMode={dm}",
            "fetched_at": int(time.time())}


# ---------------------------------------------------------------- pre-warm

def prewarm(cfg, log, force=False):
    """Refresh audit + sesi. Kembalikan dict cache pre-warm."""
    res = {"audits": {}, "session": None, "fetched_at": int(time.time())}
    for contract in cfg["audit_contracts"]:
        s = fetch_audit(contract, cfg.get("chain_id", "56"))
        res["audits"][contract] = s
        block, why = audit_is_blocking(s)
        if block:
            log.write(f"PRE-WARM audit MEMBLOKIR {contract}: {why}")
        elif not s.get("hasResult"):
            log.write(f"PRE-WARM audit {contract}: TIDAK ADA HASIL "
                      f"(hasResult=false — diungkapkan, bukan lolos)")
        else:
            log.write(f"PRE-WARM audit {contract}: riskLevel="
                      f"{s.get('riskLevel')} ({s.get('riskLevelEnum')}), "
                      f"hit={len(s.get('risk_hits') or [])}")
    sess = session_check()
    res["session"] = sess
    log.write(f"PRE-WARM sesi: connected={sess['connected']} "
              f"devMode={sess['devmode_enabled']} "
              f"expires={sess.get('session_expires')}")
    return res


def prewarm_fresh_enough(cfg, cache, now=None):
    """True bila cache audit (semua kontrak) + sesi masih dalam TTL."""
    now = now or int(time.time())
    if not cache:
        return False
    if now - cache.get("fetched_at", 0) > cfg.get("audit_ttl_s", 600):
        return False
    sess = cache.get("session") or {}
    if not sess.get("ok"):
        return False
    for contract in cfg["audit_contracts"]:
        if contract not in (cache.get("audits") or {}):
            return False
    return True


# ---------------------------------------------------------------- preview / execute

def _find_balance_deltas(obj, depth=0):
    """Cari struktur perubahan saldo di output preview (rekursif).

    Kembalikan list dict mentah yang mengandung kunci mirip balance.
    Bentuk persis output baw tidak dijamin — parser ini defensif.
    """
    found = []
    if depth > 4 or not isinstance(obj, (dict, list)):
        return found
    if isinstance(obj, dict):
        keys = {k.lower() for k in obj.keys()}
        if keys & {"balancechange", "balancechanges", "tokenbalancechange",
                   "tokenbalancechanges", "balance", "amount"}:
            found.append(obj)
        for v in obj.values():
            found.extend(_find_balance_deltas(v, depth + 1))
    else:
        for v in obj:
            found.extend(_find_balance_deltas(v, depth + 1))
    return found


def _delta_matches(expected_raw, deltas):
    """True bila salah satu struktur perubahan saldo memuat expected_raw."""
    if expected_raw is None:
        return True  # tidak ada ekspektasi -> tidak dicek
    want = str(expected_raw)
    for d in deltas:
        s = json.dumps(d)
        if want in s or str(int(want)) in s:
            return True
    return False


def _preview_code(prev):
    """Ambil kode hasil preview dari bentuk mana pun.

    Bentuk sukses lama: data.simulationCode. Bentuk sukses BARU
    (terverifikasi live 16 Nov 2026, sampel nyata): kode di
    data.simulationResult.simulationCode. Bentuk gagal (live 14 Nov
    2026): top-level error.code, mis. {"success": false, "error":
    {"code": 351805, "message": "..."}}.
    """
    data = prev.get("data") or {}
    sim = data.get("simulationResult") or {}
    code = sim.get("simulationCode", sim.get("simulation_code"))
    if code is None:
        code = data.get("simulationCode", data.get("simulation_code"))
    if code is None:
        err = prev.get("error") or {}
        code = err.get("code")
    return str(code) if code is not None else None


def _risk_hit_in(obj, depth=0):
    """True bila ada dict {isHit: true, riskType: 'RISK'} di obj."""
    if depth > 4 or not isinstance(obj, (dict, list)):
        return False
    if isinstance(obj, dict):
        if obj.get("isHit") and obj.get("riskType") == "RISK":
            return True
        return any(_risk_hit_in(v, depth + 1) for v in obj.values())
    return any(_risk_hit_in(v, depth + 1) for v in obj)


def preview_is_clean(cfg, prev):
    """Nilai output preview baw. Kembalikan (clean_bool, alasan)."""
    if not prev.get("ok"):
        return False, (f"preview gagal dieksekusi: "
                       f"code={_preview_code(prev)} "
                       f"error={str(prev.get('error'))[:200]}")
    data = prev.get("data") or prev
    # Wadah simulasi: bentuk baru (16 Nov 2026) data.simulationResult;
    # bentuk lama field simulasi langsung di data.
    sim = data.get("simulationResult") if isinstance(
        data.get("simulationResult"), dict) else data
    # Bentuk umum: simulationCode / simulationErrorDetail di sim.
    # Bila field tidak ada sama sekali -> fail closed.
    if "simulationCode" not in sim and "simulation_code" not in sim:
        return False, ("preview: struktur tidak dikenali "
                       f"(kunci: {sorted(data.keys())[:12]})")
    code = _preview_code(prev)
    err = sim.get("simulationErrorDetail",
                  sim.get("simulation_error_detail"))
    if code != "000000000":
        return False, f"preview: simulationCode={code} err={err}"
    if err is not None:
        return False, f"preview: simulationErrorDetail={err}"
    value = data.get("value", sim.get("gasTokenFromData", 0))
    if value not in (0, "0", "0x0", None):
        return False, f"preview: value bukan 0: {value}"
    for key in ("authorityChanges", "allowanceChanges"):
        ch = sim.get(key, sim.get(key.lower()))
        if ch is None:
            ch = data.get(key, data.get(key.lower()))
        if ch:
            return False, f"preview: {key} tidak kosong: {str(ch)[:200]}"
    # Risk items: bentuk lama data.riskItems[].details[] dan bentuk
    # baru data.risks.riskDetails[] (16 Nov 2026).
    for item in data.get("riskItems") or []:
        for d in item.get("details") or []:
            if d.get("isHit") and d.get("riskType") == "RISK":
                return False, (f"preview: RISK hit "
                               f"{item.get('id')}/{d.get('title')}")
    if _risk_hit_in(data.get("risks")):
        return False, "preview: RISK hit di data.risks"
    deltas = _find_balance_deltas(data)
    if cfg.get("expected_delta_raw") is not None and not deltas:
        return False, ("preview: tidak ada info perubahan saldo untuk "
                       "diverifikasi terhadap expected_delta_raw "
                       "(fail closed)")
    if not _delta_matches(cfg.get("expected_delta_raw"), deltas):
        return False, ("preview: perubahan saldo tidak memuat expected "
                       f"{cfg.get('expected_delta_raw')}")
    return True, "preview bersih"


def run_preview(cfg, log):
    """Simulasi mint gratis. TIDAK broadcast. Kembalikan dict preview."""
    t0 = time.time()
    args = ["contract-call", "preview",
            "--binanceChainId", str(cfg.get("chain_id", "56")),
            "--from", cfg["agent_wallet"],
            "--to", cfg["mint_contract"],
            "--value", "0",
            "--inputData", cfg["free_calldata"]]
    prev = baw_json(args)
    prev["elapsed_s"] = round(time.time() - t0, 2)
    log.write(f"PREVIEW selesai {prev['elapsed_s']} dtk "
              f"(requestId={(prev.get('data') or {}).get('requestId')})")
    return prev


def run_execute(cfg, log, request_id):
    """SATU broadcast execute. TIDAK PERNAH dipanggil dua kali untuk
    satu trigger. Kembalikan dict hasil execute."""
    t0 = time.time()
    ex = baw_json(["contract-call", "execute", "--requestId", request_id])
    ex["elapsed_s"] = round(time.time() - t0, 2)
    data = ex.get("data") or {}
    log.write(f"EXECUTE selesai {ex['elapsed_s']} dtk "
              f"status={data.get('status')} tx={data.get('txHash')}")
    return ex


def verify_receipt(cfg, log, tx_hash, timeout_s=60):
    """Batch receipt + saldo token + freeDone + freeMinted, ulang ~60 dtk.

    Wajib: receipt_status=1, freeDone=true, saldo token naik TEPAT
    expected_delta_raw dari saldo pra-eksekusi (bila token_contract
    dikonfigurasi).
    """
    token = cfg.get("token_contract")
    user = cfg["agent_wallet"]
    batch = [
        {"jsonrpc": "2.0", "method": "eth_getTransactionReceipt",
         "params": [tx_hash], "id": 0},
        {"jsonrpc": "2.0", "method": "eth_call",
         "params": [{"to": cfg["mint_contract"],
                     "data": cfg.get("free_done_selector", "0x4bba7bb0")
                     + _arg_addr(user)}, "latest"], "id": 2},
        {"jsonrpc": "2.0", "method": "eth_call",
         "params": [{"to": cfg["mint_contract"],
                     "data": cfg.get("free_minted_selector", "0xd10a1a2b")},
                    "latest"], "id": 3},
    ]
    if token:
        batch.append(
            {"jsonrpc": "2.0", "method": "eth_call",
             "params": [{"to": token,
                         "data": "0x70a08231" + _arg_addr(user)}, "latest"],
             "id": 1})
    deadline = time.time() + timeout_s
    last = None
    while time.time() < deadline:
        try:
            out, endpoint, _ = rpc_batch(batch)
        except Exception as e:  # noqa: BLE001
            last = {"error": str(e)[:200]}
            time.sleep(3)
            continue
        by_id = {x.get("id"): x for x in out if isinstance(x, dict)}
        receipt = by_id.get(0, {}).get("result")
        if receipt:
            bal = _u256(by_id.get(1, {}).get("result")) if token else None
            free_done = _u256(by_id.get(2, {}).get("result"))
            free_minted = _u256(by_id.get(3, {}).get("result"))
            last = {
                "receipt_status": (int(receipt["status"], 16)
                                   if receipt.get("status") else None),
                "receipt_block": _u256(receipt.get("blockNumber")),
                "gas_used": _u256(receipt.get("gasUsed")),
                "token_balance_raw": bal,
                "freeDone": (bool(free_done)
                             if free_done is not None else None),
                "freeMinted": free_minted,
                "endpoint": endpoint,
            }
            return last
        time.sleep(3)
    return last or {"error": "receipt tidak muncul dalam batas waktu"}


# ---------------------------------------------------------------- selftest

def selftest(log):
    """Uji offline tanpa jaringan: config, trigger, parsing audit/preview."""
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        log.write(f"SELFTEST {'PASS' if cond else 'FAIL'} {name} {detail}")
        ok = ok and bool(cond)

    cfg = {
        "sale_name": "selftest", "agent_wallet":
        "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E",
        "mint_contract": "0x133D81871f5C9881d4aE09b0492d6f061a54361a",
        "free_calldata": "0x8ab53447", "free_total": 210,
        "poll_interval_s": 12, "prewarm_interval_s": 300,
        "min_bnb_wei": 30000000000000, "audit_ttl_s": 600,
        "dry_run": True, "expected_delta_raw": "5000000000000000000000",
        "poll_calls": [
            {"label": "started", "to": "0x133D81871f5C9881d4aE09b0492d6f061a54361a",
             "data": "0x1f2698ab", "kind": "bool"},
            {"label": "freeMinted", "to": "0x133D81871f5C9881d4aE09b0492d6f061a54361a",
             "data": "0xd10a1a2b", "kind": "uint"},
            {"label": "freeDone", "to": "0x133D81871f5C9881d4aE09b0492d6f061a54361a",
             "data": "0x4bba7bb0{user}", "kind": "bool"},
        ],
        "trigger": {"started": True, "freeDone": False},
        "audit_contracts": ["0x133D81871f5C9881d4aE09b0492d6f061a54361a"],
    }
    try:
        cfg2 = load_config.__wrapped__ if hasattr(load_config, "__wrapped__") else None
        # validasi langsung pada dict (load_config butuh file; uji lewat
        # fungsi yang sama dengan menulis file temp di workspace)
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json",
                                         delete=False,
                                         dir="/home/hatch/workspace/fast_exec") as f:
            json.dump(cfg, f)
            tmp = f.name
        loaded = load_config(tmp)
        os.unlink(tmp)
        check("load_config valid", loaded["sale_name"] == "selftest")
        check("validate_live menolak dry_run",
              bool(validate_live(loaded)))
    except Exception as e:  # noqa: BLE001
        check("load_config valid", False, str(e)[:120])

    poll_open = {"values": {"started": True, "freeMinted": 100,
                            "freeDone": False},
                 "bnb_balance_raw": 100000000000000,
                 "bnb_balance": 0.0001}
    met, why = trigger_met(cfg, poll_open)
    check("trigger buka", met, why)
    poll_soldout = {"values": {"started": True, "freeMinted": 210,
                               "freeDone": False},
                    "bnb_balance_raw": 100000000000000,
                    "bnb_balance": 0.0001}
    met, why = trigger_met(cfg, poll_soldout)
    check("trigger habis ditolak", not met, why)
    poll_notopen = {"values": {"started": False, "freeMinted": 0,
                               "freeDone": False},
                    "bnb_balance_raw": 100000000000000,
                    "bnb_balance": 0.0001}
    met, why = trigger_met(cfg, poll_notopen)
    check("trigger belum buka ditolak", not met, why)
    check("free_remaining 110", free_remaining(cfg, poll_open) == 110)

    # parsing audit: hasResult=false tidak memblokir; RISK memblokir.
    s_noresult = {"ok": True, "hasResult": False, "risk_hits": [],
                  "riskAlert": None}
    b, _ = audit_is_blocking(s_noresult)
    check("audit no-result tidak memblokir", not b)
    s_risk = {"ok": True, "hasResult": True,
              "risk_hits": [{"id": "X", "title": "t", "riskType": "RISK"}],
              "riskAlert": None}
    b, _ = audit_is_blocking(s_risk)
    check("audit RISK memblokir", b)
    s_apifail = {"ok": False, "error": "timeout"}
    b, _ = audit_is_blocking(s_apifail)
    check("audit API gagal memblokir", b)
    s_caution = {"ok": True, "hasResult": True,
                 "risk_hits": [{"id": "X", "title": "t",
                                "riskType": "CAUTION"}],
                 "riskAlert": None}
    b, _ = audit_is_blocking(s_caution)
    check("audit CAUTION saja tidak memblokir", not b)

    # parsing preview bersih / kotor.
    good = {"ok": True, "data": {
        "simulationCode": "000000000", "simulationErrorDetail": None,
        "value": 0, "authorityChanges": [], "allowanceChanges": [],
        "balanceChanges": [{"amount": "5000000000000000000000"}]}}
    clean, why = preview_is_clean(cfg, good)
    check("preview bersih", clean, why)
    bad_code = {"ok": True, "data": {
        "simulationCode": "351803", "simulationErrorDetail": "risk",
        "value": 0, "authorityChanges": [], "allowanceChanges": []}}
    clean, why = preview_is_clean(cfg, bad_code)
    check("preview 351803 ditolak", not clean, why)
    # Bentuk gagal nyata (live 14 Nov 2026): error.code top-level.
    real_fail = {"ok": False, "success": False,
                 "error": {"code": 351805, "name": "SERVICE_ERROR",
                           "message": "Transaction simulation failed: "
                           "execution reverted: CLOSED"}}
    check("preview gagal: kode 351805 terbaca",
          _preview_code(real_fail) == "351805")
    clean, why = preview_is_clean(cfg, real_fail)
    check("preview gagal nyata ditolak", not clean, why)
    # Bentuk sukses BARU (live 16 Nov 2026, sampel nyata baw):
    # kode + perubahan di data.simulationResult, risiko di data.risks.
    new_good = {"ok": True, "data": {
        "requestId": "d9df9fdf58c24d3b9d42982813ebdf28",
        "simulationResult": {
            "gasTokenFromData": 0,
            "balanceChanges": [
                {"amount": "5000000000000000000000"}],
            "simulationErrorDetail": None,
            "simulationCode": "000000000",
            "authorityChanges": [], "allowanceChanges": []},
        "risks": {"addresses": {}, "riskDetails": [],
                  "riskBehaviors": []},
        "requireConfirmation": False,
        "gasLimit": None}}
    clean, why = preview_is_clean(cfg, new_good)
    check("preview baru bersih", clean, why)
    check("preview_code baca bentuk baru",
          _preview_code(new_good) == "000000000")
    new_bad_code = {"ok": True, "data": {
        "simulationResult": {
            "simulationCode": "351803",
            "simulationErrorDetail": "risk",
            "gasTokenFromData": 0,
            "balanceChanges": [],
            "authorityChanges": [], "allowanceChanges": []},
        "risks": {"riskDetails": []}}}
    clean, why = preview_is_clean(cfg, new_bad_code)
    check("preview baru 351803 ditolak", not clean, why)
    new_risk = {"ok": True, "data": {
        "simulationResult": {
            "simulationCode": "000000000",
            "simulationErrorDetail": None,
            "gasTokenFromData": 0,
            "balanceChanges": [
                {"amount": "5000000000000000000000"}],
            "authorityChanges": [], "allowanceChanges": []},
        "risks": {"riskDetails": [
            {"isHit": True, "riskType": "RISK",
             "title": "contoh"}]}}}
    clean, why = preview_is_clean(cfg, new_risk)
    check("preview baru RISK ditolak", not clean, why)
    unknown = {"ok": True, "data": {"foo": 1}}
    clean, why = preview_is_clean(cfg, unknown)
    check("preview struktur tak dikenal ditolak", not clean, why)

    # batch build: {user} tersubstitusi, jumlah call benar.
    batch = build_poll_batch(cfg)
    check("batch 2 + 3 calls", len(batch) == 5,
          f"len={len(batch)}")
    check("batch {user} tersubstitusi",
          _arg_addr(cfg["agent_wallet"]) in batch[4]["params"][0]["data"])

    # --wait-until: parsing + status tunggu + terminal saat menunggu.
    check("wait-until ISO +07:00",
          parse_wait_until("2026-11-16T19:00:00+07:00")
          == int(datetime(2026, 11, 16, 19, 0, 0,
                          tzinfo=WIB).timestamp()))
    check("wait-until Z",
          parse_wait_until("2026-11-16T12:00:00Z")
          == int(datetime(2026, 11, 16, 12, 0, 0,
                          tzinfo=timezone.utc).timestamp()))
    check("wait-until epoch",
          parse_wait_until("1794750000") == 1794750000)
    check("wait-until naive = WIB",
          parse_wait_until("2026-11-16 19:00:00")
          == int(datetime(2026, 11, 16, 19, 0, 0,
                          tzinfo=WIB).timestamp()))
    try:
        parse_wait_until("bukan-waktu")
        check("wait-until invalid ditolak", False)
    except ValueError:
        check("wait-until invalid ditolak", True)
    check("is_waiting masa depan",
          is_waiting(int(time.time()) + 3600))
    check("is_waiting masa lalu",
          not is_waiting(int(time.time()) - 3600))
    check("is_waiting tanpa nilai",
          not is_waiting(None))
    check("terminal_from_poll kuota habis",
          terminal_from_poll(cfg, poll_soldout)
          == "terminal: kuota gratis habis")
    check("terminal_from_poll belum habis",
          terminal_from_poll(cfg, poll_open) is None)

    log.write(f"SELFTEST {'SEMUA PASS' if ok else 'ADA FAIL'}")
    return 0 if ok else 1


# ---------------------------------------------------------------- main loop

def _write_state(path, state):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=1, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def _event(state, kind, detail):
    ev = state.setdefault("events", [])
    ev.append({"ts": _now_wib(), "kind": kind, "detail": str(detail)[:500]})
    del ev[:-200]


def attempt_execution(cfg, log, state, poll):
    """Jalur eksekusi SATU trigger. Kembalikan (terminal_bool, alasan).

    Urutan: audit (cache bila segar, else segar) -> sesi (cache bila
    segar, else segar) -> baca-ulang verifikasi -> preview -> execute
    (SEKALI, tanpa retry) -> verifikasi receipt.
    """
    t_trig = time.time()
    # 1. Audit: cache bila segar, else fetch segar sekarang.
    cache = state.get("prewarm") or {}
    if prewarm_fresh_enough(cfg, cache):
        log.write("EXEC: audit pakai cache pre-warm (segar)")
        audits = cache["audits"]
    else:
        log.write("EXEC: cache pre-warm basi — fetch audit segar")
        audits = {}
        for contract in cfg["audit_contracts"]:
            audits[contract] = fetch_audit(contract, cfg.get("chain_id", "56"))
    for contract, s in audits.items():
        block, why = audit_is_blocking(s)
        if block:
            return True, f"terminal: audit memblokir ({why})"
        if not s.get("hasResult"):
            log.write(f"EXEC: audit {contract} TIDAK ADA HASIL "
                      f"(diungkapkan, bukan lolos)")
        else:
            log.write(f"EXEC: audit {contract} riskLevel="
                      f"{s.get('riskLevel')} ({s.get('riskLevelEnum')})")
    # 2. Sesi baw.
    sess = (cache.get("session") if prewarm_fresh_enough(cfg, cache)
            else None)
    if sess is None:
        log.write("EXEC: sesi cache basi — cek sesi segar")
        sess = session_check()
    if not sess.get("ok"):
        log.write(f"EXEC: sesi tidak siap: {sess.get('error')} "
                  f"— trigger dilewati, kembali polling")
        return False, "sesi tidak siap (bukan terminal; pantau terus)"
    log.write("EXEC: sesi CONNECTED + devMode aktif")
    # 3. Baca-ulang verifikasi tepat sebelum preview (satu batch segar).
    try:
        poll2 = poll_once(cfg)
    except Exception as e:  # noqa: BLE001
        log.write(f"EXEC: baca-ulang gagal: {e} — batal, kembali polling")
        return False, "baca-ulang gagal (bukan terminal)"
    met, why = trigger_met(cfg, poll2)
    if not met:
        log.write(f"EXEC: trigger tidak lagi terpenuhi: {why} — batal")
        return False, f"trigger hilang: {why}"
    # Saldo token pra-eksekusi (untuk verifikasi delta).
    pre_bal = None
    if cfg.get("token_contract"):
        try:
            b = [{"jsonrpc": "2.0", "method": "eth_call",
                  "params": [{"to": cfg["token_contract"],
                              "data": "0x70a08231"
                              + _arg_addr(cfg["agent_wallet"])}, "latest"],
                  "id": 0}]
            out, _, _ = rpc_batch(b)
            pre_bal = _u256(out[0].get("result"))
        except Exception as e:  # noqa: BLE001
            log.write(f"EXEC: baca saldo token gagal: {e} — lanjut, "
                      f"verifikasi saldo dilewati")
    # 4. Preview.
    prev = run_preview(cfg, log)
    code = _preview_code(prev)
    if code == "351805":
        log.write("EXEC: preview 351805 (gas/saldo/revert) — bukan "
                  "terminal, kembali polling")
        return False, "preview 351805 (bukan terminal)"
    if code == "351803":
        return True, "terminal: preview diblokir risk (code 351803)"
    clean, why = preview_is_clean(cfg, prev)
    if not clean:
        return True, f"terminal: preview kotor ({why})"
    log.write(f"EXEC: preview bersih ({why}); "
              f"trigger->preview {round(time.time() - t_trig, 1)} dtk")
    req_id = (prev.get("data") or {}).get("requestId")
    if not req_id:
        return True, "terminal: preview bersih tapi tanpa requestId"
    # 5. Execute — SEKALI, tanpa retry.
    ex = run_execute(cfg, log, req_id)
    data = ex.get("data") or {}
    status = data.get("status")
    tx = data.get("txHash")
    if status == "PENDING_CONFIRMATION":
        return True, ("terminal: PENDING_CONFIRMATION — eksekusi di tangan "
                      "user di Binance App; jangan eksekusi ulang")
    if not ex.get("ok") or status != "BROADCASTED" or not tx:
        return True, (f"terminal: execute error "
                      f"(status={status}, err={ex.get('error')})")
    log.write(f"EXEC: broadcasted tx={tx}")
    # 6. Verifikasi receipt.
    ver = verify_receipt(cfg, log, tx)
    log.write(f"EXEC: verifikasi receipt: {json.dumps(ver)[:400]}")
    ok_receipt = ver.get("receipt_status") == 1
    ok_done = ver.get("freeDone") is True
    ok_delta = True
    if (cfg.get("expected_delta_raw") is not None and pre_bal is not None
            and ver.get("token_balance_raw") is not None):
        delta = ver["token_balance_raw"] - pre_bal
        ok_delta = str(delta) == str(cfg["expected_delta_raw"])
        log.write(f"EXEC: delta saldo token {delta} "
                  f"(harap {cfg['expected_delta_raw']})")
    if ok_receipt and ok_done and ok_delta:
        state["mint_result"] = {"tx": tx, "verification": ver,
                                "checked_at": _now_wib()}
        return True, f"terminal: MINT SUKSES tx={tx}"
    return True, (f"terminal: receipt_status={ver.get('receipt_status')} "
                  f"freeDone={ver.get('freeDone')} delta_ok={ok_delta} "
                  f"— laporkan apa adanya, jangan retry")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=None)
    ap.add_argument("--live", action="store_true",
                    help="mode live (butuh config dry_run=false juga)")
    ap.add_argument("--dry-run", action="store_true",
                    help="paksa dry-run walau config dry_run=false")
    ap.add_argument("--once", action="store_true",
                    help="satu poll + satu pre-warm lalu keluar")
    ap.add_argument("--duration-s", type=int, default=0,
                    help="batas durasi loop (0 = sampai terminal)")
    ap.add_argument("--stop-on-trigger", action="store_true",
                    help="berhenti (bukan eksekusi) saat trigger terdeteksi "
                    "di dry-run")
    ap.add_argument("--wait-until", default=None, metavar="WAKTU",
                    help="tunggu sampai waktu buka (ISO 8601, mis. "
                    "2026-11-16T19:00:00+07:00, atau epoch detik); "
                    "sebelum waktu itu loop hanya poll (tanpa "
                    "preview/execute), sesudahnya live penuh; nilai di "
                    "masa lalu = live langsung")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    log = Log()
    if args.selftest:
        return selftest(log)

    if not args.config:
        ap.error("--config wajib (kecuali --selftest)")
    cfg = load_config(args.config)
    wait_until_epoch = None
    wait_until_iso = None
    if args.wait_until:
        try:
            wait_until_epoch = parse_wait_until(args.wait_until)
        except ValueError as e:
            log.write(f"--wait-until tidak valid: {e}")
            return 2
        wait_until_iso = datetime.fromtimestamp(
            wait_until_epoch, WIB).strftime("%Y-%m-%d %H:%M:%S WIB")
        if wait_until_epoch <= int(time.time()):
            log.write(f"--wait-until {wait_until_iso} sudah lewat — "
                      f"live langsung")
        else:
            log.write(f"MODE TUNGGU sampai {wait_until_iso} — poll saja, "
                      f"tanpa preview/execute sebelum waktu buka")
    live = args.live and not args.dry_run
    if args.live and args.dry_run:
        log.write("flag --live + --dry-run bersamaan: dry-run menang")
        live = False
    if live:
        problems = validate_live(cfg)
        if problems:
            log.write("MODE LIVE DITOLAK:")
            for p in problems:
                log.write(f"  - {p}")
            return 2
        log.write(f"MODE LIVE di-arm untuk sale '{cfg['sale_name']}' — "
                  f"website gate: {cfg.get('website_url')}")
    else:
        log.write(f"MODE DRY-RUN untuk sale '{cfg['sale_name']}' — "
                  f"tidak ada preview/execute")

    base = os.path.dirname(os.path.abspath(args.config))
    state_path = cfg.get("state_path") or os.path.join(
        base, f"fcfs_fast_state_{cfg['sale_name']}.json")
    log_path = cfg.get("log_path") or os.path.join(
        base, f"fcfs_fast_{cfg['sale_name']}.log")
    log = Log(log_path)
    log.write(f"START sale={cfg['sale_name']} live={live} "
              f"poll={cfg['poll_interval_s']}s "
              f"prewarm={cfg['prewarm_interval_s']}s "
              f"wait_until={wait_until_iso or '-'} "
              f"config={args.config}")

    state = {"sale_name": cfg["sale_name"], "live": live,
             "started_at": _now_wib(), "events": [], "terminal": None,
             "wait_until": wait_until_iso,
             "wait_until_epoch": wait_until_epoch, "waiting": False}
    t_start = time.time()
    last_prewarm = 0
    poll_n = 0
    executed = False  # pengaman: execute hanya sekali per proses

    while True:
        # --- pre-warm (awal + berkala) ---
        now = int(time.time())
        if now - last_prewarm >= cfg["prewarm_interval_s"]:
            try:
                state["prewarm"] = prewarm(cfg, log)
                last_prewarm = now
            except Exception as e:  # noqa: BLE001
                log.write(f"PRE-WARM gagal: {e}")
                _event(state, "prewarm_failed", str(e)[:200])
        # --- poll ---
        t0 = time.time()
        try:
            poll = poll_once(cfg)
            poll_n += 1
            state["last_poll"] = poll
            state["last_poll_at"] = _now_wib()
            state["waiting"] = is_waiting(wait_until_epoch)
            if poll_n % 10 == 1 or poll_n <= 2:
                log.write(f"POLL #{poll_n} blok={poll['block']} "
                          f"values={poll['values']} "
                          f"BNB={poll['bnb_balance']} "
                          f"{poll['elapsed_s']}s via {poll['endpoint']}")
        except Exception as e:  # noqa: BLE001
            log.write(f"POLL gagal: {e} — state lama dipertahankan, "
                      f"tidak ada eksekusi dari data basi")
            _event(state, "poll_failed", str(e)[:200])
            poll = None
        _write_state(state_path, state)

        if poll is not None:
            term = None
            if state["waiting"]:
                # Mode tunggu: trigger TIDAK dievaluasi (tanpa
                # preview/execute sebelum waktu buka); kondisi terminal
                # tetap dicek — sale yang sudah habis tidak perlu
                # ditunggu.
                if poll_n % 10 == 1 or poll_n <= 2:
                    log.write(f"MENUNGGU sampai {wait_until_iso} "
                              f"(sisa {wait_until_epoch - int(time.time())} "
                              f"dtk) — trigger tidak dievaluasi")
                term = terminal_from_poll(cfg, poll)
            else:
                met, why = trigger_met(cfg, poll)
                if met:
                    log.write(f"TRIGGER TERDETEKSI: {why} "
                              f"(poll #{poll_n}, blok {poll['block']})")
                    _event(state, "trigger", why)
                    if not live:
                        if args.stop_on_trigger:
                            state["terminal"] = "dry-run trigger terdeteksi"
                            _write_state(state_path, state)
                            log.write("DRY-RUN stop-on-trigger — selesai")
                            log.close()
                            return 0
                        log.write("DRY-RUN: trigger dicatat, tanpa eksekusi")
                    elif executed:
                        log.write("SUDAH PERNAH execute di proses ini — "
                                  "tidak execute ulang")
                    else:
                        executed = True
                        terminal, reason = attempt_execution(cfg, log, state,
                                                             poll)
                        log.write(f"JALUR EKSEKUSI: {reason}")
                        _event(state, "execution", reason)
                        if terminal:
                            state["terminal"] = reason
                            _write_state(state_path, state)
                            log.write(f"TERMINAL: {reason}")
                            log.close()
                            return 0
                else:
                    # kondisi terminal tanpa trigger: kuota habis / gagal /
                    # sudah klaim — cek dari poll segar.
                    term = terminal_from_poll(cfg, poll)
            if term:
                state["terminal"] = term
                _write_state(state_path, state)
                log.write(term)
                log.close()
                return 0
        if args.once:
            log.write("--once selesai")
            log.close()
            return 0
        if args.duration_s and time.time() - t_start >= args.duration_s:
            log.write(f"durasi {args.duration_s}s habis — berhenti "
                      f"(bukan terminal)")
            log.close()
            return 0
        # tidur sisa interval (poll yang lambat tidak menumpuk).
        spent = time.time() - t0
        time.sleep(max(0, cfg["poll_interval_s"] - spent))


if __name__ == "__main__":
    sys.exit(main())
