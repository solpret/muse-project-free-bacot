#!/usr/bin/env python3
"""Verify for free-mint-search run 2026-11-13 03:31 WIB.
ONE JSON-RPC batch per contract (all views in a single POST), contracts run
in parallel (4 workers), per-item error -> None. Read-only; writes
run-2026-11-13-0331-verify.json. No preview/mint.
Merged targets: 0101 verify + verify-new (Agentx, OUTY) + GAME + HIVE/
Bubblebruin/Zapcourier supply re-reads. AgcNFT dropped (sold out 333/333)."""
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
def dec_str(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        if len(b) < 64: return None
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception: return None
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

GENERIC = [("totalSupply","totalSupply()"),("totalMinted","totalMinted()"),
           ("freeMinted","freeMinted()"),("freeClaimed","freeClaimed()"),
           ("FREE_SUPPLY","FREE_SUPPLY()"),("FREE_CAP","FREE_CAP()"),
           ("mintOpen","mintOpen()"),("mintOpensAt","mintOpensAt()"),
           ("balanceOf_user","balanceOf(address)",enc_addr(USER)),
           ("freeClaimed_user","freeClaimed(address)",enc_addr(USER)),
           ("freeAvailable_user","freeAvailable(address)",enc_addr(USER))]
TARGETS = {
 "SolNFT": ("0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606",
            [("totalMinted","totalMinted()"),("freeMinted","freeMinted()"),("FREE_CAP","FREE_CAP()"),
             ("mintOpen","mintOpen()"),("mintOpensAt","mintOpensAt()"),
             ("freeClaimed_user","freeClaimed(address)",enc_addr(USER)),
             ("balanceOf_user","balanceOf(address)",enc_addr(USER))]),
 "Agentx": ("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
            [("totalMinted","totalMinted()"),("freeMinted","freeMinted()"),("FREE_CAP","FREE_CAP()"),
             ("MAX_SUPPLY","MAX_SUPPLY()"),("mintOpen","mintOpen()"),("mintOpensAt","mintOpensAt()"),
             ("price","price()"),("freeClaimed_user","freeClaimed(address)",enc_addr(USER)),
             ("balanceOf_user","balanceOf(address)",enc_addr(USER)),
             ("holdsAgentId_user","holdsAgentId(address)",enc_addr(USER)),
             ("mintsBy_user","mintsBy(address)",enc_addr(USER)),
             ("owner","owner()"),("name","name()"),("symbol","symbol()"),
             ("nextTokenId","nextTokenId()")]),
 "OUTY": ("0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412",
          [("minted","minted()"),("freeSold","freeSold()"),("paidSold","paidSold()"),
           ("FREE_SUPPLY","FREE_SUPPLY()"),("PAID_CAP","PAID_CAP()"),("START","START()"),
           ("FREE_END","FREE_END()"),("FREE_FEE","FREE_FEE()"),("PRICE","PRICE()"),
           ("phase","phase()"),("status","status()"),("freeOpen","freeOpen()"),("paidOpen","paidOpen()"),
           ("freeQuotaOf_user","freeQuotaOf(address)",enc_addr(USER)),
           ("quotaOf_user","quotaOf(address)",enc_addr(USER)),
           ("balanceOf_user","balanceOf(address)",enc_addr(USER)),
           ("owner","owner()"),("name","name()"),("symbol","symbol()")]),
 "OBFG": ("0x5314071bba19943f58347ba5dec423e5032a6818",
          [("totalSupply","totalSupply()"),("totalMinted","totalMinted()"),("freeMinted","freeMinted()"),
           ("FREE_SUPPLY","FREE_SUPPLY()"),("saleStart","saleStart()"),
           ("saleOpen","saleOpen()"),("freeAvailable_user","freeAvailable(address)",enc_addr(USER)),
           ("balanceOf_user","balanceOf(address)",enc_addr(USER))]),
 "RESUME-BC1B": ("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053",
                 [("totalSupply","totalSupply()"),("freeCount","freeCount()"),("FREE_CAP","FREE_CAP()"),
                  ("saleStart","saleStart()"),("freeMinted_user","freeMinted(address)",enc_addr(USER)),
                  ("balanceOf_user","balanceOf(address)",enc_addr(USER))]),
 "LuckyCatch": ("0xD405C90079c594DA2456F5b37B4158A12f1382e5",
                [("totalSupply","totalSupply()"),("mintOpen","mintOpen()"),
                 ("balanceOf_user","balanceOf(address)",enc_addr(USER)),
                 ("agentFreeCount","agentFreeCount()"),("paidSold","paidSold()")]),
 "MECHA": ("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
           [("totalMinted","totalMinted()"),("freeClaimed","freeClaimed()"),("FREE_SUPPLY","FREE_SUPPLY()"),
            ("freeAvailable_user","freeAvailable(address)",enc_addr(USER)),
            ("balanceOf_user","balanceOf(address)",enc_addr(USER))]),
 "Steady": ("0x4919afF275a3cf126A8F9fD280Ae8Cd24D734cCf",
            [("totalSupply","totalSupply()"),("freeClaimed","freeClaimed()"),("FREE_SUPPLY","FREE_SUPPLY()"),
             ("mintOpen","mintOpen()"),("freeUsed_user","freeUsed(address)",enc_addr(USER)),
             ("balanceOf_user","balanceOf(address)",enc_addr(USER))]),
 "DragonAgent": ("0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6", GENERIC),
 "ObsidianGranary": ("0x11986f3DF799a28bB97921F49406a7197b1d34d2", GENERIC),
 "Stampooor": ("0x467696af8c2206B977B24081445104632dc1D459", GENERIC),
 "AgentPals": ("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", GENERIC),
 "BHTB-sale": ("0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467",
               [("totalSupply","totalSupply()"),("freeClaimed_user","freeClaimed(address)",enc_addr(USER)),
                ("freeUsed","freeUsed()"),("FREE_QUOTA","FREE_QUOTA()"),("FREE_TOKENS","FREE_TOKENS()"),
                ("balanceOf_user","balanceOf(address)",enc_addr(USER)),("mintEnd","mintEnd()")]),
 "AgentGrid-sale": ("0x651302C0043040D48EaAF85605E12F0549aD6D89",
                    [("totalSupply","totalSupply()"),("FREE_SHARES","FREE_SHARES()"),
                     ("freeSharesRemaining","freeSharesRemaining()"),("freeUsed","freeUsed()"),
                     ("freeClaimed_user","freeClaimed(address)",enc_addr(USER)),
                     ("balanceOf_user","balanceOf(address)",enc_addr(USER))]),
 "HIVE": ("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77",
          [("totalSupply","totalSupply()"),("totalMinted","totalMinted()"),("FREE_SUPPLY","FREE_SUPPLY()"),
           ("MAX_SUPPLY","MAX_SUPPLY()"),("balanceOf_user","balanceOf(address)",enc_addr(USER))]),
 "Bubblebruin": ("0xc205F8c74733D914776D66cBc4Cf10BF701D96Aa",
                 [("totalSupply","totalSupply()"),("freeClaimed","freeClaimed()"),("FREE_SUPPLY","FREE_SUPPLY()"),
                  ("mintOpen","mintOpen()"),("balanceOf_user","balanceOf(address)",enc_addr(USER))]),
 "Zapcourier": ("0x672c1dF4F7121DaCBD3504995441C47d2fAbCdDC",
                [("totalSupply","totalSupply()"),("freeClaimed","freeClaimed()"),("FREE_SUPPLY","FREE_SUPPLY()"),
                 ("mintOpen","mintOpen()"),("balanceOf_user","balanceOf(address)",enc_addr(USER))]),
 "binanceai-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
                    [("launched","launched()"),("failed","failed()"),("isRefundPhase","isRefundPhase()"),
                     ("tokenClaimed_user","tokenClaimed(address)",enc_addr(USER))]),
 "binanceai-token": ("0x209173F09aFbCA053C0de9e9763f503e9fb54a3c",
                     [("totalSupply","totalSupply()"),("balanceOf_user","balanceOf(address)",enc_addr(USER))]),
}
snap = json.load(open(BASE + "onchain-snapshot.json"))
contracts = snap.get("contracts") or {}
def find_addr(*needles):
    for name, v in contracts.items():
        if isinstance(v, dict) and v.get("address"):
            n = name.lower()
            if any(nd.lower() in n for nd in needles):
                return v["address"]
    return None
RETRY_NAMES = {"OLIVER": ["oliver"], "Cobalt": ["cobalt"], "SYNERGYPASS": ["synergy"],
               "DRAGON-0xad0d": ["dragon-0xad0d"], "AGENT-COSMOS": ["agent cosmos", "cosmos"],
               "AGENT-ID-card": ["agent id card"], "RunicKey": ["runickey", "runic"],
               "Thor": ["thor"], "Vexa": ["vexa"]}
for nm, needles in RETRY_NAMES.items():
    a = find_addr(*needles)
    if a:
        TARGETS["retry-" + nm] = (a, GENERIC)
    else:
        print(f"RETRY {nm}: address not found in snapshot", flush=True)

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
                rv = it.get("result")
                out[key] = dec_str(rv) if (key in ("name", "symbol") or key.startswith("tokenURI")) else to_int(rv)
            out["_addr"] = addr
            return name, out
        except Exception:
            continue
    return name, {"_addr": addr, "_error": "all-endpoints-failed"}

t0 = time.time()
out = {"started_wib": "2026-11-13 03:31 WIB", "block": None, "reads": {}}
try:
    res = post_rpc(EPS[0], {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
    out["block"] = int(res.get("result"), 16)
except Exception as e:
    out["block_error"] = f"{type(e).__name__}: {str(e)[:100]}"
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    for name, r in ex.map(one, TARGETS.items()):
        out["reads"][name] = r
        print(f"{name}: {json.dumps(r)}", flush=True)
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-13-0331-verify.json", "w"), indent=1)
print("ELAPSED", out["elapsed_s"], "BLOCK", out.get("block"))
