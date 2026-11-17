#!/usr/bin/env python3
"""Hot-leg 0014 leg4 RETRY: batched re-read with chunk=10 (dataseed rejects batches of
50+/150 calls with a 1-element error list; batch of 5 verified OK). Overwrites the
all-null run-2026-11-09-0014-reread.json and corrects hot-leg-2026-11-09-0014.json."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = "2026-11-09T00:14:38+07:00"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc.publicnode.com/"]
t0 = time.time()

def curl(url, timeout=20, post=None):
    cmd = ["curl", "-sL", "--max-time", str(timeout)]
    if post is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(post)]
    cmd.append(url)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5).stdout

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def batch_calls(calls, chunk=10):
    out = {}
    blk = None
    def run_chunk(part):
        payload = []
        for i, (lab, addr, sig, arg) in enumerate(part):
            data = sel(sig)
            if arg == "USER": data += enc_addr(USER)
            payload.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                            "params": [{"to": addr, "data": data}, "latest"]})
        payload.append({"jsonrpc": "2.0", "id": len(part) + 1, "method": "eth_blockNumber", "params": []})
        for ep in EPS:
            try:
                res = json.loads(curl(ep, timeout=20, post=payload))
                if isinstance(res, list) and len(res) == len(part) + 1:
                    by_id = {r.get("id"): r.get("result") for r in res}
                    if by_id.get(len(part) + 1) is None: continue
                    vals = {part[i][0]: to_int(by_id.get(i + 1)) for i in range(len(part))}
                    return vals, to_int(by_id.get(len(part) + 1))
            except Exception:
                continue
        return {lab: None for lab, _, _, _ in part}, None
    chunks = [calls[i:i + chunk] for i in range(0, len(calls), chunk)]
    with ThreadPoolExecutor(max_workers=8) as ex:
        for vals, b in ex.map(run_chunk, chunks):
            out.update(vals)
            if b is not None: blk = b
    return out, blk

snap = json.load(open(BASE + "onchain-snapshot.json"))
prev = json.load(open(BASE + "run-2026-11-09-0004-reread.json"))
C_VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
           "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
           "freeClaimed(address)"]
C_KEYS = ["totalSupply", "totalMinted", "freeClaimed", "freeMinted",
          "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"]
T_VIEWS = ["totalSupply()", "freeMinted()", "freeSharesRemaining()",
           "balanceOf(address)", "freeClaimed(address)"]
T_KEYS = ["totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"]

calls = []
contracts = {}
for name, v in snap.get("contracts", {}).items():
    if isinstance(v, dict) and v.get("address"):
        contracts[name] = v["address"]
        for k, sig in zip(C_KEYS, C_VIEWS):
            calls.append((f"C|{name}|{k}", v["address"], sig, "USER" if "address" in sig else ""))
track_c = {}
for name, v in snap.get("track_c", {}).items():
    if not isinstance(v, dict): continue
    addr = v.get("sale") or v.get("token")
    if not addr: continue
    track_c[name] = addr
    for k, sig in zip(T_KEYS, T_VIEWS):
        calls.append((f"T|{name}|{k}", addr, sig, "USER" if "address" in sig else ""))

vals, blk = batch_calls(calls, chunk=10)
reread = {"block": blk, "reread": {}, "track_c": {}, "started_wib": NOW, "retry_note": "chunk=10"}
for name, addr in contracts.items():
    reread["reread"][name] = {"address": addr}
    for k in C_KEYS:
        reread["reread"][name][k] = vals.get(f"C|{name}|{k}")
for name, addr in track_c.items():
    reread["track_c"][name] = {"address": addr}
    for k in T_KEYS:
        reread["track_c"][name][k] = vals.get(f"T|{name}|{k}")
json.dump(reread, open(BASE + "run-2026-11-09-0014-reread.json", "w"), indent=1)

n_nonnull = sum(1 for sec in ("reread", "track_c") for o in reread[sec].values()
                for k, v in o.items() if k != "address" and v is not None)
n_tot = sum(1 for sec in ("reread", "track_c") for o in reread[sec].values()
            for k, v in o.items() if k != "address")
diffs, recoveries = [], []
for section in ("reread", "track_c"):
    for name, cur in reread[section].items():
        for k, v in cur.items():
            if k == "address": continue
            ov = prev.get(section, {}).get(name, {}).get(k)
            if v != ov:
                if ov is None and v is not None:
                    recoveries.append({"item": name, "field": k, "old": ov, "new": v})
                elif v is None:
                    pass
                else:
                    diffs.append({"item": name, "field": k, "old": ov, "new": v})

summary = json.load(open(BASE + "hot-leg-2026-11-09-0014.json"))
summary["legs"]["reread"] = (f"RETRY ok (chunk=10), block {blk}, {len(contracts)} contracts + "
    f"{len(track_c)} track_c re-read; {n_nonnull}/{n_tot} values non-null; {len(diffs)} changes, "
    f"{len(recoveries)} null->value recoveries. First attempt chunk=150 FAILED (all-null, block None) "
    f"- dataseed rejects batches >=50 with a 1-element error list; batch of 5 verified OK.")
summary["reread_diffs"] = diffs
summary["reread_recoveries"] = recoveries
summary["reread_retry_elapsed_sec"] = round(time.time() - t0, 1)
json.dump(summary, open(BASE + "hot-leg-2026-11-09-0014.json", "w"), indent=1)
print(json.dumps({"block": blk, "non_null": f"{n_nonnull}/{n_tot}",
                  "diffs": diffs, "recoveries": recoveries,
                  "elapsed": round(time.time() - t0, 1)}, indent=1))
