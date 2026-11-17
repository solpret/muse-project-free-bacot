#!/usr/bin/env python3
"""Supplemental merge run 1931: Subagent B verification outcomes.
BAHUANG2 strong-lead promotion (pending report, gate-blocked); GLOOP 18-bit
launched status change; NOVRA track-C exhausted entry; Bound Agents sold-out entry.
Read-only except snapshot. Never touches pending_claims/binanceai."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN_WIB = "2026-11-08 19:31 WIB"

def load(p):
    with open(p) as f: return json.load(f)
def save(p, obj):
    tmp = p + ".tmp"
    with open(tmp, "w") as f: json.dump(obj, f, indent=1)
    import os; os.replace(tmp, p)

snap = load(BASE + "/onchain-snapshot.json")
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})

# BAHUANG2: strong-lead promotion (legs verified fresh), gate still failed
b = contracts.get("BAHUANG2")
if b is not None:
    b["totalMinted"] = 889
    b["freeMinted"] = 886
    b["freePctVerified"] = 29.53
    b["status"] = "strong-lead-pending-report-2026-11-08"
    b["lastReadBlock"] = 132395502
    b["lastReadWib"] = RUN_WIB
    b["runNote1931_1108"] = ("Run 1931 (verifikasi kaki B): totalMinted 425->889, freeMinted 424->886/3000 FREE_CAP = "
        "29,53% >=25% (free view terverifikasi); umur terverifikasi (mintStart 1794133293 = 2026-11-08 17:21:33 WIB, "
        "first mint 17:21:43 WIB, <=48 jam); slot user terbuka (freeCount(user)=0, balanceOf=0, FREE_PER_WALLET=2, "
        "quote(user,1)=[2, 20, 429236604273167 wei, 1]); owner() revert = unverified (bukan di discards). "
        "PROMOSI early->strong lead (3 kaki terpenuhi) PENDING REPORT - parent laporkan sekali. "
        "GATE TETAP GAGAL (website_gate NOT VERIFIED run 1731; B run 1931: gate masih failed) -> TIDAK BISA direct mint "
        "walau strong lead; TIDAK di-preview/di-mint.")

# GLOOP 18-bit (snapshot key "GLOOP", addr 0x183C...): upcoming -> launched
g = contracts.get("GLOOP")
if g is not None and (g.get("address") or "").lower() == "0x183cbb52b3c7bcb2433d50de0add99b59f4de4fe":
    g["totalMinted"] = 1049
    g["difficultyBits"] = 21
    g["mintOpen"] = 1
    g["MINT_START"] = 1794139200
    g["hasMinted_user"] = 0
    g["status"] = "watchlist-only-launched-2026-11-08"
    g["lastReadBlock"] = 132395502
    g["lastReadWib"] = RUN_WIB
    g["runNote1931_1108"] = ("Run 1931 (verifikasi kaki B): LAUNCHED - totalMinted 1049 (B: 853 saat sweep, naik cepat), "
        "mintOpen=1, MINT_START 1794139200 (2026-11-08 19:00 WIB), difficultyBits 21 (PoW-gated, seperti Gloop 0x79d1; "
        "owner SAMA 0x72b9050747bc33d6fef0d76d49b0c7840da47e3b, bukan di discards). free% UNVERIFIED (tanpa free view; "
        "totalMinted 1049/3333 = 31,5% total-supply BUKAN free% dan tidak boleh disubstitusi) -> BUKAN strong lead. "
        "Status upcoming-prelaunch -> launched; BUKAN early lead baru (proyek/owner sama dengan Gloop early lead 0x79d1 "
        "yang sudah dilaporkan) - parent putuskan bila perlu laporan perubahan.")

# NOVRA: track-C, S1 verified but free pool EXHAUSTED
track_c["NOVRA"] = {
    "sale": "0x75Ac13cF23a8dccC703D1496138251FD7f247890",
    "token": "0x75Ac13cF23a8dccC703D1496138251FD7f247890",
    "name": "NOVRA", "symbol": "NOVRA",
    "status": "track-c-free-pool-exhausted-2026-11-08",
    "saleShape": ("S1 VERIFIED run 1931 (verifikasi kaki B): Sourcify exact_match; mint + quote + freeRemaining/freeUsed/"
        "freeSharesUsed + agentIdRegistry + isAgent; FREE_CAP 72; TOKENS_PER_SHARE 1e6."),
    "FREE_CAP": 72, "sharesSold": 73, "freeRemaining": 0,
    "totalSupply": 73000000000000000000000000,
    "quote_user_1": [0, 1000000000000000],
    "freeUsed_user": 0, "mintedBy_user": 0, "userBalance": 0,
    "site": "https://novranetwork.pages.dev/",
    "gate": "FAILED (B run 1931: site + /skill.md + /launch.json semua 'Contract: -', seperti MALTA).",
    "lastReadBlock": 132395502, "lastReadWib": RUN_WIB,
    "baselineNote": ("Ditemukan B run 1931 via thecolony.ai post (Nov 7: 46 sold / 26 dari 72 free tersisa per 7 Nov 15:37 WIB). "
        "Verifikasi on-chain run 1931: S1 LOLOS, TAPI free pool HABIS (freeRemaining()=0, sharesSold 73 = 72 free + 1 paid, "
        "quote(user,1)=(0 free, 0,001 BNB cost)) -> BUKAN lead lagi (pool 0); gate JUGA failed. TIDAK di-preview/di-mint, "
        "TIDAK dilaporkan sebagai lead baru - dicatat exhausted agar tidak ditemukan ulang. Parent laporkan perubahan "
        "pool-habis sekali bila dianggap perlu (temuan B, verifikasi A)."),
}

# Bound Agents: sold out at discovery, never a lead
contracts["Bound Agents"] = {
    "address": "0xa75526d63bd5E3b3e8A65a5f2efEF45072904d04",
    "name": "Bound Agents", "symbol": "BOUND", "kind": "ERC721",
    "status": "sold-out-2026-11-08",
    "totalSupply": 10000, "MAX_SUPPLY": 10000, "mintOpen": 1,
    "owner": "0x0b7c7a171d4385c7b4e308d81605b764ce88f0ed",
    "ownerInDiscards": False,
    "AGENT_ID": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "sourcify": "exact_match",
    "mintedBy_user": 1, "userBalance": 0,
    "lastReadBlock": 132395502, "lastReadWib": RUN_WIB,
    "baselineNote": ("Ditemukan B run 1931 (Boltbook post klaim 10.000/10.000 tapi freeMint() value 0 masih aktif). Verifikasi "
        "on-chain run 1931: totalSupply 10000 = MAX_SUPPLY 10000 -> SOLD OUT; AGENT_ID()=registry persis, freeMint fn ada; "
        "mintedBy(user)=1 (slot user terpakai). TIDAK PERNAH dilaporkan sebagai lead (sold out saat ditemukan); dicatat "
        "sold-out agar tidak ditemukan ulang."),
}

snap["runNote1931_1108_bverify"] = (
    "Run 1931 verifikasi kaki B (5 item): NOVRA 0x75Ac13cF S1 LOLOS (exact_match, mint+quote+freeRemaining/freeUsed+"
    "agentIdRegistry) TAPI free pool HABIS (freeRemaining 0, sharesSold 73, quote(user,1)=(0 free, 0,001 BNB)) + gate FAILED "
    "-> BUKAN lead, dicatat track_c exhausted. ORBIT PASS 0x51d3c0 S1 LOLOS (exact_match, mint+costOf+freeLeft/freeOf+agentIds; "
    "totalSupply 420/2000, freeLeft 1580, costOf(user,1)=0, mintOpen 1) TAPI owner 0x1103... ADA di same-owner-discards "
    "(gelombang costOf/mintsLeft 10 kontrak, discarded 2026-11-06) -> same-owner-discarded, log only, TIDAK dilaporkan. "
    "Bound Agents 0xa75526 AGENT_ID()=registry persis + freeMint, TAPI totalSupply 10000/10000 SOLD OUT, mintedBy(user)=1 -> "
    "dicatat sold-out, TIDAK dilaporkan sebagai lead. BAHUANG2 0x57CC35 PROMOSI early->strong: freeMinted 886/3000 = 29,53% "
    ">=25% (terverifikasi), umur terverifikasi (mintStart 17:21:33 WIB), slot user terbuka (freeCount=0, FREE_PER_WALLET=2) -> "
    "status strong-lead-pending-report (parent laporkan sekali); GATE TETAP GAGAL -> TIDAK BISA direct mint. "
    "GLOOP 18-bit 0x183C... LAUNCHED: totalMinted 1049, mintOpen 1, difficultyBits 21 (PoW), owner SAMA dengan Gloop 0x79d1; "
    "free% UNVERIFIED -> BUKAN strong lead; status upcoming -> launched."
)
save(BASE + "/onchain-snapshot.json", snap)
print("SUPPLEMENTAL MERGE DONE: contracts=%d track_c=%d" % (len(contracts), len(track_c)))
print("BAHUANG2:", contracts["BAHUANG2"]["status"], contracts["BAHUANG2"]["freePctVerified"])
print("GLOOP:", contracts["GLOOP"]["status"], contracts["GLOOP"]["totalMinted"])
print("NOVRA:", track_c["NOVRA"]["status"])
print("Bound Agents:", contracts["Bound Agents"]["status"])
