#!/usr/bin/env python3
"""Hot-leg run 2026-11-12 19:59 WIB — follow-up: (a) retry 25 null leg4 reads from
main run (raced batches); (b) OBFG first-mint probe via eth_getLogs Transfer-from-zero
(fromBlock just before saleStart block) + block timestamp; (c) THONK small retry.
Hard deadline T0+170s. Read-only; writes only own file. Baseline compare uses
first-wins newest-first merge, skipping views=None."""
import json, time, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-12-1959"
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
OBFG = "0x5314071bba19943f58347bA5deC423E5032A6818"
out = {"run": "free-mint-hot-leg 2026-11-12 19:59 WIB follow-up", "started_wib": now_wib}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def _post_one(ep, payload, timeout=12):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)
def post_rpc_race(payload, timeout=12):
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = {ex.submit(_post_one, ep, payload, timeout): ep for ep in EPS}
        for fut in as_completed(futs):
            try:
                res = fut.result()
                if isinstance(res, list) and len(res) == len(payload):
                    return res
            except Exception:
                continue
    return None
def raw_batch(addr, views):
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
    res = post_rpc_race(calls, timeout=12)
    if res is None:
        return None
    return {key: (None if (isinstance(it, dict) and "error" in it)
                  else (to_int(it.get("result")) if isinstance(it, dict) else None))
            for it, key in zip(res, keys)}

VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
         "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)", "freeClaimed(address)",
         "freeUsed(address)", "mintedBy(address)", "freeMintedBy(address)", "mintStart()",
         "freeLeft()", "freeAvailable(address)", "saleStart()", "saleEnd()", "PRICE()",
         "price()", "launched()", "freeSharesLeft()", "openedAt()", "freeSharesRemaining()",
         "freeClaimedByWallet(address)", "currentState()", "finalized()", "refunding()",
         "totalFreeMinted()", "FREE_SHARES()", "freeLeftFor(address)"]
TARGETS = [
    ("RunicKey", "0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4"),
    ("BinanceLife", "0x4367b86F889014e6fD57fE812B86A581b913C645"),
    ("SEVEN", "0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96"),
    ("Snailings", "0x5d8f22549fdba6a437c40564d2a65664e714034b"),
    ("RAMRAIDERS", "0x98dcfdeb5e015bbb3c9aca2a90ba0ee80e35315b"),
    ("Pathwyrm", "0xf100c608913dc07ed268bea865fca10004f04657"),
    ("SUDOSAINTS", "0x869d330bb48e7ab32da16745ef9a36a69d34f12f"),
    ("CRTSAINTS", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F"),
    ("NOVA2", "0xdbbc87ae7734e4a16958426f204e6f79ce92e630"),
    ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"),
    ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d"),
    ("0x016b9CE7", "0x016b9CE7508628e4Fb19E4fAF3129Fdc41b150d7"),
    ("0x2e50", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3"),
    ("MOONDRILL", "0x87b354E2014D2e418927A1105dD219A2e7b063b0"),
    ("NAOMI", "0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9"),
    ("AgenticGangster", "0x0a2a07ef09dd7d83e2312476f0588abaa3e34ce3"),
    ("AGCR", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc"),
    ("Ronin", "0xF62FA2ee1490708D51DeF7212493D5c7878Fa110"),
    ("DragonAgent", "0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6"),
    ("Kitebots", "0x8B8e59c014eb3E229e043AE8F3B0D7E201d21DB0"),
    ("Kongtou-AirdropCnNFT", "0xb5A132A2Efd8351DA2c04e38E2568dd8DC5b1c1a"),
    ("0x7Eb9", "0x7Eb92041aa3037e39baA88154F279e3D9F85c593"),
    ("MECHA", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78"),
    ("OliverAgents", "0xad86e4d52e55709d1bda08f922853d4b109e0810"),
    ("DACIT", "0x90ddd762f407b3edf43f732cd5a68a9e4695a6bd"),
]
reads = {}
for name, addr in TARGETS:
    if time.time() > T0 + 150:
        reads[name] = {"address": addr, "error": "deadline-hit-skipped"}; continue
    r = raw_batch(addr, VIEWS)
    reads[name] = {"address": addr, "views": r}
    if r: reads[name]["summary"] = {k: v for k, v in r.items() if v is not None}
out["leg4_retry"] = reads

# THONK small retry (watchlist-only S1, age-unverified)
THONK = "0x22e69F9a7BeC3D991C0ceB5a103E509319E42B2A"
thonk_r = None
if time.time() < T0 + 155:
    thonk_r = raw_batch(THONK, ["freeMinted()", "FREE_SUPPLY()", "freeAvailable(address)",
                                "totalMinted()", "saleStart()", "mintOpen()"])
out["leg3_retry_thonk"] = {"views": thonk_r,
                          "summary": {k: v for k, v in thonk_r.items() if v is not None} if thonk_r else None}

# OBFG first-mint probe: Transfer-from-zero logs, fromBlock ~15 min before saleStart
probe = None
try:
    if time.time() < T0 + 165:
        payload = [{"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                    "params": [{"fromBlock": "0x7ef58c0", "toBlock": "latest", "address": OBFG,
                                "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                                           "0x0000000000000000000000000000000000000000000000000000000000000000"]}]}]
        res = post_rpc_race(payload, timeout=15)
        logs = res[0].get("result") if isinstance(res, list) and res and isinstance(res[0], dict) else None
        if isinstance(logs, list) and logs:
            first = logs[0]
            blk = int(first.get("blockNumber", "0x0"), 16)
            probe = {"n_logs": len(logs), "first_block": blk, "first_tx": first.get("transactionHash")}
            rb = post_rpc_race([{"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                 "params": [hex(blk), False]}], timeout=12)
            if isinstance(rb, list) and rb and isinstance(rb[0], dict):
                ts = (rb[0].get("result") or {}).get("timestamp")
                if ts:
                    probe["first_block_ts"] = int(ts, 16)
                    probe["first_block_wib"] = datetime.fromtimestamp(
                        int(ts, 16), tz=timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        elif isinstance(logs, list):
            probe = {"n_logs": 0, "note": "no Transfer-from-zero in range"}
        else:
            probe = {"error": "getLogs unreadable", "raw": str(res)[:200]}
except Exception as e:
    probe = {"error": str(e)[:150]}
out["first_mint_probe"] = probe

# Compare retry reads vs 1959 main + 1944 baselines (first-wins newest-first, skip None views)
changes = []
try:
    prev = {}
    for f in ("hot-leg-run-2026-11-12-1959.json", "run-2026-11-12-1959-verify2.json",
              "hot-leg-run-2026-11-12-1944.json", "run-2026-11-12-1944-verify2.json",
              "hot-leg-2026-11-12-1944-followup.json",
              "hot-leg-run-2026-11-12-1939.json", "run-2026-11-12-1939-verify2.json",
              "hot-leg-2026-11-12-1939-followup.json"):
        try:
            d = json.load(open(BASE + f))
            for _n, _e in (d.get("leg4_reads") or d.get("reads") or d.get("leg4_retry") or {}).items():
                if _n in prev:
                    continue
                _v = _e.get("views") if isinstance(_e, dict) else None
                if _v:
                    prev[_n] = _e
        except Exception:
            pass
    for name, e in reads.items():
        if "views" not in e or not e["views"]: continue
        p = prev.get(name, {})
        pv = p.get("views") or {}
        for k, v in e["views"].items():
            if v is None: continue
            if k in pv and pv[k] is not None and pv[k] != v:
                changes.append(f"{name}.{k}: {pv[k]} -> {v}")
            elif k not in pv or pv.get(k) is None:
                changes.append(f"{name}.{k}: (new read) {v}")
except Exception as ex:
    changes = [f"compare-error: {ex}"]
out["leg4_retry_changes"] = changes
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-{TAG}-followup.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
