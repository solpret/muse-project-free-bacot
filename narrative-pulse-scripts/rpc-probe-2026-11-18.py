#!/usr/bin/env python3
"""Probe RPC publik BSC gratis untuk eth_getLogs (scan tracked-wallet).
Perintah user 18 Nov 2026 ~05:45 WIB ('Cari RPC lain sekarang') — bloXroute
403 persisten >4 jam (run 208+209 gagal total). Uji ulang 14 Nov + kandidat baru.
Metode: curl (bukan urllib — header Connection: close urllib dipotong proxy).
Tiap endpoint: eth_blockNumber (15 dtk) lalu eth_getLogs jendela 200 blok
dengan filter driver (Transfer topic0, from=zero, to=[AFeng]) (60 dtk).
Hasil: ~/workspace/narrative-pulse/rpc-probe-2026-11-18.json
"""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed

TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
AFENG = "0x000000000000000000000000bf004bff64725914ee36d03b87d6965b0ced4903"

ENDPOINTS = [
    ("bloXroute (saat ini, re-probe)", "https://bsc.rpc.blxrbdn.com"),
    ("bloXroute alt host", "https://bsc.blxrbdn.com"),
    ("dataseed binance.org", "https://bsc-dataseed.binance.org"),
    ("dataseed bnbchain.org", "https://bsc-dataseed.bnbchain.org"),
    ("dataseed1 bnbchain.org", "https://bsc-dataseed1.bnbchain.org"),
    ("dataseed2 bnbchain.org", "https://bsc-dataseed2.bnbchain.org"),
    ("dataseed1 defibit.io", "https://bsc-dataseed1.defibit.io"),
    ("dataseed1 ninicoin.io", "https://bsc-dataseed1.ninicoin.io"),
    ("publicnode bsc", "https://bsc.publicnode.com"),
    ("publicnode bsc-rpc", "https://bsc-rpc.publicnode.com"),
    ("blastapi public", "https://bsc-mainnet.public.blastapi.io"),
    ("blockpi public", "https://bsc.blockpi.network/v1/rpc/public"),
    ("drpc.org", "https://bsc.drpc.org"),
    ("1rpc.io/bnb", "https://1rpc.io/bnb"),
    ("meowrpc", "https://bsc.meowrpc.com"),
    ("llamarpc binance", "https://binance.llamarpc.com"),
    ("omniatech", "https://endpoints.omniatech.io/v1/bsc/mainnet/public"),
    ("onfinality public", "https://bnb.api.onfinality.io/public"),
    ("therpc.io", "https://rpc.therpc.io/bsc"),
    ("ankr public (tanpa key)", "https://rpc.ankr.com/bsc"),
    ("lava.build", "https://bsc.lava.build"),
    ("alchemy demo", "https://bnb-mainnet.g.alchemy.com/v2/demo"),
    ("48.club (max ~20 blok, bukan kandidat driver)", "https://rpc-bsc.48.club"),
]

def curl_json(url, payload, timeout):
    cmd = ["curl", "-s", "-m", str(timeout), "-X", "POST",
           "-H", "Content-Type: application/json", "-d", payload, url]
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        return time.time() - t0, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return time.time() - t0, "", "TIMEOUT curl"

def probe(name, url):
    out = {"name": name, "url": url, "blockNumber": None, "getLogs": None}
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})
    dt, body, err = curl_json(url, payload, 15)
    out["blockNumber"] = {"secs": round(dt, 1), "body": body[:300], "err": err}
    try:
        tip = int(json.loads(body)["result"], 16)
    except Exception:
        out["getLogs"] = {"skipped": "no tip"}
        return out
    frm, to = tip - 200, tip
    f = {"fromBlock": hex(frm), "toBlock": hex(to),
         "topics": [[TRANSFER], [ZERO], [AFENG]]}
    # 48.club: jendela kecil saja
    if "48.club" in url:
        f["fromBlock"] = hex(tip - 10)
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs", "params": [f]})
    dt, body, err = curl_json(url, payload, 60)
    try:
        d = json.loads(body)
        if "result" in d:
            out["getLogs"] = {"secs": round(dt, 1), "status": "OK",
                              "logs": len(d["result"]), "window": [frm, to]}
        else:
            out["getLogs"] = {"secs": round(dt, 1), "status": "ERROR",
                              "error": json.dumps(d.get("error"))[:300]}
    except Exception:
        out["getLogs"] = {"secs": round(dt, 1), "status": "NON-JSON",
                          "body": body[:300], "err": err}
    return out

def probe_blockscout():
    """Blockscout REST getLogs — jalur non-JSON-RPC, perlu driver baru bila jalan."""
    out = {"name": "Blockscout REST (bnb-smart-chain)", "url": "https://blockscout.com/bnb-smart-chain/api"}
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})
    dt, body, err = curl_json("https://bsc.rpc.blxrbdn.com", payload, 15)
    try:
        tip = int(json.loads(body)["result"], 16)
    except Exception:
        out["getLogs"] = {"skipped": "no tip from bloXroute"}
        return out
    frm, to = tip - 200, tip
    q = ("https://blockscout.com/bnb-smart-chain/api?module=logs&action=getLogs"
         f"&fromBlock={frm}&toBlock={to}&topic0={TRANSFER}&topic1={ZERO}&topic2={AFENG}")
    t0 = time.time()
    try:
        r = subprocess.run(["curl", "-s", "-m", "60", q], capture_output=True, text=True, timeout=65)
        dt = time.time() - t0
        try:
            d = json.loads(r.stdout)
            if d.get("status") == "1":
                out["getLogs"] = {"secs": round(dt, 1), "status": "OK",
                                  "logs": len(d.get("result", [])), "window": [frm, to]}
            else:
                out["getLogs"] = {"secs": round(dt, 1), "status": "ERROR",
                                  "body": r.stdout[:300]}
        except Exception:
            out["getLogs"] = {"secs": round(dt, 1), "status": "NON-JSON", "body": r.stdout[:300]}
    except subprocess.TimeoutExpired:
        out["getLogs"] = {"secs": 60, "status": "TIMEOUT"}
    return out

def main():
    results = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(probe, n, u): n for n, u in ENDPOINTS}
        for f in as_completed(futs):
            try:
                results.append(f.result())
            except Exception as e:
                results.append({"name": futs[f], "error": str(e)})
    results.append(probe_blockscout())
    order = {u: i for i, (_, u) in enumerate(ENDPOINTS)}
    results.sort(key=lambda r: order.get(r.get("url", ""), 99))
    path = "/home/hatch/workspace/narrative-pulse/rpc-probe-2026-11-18.json"
    with open(path, "w") as fh:
        json.dump({"ran_at_wib": "2026-11-18 ~05:47", "results": results}, fh, indent=2)
    for r in results:
        gl = r.get("getLogs") or {}
        bn = r.get("blockNumber") or {}
        bn_body = bn.get("body", "") if isinstance(bn, dict) else str(bn)
        print(f"{r['name']}: blockNumber={bn_body[:80]} | getLogs={gl.get('status')} {gl.get('logs','')} {gl.get('error','')}{gl.get('body','')[:120]}")
    print("WROTE", path)

if __name__ == "__main__":
    main()
