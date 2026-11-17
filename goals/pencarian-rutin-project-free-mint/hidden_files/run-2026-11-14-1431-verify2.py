#!/usr/bin/env python3
"""Follow-up verification run 1431: YUANBAO earlier-window first-mint check,
Hashcat first-mint attempt, YUANBAO website-gate pointers (contractURI/tokenURI).
Read-only; writes run-2026-11-14-1431-verify2.json."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
t0 = time.time()
out = {"started_wib": "2026-11-14T14:31+07:00"}
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a, str) and a.startswith("0x") and len(a) == 42 else enc_u(int(a))
    return d
def post_rpc(ep, payload, timeout=60):
    o = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(o)
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
def logs_window(addr, frm, to):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                              "params": [{"fromBlock": hex(frm), "toBlock": hex(to),
                                          "address": addr, "topics": [TRANSFER, ZERO_TOPIC]}]}, timeout=60)
            if isinstance(r, dict) and isinstance(r.get("result"), list):
                return r["result"], ep, None
            return None, ep, str(r)[:150]
        except Exception as e:
            continue
    return None, None, "all endpoints failed"
# YUANBAO earlier windows
YUAN = "0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E"
yuan = {"windows": []}
for (frm, to) in [(133433000, 133434999), (133431000, 133432999)]:
    logs, ep, err = logs_window(YUAN, frm, to)
    yuan["windows"].append({"from": frm, "to": to, "ep": ep,
                            "n": len(logs) if logs is not None else None,
                            "first_block": int(logs[0]["blockNumber"], 16) if logs else None,
                            "first_ts": int(logs[0]["blockTimestamp"], 16) if logs and "blockTimestamp" in logs[0] else None,
                            "err": err})
    print("yuanbao", frm, to, "n=", len(logs) if logs is not None else err, flush=True)
    if logs:
        break
out["yuanbao_earlier"] = yuan
# Hashcat first-mint: estimate ~13:05-13:15 WIB -> blocks ~133492000-133495000; try 2 windows
HADE = "0x5aff123300685b6e08aa4396227baf44aabbd4ed"
hade = {"windows": []}
for (frm, to) in [(133492000, 133493999), (133490000, 133491999)]:
    logs, ep, err = logs_window(HADE, frm, to)
    hade["windows"].append({"from": frm, "to": to, "ep": ep,
                            "n": len(logs) if logs is not None else None,
                            "first_block": int(logs[0]["blockNumber"], 16) if logs else None,
                            "first_ts": int(logs[0]["blockTimestamp"], 16) if logs and "blockTimestamp" in logs[0] else None,
                            "err": err})
    print("hashcat", frm, to, "n=", len(logs) if logs is not None else err, flush=True)
    if logs:
        break
out["hashcat_first_mint"] = hade
# YUANBAO gate pointers: contractURI + tokenURI(0/1)
def batch_read(addr, views):
    calls, meta = [], []
    for key, sig, args in views:
        calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        meta.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=60)
            if not isinstance(res, list) or len(res) != len(calls): continue
            r = {}
            for it, key in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    r[key] = None
                else:
                    v = it["result"]
                    r[key] = to_int(v[:66]) if len(v) >= 66 else v
            return r, ep
        except Exception:
            continue
    return None, None
yreads, yep = batch_read(YUAN, [("contractURI","contractURI()",[]),
    ("tokenURI_0","tokenURI(uint256)",[0]),("tokenURI_1","tokenURI(uint256)",[1]),
    ("name","name()",[]),("symbol","symbol()",[])])
out["yuanbao_pointers"] = {"reads": yreads, "ep": yep}
print("yuanbao pointers:", json.dumps(yreads), flush=True)
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-14-1431-verify2.json", "w"), indent=1)
print("DONE", out["elapsed_s"])
