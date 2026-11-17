import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
p = f"{BASE}/run-2026-11-08-1631-analysis.json"
a = json.load(open(p))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
already = []
for rec in a["sellout_genuinely_new_vs_1601"]:
    e = snap["contracts"][rec["name"]]
    fm = e.get("freeMinted")
    fs = e.get("FREE_SUPPLY")
    already.append({
        "name": rec["name"],
        "snap_freeMinted": fm,
        "snap_FREE_SUPPLY": fs,
        "already_sold_out_in_snapshot": bool(isinstance(fm, int) and isinstance(fs, int) and fs and fm >= fs),
    })
a["sellout_correction"] = {
    "note": "Analisis 1601 HANYA cek freeClaimed>=FREE_SUPPLY dan totalSupply>=MAX_SUPPLY (TANPA cek freeMinted>=FREE_SUPPLY), sehingga 8 kontrak yang freeMinted-nya sudah == FREE_SUPPLY di snapshot tidak masuk daftar sellout_new 1601. Analisis 1631 menambah cek freeMinted>=FREE_SUPPLY; 8 nama itu BUKAN sellout baru interval ini.",
    "already_sold_out_before_1601": [x for x in already if x["already_sold_out_in_snapshot"]],
    "genuinely_new_sellout_this_interval": ["Voltlings"],
    "voltlings_evidence": "snapshot freeMinted 84/111 (run 1601) -> 1631 freeMinted 111/111, totalSupply 84->111 (+27 interval), free_remaining 0, firstMint 2026-11-08 16:32:01 WIB block 132369105",
}
json.dump(a, open(p, "w"), indent=1)
print("patched. already-sold-out:", len([x for x in already if x["already_sold_out_in_snapshot"]]), "/ 9")
print("genuinely new this interval: Voltlings only")
