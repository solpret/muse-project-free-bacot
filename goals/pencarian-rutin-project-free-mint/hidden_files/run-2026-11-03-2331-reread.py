#!/usr/bin/env python3
"""Main run 2201 reread - read-only."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:160]}"
    return None, err
def collect(to, tests):
    out = {}
    for name, arg in tests:
        val, err = call(to, sel(name) + arg)
        try: iv = int(val, 16) if val else None
        except Exception: iv = None
        out[name] = {"int": iv, "raw": val, "error": err if val is None else None}
    return out
def block():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
    return None
def dec_str(raw):
    # decode ABI string return
    try:
        if not raw or len(raw) < 130: return None
        off = int(raw[2:66], 16); ln = int(raw[66:130], 16)
        hx = raw[130:130 + ln * 2]
        return bytes.fromhex(hx).decode(errors="replace")
    except Exception: return None
def str_call(to, name):
    val, err = call(to, sel(name))
    return {"int": None, "str": dec_str(val), "raw": val, "error": err if val is None else None}

snap = json.load(open(BASE + "onchain-snapshot.json"))
c = snap["contracts"]
names = ["Syntaxia","Noesyn","Lumenhold","Vertexa","Omegrid","Auditrix","Robogent","Synaptik",
 "Yydsgent","Mechfarm-1FAb","Saturnagent-ef87","Ronagent","Ghoulfarm","Phoenixgent","Nbgent",
 "Weldagent","Frostagent","Niubimind","Shogunode","Botkirin","Pumpkinagent","Saturnode",
 "Glitchpilotfox","Cogentbyte","Argonode","Marsgent","Chipbotcore","Cuprihive","Neonnodefox",
 "Rubynode","Scarabswarm","Merith","Agentdragon","Wuyuhive","Rimeagent","Pandadroid","SYNTHIA","Ghost Frog","Ghostpilotcat","Droidneon","Osiris Guardians","LanternLords","Brinedroid"]
tests = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""),
         ("mintedBy(address)", enc_addr(USER)[2:]), ("freeUsed(address)", enc_addr(USER)[2:]),
         ("balanceOf(address)", enc_addr(USER)[2:]), ("mintOpen()", "")]
out = {"block": block()}
for n in names:
    a = c[n]["address"]
    out[n] = collect(a, tests)
# SYNTHIA + bonus token + its NFT + Sourcify-new 29EE
syn = "0xFe1Bbe79A6Ea942e01722E626097741971c6cf82"
out["SYNTHIA"] = collect(syn, tests)
out["SYNTHIA_str"] = {"name": str_call(syn, "name()"), "symbol": str_call(syn, "symbol()")}
out["SYNTHIA_extra"] = collect(syn, [("owner()", ""), ("contractURI()", ""), ("freeLeft()", ""),
    ("freeMinted()", ""), ("MAX_SUPPLY()", ""), ("totalMinted()", "")])
bonus = "0xE57FDfE8167ECA525Eefcc0EC283D56395D26726"
out["BONUS_TOKEN_E57F"] = {"name": str_call(bonus, "name()"), "symbol": str_call(bonus, "symbol()"),
    "decimals": collect(bonus, [("decimals()", "")]), "totalSupply": collect(bonus, [("totalSupply()", "")])}
nft9432 = "0x9432f294e68713c8144177659e177F1b7C997434"
out["NFT_9432"] = collect(nft9432, tests)
out["NFT_9432_str"] = {"name": str_call(nft9432, "name()"), "symbol": str_call(nft9432, "symbol()")}
new29 = "0x29EE92a8D6Dc62035D0C2b4D53B5df504D3Ebe91"
out["NEW29EE"] = collect(new29, tests)
out["NEW29EE_str"] = {"name": str_call(new29, "name()"), "symbol": str_call(new29, "symbol()")}
out["NEW29EE_extra"] = collect(new29, [("mintOpen()", ""), ("mintPrice()", ""), ("maxSupply()", ""),
    ("totalMinted()", ""), ("owner()", ""), ("registry()", "")])
# Mirror Pair + AZET (age check) + IMARS + binanceai
# Mirror Pair removed run 2131 (age-excluded); no reread.
out["IMARS"] = collect("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",
    [("opened()", ""), ("freeMinted()", ""), ("FREE_SHARES()", ""), ("totalMinted()", ""),
     ("freeClaimed(address)", enc_addr(USER)[2:])])
out["BINANCEAI"] = collect("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
    [("launched()", ""), ("totalShares()", ""), ("isRefundPhase()", ""), ("failed()", ""),
     ("tokenClaimed(address)", enc_addr(USER)[2:])])

for _n,_a in [("Osiris Guardians","0xD6fCF9dB58a559AAFBbf9Fd823F4f081E6701311"),("LanternLords","0xC9c0De69ea301cA9479149554bf325aE3342584B"),("Brinedroid","0xa069401266707e1318bdff45b3F1F61E52D1AE48")]:
    out[_n+"_extra"] = collect(_a, [("freeMinted()", ""), ("FREE_SUPPLY()", ""), ("owner()", "")])
out["FLYING"] = collect("0x9e14822255f2f287f5ef233e4cf8580481dcf75e", [("totalSupply()",""),("totalMinted()",""),("mintOpen()",""),("mintedBy(address)",enc_addr(USER)[2:]),("balanceOf(address)",enc_addr(USER)[2:])])
json.dump(out, open(BASE + "run-2026-11-03-2331-reread.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:6000])
