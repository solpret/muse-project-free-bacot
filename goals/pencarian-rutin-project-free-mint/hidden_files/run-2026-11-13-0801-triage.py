#!/usr/bin/env python3
"""Triage for free-mint-search run 2026-11-13 08:01 WIB (stage 2).
One JSON-RPC batch per contract, parallel. Read-only; writes
run-2026-11-13-0801-triage.json. No preview/mint.
Targets: 0x70Fd (OUTY-style, Sourcify-new 08:25 WIB), 0x4158 Lumen Findings
(AgentLabs-style, Sourcify-new 08:05 WIB), Zero 0x89B3 extras
(freeClaimed/mintsBy/costOf/tokenURI-1), AgentLabs retry (specimensOf etc.),
getCode for 2 Boltbook 'new' addresses (suspected tx hashes).
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
def get_code(addr):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [addr, "latest"]}, timeout=15)
            code = r.get("result", "")
            return {"address": addr, "code_len": (len(code) - 2) // 2 if code.startswith("0x") else -1,
                    "endpoint": ep}
        except Exception as e:
            continue
    return {"address": addr, "code_len": None, "error": "all endpoints failed"}
TARGETS = {
 "New70Fd": ("0x70FdD1a7f382893708d00fC2eF9C38cAe7DEC92B",
    [("name", "name()"), ("symbol", "symbol()"), ("minted", "minted()"),
     ("freeSold", "freeSold()"), ("paidSold", "paidSold()"),
     ("FREE_SUPPLY", "FREE_SUPPLY()"), ("PAID_CAP", "PAID_CAP()"),
     ("START", "START()"), ("FREE_END", "FREE_END()"), ("FREE_FEE", "FREE_FEE()"),
     ("PRICE", "PRICE()"), ("phase", "phase()"), ("freeOpen", "freeOpen()"),
     ("paidOpen", "paidOpen()"), ("REGISTRY", "REGISTRY()"),
     ("freeQuotaOf_user", "freeQuotaOf(address)", enc_addr(USER)),
     ("quotaOf_user", "quotaOf(address)", enc_addr(USER)),
     ("freeByAgent_user", "freeByAgent(uint256)", enc_u(AGENT_ID)),
     ("balanceOf_user", "balanceOf(address)", enc_addr(USER))]),
 "LumenFindings": ("0x4158B701EaA30E8FaDBaA526F70780A38318c1C4",
    [("name", "name()"), ("symbol", "symbol()"),
     ("totalSpecimens", "totalSpecimens()"), ("currentExperiment", "currentExperiment()"),
     ("genesisStart", "genesisStart()"), ("experimentEnd", "experimentEnd()"),
     ("experimentStart", "experimentStart()"),
     ("specimensOf_user", "specimensOf(address)", enc_addr(USER)),
     ("priceFor_user", "priceFor(address)", enc_addr(USER)),
     ("holdsAgentId_user", "holdsAgentId(address)", enc_addr(USER)),
     ("balanceOf_user", "balanceOf(address)", enc_addr(USER)),
     ("genesisOpen", "genesisOpen()"), ("isSealed", "isSealed()"),
     ("specimensInExperiment", "specimensInExperiment(uint256)", enc_u(1))]),
 "Zero-extras": ("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647",
    [("freeClaimed_user", "freeClaimed(address)", enc_addr(USER)),
     ("mintsBy_user", "mintsBy(address)", enc_addr(USER)),
     ("costOf_user_1", "costOf(address,uint256)", enc_addr(USER) + enc_u(1)),
     ("tokenURI_1", "tokenURI(uint256)", enc_u(1)),
     ("price", "price()"), ("MAX_PER_WALLET", "MAX_PER_WALLET()")]),
 "AgentLabs-retry": ("0x639329f5dc4317c44D9Fed961a1217ba845012F7",
    [("totalSupply", "totalSupply()"), ("totalSpecimens", "totalSpecimens()"),
     ("participants", "participants()"),
     ("specimensOf_user", "specimensOf(address)", enc_addr(USER)),
     ("isSealed", "isSealed()"), ("experimentEnd", "experimentEnd()")]),
}
def main():
    t0 = time.time()
    out = {"started_wib": "2026-11-13T08:01+07:00", "reads": {}, "codes": {}}
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
    for n, r in out["reads"].items():
        if isinstance(r, dict):
            r["summary"] = {k: v for k, v in r.get("views", {}).items() if v is not None}
    for a in ["0x654c2ac4fd3e17195ad7924a905f39bd827408e1", "0xdfc4879a5b39fcb5febbdc986a0d4b026e0614f7"]:
        out["codes"][a] = get_code(a)
    out["elapsed_s"] = round(time.time() - t0, 1)
    print(json.dumps(out, indent=1))
    json.dump(out, open(BASE + "run-2026-11-13-0801-triage.json", "w"), indent=1)
if __name__ == "__main__":
    main()
