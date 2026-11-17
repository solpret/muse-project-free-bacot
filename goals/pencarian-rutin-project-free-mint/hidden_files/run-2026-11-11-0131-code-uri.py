#!/usr/bin/env python3
"""Run 0131: eth_getCode registry-bytes + contractURI() for 5 contracts; Ankr pre-flight; binanceai launched(). Read-only."""
import json, subprocess, time, base64
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def rpc(method,params):
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":method,"params":params})
            if isinstance(r,dict) and "result" in r: return r["result"]
        except Exception: continue
    return None
ADDRS={
 "Pico Alcazar":"0xdf95946fe4ea475e7180f77817f9e34b459121f2",
 "Tiling Hammock":"0x5f872b5c147a5ebe79b63a06f79b920e51648e31",
 "Hexel Pantry":"0x4a8e51016829632ae15f574a837c17c5bf1bc50b",
 "GangDotFun":"0x64af2a4aa164aefec5c09c405ad894065d34633f",
 "Dragon Agent":"0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6",
 "Arcane Stones":"0x23f3De28E55C392F24A217B2B1602C90e0292f35",
 "STALL":"0xe3de7fd0d12cff4a46d8bf702ab593b6f921b308",
}
out={}
for name,addr in ADDRS.items():
    code=rpc("eth_getCode",[addr,"latest"])
    reg_bytes = (code or "").lower().find(REG) >= 0 if code else None
    uri_raw=rpc("eth_call",[{"to":addr,"data":sel("contractURI()")},"latest"])
    uri=None
    if uri_raw and len(uri_raw)>130:
        try:
            b=bytes.fromhex(uri_raw[2:])
            ln=int.from_bytes(b[32:64],"big")
            s=b[64:64+ln].decode("utf-8","ignore")
            uri=s
            if s.startswith("data:application/json;base64,"):
                uri=json.loads(base64.b64decode(s.split(",",1)[1]).decode())
        except Exception as e: uri=f"DECODE_FAIL {e} rawlen={len(uri_raw)}"
    out[name]={"address":addr,"code_len":len(code)-2 if code else None,"registry_bytes":reg_bytes,"contractURI":uri}
    print(name,"code_len=",out[name]["code_len"],"registry_bytes=",reg_bytes,"contractURI=",str(uri)[:300],flush=True)
json.dump(out,open("run-2026-11-11-0131-code-uri.json","w"),indent=1)
# Ankr pre-flight: small getLogs 50 blocks via Ankr module path used by scan script
print("PREFLIGHT-ANKR: see scan script preflight (run separately if needed)",flush=True)
# binanceai.fun launched()
MINT="0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
lv=rpc("eth_call",[{"to":MINT,"data":sel("launched()")},"latest"])
print("binanceai launched() raw=",lv,flush=True)
print("DONE")
