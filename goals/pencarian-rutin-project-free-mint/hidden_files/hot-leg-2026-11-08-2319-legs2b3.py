#!/usr/bin/env python3
"""Hot-leg 2319 legs2b-3: Boltbook new-contract notes + fresh reads NUSA/Kitebots/LOCKSMITH
+ Pokechain/Saturnode (Boltbook-new this run, already in snapshot - change-check only)."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-2319"
NOW = "2026-11-08T23:19:38+07:00"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]
seen = json.load(open(BASE + "hot-leg-seen.json"))
log = {"run": "free-mint-hot-leg 2026-11-08 23:19:38 WIB legs2b-3"}
t0 = time.time()

# Leg 2b notes (Boltbook front page EN 46,618 B / ZH 46,802 B, 12 unique addresses):
# both new-vs-seen addresses are ALREADY in the main snapshot -> dedup, no new report.
# Pokechain 0x4ef9...: early-lead-reported-2026-11-08, user ALREADY minted #5381 22:11 WIB,
# website verified, free shape UNVERIFIED on-chain. Saturnode 0x6124...: bridge finding,
# watchlist-only, age UNVERIFIED. Neither is a new lead; change-check only via fresh reads below.
log["leg2b_boltbook"] = {
    "en_bytes": 46618, "zh_bytes": 46802, "zh_first_try": "timeout-20s (skipped, retried OK)",
    "unique_addrs": 12, "new_vs_seen": ["0x4ef929af00cb93993c3d01834c4da79200d31e32",
                                        "0x6124b3ae64ada7b73581ccd01fef89e583e8742c"],
    "new_in_snapshot": 2, "new_not_in_snapshot": 0,
    "keyword_hits": {"free share": 0, "first share free": 0, "1 free share": 0,
                     "free mint share": 0, "免费份额": 0, "首个免费": 0, "免费铸造": 0, "免费mint": 0},
    "note": "Both Boltbook-new addresses already in main snapshot (Pokechain early-lead-reported, "
            "user already minted #5381; Saturnode bridge watchlist-only). No new lead; no report."}

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def post_rpc(ep, payload, timeout=15):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def batch_call(calls):
    """calls: list of (addr, sig, arg) ; arg '' | 'USER' | 'USER1'. Returns {label: int|None} + block."""
    payload = []
    labels = []
    for i, (addr, sig, arg) in enumerate(calls):
        data = sel(sig)
        if arg == "USER": data += enc_addr(USER)
        elif arg == "USER1": data += enc_addr(USER) + format(1, "064x")
        payload.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                        "params": [{"to": addr, "data": data}, "latest"]})
        labels.append(f"{addr}:{sig}")
    payload.append({"jsonrpc": "2.0", "id": len(calls) + 1, "method": "eth_blockNumber", "params": []})
    last_err = None
    for ep in EPS:
        try:
            res = post_rpc(ep, payload, timeout=20)
            if isinstance(res, list):
                by_id = {r.get("id"): r.get("result") for r in res}
                # A list of per-item errors (e.g. publicnode -32005 rate limit) is NOT
                # a usable response: require at least the blockNumber result.
                if by_id.get(len(calls) + 1) is None:
                    last_err = f"{ep}: all items errored (likely rate limit); trying next endpoint"
                    continue
                vals = {}
                for i, lab in enumerate(labels):
                    vals[lab] = to_int(by_id.get(i + 1))
                return {"endpoint": ep, "block": to_int(by_id.get(len(calls) + 1)), "values": vals}
            last_err = f"non-list response from {ep}"
        except Exception as ex:
            last_err = f"{ep}: {type(ex).__name__}: {ex}"
    return {"error": last_err or "all endpoints failed"}

NUSA = "0x7D08289E962f5aEc00d56D67322eb2FD056B687c"
LOCK = "0x05e8738290be6639fD0f7236ebF444E5466D3164"
KITE = "0x8b8e59c014eb3e229e043ae8f3b0d7e201d21db0"
POKE = "0x4EF929aF00cB93993c3D01834C4DA79200d31e32"
SATU = "0x6124b3ae64ada7b73581ccd01fef89e583e8742c"
calls = []
for sig in ["freeMinted()", "sharesMinted()", "paidShares()", "soldOut()", "closed()"]:
    calls.append((NUSA, sig, ""))
for sig in ["freeAvailable(address)", "freeClaimed(address)", "hasMinted(address)"]:
    calls.append((NUSA, sig, "USER"))
for sig in ["freeMinted()", "totalSupply()", "MAX_SUPPLY()", "FREE_CAP()", "FREE_PCT()"]:
    calls.append((KITE, sig, ""))
for sig in ["canFreeMint(address)", "freeClaimed(address)"]:
    calls.append((KITE, sig, "USER"))
for sig in ["freeMintedTotal()", "totalMinted()", "totalSupply()", "mintActive()"]:
    calls.append((LOCK, sig, ""))
for sig in ["freeMinted(address)", "mintedCount(address)", "balanceOf(address)"]:
    calls.append((LOCK, sig, "USER"))
calls.append((POKE, "totalMinted()", ""))
calls.append((POKE, "balanceOf(address)", "USER"))
for sig in ["totalSupply()", "freeClaimed()"]:
    calls.append((SATU, sig, ""))
calls.append((SATU, "balanceOf(address)", "USER"))
res = batch_call(calls)
log["fresh_reads"] = res
json.dump(res, open(BASE + TAG + "-fresh-reads.json", "w"), indent=1)
log["elapsed_sec"] = round(time.time() - t0, 1)
json.dump(log, open(BASE + TAG + "-legs2b3.log", "w"), indent=1)
print(json.dumps(log, indent=1))
print("ELAPSED", round(time.time() - t0, 1))
