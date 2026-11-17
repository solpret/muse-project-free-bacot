#!/usr/bin/env python3
"""Cek saldo on-chain read-only PARALEL untuk holder-candidate-watch (Mode B fallback).

Versi paralel dari holder-balance-check.py: 8 thread, rotasi endpoint per
cek + retry. Dibuat 2026-11-12 karena holder-balance-check.py sekuensial
gagal total (semua endpoint tidak merespons eth_blockNumber) pada run
00:30 WIB 2026-11-12, sementara curl langsung menunjukkan
bsc-dataseed1-4 merespons. Disimpan di workspace (bukan /tmp) agar tidak
hilang saat VM restart. Tanpa wallet connect, tanpa signing.
"""
import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "hbc", __file__.rsplit("/", 1)[0] + "/holder-balance-check.py")
_hbc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_hbc)
CHECKS, A, B = _hbc.CHECKS, _hbc.A, _hbc.B

ENDPOINTS = [
    "https://bsc-dataseed1.binance.org/",
    "https://bsc-dataseed2.binance.org/",
    "https://bsc-dataseed3.binance.org/",
    "https://bsc-dataseed4.binance.org/",
]
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
      "Content-Type": "application/json"}


def rpc(endpoint, payload, timeout=20):
    req = urllib.request.Request(endpoint, data=json.dumps(payload).encode(),
                                 headers=UA, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def block_number():
    for ep in ENDPOINTS:
        try:
            res = rpc(ep, {"jsonrpc": "2.0", "id": 1,
                           "method": "eth_blockNumber", "params": []})
            return int(res["result"], 16), ep
        except Exception:
            continue
    return None, None


def check_one(args):
    idx, (label, wallet, ca, expected) = args
    data = "0x70a08231" + wallet[2:].rjust(64, "0")
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
               "params": [{"to": ca, "data": data}, "latest"]}
    last_err = None
    for attempt in range(2):
        for ep in ENDPOINTS:
            try:
                res = rpc(ep, payload)
                if "error" in res:
                    raise RuntimeError(res["error"])
                val = int(res["result"], 16) / 1e18
                status = "OK" if abs(val - expected) < 0.01 else "BERUBAH"
                return (idx, label, val, expected, status, ep)
            except Exception as e:
                last_err = e
                continue
    return (idx, label, None, expected, "GAGAL", str(last_err))


def main():
    block, used = block_number()
    if block is None:
        print("GAGAL: semua endpoint tidak merespons eth_blockNumber")
        return
    print(f"blok {block} via {used}")
    results = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(check_one, (i, c)): i for i, c in enumerate(CHECKS)}
        for fut in as_completed(futs):
            r = fut.result()
            results[r[0]] = r
    changed, failed = [], []
    for i in sorted(results):
        idx, label, val, expected, status, ep = results[i]
        if val is None:
            failed.append(label)
            print(f"{label}: GAGAL DIBACA ({ep}) — BUKAN bukti saldo 0")
        else:
            if status == "BERUBAH":
                changed.append((label, expected, val))
            print(f"{label}: {val:,.2f} (diharapkan {expected:,.2f}) {status}")
    print(f"ringkasan: {len(CHECKS)-len(failed)} terbaca, "
          f"{len(failed)} gagal, {len(changed)} berubah")
    for label, exp, val in changed:
        print(f"BERUBAH: {label} {exp:,.2f} -> {val:,.2f}")
    for label in failed:
        print(f"GAGAL: {label}")


if __name__ == "__main__":
    main()
