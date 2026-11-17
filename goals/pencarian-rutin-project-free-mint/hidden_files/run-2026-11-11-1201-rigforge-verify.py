#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-11 11:59 WIB - lean pattern (same as 1144 run).
Leg 1 Sourcify feed (fresh fetch) + shape-check genuinely new contracts only.
Leg 2 Boltbook EN+ZH (fresh fetch). Retry ABI for 0x67dceae0 + 0x9f1ca12e (1149 no-abi).
Leg 3 re-read CAP7 0x748f + Bot Fighters 0x58a7 + RigForge RigSale 0xa1cc (read-only
monitor; fastmint fire armed 11:47 handles the 12:00 execution - hot leg does NOT execute).
Leg 4 priority re-read vs 1149-prio baseline.
Read-only except own hot-leg state files. No preview/mint, no chain scan.
Skip any leg that stalls; target <2 min."""
import json, time, subprocess, re, os
from Crypto.Hash import keccak
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc.nodereal.io/"
EP2 = "https://bsc-dataseed.binance.org/"
T0 = time.time()
NOW_ISO = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
RUN = "2026-11-11 11:59 WIB"
STAMP = "2026-11-11-1159"

def curl(url, timeout=20, post=None, ep=None):
    cmd = ["curl", "-s", "-L", "--max-time", str(timeout)]
    if post is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "--data", post]
    cmd.append(ep or url)
    pr = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
    return pr.stdout, pr.returncode

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def batch_call(addr, datas, timeout=25):
    calls = [{"jsonrpc": "2.0", "id": i+1, "method": "eth_call",
              "params": [{"to": addr, "data": d}, "latest"]} for i, (_, d) in enumerate(datas)]
    payload = json.dumps(calls)
    for ep in (EP, EP2):
        try:
            out, rc = curl(None, timeout, post=payload, ep=ep)
            resps = json.loads(out)
            if isinstance(resps, dict): resps = [resps]
            if len(resps) != len(calls): continue
            outd = {}
            for (key, _), r in zip(datas, resps):
                outd[key] = r.get("result") if isinstance(r, dict) and "error" not in r else None
            return outd
        except Exception:
            continue
    return None

# ---------- Leg 1: Sourcify feed (fresh fetch) ----------

import json as _json
RIGSALE = "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d"
AGENT_ID = 107187496765866644729837695198686237165740365523485558112864918211974996443404
TX = "0xe766edcbb12cc56f1e4a93e32439942644152d6324949d034b83fb2bdcce1cbc"
_b, _rc = curl(None, 15, post=_json.dumps({"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}), ep=EP)
block = int(_json.loads(_b)["result"], 16)
_rcpt, _ = curl(None, 20, post=_json.dumps({"jsonrpc":"2.0","method":"eth_getTransactionReceipt","params":[TX],"id":2}), ep=EP)
rcpt = _json.loads(_rcpt).get("result")
views = [
 ("freeSharesLeft", sel("freeSharesLeft()")), ("openedAt", sel("openedAt()")),
 ("sharesLeftFor_agentId", sel("sharesLeftFor(uint256)") + enc_uint(AGENT_ID)),
 ("agentShares_agentId", sel("agentShares(uint256)") + enc_uint(AGENT_ID)),
 ("freeTaken_agentId", sel("freeTaken(uint256)") + enc_uint(AGENT_ID)),
 ("freeBooked_user", sel("freeBooked(address)") + enc_addr(USER)),
 ("freeSharesClaimed", sel("freeSharesClaimed()")),
]
raw = batch_call(RIGSALE, views, timeout=25)
out = {"block_now": block, "tx": TX}
out["receipt"] = {"blockNumber": int(rcpt["blockNumber"],16) if rcpt else None, "status": rcpt.get("status") if rcpt else None, "gasUsed": int(rcpt["gasUsed"],16) if rcpt else None, "from": rcpt.get("from") if rcpt else None, "to": rcpt.get("to") if rcpt else None} if rcpt else None
for k,v in (raw or {}).items():
    out[k] = to_int(v)
print(_json.dumps(out, indent=1))
_json.dump(out, open(BASE + "run-2026-11-11-1201-rigforge-verify.json","w"), indent=1)
