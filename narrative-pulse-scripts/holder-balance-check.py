#!/usr/bin/env python3
"""Cek saldo on-chain read-only untuk holder-candidate-watch (Mode B fallback).

Membaca balanceOf (desimal 18) untuk semua posisi terlacak Dompet A dan
Dompet B via JSON-RPC publik BSC. Tanpa wallet connect, tanpa signing.
Dipakai saat halaman GMGN login-gated dan detail aktivitas tidak terbaca.
"""
import json
import urllib.request

ENDPOINTS = [
    "https://bsc-dataseed.binance.org/",
    "https://bsc-dataseed1.binance.org/",
    "https://bsc-dataseed2.binance.org/",
    "https://bsc-dataseed3.binance.org/",
    "https://bsc-dataseed4.binance.org/",
    "https://bsc.publicnode.com",
    "https://rpc.ankr.com/bsc",
]
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
      "Content-Type": "application/json"}

A = "0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"
B = "0xd392967fc834d718f4f9627fc5552881d1048727"

# (label, wallet, CA, expected)
CHECKS = [
    ("ok", A, "0xc853d8253f0d8346ca80f3f6af53e49a763e7777", 840175.64),
    ("wangcai", A, "0x9d01d9ca91703b881dc0e585c6b746085b8f7777", 851502.39),
    ("shijiezhiyan", A, "0xf99980ab40e315a163ca81e105a5123fad747777", 467285.97),
    ("zhaozi", A, "0x2d49950ce0e83fa4dc7f3e67751669075fed7777", 213952.71),
    ("lulu", A, "0x54639e15a77ccbd9a8d57af5fd9920bc07bd7777", 163065.68),
    ("goerem", A, "0xf951b6b83872dae16dd33c93071aa570373f7777", 195200.00),
    ("jixiang", A, "0xea7886d590ba1d7d6d4e7761148ba26405c67777", 200039.83),
    ("pituo", A, "0xc9836647de5ed3ff3dbd064a7a7a6527b9f87777", 242680.21),
    ("huadiweilao", A, "0x1ed2e3e5a991c5e04d4b0e88153a9aaef7167777", 143777.03),
    ("1113", A, "0x064f86075d930544ac655350f8295d1ef04d7777", 153480.93),
    ("lina", A, "0x0c3c88345196b05d8c75a9a2dc0b2f2be07d7777", 228874.33),
    ("mangxiaoliu", A, "0x6b0d76a0e5da1e1bf2e39f2921b1b9ad8fb87777", 221568.62),
    ("KIM", A, "0x4cf98f0616311a9e6988f0857e13cf27fd287777", 0),
    ("MMGA", A, "0xdbdf764636f80b42c59f3b9be510043310f67777", 0),
    ("Kim", A, "0xd499353371ffed80e07bb5978bc5c96993f37777", 0),
    ("yueqiu-tu", A, "0x3a03269a7cef8a321e964dad336bd78ae64e7777", 0),
    ("bi-an-bisheng", A, "0xb1c5ab95fc2f42e254b39f3d731a496d41337777", 0),
    ("yangwang", A, "0x5a8d94c69998daffcfdc365f1d333dc4ab087777", 0),
    ("dagou", A, "0x482ec62043b50ef5ac67b6c520439edbaf277777", 0),
    ("bi-an-yizhi-zai", A, "0x98757f71d5c00c992be6d04f2cdfb33ce83c7777", 0),
    ("xiaohuangshu", A, "0x3bb3e494c9dcbbd016e33c96cfa7ef3f704b7777", 0),
    ("Flap", A, "0x55c3992fd542f1a898898cdb010f71e2683f7777", 0),
    ("MSX", B, "0x23214ccbffb6ef479da64d1842b10b5525997777", 0),  # keluar penuh sejak run 04:30 WIB 2026-11-12 (sebelumnya 62986.65)
    ("AiPro", B, "0xfe295c812b35f14aeb2df2224b21f80befed7777", 210844.93),
    ("bi-an-gongzhu", B, "0x0c21248002c5bd2e96155509369508e361cd7777", 0),  # keluar penuh sejak run 04:30 WIB 2026-11-12 (sebelumnya 472406.33)
    # True 0x9d46 / 0x6406: keluar penuh sejak run 18:30 WIB 2026-11-06 — harapan 0 (sebelumnya 499253.89/473979.09, saldo pra-keluar)
    ("True-0x9d46", B, "0x9d46a3c5eb87f8bd1a3a5afd9ffdf070f0077777", 0),
    ("True-0x6406", B, "0x640652ce87b57f333745edf3294840c3e0dd7777", 0),
    ("bibi", B, "0x9212cf1f9f4a9c69bb010146ba5b0725169d4444", 0),
]


def rpc(endpoint, payload):
    req = urllib.request.Request(endpoint, data=json.dumps(payload).encode(),
                                 headers=UA, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def balance(endpoint, wallet, ca):
    data = "0x70a08231" + wallet[2:].rjust(64, "0")
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
               "params": [{"to": ca, "data": data}, "latest"]}
    res = rpc(endpoint, payload)
    if "error" in res:
        raise RuntimeError(res["error"])
    return int(res["result"], 16) / 1e18


def block_number(endpoint):
    res = rpc(endpoint, {"jsonrpc": "2.0", "id": 1,
                         "method": "eth_blockNumber", "params": []})
    return int(res["result"], 16)


def main():
    block = None
    used = None
    for ep in ENDPOINTS:
        try:
            block = block_number(ep)
            used = ep
            break
        except Exception:
            continue
    if block is None:
        print("GAGAL: semua endpoint tidak merespons eth_blockNumber")
        return
    print(f"blok {block} via {used}")
    changed = []
    failed = []
    for label, wallet, ca, expected in CHECKS:
        val = None
        last_err = None
        for ep in ENDPOINTS:
            try:
                val = balance(ep, wallet, ca)
                break
            except Exception as e:
                last_err = e
        if val is None:
            failed.append((label, str(last_err)))
            print(f"{label}: GAGAL DIBACA ({last_err}) — BUKAN bukti saldo 0")
            continue
        status = "OK" if abs(val - expected) < 0.01 else "BERUBAH"
        if status == "BERUBAH":
            changed.append((label, expected, val))
        print(f"{label}: {val:,.2f} (diharapkan {expected:,.2f}) {status}")
    print(f"ringkasan: {len(CHECKS)-len(failed)} terbaca, {len(failed)} gagal, {len(changed)} berubah")
    if changed:
        for label, exp, val in changed:
            print(f"BERUBAH: {label} {exp:,.2f} -> {val:,.2f}")
    if failed:
        for label, err in failed:
            print(f"GAGAL: {label}: {err}")


if __name__ == "__main__":
    main()
