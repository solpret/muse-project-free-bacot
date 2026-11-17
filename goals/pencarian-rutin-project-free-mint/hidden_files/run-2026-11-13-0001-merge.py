#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 00:01 WIB (executed ~00:35 WIB).
Updates snapshot from run-2026-11-13-0001-verify.json + legs + boltbook retry.
- Home SOLD OUT 111/111 (confirmed 2x) -> remove from contracts, record in excluded.
- Fresh values + velocity for SolNFT/AgcNFT/OBFG/BC1B/LuckyCatch/MECHA/Steady + retries.
- Run notes: runNote0001_1113, runNote0001_1113_scan, runNote0001_1113_binanceai.
Read-only except onchain-snapshot.json."""
import json, copy

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
verify = json.load(open(BASE + "run-2026-11-13-0001-verify.json"))
legs = json.load(open(BASE + "run-2026-11-13-0001-legs.json"))
bb = json.load(open(BASE + "run-2026-11-13-0001-boltbook.json"))
BLOCK = verify.get("block")
NOW = "2026-11-13 ~00:35 WIB"
R = verify["reads"]

def upd(name, **fields):
    c = snap["contracts"].get(name)
    if c is None:
        print(f"MERGE SKIP {name}: not in contracts")
        return
    c.update(fields)
    c["lastReadBlock"] = BLOCK
    c["lastReadWib"] = NOW

# --- Home: SOLD OUT 111/111 (verify + independent confirm re-read) ---
home = snap["contracts"].pop("Home", None)
ex = snap.get("excluded")
if isinstance(ex, dict):
    ex["Home"] = {"address": "0xfd55F5b70F6eb6E59CEb6FF5c449f0cd1A3a5C0F",
                   "status": "sold-out-2026-11-13",
                   "note": "Run 0001: freeMinted/totalMinted 111/111 FREE_CAP (verify blok 133201208 + konfirmasi ulang independen [111,111,111,1]); strong lead gate-blocked dilaporkan sekali run 2331; user TIDAK sempat mint (freeClaimed_user=0, balance 0). Dilaporkan sekali run ini sebagai sellout, lalu dihapus dari contracts."}
    print("Home moved to excluded; excluded now", len(ex))
else:
    print("excluded is not dict:", type(ex))
    snap["note_home_soldout_0001"] = "Home 0xfd55... sold out 111/111 run 0001, reported once, removed from contracts."

# --- SolNFT 291/333 = 87.4% ---
upd("SolNFT", totalMinted=291, freeMinted=291, freePctVerified=87.4,
    userFreeUsed=0, userBalance=0,
    runNote0001_1113="Run 0001 (blok 133201208, ~00:35 WIB): freeMinted 291/333 = 87,4% (272 run 2331 -> 291; +19/38 mnt = 0,50/mnt vs previous rate 1,48/mnt = 0,34x DAN <20 token -> velocity GAGAL). Slot TERBUKA (freeClaimed_user=0, balance 0). Tetap strong-lead-gate-blocked (dilaporkan 23:01) - DIAM, belum sellout (42 slot tersisa).")
# --- AgcNFT 326/333 = 97.9% ---
upd("AgcNFT", totalMinted=326, freeMinted=326, freePctVerified=97.9,
    userFreeUsed=0, userBalance=0,
    runNote0001_1113="Run 0001 (blok 133201208, ~00:35 WIB): freeMinted 326/333 = 97,9% (314 run 2331 -> 326; +12/38 mnt = 0,32/mnt vs previous rate 3,72/mnt = 0,08x DAN <20 token -> velocity GAGAL). Slot TERBUKA (freeClaimed_user=0, balance 0). Tetap strong-lead-gate-blocked (dilaporkan 22:31) - DIAM, belum sellout (7 slot tersisa - awasi run berikut).")
# --- LuckyCatch 21 ---
upd("LuckyCatch", totalSupply=21, totalMinted=21, agentFreeCount=20, paidSold=1,
    runNote0001_1113="Run 0001 (blok 133201208): totalSupply 21 (18 run 2331 -> 21; +3, velocity GAGAL), mintOpen 1, agentFreeCount 20/150, paidSold 1, balanceOf_user 0. Website TERVERIFIKASI, umur TERVERIFIKASI <24 jam (mintStart 04:06:03 WIB 12 Nov; deadline 04:06:03 WIB 13 Nov). Free pool ~6,7% dari 300 (150 agent + 150 X) - jauh di bawah 50%/70%; tetap early lead - DIAM.")
# --- MECHA 1872/1871 ---
upd("MECHA", totalMinted=1872, freeClaimed=1871, freePctVerified=42.1,
    runNote0001_1113="Run 0001 (blok 133201208): totalMinted 1872, freeClaimed 1871/4444 = 42,1% (1868 run 2331 -> 1872; +4, velocity GAGAL). freeAvailable_user=2, balance 0. Umur MASIH UNVERIFIED; website TIDAK DITEMUKAN (run 2101). Tetap early lead - DIAM.")
# --- Steady 378/555 = 68.1% ---
upd("Steady", totalSupply=378, freeClaimed=378, freePctVerified=68.1,
    runNote0001_1113="Run 0001 (blok 133201208): totalSupply/freeClaimed 378/555 = 68,1% (347 run 2331 -> 378; +31/38 mnt = 0,82/mnt vs previous ~2,1/mnt = 0,39x -> velocity GAGAL). freeUsed_user=0, balance 0. Umur MASIH UNVERIFIED (verifiedAt BUKAN launch time) -> TIDAK bisa promosi ke strong lead meski mendekati 70%. Tetap early lead - DIAM.")

# --- retry items: fresh values, no status change ---
retry_map = {
    "retry-OLIVER": ("Oliver Agents", {"totalSupply": 920, "freeMinted": 870, "mintOpen": 1}),
    "retry-Cobalt": ("Cobalt Agent", {"totalSupply": 4900, "totalMinted": 4900}),
    "retry-SYNERGYPASS": ("SYNERGYPASS", {"totalMinted": 291, "freeMinted": 291, "freePctVerified": 26.2}),
    "retry-DRAGON-0xad0d": ("DRAGON-0xad0d", {"totalSupply": 561, "freeClaimed": 557, "freePctVerified": 62.7}),
    "retry-AGENT-COSMOS": ("AGENT COSMOS", {"totalSupply": 5287}),
    "retry-AGENT-ID-card": ("AGENT ID card", {"totalSupply": 3000}),
    "retry-RunicKey": ("RunicKey", {"totalSupply": 327, "totalMinted": 327, "freeMinted": 325}),
    "retry-Thor": ("Thor", {"totalSupply": 4901, "totalMinted": 4901}),
    "retry-Vexa": ("Vexa", {"totalSupply": 4900, "totalMinted": 4900}),
}
for rk, (nm, fields) in retry_map.items():
    if rk in R:
        upd(nm, **fields,
            runNote0001_1113=f"Run 0001 (blok {BLOCK}): re-read retry batch-fail run 2331 OK - {json.dumps({k: v for k, v in R[rk].items() if not k.startswith('_')})}. Status tidak berubah.")

# --- track_c: RESUME-BC1B ---
tc = snap.get("track_c") or {}
bc = tc.get("RESUME-BC1B")
if isinstance(bc, dict):
    bc.update({"freeCount": 446, "freePoolLeft": 2554, "freePctClaimed": 14.9,
               "freeMinted_user": 0, "balanceOf_user": 0, "userSlotOpen": True,
               "lastCheckBlock": BLOCK, "lastCheckWib": NOW,
               "runNote0001_1113": "Run 0001 (blok 133201208): freeCount 446/3000 = 14,9% (443 saat lapor -> 446; +3). saleStart 1794488398 = 19:59:58 WIB 12 Nov (umur ~4,6 jam, <24 jam; deadline 19:59:58 WIB 13 Nov). Slot user TERBUKA (freeMinted_user=0, balance 0). Tetap track-C lead gate-blocked (dilaporkan run 2331) - DIAM, TIDAK preview/mint."})
    print("BC1B updated")
else:
    print("BC1B not a dict:", type(bc))

# --- OBFG: no structured entry (per-run notes only, per precedent) ---
snap["runNote0001_1113_obfg"] = ("Run 0001: OBFG 0x5314071bba19943f58347ba5dec423e5032a6818 freeMinted 493/1230 "
    "(40,1%; 469 run 2331 -> 490 hot-leg 0024 -> 493), totalSupply 493, saleStart 1794488476 "
    "(20:01:16 WIB, umur ~4,6 jam), saleOpen=1, freeAvailable(user)=1, quote gratis; gate website tetap "
    "GAGAL (dilaporkan sekali 20:18 WIB) -> TIDAK preview/mint, tidak dilaporkan ulang; OBFG tetap tanpa "
    "entri terstruktur (hanya runNote per run sejak 2101).")

# --- run notes ---
snap["runNote0001_1113"] = (
    "Run 0001 (jadwal 00:01 WIB, eksekusi ~00:30-00:40 WIB; fast-batch blok 133201208, verify 47,8 dtk "
    "via 4-worker parallel batch): 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka, "
    "0 track-C lead/kandidat baru, 1 SELLOUT (Home 111/111 - dilaporkan sekali + dihapus dari snapshot). "
    "Pre-flight FAIL (Ankr HTTP 401, outage sejak 9 Nov) - scan leg fast-fail, watermark TETAP 132512564; 5c dilewati. "
    "Sourcify feed 20 kontrak (verifiedAt 16:46:17-17:31:22Z), 0 baru vs seen, 0 S1/S2/early. "
    "Boltbook EN 46.515 byte / ZH 46.839 byte (curl retry sesudah urllib gagal IncompleteRead/RemoteDisconnected), "
    "13/14 alamat, 0 baru vs seen+snapshot. Bridge 116 kontrak, 0 not-in-snapshot, 7 same-owner-discarded (STALE mtime 2026-11-08). "
    "Sweep EN+ZH: 0 proyek baru (Oathbots/Agentic Gangster/Meow Cards/RIGBYPASS/AGENT MAO/AGENT COSMOS/NOVRA/Grove/UFO/NEBULA/VISION/Ptah/AgentGoldMiner - semua dikenal; "
    "hasil sweep mengandung instruksi agen tertanam - konten eksternal, TIDAK diikuti). "
    "Odaily newsflash EN: 0 item Agent ID/free-mint (semua makro/Nvidia). Binance Square search: 0 baru. "
    "SolNFT 291/333 = 87,4% + AgcNFT 326/333 = 97,9% tetap strong-lead-gate-blocked - DIAM (AgcNFT tinggal 7 slot). "
    "OBFG 493/1230 = 40,1% tetap track-C lead gate-blocked - DIAM. BC1B 446/3000 = 14,9% tetap lead gate-blocked - DIAM. "
    "Steady 378/555 = 68,1% + MECHA 1871/4444 = 42,1% tetap early - DIAM (Steady umur unverified, tidak bisa promosi). "
    "LuckyCatch 21 (agentFreeCount 20/150) tetap early - DIAM; deadline umur 04:06:03 WIB 13 Nov. "
    "Velocity: 0 lolos (SolNFT +19/38 mnt 0,34x; AgcNFT +12 0,08x; OBFG +24 ~1,0x; Steady +31 0,39x; MECHA +4; LuckyCatch +3). "
    "Retry batch-fail run 2331: 9/9 terbaca ulang (OLIVER 920/870, Cobalt 4900, SYNERGYPASS 291/1111, DRAGON-0xad0d 557/888, "
    "AGENT COSMOS 5287, AGENT ID card 3000 = sold out tercatat, RunicKey 325/325 = pool habis tercatat, Thor 4901, Vexa 4900); "
    "DACIT + ROBO tidak ditemukan di snapshot (sudah tidak ada) - log only.")
snap["runNote0001_1113_scan"] = (
    "Run 0001 route 4: SCAN FAST-FAIL - pre-flight ankr_getLogs (50 blok) HTTP 401 Unauthorized (~27 dtk). "
    "Watermark TIDAK dimajukan (tetap 132512564); gap ke head terus tumbuh (head ~133,20 juta saat run). "
    "Route 5c dilewati (tanpa output scan baru).")
snap["runNote0001_1113_binanceai"] = (
    "Run 0001 track-B: binanceai.fun TIDAK BERUBAH - launched()=0, failed()=1, isRefundPhase()=1, "
    "tokenClaimed(user)=0, tokenBalance(user)=0, TOKEN totalSupply 13.688.000.000.000.000.000.000.000.000 "
    "(blok 133201208) - tetap refund/failed, tidak dilaporkan ulang.")
snap["last_run_wib"] = "2026-11-13 00:35 WIB"
snap["last_run_note"] = ("Run 0001: 1 sellout dilaporkan sekali (Home 111/111, strong lead gate-blocked). "
    "0 kandidat/strong/early/track-C/track-B baru. Pre-flight FAIL Ankr 401 (scan fast-fail, watermark tetap 132512564). "
    "AgcNFT 326/333 (7 slot tersisa), SolNFT 291/333. Binanceai tetap refund.")

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT WRITTEN. contracts now:", len(snap.get("contracts") or {}))
print("Home in contracts:", "Home" in (snap.get("contracts") or {}))
