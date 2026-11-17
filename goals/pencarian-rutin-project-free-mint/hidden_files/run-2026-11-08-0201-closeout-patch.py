#!/usr/bin/env python3
"""Run 0201 parent close-out patch (after discovery delivery):
1. AgentBook: move contracts -> excluded (free pool sold out; sellout ALREADY
   reported once by hot-leg ~22:19 WIB 7 Nov, blok 132224818, hot-leg-reported.json;
   this run only confirms fresh + updates status — NO re-report).
2. Add runNote0201_discovery + runNote0201_closeout to the snapshot.
Atomic snapshot replace. Does NOT touch watermark/seen/checked files.
"""
import json, os

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(HF + "onchain-snapshot.json"))

ab = snap["contracts"].pop("AgentBook", None)
assert ab is not None, "AgentBook not in contracts (expected strong-lead-gate-blocked)"
snap.setdefault("excluded", {})["AgentBook"] = {
    "address": "0xEECaCBE6eAC6D6F2a38e8daA9049C7AA08aD43b0",
    "track": "A",
    "status": "excluded-sold-out-free-pool-2026-11-08",
    "note": ("Run 0201: free pool HABIS — remainingFree()=0, freeClaimed()=333/333 FREE_QUOTA, "
             "totalSupply 400 (= 333 free + 67 paid), verifikasi segar parent blok 132258134 "
             "(run-2026-11-08-0201-closeout.json); Boltbook 02:04-02:10 WIB sepakat (free 333 penuh; "
             "paid lane 0,0005 BNB 2.933 tersisa, 0 penjualan 66 mnt). Sellout SUDAH dilaporkan sekali "
             "oleh hot-leg ~22:19 WIB 7 Nov (blok 132224818, hot-leg-reported.json) — run ini TIDAK "
             "melaporkan ulang, hanya memindahkan dari kontrak aktif ke excluded. User TIDAK dapat "
             "free mint (balanceOf=0, freeUsed=0); jalur berbayar tetap buka tapi TIDAK dieksekusi."),
    "prev_status": (ab or {}).get("status"),
    "firstMintWib": (ab or {}).get("firstMintWib"),
}

snap["runNote0201_discovery"] = (
    "Run 0201 discovery (subagent, run-2026-11-08-0201-discovery-summary.md): Boltbook boltbook.fun "
    "EN 47.206 B / ZH 47.412 B (HTTP 200) + /u/raca 25.943 B; EN=ZH identik, 10 alamat unik; 0 free-share "
    "keyword hit. Klasifikasi 24 alamat: 11 di snapshot (WAR3, Thetavox, helm.ai, Alchemister2, Night "
    "Shift age-excluded, ABOOK, ONES, BOLT, 3 owner wallet), 4 excluded (Horus sold-out, Luma age, PIXEL "
    "BOYZ age, FREEDROP same-owner), 6 scan-seen/hot-leg-seen bukan first-seen (SPACE ROT baru di front "
    "page — lihat closeout; BRAINROT ZOO, Tera Card, Gacha Gang, Ticker Pets — lihat closeout, Odyssey), "
    "3 false positive (wallet raca.ai, 2 potongan tx hash). Meow & Bark = snapshot watchlist-only, tanpa "
    "perubahan tier. AlphaPulse: share sale berbayar, mint page 404, tanpa kontrak — bukan lead. ORBITA "
    "pace check tanpa kontrak. JOLT season = claim season, bukan free mint. MINTS index 58 proyek, "
    "byte-identical vs 0131, updated_at tidak berubah. Sweep ZH: Nidavellir sudah excluded "
    "(free-window-closed), Laser Agents 13 hari (age), congge Oct 26 list lama, AGENT MAO paused. 5b: 0 "
    "hit baru. Sourcify 5a: 20 kontrak, 0 S1/S2/0 agent-mint (6 near-miss registry=False). Square/Odaily/"
    "PANews: hanya item lama, 0 site link baru. DappBay: tanpa match Hopkin/Nidavellir. Bridge TIDAK "
    "berubah (sha256 b3f349f1..., 115 kontrak, 7 same_owner_discarded, 0 promosi). 0 lead baru dari kaki ini."
)
snap["runNote0201_closeout"] = (
    "Run 0201 parent close-out (blok 132258134, run-2026-11-08-0201-closeout.json, single-call reads): "
    "AgentBook free pool HABIS terkonfirmasi segar (remainingFree 0, freeClaimed 333/333, totalSupply 400) "
    "-> dipindah ke excluded (sellout sudah dilaporkan hot-leg ~22:19 WIB 7 Nov; TIDAK dilaporkan ulang). "
    "SPACE ROT 0x6c724401... (baru di front page Boltbook, post klaim +118 mint/38 mnt, 205 live): "
    "totalSupply 261, freeLeft 3072/3333, mintOpen 1, balanceOf(user)=0, registry BYTES true TAPI "
    "AGENT_ID()/agentRegistry() revert + Sourcify unverified (IncompleteRead) + first mints BUKAN di run "
    "ini (first-seen run 0131) -> BUKAN agent-shaped per strict test, BUKAN early lead, TIDAK ditambah ke "
    "snapshot. Ticker Pets 0x31975837...: totalSupply 571, freeMinted 555/555 (pool HABIS; post 02:1x masih "
    "498/555), mintOpen 1, balanceOf(user)=0, AGENT_ID() MENGEMBALIKAN registry exact "
    "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (agent-shaped TERKONFIRMASI) — tapi pool sudah habis dan "
    "first mints bukan di run ini -> tidak promotable, TIDAK ditambah, tidak dilaporkan (tidak pernah jadi "
    "lead). KAGENT phase=4 + HOPKIN age-excluded sudah ditangani run 0131; run ini hanya konfirmasi."
)

with open(HF + "onchain-snapshot.json.tmp", "w") as f:
    json.dump(snap, f, indent=1)
os.replace(HF + "onchain-snapshot.json.tmp", HF + "onchain-snapshot.json")
print("CLOSEOUT-PATCH DONE agentbook->excluded discovery+closeout notes added")
