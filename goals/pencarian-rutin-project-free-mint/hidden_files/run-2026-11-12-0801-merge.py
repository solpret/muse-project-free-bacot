#!/usr/bin/env python3
"""Free-mint-search run 2026-11-12 08:01 WIB — MERGE (written fresh this run).
Merges, in order:
  1. legs 0801 (feed 20, 7 baru vs seen, 1 S1/early = AirdropCnNFT; Boltbook 0 baru; bridge 116/0)
  2. verify.py AirdropCnNFT first read (23/111, blok 133069397)
  3. verify2.py key items (blok 133069998): SEVEN SELLOUT 1111/1111; AirdropCnNFT 75/111;
     AGCR 2394/2400; MECHA 1405; BUCKET 661; MOONDRILL 86; CRTSAINTS 76; SUDOSAINTS 664;
     Pickgrid 218; LuckyCatch 13; BinanceLife 18; 0x2e50 83; binanceai launched 0;
     RigForge 678/0; NAOMI sold out; AgenticGangster sold out; WFPASS sold out; Stampooor 891; 0x7Eb9 1161
  4. tc-age 0801 (CLEPSYDRA / MoonAgent / WNO 1651)
  5. reread 0801 (63 kontrak + 21 track_c, blok 133069638)
  6. AirdropCnNFT final read (111/111 SELLOUT, blok 133070410)
Read-only wrt chain. Writes snapshot (+ .bak-0801) and run-2026-11-12-0801-final.json.
No preview, no mint.
"""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap_path = BASE + "onchain-snapshot.json"
shutil.copy(snap_path, BASE + "onchain-snapshot.json.bak-0801")
snap = json.load(open(snap_path))
legs = json.load(open(BASE + "run-2026-11-12-0801-legs.json"))
v1 = json.load(open(BASE + "run-2026-11-12-0801-verify.json"))
v2 = json.load(open(BASE + "run-2026-11-12-0801-verify2.json"))
tc = json.load(open(BASE + "run-2026-11-12-0801-tc-age.json"))
reread = json.load(open(BASE + "run-2026-11-12-0801-reread.json"))

def index(section):
    out = {}
    v = snap.get(section, {})
    if isinstance(v, dict):
        for k, it in v.items():
            if isinstance(it, dict) and it.get("address"):
                out[it["address"].lower()] = (k, it)
    return out

cidx = index("contracts")
tidx = index("track_c")
updates = {}
crossings = []

def upd(addr, fields, section="contracts", block=None, wib=None):
    idx = cidx if section == "contracts" else tidx
    key = idx.get(addr.lower())
    if key is None:
        updates[addr] = "NOT-IN-SNAPSHOT"
        return
    k, it = key
    for f, val in fields.items():
        if val is not None:
            it[f] = val
    if block:
        it["lastReadBlock"] = block
    if wib:
        it["lastReadWib"] = wib
    updates[addr] = k

# --- threshold-crossing check on reread (free% vs FREE_SUPPLY, vs snapshot prev) ---
for name, d in reread["reread"].items():
    if not isinstance(d, dict) or not d.get("address"):
        continue
    key = cidx.get(d["address"].lower())
    if key is None:
        continue
    k, it = key
    fm = d.get("freeMinted") if d.get("freeMinted") is not None else it.get("freeClaimed")
    cap = d.get("FREE_SUPPLY") if d.get("FREE_SUPPLY") is not None else it.get("FREE_SUPPLY")
    if fm is not None and cap:
        pct = 100.0 * fm / cap
        prev = it.get("freeClaimed")
        prev_cap = it.get("FREE_SUPPLY")
        prev_pct = (100.0 * prev / prev_cap) if (prev is not None and prev_cap) else None
        if pct >= 50 and (prev_pct is None or prev_pct < 50):
            crossings.append(f"{name}: {prev_pct}% -> {pct:.1f}% (cross 50%)")
        if pct > 70 and (prev_pct is None or prev_pct <= 70):
            crossings.append(f"{name}: {prev_pct}% -> {pct:.1f}% (cross 70%)")

V2 = v2["reads"]
VB2 = v2["block"]

def ssum(name):
    return (V2.get(name) or {}).get("summary") or {}

# --- verify2 key items ---
upd("0x467696af8c2206B977B24081445104632dc1D459", {  # Stampooor post-mint
    "freeMinted": ssum("Stampooor").get("freeMinted"),
    "totalMinted": ssum("Stampooor").get("totalMinted"),
    "FREE_SUPPLY": ssum("Stampooor").get("FREE_SUPPLY"),
    "mintOpen": ssum("Stampooor").get("mintOpen"),
    "freeAvailable_user": ssum("Stampooor").get("freeAvailable_user"),
    "freeUsed_user": ssum("Stampooor").get("freeUsed_user"),
    "balanceOf_user": ssum("Stampooor").get("balanceOf_user")}, block=VB2, wib="2026-11-12 08:11 WIB")
upd("0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96", {  # SEVEN SELLOUT
    "status": "sold-out-2026-11-12",
    "freeMinted": ssum("SEVEN").get("freeMinted"),
    "totalMinted": ssum("SEVEN").get("totalMinted"),
    "MAX_SUPPLY": ssum("SEVEN").get("MAX_SUPPLY"),
    "mintOpen": ssum("SEVEN").get("mintOpen"),
    "balanceOf_user": ssum("SEVEN").get("balanceOf_user")}, block=VB2, wib="2026-11-12 08:11 WIB")
upd("0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc", {  # AGCR
    "totalSupply": ssum("AGCR").get("totalSupply"),
    "totalMinted": ssum("AGCR").get("totalMinted"),
    "freeMinted": ssum("AGCR").get("freeMinted"),
    "FREE_SUPPLY": ssum("AGCR").get("FREE_SUPPLY"),
    "MAX_SUPPLY": ssum("AGCR").get("MAX_SUPPLY"),
    "balanceOf_user": ssum("AGCR").get("balanceOf_user"),
    "mintOpen": ssum("AGCR").get("mintOpen")}, block=VB2, wib="2026-11-12 08:11 WIB")
upd("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", {  # MECHA
    "totalMinted": ssum("MECHA").get("totalMinted"),
    "freeClaimed": ssum("MECHA").get("freeClaimed"),
    "freeAvailable_user": ssum("MECHA").get("freeAvailable_user"),
    "balanceOf_user": ssum("MECHA").get("balanceOf_user")}, block=VB2, wib="2026-11-12 08:11 WIB")
upd("0x2b0d3b384C341020aed1d49907b5708C423bA6DA", {  # BUCKET
    "totalSupply": ssum("BUCKET").get("totalSupply"),
    "MAX_SUPPLY": ssum("BUCKET").get("MAX_SUPPLY"),
    "balanceOf_user": ssum("BUCKET").get("balanceOf_user"),
    "freeUsed_user": ssum("BUCKET").get("freeUsed_user")}, block=VB2, wib="2026-11-12 08:11 WIB")
upd("0x87b354E2014D2e418927A1105dD219A2e7b063b0", {  # MOONDRILL
    "totalSupply": ssum("MOONDRILL").get("totalSupply"),
    "MAX_SUPPLY": ssum("MOONDRILL").get("MAX_SUPPLY"),
    "mintOpen": ssum("MOONDRILL").get("mintOpen"),
    "balanceOf_user": ssum("MOONDRILL").get("balanceOf_user"),
    "mintStart": ssum("MOONDRILL").get("mintStart")}, block=VB2, wib="2026-11-12 08:11 WIB")
upd("0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F", {  # CRTSAINTS
    "totalSupply": ssum("CRTSAINTS").get("totalSupply"),
    "MAX_SUPPLY": ssum("CRTSAINTS").get("MAX_SUPPLY"),
    "mintOpen": ssum("CRTSAINTS").get("mintOpen"),
    "balanceOf_user": ssum("CRTSAINTS").get("balanceOf_user"),
    "mintStart": ssum("CRTSAINTS").get("mintStart")}, block=VB2, wib="2026-11-12 08:11 WIB")
upd("0x869d330bb48e7ab32da16745ef9a36a69d34f12f", {  # SUDOSAINTS
    "totalSupply": ssum("SUDOSAINTS").get("totalSupply"),
    "freeMinted": ssum("SUDOSAINTS").get("freeMinted"),
    "MAX_SUPPLY": ssum("SUDOSAINTS").get("MAX_SUPPLY"),
    "balanceOf_user": ssum("SUDOSAINTS").get("balanceOf_user")}, block=VB2, wib="2026-11-12 08:11 WIB")
upd("0x7f541bcc33abed0e64455565da723e949c6f76f0", {  # Pickgrid
    "totalSupply": ssum("Pickgrid").get("totalSupply"),
    "freeMinted": ssum("Pickgrid").get("freeMinted"),
    "balanceOf_user": ssum("Pickgrid").get("balanceOf_user")}, block=VB2, wib="2026-11-12 08:11 WIB")
upd("0xD405C90079c594DA2456F5b37B4158A12f1382e5", {  # Lucky Catch
    "totalSupply": ssum("LuckyCatch").get("totalSupply"),
    "totalMinted": ssum("LuckyCatch").get("totalMinted"),
    "mintOpen": ssum("LuckyCatch").get("mintOpen"),
    "balanceOf_user": ssum("LuckyCatch").get("balanceOf_user"),
    "mintStart": ssum("LuckyCatch").get("mintStart")}, block=VB2, wib="2026-11-12 08:11 WIB")
upd("0x4367b86F889014e6fD57fE812B86A581b913C645", {  # Binance Life
    "totalMinted": ssum("BinanceLife").get("totalMinted"),
    "freeMinted": ssum("BinanceLife").get("freeMinted"),
    "MAX_SUPPLY": ssum("BinanceLife").get("MAX_SUPPLY"),
    "balanceOf_user": ssum("BinanceLife").get("balanceOf_user"),
    "mintStart": ssum("BinanceLife").get("mintStart")}, block=VB2, wib="2026-11-12 08:11 WIB")
upd("0x2e508C6510d9550031932f0D6Fe691DCe38E66E3", {  # 0x2e50
    "totalSupply": ssum("0x2e50").get("totalSupply"),
    "MAX_SUPPLY": ssum("0x2e50").get("MAX_SUPPLY"),
    "mintOpen": ssum("0x2e50").get("mintOpen"),
    "balanceOf_user": ssum("0x2e50").get("balanceOf_user"),
    "mintStart": ssum("0x2e50").get("mintStart")}, block=VB2, wib="2026-11-12 08:11 WIB")
upd("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", {  # binanceai (not in snapshot)
    "launched": ssum("binanceai-mint").get("launched")}, block=VB2, wib="2026-11-12 08:11 WIB")
upd("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", {  # RigForge track_c
    "freeSharesLeft": ssum("RigForge").get("freeSharesLeft"),
    "openedAt": ssum("RigForge").get("openedAt"),
    "freeClaimed": ssum("RigForge").get("freeClaimed")}, section="track_c", block=VB2, wib="2026-11-12 08:11 WIB")
upd("0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9", {  # NAOMI sold out confirmed
    "totalMinted": ssum("NAOMI").get("totalMinted"),
    "freeMinted": ssum("NAOMI").get("freeMinted"),
    "mintOpen": ssum("NAOMI").get("mintOpen"),
    "balanceOf_user": ssum("NAOMI").get("balanceOf_user")}, block=VB2, wib="2026-11-12 08:11 WIB")
upd("0x0a2a07ef09dd7d83e2312476f0588abaa3e34ce3", {  # Agentic Gangster sold out confirmed
    "totalSupply": ssum("AgenticGangster").get("totalSupply"),
    "freeMinted": ssum("AgenticGangster").get("freeMinted"),
    "FREE_SUPPLY": ssum("AgenticGangster").get("FREE_SUPPLY"),
    "MAX_SUPPLY": ssum("AgenticGangster").get("MAX_SUPPLY"),
    "balanceOf_user": ssum("AgenticGangster").get("balanceOf_user")}, block=VB2, wib="2026-11-12 08:11 WIB")
upd("0x7Eb92041aa3037e39baA88154F279e3D9F85c593", {  # 0x7Eb9
    "totalMinted": ssum("0x7Eb9").get("totalMinted"),
    "MAX_SUPPLY": ssum("0x7Eb9").get("MAX_SUPPLY"),
    "balanceOf_user": ssum("0x7Eb9").get("balanceOf_user")}, block=VB2, wib="2026-11-12 08:11 WIB")
upd("0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C", {  # WFPASS sold out (already reported)
    "totalSupply": ssum("WFPASS").get("totalSupply"),
    "totalMinted": ssum("WFPASS").get("totalMinted"),
    "freeMinted": ssum("WFPASS").get("freeMinted")}, block=VB2, wib="2026-11-12 08:11 WIB")

# --- AirdropCnNFT (空投): NEW early lead, sold out same run ---
snap["contracts"]["AirdropCnNFT"] = {
    "address": "0xb5A132A2Efd8351DA2c04e38E2568dd8DC5b1c1a",
    "name": "空投",
    "symbol": "空投",
    "kind": "ERC721",
    "status": "sold-out-2026-11-12",
    "source": "Sourcify feed run 0801 (verifiedAt 2026-11-12T01:02:07Z)",
    "contractFile": "src/AirdropCnNFT.sol",
    "agentIdRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "totalMinted": 111,
    "freeMinted": 111,
    "FREE_CAP": 111,
    "MAX_SUPPLY": 1111,
    "MAX_PER_WALLET": 5,
    "mintOpen": 1,
    "mintOpensAt": 1794445308,
    "mintOpensAtWib": "2026-11-12 08:01:48 WIB",
    "price": 1400000000000000,
    "freeClaimed_user": 0,
    "mintsBy_user": 0,
    "balanceOf_user": 0,
    "freePctVerified": 100.0,
    "launchNote": "Launch TERVERIFIKASI <24 jam: mintOpensAt() on-chain = 2026-11-12 08:01:48 WIB; first mints corroborated (23 minted by ~08:05, blok 133069397). Sourcify verifiedAt 2026-11-12T01:02:07Z.",
    "timeline": "08:05 WIB freeMinted 23/111 (20.7%); ~08:10 WIB 75/111 (67.6%); ~08:13 WIB 111/111 (100% SELLOUT, blok 133070410). Free pool habis ~12 menit sejak buka; ~10 mint/menit.",
    "gate": "website UNVERIFIED (6 metode dicoba run ini: A pencarian alamat 0 hasil; G pencarian nama 空投 0 hasil; H contractURI tidak ada di ABI; I tokenURI(1)='1' tanpa URL; J ABI tanpa fungsi situs; C metadata Sourcify tanpa URL). X UNVERIFIED. TIDAK pernah di-preview/di-mint (early lead; pool habis sebelum promosi).",
    "xVerified": False,
    "websiteVerified": False,
    "velocityVerified": False,
    "lastReadBlock": 133070410,
    "lastReadWib": "2026-11-12 08:13 WIB",
    "runNote0801": "Run 0801: EARLY lead baru (first-seen run ini, first mints terverifikasi on-chain) + SELLOUT di run yang sama. Dilaporkan sekali run ini sebagai early-lead-sold-out; TIDAK di-promosi (20.7% -> 67.6% -> 100% dalam ~8 menit; tidak pernah terverifikasi >70% + slot terbuka secara bersamaan; gate website tidak terverifikasi).",
}
updates["0xb5A132A2Efd8351DA2c04e38E2568dd8DC5b1c1a"] = "AirdropCnNFT"

# --- SEVEN run note ---
sv = cidx.get("0xff65cf70a15fa0b06bf8d8ed020cf9f917c80f96")
if sv:
    k, it = sv
    it["runNote0801"] = (
        "Run 0801 (blok 133069998, ~08:11 WIB): freeMinted 1111/1111 = 100% SELLOUT "
        "(1106/1111 di 0731, +5). Strong lead gate-blocked (sudah dilaporkan sekali) kini sold out - "
        "dilaporkan sekali run ini sebagai perubahan + dihapus dari pantauan aktif (status sold-out). "
        "Umur terverifikasi <24 jam (mintOpensAt 2026-11-11 23:41:37 WIB); gate TIDAK PERNAH terverifikasi (9 metode, run 0731).")

# --- tc-age ---
wno = tidx.get("0x8c969a4cd49e4774908e667702c3d7c3ece164d0")
if wno:
    wno[1]["totalShares"] = tc["WNO"].get("totalShares")
    wno[1]["lastReadBlock"] = tc["block"]
    wno[1]["lastReadWib"] = "2026-11-12 08:08 WIB"
    updates["0x8C969a4CD49E4774908e667702C3d7C3ece164D0"] = wno[0]

# --- reread 0801 (block 133069638): non-None fields only, per-item run note ---
RB2 = reread["block"]
for name, d in reread["reread"].items():
    if not isinstance(d, dict) or not d.get("address"):
        continue
    key = cidx.get(d["address"].lower())
    if key is None:
        continue
    k, it = key
    prev_free = it.get("freeMinted")
    prev_ts = it.get("totalSupply")
    for f in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted",
              "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "balanceOf_user",
              "freeClaimed_user"):
        if d.get(f) is not None:
            it[f] = d[f]
    it["lastReadBlock"] = RB2
    it["lastReadWib"] = "2026-11-12 08:14 WIB"
    it["runNote0801"] = (
        f"Run 0801 (blok {RB2}): freeMinted {prev_free}->{d.get('freeMinted')}, "
        f"totalSupply {prev_ts}->{d.get('totalSupply')}, bal_user={d.get('balanceOf_user')}.")
    updates[d["address"]] = k
for name, d in reread["track_c"].items():
    if not isinstance(d, dict) or not d.get("address"):
        continue
    key = tidx.get(d["address"].lower())
    if key is None:
        continue
    k, it = key
    for f in ("totalSupply", "freeMinted", "freeSharesRemaining",
              "balanceOf_user", "freeClaimed_user"):
        if d.get(f) is not None:
            it[f] = d[f]
    it["lastReadBlock"] = RB2
    it["lastReadWib"] = "2026-11-12 08:14 WIB"
    updates[d["address"]] = k

# bridge same_owner_discarded (corrected computation; 0731 legs.py bug returned [])
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    disc = []
    for k, v in (bridge.get("contracts") or {}).items():
        if isinstance(v, dict) and v.get("same_owner_discarded"):
            disc.append(k)
except Exception:
    disc = []
snap["runNote0801"] = (
    "Run 0801 2026-11-12 08:01 WIB (blok ~133070410): SEVEN SELLOUT 1111/1111 (strong lead gate-blocked -> sold out, "
    "dilaporkan sekali run ini + status sold-out). AIRDROP (空投, AirdropCnNFT 0xb5A1...): EARLY lead baru + SELLOUT di run yang sama "
    "(23 -> 75 -> 111/111 dalam ~8 menit, ~10 mint/menit; umur terverifikasi mintOpensAt 2026-11-12 08:01:48 WIB; "
    "gate website UNVERIFIED 6 metode; tidak pernah di-preview/di-mint; dilaporkan sekali). "
    "Stampooor pasca-mint: totalMinted/freeMinted 891/1200 (74,25%), bal user 1, freeUsed 1 - tanpa perubahan. "
    "AGCR 2394/2400 = 99,75% (umur tetap UNVERIFIED, tidak promosi). MECHA 1405; BUCKET 661; MOONDRILL 86; CRTSAINTS 76; "
    "SUDOSAINTS 664; Pickgrid 218 (72% tapi umur UNVERIFIED); LuckyCatch 13; BinanceLife 18; 0x2e50 83; 0x7Eb9 1161 (+1). "
    "NAOMI 777/777 + AgenticGangster 111/111 + WFPASS 500/500: sold out terkonfirmasi (sudah tercatat, tidak dilaporkan ulang). "
    "binanceai launched()=0 TETAP (pending claim, fase refund). RigForge freeSharesLeft 678, openedAt 0 (belum buka). "
    "CLEPSYDRA startTime 2026-11-06 21:24 WIB + MoonAgent 294/800 tetap age-excluded; WNO totalShares 1651. "
    "Scan leg FAST-FAIL preflight Ankr HTTP 401 (kuota 0% s.d. 1 Des) - watermark TIDAK maju (132512564). "
    "Legs: feed 20 (7 baru vs seen; 1 S1/early = AirdropCnNFT, 6 negatif); Boltbook EN 44.878 byte/7 alamat + ZH 43.151 byte/9 alamat, 0 baru; "
    f"bridge 116 kontrak, 0 not-in-snapshot, same_owner_discarded {len(disc)}. "
    "Sweep web EN+ZH: 0 baru (Agentic Gangster + NAOMI sudah dikenal, terkonfirmasi sold out). "
    "Reread 63 kontrak + 21 track_c: 0 crossing 50%/70% baru. Tidak ada eksekusi (tidak ada preview/mint)."
)
snap["last_run"] = "2026-11-12 08:01 WIB"
snap["last_run_wib"] = "2026-11-12 08:01 WIB"
snap["last_run_note"] = snap["runNote0801"]
json.dump(snap, open(snap_path, "w"), indent=1)
out = {"merged_updates": updates, "crossings": crossings,
       "bridge_same_owner_discarded": len(disc),
       "run_note": snap["runNote0801"][:300]}
json.dump(out, open(BASE + "run-2026-11-12-0801-final.json", "w"), indent=1)
print(json.dumps(out, indent=1))
