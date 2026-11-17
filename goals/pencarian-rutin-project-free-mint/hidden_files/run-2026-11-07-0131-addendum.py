#!/usr/bin/env python3
"""Run 0131 patch (note only): record dedupe notes. Sage Trials was already
added to the snapshot by the backfill (run 132057754-132060821, 02:12 WIB) —
this script only adds the addendum run note, no entry writes."""
import json

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
assert "Sage Trials" in snap["contracts"]
assert snap["contracts"]["Sage Trials"]["status"] == "early-lead-backfill-2026-11-07"
snap["runNote0131_1107_addendum"] = (
    "Addendum run 0131 (parent, pasca-finalisasi): 2 early lead SUDAH dilaporkan ke main chat oleh job "
    "pendamping dan TIDAK dilaporkan ulang run ini. (1) GiraffeValley (GIRAFFE) "
    "0x9F589ABd36E702129E5D33aE0d0C961F8D9f9Ca0 — temuan backfill 132055915-132057753, first mint 01:19:04 WIB, "
    "dilaporkan backfill ke chat 01:57 WIB; masuk snapshot saat run 0131 berjalan (status "
    "early-lead-backfill-2026-11-07); quote(user,1) ~0,000187 BNB (mgmtFee, bukan gas-only), free 0,5%, tanpa "
    "website — early lead saja, bukan kandidat. (2) Sage Trials (SAGE) "
    "0xB0d58925E1075c4E4C02B72f4Bbb3656A6f0b3A3 — temuan hot-leg run 01:49 (Sourcify feed), mintStart 01:50:09 WIB, "
    "dilaporkan hot-leg ke chat 02:06 WIB; run 0131 memverifikasi segar @ blok 132062802 (totalSupply 14/5000, "
    "mintOpen=true, quote cost 0, slot terbuka, website tidak terverifikasi) — dan backfill 132057754-132060821 "
    "(02:12 WIB) menambahkannya ke snapshot (status early-lead-backfill-2026-11-07, first mint blok 132059929, "
    "remaining 4986) sehingga run 0131 tidak menulis entri ganda; BUKAN strong lead (0,28%). "
    "Keduanya tetap watchlist; promosi hanya bila memenuhi kaki strong-lead/kandidat + gate website."
)
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("addendum note saved. contracts:", len(snap["contracts"]))
