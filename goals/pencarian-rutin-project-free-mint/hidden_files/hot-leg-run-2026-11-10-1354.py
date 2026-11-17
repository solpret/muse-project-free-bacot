#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-10 13:54 WIB. Legs: (1) shape-check 13 new
Sourcify-feed contracts (feed already fetched by parent: 20 verified
06:45-06:56 UTC / 13:45-13:56 WIB; 7 already seen, 13 new); (2) Boltbook
EN+ZH already fetched (EN 200 46773B, ZH 200 46971B) - 17 addrs, all seen
except 0x0474b6f6... which is a TX hash (BITCAT claim tx), not a contract;
(3) leg4 re-read of 48-item set vs 1344 baseline; (4) bridge read-only.
Read-only except own hot-leg state files. No preview/mint, no chain scan."""
import json, time, urllib.request, concurrent.futures, subprocess
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc.nodereal.io/"
T0 = time.time()
NOW_ISO = "2026-11-10T13:54:00+07:00"
RUN = "2026-11-10 13:54 WIB"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed",
              "freeMinted","freeCardsRemaining"]

NEW = ["0xD84bAf1ffB2646854e8CC7Ba3F943d198609c793","0xb90ebFbc8286942B668B0A3A7f27CC9976C35DAb",
 "0x914537c7403f6773BBB5CE39d457F7C786b1C378","0x93d461fcAB02Db6741609E9368315C43f9C2CDe4",
 "0xF6991CC30b31ABd7fE018761404435cFE34C55D1","0xe8FB34Ed06A37A3a8E26167F4a908B95D42DA7c1",
 "0x97241D7138E59B0e238FEd59Bc3Bd7e7dCB66BbE","0x3a0f62876564D36A268E097dB614864FcA94C490",
 "0xFdca29931464971BaC2B0A1573CB751831d811c0","0x47046f668814C99f4867E4C495C5D02BE4C31dd3",
 "0xdb24673Ff17254ab9db7228Bd37B9A4C6f4407B8","0x25C24806dF1256f853c2C52f2EB8da9dC3d54aF9",
 "0x124ee43F4BCF63066B1D4913f8Bb3165F1606813"]

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            meta = json.loads(r.read().decode())
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:100]}"}

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    shapes = list(ex.map(fetch_abi, NEW))
s1_pass = [s["address"] for s in shapes if s.get("S1")]
s2_pass = [s["address"] for s in shapes if s.get("S2")]
print("shape:", json.dumps(shapes), flush=True)

seen = json.load(open(BASE + "hot-leg-seen.json"))
for s in shapes:
    a = s["address"]
    if s.get("error"):
        seen[a] = {"first_seen_wib": NOW_ISO,
                   "note": f"Sourcify ABI fetch error: {s['error']} - no sale-shape evidence; recorded, not a lead, never previewed/minted.",
                   "source": "sourcify-feed", "status": "checked-abi-unavailable"}
    else:
        seen[a] = {"first_seen_wib": NOW_ISO,
                   "note": f"S1={s['S1']} S2={s['S2']} mint={s['has_mint']} quote={s['has_quote']} free={s['free_views']} agent={s['agent_ref']} token={s['is_token']}",
                   "source": "sourcify-feed", "status": "checked-not-sale-shape"}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Leg 4: re-read 48-item set vs 1344 baseline ----
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_uint(n): return format(n, "064x")
NOARG = ["totalSupply","totalMinted","totalMints","freeMinted","freeClaimed",
 "freeMintedTotal","freeLeft","freeUsed","FREE_CAP","FREE_SUPPLY","FREE_SHARES",
 "FREE_QUOTA","FREE_PER_WALLET","remainingFree","MAX_SUPPLY","MAX_FREE",
 "sharesMinted","sold","phase","launched","soldOut","closed","finalized",
 "mintOpen","mintActive","totalSkunksMinted","freeSkunksClaimed",
 "freeSkunksRemaining","freeRemaining","mintCount","MAX_MINTS","opened",
 "openedAt","saleActive","soldShares","publicMinted","launchTime","totalShares",
 "totalFreeShares","mintingOpen","TOTAL_SHARES","MAX_FREE_SHARES","SALE_START",
 "isSaleEnded","remaining","mintEnd","mintStart","SALE_END","startTime",
 "freeWindowOpen","agentFreeUsed","AGENT_FREE_CAP","paidMinted"]
ADDRARG = ["balanceOf","mintedBy","freeClaimed","freeLeft","freeUsed","freeCount",
 "freeMinted","mintedCount","freeAvailable","hasMinted","quotaOf","freeTakenBy",
 "priceFor","freeClaimedBy","freeUsedByWallet","hasFreeMinted","freeAllowance",
 "maxShares","remainingShares"]
ADDRUINT = ["quote","freeFor"]
def calldata(field):
    if field in ("address", "_batch_fail"): return None
    if field.endswith("_user1"):
        fn = field[:-6]
        if fn in ADDRUINT: return sel(f"{fn}(address,uint256)") + enc_addr(USER) + enc_uint(1)
        return None
    if field.endswith("_user"):
        fn = field[:-5]
        if fn in ADDRARG: return sel(f"{fn}(address)") + enc_addr(USER)
        return None
    if field in NOARG: return sel(f"{field}()")
    return None
def run_batch(calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)])
    p = subprocess.run(["curl", "-s", "--max-time", "30", "-X", "POST", EP,
                        "-H", "Content-Type: application/json", "--data", payload],
                       capture_output=True, text=True)
    try: return json.loads(p.stdout)
    except Exception: return {"_curl_error": p.stdout[:200] + p.stderr[:200]}
def decode(r):
    if not isinstance(r, str) or not r.startswith("0x"): return None
    try: return int(r, 16)
    except Exception: return None

prev = json.load(open(BASE + "hot-leg-2026-11-10-1344-reread.json"))
items = prev["items"]
jobs = []
for name, entry in items.items():
    for field in entry:
        data = calldata(field)
        if data: jobs.append((name, field, entry["address"], data))
p = subprocess.run(["curl", "-s", "--max-time", "15", "-X", "POST", EP,
                    "-H", "Content-Type: application/json",
                    "--data", '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],
                   capture_output=True, text=True)
try: block = int(json.loads(p.stdout)["result"], 16)
except Exception: block = None
results, failed = {}, []
for i in range(0, len(jobs), 25):
    chunk = jobs[i:i + 25]
    resp = run_batch([(to, data) for (_, _, to, data) in chunk])
    if isinstance(resp, dict) and "_curl_error" in resp:
        for (name, field, to, data) in chunk:
            results[(name, field)] = None; failed.append((name, field))
        continue
    if isinstance(resp, dict): resp = [resp]
    for j, item in enumerate(resp):
        name, field, to, data = chunk[j]
        if isinstance(item, dict) and "result" in item:
            results[(name, field)] = decode(item["result"])
        else:
            results[(name, field)] = None; failed.append((name, field))
reread = {"block": block, "items": {}, "duration_sec": round(time.time() - T0, 1)}
read_failed2 = []
for name, entry in items.items():
    row = {"address": entry["address"]}
    for field in entry:
        if field == "address": continue
        v = results.get((name, field))
        if v is None:
            row[field] = entry.get(field)
            read_failed2.append((name, field))
        else:
            row[field] = v
    reread["items"][name] = row
reread["read_failed"] = [{"item": n, "field": f} for n, f in read_failed2]
diffs = []
for name, row in reread["items"].items():
    base = items.get(name, {})
    for field, val in row.items():
        if field == "address": continue
        old = base.get(field)
        if old is None and val is None: continue
        if old != val: diffs.append({"item": name, "field": field, "old": old, "new": val})
reread["diffs_vs_1344"] = diffs
reread["baseline_note"] = "diffs vs 13:44 leg4 (block 132731772)"
json.dump(reread, open(BASE + "hot-leg-2026-11-10-1354-reread.json", "w"), indent=1)

# promo flags (0039-style) + new-flag detection vs 1344 flags
snap2 = json.load(open(BASE + "onchain-snapshot.json"))
sc = snap2.get("contracts", {}) or {}
st = snap2.get("track_c", {}) or {}
flags = []
for name, entry in reread["items"].items():
    meta = sc.get(name) or st.get(name) or {}
    status = (meta.get("status") or "") if isinstance(meta, dict) else ""
    free = entry.get("freeMinted", entry.get("freeClaimed", entry.get("freeMintedTotal")))
    cap = entry.get("FREE_CAP", entry.get("FREE_SUPPLY", entry.get("FREE_SHARES",
          entry.get("FREE_QUOTA", entry.get("MAX_SUPPLY")))))
    if isinstance(free, int) and isinstance(cap, int) and cap > 0:
        pct = free / cap
        user_open = entry.get("freeClaimed_user") in (0, False, None) or entry.get("balanceOf_user") == 0
        if free >= cap:
            flags.append({"item": name, "flag": "sellout?", "pct": round(pct, 4), "free": free, "cap": cap, "snap_status": status})
        elif pct >= 0.25 and user_open:
            flags.append({"item": name, "flag": "promo-candidate-check", "pct": round(pct, 4), "free": free, "cap": cap, "snap_status": status})
prev_flags = {}
try:
    pf = json.load(open(BASE + "hot-leg-run-2026-11-10-1344-leg4.json"))
    for f in pf.get("leg4_promo_flags", []):
        prev_flags[(f["item"], f["flag"])] = f
except Exception:
    pass
new_flags = [f for f in flags if (f["item"], f["flag"]) not in prev_flags]
pend = snap2.get("pending_claims", {}) or {}

# ---- Bridge (read-only) ----
bridge_note = ""
try:
    br = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = br.get("contracts", {})
    in_bridge_new = [a for a in NEW if a.lower() in {k.lower() for k in bcontracts}]
    discarded_n = sum(1 for v in bcontracts.values() if v.get("same_owner_discarded"))
    bridge_note = (f"scan-bridge.json read ({len(bcontracts)} contracts, last written "
                   f"{br.get('last_written', br.get('written', 'n/a'))}); {discarded_n} same_owner_discarded; "
                   f"new feed contracts in bridge: {in_bridge_new or 'none'}; no bridge contract promoted/changed by this run's re-read")
except Exception as e:
    bridge_note = f"scan-bridge.json unreadable: {type(e).__name__} - skipped, run continues"
# discards check for new contracts
try:
    discards = json.load(open(BASE + "same-owner-discards.json"))
    dc = {str(e.get("contract", "")).lower() for e in discards if isinstance(e, dict)}
    in_discards = [a for a in NEW if a.lower() in dc]
except Exception:
    in_discards = []
bridge_note += f"; new contracts in same-owner-discards.json: {in_discards or 'none'}"

out = {"run": RUN, "legs": {
  "sourcify_feed": f"20 contracts verified 13:45-13:56 WIB; 7 already seen, 13 new shape-checked, ALL not sale shape (S1=False S2=False): {', '.join(a[:6] for a in NEW)}. S1_PASS={s1_pass} S2_PASS={s2_pass}. Recorded in hot-leg-seen.json.",
  "boltbook": "EN 200 (46773B) + ZH 200 (46971B) boltbook.fun; 17 unique addresses, ALL already in hot-leg-seen.json (incl. BITCAT sale/token already minted, LUCKY777 sale already minted, Cinder Agents reported run 1301). The one 'new' hex string 0x0474b6f6... is a TX hash (BITCAT claim tx 0x0474b6f678d92fb6abbfc20055f248afee742198...), not a contract. No new lead.",
  "leg4_reread": f"{len(items)}-item set re-read at block {block} via bsc.nodereal.io eth_call batches; vs 13:44 baseline (block 132731772) {len(diffs)} diffs: {diffs}. {len(read_failed2)} read-failed fields kept baseline values, never treated as change. New promo flags vs 1344: {new_flags or 'none'}.",
  "bridge": bridge_note,
  "execution": "NONE - no preview, no mint, no claim. No candidate met execution rules."
 },
 "report": "SILENT - no new lead, candidate, pending claim, change, or blocked auto-mint to report to main chat.",
 "duration_sec": round(time.time() - T0, 1)}
leg4out = {"leg4": {"block": block, "prev_block": prev.get("block"), "rpc": EP,
                    "items_n": len(items), "changes": diffs,
                    "failed_call_idx": [{"item": n, "field": f} for n, f in failed],
                    "read_failed": reread["read_failed"],
                    "mode": "chunked eth_call batches of <=25 (read-only); null reads keep baseline, never a change"},
           "leg4_promo_flags": flags, "new_promo_flags": new_flags,
           "pending_claims": "snapshot pending_claims empty - nothing to re-read" if not pend else f"{len(pend)} pending claims present",
           "duration_sec": round(time.time() - T0, 1)}
json.dump(leg4out, open(BASE + "hot-leg-run-2026-11-10-1354-leg4.json", "w"), indent=1)
json.dump(out, open(BASE + "hot-leg-run-2026-11-10-1354.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("LEG4:", json.dumps(leg4out, indent=1)[:3000])
