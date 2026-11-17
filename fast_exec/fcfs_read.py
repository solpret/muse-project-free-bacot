#!/usr/bin/env python3
"""fcfs_read.py — generic batched pre-execution reads for ANY future FCFS race.

Aturan FCFS (lihat AGENTS.md): dalam perebutan kuota/FCFS, semua bacaan
on-chain pra-eksekusi HARUS jalan sebagai SATU JSON-RPC batch, bukan
eth_call berurutan. Skrip ini adalah alat generiknya — tidak terikat
proyek apa pun, supaya job FCFS berikutnya tinggal pakai tanpa menulis
skrip baru.

Pakai:
  python3 fcfs_read.py calls.json
  echo '[{"to":"0x...","data":"0x..."}]' | python3 fcfs_read.py -
  python3 fcfs_read.py calls.json --pretty

Format calls.json: list objek {"to": "0x...", "data": "0x..."} atau
{"calls": [...]}. Output JSON ke stdout:
  {"results": ["0x...", ...], "count": N, "elapsed_s": 12.34}
Hasil mentah hex, urutan sama dengan input — caller yang decode
(int(hex,16) untuk uint, dst). Batch di-race ke beberapa endpoint
sekaligus (fast_rpc.batch_race) supaya satu endpoint lambat tidak
menahan batch; bila race gagal total, fallback ke call_many.

Read-only total: tidak ada sign/tx/preview. Stdlib + fast_rpc saja.
"""
import json
import sys
import time

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch_race, call_many  # noqa: E402


def load_calls(argv):
    src = argv[1] if len(argv) > 1 else "-"
    raw = sys.stdin.read() if src == "-" else open(src).read()
    data = json.loads(raw)
    if isinstance(data, dict):
        data = data.get("calls", [])
    calls = []
    for item in data:
        to = item["to"]
        hexdata = item["data"]
        if not (isinstance(to, str) and to.startswith("0x")):
            raise ValueError(f"bad 'to': {to!r}")
        if not (isinstance(hexdata, str) and hexdata.startswith("0x")):
            raise ValueError(f"bad 'data': {hexdata!r}")
        calls.append((to, hexdata))
    if not calls:
        raise ValueError("no calls given")
    return calls


def main():
    pretty = "--pretty" in sys.argv[1:]
    t0 = time.time()
    calls = load_calls([a for a in sys.argv if a != "--pretty"])
    try:
        # Race 10 detik: cukup untuk endpoint sehat, gagal cepat supaya
        # fallback tidak menunggu lama.
        results = batch_race(calls, timeout=10)
    except Exception:
        results = call_many(calls)
    out = {
        "results": list(results),
        "count": len(results),
        "elapsed_s": round(time.time() - t0, 2),
    }
    print(json.dumps(out, indent=2 if pretty else None))
    print(f"# {len(results)} calls in {out['elapsed_s']}s", file=sys.stderr)


if __name__ == "__main__":
    main()
