"""Follow-up 2026-11-13 09:24 WIB leg4-lite: re-read 3 change-sensitive items whose
leg4/leg3 reads were NULL or deadline-skipped in the 0924 run (RPC slow then, recovered now).
- Agentx 0x64a5: 56,3% at 0809; could cross 70% -> strong lead (gate-blocked).
- RESUME 0xBC1B: 444/3000 at 00:04, sellout predicted ~09:30 WIB today.
- JNTM 0x1320: track-C lead, quote(user,1) still NULL.
Read-only; writes only its own result json + note appends to hot-leg-seen.json.
"""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

def _post_one(ep, payload, timeout=10):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)

def post_rpc_race(payload, timeout=12):
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(_post_one, ep, payload, timeout): ep for ep in EPS}
        for fut in as_completed(futs):
            try:
                res = fut.result()
                if isinstance(res, list) and len(res) == len(payload):
                    return res
            except Exception:
                continue
    return None

def batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for _ in range(3):
        res = post_rpc_race(calls, timeout=12)
        if res is not None and any(isinstance(it, dict) and it.get("result") for it in res):
            return {k: (None if (isinstance(it, dict) and "error" in it)
                        else (to_int(it.get("result")) if isinstance(it, dict) else None))
                    for it, k in zip(res, keys)}
        time.sleep(2)
    return None

out = {"run": "hot-leg 0924 leg4-lite follow-up", "started_wib":
       datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")}

# Agentx
AX = "0x64a5e5f475defdf9b7302cc40641a1cbcb94e492"
ax = batch(AX, ["freeMinted()", "FREE_CAP()", "mintOpen()", "freeClaimed(address)",
                "balanceOf(address)", "totalMinted()", "mintOpensAt()"])
out["agentx"] = ax
if ax and ax.get("freeMinted") is not None and ax.get("FREE_CAP"):
    out["agentx_pct"] = round(100 * ax["freeMinted"] / ax["FREE_CAP"], 1)

# RESUME (S2)
BC = "0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053"
bc = batch(BC, ["freeCount()", "FREE_CAP()", "freeMinted(address)", "balanceOf(address)",
                "totalSupply()", "saleStart()", "refundOpen()", "paidMinted(address)"])
out["resume"] = bc
if bc and bc.get("freeCount") is not None and bc.get("FREE_CAP"):
    out["resume_pct"] = round(100 * bc["freeCount"] / bc["FREE_CAP"], 1)

# JNTM quote(user,1)
JNTM = "0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b"
data = sel("quote(address,uint256)") + enc(USER) + format(1, "064x")
q = None
for _ in range(3):
    res = post_rpc_race([{"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": JNTM, "data": data}, "latest"]}], timeout=12)
    if isinstance(res, list) and res and isinstance(res[0], dict) and res[0].get("result"):
        try:
            b = bytes.fromhex(res[0]["result"][2:])
            words = [int.from_bytes(b[i:i + 32], "big") for i in range(0, min(len(b), 160), 32)]
            tail = None
            if len(words) >= 5 and words[4] < len(b):
                off = words[4]; ln = int.from_bytes(b[off:off + 32], "big")
                tail = b[off + 32:off + 32 + ln].decode(errors="replace")
            q = {"words": words, "tail_string": tail}
            break
        except Exception as e:
            q = {"decode_error": str(e)[:100]}; break
    time.sleep(2)
out["jntm_quote_user_1"] = q
# JNTM pool read too
jm = batch(JNTM, ["totalMinted()", "mintStart()", "freeClaimed()", "FREE_LOTS_CAP()",
                  "TOTAL_LOTS()", "freeSharesRemaining()", "mintOpen()"])
out["jntm_views"] = jm

out["elapsed_s"] = round(time.time() - T0, 1)
print(json.dumps(out, indent=1))
json.dump(out, open(BASE + "hot-leg-2026-11-13-0924-leg4lite.json", "w"), indent=1)
seen = json.load(open(BASE + "hot-leg-seen.json"))
def note_append(addr, text):
    if isinstance(seen.get(addr), dict):
        seen[addr]["note"] = (seen[addr].get("note", "") + text)[:900]
if ax:
    note_append(AX, f" | LEG4LITE-0924: " + ", ".join(f"{k}={v}" for k, v in ax.items() if v is not None)[:300] +
                (f" | {out.get('agentx_pct')}%" if out.get("agentx_pct") is not None else ""))
if bc:
    note_append(BC, f" | LEG4LITE-0924: " + ", ".join(f"{k}={v}" for k, v in bc.items() if v is not None)[:300] +
                (f" | {out.get('resume_pct')}%" if out.get("resume_pct") is not None else ""))
if jm:
    note_append(JNTM, f" | LEG4LITE-0924: " + ", ".join(f"{k}={v}" for k, v in jm.items() if v is not None)[:300] +
                (f" | quote1={q}" if q else " | quote1=NULL"))
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
