#!/usr/bin/env python3
"""Hot-leg 2026-11-16 20:34 WIB — leg 4 batch re-read (read-only).
Re-reads AGCLUB, BinanceAI-mint, ORBIT, RigForge, CosmicSentinel, BUBB,
Poffzi (saleStart 23:00:11 WIB — still pre-launch) via per-contract
curl JSON-RPC batches to bsc-dataseed (fast_rpc batch_race stalled >280s
at 19:04; curl recovery took 9.2s). Vezlune dropped: sold out + reported
once at 19:04. Fallback endpoint defibit on per-contract failure."""
import json, subprocess, time
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
RPCS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.defibit.io/"]

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def call0(sig):
    return sel(sig)

def callAddr(sig):
    return sel(sig) + USER_PAD

PLAN = [
    ("AGCLUB", "0x67270bb351515abf3089ca5420456897363f5e75", [
        ("totalMinted", call0("totalMinted()")),
        ("freeMinted", call0("freeMinted()")),
        ("FREE_CAP", call0("FREE_CAP()")),
        ("mintOpen", call0("mintOpen()")),
        ("balanceOf_user", callAddr("balanceOf(address)")),
    ]),
    ("BinanceAI-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
        ("launched", call0("launched()")),
        ("failed", call0("failed()")),
        ("isRefundPhase", call0("isRefundPhase()")),
        ("tokenClaimed_user", callAddr("tokenClaimed(address)")),
    ]),
    ("ORBIT", "0x7d5F7f323db3050AF92E9aa1584E883B3b24d680", [
        ("freeClaimed", call0("freeClaimed()")),
        ("FREE_MAX", call0("FREE_MAX()")),
        ("claimOpen", call0("claimOpen()")),
        ("hasFreeClaimed_user", callAddr("hasFreeClaimed(address)")),
        ("totalSupply", call0("totalSupply()")),
    ]),
    ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", [
        ("freeSharesLeft", call0("freeSharesLeft()")),
        ("openedAt", call0("openedAt()")),
        ("freeClaimed", call0("freeClaimed()")),
        ("freeBooked_user", callAddr("freeBooked(address)")),
    ]),
    ("CosmicSentinel", "0x88731d1eb41c36f3d705fdb58b658244c06afc36", [
        ("totalSupply", call0("totalSupply()")),
        ("totalMinted", call0("totalMinted()")),
        ("freeMinted", call0("freeMinted()")),
        ("mintOpen", call0("mintOpen()")),
        ("balanceOf_user", callAddr("balanceOf(address)")),
    ]),
    ("BUBB", "0x0d72970046c056db90888351b739246f468bff0b", [
        ("totalSupply", call0("totalSupply()")),
        ("freeMinted", call0("freeMinted()")),
        ("mintOpen", call0("mintOpen()")),
        ("balanceOf_user", callAddr("balanceOf(address)")),
    ]),
    ("Poffzi", "0x3D7A6e3d007990B36ab092404C9027a3CD989C14", [
        ("totalSupply", call0("totalSupply()")),
        ("totalMinted", call0("totalMinted()")),
        ("freeMinted", call0("freeMinted()")),
        ("FREE_SUPPLY", call0("FREE_SUPPLY()")),
        ("mintOpen", call0("mintOpen()")),
        ("saleOpen", call0("saleOpen()")),
        ("saleStart", call0("saleStart()")),
        ("balanceOf_user", callAddr("balanceOf(address)")),
    ]),
]

def decode(h):
    if h is None:
        return None
    h = h[2:] if h.startswith("0x") else h
    if not h:
        return None
    try:
        return int(h, 16)
    except Exception:
        return f"NON-INT:{h[:40]}"

def rpc_batch(calls, timeout=25):
    """calls: list of (id, to, data). Returns {id: result-hex-or-None, '_err': str|None}."""
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, to, data in calls])
    last_err = None
    for url in RPCS:
        try:
            p = subprocess.run(["curl", "-sS", "--max-time", str(timeout), "-X", "POST",
                                "-H", "Content-Type: application/json", "-d", payload, url],
                               capture_output=True, text=True, timeout=timeout + 5)
            if p.returncode != 0 or not p.stdout.strip():
                last_err = f"curl rc={p.returncode} {p.stderr[:80]} @ {url}"
                continue
            d = json.loads(p.stdout)
            if isinstance(d, dict) and "error" in d:
                last_err = f"rpc error {d['error']} @ {url}"
                continue
            out = {}
            for item in d if isinstance(d, list) else [d]:
                out[item.get("id")] = item.get("result")
            return out, None
        except Exception as e:
            last_err = f"{type(e).__name__}: {str(e)[:80]} @ {url}"
    return {}, last_err

def main():
    t0 = time.time()
    results, mode_notes = {}, []
    for name, addr, views in PLAN:
        calls = [(i, addr, data) for i, (vname, data) in enumerate(views)]
        raw, err = rpc_batch(calls)
        if err:
            results[name] = {vname: f"ERROR: {err}" for vname, _ in views}
            mode_notes.append(f"{name}: {err}")
        else:
            results[name] = {vname: decode(raw.get(i)) for i, (vname, _) in enumerate(views)}
    # block number
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})
    block = None
    for url in RPCS:
        try:
            p = subprocess.run(["curl", "-sS", "--max-time", "20", "-X", "POST",
                                "-H", "Content-Type: application/json", "-d", payload, url],
                               capture_output=True, text=True, timeout=25)
            block = int(json.loads(p.stdout)["result"], 16)
            break
        except Exception as e:
            block = f"ERROR: {e}"
    out = {"mode": "curl-batch bsc-dataseed (+defibit fallback)", "block": block,
           "elapsed_s": round(time.time() - t0, 1), "notes": mode_notes,
           "reads": {n: {"address": a, "views": results.get(n, {})} for n, a, _ in PLAN}}
    print(json.dumps(out, indent=1))
    with open(f"{BASE}/hot-leg-2026-11-16-2034-reread.json", "w") as f:
        json.dump(out, f, indent=1)

if __name__ == "__main__":
    main()
