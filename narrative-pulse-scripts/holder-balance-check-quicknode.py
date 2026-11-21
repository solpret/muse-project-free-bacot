#!/usr/bin/env python3
"""Cek saldo on-chain read-only via QuickNode (fallback holder-candidate-watch).

Dipakai saat SEMUA endpoint RPC publik BSC tidak merespons eth_blockNumber
(seperti run 14:30 WIB 2026-11-18, dan run 18:30 WIB 2026-11-18 percobaan
1-2). Satu batch JSON-RPC (28x balanceOf + eth_blockNumber) ke endpoint
QuickNode BSC user (custom.quicknode) via CONNECT tunnel + surrogate mentah
di path (jangan percent-encode — lihat quicknode.py). Tanpa wallet connect,
tanpa signing. Membandingkan dengan CHECKS dari holder-balance-check.py.
"""
import json
import sys

sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
import quicknode  # noqa: E402
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "hbc", "/home/hatch/workspace/narrative-pulse/holder-balance-check.py")
_hbc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_hbc)
CHECKS = _hbc.CHECKS

BLOCK = None


def batch_rpc(calls, timeout=120):
    entry = quicknode.dynamic_credential_entry(quicknode.CREDENTIAL)
    surrogate = str(entry["surrogate"]).strip()
    if not surrogate.startswith("hsurr:"):
        raise RuntimeError("authd returned a non-surrogate value")
    path = f"/{surrogate}/"  # mentah, jangan quote
    body = json.dumps(calls).encode()
    conn = quicknode.ProxyHTTPSConnection(quicknode.HOST, 443, timeout=timeout)
    try:
        conn.request("POST", path, body=body,
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        raw = resp.read()
        status = resp.status
    finally:
        conn.close()
    return status, json.loads(raw.decode("utf-8"))


def main():
    # QuickNode paket gratis: batas 15 request/detik — batch 29 item kena
    # -32007. Pecah jadi batch ≤14 item + jeda 1,2 dtk antar batch.
    import time
    calls = []
    for i, (label, wallet, ca, expected) in enumerate(CHECKS):
        data = "0x70a08231" + wallet[2:].rjust(64, "0")
        calls.append({"jsonrpc": "2.0", "id": i, "method": "eth_call",
                      "params": [{"to": ca, "data": data}, "latest"]})
    by_id = {}
    for start in range(0, len(calls), 14):
        chunk = calls[start:start + 14]
        status, res = batch_rpc(chunk)
        if status != 200 or not isinstance(res, list):
            print(f"GAGAL batch {start}: http {status}, {str(res)[:200]}")
            return 1
        for r in res:
            if isinstance(r, dict) and "id" in r:
                by_id[r["id"]] = r
        time.sleep(1.2)
    status, res = batch_rpc([{"jsonrpc": "2.0", "id": 99,
                              "method": "eth_blockNumber", "params": []}])
    if isinstance(res, list):
        res = res[0] if res else {}
    if status != 200 or not isinstance(res, dict) or "result" not in res:
        print(f"GAGAL eth_blockNumber: http {status}, {str(res)[:200]}")
        return 1
    block = int(res["result"], 16)
    print(f"blok: {block} (via QuickNode)")
    changed, failed = [], []
    for i, (label, wallet, ca, expected) in enumerate(CHECKS):
        r = by_id.get(i, {})
        if "result" not in r:
            failed.append(label)
            print(f"{label}: GAGAL {str(r.get('error'))[:120]}")
            continue
        val = int(r["result"], 16) / 1e18
        mark = "" if abs(val - expected) < 0.01 else "  <-- BERUBAH"
        if mark:
            changed.append((label, expected, val))
        print(f"{label}: {val:,.2f} (harapan {expected:,.2f}){mark}")
    print(f"ringkasan: {len(CHECKS)-len(failed)} terbaca, {len(failed)} gagal, "
          f"{len(changed)} berubah, blok {block}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
