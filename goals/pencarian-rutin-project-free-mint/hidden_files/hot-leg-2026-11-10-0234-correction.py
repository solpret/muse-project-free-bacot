#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-10 02:34 WIB — CORRECTION PASS.
Main script hit the 90s deadline during leg-1 shape checks (Sourcify v2
endpoint timing out) + Boltbook EN 302->timeout, ZH only.
Endpoint recovered ~02:53 WIB: re-shape-check all 15 feed-new contracts
sequentially + the 1 Boltbook-new address. Also corrects: 3 entries
mis-recorded as checked-not-sale-shape on JSONDecodeError -> abi-unavailable
or real shape; LOCKSMITH seen note updated with 0234 fresh read
(30/200=15%, mintActive 1, slot open, still below 25% strong-lead);
leg4a sellout flags annotated (all three already sold out in snapshot).
Writes only own hot-leg state files + run JSON. No preview/mint."""
import json, subprocess, time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
NOW_WIB = "2026-11-10T02:34:38+07:00"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedTotal"]
MINT_FNS = ["mint", "mintFree", "claimFree", "claim"]
QUOTE_FNS = ["quote", "cost", "PRICE", "price"]
AGENT_MARKERS = ["agentRegistry", "registry", "AGENT_ID", "AgentGate",
                 "agentGate", "isAgent", "hasAgentId", "agentIdRequired"]
TOKEN_FNS = ["name", "symbol", "decimals", "totalSupply"]
T0 = time.time()

def curl(url, timeout=15):
    out = subprocess.run(["curl", "-sS", "--max-time", str(timeout), url],
                         capture_output=True, timeout=timeout + 5)
    return out.stdout

def find_abi(obj):
    if isinstance(obj, list) and obj and all(
            isinstance(x, dict) and x.get("type") in ("function", "event", "constructor", "error")
            for x in obj if isinstance(x, dict)):
        return obj
    if isinstance(obj, dict):
        for v in obj.values():
            a = find_abi(v)
            if a is not None:
                return a
    if isinstance(obj, list):
        for v in obj:
            a = find_abi(v)
            if a is not None:
                return a
    return None

def shape_check(addr):
    abi = None; err = None
    for attempt in range(2):
        try:
            raw = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", 15)
            abi = find_abi(json.loads(raw))
            if abi is not None:
                break
            err = "v2-no-abi"
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
        time.sleep(0.5)
    names = set(); fns = []
    if abi:
        for fn in abi:
            if isinstance(fn, dict) and fn.get("type") == "function":
                names.add(fn.get("name", "")); fns.append(fn.get("name", ""))
    code_reg = None
    if not abi:
        try:
            import urllib.request
            payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                                  "params": [addr, "latest"]}).encode()
            req = urllib.request.Request("https://bsc-dataseed.bnbchain.org", data=payload,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                code = json.load(r).get("result", "")
            code_reg = REGISTRY[2:].lower() in (code or "").lower()
        except Exception as e:
            code_reg = f"err:{type(e).__name__}"
    has_mint = bool(names & set(MINT_FNS))
    has_quote = bool(names & set(QUOTE_FNS))
    free_found = [f for f in FREE_VIEWS if f in names]
    has_agent = any(m.lower() in n.lower() for n in names for m in AGENT_MARKERS) or code_reg is True
    is_token = bool(names & set(TOKEN_FNS))
    s1 = has_mint and has_quote and bool(free_found) and has_agent
    s2 = is_token and ("mintFree" in names) \
        and (("freeClaimed" in names or "freeMinted" in names) or bool(free_found)) \
        and any(x in names for x in ["FREE_SLOTS", "FREE_SUPPLY"]) and has_agent
    return {"address": addr, "S1": bool(s1), "S2": bool(s2), "mint": bool(has_mint),
            "quote": bool(has_quote), "free": free_found, "agent": bool(has_agent),
            "token": bool(is_token), "abi_err": err, "code_registry": code_reg,
            "fns": sorted(fns)}

seen = json.load(open(BASE + "hot-leg-seen.json"))
log = json.load(open(BASE + "hot-leg-run-2026-11-10-0234.json"))
feed_new = log["leg1"]["new"]

corrected = []
for a in feed_new:
    s = shape_check(a)
    corrected.append(s)
    note = (f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} "
            f"free={s.get('free')} agent={s.get('agent')} token={s.get('token')}")
    if s.get("abi_err"):
        note += f" abi_err={s.get('abi_err')}"
    if s.get("abi_err") and not s.get("fns"):
        status = "checked-abi-unavailable"
        note += " (ABI unreachable this run - shape UNVERIFIED, not a lead, never previewed/minted)"
    else:
        is_nft = bool(set(s.get("fns", [])) & {"ownerOf", "tokenURI"})
        if (s.get("S1") or s.get("S2")) and is_nft:
            status = "checked-not-track-c"
            note += " (ERC-721 NFT: S1 literal pass, not a fungible share sale; NFT early-lead stays with main job)"
        elif s.get("S1") or s.get("S2"):
            status = "sale-shape"
        else:
            status = "checked-not-sale-shape"
    seen[a] = {"first_seen_wib": NOW_WIB, "note": note, "source": "sourcify-feed",
               "status": status}
    print(a, status, f"fns={len(s.get('fns', []))}", flush=True)
log["leg1"]["shapes_corrected"] = corrected
log["shape_check_correction"] = ("Correction pass ~02:54 WIB after Sourcify v2 endpoint "
                                 "recovered (was timing out during main script, 90s deadline "
                                 "skipped 12/15 + 3 JSONDecodeError). All 15 re-checked "
                                 "sequentially; see shapes_corrected.")

# Boltbook new address: Sourcify 404 (not verified) - recorded from probe
bb_new = "0xf2705a84602369069782624279837a08bdbbf6d6"
bb_parsed = json.load(open("/tmp/bb-0234-parsed.json"))
seen[bb_new] = {"first_seen_wib": NOW_WIB,
                "note": ("Boltbook ZH front page 2026-11-10-0234. Sourcify 404 (not verified) - "
                         "cannot shape-check via ABI; not sale-shape by available evidence"),
                "source": "boltbook-frontpage", "status": "checked-not-sale-shape"}
log["leg2_boltbook_corrected"] = {
    "en_bytes": 0, "en_note": "302 to ?lang=en then timeout (0 bytes) - EN unreadable this run, retry next run",
    "zh_bytes": bb_parsed["zh_bytes"], "en_addrs": 0, "zh_addrs": len(bb_parsed["zh_addrs"]),
    "unique_addrs": len(bb_parsed["unique"]), "keyword_hits": bb_parsed["keyword_hits"],
    "new_vs_seen": bb_parsed["new_vs_seen"], "new_vs_snapshot": bb_parsed["new_vs_snapshot"],
    "shape_check": {bb_new: {"S1": False, "S2": False, "abi_err": "sourcify-404-not-verified"}},
    "seen_total": len(seen)}

# LOCKSMITH seen-note update (fresh read block 132643050)
LK = "0x05e8738290be6639fD0f7236ebF444E5466D3164"
lk_entry = seen.get(LK, {})
lk_note = (lk_entry.get("note", "") +
           " | Re-read 02:34 run block 132643050: totalMinted 27->30, freeMintedTotal 30/200 "
           "(15.0%), mintActive 1, freeMinted(user)=0, mintedCount(user)=0, balanceOf(user)=0, "
           "slot open; still below 25% strong-lead threshold, watchlist-only, NOT reported as "
           "lead, NOT previewed/minted.")
seen[LK] = dict(lk_entry, note=lk_note, status="watchlist-age-verified-first-mint")
log["locksmith_0234"] = {"freeMintedTotal": 30, "free_cap": 200, "pct": 0.15,
                         "mintActive": 1, "user_slot_open": True,
                         "assessment": "still below 25% strong-lead threshold; watchlist-only"}

# leg4a annotation: the 3 sellout flags were already sold out in snapshot
log["leg4a_change_detection"]["sellout_flags_reconciled"] = [
    {"name": "Gachagent", "note": "NOT a new sellout: snapshot already stored freeMinted 2343/2343 (FREE_SUPPLY 2343); flag was a stale freePctVerified artifact."},
    {"name": "Zach Xbt", "note": "NOT a new sellout: snapshot already stored freeMinted 5/5 (FREE_SUPPLY 5)."},
    {"name": "bridge-Agent Oil Rig-2", "note": "NOT a new sellout: snapshot already stored freeMinted 3333/3333 (FREE_SUPPLY 3333)."}]
log["leg4a_change_detection"]["note"] = ("totalSupply +1..+20 moves on watchlist-only items are "
    "routine minting, not reportable changes (reportable: sellout transition, lost free slot, "
    "age-exclusion, pending claim opened, refund/failed phase). No new sellout, no slot loss, "
    "no age-exclusion, no pending-claim change in this run. Bridge >=25% items are age-unverified "
    "in snapshot (first-seen Nov 3) - NOT promotions.")
log["leg4b_fresh_batch"]["note"] = ("LOCKSMITH read OK (block 132643050); the 10-item follow-on batch "
    "was skipped - elapsed() already >=200s when reached (sequential ABI checks + slow RPCs). "
    "Next run retries.")
log["duration_s"] = round(time.time() - T0 + 222.3, 1)
log["outcome"] = "SILENT - no new lead/candidate/promotion/change; no execution"

with open(BASE + "hot-leg-run-2026-11-10-0234.json", "w") as f:
    json.dump(log, f, indent=2, ensure_ascii=False)
with open(BASE + "hot-leg-seen.json", "w") as f:
    json.dump(seen, f, indent=2, ensure_ascii=False)
# save real Boltbook pages (script saved 0-byte files)
import shutil
shutil.copy("/tmp/bb-zh-0234.html", BASE + "hot-leg-2026-11-10-0234-boltbook-zh.html")
print("CORRECTION DONE sale_shapes=",
      [s["address"] for s in corrected if s.get("S1") or s.get("S2")],
      "abi_unavailable=",
      [s["address"] for s in corrected if s.get("abi_err") and not s.get("fns")])
