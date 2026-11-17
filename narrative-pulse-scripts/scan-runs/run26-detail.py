#!/usr/bin/env python3
import json, sys, time
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home()/"workspace/fast_exec"))
import fast_rpc
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def dec_str(hexdata):
    try:
        b=bytes.fromhex(hexdata[2:])
        if len(b)<96: return None
        off=int.from_bytes(b[0:32],"big"); ln=int.from_bytes(b[off:off+32],"big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception: return None
def topic(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()
T_TRANSFER=topic("Transfer(address,address,uint256)")
T_SINGLE=topic("TransferSingle(address,address,address,uint256,uint256)")
ZERO="0x"+"0"*64
TXS=["0x0f8c6f8ed5fd6f1c663dcf56b7616790d9714515be49a2d2692e9a9d752d0781",
"0x49b77c6dc235b8cad2c4552daf3d798816a7ea87283b79def593b0bbce74269a",
"0xc1f7d71d0ce44d59240676cf852b8cce3b7e6603d2c027e9a884b7759cf5e864"]
for h in TXS:
    r=fast_rpc.race("eth_getTransactionReceipt",[h])
    print("TX",h,"status",r.get("status"),"block",int(r.get("blockNumber"),16) if r.get("blockNumber") else None)
    for lg in r.get("logs") or []:
        tp=lg.get("topics") or []
        print("  log addr",lg.get("address"),"topics",tp,"data",lg.get("data"))
    time.sleep(4)
    # tx value
    tx=fast_rpc.race("eth_getTransactionByHash",[h])
    print("  tx to",tx.get("to"),"value",tx.get("value"),"input", (tx.get("input") or "")[:40])
    time.sleep(4)
for addr in ["0xdc11764a5664e333c8d303eb465e89a1caadb85b","0xf9a314e76855cab1f676ddbe77a5a91fa163da53","0x65b1721bf9ba3ea504bb13fd89d47abc13c739a5"]:
    out={}
    for fn in ["name()","symbol()","owner()"]:
        try:
            r=fast_rpc.race("eth_call",[{"to":addr,"data":sel(fn)},"latest"])
            out[fn]=dec_str(r) if fn!="owner()" else ("0x"+r[-40:] if r and len(r)>=42 else r)
        except Exception as e: out[fn]=f"ERROR {e}"[:200]
        time.sleep(4)
    for fn in ["decimals()"]:
        try:
            r=fast_rpc.race("eth_call",[{"to":addr,"data":sel(fn)},"latest"])
            out[fn]=int(r,16) if r else None
        except Exception as e: out[fn]=f"ERROR {e}"[:200]
        time.sleep(4)
    print(addr, out)
