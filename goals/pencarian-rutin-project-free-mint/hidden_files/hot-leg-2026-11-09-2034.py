#!/usr/bin/env python3
"""Hot-leg run 2026-11-09 20:34 WIB - legs 1/2 done by parent (feed+Boltbook),
JINMA track-C lead direct mint executed + verified, leg 4 re-read, bridge leg,
seen/reported bookkeeping. Adapted from hot-leg-2026-11-09-2029.py."""
import json, time, os, glob, subprocess, datetime
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-09-2034"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
WIB = datetime.timezone(datetime.timedelta(hours=7))

def wib_now():
    return datetime.datetime.now(WIB).isoformat(timespec="seconds")

seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
reported = json.load(open(f"{BASE}/hot-leg-reported.json"))

# ---- leg 1: 4 new Sourcify feed contracts, shape-checked via Sourcify v2 ABI ----
seen["0x8553e7033C06fC69B7508d58507b75242cF86EC4"] = {
    "first_seen_wib": wib_now(),
    "note": "JINMA sale (JinmaLaunch). S1 PASS: mint(uint256,address)+quote(address,uint256)->(freeCount,paidCount,cost)+freeSharesRemaining/freeSharesClaimed/publicFreeRemaining+AGENT_ID_REGISTRY()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (verified on-chain block 132594951). FREE_SHARES 2222, TOTAL 9999, PAID 7777, TOKENS_PER_SHARE 5e25, PRICE 0.002 BNB. Track-C LEAD, executed this run (see hot-leg-reported.json).",
    "source": "sourcify-feed+boltbook-en", "status": "track-c-lead-minted"}
seen["0xe4517E6718b24D5725956ac7A90686592a7b1539"] = {
    "first_seen_wib": wib_now(),
    "note": "JINMA token (金马/JINMA, ERC-20, dec 18). Plain token leg of JINMA sale 0x8553e7033C06fC69B7508d58507b75242cF86EC4; no mint/free/agent views - NOT a sale shape itself. Audit token hasResult=true riskLevel 2 LOW, 0 RISK hits (CAUTION only: Contract Code Not Verified - refuted by Sourcify exact_match - + Newly Created Token).",
    "source": "sourcify-feed+boltbook-en", "status": "checked-token-leg"}
seen["0x9d898fB21bA43b7e5185A7e081C1E7bB4dd399d9"] = {
    "first_seen_wib": wib_now(),
    "note": "JINMA deploy helper. fns caller/deploy/done only - NOT sale shape. Printed on jinma.pages.dev/llms.txt as deploy helper of sale 0x8553e7033C06fC69B7508d58507b75242cF86EC4.",
    "source": "sourcify-feed", "status": "checked-not-sale-shape"}
seen["0x254061D7Ee8512D3ed3Dd0aff7B31d9EaBdBCfC5"] = {
    "first_seen_wib": wib_now(),
    "note": "S1=False S2=False. Income/vault/leadership pool contract (claimLeadershipPool/claimVaultPool/vaultShares, priceManager) - no free view, no agent registry, no sale mint - not sale shape.",
    "source": "sourcify-feed", "status": "checked-not-sale-shape"}
out = {"run": "free-mint-hot-leg 2026-11-09 20:34:38 WIB",
       "started_wib": wib_now(),
       "leg1": {"feed_n": 20, "new": ["0x9d898fB21bA43b7e5185A7e081C1E7bB4dd399d9",
                                       "0x8553e7033C06fC69B7508d58507b75242cF86EC4",
                                       "0xe4517E6718b24D5725956ac7A90686592a7b1539",
                                       "0x254061D7Ee8512D3ed3Dd0aff7B31d9EaBdBCfC5"],
                "shapes": "JINMA sale S1 PASS; JINMA token = token leg; deployer + vault contract not sale shape",
                "seen_total": len(seen)}}
out["leg2_boltbook"] = {
    "note": "boltbook.fun EN via ?lang=en (47,861 B, 302->follow) + ZH (47,941 B), both HTTP 200. 10 unique addresses, 0 new vs seen. Keyword hits '1 free share'/'free share': NEW post raulzyan.ai /p/Ak2uA5PcLEmi (~20:37 WIB) = JINMA fair mint LIVE (sale 0x8553..., token 0xe451...); other hits MALTA 0x7280... / YAMA 0x86D7... / TIME CARDS 0xc562... (all already seen)."}
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)

# ---- JINMA reported entry (track-C lead direct mint, executed + verified) ----
reported["0x8553e7033C06fC69B7508d58507b75242cF86EC4"] = {
    "detail": "JINMA (金马/JINMA) track-C LEAD + DIRECT MINT executed under track-C lead direct mint rule. Sale 0x8553e7033C06fC69B7508d58507b75242cF86EC4, token 0xe4517E6718b24D5725956ac7A90686592a7b1539. S1 shape pass (mint+quote+free views+registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F). Website gate VERIFIED: jinma.pages.dev/llms.txt + homepage (HTTP 200) print exact sale+token+deployer. Age verified <=48h: first public mint ~20:35-20:37 WIB (Boltbook post raulzyan.ai 20:37 WIB 'first public mint just landed'; Sourcify verifiedAt 20:32:42 WIB; on-chain 35 public mints by block 132594951). On-chain fresh pre-exec block 132595712: publicFreeRemaining 1065/1111, freeSharesClaimed(user)=false, hasAgentId(user)=true, quote(user,1)=(freeCount 1, paidCount 0, cost 0), launched=false, failed=false. Audit: token hasResult=true riskLevel 2 LOW, 0 RISK hits (CAUTION only: Contract Code Not Verified - refuted by Sourcify exact_match - + Newly Created Token); sale hasResult=false (no result, disclosed, not a pass). Preview clean 000000000, value 0, no authority/allowance/risk, sim balance +5e25 JINMA. Mint mint(1, 0x0): tx 0x6a1896f26b61db371bce2dea1bcc115452b9c4ce73fd80fc0c8e41b27bccd0a4, receipt status 1, block 132595827, gasUsed 195418 (~0.0000144 BNB). Verified post-mint: freeSharesClaimed(user) true, sharesMinted(user) 1, JINMA balance 0 -> 50,000,000 (5e25), totalShares 1158 -> 1164, publicFreeRemaining 1065 -> 1058. Transfers locked until pool launch; no PCS pair yet -> registered in pending-swaps.json (50,000,000 JINMA delta) for auto-swap when pair opens. Marketplace/rarity checks N/A (fungible token, not NFT).",
    "reported_wib": wib_now(), "what": "minted",
    "sale": "0x8553e7033C06fC69B7508d58507b75242cF86EC4",
    "token": "0xe4517E6718b24D5725956ac7A90686592a7b1539",
    "tx": "0x6a1896f26b61db371bce2dea1bcc115452b9c4ce73fd80fc0c8e41b27bccd0a4",
    "block": 132595827, "gas": 195418}
json.dump(reported, open(f"{BASE}/hot-leg-reported.json", "w"), indent=1)
out["leg3_jinma"] = {"result": "track-C lead direct mint EXECUTED + VERIFIED on-chain (see reported entry)",
                     "tx": "0x6a1896f26b61db371bce2dea1bcc115452b9c4ce73fd80fc0c8e41b27bccd0a4"}

# ---- snapshot + bridge (read-only) ----
for _try in range(5):
    try:
        snap = json.load(open(f"{BASE}/onchain-snapshot.json")); break
    except Exception:
        snap = None; time.sleep(2)
if snap is None:
    raise SystemExit("snapshot unreadable after retries")
snap_addrs = set()
for sec in ("contracts", "track_c"):
    for v in snap.get(sec, {}).values():
        if isinstance(v, dict) and v.get("address"):
            snap_addrs.add(str(v["address"]).lower())
try:
    bridge = json.load(open(f"{BASE}/scan-bridge.json"))
    bcontracts = bridge.get("contracts", {})
    same_disc = sum(1 for v in bcontracts.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
    in_snap = sum(1 for k in bcontracts if k.lower() in snap_addrs)
    out["bridge_leg"] = {"total": len(bcontracts), "same_owner_discarded": same_disc,
                         "in_snapshot_addr": in_snap, "not_in_snapshot_addr": len(bcontracts) - in_snap,
                         "mtime": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(os.path.getmtime(f"{BASE}/scan-bridge.json"))),
                         "note": "Bridge read-only; promotions only if a bridge contract already in snapshot newly meets a tier or changes state."}
except Exception as e:
    out["bridge_leg"] = {"error": f"{type(e).__name__}: {e}", "note": "bridge skipped, run continues"}

# ---- leg 4: priority re-read (same mechanism as 2029 run) ----
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc.publicnode.com", "https://bsc-dataseed1.bnbchain.org/"]
def post_rpc(ep, payload, timeout=12):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)
def rpc_healthy():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=8)
            if r.get("result"): return ep, int(r["result"], 16)
        except Exception:
            continue
    return None, None
def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address,uint256)" in sig:
            data = sel(sig) + enc(USER) + format(1, "064x"); key = base + "_user1"
        elif "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=12)
            if not isinstance(res, list) or len(res) != len(calls): continue
            outd = {}
            for item, key in zip(res, keys):
                outd[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return outd
        except Exception:
            continue
    return None

FIELD_TO_SIG = {
    "freeMinted": "freeMinted()", "FREE_CAP": "FREE_CAP()", "freeCount_user": "freeCount(address)",
    "mintOpen": "mintOpen()", "balanceOf_user": "balanceOf(address)", "totalSupply": "totalSupply()",
    "FREE_SUPPLY": "FREE_SUPPLY()", "mintedBy_user": "mintedBy(address)", "FREE_SHARES": "FREE_SHARES()",
    "totalMinted": "totalMinted()", "finalized": "finalized()", "freeClaimed_user": "freeClaimed(address)",
    "freeClaimed": "freeClaimed()", "freeLeft": "freeLeft()", "remainingFree": "remainingFree()",
    "FREE_QUOTA": "FREE_QUOTA()", "freeUsed": "freeUsed()", "freeTakenBy_user": "freeTakenBy(address)",
    "MAX_SUPPLY": "MAX_SUPPLY()", "totalMints": "totalMints()", "mintActive": "mintActive()",
    "freeMintedTotal": "freeMintedTotal()", "quote_user1": "quote(address,uint256)",
    "freeLeft_user": "freeLeft(address)", "freeUsed_user": "freeUsed(address)",
    "freeFor_user1": "freeFor(address,uint256)", "priceFor_user": "priceFor(address)",
    "FREE_PER_WALLET": "FREE_PER_WALLET()", "mintedCount_user": "mintedCount(address)",
    "freeMinted_user": "freeMinted(address)", "phase": "phase()", "launched": "launched()",
    "sold": "sold()", "MAX_FREE": "MAX_FREE()", "sharesMinted": "sharesMinted()",
    "soldOut": "soldOut()", "closed": "closed()", "freeAvailable_user": "freeAvailable(address)",
    "hasMinted_user": "hasMinted(address)", "quotaOf_user": "quotaOf(address)",
}
def _load_prev():
    cands = sorted(glob.glob(f"{BASE}/hot-leg-*-reread.json"), reverse=True)
    for _f in cands:
        try:
            _d = json.load(open(_f))
        except Exception:
            continue
        if _d.get("FAILED"):
            continue
        _items = _d.get("items", {})
        if _d.get("block") is None and _items and all(v.get("_batch_fail") for v in _items.values()):
            continue
        out["leg4_diff_prev_file"] = _f.split("/")[-1]
        return _d
    out["leg4_diff_prev_file"] = None
    return {"items": {}, "block": None}
prev = _load_prev()
prev_items = prev.get("items", {})
prev_block = prev.get("block")

healthy_ep, block = rpc_healthy()
out["leg4_rpc"] = {"healthy_endpoint": healthy_ep, "block": block}
if healthy_ep is None:
    out["leg4_priority"] = "SKIPPED - RPC transport dead. No reread data; 'no changes' NOT established."
    out["leg4_changes"] = []
    out["leg4_promo_flags"] = []
else:
    items = {}
    def read_item(kv):
        name, prevd = kv
        addr = prevd["address"]
        views = [FIELD_TO_SIG[f] for f in prevd if f in FIELD_TO_SIG]
        got = raw_batch(addr, views)
        d = {"address": addr}
        if got is None:
            d["_batch_fail"] = True
            for f in prevd:
                if f != "address": d[f] = prevd[f]
        else:
            d.update(got)
        return name, d
    with ThreadPoolExecutor(max_workers=8) as ex:
        for name, d in ex.map(read_item, list(prev_items.items())):
            items[name] = d
    json.dump({"block": block, "items": items, "duration_sec": round(time.time() - T0, 1)},
              open(f"{BASE}/hot-leg-{TS}-reread.json", "w"), indent=1)
    out["leg4_priority"] = {"block": block, "prev_block": prev_block, "n_items": len(items), "duration_sec": round(time.time() - T0, 1)}
    changes = []
    for name, d in items.items():
        pd = prev_items.get(name)
        if not pd or d.get("_batch_fail"): continue
        for f, v in d.items():
            if f in ("address", "_batch_fail"): continue
            ov = pd.get(f)
            if v != ov and not (v is None and ov is None):
                changes.append({"item": name, "field": f, "old": ov, "new": v})
    out["leg4_changes"] = changes
    snap_contracts = snap.get("contracts", {})
    snap_status_by_addr = {}
    for _v in snap_contracts.values():
        if isinstance(_v, dict) and _v.get("address"):
            snap_status_by_addr[str(_v["address"]).lower()] = str(_v.get("status", ""))
    rep_addrs = {k.lower().split("#")[0] for k in reported}
    seen_by_low = {k.lower(): v for k, v in seen.items()}
    try:
        _disc = json.load(open(f"{BASE}/same-owner-discards.json"))
        same_owner_discards_lows = {str(e.get("contract", "")).lower() for e in _disc if isinstance(e, dict)}
    except Exception:
        same_owner_discards_lows = set()
    promo = []
    for name, d in items.items():
        if d.get("_batch_fail"): continue
        cap = d.get("FREE_SUPPLY") or d.get("FREE_CAP") or d.get("FREE_SHARES") or d.get("FREE_QUOTA") or d.get("MAX_FREE")
        claimed = d.get("freeClaimed") if d.get("freeClaimed") is not None else d.get("freeMinted")
        if cap and claimed is not None:
            pct = claimed / cap
            if pct >= 0.99:
                ent_status = snap_status_by_addr.get(d["address"].lower(), "")
                reason = "already-reported-in-snapshot" if "sold" in ent_status else "check-main-job"
                promo.append({"item": name, "address": d["address"], "pct": round(pct, 4),
                              "free": claimed, "cap": cap, "suppressed": True,
                              "reason": reason, "kind": "sellout-or-near"})
            elif pct >= 0.25:
                slot_open = ((d.get("freeLeft_user") or 0) > 0 or d.get("freeFor_user1") == 1
                             or d.get("quote_user1") == 0 or d.get("freeClaimed_user") == 0
                             or d.get("freeCount_user") == 0)
                minted_by_user = (d.get("balanceOf_user") or 0) > 0 or d.get("freeClaimed_user") == 1
                addr_low = d["address"].lower()
                seen_entry = seen_by_low.get(addr_low, {})
                seen_status = seen_entry.get("status", "") if isinstance(seen_entry, dict) else ""
                snap_status = snap_status_by_addr.get(addr_low, "")
                age_excluded = seen_status == "checked-not-lead-age-excluded"
                already_reported_snap = any(t in snap_status for t in ("strong-lead", "early-lead-reported", "gate-blocked", "candidate", "sold-out"))
                gate_blocked_reported = any(k.lower().startswith(addr_low + "#gate-blocked") for k in reported)
                discarded = addr_low in same_owner_discards_lows
                if pct >= 0.25 and slot_open and not minted_by_user and addr_low not in rep_addrs \
                        and not age_excluded and not already_reported_snap and not gate_blocked_reported and not discarded:
                    promo.append({"item": name, "address": d["address"], "pct": round(pct, 4),
                                  "free": claimed, "cap": cap, "kind": "strong-lead-promotion-candidate",
                                  "note": "needs age verification + website gate before any lead/preview"})
                elif pct >= 0.25 and slot_open and not minted_by_user:
                    promo.append({"item": name, "address": d["address"], "pct": round(pct, 4),
                                  "free": claimed, "cap": cap, "suppressed": True,
                                  "reason": ("same-owner-discarded" if discarded else
                                             "age-excluded" if age_excluded else
                                             "already-reported-in-snapshot" if already_reported_snap else
                                             "gate-blocked-already-reported" if gate_blocked_reported else
                                             "already-in-hot-leg-reported"),
                                  "kind": "strong-lead-promotion-candidate"})
    out["leg4_promo_flags"] = promo
out["pending_claims"] = snap.get("pending_claims") or "snapshot pending_claims empty at run start - nothing to re-read"
out["duration_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
print(json.dumps({"duration": out["duration_s"], "block": block,
                  "changes": out.get("leg4_changes"), "promo": out.get("leg4_promo_flags"),
                  "bridge": out.get("bridge_leg")}, indent=1))
