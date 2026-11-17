import json, urllib.request
from Crypto.Hash import keccak
RPCS = ["https://bsc-dataseed.bnbchain.org","https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
RPC = RPCS[0]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
OUT = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-1509-reread.json"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def raw(to, data):
    last=None
    for rpc in RPCS:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}).encode()
        req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                out = json.load(r)
            break
        except Exception as e:
            last=e; continue
    else:
        return {"error": str(last)}
    if "error" in out: return {"error": out["error"]}
    v = out["result"]
    if not v or v == "0x": return None
    try: return int(v, 16)
    except Exception: return v
def call(to, sig, args=""):
    return raw(to, sel(sig) + args)
def block():
    last=None
    for rpc in RPCS:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
        req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return int(json.load(r)["result"], 16)
        except Exception as e:
            last=e; continue
    raise last
blk = block()
res = {"block": blk}
NFT = {
 "HIVE": "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77",
 "Tigora": "0xE8c46E7c734259FEc1A78Fc846DcFaD94Ecb70E5",
 "BNBRunnerz": "0x8AAA14b24e71cC93672939ba3e3C3e9DE2674d27",
 "Shroomies": "0x2AE712138a74202daBB8FFC93117AA53754F54D0",
 "Blobbies": "0xa7fBAB4a96d6900122Dc51FDC839CFE5C89B23b3",
 "Robogent": "0x5eA7E757dfc4654f7478841BD30175bd7F186e24",
 "Jolly": "0xdc11764a5664e333c8d303eb465e89a1caadb85b",
 "HACKED": "0xCD355D1191Ce9849B3A935C821A66d9DF37cFE77",
 "SoulAgent": "0x8fdB9411753c58476A41F7B88a44989F8D687d63",
 "PERSONA": "0xA930C4466431B0331C911846f297D7D4e063249D",
 "RigOrb": "0x72D977237f7b3931A08434cEBD0D3814fE13539e",
}
for name, addr in NFT.items():
    res[name] = {
        "totalSupply()": call(addr, "totalSupply()"),
        "totalMinted()": call(addr, "totalMinted()"),
        "balanceOf(user)": call(addr, "balanceOf(address)", enc_addr(USER)),
    }
# RigOrb specifics
rb = NFT["RigOrb"]
res["RigOrb"]["mintOpen()"] = call(rb, "mintOpen()")
res["RigOrb"]["priceFor(user,1)"] = call(rb, "priceFor(address,uint256)", enc_addr(USER) + enc_uint(1))
res["RigOrb"]["mintedCount(user)"] = call(rb, "mintedCount(address)", enc_addr(USER))
# Robogent / Jolly free counters
res["Robogent"]["freeClaimed()"] = call(NFT["Robogent"], "freeClaimed()")
res["Jolly"]["freeMinted()"] = call(NFT["Jolly"], "freeMinted()")
# Track C
res["OSK"] = {"opened()": call("0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37", "opened()"),
              "totalMinted()": call("0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37", "totalMinted()")}
res["NIULAI"] = {"launched()": call("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF", "launched()"),
                 "phase()": call("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF", "phase()")}
res["KillZero"] = {"launched()": call("0x87ad9c1617ceb65f1b56f2ee06FE193F60aACF97", "launched()")}
res["DROID"] = {"opened()": call("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177", "opened()"),
                "freeMinted()": call("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177", "freeMinted()"),
                "totalMinted()": call("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177", "totalMinted()")}
res["IMARS"] = {"opened()": call("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f", "opened()"),
                "freeMinted()": call("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f", "freeMinted()"),
                "totalMinted()": call("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f", "totalMinted()")}
res["ASOC"] = {"freeClaimed(user)": call("0x43cEef9313CB8c4ca3757bA841C44DF40A223205", "freeClaimed(address)", enc_addr(USER)),
               "saleEnded()": call("0x43cEef9313CB8c4ca3757bA841C44DF40A223205", "saleEnded()")}
res["SENBAZURU"] = {"opened()": call("0xb21583A08581278BcF925351a99C61A4562C62f0", "opened()"),
                    "freeClaimed()": call("0xb21583A08581278BcF925351a99C61A4562C62f0", "freeClaimed()"),
                    "hasFreeShare(user)": call("0xb21583A08581278BcF925351a99C61A4562C62f0", "hasFreeShare(address)", enc_addr(USER))}
res["FABE"] = {"launched()": call("0xFabE022a5943462fee1Bd221791945DA57510BE8", "launched()"),
               "freeSharesRemaining()": call("0xFabE022a5943462fee1Bd221791945DA57510BE8", "freeSharesRemaining()"),
               "freeSharesClaimed(user)": call("0xFabE022a5943462fee1Bd221791945DA57510BE8", "freeSharesClaimed(address)", enc_addr(USER))}
res["BINANCEAI"] = {"launched()": call("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", "launched()"),
                    "totalShares()": call("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", "totalShares()"),
                    "isRefundPhase()": call("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", "isRefundPhase()"),
                    "failed()": call("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", "failed()")}

# ShibAgent R2 re-check (1001)
SHIB="0x016a148e728b8d61b2440ed311946ac06d4b5648"
res["ShibAgentR2"]={"FREE_SHARES()": call(SHIB,"FREE_SHARES()"), "freeClaimed()": call(SHIB,"freeClaimed()"), "sold()": call(SHIB,"sold()"), "phase()": call(SHIB,"phase()"), "balanceOf(user)": call(SHIB,"balanceOf(address)", enc_addr(USER)), "freeClaimedById(userId)": "see-probe"}
res["QAGENT"]={"freeMinted()": call("0xE3a4f3099a2136e0e66202A665815caB8FFA2704","freeMinted()"), "sharesMinted()": call("0xE3a4f3099a2136e0e66202A665815caB8FFA2704","sharesMinted()")}
res["StarAgent"]={"totalSupply()": call("0x7d390e37ed41a359f276d8764ca15432704b99b7","totalSupply()"), "claimedFree(user)": call("0x7d390e37ed41a359f276d8764ca15432704b99b7","claimedFree(address)", enc_addr(USER))}

AFROG="0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31"
res["AFROG"]={"totalSupply()": call(AFROG,"totalSupply()"), "freeClaimed()": call(AFROG,"freeClaimed()"), "FREE_SUPPLY()": call(AFROG,"FREE_SUPPLY()"), "balanceOf(user)": call(AFROG,"balanceOf(address)", enc_addr(USER)), "mintedBy(user)": call(AFROG,"mintedBy(address)", enc_addr(USER))}

EXTRA = {
 "Swarmcentaur": "0x87B805eCDDaB0b376531cAf6d5aD9A52E641B100",
 "Agentyyds": "0x8463abFC06173BdCaEDe96c4331C30A958789629",
 "Pilotneon": "0x01D0f3b16C89615c924007ae85779B55A22552D0",
 "Mummyhive": "0xf45fE22B3a9A748c59A7099e2E7B69f41216b1cd",
 "Saturnode": "0x6124b3ae64adA7b73581CcD01fEF89e583E8742c",
 "MeowBark": "0x7a38395ad7317594a8eb6c658f3f073a693dfaab",
 "SlimySlug": "0x2e76c45bc5851e8211012e91bc2c960e4334dbfc",
}
for name, addr in EXTRA.items():
    res[name] = {
        "totalSupply()": call(addr, "totalSupply()"),
        "freeClaimed()": call(addr, "freeClaimed()"),
        "FREE_SUPPLY()": call(addr, "FREE_SUPPLY()"),
        "balanceOf(user)": call(addr, "balanceOf(address)", enc_addr(USER)),
    }


SH="0x2AE712138a74202daBB8FFC93117AA53754F54D0"
res["Shroomies"]["price()"]=call(SH,"price()")
res["Shroomies"]["costOf(user,1)"]=call(SH,"costOf(address,uint256)",enc_addr(USER)+enc_uint(1))
res["Shroomies"]["mintOpen()"]=call(SH,"mintOpen()")
res["Shroomies"]["mintedBy(user)"]=call(SH,"mintedBy(address)",enc_addr(USER))
res["Shroomies"]["mintsLeft()"]=call(SH,"mintsLeft()")

print(json.dumps(res, indent=1))
with open(OUT, "w") as f:
    json.dump(res, f, indent=1)
