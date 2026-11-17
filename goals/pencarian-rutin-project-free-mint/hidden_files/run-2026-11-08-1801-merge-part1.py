#!/usr/bin/env python3
"""Merge run 1801 PART 1 (route-1 re-read + bridge + binanceai + Oddlode sellout).
Parent merge only. Does NOT touch scan state/seen/track-c-checked (part 2, after scan leg).
"""
import json, re

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
S = HF + "onchain-snapshot.json"
snap = json.load(open(S))
reread = json.load(open(HF + "run-2026-11-08-1801-reread.json"))
HEAD = reread["block"]  # 132381403
WIB = "2026-11-08 18:01 WIB"
contracts = snap["contracts"]

# --- 1. re-read numeric updates (non-None only) ---
NUM = ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"]
updated = 0
for name, rd in reread["reread"].items():
    e = contracts.get(name)
    if e is None:
        continue
    changed = False
    for f in NUM:
        v = rd.get(f)
        if v is not None and e.get(f) != v:
            e[f] = v
            changed = True
    e["lastReadBlock"] = HEAD
    e["lastReadWib"] = WIB
    if changed:
        updated += 1
print("contracts updated (numeric change):", updated, "of", len(reread["reread"]))

# --- 2. track_c updates ---
tc = snap["track_c"]
tc_updated = 0
for name, rd in reread["track_c"].items():
    e = tc.get(name)
    if e is None:
        continue
    for f in ["totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"]:
        v = rd.get(f)
        if v is not None and e.get(f) != v:
            e[f] = v
            tc_updated += 1
    e["lastReadWib"] = WIB
print("track_c fields updated:", tc_updated)

# --- 3. Oddlode Drills -> sold-out (freeMinted 1000/1000, minted-by-user) ---
od = contracts.get("Oddlode Drills")
if od is not None:
    od["status"] = "sold-out-free-2026-11-08"
    od["runNote1801_1108"] = ("Run 1801: freeMinted 1000/1000 (totalSupply 1001) - free pool SOLD OUT "
        "antara run 1731 (995/1000) dan run 1801. User sudah mint (balance 1, freeClaimed(user)=1) - "
        "tidak ada aksi; status diubah sold-out, tidak dilaporkan ulang sebagai lead.")
    print("Oddlode Drills -> sold-out-free-2026-11-08")

# --- 4. per-contract run notes 1801 ---
notes = {
    "HIVE Agents": "Run 1801: totalSupply flat 1256, balanceOf(user)=1, status minted-by-user - tanpa perubahan.",
    "Bubblebruin": "Run 1801: totalSupply 2081 (prev 2081), freeClaimed 2075/7777 = 26.7%, minted-by-user - tanpa perubahan.",
    "Paw Gang": "Run 1801 (read-only): totalMinted 3110->3197 (+87), totalSupply gagal baca (None = artefak RPC, bukan nol), mintOpen 1, balance 0; PoW tetap memblokir (tidak dicoba ulang).",
    "Jinli Agents": "Run 1801: 280->286 (+6), free% 31.9%, slot terbuka (bal 0), gate website tetap GAGAL - tidak di-mint, tidak dilaporkan ulang.",
    "Dafeiyu": "Run 1801: 666 flat, free view degraded (None = artefak RPC), slot terbuka (freeClaimed_user 0), gate website tetap GAGAL - tidak di-mint, tidak dilaporkan ulang.",
    "Chiphiveowl": "Run 1801: 584->587 (+3), free% 72.8%, slot terbuka (bal 0), gate website tetap GAGAL - tidak di-mint, tidak dilaporkan ulang.",
    "Farmbuxiang": "Run 1801: 480 flat, free% 68.4%, slot terbuka (bal 0), gate website tetap GAGAL - tidak di-mint, tidak dilaporkan ulang.",
    "0xbd4B4e7189ae9356514664146b0eD683601200A9": "Run 1801: velocity PASS (+27, 3.04x) free% VERIFIED 70.4% (1956/2777, 821 tersisa) - TAPI slot user SUDAH terpakai (freeClaimed(user)=1, balance 1) - BUKAN kandidat/strong lead, tidak promosi.",
    "Zhenzhu": "Run 1801: velocity 'PASS' (ratio 1.76x) adalah ARTEFAK - kontrak ERC-20 (totalSupply 2.18e16 raw units), bukan NFT; minted = delta supply token, bukan jumlah NFT. Bukan promosi, bukan lead.",
    "Cassetto": "Run 1801: 2695->2698 (+3), free% 38.5% (2693/7000), slot TERBUKA (quote(user,1)=0, freeUsed=0, mintedBy=0, bal 0; probe run 1801) - TAPI promosi ke strong lead TETAP DIBATALKAN: owner 0x5304... = factory wave 8 kontrak, sudah di same-owner-discards.json sejak run 1431 (preseden Gourdwick). contractURI base64 JSON tanpa external_link/URL (metode H: tanpa pointer situs). Tidak dilaporkan ulang, tidak di-mint.",
    "Candlewick": "Run 1801: 2977->2980 (+3), free% 42.5% (2975/7000), slot TERBUKA (quote(user,1)=0; probe run 1801) - promosi DIBATALKAN same-owner (owner 0x5304..., discards sejak run 1431). contractURI tanpa URL. Tidak dilaporkan ulang, tidak di-mint.",
    "Coralume": "Run 1801: 2795->2796 (+1), free% 39.7% (2781/7000), slot TERBUKA (quote(user,1)=0; probe run 1801) - promosi DIBATALKAN same-owner (owner 0x5304..., discards sejak run 1431). Tidak dilaporkan ulang, tidak di-mint.",
    "Retrocam": "Run 1801: 2666 flat, free% 38.0% (2661/7000), slot TERBUKA (quote(user,1)=0; probe run 1801) - promosi DIBATALKAN same-owner (owner 0x5304..., discards sejak run 1431). Tidak dilaporkan ulang, tidak di-mint.",
    "Pixpad": "Run 1801: 2837 flat, free% 40.4% (2831/7000), slot TERBUKA (quote(user,1)=0; probe run 1801) - promosi DIBATALKAN same-owner (owner 0x5304..., discards sejak run 1431). Tidak dilaporkan ulang, tidak di-mint.",
    "Keyforge": "Run 1801: 2608->2611 (+3), free% 37.2% (2606/7000), slot TERBUKA (quote(user,1)=0; probe run 1801) - promosi DIBATALKAN same-owner (owner 0x5304..., discards sejak run 1431). Tidak dilaporkan ulang, tidak di-mint.",
    "Hourglas": "Run 1801: 2979->2982 (+3), free% 42.5% (2977/7000), slot TERBUKA (quote(user,1)=0; probe run 1801) - promosi DIBATALKAN same-owner (owner 0x5304..., discards sejak run 1431). Tidak dilaporkan ulang, tidak di-mint.",
    "Compasso": "Run 1801: 2876->2880 (+4), free% 41.1% (2875/7000), slot TERBUKA (quote(user,1)=0; probe run 1801) - promosi DIBATALKAN same-owner (owner 0x5304..., discards sejak run 1431). Tidak dilaporkan ulang, tidak di-mint.",
    "CAISHEN": "Run 1801: 224 flat, free% 24.9% (221/888) - di bawah ambang strong lead 25%, tidak promosi.",
    "Agent Goats": "Run 1801: 759 flat, free% 68.2% VERIFIED (758/1111) - TAPI umur peluncuran UNVERIFIED (firstMintWib/startTimeWib kosong) + slot user UNVERIFIED (freeClaimed(user) gagal baca) - tidak promosi ke strong lead.",
}
for name, note in notes.items():
    if name in contracts:
        contracts[name]["runNote1801_1108"] = note
print("run notes set:", len([n for n in notes if n in contracts]))

# --- 5. binanceai note (re-check identical) ---
snap["runNote1801_binanceai"] = ("Run 1801: BINANCEAI re-check - launched()=0, failed()=1, isRefundPhase()=1, "
    "totalShares()=3110, tokenClaimed(user)=0, tokenBalance(user)=0 - IDENTIK run 1701/1731. Tetap fase "
    "refund/failed; tracking pending claim tetap DITUTUP; TIDAK dilaporkan ulang. Tidak ada preview/klaim.")

# --- 6. ADD bridge contracts missing from snapshot (amendment 2026-11-03 ~11:41) ---
# ERC20-only contracts are NOT added (ORE, Ikigai, AGC, ETHBack tracker, PANBA, unnamed ERC20):
# detected by heuristic below (huge raw totalSupply + no NFT views).
bridge_reads = json.load(open(HF + "run-2026-11-08-1801-bridge-binanceai.json"))
bridge = json.load(open(HF + "scan-bridge.json"))
snap_addrs = {v.get("address", "").lower() for v in contracts.values()}
added = []
for addr, meta in bridge.get("contracts", {}).items():
    if addr.lower() in snap_addrs or meta.get("same_owner_discarded"):
        continue
    rd = bridge_reads["bridge"].get(addr) or bridge_reads["bridge"].get(addr.lower()) or {}
    # ERC20 detection: huge raw totalSupply (>10^12) with no NFT views at all
    ts = rd.get("totalSupply")
    is_erc20 = isinstance(ts, int) and ts > 10**12 and rd.get("MAX_SUPPLY") is None and rd.get("FREE_SUPPLY") is None
    if is_erc20:
        continue
    note = str(meta.get("note") or "")
    m = re.match(r"^([A-Za-z0-9 _\-/]+?)(?:\s*\([A-Z0-9]+\))?\s*#", note)
    name = m.group(1).strip() if m else ("bridge-" + addr[:10])
    name = re.sub(r"\s+", " ", name)
    key = name if name not in contracts else ("bridge-" + addr[:10])
    fs = rd.get("FREE_SUPPLY")
    fc = rd.get("freeClaimed")
    freepct = round(fc / fs * 100, 2) if isinstance(fc, int) and isinstance(fs, int) and fs else None
    contracts[key] = {
        "address": addr,
        "status": "watchlist-only-pelengkap-scan-2026-11-08",
        "name": name,
        "kind": "ERC721",
        "totalSupply": ts,
        "totalMinted": rd.get("totalMinted"),
        "freeClaimed": fc,
        "freeMinted": rd.get("freeMinted"),
        "FREE_SUPPLY": fs,
        "MAX_SUPPLY": rd.get("MAX_SUPPLY"),
        "freePctVerified": freepct,
        "mintOpen": rd.get("mintOpen"),
        "userBalance": rd.get("balanceOf_user"),
        "freeClaimed_user": rd.get("freeClaimed_user"),
        "first_seen_bridge": str(meta.get("first_seen", "")),
        "bridge_reported_as": meta.get("reported_as"),
        "launchNote": "Usia peluncuran UNVERIFIED (temuan pelengkap scan; first_seen scan bukan launch time).",
        "baselineNote": ("Temuan pelengkap scan (amendment 2026-11-03 ~11:41): sudah dilaporkan sebagai 'finding' "
            "oleh scan job, BUKAN lead baru job ini. Ditambahkan ke snapshot watchlist pada re-read rutin "
            "pertama (run 1801) dengan sumber scan. Dilaporkan hanya bila re-read rutin menunjukkan promosi "
            "tier / perubahan. Catatan scan: " + note[:180]),
        "lastReadBlock": HEAD,
        "lastReadWib": WIB,
    }
    added.append(key)
print("bridge added:", len(added), added)

with open(S + ".tmp1801", "w") as _f:
    json.dump(snap, _f, indent=1)
import os as _os
_os.replace(S + ".tmp1801", S)
print("contracts now:", len(snap["contracts"]))
print("DONE PART 1")
