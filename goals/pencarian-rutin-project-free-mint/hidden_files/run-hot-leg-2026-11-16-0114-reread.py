#!/usr/bin/env python3
"""Re-read for free-mint-search run 2026-11-16 01:14 WIB (hot-leg).
Run 0114: B77D + AbsurdAgentNFT removed from ITEMS (age-excluded main-job run 0101, deleted from snapshot).
Focus set only (degraded egress; small batches, curl timeout 150s). Run 0401: WoozCode + NovaRemnants removed (age-excluded run 0231, must not be re-read).
Post-run fixes 2131: PX24 address corrected (was typo b140136c, no code); NOTV removed (age-excluded run 2131); DragonAgents removed (age-excluded run 2001).
Read-only; writes run-hot-leg-2026-11-16-0114-reread.json. No preview/mint.
Run 0801: AngelEye-77D9, AngelEye-07bD, SPEC dihapus dari ITEMS (age-excluded run 0801, silent) - jangan dibaca ulang run berikut.
Run 1301: AgentZENITH dihapus dari ITEMS (age-excluded run 1301, sudah dilaporkan sekali) - jangan dibaca ulang run berikut.
Run 1601: PIXEL FROGS dihapus dari ITEMS (age-excluded run 1531, 24,07 jam) - jangan dibaca ulang run berikut."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        elif isinstance(a, str) and a.startswith("0x"):
            d += enc_u(int(a, 16))  # bytes32 / uint256 hex arg
        else:
            d += enc_u(int(a))
    return d
def post_rpc(ep, payload, timeout=150):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)

U = [USER]
ITEMS = {
 "AGCLUB": ("0x67270bb351515abf3089ca5420456897363f5e75", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("FREE_CAP","FREE_CAP()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("totalMinted","totalMinted()",[]),
    ("balanceOf_user","balanceOf(address)",U)]),
 "MORFO": ("0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186", [
    ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[])]),
 "NOISE": ("0xBA5352A3A05Ec637394810D791a412E78A349247", [
    ("totalMinted","totalMinted()",[]),("remainingSupply","remainingSupply()",[]),
    ("mintOpen","mintOpen()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("priceFor_user","priceFor(address)",U),("freeUsed_user","freeUsed(address)",U)]),
 "RaceAgents": ("0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_MAX","FREE_MAX()",[]),("mintOpen","mintOpen()",[])]),
 "Zero": ("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("balanceOf_user","balanceOf(address)",U)]),
 "HIVE": ("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77", [
    ("totalSupply","totalSupply()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "AgentNOVA": ("0x43462d7f269fde4914b03e1e07067a61b62b9540", [
    ("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("freeMintedPerWallet_user","freeMintedPerWallet(address)",U),
    ("mintedPerWallet_user","mintedPerWallet(address)",U),
    ("balanceOf_user","balanceOf(address)",U),("TOKEN_PRICE","TOKEN_PRICE()",[])]),
 "SPARKS": ("0xd52fd117c4b47d03e4e16e778871f09faa5a024b", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("hasAgentId_user","hasAgentId(address)",U),
    ("paused","paused()",[]),("mintedByWallet_user","mintedByWallet(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "AgentBubble": ("0x0d72970046c056db90888351b739246f468bff0b", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("freeClaimed_user","freeClaimed(address)",U)]),
 "BinanceAI-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched","launched()",[]),("failed","failed()",[]),
    ("isRefundPhase","isRefundPhase()",[]),("totalShares","totalShares()",[]),
    ("tokenClaimed_user","tokenClaimed(address)",U)]),
 "WANGCAI": ("0x61A2ff9Be3db25e23886bC59D92d44fAa05959Cd", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("AGENT_ID","AGENT_ID()",[]),
    ("balanceOf_user","balanceOf(address)",U),("owner","owner()",[])]),
 "YUANBAO": ("0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("AGENT_ID","AGENT_ID()",[]),
    ("balanceOf_user","balanceOf(address)",U),("owner","owner()",[])]),
 "PX24": ("0xe712510fcb27935e657e41ebb97982d6b123136c", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[])]),
 "Zephyra": ("0x00a9791be6317d6e3a6c60f75a706c870d882048", [
    ("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("priceFor_user_1","priceFor(address,uint256)",[USER,1]),
    ("mintedBy_user","mintedBy(address)",U),("hasAgentId_user","hasAgentId(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "LumenFindings": ("0x4158B701EaA30E8FaDBaA526F70780A38318c1C4", [
    ("totalSpecimens","totalSpecimens()",[]),("currentExperiment","currentExperiment()",[]),
    ("genesisStart","genesisStart()",[]),("genesisOpen","genesisOpen()",[]),
    ("priceFor_user","priceFor(address)",U),("holdsAgentId_user","holdsAgentId(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "Pengu": ("0x5AEc03C90656743475810926B2B2bd443D5c26a4", [
    ("freeMinted","freeMinted()",[]),("FREE_CAP","FREE_CAP()",[]),
    ("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("freeClaimed_user","freeClaimed(address)",U),
    ("holdsAgentId_user","holdsAgentId(address)",U),("mintsBy_user","mintsBy(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "CPASS": ("0x5877d2bb9f226cc3e438f4d656caeb27deafc576", [
    ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
    ("priceFor_user","priceFor(address)",U),("mintCountOf_user","mintCountOf(address)",U),
    ("holdsAgentId_user","holdsAgentId(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "ORBIT": ("0x7d5F7f323db3050AF92E9aa1584E883B3b24d680", [
    ("freeClaimed","freeClaimed()",[]),("FREE_MAX","FREE_MAX()",[]),
    ("claimOpen","claimOpen()",[]),("hasFreeClaimed_user","hasFreeClaimed(address)",U),
    ("totalSupply","totalSupply()",[])]),
 "TrashBandits": ("0x2d61347D9b48De99cBdF0D8D7a2DD73f5B15E90D", [
    ("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "SKRR": ("0x9081f02876c173d0c69f042959cfd0d61c668b17", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[])]),
 "REOPIR": ("0x12f65bc14037ccdf3f97afc0e67a0e4aca3cf5b9", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("mintedBy_user","mintedBy(address)",U),
    ("freeUsed_user","freeUsed(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "FrieAgent-B751": ("0xb7517e3b31107695f2f8837fafc76999b956c871", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintedBy_user","mintedBy(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "FrieAgent-c64d": ("0xc64da7479c5abc8e6dfadeb4d17502ebcf9837e5", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintedBy_user","mintedBy(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "Ledgera": ("0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "MAMI": ("0xfe36c6d7a1e352cd0822c6818269d190e8e63c13", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "INKI": ("0x5ae38f527340e1aaf4ea214f9778bdc2266e2bd7", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "HashcatDepot": ("0x5aff123300685b6e08aa4396227baf44aabbd4ed", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintsLeft","mintsLeft()",[]),("mintedBy_user","mintedBy(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "OTV": ("0xfab9c88d25e111edd68a2cca3e0f650863a5bf25", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("FREE_MINT_CAP","FREE_MINT_CAP()",[]),("freeMintsLeft","freeMintsLeft()",[]),
    ("PRICE","PRICE()",[]),("mintOpen","mintOpen()",[])]),
 "RAVE": ("0x7c40B78992d86EDfFB5553C74dB5EF427100bb95", [
    ("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("freeClaimed_user","freeClaimed(address)",U),("mintsBy_user","mintsBy(address)",U),
    ("holdsAgentId_user","holdsAgentId(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "HANAMI": ("0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", [
    ("freeSharesLeft","freeSharesLeft()",[]),("openedAt","openedAt()",[]),
    ("freeClaimed","freeClaimed()",[]),("freeBooked_user","freeBooked(address)",U)]),
 "CosmicSentinel": ("0x88731d1eb41c36f3d705fdb58b658244c06afc36", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "GUARD": ("0xB8b7eF8D49981F8987Dfc271DCa50E24ce87AbEb", [
    ("totalMinted","totalMinted()",[]),("freeRemaining","freeRemaining()",[]),
    ("freeBlock","freeBlock()",[]),("maxSupply","maxSupply()",[]),
    ("mintOpenTimestamp","mintOpenTimestamp()",[]),("mintPaused","mintPaused()",[]),
    ("price","price()",[]),("freeUsed_user","freeUsed(address)",U),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "Matrix Agents": ("0x1F669b714337F3C2585072c53fdDD89581F928fF", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("freeRemaining","freeRemaining()",[]),("mintOpen","mintOpen()",[]),
    ("FREE_MAX","FREE_MAX()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("paidMinted","paidMinted()",[]),("mintPrice","mintPrice()",[]),
    ("freeClaimedByAgent_masgayut","freeClaimedByAgent(bytes32)",["0xecf9f926ceb2314ff2b025ef0ce7fb6e1fd0f8ba6a79adffff80a4beb3ac410c"]),
    ("freeClaimedByAgent_masgayut_ai","freeClaimedByAgent(bytes32)",["0x621fa1d010af5819fe524dea10780d79858451bedb5e4b81ac7d183d0e9e1cc3"])]),
}

def chunked(items, n=15):
    items = list(items.items())
    for i in range(0, len(items), n):
        yield items[i:i+n]

def read_chunk(chunk):
    calls, meta = [], []
    for name, (addr, views) in chunk:
        for key, sig, args in views:
            calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                          "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
            meta.append((name, key))
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=150)
            if not isinstance(res, list) or len(res) != len(calls):
                print("  chunk ep", ep, "bad shape", type(res), str(res)[:120], flush=True); continue
            out = {}
            for it, (name, key) in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    out.setdefault(name, {})[key] = None
                else:
                    r = it["result"]
                    out.setdefault(name, {})[key] = to_int(r[:66]) if len(r) >= 66 else r
            return out, ep
        except Exception as e:
            print("  chunk ep", ep, "exc", str(e)[:100], flush=True); continue
    return None, None

def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=150)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16)
        except Exception: continue
    return None

reads, ok = {}, 0
chunks = list(chunked(ITEMS, 3))  # ~3 contracts per chunk => <=18 calls
for ci, ch in enumerate(chunks):
    r, ep = read_chunk(ch)
    names = [n for n, _ in ch]
    if r is None:
        print(f"chunk {ci+1}/{len(chunks)} FAIL {names}", flush=True)
        for n in names: reads[n] = {"address": ITEMS[n][0], "views": None}
        continue
    ok += sum(1 for n in names if r.get(n) is not None)
    for n in names: reads[n] = {"address": ITEMS[n][0], "views": r.get(n)}
    print(f"chunk {ci+1}/{len(chunks)} OK via {ep} ({time.time()-t0:.0f}s) {names}", flush=True)
    time.sleep(5)
blk = block_number()
out = {"started_wib": "2026-11-16T01:14+07:00", "reads": reads, "reads_ok": ok,
       "reads_total": len(ITEMS), "block": blk, "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "run-hot-leg-2026-11-16-0114-reread.json", "w"), indent=1)
print("DONE reads_ok", ok, "/", len(ITEMS), "block", blk, "elapsed", round(time.time() - t0, 1))
