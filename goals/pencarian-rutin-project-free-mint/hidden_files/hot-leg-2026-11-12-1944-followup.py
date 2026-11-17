#!/usr/bin/env python3
"""Hot-leg run 2026-11-12 19:44 WIB — follow-up: (a) deep read NEW sale-shape
0x5314071bba19943f58347bA5deC423E5032A6818 (ERC-721, S1+S2 pass, verified 19:41:30 WIB)
— uint views + name/symbol/contractURI strings + quote(user,1); (b) retry 26 null
leg4 reads; (c) first-mint log probe for 0x5314 if launched. Raced batches, hard
deadline T0+170s. Read-only; writes only own file. Baseline compare uses
first-wins newest-first merge (fixes inverted merge in main run)."""
import json, time, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-12-1944"
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
NEW = "0x5314071bba19943f58347bA5deC423E5032A6818"
out = {"run": "free-mint-hot-leg 2026-11-12 19:44 WIB follow-up", "started_wib": now_wib}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def dec_str(h):
    try:
        b = bytes.fromhex(h[2:])
        if len(b) < 96: return None
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off + 32], "big")
        return b[off + 32:off + 32 + ln].decode(errors="replace")
    except Exception:
        return None
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
def raw_hex(addr, sig):
    res = post_rpc_race([{"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": addr, "data": sel(sig)}, "latest"]}], timeout=12)
    if isinstance(res, list) and res and isinstance(res[0], dict) and "result" in res[0]:
        return res[0]["result"]
    return None

NEW_UINT = ["totalSupply()", "totalMinted()", "freeMinted()", "FREE_SUPPLY()", "FREE_PER_WALLET()",
            "freeRemaining()", "isFreeOpen()", "mintOpen()", "saleOpen()", "saleStart()", "saleEnd()",
            "SALE_END()", "PRICE()", "price()", "cost()", "maxSupply()", "MAX_SUPPLY()", "paidMinted()",
            "paidSupply()", "remainingSupply()", "publicRemaining()", "FREE_MODE()", "MAX_PER_TX()",
            "MAX_PER_WALLET()", "PAID_PER_WALLET()", "raisedWei()", "settledWei()", "saleClosed()",
            "freeAvailable(address)", "freeMintedBy(address)", "mintedBy(address)",
            "balanceOf(address)", "hasAgentId(address)", "remainingQuota(address)",
            "paidAvailable(address)", "owner()"]
new_r = raw_batch(NEW, NEW_UINT) if time.time() < T0 + 40 else None
new_str = {}
for s in ("name()", "symbol()", "contractURI()"):
    if time.time() < T0 + 60:
        h = raw_hex(NEW, s)
        new_str[s.split("(")[0]] = dec_str(h) if h else None
# quote(user,1): quote(address,uint256) -> 5 words; first word = cost
quote_hex = None
if time.time() < T0 + 70:
    data = sel("quote(address,uint256)") + enc(USER) + format(1, "064x")
    res = post_rpc_race([{"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": NEW, "data": data}, "latest"]}], timeout=12)
    if isinstance(res, list) and res and isinstance(res[0], dict) and res[0].get("result"):
        quote_hex = res[0]["result"]
quote_words = None
if quote_hex:
    try:
        b = bytes.fromhex(quote_hex[2:])
        quote_words = [int.from_bytes(b[i:i + 32], "big") for i in range(0, min(len(b), 160), 32)]
    except Exception:
        quote_words = None
out["new_contract"] = {"address": NEW, "views": new_r,
                       "summary": {k: v for k, v in new_r.items() if v is not None} if new_r else None,
                       "strings": new_str, "quote_user_1_words": quote_words}
if new_r:
    try:
        seen = json.load(open(BASE + "hot-leg-seen.json"))
        if isinstance(seen.get(NEW), dict):
            ssum = out["new_contract"]["summary"] or {}
            seen[NEW]["note"] = (seen[NEW].get("note", "") +
                f" | FOLLOWUP {now_wib}: " + ", ".join(f"{k}={v}" for k, v in ssum.items())[:300] +
                f" | name={new_str.get('name')} sym={new_str.get('symbol')} contractURI={str(new_str.get('contractURI'))[:120]} quote1={quote_words}").strip()[:900]
            json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
    except Exception as e:
        out["new_contract"]["seen_write_error"] = str(e)[:100]

# ---- Leg4 null retries ----
VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
         "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)", "freeClaimed(address)",
         "freeUsed(address)", "mintedBy(address)", "freeMintedBy(address)", "mintStart()",
         "freeLeft()", "freeAvailable(address)", "saleStart()", "saleEnd()", "PRICE()",
         "price()", "launched()", "freeSharesLeft()", "openedAt()", "freeSharesRemaining()",
         "freeClaimedByWallet(address)", "currentState()", "finalized()", "refunding()",
         "totalFreeMinted()", "FREE_SHARES()", "freeLeftFor(address)"]
TARGETS = [
    ("RAMRAIDERS", "0x98dcfdeb5e015bbb3c9aca2a90ba0ee80e35315b"),
    ("Pathwyrm", "0xf100c608913dc07ed268bea865fca10004f04657"),
    ("BinanceLife", "0x4367b86F889014e6fD57fE812B86A581b913C645"),
    ("BUCKET", "0x2b0d3b384C341020aed1d49907b5708C423bA6DA"),
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
    ("NAPPER", "0x3964BFc3354C0d18886dcAD52Abc55C689e6A1d4"),
    ("WFPASS", "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C"),
    ("SEVEN", "0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96"),
    ("Airdrop-417d", "0x417d04C0a323fC89cDBbEf4D361161fCfA45baF9"),
    ("LuckyCatch", "0xD405C90079c594DA2456F5b37B4158A12f1382e5"),
    ("Pickgrid", "0x7f541bcc33abed0e64455565da723e949c6f76f0"),
]
reads = {}
for name, addr in TARGETS:
    if time.time() > T0 + 150:
        reads[name] = {"address": addr, "error": "deadline-hit-skipped"}; continue
    r = raw_batch(addr, VIEWS)
    reads[name] = {"address": addr, "views": r}
    if r: reads[name]["summary"] = {k: v for k, v in r.items() if v is not None}
out["leg4_retry"] = reads

# ---- First-mint log probe for NEW contract (only if launched: freeMinted>0 or isFreeOpen) ----
out["first_mint_probe"] = None
try:
    fm = (new_r or {}).get("freeMinted")
    if fm is not None and fm > 0 and time.time() < T0 + 165:
        # Transfer topic; from zero address; narrow range around verification (block ~133162000)
        payload = [{"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                    "params": [{"fromBlock": "0x7ef3f00", "toBlock": "latest", "address": NEW,
                                "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                                           "0x0000000000000000000000000000000000000000000000000000000000000000"]}]}]
        res = post_rpc_race(payload, timeout=15)
        logs = res[0].get("result") if isinstance(res, list) and res and isinstance(res[0], dict) else None
        if isinstance(logs, list) and logs:
            first = logs[0]
            out["first_mint_probe"] = {"n_logs": len(logs), "first_block": int(first.get("blockNumber", "0x0"), 16),
                                       "first_tx": first.get("transactionHash")}
        elif isinstance(logs, list):
            out["first_mint_probe"] = {"n_logs": 0, "note": "no Transfer-from-zero in range 0x7ef3f00..latest"}
        else:
            out["first_mint_probe"] = {"error": "getLogs unreadable", "raw": str(res)[:200]}
except Exception as e:
    out["first_mint_probe"] = {"error": str(e)[:150]}

# ---- Compare (first-wins newest-first) vs 1944 main + 1939 follow-up/main ----
changes = []
try:
    prev = {}
    for f in ("run-2026-11-12-1944-verify2.json",
              "hot-leg-2026-11-12-1939-followup.json", "run-2026-11-12-1939-verify2.json",
              "hot-leg-run-2026-11-12-1939.json",
              "hot-leg-2026-11-12-1929-followup.json", "run-2026-11-12-1929-verify2.json"):
        try:
            d = json.load(open(BASE + f))
            for nm, e in (d.get("leg4_reads") or d.get("reads") or d.get("leg4_retry") or {}).items():
                if nm not in prev:
                    prev[nm] = e
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
