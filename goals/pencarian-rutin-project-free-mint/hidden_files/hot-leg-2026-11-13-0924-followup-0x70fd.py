"""Follow-up 2026-11-13 09:24 WIB: verify sale-shape 0x70Fd... (S1/S2 PASS via retry)
curl-based raced batch (bsc-dataseed endpoints, same as hot-leg run script).
Read-only; writes only its own result json + appends note to hot-leg-seen.json.
"""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0x70FdD1a7f382893708d00fC2eF9C38cAe7DEC92B"
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

def post_rpc_race(payload, timeout=10):
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

def dec_str(h):
    if not h or h == "0x": return None
    b = bytes.fromhex(h[2:])
    try:
        if len(b) >= 64:
            off = int.from_bytes(b[0:32], "big"); ln = int.from_bytes(b[off:off+32], "big")
            return b[off+32:off+32+ln].decode(errors="replace")
    except Exception: pass
    return h

views = ["START()", "DEADLINE()", "FREE_END()", "FREE_SUPPLY()", "freeSold()", "freeOpen()",
         "paidSold()", "PAID_CAP()", "minted()", "finalized()", "phase()", "floorMet()",
         "PRICE()", "FREE_FEE()", "FREE_PER_AGENT()", "REGISTRY()", "escrowed()",
         "freeQuotaOf(address)", "balanceOf(address)", "name()", "symbol()"]
calls, keys = [], []
for i, sig in enumerate(views):
    base = sig.split("(")[0]
    if "(address)" in sig:
        data = sel(sig) + enc(USER); key = base + "_user"
    else:
        data = sel(sig); key = base
    calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                  "params": [{"to": ADDR, "data": data}, "latest"]})
    keys.append(key)

res = None
for attempt in range(3):
    res = post_rpc_race(calls, timeout=12)
    if res is not None and any(isinstance(it, dict) and it.get("result") for it in res):
        break
    time.sleep(2)

out = {"address": ADDR, "attempts": attempt + 1, "elapsed_s": round(time.time() - T0, 1)}
if res is None:
    out["error"] = "RPC batch failed on all endpoints (3 attempts) - pool/slot/age UNVERIFIED, NOT a lead, retry next run"
else:
    vals = {}
    for it, key in zip(res, keys):
        if isinstance(it, dict) and "error" in it:
            vals[key] = None
        elif isinstance(it, dict):
            vals[key] = it.get("result")
    decoded = {}
    for k, v in vals.items():
        if k in ("name", "symbol"):
            decoded[k] = dec_str(v)
        elif k == "REGISTRY":
            decoded[k] = "0x" + v[-40:] if v and len(v) >= 42 else v
        else:
            decoded[k] = to_int(v)
    out["views"] = decoded
    for k in ("START", "DEADLINE", "FREE_END"):
        v = decoded.get(k)
        if isinstance(v, int) and v > 0:
            out[k + "_wib"] = datetime.fromtimestamp(v, timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
    fs, sold = decoded.get("FREE_SUPPLY"), decoded.get("freeSold")
    if isinstance(fs, int) and isinstance(sold, int) and fs:
        out["pct_free_claimed"] = round(100 * sold / fs, 1)
        out["free_remaining"] = fs - sold
    # tokenURI(1) - method I pointer
    data = sel("tokenURI(uint256)") + format(1, "064x")
    r2 = post_rpc_race([{"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                         "params": [{"to": ADDR, "data": data}, "latest"]}], timeout=10)
    if isinstance(r2, list) and r2 and isinstance(r2[0], dict) and r2[0].get("result"):
        out["tokenURI_1"] = dec_str(r2[0]["result"])

print(json.dumps(out, indent=1))
json.dump(out, open(BASE + "hot-leg-2026-11-13-0924-followup-0x70fd.json", "w"), indent=1)
seen = json.load(open(BASE + "hot-leg-seen.json"))
if isinstance(seen.get(ADDR), dict):
    if out.get("views"):
        s = out["views"]
        note = " | FOLLOWUP-0924: " + ", ".join(f"{k}={v}" for k, v in s.items() if v is not None)[:400]
        if "pct_free_claimed" in out:
            note += f" | free {out['pct_free_claimed']}% ({s.get('freeSold')}/{s.get('FREE_SUPPLY')})"
        seen[ADDR]["note"] = (seen[ADDR].get("note", "") + note)[:900]
    else:
        seen[ADDR]["note"] = (seen[ADDR].get("note", "") + " | FOLLOWUP-0924: RPC batch failed x3 - pool/slot/age UNVERIFIED, NOT a lead, retry next run.")[:900]
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
