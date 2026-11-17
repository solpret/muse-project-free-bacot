#!/usr/bin/env python3
"""free-mint-hot-leg run 2026-11-10 02:54 WIB (scheduled 02:54:38 WIB).
Network-outage run: ALL outbound HTTPS timed out (Sourcify, Boltbook EN+ZH,
bsc-dataseed x2, Ankr RPC, google.com) - VM egress down at run time.
Per speed/failure rules: skip stalled legs, record skips, continue with
local-only legs (bridge, read-only). No shape checks, no RPC re-read, no
preview/mint. Writes only own run JSON. Retried legs next run, never
aggressively.
"""
import json, time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
T0 = time.time()
RUN = "free-mint-hot-leg 2026-11-10 02:54 WIB (scheduled 02:54:38 WIB)"
log = {"run": RUN}

# --- network probes (evidence, already attempted via shell before this script) ---
log["network_probes"] = {
    "sourcify_feed": "curl 15s timeout, 0 bytes",
    "boltbook_en": "curl 15s timeout, 0 bytes",
    "boltbook_zh": "curl 15s timeout, 0 bytes",
    "bsc_dataseed": "curl POST eth_blockNumber 10s timeout, 0 bytes",
    "ankr_rpc": "curl POST eth_blockNumber 8s timeout, 0 bytes",
    "google": "curl 8s timeout, 0 bytes",
    "bsc_dataseed1": "curl 8s timeout, 0 bytes",
    "verdict": "general egress outage (7 failed attempts, 5 distinct hosts incl. google.com) - NOT endpoint-specific",
}

# --- leg 1: Sourcify feed SKIPPED (network down) ---
log["leg1_feed"] = {"n": 0, "addrs": [], "error": "SKIPPED - Sourcify timeout (egress outage)", "verifiedAt_range": None}
log["leg1"] = {"new": [], "shapes": [], "note": "SKIPPED - no feed, no shape checks this run"}

# --- leg 2: Boltbook SKIPPED (network down) ---
log["leg2_boltbook"] = {"en_bytes": 0, "zh_bytes": 0,
                        "note": "SKIPPED - boltbook.fun EN+ZH both timeout (egress outage); retry next run"}

# --- leg 3: nothing to verify ---
log["leg3_new_sale_shapes"] = []
log["leg3_verify"] = "None - no new sale-shape contract (legs 1-2 skipped)"

# --- pending correction from 02:34 run (NOT executed; Sourcify down) ---
log["pending_correction_0234"] = {
    "script": "hot-leg-2026-11-10-0234-correction.py (written 02:55 WIB, never executed: run JSON + seen.json mtimes predate it, no shapes_corrected key)",
    "contracts_shape_unverified": 15,
    "feed_new_0234": ["0x2B18E242834E59512aca1E931438FA1685F3C5A2",
                      "0x974ff9dc210798e60d2430CCb6069DF3a66ae398",
                      "0xCf60fE48669B2D5ab7A60fD8C5F02104d7f4Ac16",
                      "0x1407c5E72dB514e50B9D162eF9Efff83Ba5E5348",
                      "0x48E4374f15CAc92A518E3E3D30B13dE0BC1cEA75",
                      "0xc4fC3150945875502cA2183bDE277813eEc8F096",
                      "0x651B49f4C14dAAf270274a6C682f0d65F27eF6CD",
                      "0x2403ba50cc25dc4A8Ff9D518452A33C8205836eA",
                      "0x95972735b5Ab59Cb5E82f057958A36E8BB9940Ef",
                      "0x404056Ab781D713B8f5Dc55F5B9592962B187099",
                      "0x34D8A2debE49DCCa0f7cC77d74163cFB94Cc19F5",
                      "0xB3f66517bEC4cC5A8E799dB2dDA4C810BefCc917",
                      "0xDBAD9E797157F76B2122c69C01BAC47541A3e62C",
                      "0x2E8B7e47424876B29fa2276025dE03F812813b03",
                      "0x7635Ef16370ef490298649A188c9205D1d7FDA67"],
    "boltbook_new_0234": "0xf2705a84602369069782624279837a08bdbbf6d6 (ZH front page 02:34, Sourcify 404 per /tmp/bb-0234-parsed.json)",
    "action": "retry correction next run when egress recovers; 15 contracts stay shape-UNVERIFIED (not leads, never previewed/minted)",
}

# --- bridge leg (read-only, local files) ---
bridge = json.load(open(BASE + "scan-bridge.json"))
snap = json.load(open(BASE + "onchain-snapshot.json"))
snap_addrs = set()
for sec in ("contracts", "track_c", "pending_claims"):
    for k, v in snap.get(sec, {}).items():
        if isinstance(k, str) and k.startswith("0x") and len(k) == 42:
            snap_addrs.add(k.lower())
        if isinstance(v, dict):
            for f in ("address", "sale", "token"):
                a = v.get(f)
                if isinstance(a, str) and a.startswith("0x"):
                    snap_addrs.add(a.lower())
bcontracts = bridge.get("contracts", {}) if isinstance(bridge, dict) else {}
b_disc = sum(1 for ent in bcontracts.values()
             if isinstance(ent, dict) and ent.get("same_owner_discarded"))
b_in_snap = sum(1 for addr in bcontracts if addr.lower() in snap_addrs)
b_not_in_snap = [a for a in bcontracts if a.lower() not in snap_addrs]
log["bridge_leg"] = {"total": len(bcontracts), "same_owner_discarded": b_disc,
                     "in_snapshot_addr": b_in_snap,
                     "not_in_snapshot_addr": len(bcontracts) - b_in_snap,
                     "not_in_snapshot": b_not_in_snap,
                     "bridge_mtime": "2026-11-08 18:21 (unchanged since 02:34 run - same 8 not-in-snapshot)",
                     "note": "Bridge read-only; no promotion check possible this run (leg 4 RPC skipped). Bridge contracts not in snapshot are recorded for the main 30-min job only."}

# --- leg 4: on-chain re-read SKIPPED (RPC unreachable) ---
log["leg4a_change_detection"] = {"status": "SKIPPED",
                                 "reason": "BSC RPC unreachable (bsc-dataseed + ankr both timeout; egress outage)",
                                 "baseline": "run-2026-11-10-0231-reread.json block 132641351 (560 items) + 02:34 leg4a changes - NOT re-read this run",
                                 "note": "No change detection possible; next run re-reads against the same merged baseline."}
log["leg4b_fresh_batch"] = {"status": "SKIPPED",
                            "reason": "RPC unreachable - LOCKSMITH (30/200=15% at block 132643050, below 25% strong-lead) + 10-item todo batch NOT re-read this run"}
log["pending_claims"] = "snapshot pending_claims empty at run start - nothing to re-read"
log["duration_s"] = round(time.time() - T0, 1)
log["outcome"] = "SILENT - network outage: all legs needing egress skipped; no new lead/candidate/promotion/change; no execution. Failed run alone never produces a chat report."

with open(BASE + "hot-leg-run-2026-11-10-0254.json", "w") as f:
    json.dump(log, f, indent=2, ensure_ascii=False)
print(json.dumps(log, indent=2, ensure_ascii=False))
