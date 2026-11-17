#!/usr/bin/env python3
"""Verify for free-mint-search run 2026-11-13 00:31 WIB.
ONE JSON-RPC batch per contract (all views in a single POST), contracts run
in parallel (4 workers), per-item error -> None (a reverting view must not
kill the whole batch). Read-only; writes run-2026-11-13-0031-verify.json.
No preview/mint."""
import json, subprocess, time, concurrent.futures
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def read_contract(addr, views):
    """One batch POST per contract; per-item error -> None."""
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            return {key: (None if (isinstance(it, dict) and "error" in it)
                          else (to_int(it.get("result")) if isinstance(it, dict) else None))
                    for it, key in zip(res, keys)}
        except Exception:
            continue
    return {"_error": "all-endpoints-failed"}

GENERIC = ["totalSupply()", "totalMinted()", "freeMinted()", "freeClaimed()",
           "FREE_SUPPLY()", "FREE_CAP()", "mintOpen()", "mintOpensAt()",
           "balanceOf(address)", "freeClaimed(address)", "freeAvailable(address)"]

TARGETS = {
    "SolNFT": ("0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606",
               ["totalMinted()", "freeMinted()", "FREE_CAP()", "mintOpen()", "mintOpensAt()",
                "freeClaimed(address)", "balanceOf(address)"]),
    "AgcNFT": ("0xdAc222886b887fC5b6262889B189B8eb57e99794",
               ["totalMinted()", "freeMinted()", "FREE_CAP()", "mintOpen()", "mintOpensAt()",
                "freeClaimed(address)", "balanceOf(address)"]),
    "OBFG": ("0x5314071bba19943f58347ba5dec423e5032a6818",
             ["totalSupply()", "totalMinted()", "freeMinted()", "FREE_SUPPLY()", "saleStart()",
              "saleOpen()", "freeAvailable(address)", "balanceOf(address)"]),
    "RESUME-BC1B": ("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053",
                    ["totalSupply()", "freeCount()", "FREE_CAP()", "saleStart()",
                     "freeMinted(address)", "balanceOf(address)"]),
    "LuckyCatch": ("0xD405C90079c594DA2456F5b37B4158A12f1382e5",
                   ["totalSupply()", "mintOpen()", "balanceOf(address)",
                    "agentFreeCount()", "paidSold()"]),
    "MECHA": ("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
              ["totalMinted()", "freeClaimed()", "FREE_SUPPLY()", "freeAvailable(address)",
               "balanceOf(address)"]),
    "Steady": ("0x4919afF275a3cf126A8F9fD280Ae8Cd24D734cCf",
               ["totalSupply()", "freeClaimed()", "FREE_SUPPLY()", "mintOpen()",
                "freeUsed(address)", "balanceOf(address)"]),
    "DragonAgent": ("0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6", GENERIC),
    "ObsidianGranary": ("0x11986f3DF799a28bB97921F49406a7197b1d34d2", GENERIC),
    "Stampooor": ("0x467696af8c2206B977B24081445104632dc1D459", GENERIC),
    "AgentPals": ("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", GENERIC),
    "BHTB-sale": ("0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467",
                  ["totalSupply()", "freeClaimed(address)", "freeUsed()", "FREE_QUOTA()",
                   "FREE_TOKENS()", "balanceOf(address)", "mintEnd()"]),
    "AgentGrid-sale": ("0x651302C0043040D48EaAF85605E12F0549aD6D89",
                       ["totalSupply()", "FREE_SHARES()", "freeSharesRemaining()", "freeUsed()",
                        "freeClaimed(address)", "balanceOf(address)"]),
    "binanceai-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
                       ["launched()", "failed()", "isRefundPhase()", "tokenClaimed(address)"]),
    "binanceai-token": ("0x209173F09aFbCA053C0de9e9763f503e9fb54a3c",
                        ["totalSupply()", "balanceOf(address)"]),
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
RETRY_NAMES = {
    "OLIVER": ["oliver"],
    "Cobalt": ["cobalt"],
    "DACIT": ["dacit"],
    "SYNERGYPASS": ["synergy"],
    "DRAGON-0xad0d": ["dragon-0xad0d"],
    "AGENT-COSMOS": ["agent cosmos", "cosmos"],
    "AGENT-ID-card": ["agent id card"],
    "RunicKey": ["runickey", "runic"],
    "Thor": ["thor"],
    "Vexa": ["vexa"],
    "ROBO": ["robo"],
}
for nm, needles in RETRY_NAMES.items():
    a = find_addr(*needles)
    if a:
        TARGETS["retry-" + nm] = (a, GENERIC)
    else:
        print(f"RETRY {nm}: address not found in snapshot", flush=True)

def one(name_addr):
    name, (addr, views) = name_addr
    t1 = time.time()
    r = read_contract(addr, views)
    r["_addr"] = addr
    r["_elapsed_s"] = round(time.time() - t1, 1)
    return name, r

out = {"started_wib": "2026-11-13 00:31 WIB", "block": None, "reads": {}}
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
json.dump(out, open(BASE + "run-2026-11-13-0031-verify.json", "w"), indent=1)
print("ELAPSED", out["elapsed_s"], "BLOCK", out.get("block"))
