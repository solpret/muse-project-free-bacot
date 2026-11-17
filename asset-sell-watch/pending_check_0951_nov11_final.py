#!/usr/bin/env python3
"""Final targeted verification run 09:51 Nov 11 via 1rpc.io/bnb.
- balanceOf: 币安加油, ORBITA, POSTAGE (still rpc_failed_balance)
- getPair: YYDS, LUCKY777 (pair existed at 08:51, null twice since — a pair
  cannot vanish, so null must be a read error; verify with a fresh endpoint)
- getReserves: BITCAT pair (quote reverted INSUFFICIENT_LIQUIDITY)
- gas price sanity check.
Merges into pending_check_0951_nov11_stdout.json. Read-only."""
import json, subprocess
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
URL = "https://1rpc.io/bnb"
PATH = "/home/hatch/workspace/asset-sell-watch/pending_check_0951_nov11_stdout.json"
TOK = {
    "币安加油": "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f",
    "ORBITA": "0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709",
    "POSTAGE": "0x6C310EABEdFD4eEd6148bf2C07241FB45a52FB42",
    "YYDS": "0xd23be069c3c3a7f631af52584a16a9e46bb41da1",
    "LUCKY777": "0xc6D4ec8CB889aFBa9f251606001457644E260f7D",
}
PAIRS = {"BITCAT": "0x8dD64bb9F614D58716eB0e343e1F794B2E7A04f4"}

def sel(sig):
    return keccak(text=sig).hex()[:8]

def call(to, data, timeout=20):
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

def rpc(method, params, timeout=20):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    try:
        p = subprocess.run(["curl", "-s", "-m", str(timeout), "-X", "POST",
                            "-H", "Content-Type: application/json",
                            "-d", body, URL],
                           capture_output=True, text=True, timeout=timeout + 5)
        res = json.loads(p.stdout)
        return res.get("result"), res.get("error")
    except Exception as e:
        return None, str(e)

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

def main():
    out = json.load(open(PATH))
    idx = {e["symbol"]: i for i, e in enumerate(out["entries"])}
    gp, gerr = rpc("eth_gasPrice", [])
    print("gasPrice(1rpc):", gp, "err:", gerr, flush=True)
    out["gas_price_1rpc_wei"] = u256(gp) if gp else None
    for sym, tok in TOK.items():
        item = out["entries"][idx[sym]]
        bal_h, bal_err = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
        if bal_h is not None:
            dec_h, _ = call(tok, "0x" + sel("decimals()"))
            dec = u256(dec_h) if dec_h else 18
            bal = u256(bal_h)
            item["balance_raw"] = str(bal); item["balance_human"] = bal / (10**dec) if dec < 40 else None
            item["decimals"] = dec; item["balance_endpoint"] = URL + " (final)"
            item["status"] = "empty" if bal == 0 else item.get("status")
            item.pop("balance_error", None)
            print(sym, "bal:", item["balance_human"], flush=True)
        else:
            item["balance_error"] = bal_err
            print(sym, "bal FAILED:", bal_err, flush=True)
        if sym in ("YYDS", "LUCKY777"):
            pair_h, pair_err = call(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex())
            if pair_h is not None:
                pair = ("0x" + pair_h[-40:]) if u256(pair_h) else None
                item["pair_wbnb"] = pair; item["pair_endpoint"] = URL + " (final)"
                if pair:
                    res_h, res_err = call(pair, "0x" + sel("getReserves()"))
                    if res_h:
                        r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
                        item["reserves"] = [str(r0), str(r1)]
                        item["status"] = "pair_empty" if (r0 == 0 or r1 == 0) else "pair_live"
                    else:
                        item["reserves_error"] = res_err
                else:
                    item["status"] = "no_pair"
                print(sym, "pair:", pair, "reserves:", item.get("reserves"), "status:", item.get("status"), flush=True)
            else:
                print(sym, "getPair FAILED:", pair_err, flush=True)
                item["pair_error"] = pair_err
        out["entries"][idx[sym]] = item
        json.dump(out, open(PATH, "w"), indent=1)
    for sym, pair in PAIRS.items():
        item = out["entries"][idx[sym]]
        res_h, res_err = call(pair, "0x" + sel("getReserves()"))
        if res_h:
            r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
            item["reserves"] = [str(r0), str(r1)]
            item["status"] = "pair_empty" if (r0 == 0 or r1 == 0) else "pair_live"
            print(sym, "reserves:", item["reserves"], "status:", item["status"], flush=True)
        else:
            item["reserves_error"] = res_err
            print(sym, "getReserves FAILED:", res_err, flush=True)
        out["entries"][idx[sym]] = item
        json.dump(out, open(PATH, "w"), indent=1)
    print("DONE")

if __name__ == "__main__":
    main()
