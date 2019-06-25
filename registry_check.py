#!/usr/bin/env python3"
from liquid_rpc_class import RPCHost
import wallycore as wally
import json
import struct
import re
import requests

registryURL = 'https://assets.blockstream.info/'
liquidURL = 'http://username:password@127.0.0.1:7041/wallet/wallet.dat'
explorerURL = 'https://blockstream.info/liquid/api/tx/'


def check_tx(issuance_txid, issuance_vin, asset, explorer):
    if (explorer):
        resp = requests.get(url=explorerURL+issuance_txid, verify=True)
        issuance = resp.json()
        c = issuance['vin'][issuance_vin]['issuance']['asset_entropy'] + '0000000000000000000000000000000000000000000000000000000000000000'
        asset_id = wally.hex_from_bytes(wally.sha256_midstate(wally.hex_to_bytes(c))[::-1])
    else:
        issuance = host.call('getrawtransaction', issuance_txid, 1)
        asset_id = issuance['vin'][issuance_vin]['issuance']['asset']

    return(asset_id == asset)


def check_contract(prev_tx, prev_vout, contract_hash, asset):
    a = wally.hex_from_bytes(wally.hex_to_bytes(prev_tx)[::-1])+wally.hex_from_bytes(struct.pack('<L', int(prev_vout)))
    a = wally.hex_from_bytes(wally.sha256d(wally.hex_to_bytes(a)))
    b = a + contract_hash
    merkle = wally.hex_from_bytes(wally.sha256_midstate(wally.hex_to_bytes(b)))
    c = merkle + '0000000000000000000000000000000000000000000000000000000000000000'
    asset_id = wally.hex_from_bytes(wally.sha256_midstate(wally.hex_to_bytes(c))[::-1])
    return(asset_id == asset)


def check_website(domain, asset):
    asserURL = 'https://'+domain+'/.well-known/liquid-asset-proof-'+asset
    resp = requests.get(url=asserURL, verify=True)
    if (re.match(r'^.*'+domain+'.*'+asset, resp.text)):
        return(True)
    else:
        return(False)


host = RPCHost(liquidURL)
resp = requests.get(url=registryURL, verify=True)
assets = resp.json()
for asset in assets.keys():
    contract = json.dumps(assets[asset]['contract'], separators=(',',':'), sort_keys=True)
    contract_hash = wally.hex_from_bytes(wally.sha256(contract.encode('ascii')))
    prev_tx = assets[asset]['issuance_prevout']['txid']
    prev_vout = assets[asset]['issuance_prevout']['vout']
    issuance_txid = assets[asset]['issuance_txin']['txid']
    issuance_vin = assets[asset]['issuance_txin']['vin']
    domain = assets[asset]['contract']['entity']['domain']

    if(check_contract(prev_tx, prev_vout, contract_hash, asset)):
        contract = 'valid contract'
    else:
        contract = 'invalid contract'

    if(check_tx(issuance_txid, issuance_vin, asset, False)):
        tx = 'valid transaction'
    else:
        tx = 'invalid transaction'

    if (check_website(domain, asset)):
        website = 'valid website'
    else:
        website = 'invalid website'

    print(asset+' has '+contract+', '+tx+' and '+website+'.')
