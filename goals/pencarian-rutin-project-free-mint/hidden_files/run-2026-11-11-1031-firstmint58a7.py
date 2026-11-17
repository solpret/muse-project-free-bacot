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
def head():
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception: continue
    return None
def ts_at(blk):
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": ADDR, "data": sel("totalSupply()")}, hex(blk)]}, timeout=25)
            res = r.get("result")
            if res is None: return None
            return int(res, 16)
        except Exception: continue
    return None
h = head()
print("HEAD", h, flush=True)
out = {"head": h, "started_wib": "2026-11-11 ~11:10 WIB", "reads": {}}
if h:
    # coarse brackets: head-1000, -3000, -6000, -12000
    for d in (1000, 3000, 6000, 12000):
        b = h - d
        v = ts_at(b)
        out["reads"][str(b)] = v
        print(f"totalSupply @{b} (head-{d}): {v}", flush=True)
    # bisect between the last zero and first nonzero, if bracketed
    pts = sorted(((int(k), v) for k, v in out["reads"].items()), key=lambda x: x[0])
    zero_pts = [b for b, v in pts if v == 0]
    nz_pts = [b for b, v in pts if v is not None and v > 0]
    if zero_pts and nz_pts:
        lo, hi = max(zero_pts), min(nz_pts)
        print(f"BISECT {lo} (0) .. {hi} ({out['reads'][str(hi)]})", flush=True)
        while hi - lo > 1:
            mid = (lo + hi) // 2
            v = ts_at(mid)
            print(f"  @{mid}: {v}", flush=True)
            if v is None:
                break
            out["reads"][str(mid)] = v
            if v == 0: lo = mid
            else: hi = mid
        out["first_mint_block"] = hi
        out["first_mint_block_supply"] = out["reads"].get(str(hi))
        print("FIRST MINT BLOCK ~", hi, flush=True)
    elif nz_pts and not zero_pts:
        out["note"] = "totalSupply > 0 at oldest bracket (head-12000); launch older than ~2.8h or state pruned beyond; NOT bracketed"
        print("NOT BRACKETED: >0 at head-12000", flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-11-1031-probe-58a7-firstmint.json", "w"), indent=1)
print("DONE", flush=True)
