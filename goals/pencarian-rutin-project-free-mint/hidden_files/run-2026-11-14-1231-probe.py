#!/usr/bin/env python3
"""Probe run 2026-11-14 12:31 WIB: 13 new Sourcify feed contracts (ABI S1/S2 + NFT agent shape).
Read-only; no preview/mint. Writes run-2026-11-14-1231-probe.json."""
import json, subprocess, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"
ADDRS = [
 "0x913447c741ca3c28765C630ba0FdfE67867b7C6e","0x3c6A3b678A28c3E592969BdbC1E90Fe1D82b7FF2",
 "0x0fB9beE89DC7EfFc2B2AF33bb5c218ad2933AbB1","0xE58Fa9A2C41DCaD5547D1804b362058563aad71E",
 "0xE58395e362DF4086ce2bf64224e0E4512b391281","0x86F2C0985b2F6931E1605a9F89D164b4A47a6Ef4",
 "0xE9B715882757D6f39599B3c987216E82613e1777","0xa34d4c64d7be13947F91c492f4611a990de47C3e",
 "0x72F47C24deD5f70CC78cAFb37A05A081E1B5D2AB","0xf9daE624f4A43ca820DacaF8E3Cd0704DD30c452",
 "0xFFdeb2F6761d0Ea17bd743217B1213BF15D28D4e","0xd4C319985816C607BbF53918Ab763Cc8D0b1D475",
 "0x210DEC35BAAE827652EBAC113189812582F87Da5",
]
FREE_VIEWS = ("freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted",
              "freeRemaining","freeSupply","freeCount","freeMintsLeft")
def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        out = subprocess.run(["curl","-sL","--max-time","30",url], capture_output=True, text=True, timeout=40).stdout
        d = json.loads(out)
        return d
    except Exception as e:
        return {"error": str(e)[:120]}
def analyze(addr, d):
    res = {"address": addr, "verified": False, "n_fns": 0, "names": [], "S1": False, "S2": False, "nft_agent": False, "notes": []}
    try:
        abi = d.get("abi")
        if abi is None:
            std = d.get("stdJson", {})
            out = std.get("output", {}).get("contracts", {})
            for f, contracts in out.items():
                for name, c in contracts.items():
                    if c.get("abi"): abi = c["abi"]; res["contract_name"] = name; break
        if abi is None:
            res["notes"].append("no ABI in Sourcify response (keys: %s)" % list(d.keys())[:6])
            return res
        res["verified"] = True
        names = [f.get("name","") for f in abi if isinstance(f, dict) and f.get("type")=="function"]
        res["n_fns"] = len(names); res["names"] = names
        low = [n.lower() for n in names]
        has_mint = any(n.startswith("mint") for n in low)
        has_quote = any(("quote" in n or n in ("cost","price","getprice","mintprice")) for n in low)
        has_free = any(n in FREE_VIEWS or n.lower() in [f.lower() for f in FREE_VIEWS] for n in names)
        has_reg = any("agent" in n.lower() and ("regist" in n.lower() or "gate" in n.lower()) for n in names)
        has_token = all(x in low for x in ("name","symbol","decimals","totalsupply"))
        noarg_free = any(n in ("mintfree","freemint","claimfree") for n in low)
        reg_bytes = REG.lower() in json.dumps(d).lower()
        res["S1"] = bool(has_mint and has_quote and has_free and (has_reg or reg_bytes))
        res["S2"] = bool(has_token and noarg_free and has_free and (has_reg or reg_bytes))
        res["nft_agent"] = bool(has_mint and has_free and (has_reg or reg_bytes))
        res["notes"].append("mint=%s quote=%s free=%s regfn=%s regbytes=%s token=%s noargfree=%s" % (has_mint, has_quote, has_free, has_reg, reg_bytes, has_token, noarg_free))
        return res
    except Exception as e:
        res["notes"].append("analyze error: " + str(e)[:150])
        return res
out = {"started_wib": "2026-11-14T12:31+07:00", "results": []}
for a in ADDRS:
    d = fetch_abi(a)
    r = analyze(a, d)
    out["results"].append(r)
    print(a, "verified" if r["verified"] else "NOT-VERIFIED", "fns=%d" % r["n_fns"], "S1=%s S2=%s nft_agent=%s" % (r["S1"], r["S2"], r["nft_agent"]), r["notes"], flush=True)
json.dump(out, open(BASE + "run-2026-11-14-1231-probe.json", "w"), indent=1)
print("DONE", sum(1 for r in out["results"] if r["S1"] or r["S2"] or r["nft_agent"]), "shape hits /", len(ADDRS))
