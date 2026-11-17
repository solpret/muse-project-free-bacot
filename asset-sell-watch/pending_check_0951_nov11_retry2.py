#!/usr/bin/env python3
"""Publicnode-only retry for pending-swap-watch run 09:51 Nov 11.
RPCs degraded ~10:05 WIB: dataseeds hang/empty, publicnode responds but
slow (~15s). Single endpoint, curl -m 30, 3 threads, incremental merge.
Retries every entry still unverified in the 09:51 stdout (status
rpc_failed_balance, or no_pair where a pair existed at 08:51).
Read-only."""
import json, subprocess, threading
from concurrent.futures import ThreadPoolExecutor
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
URL = "https://bsc.publicnode.com/"
PATH = "/home/hatch/workspace/asset-sell-watch/pending_check_0951_nov11_stdout.json"
LOCK = threading.Lock()

def sel(sig):
    return keccak(text=sig).hex()[:8]

def call(to, data, timeout=30):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": to, "data": data}, "latest"]})
    try:
        p = subprocess.run(["curl", "-s", "-m", str(timeout), "-X", "POST",
                            "-H", "Content-Type: application/json",
                            "-d", body, URL],
                           capture_output=True, text=True, timeout=timeout + 5)
    except Exception as e:
        return None, str(e)
    try:
        res = json.loads(p.stdout)
    except Exception:
        return None, "bad json: " + p.stdout[:120]
    if isinstance(res, dict) and (res.get("error") or not res.get("result")):
        return None, str(res.get("error"))
    return res.get("result"), None

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

def check(src, gas_est):
    tok = src["token"]; sym = src["symbol"]
    item = {"symbol": sym, "token": tok, "registered_amount_human": src.get("amount_human"),
            "amount_to_sell_raw": src.get("amount_to_sell_raw"),
            "reason_prev": src.get("reason"), "retry": True, "retry_publicnode30": True}
    bal_h, bal_err = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
    dec_h, _ = call(tok, "0x" + sel("decimals()"))
    if bal_h is None:
        item["status"] = "rpc_failed_balance"; item["balance_error"] = bal_err
        return item
    bal = u256(bal_h); dec = u256(dec_h) if dec_h else 18
    item["balance_raw"] = str(bal); item["balance_human"] = bal / (10**dec) if dec < 40 else None
    item["decimals"] = dec; item["balance_endpoint"] = URL
    if bal == 0:
        item["status"] = "empty"; return item
    pair_h, _ = call(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex())
    pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
    item["pair_wbnb"] = pair; item["pair_endpoint"] = URL
    if not pair:
        item["status"] = "no_pair"; return item
    t0_h, _ = call(pair, "0x" + sel("token0()"))
    t1_h, _ = call(pair, "0x" + sel("token1()"))
    res_h, res_err = call(pair, "0x" + sel("getReserves()"))
    if res_h:
        try:
            r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
            item["reserves"] = [str(r0), str(r1)]
            item["token0"] = ("0x" + t0_h[-40:]) if t0_h else None
            item["token1"] = ("0x" + t1_h[-40:]) if t1_h else None
            if r0 == 0 or r1 == 0:
                item["status"] = "pair_empty"; return item
        except Exception as ex:
            item["reserves_error"] = str(ex)
    else:
        item["reserves_error"] = res_err
    sell_amt = int(src["amount_to_sell_raw"]) if src.get("amount_to_sell_raw") else bal
    item["sell_amount_raw"] = str(sell_amt)
    q_h, q_err = call(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell_amt, [tok, WBNB]]).hex())
    if q_h:
        try:
            outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
            item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
            item["quote_raw"] = str(outs[1]) if len(outs) == 2 else None
            item["quote_endpoint"] = URL
        except Exception as ex:
            item["quote_error"] = str(ex)
    else:
        item["quote_error"] = q_err
    if item.get("quote_bnb") is not None:
        q = item["quote_bnb"]
        item["quote_ge_2x_gas"] = (gas_est is not None and q >= 2 * gas_est)
        item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
    else:
        item["status"] = "no_quote"
    sc = src.get("sale_contract")
    if sc:
        lh, _ = call(sc, "0x" + sel("launched()"))
        item["sale_contract"] = sc; item["launched_raw"] = lh
        if lh is not None:
            try:
                item["launched"] = decode(["bool"], bytes.fromhex(lh[2:]))[0]
            except Exception:
                item["launched"] = None
    return item

def main():
    out = json.load(open(PATH))
    data = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))
    by_sym = {e["symbol"]: e for e in data["entries"]}
    gas_est = out.get("gas_est_300k_bnb")
    idx = {e["symbol"]: i for i, e in enumerate(out["entries"])}
    syms = [e["symbol"] for e in out["entries"]
            if e.get("status") == "rpc_failed_balance"
            or e["symbol"] in ("YYDS", "BITCAT", "JINMA", "LUCKY777")]
    print("retrying:", syms, flush=True)
    def work(sym):
        item = check(by_sym[sym], gas_est)
        with LOCK:
            out["entries"][idx[sym]] = item
            json.dump(out, open(PATH, "w"), indent=1)
        print(sym, "->", item.get("status"), "| bal:", item.get("balance_human"),
              "| pair:", item.get("pair_wbnb"), "| reserves:", item.get("reserves"),
              "| quote:", item.get("quote_bnb"), "| err:", item.get("balance_error"), flush=True)
        return item
    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(work, syms))
    print("DONE")

if __name__ == "__main__":
    main()
