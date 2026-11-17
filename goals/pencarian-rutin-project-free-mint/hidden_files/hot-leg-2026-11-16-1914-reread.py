#!/usr/bin/env python3
"""Hot-leg 2026-11-16 19:14 WIB — leg 4 batch re-read (read-only), curl-based.
Per-contract JSON-RPC batches to bsc-dataseed (fallback defibit), same PLAN
as the 19:04 run: AGCLUB, BinanceAI-mint, ORBIT, RigForge, CosmicSentinel,
BUBB, Vezlune, Poffzi. fast_rpc batch_race stalled >280s at 19:04, so it is
not used here."""
import json, subprocess, time
from eth_hash.auto import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
ENDPOINTS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.defibit.io/"]

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
    ("Vezlune", "0xA9531f2C18E9398b50c13f1a108EbE7462927154", [
        ("totalSupply", call0("totalSupply()")),
        ("totalMinted", call0("totalMinted()")),
        ("freeMinted", call0("freeMinted()")),
        ("FREE_SUPPLY", call0("FREE_SUPPLY()")),
        ("mintOpen", call0("mintOpen()")),
        ("saleOpen", call0("saleOpen()")),
        ("saleStart", call0("saleStart()")),
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
    except ValueError:
        return f"RAW:{h[:40]}"

def rpc_batch(calls, endpoint, timeout=25):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)])
    p = subprocess.run(["curl", "-sS", "--max-time", str(timeout), "-X", "POST",
                        "-H", "Content-Type: application/json", "-d", payload,
                        endpoint], capture_output=True, text=True, timeout=timeout + 5)
    if p.returncode != 0:
        raise RuntimeError(f"curl rc={p.returncode} {p.stderr[:120]}")
    d = json.loads(p.stdout)
    if isinstance(d, dict) and "error" in d:
        raise RuntimeError(f"rpc error: {d['error']}")
    return [r.get("result") if isinstance(r, dict) else None for r in d]

def rpc_single(method, endpoint, timeout=20):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": []})
    p = subprocess.run(["curl", "-sS", "--max-time", str(timeout), "-X", "POST",
                        "-H", "Content-Type: application/json", "-d", payload,
                        endpoint], capture_output=True, text=True, timeout=timeout + 5)
    d = json.loads(p.stdout)
    return d.get("result")

def main():
    t0 = time.time()
    reads = {}
    for name, addr, views in PLAN:
        calls = [(addr, data) for _, data in views]
        got = None
        err = None
        for ep in ENDPOINTS:
            try:
                got = rpc_batch(calls, ep)
                break
            except Exception as e:
                err = f"{ep}: {type(e).__name__}: {str(e)[:100]}"
        if got is None:
            reads[name] = {"address": addr, "error": err,
                           "views": {v: "ERROR" for v, _ in views}}
            print(name, "FAILED:", err, flush=True)
            continue
        vals = {v: decode(r) for (v, _), r in zip(views, got)}
        reads[name] = {"address": addr, "views": vals}
        print(name, vals, flush=True)
    block = None
    for ep in ENDPOINTS:
        try:
            block = int(rpc_single("eth_blockNumber", ep), 16)
            break
        except Exception:
            continue
    out = {"mode": "curl-per-contract-batch", "block": block,
           "elapsed_s": round(time.time() - t0, 1), "reads": reads}
    print("BLOCK:", block, "elapsed:", out["elapsed_s"])
    with open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-16-1914-reread.json", "w") as f:
        json.dump(out, f, indent=1)

if __name__ == "__main__":
    main()
