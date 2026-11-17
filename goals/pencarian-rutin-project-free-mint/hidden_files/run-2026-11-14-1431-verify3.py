#!/usr/bin/env python3
"""Follow-up verification run 1431 (part 3): decode string pointers + Hashcat first-mint.
Read-only; writes run-2026-11-14-1431-verify3.json."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-rpc.publicnode.com/", "https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]
t0 = time.time()
out = {"started_wib": "2026-11-14T14:31+07:00"}
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
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
def raw_call(addr, sig, args):
    data = build_data(sig, args)
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": addr, "data": data}, "latest"]}, timeout=60)
            if isinstance(r, dict) and isinstance(r.get("result"), str) and r["result"] not in ("0x",):
                return r["result"], ep
        except Exception:
            continue
    return None, None
def decode_string(hexv):
    if not hexv or len(hexv) < 130: return None
    try:
        b = bytes.fromhex(hexv[2:])
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode("utf-8", "replace")
    except Exception as e:
        return f"<decode fail {e}>"
YUAN = "0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E"
HADE = "0x5aff123300685b6e08aa4396227baf44aabbd4ed"
for label, addr, sig, args in [
    ("yuanbao_contractURI", YUAN, "contractURI()", []),
    ("yuanbao_tokenURI_1", YUAN, "tokenURI(uint256)", [1]),
    ("hashcat_tokenURI_1", HADE, "tokenURI(uint256)", [1]),
    ("hashcat_contractURI", HADE, "contractURI()", []),
]:
    raw, ep = raw_call(addr, sig, args)
    dec = decode_string(raw) if raw else None
    out[label] = {"raw_len": len(raw) if raw else None, "decoded": (dec[:500] if dec else dec), "ep": ep}
    print(label, "=", (dec[:300] if dec else dec), flush=True)
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
def logs_window(addr, frm, to):
    for ep in EPS:  # publicnode first this time
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                              "params": [{"fromBlock": hex(frm), "toBlock": hex(to),
                                          "address": addr, "topics": [TRANSFER, ZERO_TOPIC]}]}, timeout=60)
            if isinstance(r, dict) and isinstance(r.get("result"), list):
                return r["result"], ep, None
        except Exception:
            continue
    return None, None, "all endpoints failed/no-list"
hade = {"windows": []}
for (frm, to) in [(133492000, 133492999), (133493000, 133493999), (133491000, 133491999), (133490000, 133490999)]:
    logs, ep, err = logs_window(HADE, frm, to)
    hade["windows"].append({"from": frm, "to": to, "ep": ep,
                            "n": len(logs) if logs is not None else None,
                            "first_block": int(logs[0]["blockNumber"], 16) if logs else None,
                            "first_ts": int(logs[0]["blockTimestamp"], 16) if logs and "blockTimestamp" in logs[0] else None,
                            "first_token": int(logs[0]["topics"][3], 16) if logs else None,
                            "err": err})
    print("hashcat", frm, to, "n=", len(logs) if logs is not None else err, flush=True)
    if logs:
        break
out["hashcat_first_mint"] = hade
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-14-1431-verify3.json", "w"), indent=1)
print("DONE", out["elapsed_s"])
