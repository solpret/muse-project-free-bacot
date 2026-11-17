#!/usr/bin/env python3
"""Deep-dive triage 2 for 0xfF17 (free-mint-search run 2026-11-14 02:01 WIB).
1) eth_getLogs Transfer-from-zero to 0xfF17 over last ~3000 blocks (3x 1000-block
   chunks via dataseed) to verify first mints on-chain.
2) questionFor(user)/answerFor(user)/priceFor(user)/statusOf(1)/participantsOf(1)
   to characterize the free-mint path (quiz-gated).
3) tokenURI(1) with proper string decode (method I: metadata/site evidence).
Read-only; no preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
FF17 = "0xfF172b79d040faefA1Bf34B47151edc87130246E"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "0" * 64
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def post_rpc(ep, payload, timeout=30):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        else:
            d += enc_u(int(a))
    return d
def batch(addr, views):
    calls, keys = [], []
    for i, (key, sig, args) in enumerate(views):
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=30)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            out = {}
            for it, key in zip(res, keys):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    out[key] = None
                else:
                    out[key] = it["result"]
            return out
        except Exception:
            continue
    return None
def head():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
            if isinstance(r, dict) and r.get("result"):
                return int(r["result"], 16)
        except Exception:
            continue
    return None

def decode_u256_list(hexstr):
    """Decode a return of N uint256 values."""
    b = bytes.fromhex(hexstr[2:])
    n = len(b) // 32
    return [int.from_bytes(b[i*32:(i+1)*32], "big") for i in range(n)]
def decode_string(hexstr):
    b = bytes.fromhex(hexstr[2:])
    if len(b) < 64:
        return None
    off = int.from_bytes(b[0:32], "big")
    ln = int.from_bytes(b[off:off+32], "big")
    return b[off+32:off+32+ln].decode("utf-8", "replace")

h = head()
print("head:", h, flush=True)
out = {"head": h}
# --- views ---
U = [USER]
raw = batch(FF17, [
    ("questionFor_user", "questionFor(address)", U),
    ("answerFor_user", "answerFor(address)", U),
    ("priceFor_user", "priceFor(address)", U),
    ("statusOf_1", "statusOf(uint256)", [1]),
    ("participantsOf_1", "participantsOf(uint256)", [1]),
    ("tokenURI_1", "tokenURI(uint256)", [1]),
    ("totalSnippets", "totalSnippets()", []),
    ("genesisOpen", "genesisOpen()", []),
])
views = {}
if raw:
    if raw.get("questionFor_user"):
        try: views["questionFor_user"] = decode_u256_list(raw["questionFor_user"])
        except Exception as e: views["questionFor_user"] = {"err": str(e)}
    if raw.get("answerFor_user"):
        try: views["answerFor_user"] = decode_u256_list(raw["answerFor_user"])
        except Exception as e: views["answerFor_user"] = {"err": str(e)}
    if raw.get("priceFor_user"):
        views["priceFor_user_wei"] = to_int(raw["priceFor_user"][:66]) if len(raw["priceFor_user"]) >= 66 else raw["priceFor_user"]
    if raw.get("statusOf_1"):
        views["statusOf_1"] = to_int(raw["statusOf_1"][:66])
    if raw.get("participantsOf_1"):
        views["participantsOf_1"] = to_int(raw["participantsOf_1"][:66])
    if raw.get("tokenURI_1"):
        try: views["tokenURI_1"] = decode_string(raw["tokenURI_1"])
        except Exception as e: views["tokenURI_1"] = {"err": str(e)}
    if raw.get("totalSnippets"):
        views["totalSnippets"] = to_int(raw["totalSnippets"][:66])
    if raw.get("genesisOpen"):
        views["genesisOpen"] = to_int(raw["genesisOpen"][:66])
out["views"] = views
print(json.dumps(views, indent=1), flush=True)

# --- logs: Transfer from zero, last 3000 blocks, 1000-block chunks ---
logs_all, log_errors = [], []
if h:
    for start in (h - 3000, h - 2000, h - 1000):
        params = {"fromBlock": hex(start), "toBlock": hex(min(start + 999, h)),
                  "address": FF17, "topics": [TRANSFER, ZERO]}
        ok = False
        for ep in EPS:
            try:
                r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                                  "params": [params]}, timeout=30)
                if isinstance(r, dict) and "result" in r and isinstance(r["result"], list):
                    logs_all.extend(r["result"])
                    print(f"chunk {start}-{min(start+999,h)}: {len(r['result'])} logs via {ep}", flush=True)
                    ok = True
                    break
                else:
                    print(f"chunk {start}: {ep} -> {str(r)[:150]}", flush=True)
            except Exception as e:
                print(f"chunk {start}: {ep} EXC {str(e)[:120]}", flush=True)
        if not ok:
            log_errors.append(f"chunk {start} FAILED all endpoints")
out["logs_count"] = len(logs_all)
out["log_errors"] = log_errors
mints = []
for lg in logs_all:
    try:
        blk = int(lg["blockNumber"], 16)
        tid = int(lg["topics"][3], 16) if len(lg.get("topics", [])) > 3 else None
        to = "0x" + lg["topics"][2][26:] if len(lg.get("topics", [])) > 2 else None
        mints.append({"block": blk, "tokenId": tid, "to": to, "tx": lg.get("transactionHash")})
    except Exception:
        pass
out["mints"] = sorted(mints, key=lambda m: m["block"])
print("MINTS:", json.dumps(out["mints"], indent=1), flush=True)
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-14-0201-triage-ff17-logs.json", "w"), indent=1)
print("DONE elapsed", out["elapsed_s"])
