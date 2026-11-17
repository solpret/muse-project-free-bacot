import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to, data, block="latest"):
    try:
        r = ankr_post("eth_call", [{"to": to, "data": data}, block], timeout=30)
        return r.get("result")
    except Exception as e:
        return f"ERR:{type(e).__name__}:{e}"
def blk():
    try:
        r = ankr_post("eth_blockNumber", [], timeout=20)
        return int(r.get("result","0x0"),16)
    except Exception as e:
        return f"ERR:{e}"
TS = "0x18160ddd"
BAL = "0x70a08231" + "000000000000000000000000" + USER[2:].lower()
targets = {
 "Soul Agent": "0x8fdb9411753c58476a41f7b88a44989f8d687d63",
 "Mars Nexus": "0xc4059d2f9f6f86695896e68f3e73e1e6cc3791c8",
 "Orzo-39f6": "0x39f61c0a379f132d66fb8c2adab293e6a7595b0a",
 "Qilingentle-423d": "0x423d25764E4D3D792C08e04C759cE3b0FcDE8596",
 "Hivejupiter-8DF7": "0x8DF74cBe998F8d447E7c77dD5117aFB940605400",
 "MoonCat": "0x045425004b622733ced4139e930c622187ea6c73",
}
out = {"block": blk(), "wib": time.strftime("%Y-%m-%d %H:%M:%S WIB", time.localtime(time.time()+7*3600)), "reads": {}}
for name, addr in targets.items():
    ts = call(addr, TS)
    bal = call(addr, BAL)
    def dec(v):
        try: return int(v,16) if isinstance(v,str) and v.startswith("0x") else v
        except Exception: return v
    out["reads"][name] = {"address": addr, "totalSupply": dec(ts), "balanceOf_user": dec(bal)}
    print(name, "totalSupply:", dec(ts), "balanceOf(user):", dec(bal))
print("block:", out["block"], "wib:", out["wib"])
json.dump(out, open("run-2026-11-06-2331-verify-fresh.json","w"), indent=1)
