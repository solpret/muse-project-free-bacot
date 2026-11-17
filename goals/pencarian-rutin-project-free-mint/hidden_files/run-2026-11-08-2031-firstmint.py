#!/usr/bin/env python3
"""Deep first-mint check for 4 agent-shaped first-seen candidates, run 2031.
Address-filtered ankr_getLogs (Transfer from zero), big chunks (20k blocks),
walk back up to ~48h. Block timestamps via dataseed (Ankr timestamps are fake).
Also reads extra free views (FREE_CAP/FREE_POOL/freeRemaining/freeOf).
Read-only; writes run-2026-11-08-2031-firstmint.json."""
import sys, json, time, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import _post as _fr_post
from ankr import ankr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
T0 = time.time()

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None
def call(addr, data):
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]},
                           timeout=10, retries=0)
            if isinstance(out, dict) and "result" in out: return out["result"]
            if isinstance(out, dict) and "error" in out: return None
        except Exception: continue
    return None
def block_time_wib(blk):
    for ep in EPS:
        try:
            r = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                              "params": [hex(blk), False]}, timeout=10, retries=0)
            if r and r.get("result"):
                ts = int(r["result"]["timestamp"], 16)
                return datetime.datetime.fromtimestamp(
                    ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception: continue
    return None
def head_block():
    for ep in EPS:
        try:
            r = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber",
                              "params": []}, timeout=10, retries=0)
            return int(r["result"], 16)
        except Exception: continue
    return None

def first_mint(addr, head):
    """Walk back in 20k-block chunks (max ~48h ~ 384k blocks).
    Stop after 3 consecutive EMPTY chunks older than the earliest mint found
    (launch window bracketed), or at the 48h boundary. Returns evidence dict."""
    earliest = None
    total = 0
    chunks = 0
    empty_after_earliest = 0
    CH = 20000
    frm = head
    while frm > head - 384000:
        to = frm
        frm = max(0, frm - CH + 1)
        chunks += 1
        params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
                  "address": addr, "pageSize": 1000, "decodeLogs": False,
                  "topics": [TRANSFER, ZERO_TOPIC]}
        try:
            body = ankr_post("ankr_getLogs", params, timeout=30)
        except Exception as e:
            return {"error": str(e)[:200], "earliest_block": earliest, "logs": total, "chunks": chunks}
        logs = (body.get("result", {}) or {}).get("logs", []) if isinstance(body, dict) else []
        n4 = 0
        for lg in logs:
            if len(lg.get("topics", [])) == 4:
                blk = int(lg["blockNumber"], 16)
                total += 1
                n4 += 1
                if earliest is None or blk < earliest: earliest = blk
        print(f"  chunk {frm}-{to}: {n4} mints, earliest so far {earliest}", flush=True)
        if earliest is not None and to < earliest:
            if n4 == 0:
                empty_after_earliest += 1
                if empty_after_earliest >= 3:
                    break
            else:
                empty_after_earliest = 0
        time.sleep(1.0)
    return {"earliest_block": earliest, "logs": total, "chunks": chunks,
            "empty_chunks_after_earliest": empty_after_earliest,
            "walked_to_block": frm,
            "boundary_hit": earliest is not None and earliest <= head - 384000 + CH}

CANDS = {
    "BMT Agents": "0x7D6e8528cc918Afbd0ba5B0998C8a57860D2Ded6",
    "Pressure": "0xD61aF26aD1D8D9903436455e665d38167AcCCbEc",
    "Pilotchrome": "0x3AD8738C82aDe72bc632eA58a51E2368847BBf44",
    "Forklings": "0xD7B3FD33e0b465B0e374906F60567D317b758FD8",
}
head = head_block()
print("HEAD", head, flush=True)
out = {"head": head}
for name, addr in CANDS.items():
    print(f"== {name} {addr}", flush=True)
    r = first_mint(addr, head)
    if r.get("earliest_block"):
        r["earliest_wib"] = block_time_wib(r["earliest_block"])
    # extra free views
    r["FREE_CAP"] = to_int(call(addr, sel("FREE_CAP()")))
    r["FREE_POOL"] = to_int(call(addr, sel("FREE_POOL()")))
    r["freeRemaining"] = to_int(call(addr, sel("freeRemaining()")))
    r["freeOf_user"] = to_int(call(addr, sel("freeOf(address)") + enc_addr(USER)))
    r["freeMintCount"] = to_int(call(addr, sel("freeMintCount()")))
    r["paidMintCount"] = to_int(call(addr, sel("paidMintCount()")))
    out[name] = r
    print(f"  => {name}: earliest={r.get('earliest_block')} {r.get('earliest_wib')} logs={r.get('logs')} "
          f"FREE_CAP={r.get('FREE_CAP')} FREE_POOL={r.get('FREE_POOL')} freeRemaining={r.get('freeRemaining')} "
          f"freeOf_user={r.get('freeOf_user')}", flush=True)

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{BASE}/run-2026-11-08-2031-firstmint.json", "w"), indent=1)
print(f"DONE in {out['elapsed_s']}s", flush=True)
