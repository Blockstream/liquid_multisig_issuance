#!/usr/bin/env python3
from liquid_rpc_class import RPCHost
import json
import sys
from liquid_utils import connect, generate

reissuance_token_amount = 0.00000001

feerate = 0.00003000

if len (sys.argv) != 7 :
    print('Usage: python '+sys.argv[0]+' AMOUNT ASSET_ADDRESS ENTROPY REISSUANCE_TOKEN REISSUANCE_TOKEN_ADDRESS REISSUANCE_TOKEN_CHANGE_ADDRESS' )
    sys.exit (1)

amount = sys.argv[1]
asset_address = sys.argv[2]
entropy = sys.argv[3]
reissuance_token = sys.argv[4]
reissuance_token_address = sys.argv[5]
reissuance_token_change_address = sys.argv[6]

res = {}
host_1, host_2, host_3 = connect()

# Prepare base transaction for reissuance
base = host_1.call('createrawtransaction', [], {reissuance_token_address:reissuance_token_amount}, 0, False, {reissuance_token_address:reissuance_token})
bitcoin_change = host_1.call('getrawchangeaddress')
funded = host_1.call('fundrawtransaction', base, {'feeRate': feerate, 'includeWatching': True, 'changeAddress': {'bitcoin': bitcoin_change, reissuance_token: reissuance_token_change_address}})

# Find info about the token output
utxo_info = None
unspents = host_1.call('listunspent')
for utxo in unspents:
    if utxo["asset"] == reissuance_token:
        utxo_info = utxo
        break
assert(utxo_info is not None)

reissuance_index = -1
asset_commitments = []
for i, tx_input in enumerate(host_1.call('decoderawtransaction',funded['hex'])["vin"]):
    if tx_input["txid"] == utxo_info["txid"] and tx_input["vout"] == utxo_info["vout"]:
        reissuance_index = i
    for u in unspents:
        if tx_input["txid"] == u["txid"] and tx_input["vout"] == u["vout"]:
            asset_commitments.append(u["assetcommitment"])
            break
assert(reissuance_index != -1)
res['asset_commitments'] = asset_commitments

# Create the reissuance transaction
reissuance = host_1.call('rawreissueasset', funded['hex'], [{'input_index':reissuance_index, 'asset_amount':round(float(amount), 8), 'asset_address':asset_address, 'asset_blinder':utxo_info['assetblinder'], 'entropy':entropy}])
res['reissuance'] = reissuance

# Blind transaction
blind_issuances = False
blinded_raw_tx = host_1.call('blindrawtransaction', reissuance['hex'], True, asset_commitments, blind_issuances)

# Sign multisig transaction
signed_raw_tx = host_1.call('signrawtransactionwithwallet', blinded_raw_tx)
signed_raw_tx_2 = host_2.call('signrawtransactionwithwallet', signed_raw_tx['hex'])
# if N>2 add other signers

test = host_1.call('testmempoolaccept', [signed_raw_tx_2['hex']])
res['testmempoolaccept'] = str(test)

if test[0]['allowed'] == True :
    tx = host_1.call('sendrawtransaction', signed_raw_tx_2['hex'])
    res['txid'] = tx
    generate()

print(json.dumps(res, indent=4, sort_keys=True))
