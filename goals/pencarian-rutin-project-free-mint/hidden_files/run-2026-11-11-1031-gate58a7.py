import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
ADDR = "0x58a704d9e02FE11c0A61683AE7F606E4366F13eb"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def block():
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception: continue
    return None
h = block()
print("HEAD", h, flush=True)
out = {"head": h, "started_wib": "2026-11-11 ~11:05 WIB"}
try:
    r = post(EPS[0], {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                      "params": [{"to": ADDR, "data": sel("owner()")}, "latest"]}, timeout=25)
    res = r.get("result")
    out["owner"] = "0x" + res[-40:] if res and len(res) >= 42 else res
except Exception as e:
    out["owner_error"] = repr(e)[:200]
print("OWNER", out.get("owner"), flush=True)
ZERO = "0x" + "00" * 32
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
if h:
    params = [{"address": ADDR, "fromBlock": hex(h - 300), "toBlock": hex(h),
               "topics": [TRANSFER, ZERO]}]
    t0 = time.time()
    try:
        r = post(EPS[0], {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs", "params": params}, timeout=25)
        out["getLogs"] = {"elapsed_s": round(time.time() - t0, 1), "result": r}
        print("GETLOGS", json.dumps(r)[:600], flush=True)
    except Exception as e:
        out["getLogs"] = {"elapsed_s": round(time.time() - t0, 1), "error": repr(e)[:300]}
        print("GETLOGS ERROR", repr(e)[:300], flush=True)
try:
    disc = json.load(open(BASE + "same-owner-discards.json"))
    addrs = set()
    owners = set()
    if isinstance(disc, dict):
        for k, v in disc.items():
            if isinstance(k, str) and k.startswith("0x"): addrs.add(k.lower())
            if isinstance(v, dict):
                for f in ("address", "owner", "deployer"):
                    if v.get(f): (owners if f != "address" else addrs).add(str(v[f]).lower())
    elif isinstance(disc, list):
        for v in disc:
            if isinstance(v, dict):
                for f in ("address", "owner", "deployer", "contract"):
                    if v.get(f):
                        (owners if f in ("owner", "deployer") else addrs).add(str(v[f]).lower())
    out["discards_contract_hit"] = ADDR.lower() in addrs
    out["discards_owner_hit"] = (out.get("owner") or "").lower() in owners if out.get("owner") else None
    print("DISCARDS contract_hit:", out["discards_contract_hit"], "owner_hit:", out["discards_owner_hit"], flush=True)
except Exception as e:
    out["discards_error"] = repr(e)[:200]
    print("DISCARDS ERROR", repr(e)[:200], flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-11-1031-probe-58a7-gate.json", "w"), indent=1)
print("DONE", flush=True)
