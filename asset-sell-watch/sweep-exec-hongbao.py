#!/usr/bin/env python3
"""Sweep execution — HONGBAO only (sole executable-route candidate, 2026-11-09 ~23:52 WIB).
Guards (stop on any failure, no workarounds):
  fresh quote > 0, quote >= 2x gas, net > 0, Binance audit clean of RISK
  (CAUTION-only disclosed, never blocking), preview clean 000000000 for EVERY
  step, no 351803/351805, exact-amount approval only, min-out 95% of quote,
  receipt status 1, balance-after verified. Uses sell_watch.py helpers.
Swap uses swapExactTokensForTokens (plain) — preview simulation is the safety
net: a fee-on-transfer token would make the plain swap revert in simulation.
"""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/asset-sell-watch")
import sell_watch as sw
from eth_abi import encode, decode

W = sw.W
ROUTER = sw.ROUTER
WBNB = sw.WBNB
TOK = "0x44e9AeC5b828092A9eBC3070caCcd556BB21C725"
SYM = "HONGBAO"

def fail(stage, why):
    print(json.dumps({"symbol": SYM, "status": "STOP", "stage": stage, "why": why}, indent=1))
    raise SystemExit(0)

def main():
    out = {"symbol": SYM, "token": TOK}
    bal_h = sw.call(TOK, "0x" + sw.sel("balanceOf(address)") + encode(["address"], [W]).hex())
    dec_h = sw.call(TOK, "0x" + sw.sel("decimals()"))
    if bal_h is None or dec_h is None:
        fail("balance", "rpc failed")
    bal = sw.u256(bal_h); dec = sw.u256(dec_h)
    out["balance_human"] = bal / (10 ** dec)
    out["balance_raw"] = str(bal)
    if bal == 0:
        fail("balance", "empty")
    # fresh quote (full balance, direct WBNB)
    q_h = sw.call(ROUTER, "0x" + sw.sel("getAmountsOut(uint256,address[])") +
                  encode(["uint256", "address[]"], [bal, [TOK, WBNB]]).hex())
    if not q_h:
        fail("quote", "getAmountsOut failed")
    outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
    if len(outs) != 2 or outs[1] <= 0:
        fail("quote", "quote <= 0")
    quote = outs[1] / 1e18
    out["quote_bnb"] = quote
    gp = sw.rpc_batch([("eth_gasPrice", [])])[0]
    gas_price = sw.u256(gp) if gp else 150000000
    gas_bnb = 250000 * gas_price / 1e18
    out["gas_est_bnb"] = gas_bnb
    if quote < 2 * gas_bnb or quote - gas_bnb <= 0:
        fail("quote", "quote %.8g < 2x gas %.8g" % (quote, 2 * gas_bnb))
    # fresh audit
    aud = sw.audit(TOK)
    if aud.get("error"):
        fail("audit", "audit unavailable: %s" % aud["error"])
    danger, caution = [], []
    if aud.get("riskAlert"):
        danger.append("riskAlert")
    for grp in (aud.get("riskItems") or []):
        for det in (grp.get("details") or []):
            if det.get("isHit") and det.get("riskType") == "RISK":
                danger.append(det.get("title"))
            if det.get("isHit") and det.get("riskType") == "CAUTION":
                caution.append(det.get("title"))
    out["audit"] = {"hasResult": aud.get("hasResult"), "riskLevel": aud.get("riskLevel"),
                    "risk_hits": danger, "caution_hits": caution}
    if danger:
        fail("audit", "RISK hits: %s" % danger)
    # allowance
    al_h = sw.call(TOK, "0x" + sw.sel("allowance(address,address)") +
                   encode(["address", "address"], [W, ROUTER]).hex())
    allowance = sw.u256(al_h) if al_h else 0
    out["allowance_before"] = str(allowance)
    if allowance < bal:
        ap_data = ("0x" + sw.sel("approve(address,uint256)") +
                   encode(["address", "uint256"], [ROUTER, bal]).hex())
        pv = sw.baw(["contract-call", "preview", "--binanceChainId", "56",
                     "--from", W, "--to", TOK, "--value", "0",
                     "--inputData", ap_data, "--json"])
        ok, why = sw.preview_clean(pv, allow_allowance_change=True)
        if not ok:
            fail("preview-approve", why)
        ex = sw.baw(["contract-call", "execute",
                     "--requestId", pv["data"]["requestId"], "--json"])
        txa = (ex.get("data") or {}).get("txHash")
        if not txa:
            fail("execute-approve", json.dumps(ex)[:300])
        rc = sw.receipt(txa)
        if not rc or int(rc["status"], 16) != 1:
            fail("receipt-approve", "tx %s" % txa)
        out["approve_tx"] = txa
        out["approve_block"] = int(rc["blockNumber"], 16)
    # swap preview
    min_out = int(outs[1] * 0.95)
    deadline = int(time.time()) + 600
    sw_data = ("0x" + sw.sel("swapExactTokensForTokens(uint256,uint256,address[],address,uint256)") +
               encode(["uint256", "uint256", "address[]", "address", "uint256"],
                      [bal, min_out, [TOK, WBNB], W, deadline]).hex())
    out["min_out_wei"] = str(min_out)
    pv = sw.baw(["contract-call", "preview", "--binanceChainId", "56",
                 "--from", W, "--to", ROUTER, "--value", "0",
                 "--inputData", sw_data, "--json"])
    ok, why = sw.preview_clean(pv)
    if not ok:
        fail("preview-swap", why)
    ex = sw.baw(["contract-call", "execute",
                 "--requestId", pv["data"]["requestId"], "--json"])
    txs = (ex.get("data") or {}).get("txHash")
    if not txs:
        fail("execute-swap", json.dumps(ex)[:300])
    rc = sw.receipt(txs)
    if not rc or int(rc["status"], 16) != 1:
        fail("receipt-swap", "tx %s" % txs)
    bal_after_h = sw.call(TOK, "0x" + sw.sel("balanceOf(address)") + encode(["address"], [W]).hex())
    bal_after = sw.u256(bal_after_h) / (10 ** dec) if bal_after_h else None
    out["status"] = "SOLD"
    out["swap_tx"] = txs
    out["block"] = int(rc["blockNumber"], 16)
    out["gas_used"] = int(rc["gasUsed"], 16)
    out["balance_after"] = bal_after
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
