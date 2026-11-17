#!/usr/bin/env python3
"""Verify for free-mint-search run 2026-11-13 07:01 WIB.
ONE JSON-RPC batch per contract (all views in a single POST), contracts in
parallel (4 workers), per-item error -> None. Read-only; writes
run-2026-11-13-0701-verify.json. No preview/mint.
Focus: decision items only (hot-leg 0659 re-read the 43-target leg4 ~10 min
ago). JNTM gate-L pending; Agent Muse merge; OBFG/Sol/NOTV/Agentx; PX24-group
age re-verification; LuckyCatch final read before snapshot removal; binanceai
track-B re-check.
"""
import json, subprocess, time, concurrent.futures
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENT_ID = 107187496765866644729837695198686237165740365523485558112864918211974996443404
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def words(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
    except Exception:
        return None
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def read_one(name, addr, views):
    calls = []
    for i, (key, sig, *rest) in enumerate(views):
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": sel(sig) + (rest[0] if rest else "")}, "latest"]})
    res = {"address": addr, "views": {}, "summary": {}}
    for ep in EPS:
        try:
            r = post_rpc(ep, calls)
            if not isinstance(r, list) or len(r) != len(calls):
                continue
            ok = True
            for it, (key, sig, *rest) in zip(r, views):
                if not isinstance(it, dict) or "error" in it or not it.get("result") or it["result"] == "0x":
                    res["views"][key] = None; continue
                w = words(it["result"])
                res["views"][key] = w[0] if w is not None and len(w) == 1 else w
            res["endpoint"] = ep
            return res
        except Exception as e:
            res.setdefault("errors", []).append(str(e)[:80])
    return res
GENERIC_NFT = [("totalSupply", "totalSupply()"), ("totalMinted", "totalMinted()"),
    ("freeMinted", "freeMinted()"), ("freeClaimed", "freeClaimed()"),
    ("FREE_SUPPLY", "FREE_SUPPLY()"), ("FREE_CAP", "FREE_CAP()"),
    ("MAX_SUPPLY", "MAX_SUPPLY()"), ("mintOpen", "mintOpen()"),
    ("mintStart", "mintStart()"), ("mintOpensAt", "mintOpensAt()"),
    ("name", "name()"), ("symbol", "symbol()"),
    ("balanceOf_user", "balanceOf(address)", enc_addr(USER)),
    ("costOf_user_1", "costOf(address,uint256)", enc_addr(USER) + enc_u(1))]
TARGETS = {
 "JNTM": ("0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b",
    [("freeClaimed", "freeClaimed()"), ("freeLeft", "freeLeft()"),
     ("FREE_LOTS_CAP", "FREE_LOTS_CAP()"), ("TOTAL_LOTS", "TOTAL_LOTS()"),
     ("totalMinted", "totalMinted()"), ("paidMinted", "paidMinted()"),
     ("mintStart", "mintStart()"), ("opened", "opened()"), ("openTime", "openTime()"),
     ("registry", "registry()"), ("token", "token()"),
     ("freeClaimedByAgent_user", "freeClaimedByAgent(uint256)", enc_u(AGENT_ID)),
     ("mintedByAgent_user", "mintedByAgent(uint256)", enc_u(AGENT_ID)),
     ("mintedLots_user", "mintedLots(address)", enc_addr(USER))]),
 "AgentMuse": ("0x779fa133848d23052B7345F63B3b2E5309cd13ed",
    [("freeClaimed", "freeClaimed()"), ("FREE_SHARES", "FREE_SHARES()"),
     ("bookedTotal", "bookedTotal()"), ("openedAt", "openedAt()"),
     ("DOORS_OPEN", "DOORS_OPEN()"), ("FREE_OSK", "FREE_OSK()"),
     ("bookedOf_user", "bookedOf(address)", enc_addr(USER)),
     ("canBook_user", "canBook(address)", enc_addr(USER)),
     ("agentIdOf_user", "agentIdOf(address)", enc_addr(USER)),
     ("progress", "progress()")]),
 "OBFG": ("0x5314071bba19943f58347ba5dec423e5032a6818",
    [("totalSupply", "totalSupply()"), ("totalMinted", "totalMinted()"),
     ("freeMinted", "freeMinted()"), ("FREE_SUPPLY", "FREE_SUPPLY()"),
     ("saleStart", "saleStart()"), ("saleOpen", "saleOpen()"),
     ("freeAvailable_user", "freeAvailable(address)", enc_addr(USER)),
     ("balanceOf_user", "balanceOf(address)", enc_addr(USER))]),
 "SolNFT": ("0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606",
    [("totalMinted", "totalMinted()"), ("freeMinted", "freeMinted()"),
     ("FREE_CAP", "FREE_CAP()"), ("mintOpen", "mintOpen()"),
     ("freeClaimed_user", "freeClaimed(address)", enc_addr(USER)),
     ("balanceOf_user", "balanceOf(address)", enc_addr(USER))]),
 "NOTV": ("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01",
    [("totalSupply", "totalSupply()"), ("totalMinted", "totalMinted()"),
     ("FREE_SHARES", "FREE_SHARES()"), ("freeStart", "freeStart()")]),
 "Agentx": ("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
    [("totalMinted", "totalMinted()"), ("freeMinted", "freeMinted()"),
     ("FREE_CAP", "FREE_CAP()"), ("MAX_SUPPLY", "MAX_SUPPLY()"),
     ("mintOpen", "mintOpen()"),
     ("freeClaimed_user", "freeClaimed(address)", enc_addr(USER)),
     ("balanceOf_user", "balanceOf(address)", enc_addr(USER))]),
 "PX24": ("0xe712510fcb27935e657e41ebb97982d6b123136c", GENERIC_NFT),
 "SKRR": ("0x9081f02876c173d0c69f042959cfd0d61c668b17", GENERIC_NFT),
 "ME30": ("0xa545c8726bcf4acf840dac521b369911fe2abc8d", GENERIC_NFT),
 "CY24": ("0x731d879ee2cd4bbf32efef9178d51d5c1441d052", GENERIC_NFT),
 "MECHA": ("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
    [("totalMinted", "totalMinted()"), ("freeClaimed", "freeClaimed()"),
     ("FREE_SUPPLY", "FREE_SUPPLY()")]),
 "Pickgrid": ("0x7f541bcc33abed0e64455565da723e949c6f76f0",
    [("freeMinted", "freeMinted()"), ("FREE_CAP", "FREE_CAP()"),
     ("totalMinted", "totalMinted()")]),
 "HIVE": ("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77",
    [("totalSupply", "totalSupply()"),
     ("balanceOf_user", "balanceOf(address)", enc_addr(USER))]),
 "LuckyCatch": ("0xD405C90079c594DA2456F5b37B4158A12f1382e5",
    [("totalSupply", "totalSupply()"), ("mintOpen", "mintOpen()"),
     ("agentFreeCount", "agentFreeCount()"), ("paidSold", "paidSold()"),
     ("balanceOf_user", "balanceOf(address)", enc_addr(USER))]),
 "BinanceAI-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
    [("launched", "launched()"),
     ("tokenClaimed_user", "tokenClaimed(address)", enc_addr(USER)),
     ("claimable_user", "claimable(address)", enc_addr(USER))]),
}
def main():
    t0 = time.time()
    out = {"started_wib": "2026-11-13T07:01+07:00", "reads": {}}
    try:
        r = post_rpc(EPS[0], {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
        out["block"] = int(r.get("result"), 16)
    except Exception as e:
        out["block_error"] = str(e)[:100]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(read_one, n, a, v): n for n, (a, v) in TARGETS.items()}
        for f in concurrent.futures.as_completed(futs):
            n = futs[f]
            try:
                out["reads"][n] = f.result()
            except Exception as e:
                out["reads"][n] = {"address": TARGETS[n][0], "error": str(e)[:120]}
    # summaries: copy non-null views
    for n, r in out["reads"].items():
        if isinstance(r, dict):
            r["summary"] = {k: v for k, v in r.get("views", {}).items() if v is not None}
    out["elapsed_s"] = round(time.time() - t0, 1)
    print(json.dumps(out, indent=1))
    json.dump(out, open(BASE + "run-2026-11-13-0701-verify.json", "w"), indent=1)
if __name__ == "__main__":
    main()
