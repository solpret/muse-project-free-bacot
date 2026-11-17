#!/usr/bin/env python3
"""pending-coin-swap-watch run 2026-11-12 17:51 WIB (fast batched retry).
Read-only: balanceOf (agent wallet 0xeb23), PCS V2 getPair, reserves,
getAmountsOut, gas price, sale-state spot checks. All calls are sent as
single JSON-RPC batches per phase to avoid per-call endpoint timeouts."""
import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"

def sel(sig):
    return keccak(text=sig).hex()[:8]

ENDPOINTS = ["https://bsc-dataseed1.binance.org/", "https://bsc-dataseed3.binance.org/",
             "https://bsc.publicnode.com", "https://bsc-rpc.publicnode.com",
             "https://bsc-dataseed.binance.org/", "https://bsc-dataseed2.binance.org/",
             "https://bsc-dataseed4.binance.org/"]

def _post_batch(url, batch, timeout=15):
    req = urllib.request.Request(url, data=json.dumps(batch).encode(),
                                 headers={"Content-Type": "application/json"})
    res = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    if isinstance(res, dict):
        raise RuntimeError("endpoint error: " + str(res)[:200])
    return res

def rpc_batch(calls, timeout=15):
    """calls: list of (method, params). Chunked into batches of 10; each chunk
    tries endpoints in order. Returns list of results (None on error)."""
    out = [None] * len(calls)
    last_err = None
    for start in range(0, len(calls), 10):
        chunk = calls[start:start + 10]
        batch = [{"jsonrpc": "2.0", "id": i + 1, "method": m, "params": p}
                 for i, (m, p) in enumerate(chunk)]
        done = False
        for url in ENDPOINTS:
            try:
                res = _post_batch(url, batch, timeout)
                break
            except Exception as e:
                last_err = str(e); res = None
        if res is None:
            continue
        by_id = {}
        for r in res:
            if isinstance(r, dict):
                by_id[r.get("id")] = None if (r.get("error") or not r.get("result")) else r.get("result")
        for i in range(len(chunk)):
            out[start + i] = by_id.get(i + 1)
    return out, last_err

def call(to, data):
    r, _ = rpc_batch([("eth_call", [{"to": to, "data": data}, "latest"])])
    return r[0]

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

ENTRIES = [
    ("POA", "0x21bc810818d9c9c767ba73c543f67a989fb5a543", 18, 28000000000000000000000, None),
    ("BNBbaby", "0xd0079025a9bb66a7a1de991de2e4326faba35729", 18, None, None),
    ("PATCH", "0xBbA053567846842F95C060867a5C9eb6b3983c80", 18, None, None),
    ("QAGENT", "0x25e915EEE91411b0AC3273531dbaDc34e0EAA5eB", 18, None, None),
    ("YYDS", "0xd23be069c3c3a7f631af52584a16a9e46bb41da1", 18, None, "0xD15c928B7b777CaC7d613FE840C6eC3dE8e4EdDA"),
    ("币安加油", "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f", 18, 50000000000000000000000000, "0xc939e2b49eea548c4539e45b4e355c2b2aa464d6"),
    ("PACTURE", "0x10b80088fDAf9363d83671BE66b64f231f9e92f6", 18, 10000000000000000000000000, None),
    ("ORBITA", "0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709", 18, 1000000000000000000000000, None),
    ("WW3", "0xf62628D99B28535ee593Ab5D6dFE7D914f5edca0", 18, 90000000000000000000000, None),
    ("POSTAGE", "0x6C310EABEdFD4eEd6148bf2C07241FB45a52FB42", 18, 10000000000000000000000, None),
    ("MALTA", "0x728095Ab0BD71636Db5DA4E2A6d7f5cc73729fc0", 18, 1000000000000000000000000, None),
    ("JINMA", "0xe4517E6718b24D5725956ac7A90686592a7b1539", 18, 50000000000000000000000000, "0xaa91fd1b1fc70888f5df17784720b752472e99da"),
    ("THYRK", "0x3b8747D067B2Ed8565330667128260C2a4954300", 18, 20000000000000000000, None),
    ("BITCAT", "0x8708EE82fa34c58431532323530592ee3953e9d5", 9, 37777777600000000000, "0x8dD64bb9F614D58716eB0e343e1F794B2E7A04f4"),
    ("LUCKY777", "0xc6D4ec8CB889aFBa9f251606001457644E260f7D", 18, 50000000000000000000000000, "0x81afde1cddf0d277580b8e524361e0a7ea2983c6"),
    ("WNO", "0x8C969a4CD49E4774908e667702C3d7C3ece164D0", 18, 1000000000000000000000000, None),
    ("AMBR", "0x88B06f59BdB54039AEBf1d308d8B9181a90385c1", 18, 10000000000000000000000, None),
    ("CSAGENT", "0xeD290fA2e34233d0ee97eA95C2a34E770A9DA45D", 18, 100000000000000000000000, "0x3020220Ca11BaE3F027C0DC8A3b8Bb73D5b55A00"),
    ("CHEEMSA", "0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2", 18, 5000000000000000000000000, None),
    ("NEB", "0xf08ac9c91dcfc5b74eae6c87e744cfefe0d32a68", 18, 1000000000000000000000, None),
]

def main():
    # Phase 1: one batch — gasPrice + balanceOf x20 + getPair x20
    calls = [("eth_gasPrice", [])]
    for sym, tok, dec, amt, pk in ENTRIES:
        calls.append(("eth_call", [{"to": tok, "data": "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex()}, "latest"]))
    for sym, tok, dec, amt, pk in ENTRIES:
        calls.append(("eth_call", [{"to": FACTORY, "data": "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex()}, "latest"]))
    res, err = rpc_batch(calls)
    gas_price = u256(res[0]) if res and res[0] else None
    gas_est = (gas_price * 300000 / 1e18) if gas_price else None
    out = {"run": "2026-11-12 17:51 WIB", "gas_price_gwei": (gas_price/1e9 if gas_price else None),
           "gas_est_300k_bnb": gas_est, "phase1_error": err, "entries": []}
    items = []
    for i, (sym, tok, dec, amt, pk) in enumerate(ENTRIES):
        item = {"symbol": sym, "token": tok}
        bal_h = res[1 + i]
        if bal_h is None:
            item["status"] = "rpc_failed_balance"; items.append(item); continue
        bal = u256(bal_h)
        item["balance_raw"] = str(bal); item["balance_human"] = bal / (10**dec)
        if bal == 0:
            item["status"] = "empty"; items.append(item); continue
        pair_h = res[1 + len(ENTRIES) + i]
        pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
        if not pair:
            pair = pk
        item["pair_wbnb"] = pair
        if not pair:
            item["status"] = "no_pair"; items.append(item); continue
        items.append(item)
    # Phase 2: reserves for all entries that have a pair
    need_res = [it for it in items if it.get("pair_wbnb") and it.get("status") is None]
    if need_res:
        rcalls = [("eth_call", [{"to": it["pair_wbnb"], "data": "0x" + sel("getReserves()")}, "latest"]) for it in need_res]
        rres, rerr = rpc_batch(rcalls)
        out["phase2_error"] = rerr
        for it, rh in zip(need_res, rres):
            if rh:
                try:
                    r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(rh[2:]))
                    it["reserves"] = [str(r0), str(r1)]
                    if r0 == 0 or r1 == 0:
                        it["status"] = "pair_empty"
                except Exception as ex:
                    it["reserves_error"] = str(ex)
            else:
                it["status"] = "rpc_failed_reserves"
    # Phase 3: quotes for entries with non-empty reserves
    need_q = [it for it in items if it.get("status") is None and it.get("reserves")]
    if need_q:
        qcalls = []
        for it in need_q:
            idx = [e[0] for e in ENTRIES].index(it["symbol"])
            sym, tok, dec, amt, pk = ENTRIES[idx]
            bal = u256("0x" + format(int(it["balance_raw"]), "x")) if False else int(it["balance_raw"])
            sell_amt = amt if amt is not None else bal
            it["sell_amount_raw"] = str(sell_amt)
            qcalls.append(("eth_call", [{"to": ROUTER, "data": "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell_amt, [tok, WBNB]]).hex()}, "latest"]))
        qres, qerr = rpc_batch(qcalls)
        out["phase3_error"] = qerr
        for it, qh in zip(need_q, qres):
            if qh:
                try:
                    outs = decode(["uint256[]"], bytes.fromhex(qh[2:]))[0]
                    it["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
                except Exception as ex:
                    it["quote_error"] = str(ex)
            if it.get("quote_bnb") is not None:
                q = it["quote_bnb"]
                it["quote_ge_2x_gas"] = (gas_est is not None and q >= 2 * gas_est)
                it["status"] = "executable_candidate" if it["quote_ge_2x_gas"] else "quote_dust"
            else:
                it["status"] = "no_quote"
    out["entries"] = items
    # Sale-state spot checks (best effort; failed read = null, NOT false).
    # CSAGENT: sale contract 0xF27519dE... (NOT the pair) holds opened()/floor
    # state; deadline floor 3.334 paid shares = 2026-11-12 17:04:36 WIB.
    sale_checks = {}
    # CSAGENT floor deadline 2026-11-12 17:04:36 WIB has passed (now 17:51);
    # probe refund/failed-phase state as well as opened/paidSold. A failed
    # read returns None (NOT false) — only a decoded value counts.
    for label, addr, sig in [
        ("CSAGENT_sale_opened", "0xF27519dE8268a07d3A79415112F56D11258FA91e", "opened()"),
        ("CSAGENT_sale_paidSold", "0xF27519dE8268a07d3A79415112F56D11258FA91e", "paidSold()"),
        ("CSAGENT_sale_totalPaidSold", "0xF27519dE8268a07d3A79415112F56D11258FA91e", "totalPaidSold()"),
        ("CSAGENT_sale_phase", "0xF27519dE8268a07d3A79415112F56D11258FA91e", "phase()"),
        ("CSAGENT_sale_launched", "0xF27519dE8268a07d3A79415112F56D11258FA91e", "launched()"),
        ("CSAGENT_sale_refundEnabled", "0xF27519dE8268a07d3A79415112F56D11258FA91e", "refundEnabled()"),
        ("CSAGENT_sale_refundsEnabled", "0xF27519dE8268a07d3A79415112F56D11258FA91e", "refundsEnabled()"),
        ("CSAGENT_sale_saleStart", "0xF27519dE8268a07d3A79415112F56D11258FA91e", "saleStart()"),
        ("CSAGENT_sale_saleEnd", "0xF27519dE8268a07d3A79415112F56D11258FA91e", "saleEnd()"),
        ("CSAGENT_sale_deadline", "0xF27519dE8268a07d3A79415112F56D11258FA91e", "deadline()"),
        ("BITCAT_sale_launched", "0x577874415214780b37EB8966c41563954b76A8B8", "launched()"),
        ("BITCAT_sale_phase", "0x577874415214780b37EB8966c41563954b76A8B8", "phase()"),
        ("CHEEMSA_tradingOpen", "0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2", "tradingOpen()"),
        ("PACTURE_sale_launched", "0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9", "launched()"),
        ("PACTURE_sale_phase", "0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9", "phase()"),
    ]:
        try:
            h = call(addr, "0x" + sel(sig))
            sale_checks[label] = u256(h) if h else None
        except Exception as e:
            sale_checks[label + "_error"] = str(e)
    out["sale_state_checks"] = sale_checks
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
