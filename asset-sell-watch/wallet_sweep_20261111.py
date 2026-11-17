#!/usr/bin/env python3
"""Sapuan satu kali: semua token fungible agent wallet — bisa jadi uang?
Read-only. Untuk tiap token: saldo live, pair PCS V2 (WBNB + USDT),
quote getAmountsOut atas saldo penuh, bandingkan dengan gas.
Juga: saldo BNB 3 wallet + pair token claimable (10.000 masing-masing).
Keluar: JSON + tabel ringkas stdout.
"""
import json, time, urllib.request

AGENT = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
MAIN = "0xcf3c6fc1bf670a8d3f03436395286f86dbee7418"
W3 = "0x71bcee31054137448e78f2e28dbe3160aae3e235"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
USDT = "0x55d398326f99059fF775485246999027B3197955"
RPCS = ["https://bsc-dataseed1.binance.org", "https://bsc-dataseed2.binance.org",
        "https://bsc-dataseed3.binance.org", "https://bsc-dataseed4.binance.org"]

from Crypto.Hash import keccak
def sel(s): return "0x" + keccak.new(data=s.encode(), digest_bits=256).hexdigest()[:8]
def pad(a): return a[2:].lower().rjust(64, "0")
def u(n): return format(n, "064x")

def rpc(method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    last = None
    for rpc in RPCS:
        try:
            req = urllib.request.Request(rpc, data=payload, headers={"Content-Type": "application/json"})
            d = json.load(urllib.request.urlopen(req, timeout=15))
            if "result" in d and d["result"] is not None:
                return d["result"]
            last = d.get("error")
        except Exception as e:
            last = e
    raise RuntimeError(f"rpc gagal {method}: {last}")

def call(to, data):
    return rpc("eth_call", [{"to": to, "data": data}, "latest"])

def balance_of(tok, holder):
    return int(call(tok, sel("balanceOf(address)") + pad(holder)), 16)

def decimals(tok):
    try:
        return int(call(tok, sel("decimals()")), 16)
    except Exception:
        return 18

def get_pair(a, b):
    r = call(FACTORY, sel("getPair(address,address)") + pad(a) + pad(b))
    return "0x" + r[-40:]

def quote(amount_in, tok):
    enc = sel("getAmountsOut(uint256,address[])") + u(amount_in) + u(64) + u(2) + pad(tok) + pad(WBNB)
    r = call(ROUTER, enc)
    words = [int(r[i:i+64], 16) for i in range(2, len(r), 64)]
    return words[-1]

def main():
    t0 = time.time()
    out = {"checked_at_wib": time.strftime("%Y-%m-%d %H:%M:%S WIB", time.localtime()),
           "gas_price_gwei": None, "bnb": {}, "tokens": [], "claimables": []}
    gp = int(rpc("eth_gasPrice", []), 16)
    out["gas_price_gwei"] = gp / 1e9
    gas_est = 300_000 * gp  # approve+swap konservatif
    out["gas_est_300k_bnb"] = gas_est / 1e18
    for name, w in [("agent", AGENT), ("utama", MAIN), ("wallet3", W3)]:
        out["bnb"][name] = int(rpc("eth_getBalance", [w, "latest"]), 16) / 1e18
    print(f"gas {gp/1e9} gwei | est gas 300k = {gas_est/1e18:.6f} BNB | "
          f"BNB agent {out['bnb']['agent']:.6f} utama {out['bnb']['utama']:.6f} w3 {out['bnb']['wallet3']:.6f}", flush=True)

    pend = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))
    tokens = [(e["symbol"], e["token"], e.get("decimals", 18), "pending-swap") for e in pend["entries"]]
    asset_sell = [("BAO", "0x3CD603B6742Abd53948DC4c08e50A267677b0605"),
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
        ("HONGBAO", "0x44e9AeC5b828092A9eBC3070caCcd556BB21C725")]
    tokens += [(s, t, 18, "asset-sell-watch") for s, t in asset_sell]
    tokens += [("GANG", "0x0c6302401aa5325c2e36f170f52c00b1d220b405", 18, "extra"),
               ("STOCKMEMES", "0x8c36223b4f460521ca49d2ce43a1b60c8185ba80", 18, "extra"),
               ("TSURU", "0xc50c9b132af459Fa7b351Fd6f3AAeeFd8E9E1E96", 18, "extra"),
               ("财富🐷", "0x33d612C10b509aBD8723b7E0E11e1CFFB02f5a27", 18, "extra")]
    for sym, tok, dec, src in tokens:
        row = {"symbol": sym, "token": tok, "source": src}
        try:
            bal = balance_of(tok, AGENT)
        except Exception as e:
            row["error"] = f"balanceOf gagal: {e}"; out["tokens"].append(row); continue
        d = dec
        try:
            d = decimals(tok)
        except Exception:
            pass
        row["decimals"] = d
        row["balance_human"] = bal / (10 ** d)
        row["balance_raw"] = bal
        if bal == 0:
            row["verdict"] = "saldo 0"
            out["tokens"].append(row)
            print(f"{sym}: saldo 0", flush=True); continue
        try:
            pair = get_pair(tok, WBNB)
        except Exception as e:
            row["error"] = f"getPair gagal: {e}"; out["tokens"].append(row); continue
        row["pair_wbnb"] = pair
        try:
            pair_u = get_pair(tok, USDT)
        except Exception:
            pair_u = None
        row["pair_usdt"] = pair_u
        if pair == "0x0000000000000000000000000000000000000000":
            row["verdict"] = "no_pair_wbnb"
            print(f"{sym}: bal {row['balance_human']:,.4g} no pair WBNB (USDT pair: {pair_u})", flush=True)
            out["tokens"].append(row); continue
        try:
            q = quote(bal, tok)
        except Exception as e:
            row["verdict"] = "pair_empty_or_quote_revert"
            print(f"{sym}: bal {row['balance_human']:,.4g} pair ada tapi quote gagal: {e}", flush=True)
            out["tokens"].append(row); continue
        row["quote_bnb"] = q / 1e18
        row["net_bnb"] = (q - gas_est) / 1e18
        row["verdict"] = "SELLABLE" if q >= 2 * gas_est else ("quote_dust" if q > 0 else "quote_zero")
        print(f"{sym}: bal {row['balance_human']:,.4g} quote {q/1e18:.6f} net {(q-gas_est)/1e18:.6f} -> {row['verdict']}", flush=True)
        out["tokens"].append(row)

    # claimables: pair saja (belum di wallet; klaim butuh gas sendiri)
    claim_defs = [("PETAL", "0x58f3581849a59304b4bb3a1c8cc48635df7bb87f"),
                  ("DEBRIS", "0x59a1b46c3fd4ee0938143f0292205bb1e6c93608"),
                  ("RIME", "0xe9ba5711dc1e3d8e71729a3cbd89f501a0247199"),
                  ("HYPHA", "0xbe5ca40e4bc8b561615390eefd5f1d4911ff3ea0")]
    # WIRE + EMBER: baca TOKEN() dari kontrak NFT-nya
    for nft, sym in [("0x485be9daA4620FcEE4e2bAEd7cc85Ea57Acb44b0", "WIRE"),
                     ("0x7673C596a6702D32f844266DC2ca7B1FD6d7dF21", "EMBER")]:
        try:
            r = call(nft, sel("TOKEN()"))
            claim_defs.append((sym, "0x" + r[-40:]))
        except Exception as e:
            out["claimables"].append({"symbol": sym, "error": f"TOKEN() gagal: {e}"})
    for sym, tok in claim_defs:
        row = {"symbol": sym, "token": tok, "claimable": 10000}
        try:
            pair = get_pair(tok, WBNB)
        except Exception as e:
            row["error"] = f"getPair gagal: {e}"; out["claimables"].append(row); continue
        row["pair_wbnb"] = pair
        if pair == "0x0000000000000000000000000000000000000000":
            row["verdict"] = "no_pair"
            print(f"CLAIM {sym}: no pair", flush=True)
            out["claimables"].append(row); continue
        try:
            amt = 10000 * (10 ** decimals(tok))
            q = quote(amt, tok)
            row["quote_bnb_10000"] = q / 1e18
            row["verdict"] = "pair_live" if q > 0 else "pair_empty"
            print(f"CLAIM {sym}: pair {pair} quote 10.000 = {q/1e18:.6f}", flush=True)
        except Exception as e:
            row["verdict"] = "pair_empty_or_quote_revert"
            print(f"CLAIM {sym}: pair {pair} quote gagal", flush=True)
        out["claimables"].append(row)

    json.dump(out, open("/home/hatch/workspace/asset-sell-watch/wallet-sweep-2026-11-11.json", "w"), indent=2, ensure_ascii=False)
    print(f"SELESAI {time.time()-t0:.0f} dtk -> wallet-sweep-2026-11-11.json", flush=True)

if __name__ == "__main__":
    main()
