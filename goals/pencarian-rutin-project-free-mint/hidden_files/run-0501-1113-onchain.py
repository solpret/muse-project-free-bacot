#!/usr/bin/env python3
"""On-chain re-read for free-mint-search run 2026-11-13 05:01 WIB.
ONE JSON-RPC batch per contract, contracts in parallel (6 workers).
Read-only; writes run-0501-1113-onchain.json. No preview/mint/execute.
Prev values: run 0401 (~04:07 WIB, block 133229102) + snapshot (0331 merge).
Targets: 0401 list (19) + AgentLabs + Tidalune + SpecLaunchpad + 10 new
Boltbook contracts from 0401 discovery (Voxel Sprite, Chrome Runner, BOLTBOTS,
Agc, Skua Repeater, HASHHIVE, Airdrop Card, Daybreak Drachma, Forge Machine,
Pulse Runner) — fresh reads for snapshot watchlist (first-mint/log verification
is BLOCKED this run: Ankr 401, dataseed getLogs limit-exceeded, see run log).
"""
import json, subprocess, time, concurrent.futures
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

U = enc_addr(USER)
NEW_VIEWS = [("totalSupply","totalSupply()"),("totalMinted","totalMinted()"),
 ("freeClaimed","freeClaimed()"),("freeMinted","freeMinted()"),("freeLeft","freeLeft()"),
 ("freeSupply","freeSupply()"),("FREE_SUPPLY","FREE_SUPPLY()"),("FREE_CAP","FREE_CAP()"),
 ("MAX_SUPPLY","MAX_SUPPLY()"),("mintOpen","mintOpen()"),("mintStart","mintStart()"),
 ("mintOpensAt","mintOpensAt()"),("genesisStart","genesisStart()"),("saleStart","saleStart()"),
 ("balanceOf_user","balanceOf(address)",U),
 ("freeClaimed_user","freeClaimed(address)",U),
 ("freeMinted_user","freeMinted(address)",U),
 ("mintedBy_user","mintedBy(address)",U),
 ("freeUsed_user","freeUsed(address)",U),
 ("costOf_user_1","costOf(address,uint256)",U+enc_u(1)),
 ("quote_user_1","quote(address,uint256)",U+enc_u(1)),
 ("agentIdRegistry","agentIdRegistry()"),("agentRegistry","agentRegistry()"),
 ("AGENT_REGISTRY","AGENT_REGISTRY()"),("registry","registry()"),("owner","owner()")]
TARGETS = {
 "HIVE": ("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77",
          [("totalSupply","totalSupply()"),("totalMinted","totalMinted()"),("FREE_SUPPLY","FREE_SUPPLY()"),
           ("balanceOf_user","balanceOf(address)",U)]),
 "Bubblebruin": ("0xc205F8c74733D914776D66cBc4Cf10BF701D96Aa",
          [("totalSupply","totalSupply()"),("freeClaimed","freeClaimed()"),("FREE_SUPPLY","FREE_SUPPLY()"),
           ("mintOpen","mintOpen()"),("balanceOf_user","balanceOf(address)",U)]),
 "Zapcourier": ("0x672c1dF4F7121DaCBD3504995441C47d2fAbCdDC",
          [("totalSupply","totalSupply()"),("freeClaimed","freeClaimed()"),("FREE_SUPPLY","FREE_SUPPLY()"),
           ("mintOpen","mintOpen()"),("balanceOf_user","balanceOf(address)",U)]),
 "AgentPals": ("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2",
          [("totalSupply","totalSupply()"),("totalMinted","totalMinted()"),("freeMinted","freeMinted()"),
           ("freeClaimed","freeClaimed()"),("FREE_SUPPLY","FREE_SUPPLY()"),("FREE_CAP","FREE_CAP()"),
           ("mintOpen","mintOpen()"),("balanceOf_user","balanceOf(address)",U),
           ("freeClaimed_user","freeClaimed(address)",U)]),
 "AgentRune": ("0xc1fc0bb36d2be928809e4b3e6aa94b3dd2946f53",
          [("totalSupply","totalSupply()"),("totalMinted","totalMinted()"),("freeMinted","freeMinted()"),
           ("freeClaimed","freeClaimed()"),("FREE_SUPPLY","FREE_SUPPLY()"),("FREE_CAP","FREE_CAP()"),
           ("mintOpen","mintOpen()"),("balanceOf_user","balanceOf(address)",U)]),
 "HANAMI": ("0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640",
          [("totalSupply","totalSupply()"),("totalMinted","totalMinted()"),("freeMinted","freeMinted()"),
           ("freeClaimed","freeClaimed()"),("FREE_SUPPLY","FREE_SUPPLY()"),("FREE_CAP","FREE_CAP()"),
           ("mintOpen","mintOpen()"),("balanceOf_user","balanceOf(address)",U)]),
 "MECHA": ("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
          [("totalMinted","totalMinted()"),("freeClaimed","freeClaimed()"),("FREE_SUPPLY","FREE_SUPPLY()"),
           ("freeAvailable_user","freeAvailable(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "SolNFT": ("0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606",
          [("totalMinted","totalMinted()"),("freeMinted","freeMinted()"),("FREE_CAP","FREE_CAP()"),
           ("mintOpen","mintOpen()"),("mintOpensAt","mintOpensAt()"),
           ("freeClaimed_user","freeClaimed(address)",U),("freeUsed_user","freeUsed(address)",U),
           ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "Steady": ("0x4919afF275a3cf126A8F9fD280Ae8Cd24D734cCf",
          [("totalSupply","totalSupply()"),("freeClaimed","freeClaimed()"),("FREE_SUPPLY","FREE_SUPPLY()"),
           ("mintOpen","mintOpen()"),("freeUsed_user","freeUsed(address)",U),
           ("balanceOf_user","balanceOf(address)",U)]),
 "Agentx": ("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
          [("totalMinted","totalMinted()"),("freeMinted","freeMinted()"),("FREE_CAP","FREE_CAP()"),
           ("MAX_SUPPLY","MAX_SUPPLY()"),("mintOpen","mintOpen()"),("mintOpensAt","mintOpensAt()"),
           ("freeClaimed_user","freeClaimed(address)",U),("balanceOf_user","balanceOf(address)",U),
           ("mintsBy_user","mintsBy(address)",U)]),
 "OUTY": ("0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412",
          [("minted","minted()"),("freeSold","freeSold()"),("paidSold","paidSold()"),
           ("FREE_SUPPLY","FREE_SUPPLY()"),("FREE_FEE","FREE_FEE()"),
           ("freeQuotaOf_user","freeQuotaOf(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "LuckyCatch": ("0xD405C90079c594DA2456F5b37B4158A12f1382e5",
          [("totalSupply","totalSupply()"),("mintOpen","mintOpen()"),("mintStart","mintStart()"),
           ("mintEnd","mintEnd()"),("freeMinted","freeMinted()"),("FREE_SUPPLY","FREE_SUPPLY()"),
           ("FREE_CAP","FREE_CAP()"),("agentFreeCount","agentFreeCount()"),("paidSold","paidSold()"),
           ("balanceOf_user","balanceOf(address)",U)]),
 "OBFG": ("0x5314071bba19943f58347ba5dec423e5032a6818",
          [("totalSupply","totalSupply()"),("totalMinted","totalMinted()"),("freeMinted","freeMinted()"),
           ("FREE_SUPPLY","FREE_SUPPLY()"),("saleStart","saleStart()"),("saleOpen","saleOpen()"),
           ("freeAvailable_user","freeAvailable(address)",U),("balanceOf_user","balanceOf(address)",U),
           ("quote_user_1","quote(address,uint256)",U+enc_u(1))]),
 "RESUME-BC1B": ("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053",
          [("totalSupply","totalSupply()"),("freeCount","freeCount()"),("FREE_CAP","FREE_CAP()"),
           ("saleStart","saleStart()"),("freeMinted_user","freeMinted(address)",U),
           ("balanceOf_user","balanceOf(address)",U)]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
          [("totalSupply","totalSupply()"),("freeSharesLeft","freeSharesLeft()"),
           ("freeSharesRemaining","freeSharesRemaining()"),("FREE_SHARES","FREE_SHARES()"),
           ("openedAt","openedAt()"),("freeClaimed","freeClaimed()"),
           ("freeClaimed_user","freeClaimed(address)",U),("freeBooked_user","freeBooked(address)",U),
           ("balanceOf_user","balanceOf(address)",U)]),
 "Mihao": ("0x1f82539520a8b3d4eB7C3145f7E1EaFe4B52c4e1",
          [("totalSupply","totalSupply()"),("freeMinted","freeMinted()"),("FREE_MAX","FREE_MAX()"),
           ("FREE_SHARES","FREE_SHARES()"),("freeSharesRemaining","freeSharesRemaining()"),
           ("freeCount","freeCount()"),("saleOpen","saleOpen()"),("mintOpen","mintOpen()"),
           ("freeClaimed_user","freeClaimed(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "Mihao2": ("0x34eA49e9BC199418f121366BdBEa8fDbab10c26b",
          [("totalSupply","totalSupply()"),("freeMinted","freeMinted()"),("FREE_MAX","FREE_MAX()"),
           ("FREE_SHARES","FREE_SHARES()"),("freeSharesRemaining","freeSharesRemaining()"),
           ("freeCount","freeCount()"),("saleOpen","saleOpen()"),("mintOpen","mintOpen()"),
           ("freeClaimed_user","freeClaimed(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "AgentLabs": ("0x639329f5dc4317c44D9Fed961a1217ba845012F7",
          [("genesisOpen","genesisOpen()"),("currentExperiment","currentExperiment()"),
           ("totalSpecimens","totalSpecimens()"),
           ("specimensInExperiment","specimensInExperiment(uint256)",enc_u(1)),
           ("participantsOf","participantsOf(uint256)",enc_u(1)),
           ("experimentEnd","experimentEnd(uint256)",enc_u(1)),
           ("specimensOf_user","specimensOf(uint256,address)",enc_u(1)+U),
           ("priceFor_user","priceFor(address)",U),
           ("holdsAgentId_user","holdsAgentId(address)",U),
           ("balanceOf_user","balanceOf(address)",U),
           ("isSealed","isSealed(uint256)",enc_u(1))]),
 "Tidalune": ("0x530695a8e3eb9a1253cafc9239811f4ca88791f9",
          [("totalSupply","totalSupply()"),("totalMinted","totalMinted()"),
           ("freeClaimed","freeClaimed()"),("freeMinted","freeMinted()"),
           ("FREE_SUPPLY","FREE_SUPPLY()"),("FREE_CAP","FREE_CAP()"),("MAX_SUPPLY","MAX_SUPPLY()"),
           ("mintOpen","mintOpen()"),("mintStart","mintStart()"),
           ("balanceOf_user","balanceOf(address)",U),
           ("freeUsed_user","freeUsed(address)",U),
           ("mintedBy_user","mintedBy(address)",U),
           ("quote_user_1","quote(address,uint256)",U+enc_u(1))]),
 "SpecLaunchpad": ("0x57Fc464839dfC7A4BAB5c07d6CFeF011CfC77514",
          [("totalSupply","totalSupply()"),("mintOpen","mintOpen()"),("openedAt","openedAt()"),
           ("MAX_SHARES","MAX_SHARES()"),("tokensPerShare","tokensPerShare()"),
           ("costOf_user_1","costOf(address,uint256)",U+enc_u(1)),
           ("quotaOf_user","quotaOf(address)",U),
           ("freeSharesRemaining","freeSharesRemaining()"),
           ("freeClaimed_user","freeClaimed(address)",U),
           ("AGENT_REGISTRY","AGENT_REGISTRY()"),("agentIdRegistry","agentIdRegistry()"),
           ("owner","owner()")]),
 "Voxel Sprite": ("0xe712510fcb27935e657e41ebb97982d6b123136c", NEW_VIEWS),
 "Chrome Runner": ("0x731d879ee2cd4bbf32efef9178d51d5c1441d052", NEW_VIEWS),
 "BOLTBOTS": ("0xdc0cf81f5d38484d1c3b2f2a2c6a11d6d355a56e", NEW_VIEWS),
 "Agc": ("0xdac222886b887fc5b6262889b189b8eb57e99794", NEW_VIEWS),
 "Skua Repeater": ("0x9081f02876c173d0c69f042959cfd0d61c668b17", NEW_VIEWS),
 "HASHHIVE": ("0x318abbb76631bdd4111ce2951f368fdb48def905", NEW_VIEWS),
 "Airdrop Card": ("0xf1d544cc495a05320f36cd02d12e8ef9d9fbff69", NEW_VIEWS),
 "Daybreak Drachma": ("0xa8a508ee984277a548f096117d58266afa5c259e", NEW_VIEWS),
 "Forge Machine": ("0xa545c8726bcf4acf840dac521b369911fe2abc8d", NEW_VIEWS),
 "Pulse Runner": ("0xa5f518e3dc77ccd714b49ec9643bfe8702c65968", NEW_VIEWS),
 "binanceai-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
          [("launched","launched()"),("failed","failed()"),("isRefundPhase","isRefundPhase()"),
           ("tokenClaimed_user","tokenClaimed(address)",U)]),
 "binanceai-token": ("0x209173F09aFbCA053C0de9e9763f503e9fb54a3c",
          [("totalSupply","totalSupply()"),("balanceOf_user","balanceOf(address)",U)]),
}

def one(item):
    name, (addr, views) = item
    calls, keys = [], []
    for i, (key, sig, *rest) in enumerate(views):
        data = sel(sig) + (rest[0] if rest else "")
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            out = {}
            for it, key in zip(res, keys):
                if not isinstance(it, dict) or "error" in it:
                    out[key] = None; continue
                out[key] = to_int(it.get("result"))
            out["_addr"] = addr
            return name, out
        except Exception:
            continue
    return name, {"_addr": addr, "_error": "all-endpoints-failed"}

t0 = time.time()
out = {"run": "free-mint-search 2026-11-13 05:01 WIB (on-chain leg)",
       "started_wib": time.strftime("%Y-%m-%d %H:%M:%S WIB", time.localtime()),
       "prev_run_ref": "run 0401 ~04:07 WIB, block 133229102",
       "block": None, "reads": {}}
try:
    res = post_rpc(EPS[0], {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
    out["block"] = int(res.get("result"), 16)
except Exception as e:
    out["block_error"] = f"{type(e).__name__}: {str(e)[:100]}"
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    for name, r in ex.map(one, TARGETS.items()):
        out["reads"][name] = r
        print(f"{name}: {json.dumps(r)}", flush=True)
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-0501-1113-onchain.json", "w"), indent=1)
print("ELAPSED", out["elapsed_s"], "BLOCK", out.get("block"))
