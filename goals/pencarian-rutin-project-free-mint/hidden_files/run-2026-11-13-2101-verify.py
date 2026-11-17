#!/usr/bin/env python3
"""Verify for free-mint-search run 2026-11-13 21:01 WIB.
Fresh re-read of the active watchlist (same set as run 20:31 + BUILD, GoldVein, Moon, Zora, D8DA, Cinder Agents).
Read-only; writes run-2026-11-13-2101-verify.json. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        else:
            d += enc_u(int(a))
    return d

def raw_batch(addr, views):
    """views: list of (key, sig, args). Returns dict key->int|raw|None."""
    calls, keys = [], []
    for i, (key, sig, args) in enumerate(views):
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            out = {}
            for it, key in zip(res, keys):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    out[key] = None
                else:
                    r = it["result"]
                    out[key] = to_int(r[:66]) if len(r) >= 66 else r
            return out
        except Exception:
            continue
    return None

def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
            if isinstance(r, dict) and r.get("result"):
                return int(r["result"], 16)
        except Exception:
            continue
    return None

U = [USER]
ITEMS = {
 "OBFG": ("0x5314071bba19943f58347ba5dec423e5032a6818", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("saleStart","saleStart()",[]),("saleOpen","saleOpen()",[]),
    ("freeAvailable_user","freeAvailable(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "NOTV": ("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("FREE_SHARES","FREE_SHARES()",[]),("freeStart","freeStart()",[])]),
 "JNTM": ("0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b", [
    ("freeClaimed","freeClaimed()",[]),("freeLeft","freeLeft()",[]),
    ("FREE_LOTS_CAP","FREE_LOTS_CAP()",[]),("TOTAL_LOTS","TOTAL_LOTS()",[]),
    ("totalMinted","totalMinted()",[]),("paidMinted","paidMinted()",[]),
    ("mintStart","mintStart()",[]),("opened","opened()",[]),("openTime","openTime()",[]),
    ("freeClaimedByAgent_user","freeClaimedByAgent(address)",U),
    ("mintedByAgent_user","mintedByAgent(address)",U),("mintedLots_user","mintedLots(address)",U)]),
 "AgentMuse": ("0x779fa133848d23052B7345F63B3b2E5309cd13ed", [
    ("freeClaimed","freeClaimed()",[]),("FREE_SHARES","FREE_SHARES()",[]),
    ("bookedTotal","bookedTotal()",[]),("openedAt","openedAt()",[]),
    ("DOORS_OPEN","DOORS_OPEN()",[]),("bookedOf_user","bookedOf(address)",U)]),
 "Agentx": ("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492", [
    ("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_CAP","FREE_CAP()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("mintOpensAt","mintOpensAt()",[]),
    ("freeClaimed_user","freeClaimed(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "AgentLabs": ("0x639329f5dc4317c44D9Fed961a1217ba845012F7", [
    ("totalSpecimens","totalSpecimens()",[]),("priceFor_user","priceFor(address)",U),
    ("holdsAgentId_user","holdsAgentId(address)",U),("balanceOf_user","balanceOf(address)",U),
    ("genesisOpen","genesisOpen()",[]),("currentExperiment","currentExperiment()",[]),
    ("genesisStart","genesisStart()",[])]),
 "OUTY": ("0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412", [
    ("minted","minted()",[]),("freeSold","freeSold()",[]),("paidSold","paidSold()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("PAID_CAP","PAID_CAP()",[]),
    ("START","START()",[]),("FREE_END","FREE_END()",[]),("FREE_FEE","FREE_FEE()",[]),
    ("PRICE","PRICE()",[]),("phase","phase()",[]),("freeOpen","freeOpen()",[]),
    ("paidOpen","paidOpen()",[]),("freeQuotaOf_user","freeQuotaOf(address)",U),
    ("quotaOf_user","quotaOf(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "PX24": ("0xe712510fcb27935e657e41ebb97982d6b123136c", [
    ("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U),
    ("costOf_user_1","costOf(address,uint256)",[USER,1])]),
 "SKRR": ("0x9081f02876c173d0c69f042959cfd0d61c668b17", [
    ("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U),
    ("costOf_user_1","costOf(address,uint256)",[USER,1])]),
 "ME30": ("0xa545c8726bcf4acf840dac521b369911fe2abc8d", [
    ("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U),
    ("costOf_user_1","costOf(address,uint256)",[USER,1])]),
 "CY24": ("0x731d879ee2cd4bbf32efef9178d51d5c1441d052", [
    ("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U),
    ("costOf_user_1","costOf(address,uint256)",[USER,1])]),
 "MECHA": ("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", [
    ("totalMinted","totalMinted()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[])]),
 "Pickgrid": ("0x7f541bcc33abed0e64455565da723e949c6f76f0", [
    ("freeMinted","freeMinted()",[]),("FREE_CAP","FREE_CAP()",[]),
    ("totalSupply","totalSupply()",[]),("saleStart","saleStart()",[]),
    ("mintOpensAt","mintOpensAt()",[]),("freeAvailable_user","freeAvailable(address)",U),
    ("freeClaimed_user","freeClaimed(address)",U)]),
 "BinanceAI-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched","launched()",[]),("tokenClaimed_user","tokenClaimed(address)",U),
    ("isRefundPhase","isRefundPhase()",[]),("failed","failed()",[]),
    ("refundClaimed_user","refundClaimed(address)",U)]),
 "HIVE": ("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77", [
    ("totalSupply","totalSupply()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "BinanceAI-token": ("0x209173F09aFbCA053C0de9e9763f503e9fb54a3c", [
    ("totalSupply","totalSupply()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "Zero": ("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647", [
    ("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_CAP","FREE_CAP()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("mintOpensAt","mintOpensAt()",[]),
    ("freeClaimed_user","freeClaimed(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "BC1B": ("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053", [
    ("totalSupply","totalSupply()",[]),("freeCount","freeCount()",[]),
    ("balanceOf_user","balanceOf(address)",U)]),
 "OLIVER": ("0xad86e4d52e55709d1bda08f922853d4b109e0810", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("freeRemaining","freeRemaining()",[]),("FREE_MAX","FREE_MAX()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedCount","mintedCount()",[]),("paidMinted","paidMinted()",[]),
    ("mintPrice","mintPrice()",[]),("mintOpensAt","mintOpensAt()",[]),
    ("saleStart","saleStart()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "RoyalRush": ("0x2e34d33256C920C33b2a03FEC132A2c74061d5D3", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("freeRemaining","freeRemaining()",[]),("FREE_MAX","FREE_MAX()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintPrice","mintPrice()",[]),("mintedCount","mintedCount()",[]),
    ("paidMinted","paidMinted()",[]),("mintOpensAt","mintOpensAt()",[]),
    ("saleStart","saleStart()",[]),("freeClaimedByAgent_user","freeClaimedByAgent(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "Mossbound": ("0xe589A94316C68d4A4f008f841Deb7e9612445244", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("freeRemaining","freeRemaining()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("FREE_PER_WALLET","FREE_PER_WALLET()",[]),
    ("saleStart","saleStart()",[]),("saleEnd","saleEnd()",[]),("saleOpen","saleOpen()",[]),
    ("mintOpen","mintOpen()",[]),("isFreeOpen","isFreeOpen()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("freeAvailable_user","freeAvailable(address)",U)]),
 "Slate": ("0x5893199322A5300775912ebD236d8f1fEFC700Db", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("freeRemaining","freeRemaining()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("FREE_PER_WALLET","FREE_PER_WALLET()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("saleStart","saleStart()",[]),
    ("saleOpen","saleOpen()",[]),("mintOpen","mintOpen()",[]),("isFreeOpen","isFreeOpen()",[]),
    ("balanceOf_user","balanceOf(address)",U)]),
 "Ochre": ("0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("freeRemaining","freeRemaining()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("FREE_PER_WALLET","FREE_PER_WALLET()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("saleStart","saleStart()",[]),
    ("saleOpen","saleOpen()",[]),("mintOpen","mintOpen()",[]),("isFreeOpen","isFreeOpen()",[]),
    ("balanceOf_user","balanceOf(address)",U)]),
 "DragonAgent": ("0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6", [
    ("totalSupply","totalSupply()",[]),("balanceOf_user","balanceOf(address)",U),
    ("price","price()",[]),("MAX_PER_WALLET","MAX_PER_WALLET()",[])]),
 "VioletWaybill": ("0x36D9A4392E3d9ff05B6929C82D536367E9c1bc8d", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("freeRemaining","freeRemaining()",[]),
    ("paidMinted","paidMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("FREE_PER_WALLET","FREE_PER_WALLET()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("saleStart","saleStart()",[]),("saleOpen","saleOpen()",[]),
    ("mintOpen","mintOpen()",[]),("isFreeOpen","isFreeOpen()",[]),
    ("balanceOf_user","balanceOf(address)",U)]),
 "CinderCrucible": ("0x73f1A09e49cA70F8ac6a2F8673Bf7f0f69219b23", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("freeRemaining","freeRemaining()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("saleStart","saleStart()",[]),
    ("saleOpen","saleOpen()",[]),("mintOpen","mintOpen()",[]),("isFreeOpen","isFreeOpen()",[]),
    ("freeAvailable_user","freeAvailable(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "BUBB": ("0x0d72970046c056db90888351b739246f468bff0b", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("freeRemaining","freeRemaining()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("FREE_CAP","FREE_CAP()",[]),("FREE_MAX","FREE_MAX()",[]),
    ("mintOpen","mintOpen()",[]),("saleOpen","saleOpen()",[]),
    ("freeAvailable_user","freeAvailable(address)",U),
    ("freeClaimed_user","freeClaimed(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "MossSignal": ("0xb2e5d82900b854d3cb8c6bb917426abadb687f68", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("freeAvailable_user","freeAvailable(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "AgentCosmos": ("0x3aeda314ec05bc22e3c26a543e16df2b8cc8fe69", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("freeAvailable_user","freeAvailable(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "HANAMI": ("0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("freeAvailable_user","freeAvailable(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "UNRES1": ("0x6430594F2C40A4374f2EfEdF034C77065DC4CC7D", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "UNRES2": ("0xEa98b2065d43c0DE0Ad8629F5D0A08fDABcc708A", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "FROST": ("0x18fdbee7fdd021688057d452e1ddb58f71fb5ea0", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("freeAvailable_user","freeAvailable(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "BUILD": ("0xC43f7Ab11728FC884662B35AD974ff703cb4221d", [
    ("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),
    ("freeLeft","freeLeft()",[]),("FREE_CAP","FREE_CAP()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("freeClaimed_user","freeClaimed(address)",U),("balanceOf_user","balanceOf(address)",U),
    ("holdsAgentId_user","holdsAgentId(address)",U),("mintedCount_user","mintedCount(address)",U)]),
 "GoldVein": ("0xB5Bb50828eB449e7b27AaAd8F7e0CFc621347CB8", [
    ("freeSold","freeSold()",[]),("paidSold","paidSold()",[]),
    ("FREE_SHARES","FREE_SHARES()",[]),("PAID_SHARES","PAID_SHARES()",[]),
    ("startTime","startTime()",[]),("endTime","endTime()",[]),("finalized","finalized()",[]),
    ("freeClaimed_user","freeClaimed(address)",U),("hasAgentId_user","hasAgentId(address)",U),
    ("balanceOf_user","balanceOf(address)",U),("totalSupply","totalSupply()",[]),
    ("costFor_1","costFor(uint256)",[1])]),
 "Moon": ("0x5c6e5f9c1335a8c646e7ad390459a6c4c59b8a95", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("agentIdRegistry","agentIdRegistry()",[]),("mintsBy_user","mintsBy(address)",U),
    ("balanceOf_user","balanceOf(address)",U),("nextTokenId","nextTokenId()",[])]),
 "Zora": ("0xd2e6750064d6617f71475fb429980ce8e2697f2c", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("FREE_MAX","FREE_MAX()",[]),
    ("mintOpen","mintOpen()",[]),("freeAvailable_user","freeAvailable(address)",U),
    ("freeClaimed_user","freeClaimed(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "D8DA": ("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045", [
    ("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "CinderAgents": ("0x49966cf050a5a9cedd252184875267c0e93dbc00", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("freeClaimed_user","freeClaimed(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
}

reads, ok = {}, 0
for name, (addr, views) in ITEMS.items():
    r = raw_batch(addr, views)
    reads[name] = {"address": addr, "views": r, "summary": r}
    if r is not None:
        ok += 1
    print(name, "OK" if r is not None else "FAIL", json.dumps(r)[:220], flush=True)

blk = block_number()
out = {"started_wib": "2026-11-13T21:01+07:00", "reads": reads, "reads_ok": ok,
       "reads_total": len(ITEMS), "block": blk, "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "run-2026-11-13-2101-verify.json", "w"), indent=1)
print("DONE reads_ok", ok, "/", len(ITEMS), "block", blk, "elapsed", round(time.time() - t0, 1))
