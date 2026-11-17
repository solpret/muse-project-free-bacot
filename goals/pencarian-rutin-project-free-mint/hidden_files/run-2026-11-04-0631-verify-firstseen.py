#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:120]}"
    return None, err
def safe_int(val):
    try:
        if val and len(val) <= 130: return int(val, 16)
    except Exception: pass
    return None
def hexaddr(val):
    try:
        if val: return "0x" + val[-40:]
    except Exception: return None
def collect(to, tests):
    out = {}
    for name, arg in tests:
        val, err = call(to, sel(name) + arg)
        out[name] = {"int": safe_int(val), "addr": hexaddr(val), "error": err if val is None else None}
    return out
def dec_str(raw):
    try:
        if not raw or len(raw) < 130: return None
        off = int(raw[2:66], 16); ln = int(raw[66:130], 16)
        return bytes.fromhex(raw[130:130 + ln * 2]).decode(errors="replace")
    except Exception: return None
def str_call(to, name):
    val, err = call(to, sel(name))
    return {"str": dec_str(val), "error": err if val is None else None}
def block():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
    return None
tests = [("totalSupply()", ""), ("totalMinted()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""), ("freeAllocation()", ""), ("totalFreeMinted()", ""), ("remainingFreeSupply()", ""), ("freeMinted()", ""), ("mintOpen()", ""), ("mintedBy(address)", enc_addr(USER)[2:]), ("freeUsed(address)", enc_addr(USER)[2:]), ("freeMintedByWallet(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:]), ("MAX_SUPPLY()", ""), ("mintPrice()", "")]
items = {
 "NanoNarwhals":"0x3c1d49451791eE8bE33FD766A879b4A79B9a06e5",
 "NeonBadgers":"0x662e144aFEF030E6e24236337c72FA3a53C15793",
 "ByteOtters":"0x654461557A3CA8397EA21BA04A06a65bEC03b4Ba",
 "CircuitCapybaras":"0xB2DD7a694eb8F85b92074Cf8070E615a4E84766C",
 "OrbitAxolotls":"0xE1eF6f4AcBfe2d257C135b644FA4bFdd498536e7A",
 "SignalOwls":"0xFFe8ED361Ce18E9fa7C418C39272E1d9186cfdda",
 "EchoSalamanders":"0xB7f871d9582D058Bb3B3D0c1aC7F1C2C27Ac7fa1",
 "VectorVultures":"0xC61B5c2c2399edAda510E4AB6782FBCAF892365E",
 "LumenOracleAgent":"0xF250e0cA582794E753caA6f55d2208fbE0a488B3",
}
out = {"block": block()}
for n, a in items.items():
    out[n] = collect(a, tests)
    out[n+"_extra"] = collect(a, [("owner()", ""), ("AGENT_ID()", ""), ("agentIdRegistry()", "")])
    out[n+"_quote"] = collect(a, [("quote(address,uint256)", enc_addr(USER)[2:]+"01".rjust(64,"0")), ("quoteMint(uint256)", "01".rjust(64,"0")), ("freeFor(address,uint256)", enc_addr(USER)[2:]+"01".rjust(64,"0"))])
    out[n+"_str"] = {"name": str_call(a, "name()"), "symbol": str_call(a, "symbol()"), "contractURI": str_call(a, "contractURI()")}
    print(n, json.dumps(out[n]), json.dumps(out[n+"_extra"]), json.dumps(out[n+"_quote"]), json.dumps(out[n+"_str"]))
json.dump(out, open(BASE + "run-2026-11-04-0631-verify-firstseen.json", "w"), indent=1)
print("block", out["block"])
