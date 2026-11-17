#!/usr/bin/env python3
"""Hot-leg run 2026-11-15 18:44 WIB. Legs (1) Sourcify feed, (2) Boltbook en+zh,
(3) shape-check new contracts S1/S2 + retry shape-check-failed first-seen today,
(4) re-read of the 36 items from run-hot-leg-2026-11-15-1839-reread.json
(block 133722243) vs that baseline, (5) bridge read-only.
Read-only except hot-leg-seen.json (own file) + this run's outputs.
No preview/mint."""
import json, re, time, subprocess
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = "2026-11-15T18:44+07:00"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124",
            "0x8b47354E7b76B1970a0D06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
t0 = time.time()

def get(url, timeout=20):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout),
                        "-A", "hot-leg/1.0", url],
                       capture_output=True, text=True, timeout=timeout + 10)
    if r.returncode != 0:
        raise RuntimeError(f"curl rc={r.returncode}: {r.stderr[:120]}")
    return r.stdout

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower(): v for k, v in seen.items()}

# (1) Sourcify feed
feed = json.loads(get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"))
results = feed.get("results", [])
feed_addrs = [r["address"] for r in results]
feed_new = [a for a in feed_addrs if a.lower() not in seen_l and a not in EXCLUDED
            and a.lower() != REG.lower()]

# (2) Boltbook en + zh (retry once on failure)
def boltbook(lang_url):
    for attempt in range(2):
        try:
            html = get(lang_url)
            addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
            return len(html), addrs, attempt, None
        except Exception as ex:
            err = f"{type(ex).__name__}: {str(ex)[:100]}"
            if attempt == 1:
                return 0, [], err, err
            time.sleep(2)
en_bytes, en_addrs, en_att, en_err = boltbook("https://boltbook.fun/")
zh_bytes, zh_addrs, zh_att, zh_err = boltbook("https://boltbook.fun/?lang=zh")
bb_addrs = sorted(set(en_addrs) | set(zh_addrs))
bb_new = [a for a in bb_addrs if a.lower() not in seen_l and a not in EXCLUDED]

# (3) shape-check new contracts + retry shape-check-failed first-seen today
def shape(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        meta = json.loads(get(url, timeout=15))
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId",
                                  "agentGate", "AgentGate"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = (is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"})
              and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref)
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
                "is_token": is_token, "n_fns": len(names), "status": "checked",
                "verifiedAt": next((r.get("verifiedAt") for r in results
                                    if r["address"].lower() == addr.lower()), None)}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}",
                "verifiedAt": None}

retry = []
for k, v in seen.items():
    if isinstance(v, dict) and v.get("status") == "shape-check-failed":
        fsw = v.get("first_seen_wib", "")
        if fsw.startswith("2026-11-15"):
            retry.append(k)
import concurrent.futures
targets = feed_new + [a for a in bb_new if a.lower() not in {x.lower() for x in feed_new}]
retry_targets = [a for a in retry if a.lower() not in {x.lower() for x in targets}]
all_targets = targets + retry_targets
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    shape_out = list(ex.map(shape, all_targets))

# (4) re-read vs 1754 baseline - deferred to reread script
NOARG = {"totalSupply", "totalMinted", "freeMinted", "freeClaimed", "FREE_SUPPLY",
         "FREE_CAP", "FREE_MAX", "FREE_MINT_CAP", "MAX_SUPPLY", "maxSupply", "mintOpen",
         "launched", "failed", "isRefundPhase", "totalShares", "remainingSupply",
         "standardRemaining", "legendaryRemaining", "paused", "TOKEN_PRICE", "claimOpen",
         "mintStartTime", "AGENT_ID", "freeSharesLeft", "openedAt", "freeBlock",
         "mintOpenTimestamp", "mintPaused", "price", "PRICE", "mintPrice", "paidMinted",
         "totalSpecimens", "currentExperiment", "genesisStart", "genesisOpen",
         "mintsLeft", "freeMintsLeft", "freeRemaining", "owner", "freeCount",
         "freeMintsLeft"}
ADDRARG = {"balanceOf", "freeClaimedOf", "freeUsed", "mintedBy", "mintedByWallet",
           "freeMintedPerWallet", "mintedPerWallet", "mintCountOf", "mintsBy",
           "holdsAgentId", "hasAgentId", "isEligible", "tokenClaimed", "freeBooked",
           "hasFreeClaimed", "priceFor", "freeClaimed"}
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

base = json.load(open(BASE + "run-hot-leg-2026-11-15-1839-reread.json"))
base_reads = base["reads"]
calls = []
for name, it in base_reads.items():
    if not it or it.get("views") is None:
        continue
    addr = it["address"]
    for vn, bv in it["views"].items():
        if bv is None:
            continue
        if vn.startswith("freeClaimedByAgent"):
            continue
        if vn == "priceFor_user_1":
            calls.append((name, vn, sel("priceFor(address,uint256)") + enc_addr(USER) + enc_u(1)))
        elif vn.endswith("_user"):
            fn = vn[:-5]
            if fn in ADDRARG:
                calls.append((name, vn, sel(f"{fn}(address)") + enc_addr(USER)))
        elif vn in NOARG:
            calls.append((name, vn, sel(f"{vn}()")))

leg4_out = {"reads": {}, "block": None, "error": "deferred to reread script", "n_calls": 0}
diffs = {}

# (5) bridge (read-only)
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    b_contracts = bridge.get("contracts", bridge) if isinstance(bridge, dict) else bridge
    if isinstance(b_contracts, dict):
        b_list = list(b_contracts.keys())
        b_disc = sum(1 for v in b_contracts.values()
                     if isinstance(v, dict) and v.get("same_owner_discarded"))
    else:
        b_list, b_disc = b_contracts, 0
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for coll in ("contracts", "track_c", "pending_claims"):
        c = snap.get(coll, {})
        if isinstance(c, dict):
            snap_addrs |= {k.lower() for k in c.keys()}
            snap_addrs |= {(v.get("address") or "").lower() for v in c.values()
                           if isinstance(v, dict)}
        elif isinstance(c, list):
            snap_addrs |= {x.get("address", "").lower() for x in c if isinstance(x, dict)}
    not_in_snap = [a for a in b_list if a.lower() not in snap_addrs]
    bridge_out = {"contracts": len(b_list), "same_owner_discarded": b_disc,
                  "not_in_snapshot": len(not_in_snap),
                  "not_in_snapshot_list": not_in_snap}
except Exception as ex:
    bridge_out = {"error": f"{type(ex).__name__}: {str(ex)[:120]}"}

# update seen (own file only): new targets recorded; retry failures stay shape-check-failed
added = []
for o in shape_out:
    a = o["address"]
    if a.lower() in seen_l:
        if o.get("status") == "checked":
            seen[a]["status"] = "checked"
            seen[a]["note"] = (f"S1={o['S1']} S2={o['S2']} mint={o['has_mint']} "
                               f"quote={o['has_quote']} free={o['free_views']} agent={o['agent_ref']}")
    else:
        if o.get("status") == "checked":
            seen[a] = {"first_seen_wib": NOW,
                       "note": (f"S1={o['S1']} S2={o['S2']} mint={o['has_mint']} "
                                f"quote={o['has_quote']} free={o['free_views']} agent={o['agent_ref']}"),
                       "source": "hot-leg-1844", "status": "checked"}
        else:
            seen[a] = {"first_seen_wib": NOW, "note": o.get("error", ""),
                       "source": "hot-leg-1844", "status": "shape-check-failed"}
        added.append(a)
if added:
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"))

out = {"run": "free-mint-hot-leg 2026-11-15T18:44+07:00", "started_wib": NOW,
       "sourcify_feed": {"total": len(results), "new": len(feed_new),
                         "new_contracts": feed_new,
                         "top": feed_addrs[0] if feed_addrs else None,
                         "top_verifiedAt": results[0].get("verifiedAt") if results else None},
       "boltbook_en": {"bytes": en_bytes, "full_address_contracts": len(en_addrs),
                       "new": len(bb_new), "attempts": en_att, "error": en_err},
       "boltbook_zh": {"bytes": zh_bytes, "full_address_contracts": len(zh_addrs),
                       "new": len(bb_new), "attempts": zh_att, "error": zh_err},
       "shape_check_targets": all_targets, "n_new_targets": len(targets),
       "n_retry_targets": len(retry_targets),
       "shape_check": shape_out,
       "shape_hits": [o["address"] for o in shape_out if o.get("S1") or o.get("S2")],
       "leg4_reread": leg4_out, "leg4_base_block": base.get("block"),
       "leg4_diffs_vs_1839": diffs,
       "bridge": bridge_out,
       "seen_added": added, "seen_n": len(seen),
       "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "run-hot-leg-2026-11-15-1844.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in
                  ("sourcify_feed", "boltbook_en", "boltbook_zh", "shape_hits",
                   "leg4_diffs_vs_1839", "bridge", "seen_added", "seen_n", "elapsed_s")}, indent=1))
print("LEG4 block:", leg4_out.get("block"), "error:", leg4_out.get("error"),
      "n_calls:", leg4_out.get("n_calls"))
