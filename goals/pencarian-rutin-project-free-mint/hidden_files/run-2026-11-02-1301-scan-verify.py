#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from ankr import ankr_post
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e: err = str(e)[:120]
    return None, err
def iv(val):
    try: return int(val, 16) if val else None
    except Exception: return None
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "0"*64
cands = [
 ("Gravewrap","0x00cd422D25ec1aA8242602a2A000669e7BA9Be32",131187624),
 ("Cortexion","0x9bCdeA7285BD293c034a0056f361709A6c26C1bF",131187842),
 ("Mofishel","0xcb1797085f9A6790BAe1f02f9619642f3842B507",131187538),
 ("Bonejestra","0xcAA6554463a98F9afc966175694Cd81aC7c41B41",131187515),
 ("Kraknito","0x3134f8d194951d8f87fAb8B1cCc0571c68733de9",131187561),
 ("Gryphlume","0x8eA465aBd41Aec8B6f1BD80a7C6c37d3aE85529C",131187520),
 ("Hexrotta","0x25256EE137d4B2B9d440431aE8fC8fd9770c50A9",131187521),
 ("Cyberlynx","0xD4D848F81216Ef2856fEe2cdFa529a1bB53c50C0",131187991),
 ("Ringhelm","0x74a7D2ED15CaE609189FaD2876F0bF6E69f2622F",131188402),
 ("Chromeshade","0x5ba7355Fb4001eFe5232eb0286e11Fd81Eee99a4",131188003),
 ("Quantumoth","0x9FE22718Fb0196195263822Bd930FDb20852983f",131187554),
 ("Lycanthrax","0x6c1a1Fad4b1Aee87f041b25b5a7D4646633584E6",131188168),
 ("Marsito","0xeF4efd901c2AF4c9e974f30F02Ba4572e5F88117",131187558),
 ("Arachnoir","0xe6FfadcfB8766e6199EC74f896dA37F00B0F5BCa",131188243),
 ("Yydsbao","0x2D96bb1F9b3150aeD357B43A74cf3C42BfB70066",131187565),
]
out = {}
for name, addr, fb in cands:
    # pre-window logs: 131000000 .. 131187510
    pre = None
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": "131000000", "toBlock": "131187510", "address": [addr.lower()], "topics": [TRANSFER, ZERO, None]}, timeout=30)
        logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
        pre = len(logs)
    except Exception as e:
        pre = f"ERR {type(e).__name__}: {str(e)[:120]}"
    reads = {}
    for fn, arg in [("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("MAX_SUPPLY()",""),("mintOpen()",""),("mintedBy(address)",enc_addr(USER)[2:]),("freeUsed(address)",enc_addr(USER)[2:]),("balanceOf(address)",enc_addr(USER)[2:]),("quote(address,uint256)",enc_addr(USER)[2:]+format(1,"064x"))]:
        v,_ = call(addr, sel(fn)+arg); reads[fn]=iv(v)
    out[name] = {"address": addr, "scan_first_block": fb, "pre_window_logs_131000000_131187510": pre, "reads": reads}
    print(name, "pre:", pre, reads)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-1301-scan-verify.json","w"), indent=1)
