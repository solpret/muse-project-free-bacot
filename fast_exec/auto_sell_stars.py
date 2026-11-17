#!/usr/bin/env python3
"""auto_sell_stars.py — auto-sell 1000 token Binance Life AI ke BNB via PCS V2.

Dibangun 16 Nov 2026 atas perintah user ("Langsung buatkan auto sell saat
pool terbuka"). Menjual HANYA delta 1000 token hasil beli 2 share
(tx 0xba9bae830ebda34d1c0fed01df82fa1bb8df2aa0c531bd6de1e667a8e5464628),
bukan saldo lain. Pola: fcfs_fast.py (SATU JSON-RPC batch per poll,
pre-warm audit + sesi baw).

Trigger: pair PCS V2 (token, WBNB) != 0x0 DAN quote getAmountsOut(1000) > 0.
opened() dicatat di state; bila pair sudah berlikuiditas tapi opened() masih
false, quote tetap dievaluasi (keputusan ini didokumentasikan di state).

Gate jual (aturan post-mint auto-swap 2026-11-03):
  - pair nyata + likuiditas (quote > 0 membuktikannya; reserves dibaca sekali
    saat pair ditemukan dan dicatat di state)
  - quote >= 2x estimasi gas ((approve_gas + swap_gas) x gas price live)
  - audit Binance segar: hasResult=true + tanpa RISK (API gagal / tanpa hasil
    = fail-closed, terminal "audit unverified")
  - preview bersih tiap langkah; approve exact-delta bila allowance ke router
    kurang (allowance change ke router pada langkah approve DIHARAPKAN);
    swap min-out 95% quote; pada langkah swap TIDAK BOLEH ada allowance /
    authority change.
  - Bila tidak bisa jual (no pair, quote debu, audit RISK, preview kotor
    351803/351805) -> TAHAN, terminal + laporkan sekali, TANPA retry.
    Pengecualian: quote debu (quote > 0 tapi < 2x gas) BUKAN terminal —
    likuiditas bisa membesar; loop terus memantau (TAHAN = jangan jual di
    harga debu). Bila saldo token 0 -> terminal "no balance". Bila saldo
    > 1000 -> jual HANYA 1000. Bila 0 < saldo < 1000 -> jual saldo aktual
    (<= 1000, tetap hanya delta milik sendiri).

Mode: default dry-run. Live butuh config dry_run=false DAN flag --live.
Loop MATI bila VM restart — watchdog cron auto-sell-stars-watchdog (2 menit)
menyalakan ulang dari pointer armed-autosell.json; restart TIDAK PERNAH
melewati terminal (state.terminal terisi -> watchdog diam + proses baru
keluar langsung).
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
ZERO_ADDR = "0x0000000000000000000000000000000000000000"
NATIVE_ADDR = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

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


def _arg_addr(a):
    return a[2:].lower().rjust(64, "0")


def _u256(hexstr):
    if hexstr is None or hexstr == "0x":
        return None
    try:
        return int(hexstr, 16)
    except (ValueError, TypeError):
        return None


def _addr(word):
    """Ambil alamat (20 byte terakhir) dari satu word hex 32 byte."""
    if not word:
        return None
    h = word[2:] if word.startswith("0x") else word
    if len(h) < 40:
        return None
    return "0x" + h[-40:].lower()


def _pad32(x):
    return format(int(x), "064x")


def _num(v):
    """Angka dari JSON (int/float/str) -> float, atau None bila bukan angka."""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return None
    return None


def _approx(a, b, rel=1e-6):
    if a is None or b is None:
        return False
    return abs(a - b) <= max(1.0, abs(b) * rel)


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
    """Satu batch ke endpoint pertama yang menjawab."""
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


def rpc_single(method, params):
    """Satu call (bukan batch). Kembalikan result mentah atau None."""
    batch = [{"jsonrpc": "2.0", "method": method, "params": params, "id": 0}]
    out, _, _ = rpc_batch(batch)
    entry = out[0] if out else {}
    if "error" in entry:
        return None
    return entry.get("result")


# ---------------------------------------------------------------- calldata

def build_amounts_out_calldata(cfg):
    amt = int(cfg["sell_amount_raw"])
    return ("0xd06ca61f" + _pad32(amt) + _pad32(0x40) + _pad32(2)
            + _arg_addr(cfg["token"]) + _arg_addr(cfg["wbnb"]))


def build_getpair_calldata(cfg):
    return ("0xe6a43905" + _arg_addr(cfg["token"])
            + _arg_addr(cfg["wbnb"]))


def build_approve_calldata(cfg, amount):
    return "0x095ea7b3" + _arg_addr(cfg["router"]) + _pad32(amount)


def build_swap_calldata(cfg, amount_in, min_out, deadline):
    return ("0x18cbafe5" + _pad32(amount_in) + _pad32(min_out)
            + _pad32(0xa0) + _arg_addr(cfg["agent_wallet"])
            + _pad32(deadline) + _pad32(2) + _arg_addr(cfg["token"])
            + _arg_addr(cfg["wbnb"]))


def _decode_amounts_out(hexstr):
    """Decode hasil getAmountsOut (uint256[]): kembalikan amounts[1] (WBNB
    keluar) atau None bila revert/kosong/pendek."""
    if not hexstr or hexstr == "0x":
        return None
    try:
        raw = bytes.fromhex(hexstr[2:] if hexstr.startswith("0x")
                            else hexstr)
    except ValueError:
        return None
    if len(raw) < 128:
        return None
    length = int.from_bytes(raw[32:64], "big")
    if length != 2:
        return None
    return int.from_bytes(raw[96:128], "big")


# ---------------------------------------------------------------- config

REQUIRED_STR = ["token", "agent_wallet", "router", "factory", "wbnb"]
REQUIRED_INT = ["poll_interval_s", "prewarm_interval_s", "approve_gas",
                "swap_gas", "min_out_bps"]


def load_config(path):
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    for k in REQUIRED_STR:
        v = cfg.get(k)
        if not isinstance(v, str) or not v.startswith("0x") or len(v) != 42:
            raise ValueError(f"config: '{k}' bukan alamat 0x 42 karakter")
    for k in REQUIRED_INT:
        if not isinstance(cfg.get(k), int) or cfg[k] <= 0:
            raise ValueError(f"config: '{k}' wajib integer > 0")
    raw = cfg.get("sell_amount_raw")
    if not isinstance(raw, str) or not raw.isdigit() or int(raw) <= 0:
        raise ValueError("config: 'sell_amount_raw' wajib string digit > 0")
    if cfg.get("min_out_bps", 9500) > 10000:
        raise ValueError("config: 'min_out_bps' tidak boleh > 10000")
    cfg.setdefault("chain_id", "56")
    cfg.setdefault("audit_ttl_s", 600)
    cfg.setdefault("audit_contracts", [cfg["token"]])
    cfg.setdefault("dry_run", True)
    return cfg


def validate_live(cfg):
    """Tolak mode live bila guard arming tidak lengkap."""
    problems = []
    if cfg.get("dry_run", True):
        problems.append("config dry_run=true — set false untuk live.")
    return problems


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


def audit_is_sell_blocking(summary):
    """True bila audit ini MENGHENTIKAN penjualan (fail-closed, lebih ketat
    dari fcfs: hasResult=false JUGA memblokir — jual butuh hasil audit
    positif, bukan 'tidak ada hasil').

    Yang menghentikan: kegagalan API, hasResult=false, RISK hit, riskAlert.
    CAUTION saja tidak memblokir.
    """
    if not summary.get("ok"):
        return True, f"audit API gagal: {summary.get('error')}"
    if not summary.get("hasResult"):
        return True, "audit tanpa hasil (hasResult=false)"
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

def prewarm(cfg, log):
    """Refresh audit + sesi. Kembalikan dict cache pre-warm."""
    res = {"audits": {}, "session": None, "fetched_at": int(time.time())}
    for contract in cfg["audit_contracts"]:
        s = fetch_audit(contract, cfg.get("chain_id", "56"))
        res["audits"][contract] = s
        block, why = audit_is_sell_blocking(s)
        if block:
            log.write(f"PRE-WARM audit MEMBLOKIR {contract}: {why}")
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


# ---------------------------------------------------------------- poll

# (id, label, kind, to-key, data-template) — data {user}/{router} disubstitusi.
POLL_CALLS = [
    (1, "opened", "bool", "token", "0x5f88eade"),
    (2, "pool", "address", "token", "0x16f0115b"),
    (3, "pair", "address", "factory", "GETPAIR"),
    (4, "balance", "uint", "token", "0x70a08231{user}"),
    (5, "allowance", "uint", "token", "0xdd62ed3e{user}{router}"),
    (6, "quote", "amounts_out", "router", "AMOUNTS_OUT"),
]


def build_poll_batch(cfg):
    """eth_blockNumber + eth_getBalance + eth_gasPrice + semua poll_calls,
    SATU batch."""
    user = cfg["agent_wallet"]
    batch = [
        {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [],
         "id": 0},
        {"jsonrpc": "2.0", "method": "eth_getBalance",
         "params": [user, "latest"], "id": 100},
        {"jsonrpc": "2.0", "method": "eth_gasPrice", "params": [],
         "id": 101},
    ]
    for cid, label, kind, to_key, data in POLL_CALLS:
        if data == "GETPAIR":
            data = build_getpair_calldata(cfg)
        elif data == "AMOUNTS_OUT":
            data = build_amounts_out_calldata(cfg)
        else:
            data = data.replace("{user}", _arg_addr(user)).replace(
                "{router}", _arg_addr(cfg["router"]))
        batch.append({"jsonrpc": "2.0", "method": "eth_call",
                      "params": [{"to": cfg[to_key], "data": data},
                                 "latest"], "id": cid})
    return batch


def decode_poll(cfg, out):
    by_id = {x.get("id"): x for x in out if isinstance(x, dict)}
    block = _u256(by_id.get(0, {}).get("result"))
    bnb_raw = _u256(by_id.get(100, {}).get("result"))
    gas_price = _u256(by_id.get(101, {}).get("result"))
    if block is None or bnb_raw is None:
        raise IOError(f"hasil blok/saldo kosong (block={block})")
    vals = {}
    for cid, label, kind, _to_key, _data in POLL_CALLS:
        entry = by_id.get(cid, {})
        raw_hex = entry.get("result")
        if kind == "amounts_out":
            # Quote boleh revert/kosong sebelum pair ada -> None, bukan gagal.
            vals[label] = _decode_amounts_out(raw_hex)
            continue
        if "error" in entry or raw_hex is None:
            raise IOError(f"{label}: RPC error {entry.get('error')}")
        if kind == "bool":
            vals[label] = bool(_u256(raw_hex))
        elif kind == "address":
            vals[label] = _addr(raw_hex)
        else:
            vals[label] = _u256(raw_hex)
    return {"block": block, "bnb_balance_raw": bnb_raw,
            "bnb_balance": bnb_raw / 10**18,
            "gas_price_raw": gas_price,
            "gas_price_gwei": (gas_price / 10**9 if gas_price else None),
            "values": vals}


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


def trigger_met(poll):
    """True bila pair ada DAN quote > 0. opened() dicatat, bukan syarat —
    bila pair sudah berlikuiditas tapi opened() masih false, quote tetap
    dievaluasi (keputusan didokumentasikan di state)."""
    vals = poll["values"]
    pair = vals.get("pair")
    quote = vals.get("quote")
    if pair is None or pair == ZERO_ADDR:
        return False, "trigger: pair belum ada"
    if quote is None or quote <= 0:
        return False, f"trigger: quote kosong/nol (quote={quote})"
    return True, (f"trigger OK (pair={pair} quote={quote} wei "
                   f"opened={vals.get('opened')})")


def terminal_from_poll(poll):
    """Kondisi terminal dari poll segar: saldo token 0 -> tidak ada yang
    dijual."""
    if poll["values"].get("balance") == 0:
        return "terminal: no balance (saldo token 0)"
    return None


# ---------------------------------------------------------------- single reads

def fresh_quote(cfg):
    """Quote getAmountsOut segar (single call). None bila revert/kosong."""
    res = rpc_single("eth_call", [{"to": cfg["router"],
                                   "data": build_amounts_out_calldata(cfg)},
                                  "latest"])
    return _decode_amounts_out(res)


def read_allowance(cfg):
    res = rpc_single("eth_call", [{"to": cfg["token"],
                                   "data": "0xdd62ed3e"
                                   + _arg_addr(cfg["agent_wallet"])
                                   + _arg_addr(cfg["router"])}, "latest"])
    return _u256(res)


def read_token_balance(cfg):
    res = rpc_single("eth_call", [{"to": cfg["token"],
                                   "data": "0x70a08231"
                                   + _arg_addr(cfg["agent_wallet"])},
                                  "latest"])
    return _u256(res)


def read_bnb(cfg):
    res = rpc_single("eth_getBalance", [cfg["agent_wallet"], "latest"])
    return _u256(res)


def read_reserves(cfg, pair):
    """Baca getReserves + token0 sekali saat pair ditemukan. Kembalikan dict
    atau None bila gagal (tidak fatal — quote tetap penentu likuiditas)."""
    res = rpc_single("eth_call", [{"to": pair, "data": "0x0902f1ac"},
                                  "latest"])
    t0 = rpc_single("eth_call", [{"to": pair, "data": "0x0dfe1681"},
                                 "latest"])
    if res is None:
        return None
    try:
        raw = bytes.fromhex(res[2:] if res.startswith("0x") else res)
    except ValueError:
        return None
    if len(raw) < 64:
        return None
    return {"pair": pair,
            "reserve0": int.from_bytes(raw[0:32], "big"),
            "reserve1": int.from_bytes(raw[32:64], "big"),
            "token0": _addr(t0) if t0 else None}


# ---------------------------------------------------------------- preview / execute

def _sim(prev):
    """Ambil (simulationResult, data) dari bentuk preview baw yang nyata:
    data.simulationResult.{simulationCode, balanceChanges, ...} (terverifikasi
    dari preview beli 16 Nov 2026). Fallback ke bentuk datar."""
    data = prev.get("data") or {}
    sim = data.get("simulationResult")
    if isinstance(sim, dict):
        return sim, data
    return data, data


def _preview_code(prev):
    """Kode hasil preview dari bentuk mana pun (sukses: simulationCode;
    gagal nyata: top-level error.code, mis. 351805/351803)."""
    sim, _data = _sim(prev)
    code = sim.get("simulationCode", sim.get("simulation_code"))
    if code is None:
        err = prev.get("error") or {}
        code = err.get("code")
    return str(code) if code is not None else None


def _base_preview_checks(prev):
    """Cek umum semua preview. Kembalikan (ok, alasan) atau (True, None)
    bila lolos cek umum (cek spesifik allowance/saldo dilakukan pemanggil)."""
    if not prev.get("ok"):
        return False, (f"preview gagal dieksekusi: "
                       f"code={_preview_code(prev)} "
                       f"error={str(prev.get('error'))[:200]}")
    sim, data = _sim(prev)
    if "simulationCode" not in sim and "simulation_code" not in sim:
        return False, ("preview: struktur tidak dikenali "
                       f"(kunci: {sorted(sim.keys())[:12]})")
    code = _preview_code(prev)
    err = sim.get("simulationErrorDetail",
                  sim.get("simulation_error_detail"))
    if code != "000000000":
        return False, f"preview: simulationCode={code} err={err}"
    if err is not None:
        return False, f"preview: simulationErrorDetail={err}"
    gtf = _num(data.get("gasTokenFromData",
                        sim.get("gasTokenFromData", 0)))
    if gtf is None or gtf != 0:
        return False, f"preview: value bukan 0 (gasTokenFromData={gtf})"
    if sim.get("authorityChanges"):
        return False, ("preview: authorityChanges tidak kosong: "
                       f"{str(sim.get('authorityChanges'))[:200]}")
    risks = data.get("risks") or {}
    for d in risks.get("riskDetails") or []:
        if d.get("isHit") and d.get("riskType") == "RISK":
            return False, "preview: RISK hit di riskDetails"
    for d in risks.get("riskBehaviors") or []:
        if isinstance(d, dict) and d.get("riskType") == "RISK":
            return False, "preview: RISK hit di riskBehaviors"
    return True, None


def preview_approve_is_clean(cfg, prev, sell_amount):
    """Preview approve exact-delta. SATU allowance change DIHARAPKAN:
    token == token, spender == router, postAmount ≈ sell_amount. Entry
    lain / jumlah entry != 1 -> kotor."""
    ok, why = _base_preview_checks(prev)
    if not ok:
        return False, why
    sim, _data = _sim(prev)
    changes = sim.get("allowanceChanges") or []
    if len(changes) != 1:
        return False, (f"preview approve: allowanceChanges harus 1, "
                       f"ada {len(changes)}")
    e = changes[0]
    tok = str(e.get("tokenAddress", "")).lower()
    spender = str(e.get("spender", "")).lower()
    post = _num(e.get("postAmount"))
    if tok != cfg["token"].lower():
        return False, f"preview approve: tokenAddress {tok} bukan token"
    if spender != cfg["router"].lower():
        return False, f"preview approve: spender {spender} bukan router"
    if not _approx(post, float(sell_amount)):
        return False, (f"preview approve: postAmount {post} != "
                       f"{sell_amount}")
    return True, "preview approve bersih (allowance sesuai ekspektasi)"


def preview_swap_is_clean(cfg, prev, sell_amount):
    """Preview swap ketat: TIDAK BOLEH ada allowance/authority change;
    saldo token harus ≈ -sell_amount dan BNB harus masuk."""
    ok, why = _base_preview_checks(prev)
    if not ok:
        return False, why
    sim, _data = _sim(prev)
    if sim.get("allowanceChanges"):
        return False, ("preview swap: allowanceChanges tidak kosong: "
                       f"{str(sim.get('allowanceChanges'))[:200]}")
    bcs = sim.get("balanceChanges") or []
    if not bcs:
        return False, "preview swap: tidak ada balanceChanges (fail closed)"
    tok_ok = False
    bnb_ok = False
    for b in bcs:
        ca = str(b.get("contractAddress", "")).lower()
        ch = _num(b.get("change"))
        if (ca == cfg["token"].lower() and ch is not None and ch < 0
                and _approx(abs(ch), float(sell_amount))):
            tok_ok = True
        if ca == NATIVE_ADDR and ch is not None and ch > 0:
            bnb_ok = True
    if not tok_ok:
        return False, (f"preview swap: perubahan saldo token tidak "
                       f"≈ -{sell_amount}")
    if not bnb_ok:
        return False, "preview swap: tidak ada BNB masuk"
    return True, "preview swap bersih"


def run_preview(cfg, log, to, value, input_data):
    """Simulasi contract call. TIDAK broadcast. Kembalikan dict preview."""
    t0 = time.time()
    args = ["contract-call", "preview",
            "--binanceChainId", str(cfg.get("chain_id", "56")),
            "--from", cfg["agent_wallet"],
            "--to", to,
            "--value", str(value),
            "--inputData", input_data]
    prev = baw_json(args)
    prev["elapsed_s"] = round(time.time() - t0, 2)
    log.write(f"PREVIEW selesai {prev['elapsed_s']} dtk "
              f"(requestId={(prev.get('data') or {}).get('requestId')})")
    return prev


def run_execute(cfg, log, request_id):
    """SATU broadcast execute. TIDAK PERNAH dipanggil dua kali untuk satu
    langkah yang sama. Kembalikan dict hasil execute."""
    t0 = time.time()
    ex = baw_json(["contract-call", "execute", "--requestId", request_id])
    ex["elapsed_s"] = round(time.time() - t0, 2)
    data = ex.get("data") or {}
    log.write(f"EXECUTE selesai {ex['elapsed_s']} dtk "
              f"status={data.get('status')} tx={data.get('txHash')}")
    return ex


def verify_tx(cfg, log, tx_hash, timeout_s=90):
    """Tunggu receipt sampai muncul. Kembalikan dict verifikasi."""
    batch = [{"jsonrpc": "2.0", "method": "eth_getTransactionReceipt",
              "params": [tx_hash], "id": 0}]
    deadline = time.time() + timeout_s
    last = {"error": "receipt tidak muncul dalam batas waktu"}
    while time.time() < deadline:
        try:
            out, endpoint, _ = rpc_batch(batch)
        except Exception as e:  # noqa: BLE001
            last = {"error": str(e)[:200]}
            time.sleep(3)
            continue
        receipt = (out[0] if out else {}).get("result")
        if receipt:
            last = {
                "receipt_status": (int(receipt["status"], 16)
                                   if receipt.get("status") else None),
                "receipt_block": _u256(receipt.get("blockNumber")),
                "gas_used": _u256(receipt.get("gasUsed")),
                "effective_gas_price": _u256(
                    receipt.get("effectiveGasPrice")),
                "endpoint": endpoint,
            }
            return last
        time.sleep(3)
    return last


# ---------------------------------------------------------------- sell flow

def attempt_sell(cfg, log, state, poll):
    """Jalur jual SATU trigger. Kembalikan (terminal_bool, alasan).

    Urutan: audit segar -> sesi -> baca-ulang verifikasi -> quote segar +
    gate gas -> approve (bila perlu: preview -> execute -> verifikasi) ->
    re-quote -> preview swap -> execute swap (SEKALI, tanpa retry) ->
    verifikasi receipt + saldo.
    """
    t_trig = time.time()
    # 1. Audit segar (wajib hasResult=true + tanpa RISK; gagal = terminal).
    for contract in cfg["audit_contracts"]:
        s = fetch_audit(contract, cfg.get("chain_id", "56"))
        block, why = audit_is_sell_blocking(s)
        if block:
            return True, f"terminal: audit memblokir ({why})"
        log.write(f"SELL: audit {contract} riskLevel={s.get('riskLevel')} "
                  f"({s.get('riskLevelEnum')})")
    # 2. Sesi baw.
    sess = session_check()
    if not sess.get("ok"):
        log.write(f"SELL: sesi tidak siap: {sess.get('error')} — kembali "
                  f"polling (bukan terminal)")
        return False, "sesi tidak siap (bukan terminal; pantau terus)"
    log.write("SELL: sesi CONNECTED + devMode aktif")
    # 3. Baca-ulang verifikasi tepat sebelum eksekusi (satu batch segar).
    try:
        poll2 = poll_once(cfg)
    except Exception as e:  # noqa: BLE001
        log.write(f"SELL: baca-ulang gagal: {e} — batal, kembali polling")
        return False, "baca-ulang gagal (bukan terminal)"
    met, why = trigger_met(poll2)
    if not met:
        log.write(f"SELL: trigger tidak lagi terpenuhi: {why} — batal")
        return False, f"trigger hilang: {why}"
    balance = poll2["values"]["balance"]
    sell_amount = min(balance, int(cfg["sell_amount_raw"]))
    if sell_amount <= 0:
        return True, "terminal: no balance (saldo token 0)"
    log.write(f"SELL: saldo token {balance}, jual {sell_amount}")
    # 4. Quote segar + gate gas (quote >= 2x estimasi gas).
    quote = fresh_quote(cfg)
    if quote is None or quote <= 0:
        log.write("SELL: quote hilang/nol — batal, kembali polling")
        return False, "quote hilang/nol (bukan terminal)"
    gas_price = poll2.get("gas_price_raw") or 0
    est_gas = (cfg["approve_gas"] + cfg["swap_gas"]) * gas_price
    if quote < 2 * est_gas:
        state["last_dust"] = {"quote_wei": quote,
                              "est_gas_wei": est_gas,
                              "gas_price_wei": gas_price,
                              "checked_at": _now_wib()}
        log.write(f"SELL: quote debu {quote} wei < 2x gas {2 * est_gas} "
                  f"wei — TAHAN, kembali polling")
        return False, "quote debu (< 2x gas) — tahan"
    if poll2["bnb_balance_raw"] < est_gas:
        log.write(f"SELL: BNB {poll2['bnb_balance_raw']} < estimasi gas "
                  f"{est_gas} — kembali polling (bukan terminal)")
        return False, "BNB kurang untuk gas (bukan terminal)"
    log.write(f"SELL: quote {quote} wei, estimasi gas {est_gas} wei "
              f"(gas {gas_price} wei), rasio {quote / est_gas:.1f}x")
    # 5. Approve exact-delta bila allowance ke router kurang.
    allowance = poll2["values"]["allowance"]
    if allowance < sell_amount:
        ap_cd = build_approve_calldata(cfg, sell_amount)
        prev = run_preview(cfg, log, cfg["token"], "0", ap_cd)
        code = _preview_code(prev)
        if code in ("351805", "351803"):
            return True, (f"terminal: preview dirty "
                          f"(approve code {code})")
        clean, why2 = preview_approve_is_clean(cfg, prev, sell_amount)
        if not clean:
            return True, f"terminal: preview dirty (approve: {why2})"
        log.write(f"SELL: preview approve bersih ({why2})")
        req_id = (prev.get("data") or {}).get("requestId")
        if not req_id:
            return True, ("terminal: preview approve bersih tapi tanpa "
                          "requestId")
        ex = run_execute(cfg, log, req_id)
        data = ex.get("data") or {}
        if not ex.get("ok") or data.get("status") != "BROADCASTED" \
                or not data.get("txHash"):
            return True, (f"terminal: execute approve error "
                          f"(status={data.get('status')}, "
                          f"err={ex.get('error')})")
        ver = verify_tx(cfg, log, data["txHash"])
        if ver.get("receipt_status") != 1:
            return True, (f"terminal: receipt approve status="
                          f"{ver.get('receipt_status')} — jangan retry")
        al2 = read_allowance(cfg)
        if al2 is None or al2 < sell_amount:
            return True, (f"terminal: allowance pasca-approve {al2} < "
                          f"{sell_amount} — jangan retry")
        log.write(f"SELL: approve OK tx={data['txHash']} "
                  f"allowance={al2}")
    else:
        log.write(f"SELL: allowance {allowance} sudah >= {sell_amount}, "
                  f"lewati approve")
    # 6. Re-quote + preview swap (min-out 95% quote, deadline +10 menit).
    quote2 = fresh_quote(cfg)
    if quote2 is None or quote2 <= 0:
        log.write("SELL: quote hilang sebelum swap (approve sudah "
                  "dilakukan bila perlu) — kembali polling")
        return False, "quote hilang sebelum swap (bukan terminal)"
    min_out = quote2 * cfg["min_out_bps"] // 10000
    deadline = int(time.time()) + 600
    sw_cd = build_swap_calldata(cfg, sell_amount, min_out, deadline)
    bnb_before = read_bnb(cfg)
    prev = run_preview(cfg, log, cfg["router"], "0", sw_cd)
    code = _preview_code(prev)
    if code in ("351805", "351803"):
        return True, f"terminal: preview dirty (swap code {code})"
    clean, why2 = preview_swap_is_clean(cfg, prev, sell_amount)
    if not clean:
        return True, f"terminal: preview dirty (swap: {why2})"
    log.write(f"SELL: preview swap bersih ({why2}); quote {quote2} wei, "
              f"minOut {min_out} wei; trigger->preview "
              f"{round(time.time() - t_trig, 1)} dtk")
    req_id = (prev.get("data") or {}).get("requestId")
    if not req_id:
        return True, "terminal: preview swap bersih tapi tanpa requestId"
    # 7. Execute swap — SEKALI, tanpa retry.
    ex = run_execute(cfg, log, req_id)
    data = ex.get("data") or {}
    tx = data.get("txHash")
    if not ex.get("ok") or data.get("status") != "BROADCASTED" or not tx:
        return True, (f"terminal: execute swap error "
                      f"(status={data.get('status')}, "
                      f"err={ex.get('error')})")
    log.write(f"SELL: swap broadcasted tx={tx}")
    ver = verify_tx(cfg, log, tx)
    log.write(f"SELL: verifikasi receipt: {json.dumps(ver)[:400]}")
    bal_after = read_token_balance(cfg)
    bnb_after = read_bnb(cfg)
    ok_receipt = ver.get("receipt_status") == 1
    ok_bal = bal_after is not None and bal_after == balance - sell_amount
    gas_cost = None
    bnb_received = None
    if (ver.get("gas_used") is not None
            and ver.get("effective_gas_price") is not None):
        gas_cost = ver["gas_used"] * ver["effective_gas_price"]
    if bnb_before is not None and bnb_after is not None \
            and gas_cost is not None:
        bnb_received = (bnb_after - bnb_before) + gas_cost
    state["sell_result"] = {
        "tx": tx, "verification": ver,
        "token_balance_before": balance,
        "token_balance_after": bal_after,
        "sell_amount": sell_amount,
        "bnb_before_raw": bnb_before, "bnb_after_raw": bnb_after,
        "bnb_received_wei": bnb_received, "gas_cost_wei": gas_cost,
        "quote_wei": quote2, "min_out_wei": min_out,
        "checked_at": _now_wib(),
    }
    if ok_receipt and ok_bal:
        return True, (f"terminal: SOLD tx={tx} bnb_diterima="
                      f"{bnb_received} wei")
    return True, (f"terminal: receipt_status={ver.get('receipt_status')} "
                  f"saldo_token_sesudah={bal_after} "
                  f"(harap {balance - sell_amount}) — laporkan apa adanya, "
                  f"jangan retry")


# ---------------------------------------------------------------- selftest

def selftest(log):
    """Uji offline tanpa jaringan: config, trigger, decode quote, audit
    ketat, parsing preview (approve + swap), pembangun calldata."""
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        log.write(f"SELFTEST {'PASS' if cond else 'FAIL'} {name} {detail}")
        ok = ok and bool(cond)

    cfg = {
        "token": "0x41776Fe083239771798234B30DA0f6f1FD193ebf",
        "agent_wallet": "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E",
        "router": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
        "factory": "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73",
        "wbnb": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
        "sell_amount_raw": "1000000000000000000000",
        "poll_interval_s": 15, "prewarm_interval_s": 300,
        "approve_gas": 60000, "swap_gas": 250000, "min_out_bps": 9500,
        "audit_contracts": ["0x41776Fe083239771798234B30DA0f6f1FD193ebf"],
        "audit_ttl_s": 600, "dry_run": True, "chain_id": "56",
    }
    import tempfile
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                         dir="/home/hatch/workspace/fast_exec") as f:
            json.dump(cfg, f)
            tmp = f.name
        loaded = load_config(tmp)
        os.unlink(tmp)
        check("load_config valid", loaded["token"] == cfg["token"])
        check("validate_live menolak dry_run",
              bool(validate_live(loaded)))
    except Exception as e:  # noqa: BLE001
        check("load_config valid", False, str(e)[:120])

    # trigger: pair 0x0 / quote None -> tidak; pair ada + quote > 0 -> ya.
    p_nopair = {"values": {"pair": ZERO_ADDR, "quote": None,
                           "opened": False, "balance": 10**21}}
    met, _ = trigger_met(p_nopair)
    check("trigger tanpa pair ditolak", not met)
    p_noquote = {"values": {"pair": "0x1111111111111111111111111111111111111111",
                            "quote": None, "opened": False,
                            "balance": 10**21}}
    met, _ = trigger_met(p_noquote)
    check("trigger quote None ditolak", not met)
    p_open = {"values": {"pair": "0x1111111111111111111111111111111111111111",
                         "quote": 123456, "opened": False,
                         "balance": 10**21}}
    met, why = trigger_met(p_open)
    check("trigger pair+quote lolos walau opened=false", met, why)
    check("terminal_from_poll saldo 0",
          terminal_from_poll({"values": {"balance": 0}})
          == "terminal: no balance (saldo token 0)")
    check("terminal_from_poll saldo 1000",
          terminal_from_poll({"values": {"balance": 10**21}}) is None)

    # decode getAmountsOut: offset+len+amountIn+amountOut.
    amt = 10**21
    raw = ("0x" + _pad32(0x20) + _pad32(2) + _pad32(amt)
           + _pad32(999999))
    check("decode amounts_out", _decode_amounts_out(raw) == 999999)
    check("decode amounts_out kosong", _decode_amounts_out("0x") is None)
    check("decode amounts_out pendek",
          _decode_amounts_out("0x" + _pad32(0x20)) is None)

    # audit ketat: no-result memblokir; RISK memblokir; CAUTION lolos.
    s_noresult = {"ok": True, "hasResult": False, "risk_hits": [],
                  "riskAlert": None}
    b, _ = audit_is_sell_blocking(s_noresult)
    check("audit no-result memblokir (jual)", b)
    s_risk = {"ok": True, "hasResult": True,
              "risk_hits": [{"id": "X", "title": "t", "riskType": "RISK"}],
              "riskAlert": None}
    b, _ = audit_is_sell_blocking(s_risk)
    check("audit RISK memblokir", b)
    s_ok = {"ok": True, "hasResult": True, "riskLevel": 2,
            "risk_hits": [{"id": "X", "title": "Newly Created Token",
                           "riskType": "CAUTION"}], "riskAlert": None}
    b, _ = audit_is_sell_blocking(s_ok)
    check("audit LOW + CAUTION lolos", not b)

    # preview approve: bentuk nyata (simulationResult bersarang).
    good_ap = {"ok": True, "data": {
        "requestId": "r1", "gasTokenFromData": 0,
        "simulationResult": {
            "simulationCode": "000000000", "simulationErrorDetail": None,
            "authorityChanges": [],
            "allowanceChanges": [{
                "tokenAddress": cfg["token"], "owner": cfg["agent_wallet"],
                "spender": cfg["router"], "preAmount": 0,
                "postAmount": 1e21}]}}}
    clean, why = preview_approve_is_clean(cfg, good_ap, 10**21)
    check("preview approve bersih", clean, why)
    bad_spender = json.loads(json.dumps(good_ap))
    bad_spender["data"]["simulationResult"]["allowanceChanges"][0][
        "spender"] = "0xd637dffd418505004a3d5541c7dff64cc995e55c"
    clean, _ = preview_approve_is_clean(cfg, bad_spender, 10**21)
    check("preview approve spender salah ditolak", not clean)
    two_entries = json.loads(json.dumps(good_ap))
    two_entries["data"]["simulationResult"]["allowanceChanges"].append(
        two_entries["data"]["simulationResult"]["allowanceChanges"][0])
    clean, _ = preview_approve_is_clean(cfg, two_entries, 10**21)
    check("preview approve 2 entry ditolak", not clean)

    # preview swap: bentuk nyata; token -1e21 + BNB masuk; allowance -> kotor.
    good_sw = {"ok": True, "data": {
        "requestId": "r2", "gasTokenFromData": 0,
        "simulationResult": {
            "simulationCode": "000000000", "simulationErrorDetail": None,
            "authorityChanges": [], "allowanceChanges": [],
            "balanceChanges": [
                {"contractAddress": cfg["token"], "change": -1e21,
                 "owner": cfg["agent_wallet"], "tokenType": "Erc20"},
                {"contractAddress": NATIVE_ADDR, "change": 123456,
                 "owner": cfg["agent_wallet"], "tokenType": "Native"}]}}}
    clean, why = preview_swap_is_clean(cfg, good_sw, 10**21)
    check("preview swap bersih", clean, why)
    sw_allow = json.loads(json.dumps(good_sw))
    sw_allow["data"]["simulationResult"]["allowanceChanges"] = [{
        "tokenAddress": cfg["token"], "owner": cfg["agent_wallet"],
        "spender": cfg["router"], "preAmount": 0, "postAmount": 10**21}]
    clean, _ = preview_swap_is_clean(cfg, sw_allow, 10**21)
    check("preview swap ada allowance ditolak", not clean)
    sw_nobnb = json.loads(json.dumps(good_sw))
    sw_nobnb["data"]["simulationResult"]["balanceChanges"] = [
        sw_nobnb["data"]["simulationResult"]["balanceChanges"][0]]
    clean, _ = preview_swap_is_clean(cfg, sw_nobnb, 10**21)
    check("preview swap tanpa BNB masuk ditolak", not clean)
    sw_fail = {"ok": False, "success": False,
               "error": {"code": 351805, "message": "reverted"}}
    check("preview gagal: kode 351805 terbaca",
          _preview_code(sw_fail) == "351805")
    clean, _ = preview_swap_is_clean(cfg, sw_fail, 10**21)
    check("preview swap gagal nyata ditolak", not clean)

    # calldata builders.
    ap = build_approve_calldata(cfg, 10**21)
    check("approve calldata 138 char", len(ap) == 2 + 8 + 64 + 64,
          f"len={len(ap)}")
    check("approve selector 0x095ea7b3", ap.startswith("0x095ea7b3"))
    sw = build_swap_calldata(cfg, 10**21, 950, 1794833600)
    check("swap calldata 522 char", len(sw) == 2 + 8 + 64 * 8,
          f"len={len(sw)}")
    check("swap selector 0x18cbafe5", sw.startswith("0x18cbafe5"))
    ao = build_amounts_out_calldata(cfg)
    check("amountsOut calldata 330 char", len(ao) == 2 + 8 + 64 * 5,
          f"len={len(ao)}")
    gp = build_getpair_calldata(cfg)
    check("getPair calldata 138 char", len(gp) == 2 + 8 + 64 * 2,
          f"len={len(gp)}")
    batch = build_poll_batch(cfg)
    check("batch 3 + 6 calls", len(batch) == 9, f"len={len(batch)}")

    # gate gas: quote >= 2x (approve+swap) x gas price.
    est = (cfg["approve_gas"] + cfg["swap_gas"]) * 50_000_000
    check("gate gas 2x (contoh 0,05 gwei)",
          2 * est == 31000000000000, f"2x={2 * est}")
    check("quote debu < 2x gas ditolak gate",
          not (10**12 >= 2 * est))

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
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    log = Log()
    if args.selftest:
        return selftest(log)

    if not args.config:
        ap.error("--config wajib (kecuali --selftest)")
    cfg = load_config(args.config)
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
        log.write(f"MODE LIVE di-arm untuk auto-sell token "
                  f"{cfg['token']} (jual {cfg['sell_amount_raw']} raw)")
    else:
        log.write("MODE DRY-RUN — tidak ada preview/execute")

    base = os.path.dirname(os.path.abspath(args.config))
    state_path = cfg.get("state_path") or os.path.join(
        base, "auto_sell_stars_state.json")
    log_path = cfg.get("log_path") or os.path.join(
        base, "auto_sell_stars.log")
    log = Log(log_path)

    # Bila state lama sudah terminal -> jangan loop (watchdog tidak boleh
    # menghidupkan ulang penjualan yang sudah selesai/gagal-terminal).
    prior = None
    if os.path.exists(state_path):
        try:
            with open(state_path, encoding="utf-8") as f:
                prior = json.load(f)
        except Exception:  # noqa: BLE001
            prior = None
    if prior and prior.get("terminal"):
        log.write(f"STATE LAMA SUDAH TERMINAL: {prior['terminal']} — "
                  f"keluar, tidak loop")
        log.close()
        return 0

    log.write(f"START auto-sell live={live} "
              f"poll={cfg['poll_interval_s']}s "
              f"prewarm={cfg['prewarm_interval_s']}s "
              f"config={args.config}")

    state = {"token": cfg["token"], "live": live,
             "started_at": _now_wib(), "events": [], "terminal": None,
             "sell_amount_raw": cfg["sell_amount_raw"],
             "pair_discovered": None, "last_dust": None}
    if prior and isinstance(prior.get("events"), list):
        state["events"] = prior["events"][-50:]
    t_start = time.time()
    last_prewarm = 0
    poll_n = 0
    executed = False  # pengaman: execute swap hanya sekali per proses

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
            # reserves: baca sekali saat pair pertama kali ditemukan.
            pair = poll["values"].get("pair")
            if pair and pair != ZERO_ADDR \
                    and not state.get("pair_discovered"):
                res = read_reserves(cfg, pair)
                state["pair_discovered"] = res or {
                    "pair": pair, "reserves_error": "baca gagal",
                    "checked_at": _now_wib()}
                log.write(f"PAIR DITEMUKAN {pair} reserves="
                          f"{state['pair_discovered']}")
            if poll_n % 20 == 1 or poll_n <= 2:
                log.write(f"POLL #{poll_n} blok={poll['block']} "
                          f"values={poll['values']} "
                          f"BNB={poll['bnb_balance']} "
                          f"gas={poll['gas_price_gwei']} gwei "
                          f"{poll['elapsed_s']}s via {poll['endpoint']}")
        except Exception as e:  # noqa: BLE001
            log.write(f"POLL gagal: {e} — state lama dipertahankan, "
                      f"tidak ada eksekusi dari data basi")
            _event(state, "poll_failed", str(e)[:200])
            poll = None
        _write_state(state_path, state)

        if poll is not None:
            term = terminal_from_poll(poll)
            if term:
                state["terminal"] = term
                _write_state(state_path, state)
                log.write(term)
                log.close()
                return 0
            met, why = trigger_met(poll)
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
                    log.write("SUDAH PERNAH execute swap di proses ini — "
                              "tidak execute ulang")
                else:
                    executed = True
                    terminal, reason = attempt_sell(cfg, log, state, poll)
                    log.write(f"JALUR JUAL: {reason}")
                    _event(state, "execution", reason)
                    if terminal:
                        state["terminal"] = reason
                        _write_state(state_path, state)
                        log.write(f"TERMINAL: {reason}")
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
