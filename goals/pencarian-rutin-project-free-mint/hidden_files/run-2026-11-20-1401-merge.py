#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 14:01 WIB into onchain-snapshot.json.
Main re-read ~14:02 WIB (50 kontrak, 418 eth_call, 249 errors - degradasi
RPC bsc-dataseed, nilai lama dipertahankan; eth_blockNumber OK, blok merge 134651989).
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama.
Read-only kecuali snapshot. Tanpa perubahan status/lead baru.
Tambahan run ini: 4 kontrak baru dicatat checked (Boltbook 0x556a3c5c unverified;
Sourcify spreamkokolili, Predict Agent Position, Predict Agent - 0 shape hit);
Coffee Agents tetap belum launch; BNB ORBIT 448->449 (tetap age-excluded)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~14:05 WIB"
reread = json.load(open(BASE + "run-2026-11-20-1401-reread.json"))
BLOCK = 134651989  # eth_blockNumber run ini OK (pre-flight Ankr head 134651878)
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1401")
snap = json.load(open(BASE + "onchain-snapshot.json"))
interim = json.load(open(BASE + "run-2026-11-20-1401-interim.json"))
vel = interim["velocity"]
def num(d, k):
    x = d.get(k)
    return x if isinstance(x, int) else None
by_addr = {}
for k, v in snap.get("contracts", {}).items():
    if isinstance(v, dict) and isinstance(v.get("address"), str):
        by_addr[v["address"].lower()] = (k, v)
n_upd = 0
for name, v in vel.items():
    addr = v["address"].lower()
    if addr not in by_addr:
        continue
    sk, sv = by_addr[addr]
    old_sup = v["old_supply"]
    new_sup = v["new_supply"]
    if new_sup is not None:
        sv["previousTotalSupply"] = old_sup
        sv["totalSupply"] = new_sup
    if v["delta"] is not None:
        sv["mintedInInterval"] = v["delta"]
        sv["intervalMinutes"] = v["minutes"]
        sv["currentRatePerMin"] = v["rate_per_min"]
    sv["velocityLegPasses"] = bool(v["velocity_pass"])
    if v["free_pct"] is not None:
        sv["freePctInference"] = v["free_pct"]
    sv["lastReadBlock"] = BLOCK
    sv["lastReadWib"] = NOW_WIB
    sv["runNote1401_1120"] = (
        f"Run 1401 (blok ~{BLOCK}, interval ~{v['minutes']} mnt): "
        f"totalSupply {old_sup}->{new_sup} (+{v['delta']}, {v['rate_per_min']}/mnt vs prev {v['prev_rate_per_min']} = {v['ratio']}x) -> velocity "
        f"{'LOLOS' if v['velocity_pass'] else 'GAGAL'}; free% {v['free_pct']}; bal_user {v['balanceOf_user']}; "
        f"status {sv.get('status')}. DIAM.")
    n_upd += 1
# ONI: totalMinted dari reread run ini
oni = snap.get("contracts", {}).get("ONI", {})
oni_v = reread["reads"].get("ONI", {}).get("views", {})
if oni and num(oni_v, "totalMinted") is not None:
    oni["totalMinted"] = num(oni_v, "totalMinted")
    oni["lastReadBlock"] = BLOCK
    oni["lastReadWib"] = NOW_WIB
    oni["runNote1401_1120"] = (
        f"Run 1401 (blok ~{BLOCK}): totalMinted {oni['totalMinted']} (vs 208 run 1331); "
        f"balanceOf(user)={num(oni_v, 'balanceOf_user')}; free views revert - free% tetap inferensi 20,8%; "
        f"bukan strong lead/kandidat - baseline tracking saja. DIAM.")
# binanceai pending claim: launched/failed/isRefundPhase TERBACA run ini
pc = snap.get("pending_claims", {}).get("binanceai.fun", {})
bv = reread["reads"]["binanceai-mint"]["views"]
for k in ("launched", "failed", "isRefundPhase", "totalShares"):
    if num(bv, k) is not None:
        pc[k] = num(bv, k)
for k in ("tokenClaimed_user", "refundClaimed_user"):
    if num(bv, k) is not None:
        pc[k] = num(bv, k)
pc["lastReadWib"] = NOW_WIB
pc["runNote1401"] = (
    f"Run 1401 (blok ~{BLOCK}): launched={bv.get('launched')}, failed={bv.get('failed')}, "
    f"isRefundPhase={bv.get('isRefundPhase')}, totalShares {bv.get('totalShares')}, "
    f"tokenClaimed(user)={bv.get('tokenClaimed_user')}, refundClaimed(user)={bv.get('refundClaimed_user')} - "
    f"tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
# track_c sales re-reads
tc = snap.get("track_c", {})
for key, rkey in (("bsccat", "bsccat-sale"), ("AONE", "AONE-sale")):
    if key in tc and rkey in reread["reads"]:
        fm = num(reread["reads"][rkey]["views"], "freeMinted")
        if fm is not None:
            old_fm = tc[key].get("freeMinted")
            tc[key]["freeMinted"] = fm
            tc[key]["runNote1401_1120"] = (
                f"Run 1401 (blok ~{BLOCK}): freeMinted {old_fm}->{fm} (FLAT). DIAM.")
        else:
            tc[key]["runNote1401_1120"] = (
                f"Run 1401 (blok ~{BLOCK}): freeMinted GAGAL baca (transport error), nilai lama dipertahankan. DIAM.")
# --- Entri baru / update run ini (dicatat, DIAM, tanpa laporan chat) ---
contracts = snap.setdefault("contracts", {})
# Coffee Agents: re-cek langsung run ini - tetap belum launch
ca = contracts.get("Coffee Agents", {})
if ca:
    ca["mintActive"] = False
    ca["mintStartTime"] = 0
    ca["totalMinted"] = 0
    ca["lastReadBlock"] = BLOCK
    ca["lastReadWib"] = NOW_WIB
    ca["runNote1401_1120"] = (
        f"Run 1401 (blok ~{BLOCK}): re-cek langsung - mintActive=0, mintStartTime=0, totalMinted=0, "
        f"freeClaimed(user)=0, mintFree() revert 'mint not open' -> TETAP BELUM LAUNCH. "
        f"Watchlist-only upcoming, bukan early lead/kandidat. DIAM.")
# BNB ORBIT: totalSupply 448 -> 449, tetap age-excluded
bo = contracts.get("BNB ORBIT", {})
if bo:
    bo["totalSupply"] = 449
    bo["lastReadBlock"] = BLOCK
    bo["lastReadWib"] = NOW_WIB
    bo["runNote1401_1120"] = (
        f"Run 1401 (blok ~{BLOCK}): totalSupply 448->449 (+1), FREE_SUPPLY 444, mintOpen=1, bal_user 0; "
        f"free views revert. Tetap age-excluded (launch ~5 Nov, >24 jam). DIAM.")
contracts["checked-0x556a-1401"] = {
    "address": "0x556a3c5c71e5febd2a7d464b72db444400de841f",
    "status": "checked-not-a-lead-2026-11-20",
    "source": "Boltbook EN+ZH front page run 1401 (baru)",
    "note": "Sourcify unverified (n_fns 0); name()/symbol()/totalSupply()/totalMinted() SEMUA revert/kosong on-chain -> bukan agent-shaped, tanpa bukti registry/free-mint konkret. Bukan lead, tidak masuk watchlist aktif.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB,
}
contracts["checked-0xc716-1401"] = {
    "address": "0xc716CF8b80B62f51a22e6963a77529aBdb2F002F",
    "name": "spreamkokolili", "symbol": "supreamkokolili",
    "status": "checked-not-a-lead-2026-11-20",
    "totalSupply": 1000000000000000000000000000,
    "source": "Sourcify recently-verified feed run 1401 (baru)",
    "note": "Shape S1/S2 FAIL: token biasa, tanpa mint/quote/free view/agent-ref. Bukan sale-shape, bukan lead.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB,
}
contracts["checked-0x63Cc-1401"] = {
    "address": "0x63Cc0DEA20Dc11e39e0cCe58c96b74Eee07c04a3",
    "name": "Predict Agent Position", "symbol": "PATPOS",
    "status": "checked-not-a-lead-2026-11-20",
    "source": "Sourcify recently-verified feed run 1401 (baru)",
    "note": "Shape FAIL: NFT dengan mint tapi tanpa quote/free view/agent-ref -> bukan agent-shaped, bukan lead.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB,
}
contracts["checked-0x92C8-1401"] = {
    "address": "0x92C8Be25004899EaeA931E2B3059E27f11a6674E",
    "name": "Predict Agent", "symbol": "PAT",
    "status": "checked-not-a-lead-2026-11-20",
    "totalSupply": 75000000000000000000000000000,
    "source": "Sourcify recently-verified feed run 1401 (baru)",
    "note": "Shape S1/S2 FAIL: agent_ref=true + mint ada, tapi TANPA quote/cost dan TANPA free view -> bukan track-C sale-shape, bukan lead. (Token prediksi agen, bukan sale gratis.)",
    "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB,
}
snap["timestamp_wib"] = NOW_WIB
snap["last_run_wib"] = "free-mint-search 2026-11-20 14:01 WIB"
snap["runNote1401"] = (
    "Run 1401: re-read 50 kontrak (418 call, 249 error RPC, blok merge 134651989); "
    "velocity LOLOS 0 (delta terbesar +1: Lumenhold + STOCK AGENT); "
    "free>70%: Lumenhold 85,4% (1281/1500) + STOCK AGENT 83,9% (freeLeft 179/1111) - "
    "umur/website UNVERIFIED, bukan strong lead, DIAM; TURTLE/LION di bawah 50% track-A (delta 0). "
    "Pre-flight Ankr 401 (sejak 9 Nov) - scan leg fast-fail, watermark TETAP 134086385, gap ~565.600 blok. "
    "Sourcify 3 baru, 0 shape hit: spreamkokolili (meme token), Predict Agent Position PATPOS (NFT tanpa agent/quote/free), "
    "Predict Agent PAT (agent_ref tapi tanpa quote/free view) - ketiganya dicatat checked-not-lead, DIAM. "
    "Boltbook EN 44.845 byte + ZH 43.115 byte, 9 alamat full, 1 baru 0x556a3c5c (Sourcify unverified, semua view revert) - "
    "dicatat checked-not-a-lead, DIAM. Bridge 0 baru (116/116 in snapshot, 7 same-owner-discarded). "
    "Sweep rute 3 EN/ZH + Square: tanpa proyek baru - semua hit sudah di snapshot (Mintu Bots paid-only, JINCHAN sold out, "
    "AGC, BNB ORBIT age-excluded 448->449, AGENT COSMOS age-excluded, STAMP PASS free sold out, RIGBYPASS excluded). "
    "Coffee Agents re-cek langsung: mintActive=0, mintStartTime=0, totalMinted=0 -> TETAP BELUM LAUNCH, watchlist-only upcoming. "
    "binanceai tetap pending/refund (launched=0, failed=1, isRefundPhase=1, totalShares 3110). "
    "bsccat freeMinted 574 FLAT; AONE freeMinted 10000 FLAT (sold out). "
    "TIDAK ada lead/kandidat/eksekusi baru - DIAM.")
snap["runNote1401_scan"] = (
    "Scan leg route 4: pre-flight Ankr getLogs HTTP 401 Unauthorized (exit 1, head 134651878) - fast-fail, "
    "watermark TETAP 134086385, gap ke head ~565.600 blok dan membesar; blocker kredensial Ankr (custom.ankr) di luar scope job ini. "
    "Track-C 5c: tanpa output scan baru (Ankr 401), tidak ada shape-check backlog run ini.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merged contracts:", n_upd, "| block:", BLOCK, "| no new leads")
