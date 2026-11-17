#!/usr/bin/env python3
"""Retry read-only untuk 5 saldo yang gagal pada run 18:30 WIB 2026-11-16.
Dipakai sekali, hanya untuk label yang gagal; bukan pengganti skrip paralel.
"""
import importlib.util
import json
import urllib.request

_spec = importlib.util.spec_from_file_location(
    "hbc", "/home/hatch/workspace/narrative-pulse/holder-balance-check.py")
_hbc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_hbc)
CHECKS = _hbc.CHECKS

ENDPOINTS = [
    "https://bsc-dataseed1.binance.org/",
    "https://bsc-dataseed2.binance.org/",
    "https://bsc-dataseed3.binance.org/",
    "https://bsc-dataseed4.binance.org/",
]
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
      "Content-Type": "application/json"}

WANT = {"wangcai", "zhaozi", "jixiang", "mangxiaoliu", "KIM"}


def rpc(endpoint, payload, timeout=25):
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


def main():
    block, used = block_number()
    print(f"blok {block} via {used}")
    for label, wallet, ca, expected in CHECKS:
        if label not in WANT:
            continue
        data = "0x70a08231" + wallet[2:].rjust(64, "0")
        payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                   "params": [{"to": ca, "data": data}, "latest"]}
        ok = False
        for attempt in range(3):
            for ep in ENDPOINTS:
                try:
                    res = rpc(ep, payload)
                    if "error" in res:
                        raise RuntimeError(res["error"])
                    val = int(res["result"], 16) / 1e18
                    status = "OK" if abs(val - expected) < 0.01 else "BERUBAH"
                    print(f"{label}: {val:,.2f} (diharapkan {expected:,.2f}) {status}")
                    ok = True
                    break
                except Exception:
                    continue
            if ok:
                break
        if not ok:
            print(f"{label}: GAGAL DIBACA (3x percobaan) — BUKAN bukti saldo 0")


if __name__ == "__main__":
    main()
