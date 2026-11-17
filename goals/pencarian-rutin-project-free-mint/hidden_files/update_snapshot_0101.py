#!/usr/bin/env python3
"""Snapshot update run 0101 (2026-11-06 01:01 WIB) — ROUTE 1 only.
Read-only on-chain values from reread-2026-11-06-0101.json (block 131862037,
block-ts 01:07:46 WIB) vs snapshot previous read block 131856855 (00:28:54 WIB)
=> interval 38.87 min by block timestamp. None never overwrites a value.
Velocity passes only if delta>=20 AND prevRate>0 AND rate>=1.5*prevRate;
prevRate None => first baseline, does NOT pass."""
import json, shutil

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(HF + "onchain-snapshot.json"))
reread = json.load(open(HF + "reread-2026-11-06-0101.json"))
BLOCK = reread["block"]
INTERVAL = 38.87
WAVE = ["PRICKLY", "unicorn.exe", "Blend In", "Buzzkill", "Whale Alert",
        "Fresh Hatch", "Lion's Share", "Otter Nonsense", "Hot Springs",
        "Down Under", "Toucan Play", "jelly.exe", "Los Flamingos",
        "Moonhowlers", "Counting Sheep", "Tusk & Trunk", "getpuffr",
        "Hippo Social Club", "LLAMA DRAMA", "Danger Noodles"]

shutil.copy(HF + "onchain-snapshot.json", HF + "onchain-snapshot-0101.bak.json")

def set_if(entry, key, val):
    if val is not None:
        entry[key] = val

updated, skipped = [], []
for label, vals in reread["contracts"].items():
    if label in ("BINANCEAI-mint", "BINANCEAI-token"):
        continue
    if label.endswith("-sale"):
        continue
    if label == "Agent Grove":
        continue
    ent = snap["contracts"].get(label)
    if ent is None:
        skipped.append(label)
        continue
    old_supply = ent.get("totalSupply")
    new_supply = vals.get("totalSupply")
    old_rate = ent.get("currentRatePerMin")
    if new_supply is not None and old_supply is not None:
        delta = new_supply - old_supply
        rate = round(delta / INTERVAL, 4)
        ent["previousTotalSupply"] = old_supply
        ent["mintedInInterval"] = delta
        ent["intervalMinutes"] = INTERVAL
        ent["previousRatePerMin"] = old_rate
        ent["currentRatePerMin"] = rate
        if old_rate is None:
            ent["velocityLegPasses"] = False
            vnote = (f"Run 0101 (blok {BLOCK}, interval {INTERVAL} mnt vs run 0001): "
                     f"{old_supply}->{new_supply} (+{delta}, {rate}/mnt); rate sebelumnya None "
                     f"= baseline pertama -> velocity TIDAK lulus run ini.")
        elif old_rate == 0:
            ent["velocityLegPasses"] = False
            vnote = (f"Run 0101 (blok {BLOCK}, interval {INTERVAL} mnt): {old_supply}->{new_supply} "
                     f"(+{delta}, {rate}/mnt vs prev 0.0 = tidak terhitung) -> velocity GAGAL.")
        else:
            ratio = round(rate / old_rate, 2)
            passes = delta >= 20 and rate >= 1.5 * old_rate
            ent["velocityLegPasses"] = passes
            vnote = (f"Run 0101 (blok {BLOCK}, interval {INTERVAL} mnt): {old_supply}->{new_supply} "
                     f"(+{delta}, {rate}/mnt vs prev {old_rate} = {ratio}x) -> velocity "
                     f"{'LOLOS' if passes else 'GAGAL'}.")
        if label == "HIVE Agents":
            ent["velocityNote0101_1106"] = vnote
        else:
            ent["velocityNote0101"] = vnote
    elif new_supply is not None:
        ent["totalSupply"] = new_supply
    for f in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "price", "owner", "balanceOf_user",
              "mintedBy_user", "freeUsed_user", "quote_user_1",
              "costOf_user_1", "costOf_user_2", "mintsLeft_user",
              "freeLeft_user"):
        set_if(ent, f, vals.get(f))
    # free % recompute only when both legs are real reads
    if ent.get("freeClaimed") is not None and ent.get("FREE_SUPPLY"):
        ent["freePctVerified"] = round(100 * ent["freeClaimed"] / ent["FREE_SUPPLY"], 2)
    elif ent.get("freeMinted") is not None and ent.get("FREE_SUPPLY"):
        ent["freePctVerified"] = round(100 * ent["freeMinted"] / ent["FREE_SUPPLY"], 2)
    ent["lastReadBlock"] = BLOCK
    ent["lastReadWib"] = "2026-11-06 run 0101"
    updated.append(label)

# Agent Grove (upcoming, phase 2 opens 13:05 WIB today)
ag = snap["contracts"].get("Agent Grove")
gv = reread["contracts"].get("Agent Grove", {})
if ag is not None:
    set_if(ag, "FREE_SUPPLY", gv.get("FREE_SUPPLY"))
    set_if(ag, "freeOpen", gv.get("freeOpen"))
    set_if(ag, "balanceOf_user", gv.get("balanceOf_user"))
    ag["lastReadBlock"] = BLOCK
    ag["lastReadWib"] = "2026-11-06 run 0101"
    ag["runNote0101"] = ("Run 0101: FREE_SUPPLY 2500, freeOpen=False (fase 2 dibuka 13:05 WIB hari ini, "
                         "belum dibuka) — tetap watchlist-only-upcoming, bukan kandidat.")
    updated.append("Agent Grove")

# Track-C notes (sale reads; None = gagal baca, bukan perubahan)
tc = snap.get("track_c", {})
tc_notes = {
    "NJAR": "Run 0101: giftsClaimed 561->569 (+8); gate-blocked lead, tanpa perubahan status.",
    "Predictagent-PRDICT": "Run 0101: totalMints 158 (sama), mintOpen=1, quote(user,1)=0; gate-blocked lead, tanpa perubahan.",
    "DROID": "Run 0101: semua view gagal baca (None) — BUKAN perubahan, retry run berikut.",
    "OSK": "Run 0101: opened=0 — tetap belum dibuka.",
    "IMARS": "Run 0101: opened=1, pool gratis habis (freeMinted 300/300) — tetap watchlist-only, BUKAN lead.",
    "NIULAI": "Run 0101: launched=0, phase=4, freeClaimed 4444 — tetap belum dibuka.",
    "LuckyBox-LUCK": "Run 0101: totalSupply 512->545 (+33, mint pihak lain), mintOpen=1, quote(user,1)=0; gate-blocked lead, tanpa perubahan.",
    "DeY": "Run 0101: totalSupply terbaca (base units), balanceOf(user)=0; tanpa perubahan status.",
    "FANBEIMAO-824d": "Run 0101: semua view gagal baca (None) — BUKAN perubahan, retry run berikut.",
    "Nvagent-NVGT": "Run 0101: mintOpen=1, quote(user,1)=0; gate-blocked lead, tanpa perubahan.",
    "Nvagent-NVGT-28Fe": "Run 0101: mintOpen=1, quote(user,1)=0; gate-blocked lead, tanpa perubahan.",
    "Hongbao-HONGBAO": "Run 0101: freeClaimed 7, mintOpen=1; gate-blocked lead, tanpa perubahan.",
    "Soarm-SOARM": "Run 0101: semua view gagal baca (None) — BUKAN perubahan, retry run berikut.",
    "Pacture": "Run 0101: freeClaimed(user)=1 (sudah diklaim) — tanpa perubahan.",
    "Ikigai-Ihigi": "Run 0101: freeMinted 273 (sama) — tanpa perubahan.",
    "KillZero-K0-sale": "Run 0101: launched=0 — tetap belum dibuka.",
    "960E-sale": "Run 0101: semua view gagal baca (None) — BUKAN perubahan, retry run berikut.",
    "CHTCI": "Run 0101: totalSupply terbaca (base units), mintOpen=1 — tanpa perubahan status.",
}
for k, note in tc_notes.items():
    if isinstance(tc.get(k), dict):
        tc[k]["runNote0101"] = note
    else:
        tc[k + "-note0101"] = note

# Track B: BINANCEAI stays refund/failed; pending_claims stays {} (already removed)
snap["runNote0101_binanceai"] = ("Run 0101: BINANCEAI launched=0, isRefundPhase=1, "
    "tokenClaimed(user)=0, tokenBalance(user)=0 — tetap refund/failed, "
    "pending_claims kosong, tidak dilaporkan ulang.")
snap["runNote0101_reread"] = (
    f"Run 0101 re-read blok {BLOCK} (interval {INTERVAL} mnt by block-ts vs run 0001). "
    f"Updated {len(updated)} kontrak; skipped (not in snapshot): {skipped}. "
    "Velocity: tidak ada yang lolos (Moonfall +44 baseline pertama; GHOST +30 ratio 0.69x; "
    "PRICKLY +40 baseline pertama; sisanya <20 token). 0 kandidat, 0 promosi, 0 sellout baru, "
    "0 slot user hilang/baru. Wave 0x293f: costOf(user,1) gagal baca run ini (None, bukan 0) — "
    "nilai lama dipertahankan, retry run berikut; wave 0x1103 costOf(user,1)=0 terverifikasi lagi.")
snap["last_run_wib"] = "2026-11-06 run 0101"
json.dump(snap, open(HF + "onchain-snapshot.json", "w"), indent=1)
print("updated:", len(updated))
print("skipped:", skipped)
print("wrote snapshot + backup onchain-snapshot-0101.bak.json")
