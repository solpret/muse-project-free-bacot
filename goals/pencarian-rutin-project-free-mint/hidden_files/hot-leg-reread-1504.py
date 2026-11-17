#!/usr/bin/env python3
"""Batched on-chain re-read for hot-leg run 2026-11-14 15:04 WIB.
Compares vs main-job 15:01 reread values; probes 9 new feed contracts' code for registry bytes."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import call_many, race
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
PAD = "0" * 24 + USER[2:].lower()
def sel(sig): return "0x" + keccak(sig.encode()).hex()[:8]
U, Q1 = PAD, "%064x" % 1
READS = []
def add(label, addr, fn, args=()):
    data = sel(fn)
    for a in args: data += a
    READS.append((label, (addr, data)))
DRAG = "0xad0D8ac3D61fC8ab397B7136C69fcBf1281a4998"
add("drag_freeClaimed", DRAG, "freeClaimed()"); add("drag_FREE_SUPPLY", DRAG, "FREE_SUPPLY()")
add("drag_totalSupply", DRAG, "totalSupply()"); add("drag_mintedBy", DRAG, "mintedBy(address)", [U])
add("drag_mintOpen", DRAG, "mintOpen()")
WANG = "0x61A2ff9Be3db25e23886bC59D92d44fAa05959Cd"
add("wang_freeClaimed", WANG, "freeClaimed()"); add("wang_mintedBy", WANG, "mintedBy(address)", [U])
YUAN = "0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E"
add("yuan_freeClaimed", YUAN, "freeClaimed()"); add("yuan_mintedBy", YUAN, "mintedBy(address)", [U])
RACE = "0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f"
add("race_freeMinted", RACE, "freeMinted()"); add("race_FREE_MAX", RACE, "FREE_MAX()")
add("race_totalSupply", RACE, "totalSupply()"); add("race_mintOpen", RACE, "mintOpen()")
BUBB = "0x0d72970046c056db90888351b739246f468bff0b"
add("bubb_freeMinted", BUBB, "freeMinted()"); add("bubb_totalSupply", BUBB, "totalSupply()")
LEDG = "0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d"
add("ledg_freeClaimed", LEDG, "freeClaimed()"); add("ledg_FREE_SUPPLY", LEDG, "FREE_SUPPLY()")
add("ledg_totalSupply", LEDG, "totalSupply()"); add("ledg_mintedBy", LEDG, "mintedBy(address)", [U])
NOISE = "0xBA5352A3A05Ec637394810D791a412E78A349247"
add("noise_totalMinted", NOISE, "totalMinted()"); add("noise_remainingSupply", NOISE, "remainingSupply()")
add("noise_priceFor", NOISE, "priceFor(address)", [U]); add("noise_freeUsed", NOISE, "freeUsed(address)", [U])
ORBIT = "0x7d5F7f323db3050AF92E9aa1584E883B3b24d680"
add("orbit_freeClaimed", ORBIT, "freeClaimed()"); add("orbit_claimOpen", ORBIT, "claimOpen()")
add("orbit_hasFreeClaimed", ORBIT, "hasFreeClaimed(address)", [U]); add("orbit_totalSupply", ORBIT, "totalSupply()")
B77D = "0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe"
add("b77d_totalMinted", B77D, "totalMinted()"); add("b77d_mintOpen", B77D, "mintOpen()")
CPASS = "0x5877d2bb9f226cc3e438f4d656caeb27deafc576"
add("cpass_totalMinted", CPASS, "totalMinted()"); add("cpass_mintOpen", CPASS, "mintOpen()")
add("cpass_priceFor", CPASS, "priceFor(address)", [U]); add("cpass_balanceOf", CPASS, "balanceOf(address)", [U])
ZEPH = "0x00a9791be6317d6e3a6c60f75a706c870d882048"
add("zeph_totalMinted", ZEPH, "totalMinted()"); add("zeph_priceFor1", ZEPH, "priceFor(address,uint256)", [U, Q1])
add("zeph_mintedBy", ZEPH, "mintedBy(address)", [U]); add("zeph_mintOpen", ZEPH, "mintOpen()")
PENGU = "0x5AEc03C90656743475810926B2B2bd443D5c26a4"
add("pengu_freeMinted", PENGU, "freeMinted()"); add("pengu_FREE_CAP", PENGU, "FREE_CAP()")
add("pengu_totalMinted", PENGU, "totalMinted()"); add("pengu_freeClaimed", PENGU, "freeClaimed(address)", [U])
AE77 = "0x77D98247BA3dDAfa9ffBceA1F13d3e4cFe3f2d4C"; AE07 = "0x07bD6DbbEf508ad83BA2C557ED979732488894A1"
for tag, a in [("ae77", AE77), ("ae07", AE07)]:
    add(tag+"_freeMinted", a, "freeMinted()"); add(tag+"_freeRemaining", a, "freeRemaining()")
    add(tag+"_FREE_POOL", a, "FREE_POOL()"); add(tag+"_saleActive", a, "saleActive()")
WOOZ = "0xfF172b79d040faefA1Bf34B47151edc87130246E"
add("wooz_totalSnippets", WOOZ, "totalSnippets()"); add("wooz_genesisOpen", WOOZ, "genesisOpen()")
NOVA_R = "0x38C1695eb72B7522c8d6452a4CE27122532A0d69"
add("novar_totalRemnants", NOVA_R, "totalRemnants()"); add("novar_genesisOpen", NOVA_R, "genesisOpen()")
add("novar_priceFor", NOVA_R, "priceFor(address)", [U])
LUMEN = "0x4158B701EaA30E8FaDBaA526F70780A38318c1C4"
add("lumen_totalSpecimens", LUMEN, "totalSpecimens()"); add("lumen_genesisOpen", LUMEN, "genesisOpen()")
add("lumen_priceFor", LUMEN, "priceFor(address)", [U])
MORFO = "0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186"
add("morfo_totalMinted", MORFO, "totalMinted()"); add("morfo_mintOpen", MORFO, "mintOpen()")
BINAI = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
add("binai_launched", BINAI, "launched()"); add("binai_failed", BINAI, "failed()")
add("binai_isRefundPhase", BINAI, "isRefundPhase()"); add("binai_totalShares", BINAI, "totalShares()")
add("binai_tokenClaimed", BINAI, "tokenClaimed(address)", [U])
NEW = ["0xC9B03dffDD392Ff043b48bc9AAa0C9Bc042b09F7","0x1e23DCB53356b5E48D9e85E973Fae664aac286D6","0x11469cFb62E9C50B261f6Ae6a789bf28720c76CA","0xF09B7044FeEDc8154ccEBC1f12eB218fFB1508f9","0xd2B8063f15B91caB967DB292251c64B3348585ca","0xE3Ad908E4A9680B83A476166b86B852D04ff75Df","0x7c40B78992d86EDfFB5553C74dB5EF427100bb95","0x2cc212f57FBBfD191640655dc6319FFb0E567c1c","0x0E8010254fD708456A42037f8149B72178af34AA"]
def to_int(x):
    if x is None: return None
    try:
        s = str(x)
        if s.startswith("0x"):
            return int(s, 16) if len(s) > 2 else None
        return int(s)
    except Exception: return None
t0 = time.time(); out = {}
try:
    out["block"] = to_int(race("eth_blockNumber", ["latest"]))
except Exception as e:
    out["block"] = f"error {str(e)[:150]}"
try:
    res = call_many([c for _, c in READS])
    if isinstance(res, dict): res = [res.get(i) for i in range(len(READS))]
    vals = {}
    for (label, _), r in zip(READS, res): vals[label] = to_int(r)
    out["ok"] = True; out["n"] = len(READS); out["vals"] = vals
except Exception as e:
    out["ok"] = False; out["error"] = str(e)[:400]
out["elapsed_s"] = round(time.time() - t0, 1)
# code probes for the 9 new feed contracts
probes = {}
for a in NEW:
    try:
        code = race("eth_getCode", [a, "latest"])
        probes[a] = {"code_len": len(code)-2 if isinstance(code, str) and code.startswith("0x") else None,
                     "registry_bytes": "60b9262456de011f7d15a54cdd8c48baaa8b022f" in (code or "").lower()}
    except Exception as e:
        probes[a] = {"error": str(e)[:100]}
out["new_code_probes"] = probes
out["elapsed_total_s"] = round(time.time() - t0, 1)
print(json.dumps(out, indent=1))
