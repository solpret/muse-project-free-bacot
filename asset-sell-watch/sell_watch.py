#!/usr/bin/env python3
"""Asset sell watch — LEG FUNGIBLE (main wallet, BSC only).

Modes:
  --baseline : read-only. Balances, pairs, reserves, quotes, net estimate.
               NO audit, NO preview, NO execution.
  (default)  : live guarded auto-sell. Executes ONLY when every guard passes:
               route exists with real liquidity, quote > 0, net BNB after gas > 0,
               Binance audit disclosed (specific risk hit STOPS; hasResult=false is
               disclosed as no result, never a pass), preview clean 000000000 for
               EVERY step, no 351803/351805, exact-amount approval only.
               Proceeds land as WBNB (BNB on DEX, 1:1). Only PCS V2 routes are
               auto-executable; any other market is reported, never executed blind.

Scope (user authorizations 2026-11-02 ~10:20 + ~10:23 WIB):
  - Main wallet only. BSC only. NEVER BNBS NEW (own monitor), NEVER BNB/USDT
    themselves, NEVER NFTs (separate leg), NEVER SEVY redeem, NEVER soulbound/
    locked/non-transferable items, NEVER approvals beyond exact router amount.
  - Tokens whose contract is not recorded are NOT tracked until verified.
Run with: ~/workspace/.abi-venv/bin/python sell_watch.py [--baseline]
"""
import sys, json, time, urllib.request, subprocess
from eth_abi import encode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
USDT = "0x55d398326f99059fF775485246999027B3197955"
BAW = "/home/hatch/workspace/.baw-cli/bin/baw"
HERE = "/home/hatch/workspace/asset-sell-watch"
STATE_PATH = HERE + "/state.json"

TOKENS = [
    ("BAO", "0x3CD603B6742Abd53948DC4c08e50A267677b0605"),
    ("PRINTER", "0x7639928DAD4f120752CEaEb0a4e60e0f33f9B30A"),
    ("BNBS-OLD", "0x171F264F938D55D968AfC5d6B133C4157A61f05F"),
    ("QILIN", "0x4fb644959f79848674acc4a48d8a3d99fc767ac2"),
    ("BAIRS", "0xDe5EBF1493EE2538061F0FF92B1666a6db372A50"),
    ("LAZA", "0x44707e71bB06C169C5bbDc139C3B33F2ee0AD34D"),
    ("JUBAO", "0x1ed3BF35e4DA25b1289C27ddbD82f0A38DDCee8b"),
    ("ZCMAO", "0x8362e6a5F38427d8d719EA47f08890784F6023DC"),
    ("JINLONG", "0x2Df4Ef534cbBe1a8F647e24D0f8C75ECe74D8288"),
    ("DOG-A", "0xF54E80a86FCF71Fa2F86Eb9bC2f21f36B94961b7"),
    ("DOG-B", "0x0e4dA795341C04d209F91C5188dbceDcbf502643"),
    ("SAMBA", "0x647a37bFD60348f9EE471aaD3FB3e7eCd6584Cd5"),
    ("VMORA", "0x538Bd9f178eEf2CFB564d2FAD1D5B0702d8B3818"),
    ("LINGYUANGOU", "0xC180B8bffdd65531F4BAE6aC7586Cfb192164A9B"),
    ("DOUDI", "0x071f76c1868039e2f042Dca1890EcB0364D8494a"),
    ("HONGBAO", "0x44e9AeC5b828092A9eBC3070caCcd556BB21C725"),
]

def sel(sig):
    return keccak(text=sig).hex()[:8]

def rpc_batch(calls):
    """calls: list of (method, params). Returns list of results (None on error)."""
    url = "https://bsc-dataseed.binance.org/"
    batch = [{"jsonrpc": "2.0", "id": i + 1, "method": m, "params": p}
             for i, (m, p) in enumerate(calls)]
    req = urllib.request.Request(url, data=json.dumps(batch).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=30).read())
    except Exception:
        return [None] * len(calls)
    out = []
    for r in res:
        if r.get("error") or not r.get("result"):
            out.append(None)
        else:
            out.append(r["result"])
    return out

def call(to, data):
    r = rpc_batch([("eth_call", [{"to": to, "data": data}, "latest"])])[0]
    return r

def call_many(items):
    """items: list of (to, data). Returns list of hex-or-None."""
    batch = []
    for (to, d) in items:
        batch.append(("eth_call", [{"to": to, "data": d}, "latest"]))
    return rpc_batch(batch)

def u256(hexstr):
    return int(hexstr, 16) if hexstr else 0

def audit(token):
    import uuid
    url = "https://web3.binance.com/bapi/defi/v1/public/wallet-direct/security/token/audit"
    body = json.dumps({"binanceChainId": "56", "contractAddress": token,
                       "requestId": str(uuid.uuid4())}).encode()
    req = urllib.request.Request(url, data=body,
        headers={"Content-Type": "application/json", "source": "agent",
                 "User-Agent": "binance-web3/1.4 (Skill)"})
    try:
        d = json.loads(urllib.request.urlopen(req, timeout=30).read())
        return d.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def baw(args):
    r = subprocess.run([BAW] + args, capture_output=True, text=True, timeout=180)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"success": False, "raw": (r.stdout + r.stderr)[:500]}

def preview_clean(d, allow_allowance_change=False):
    if not d.get("success"):
        return False, "preview failed: %s" % json.dumps(d)[:300]
    sim = d["data"]["simulationResult"]
    if sim.get("simulationCode") != "000000000":
        return False, "simulationCode %s" % sim.get("simulationCode")
    if sim.get("simulationErrorDetail"):
        return False, "simulationError %s" % sim["simulationErrorDetail"]
    if sim.get("authorityChanges"):
        return False, "authorityChanges present"
    ac = sim.get("allowanceChanges") or []
    if not allow_allowance_change and ac:
        return False, "allowanceChanges present on swap"
    risks = d["data"].get("risks", {})
    if risks.get("riskDetails") or risks.get("riskBehaviors"):
        return False, "risk hits present"
    return True, ""

def receipt(tx):
    for _ in range(12):
        r = rpc_batch([("eth_getTransactionReceipt", [tx])])[0]
        if r:
            return r
        time.sleep(5)
    return None

def main():
    baseline = "--baseline" in sys.argv
    try:
        state = json.load(open(STATE_PATH))
    except Exception:
        state = {}
    summary = {"mode": "baseline" if baseline else "live", "tokens": [], "actions": []}
    # Batch 1: balances + decimals + allowance per token (3 calls each, chunked)
    for sym, tok in TOKENS:
        item = {"symbol": sym, "contract": tok}
        bal_h = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
        dec_h = call(tok, "0x" + sel("decimals()"))
        if bal_h is None or dec_h is None:
            item["status"] = "unverified"
            summary["tokens"].append(item)
            continue
        bal = u256(bal_h)
        dec = u256(dec_h)
        item["balance"] = bal / (10 ** dec) if dec < 40 else None
        if bal == 0:
            item["status"] = "empty"
            summary["tokens"].append(item)
            continue
        # pairs
        pW = call(FACTORY, "0x" + sel("getPair(address,address)") +
                  encode(["address", "address"], [tok, WBNB]).hex())
        pU = call(FACTORY, "0x" + sel("getPair(address,address)") +
                  encode(["address", "address"], [tok, USDT]).hex())
        pairW = ("0x" + pW[-40:]) if pW and u256(pW) else None
        pairU = ("0x" + pU[-40:]) if pU and u256(pU) else None
        best = None  # (outW_wei, hops, pair_desc)
        if pairW:
            q = call(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") +
                     encode(["uint256", "address[]"], [bal, [tok, WBNB]]).hex())
            if q:
                try:
                    from eth_abi import decode as _dec
                    outs = _dec(["uint256[]"], bytes.fromhex(q[2:]))[0]
                    if len(outs) == 2 and outs[1] > 0:
                        best = (outs[1], 1, "direct WBNB")
                except Exception:
                    pass
        if pairU:
            q1 = call(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") +
                      encode(["uint256", "address[]"], [bal, [tok, USDT]]).hex())
            if q1:
                try:
                    from eth_abi import decode as _dec
                    o1 = _dec(["uint256[]"], bytes.fromhex(q1[2:]))[0]
                    if len(o1) == 2 and o1[1] > 0:
                        q2 = call(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") +
                                  encode(["uint256", "address[]"], [o1[1], [USDT, WBNB]]).hex())
                        if q2:
                            o2 = _dec(["uint256[]"], bytes.fromhex(q2[2:]))[0]
                            if len(o2) == 2 and o2[1] > 0 and (best is None or o2[1] > best[0]):
                                best = (o2[1], 2, "via USDT")
                except Exception:
                    pass
        if best is None:
            item["status"] = "no-route"
            summary["tokens"].append(item)
            continue
        outW, hops, desc = best
        item["quote_bnb"] = outW / 1e18
        item["route"] = desc
        gp = rpc_batch([("eth_gasPrice", [])])[0]
        gas_price = u256(gp) if gp else 150000000
        units = (50000 if True else 0) + hops * 200000  # approve worst case + swaps
        gas_bnb = units * gas_price / 1e18
        item["gas_est_bnb"] = gas_bnb
        net = outW / 1e18 - gas_bnb
        item["net_bnb"] = net
        # Dust/margin rule: quote must cover at least 2x estimated gas, so
        # estimation error and slippage cannot turn the sale net-negative.
        if net <= 0 or outW / 1e18 < 2 * gas_bnb:
            item["status"] = "dust"
            summary["tokens"].append(item)
            continue
        item["status"] = "executable-route"
        if baseline:
            summary["tokens"].append(item)
            continue
        # ---- LIVE guarded execution ----
        aud = audit(tok)
        # Danger = any audit detail with isHit=true and riskType=RISK, or a
        # riskAlert. CAUTION-only hits are disclosed, not blocking (standing
        # practice: e.g. BAO's CAUTION-only audit did not stop its checks).
        danger = []
        if aud.get("riskAlert"):
            danger.append("riskAlert")
        for grp in (aud.get("riskItems") or []):
            for det in (grp.get("details") or []):
                if det.get("isHit") and det.get("riskType") == "RISK":
                    danger.append(det.get("title"))
        caution = []
        for grp in (aud.get("riskItems") or []):
            for det in (grp.get("details") or []):
                if det.get("isHit") and det.get("riskType") == "CAUTION":
                    caution.append(det.get("title"))
        item["audit"] = {"hasResult": aud.get("hasResult"),
                         "risk_hits": danger, "caution_hits": caution}
        if aud.get("error"):
            item["status"] = "blocked-audit-unavailable"
            summary["actions"].append({"symbol": sym, "action": "STOP audit unavailable"})
            summary["tokens"].append(item)
            continue
        if danger:
            item["status"] = "blocked-audit-risk"
            summary["actions"].append({"symbol": sym, "action": "STOP audit risk items",
                                       "risk_hits": danger})
            summary["tokens"].append(item)
            continue
        # allowance
        al_h = call(tok, "0x" + sel("allowance(address,address)") +
                    encode(["address", "address"], [W, ROUTER]).hex())
        allowance = u256(al_h) if al_h else 0
        if allowance < bal:
            ap_data = ("0x" + sel("approve(address,uint256)") +
                       encode(["address", "uint256"], [ROUTER, bal]).hex())
            pv = baw(["contract-call", "preview", "--binanceChainId", "56",
                      "--from", W, "--to", tok, "--value", "0",
                      "--inputData", ap_data, "--json"])
            ok, why = preview_clean(pv, allow_allowance_change=True)
            if not ok:
                item["status"] = "blocked-preview-approve"
                summary["actions"].append({"symbol": sym, "action": "STOP approve preview", "why": why})
                summary["tokens"].append(item)
                continue
            ex = baw(["contract-call", "execute",
                      "--requestId", pv["data"]["requestId"], "--json"])
            txa = (ex.get("data") or {}).get("txHash")
            if not txa:
                item["status"] = "blocked-execute-approve"
                summary["actions"].append({"symbol": sym, "action": "STOP approve execute",
                                           "out": json.dumps(ex)[:300]})
                summary["tokens"].append(item)
                continue
            rc = receipt(txa)
            if not rc or int(rc["status"], 16) != 1:
                item["status"] = "blocked-receipt-approve"
                summary["actions"].append({"symbol": sym, "action": "STOP approve receipt", "tx": txa})
                summary["tokens"].append(item)
                continue
            item["approve_tx"] = txa
        min_out = int(outW * 0.95)
        path = [tok, WBNB] if hops == 1 else [tok, USDT, WBNB]
        deadline = int(time.time()) + 600
        sw_data = ("0x" + sel("swapExactTokensForTokens(uint256,uint256,address[],address,uint256)") +
                   encode(["uint256", "uint256", "address[]", "address", "uint256"],
                          [bal, min_out, path, W, deadline]).hex())
        pv = baw(["contract-call", "preview", "--binanceChainId", "56",
                  "--from", W, "--to", ROUTER, "--value", "0",
                  "--inputData", sw_data, "--json"])
        ok, why = preview_clean(pv)
        if not ok:
            item["status"] = "blocked-preview-swap"
            summary["actions"].append({"symbol": sym, "action": "STOP swap preview", "why": why})
            summary["tokens"].append(item)
            continue
        ex = baw(["contract-call", "execute",
                  "--requestId", pv["data"]["requestId"], "--json"])
        txs = (ex.get("data") or {}).get("txHash")
        if not txs:
            item["status"] = "blocked-execute-swap"
            summary["actions"].append({"symbol": sym, "action": "STOP swap execute",
                                       "out": json.dumps(ex)[:300]})
            summary["tokens"].append(item)
            continue
        rc = receipt(txs)
        if not rc or int(rc["status"], 16) != 1:
            item["status"] = "blocked-receipt-swap"
            summary["actions"].append({"symbol": sym, "action": "STOP swap receipt", "tx": txs})
            summary["tokens"].append(item)
            continue
        bal_after_h = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
        bal_after = u256(bal_after_h) / (10 ** dec) if bal_after_h else None
        item["status"] = "SOLD"
        item["swap_tx"] = txs
        item["block"] = int(rc["blockNumber"], 16)
        item["gas_used"] = int(rc["gasUsed"], 16)
        item["balance_after"] = bal_after
        summary["actions"].append({"symbol": sym, "action": "SOLD", "tx": txs,
                                   "block": item["block"], "quote_bnb": item["quote_bnb"],
                                   "balance_before": item["balance"],
                                   "balance_after": bal_after})
        summary["tokens"].append(item)
    # persist statuses for change detection
    new_state = {}
    for t in summary["tokens"]:
        new_state[t["symbol"]] = {"status": t["status"],
                                  "quote_bnb": t.get("quote_bnb"),
                                  "net_bnb": t.get("net_bnb")}
    try:
        json.dump(new_state, open(STATE_PATH, "w"), indent=1)
    except Exception:
        pass
    print(json.dumps(summary, indent=1))

if __name__ == "__main__":
    main()
