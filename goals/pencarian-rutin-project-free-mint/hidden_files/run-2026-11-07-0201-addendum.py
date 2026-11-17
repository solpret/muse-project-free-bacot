#!/usr/bin/env python3
"""Addendum run 2026-11-07 02:01 WIB — post-finalization backfill findings.
Backfill-parallel 132063186-132067141 closed the main-scan gap AFTER finalize:
chunk 1 first-seen = Jager Agent Pass (already in snapshot via run 0201, first
mint corrected to block 132063227); chunk 2 first-seen = Jager Agent
0xD8EBDDE362B0a72F7D61b5eD990742B940E30D27 (NEW, not in snapshot).
This script does a focused fresh check of Jager Agent, adds it to the snapshot
as an early lead (backfill finding), and corrects Jager Pass first-mint block
in snapshot + seen. Read-only on-chain except writing onchain-snapshot.json
and onchain-scan-seen.json. NO preview/mint/claim/sign/transaction.
Does NOT touch track-c-scan-checked.json (backfill triage still running)."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
MAIN = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
JA = "0xD8EBDDE362B0a72F7D61b5eD990742B940E30D27"
JP = "0x951f705feB9dCc95D58b445BE58b869724E50707"
OUT = f"{HF}/run-2026-11-07-0201-jageragent-check.json"

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def enc_addr(a):
    return a.lower().replace("0x", "").rjust(64, "0")

def enc_u(n):
    return hex(n)[2:].rjust(64, "0")

def call(addr, sig, args=""):
    data = sel(sig) + args
    for ep in EPS:
        try:
            r = _single(ep, "eth_call", [{"to": addr, "data": data}, "latest"], 10, retries=0)
            if isinstance(r, str) and r.startswith("0x"):
                return r
        except Exception:
            continue
    return None

def u(r):
    if r is None:
        return None
    try:
        return int(r, 16)
    except Exception:
        return r

def block():
    for ep in EPS:
        try:
            r = _single(ep, "eth_blockNumber", [], 10, retries=0)
            if isinstance(r, str):
                return int(r, 16)
        except Exception:
            continue
    return None

blk = block()
views = {}
for sig in ["name()", "symbol()", "totalSupply()", "totalMinted()", "MAX_SUPPLY()",
            "FREE_SUPPLY()", "freeSupply()", "freeMinted()", "freeClaimed()", "freeLeft()",
            "mintOpen()", "saleActive()", "saleEnded()", "mintStart()", "PRICE()", "price()",
            "gate()", "AGENT_ID()", "agentRegistry()", "agentIdRegistry()", "owner()"]:
    views[sig] = call(JA, sig)
views["balanceOf_user"] = call(JA, "balanceOf(address)", enc_addr(MAIN))
views["freeClaimed_user"] = call(JA, "freeClaimed(address)", enc_addr(MAIN))
views["freeMintCount_user"] = call(JA, "freeMintCount(address)", enc_addr(MAIN))
views["quote_user_0"] = call(JA, "quote(address,uint256)", enc_addr(MAIN) + enc_u(0))
views["quote_user_1"] = call(JA, "quote(address,uint256)", enc_addr(MAIN) + enc_u(1))
res = {"run": "2026-11-07-0201-addendum", "address": JA, "block": blk,
       "totalSupply": u(views["totalSupply()"]), "totalMinted": u(views["totalMinted()"]),
       "MAX_SUPPLY": u(views["MAX_SUPPLY()"]), "FREE_SUPPLY": u(views["FREE_SUPPLY()"]),
       "freeMinted": u(views["freeMinted()"]), "freeClaimed": u(views["freeClaimed()"]),
       "freeLeft": u(views["freeLeft()"]), "mintOpen": u(views["mintOpen()"]),
       "saleActive": u(views["saleActive()"]), "mintStart": u(views["mintStart()"]),
       "owner_raw": views["owner()"],
       "balanceOf_user": u(views["balanceOf_user"]),
       "freeClaimed_user": u(views["freeClaimed_user"]),
       "freeMintCount_user": u(views["freeMintCount_user"]),
       "quote_user_0": views["quote_user_0"], "quote_user_1": views["quote_user_1"],
       "gate_raw": views["gate()"], "agentRegistry_raw": views["agentRegistry()"],
       "agentIdRegistry_raw": views["agentIdRegistry()"]}
owner = None
if views["owner()"]:
    try:
        owner = "0x" + views["owner()"][-40:]
    except Exception:
        owner = views["owner()"]
res["owner"] = owner
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))

# Snapshot update (fresh read)
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
contracts = snap["contracts"]
if "Jager Agent" not in contracts:
    contracts["Jager Agent"] = {
        "address": JA,
        "name": "Jager Agent",
        "symbol": "JAGER",
        "kind": "ERC721",
        "status": "early-lead-backfill-2026-11-07",
        "totalSupply": res["totalSupply"],
        "totalMinted": res["totalMinted"],
        "MAX_SUPPLY": res["MAX_SUPPLY"],
        "FREE_SUPPLY": res["FREE_SUPPLY"],
        "freeMinted": res["freeMinted"],
        "balanceOf_user": res["balanceOf_user"],
        "owner": owner,
        "registry_bytes_hit": True,
        "sourcify": "not_verified",
        "agent_shaped": True,
        "note": ("EARLY LEAD temuan backfill 132065186-132067141 (first-seen chunk 2). First mint "
                 "terverifikasi on-chain blok 132067118, 2026-11-07 ~02:45 WIB; 2 mint / 2 minter "
                 "berbeda dalam chunk (minter: 0x0b55a88f… dan 0x67230d32… = owner Jager Agent Pass). "
                 "Registry bytes hit TRUE; Sourcify not_verified. Free path + slot user: lihat "
                 "run-2026-11-07-0201-jageragent-check.json (cek segar addendum). Tanpa website. "
                 "BUKAN strong lead, BUKAN kandidat. TIDAK pernah di-preview/mint. Pelaporan ke chat "
                 "oleh job backfill (temuan backfill); run ini hanya mencatat + menambah snapshot."),
        "first_seen_block": 132067118,
        "first_seen_wib": "2026-11-07 ~02:45 WIB",
        "lastReadBlock": blk,
        "lastReadWib": "2026-11-07 run 0201 addendum",
        "velocityNote": "no-fresh-supply",
        "velocityVerified": False,
    }
    print("Jager Agent added to snapshot as early-lead-backfill-2026-11-07")
else:
    print("Jager Agent already in snapshot, skipped")

# Correct Jager Pass first-mint block (backfill chunk 1: first_block 132063227,
# 61 mints / 61 minters) in snapshot note + seen file.
jp = contracts.get("Jager Agent Pass")
if jp:
    jp["first_seen_block"] = 132063227
    jp["first_seen_wib"] = "2026-11-07 02:16:xx WIB (blok 132063227, koreksi addendum dari 132063335)"
    jp["note"] = jp.get("note", "") + (
        " Koreksi addendum: first mint sebenarnya blok 132063227 (backfill chunk 132063186-132065185, "
        "61 mint / 61 minter berbeda), bukan 132063335 (itu first mint di dalam window main scan).")
    print("Jager Pass first-seen corrected to block 132063227")
seen = json.load(open(f"{HF}/onchain-scan-seen.json"))
seen["contracts"][JP] = 132063227
seen.setdefault("_meta", {})["note_0201_addendum"] = (
    "Addendum run 0201: Jager Pass first-seen dikoreksi 132063335 -> 132063227 (backfill chunk 1, "
    "first mint sebenarnya); Jager Agent 0xD8EB… first-seen 132067118 sudah ditambahkan backfill.")
json.dump(seen, open(f"{HF}/onchain-scan-seen.json", "w"), indent=1)
snap["runNote0201_addendum"] = (
    "Addendum run 0201 (pasca-finalisasi): backfill-parallel 132063186-132067141 menutup gap main scan "
    "(watermark backfill -> 132067141). Chunk 1 first-seen = Jager Agent Pass (sudah di snapshot run ini; "
    "first mint dikoreksi ke blok 132063227, 61 mint/61 minter). Chunk 2 first-seen = Jager Agent "
    "0xD8EBDDE362B0a72F7D61b5eD990742B940E30D27 (2 mint/2 minter, first blok 132067118, registry bytes hit, "
    "Sourcify not_verified) — ditambahkan ke snapshot sebagai early-lead-backfill-2026-11-07; cek segar di "
    "run-2026-11-07-0201-jageragent-check.json. Pelaporan Jager Agent ke chat oleh job backfill (temuan "
    "backfill); run ini hanya mencatat. Snapshot contracts kini 489.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot saved. contracts:", len(snap["contracts"]), "track_c:", len(snap.get("track_c", {})))
