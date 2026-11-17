import json, urllib.request, base64
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed3.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,data):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=p,headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=8) as r: v=json.load(r)["result"]
            return v if v and v!="0x" else None
        except Exception: continue
    return None
def iv(v):
    try: return int(v,16) if v else None
    except Exception: return None
def dec_str(v):
    # abi string: offset,len,data
    try:
        b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[32:64],'big'); raw=b[64:64+ln]
        if raw.startswith(b'data:application/json;base64,'):
            return base64.b64decode(raw.split(b',',1)[1]).decode()
        return raw.decode(errors='replace')
    except Exception as e: return f"ERR {e}"
for a in ["0xf1d1650dBfeB0FA8082481C8213ACCD59af3cF4A","0x2f47305baEdC1B1F28461cD6b488404A908B1BEA"]:
    print(a, dec_str(call(a,sel("contractURI()"))), flush=True)
S="0x824d1e5c1395ed7543854fCd9e4da6D3F358De16"; T="0xE8F51B6e1561055A68f3e2b3dcb39e5f19e3ca78"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0")
print("token name/symbol/dec/totalSupply:", dec_str(call(T,sel("name()"))), dec_str(call(T,sel("symbol()"))), iv(call(T,sel("decimals()"))), iv(call(T,sel("totalSupply()"))))
key=call(S,sel("agentKeyOf(address)")+u); print("agentKeyOf(user wallet):", key)
print("sharesOf(user):", iv(call(S,sel("sharesOf(address)")+u)))
print("tokensOwed(user):", iv(call(S,sel("tokensOwed(address)")+u)))
if key:
    kb=key[2:].rjust(64,"0")
    print("freeClaimedByKey(key):", iv(call(S,sel("freeClaimedByKey(bytes32)")+kb)))
    print("paidByKey(key):", iv(call(S,sel("paidByKey(bytes32)")+kb)))
print("poolSeeded:", iv(call(S,sel("poolSeeded()"))), "poolPending:", iv(call(S,sel("poolPending()"))), "totalSold:", iv(call(S,sel("totalSold()"))), "totalShares:", iv(call(S,sel("totalShares()"))))
