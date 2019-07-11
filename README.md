# Issue Liquid assets on multisig addresses
In this example, we will show how to create assets on Liquid in two 2-of-2 multisig addresses (one for the assets and one for the reissuance tokens).

## Install Liquid
Download Liquid from the [GitHub Releases page](https://github.com/ElementsProject/elements/releases), version 0.17 is necessary to run the following scripts.

## Create wallets and configure
In order to configure your Liquid regtest and create the wallets you need to write a configuration file for the liquid instance.
```
chain=elementsregtest
daemon=1
listen=1
validatepegin=0

initialfreecoins=2100000000000000

rpcuser=username
rpcpassword=password
elementsregtest.rpcallowip=0.0.0.0/0
elementsregtest.rpcport=18891
elementsregtest.port=18893

txindex=1

elementsregtest.wallet=wallet.dat
elementsregtest.wallet=wallet_1.dat
elementsregtest.wallet=wallet_2.dat
elementsregtest.wallet=wallet_3.dat
```

Save this file in the configuration folder (e.g. ~/.liquid/liquid.conf) and run the  liquidd executable.

Configure the file `liquid_utils.py` with the correct username, password and IP address for each wallet involved.

If you start with a fresh regtest you will need to move some funds from your wallet to your wallet_1. You can use the command `liquid-cli -rpcwallet=wallet.dat sendtoaddress $(liquid-cli -rpcwallet=wallet_1.dat getnewaddress) 1000` then you can generate a block `liquid-cli -rpcwallet=wallet.dat generate 1` and finally check balance of your wallet_1 `liquid-cli -rpcwallet=wallet_1.dat getbalance "*" 0 true`.

If your regtest wallet has funds or you are using mainnet you don't need to execute the previous commands.

We will use 4 wallets in this way:
- `wallet` to generate blocks and move funds (the "miner")
- `wallet_1` and `wallet_2` to create the multisig for assets and tokens (the "cosigners")
- `wallet_3` for receive assets (the "receiver")

## Create the environment
Create and activate a virtual environment for python 3.

```
virtualenv -p python3 venv3
source venv3/bin/activate
pip install -r requirements.txt
```
Remember to call this scripts from the virtualenv.

## Issue assets
The first step is issuing an asset compatible with the asset registry requirements. The assets and the reissuance tokens will be sent to two 2 of 2 multisig wallet (between wallet_1 and wallet_2).

### Configure
he parameters needed to make the issuance compatible with the asset registry can be found in the file issue.py. You will need to specify:
- a pubkey (in hexadecimal format) corresponding to a privkey controlled by the issuer; this key will be used to sign update messages for the asset registry (allowing future updates to the asset registry)
- a name for your asset (<255 ASCII chars)
- a ticker (3 or 4 ASCII chars)
- the precision, corresponding to the position shift of the point with respect to satoshis (in other words the digits after the decimal separator when you represent values in satoshi).
E.g.
Asset amount 0.00000020 == 20 satoshi with precision 0 -> 20 assets
Asset amount 0.00000315 == 315 satoshi with precision 2 -> 3,15 assets
Asset amount 1.00000000 ==  100000000 satoshi with precision 8 -> 1 assets

- the domain connected with the issuance (you will need to publish a file in the folder .well-known of this server)

Modify the variables in the file `issue.py` before calling the scripts.

```
...
# FIXME: contract information (all required for asset registry)
issuer_pubkey = ''
name = 'asset name'
ticker = 'XYZ'
precision = 0
domain = 'domain.com'
version = 0 # don't change
...
```

### Exec the script
After configuration, you can call the script passing all the arguments needed.

`Usage: python issue.py ASSET_AMOUNT ASSET_ADDRESS REISSUANCE_TOKEN_AMOUNT REISSUANCE_TOKEN_ADDRESS`

The script `create_multisig.py` helps creating multisig addresses between `wallet_1` and `wallet_2` and can be used called in a simple shell script like the following.

```
echo "Create multisig issuance"
ASSET_AMOUNT="0.00000020"
REISSUANCE_TOKEN_AMOUNT="0.00000005"
echo "   Create multisig address for the asset"
MULTISIG_ASSET=$(python create_multisig.py asset)
MULTISIG_ASSET_ADDRESS=$(echo $MULTISIG_ASSET | jq -r .multisig)
echo "   Create multisig address for the reissuance token"
MULTISIG_REISSUANCE=$(python create_multisig.py reissuance)
MULTISIG_REISSUANCE_ADDRESS=$(echo $MULTISIG_REISSUANCE | jq -r .multisig)
echo "   Create the issuance transaction (information available in the file TX_ISSUANCE.txt)"
TX_ISSUANCE=$(python issue.py $ASSET_AMOUNT $MULTISIG_ASSET_ADDRESS $REISSUANCE_TOKEN_AMOUNT $MULTISIG_REISSUANCE_ADDRESS)
echo $TX_ISSUANCE > TX_ISSUANCE.txt
```
In this example are generated 20 asset tokens and 5 reissuance tokens (consider precision = 0), you can check balance of `wallet_1` using the command `liquid-cli -rpcwallet=wallet_1.dat getbalance "*" 0 true`.

In the file TX_ISSUANCE.txt you can read all the information about the issuance and you can find the contract JSON code fragment, we will use this code for the asset registry request.

The issuance transaction is built on the basis of a simple transaction, in our case a simple transaction with op_return, on which the fees are calculated. Obviously, the fees must be increased (acting on the used feerate on the fundrawtransaction call) in order to cover the weight of the final transaction.

If the fees are too low, they can be increased by changing the value of the variable `feerate` on the script `issue.py`.

## Register the asset on asset registry
After the issuance, you can register the token in the asset registry following these steps.

```
CONTRACT=$(echo $TX_ISSUANCE  | jq -r .contract)
ASSET=$(echo $TX_ISSUANCE | jq -r .asset_id)
TXID=$(echo $TX_ISSUANCE | jq -r .txid)
ISSUANCE_TX=$(echo $TX_ISSUANCE | jq -r .txid)
DOMAIN=$(echo $TX_ISSUANCE | jq -r .contract |jq -r .entity.domain)

echo "curl https://assets.blockstream.info/ --data-raw '{\"asset_id\":\"$ASSET\",\"contract\":$CONTRACT,\"issuance_txin\":{\"txid\":\"$ISSUANCE_TX\",\"vin\":0}}'" > register_asset.sh
echo "Authorize linking the domain name $DOMAIN to the Liquid asset $ASSET" > liquid-asset-proof-$ASSET
```

Copy the generated file `liquid-asset-proof-...` in the folder `.well-known` of the same server specified in the contract.

Execute the script `register_asset.sh` or perform a simple curl call to inform the registry about the new issuance.

The asset registry will check all information about the issuance and will search for the liquid asset proof file in the specified domain.

## Move asset from the multisig address
The script send_assets.py shows how we can send a certain amount of assets to another address (multisig or not), sending the change back to another multisig.

`Usage: python send_assets.py ASSET ASSET_ADDRESS ASSET_AMOUNT ASSET_CHANGE_ADDRESS`

All the information needed can be obtained using the following script.

```
echo "Send some tokens to a singlesig address"
ASSET=$(echo $TX_ISSUANCE | jq -r .asset_id)
AMOUNT="0.00000001"
echo "   Get a receiving address (on wallet_3)"
RECEIVING_ADDRESS=$(python get_address.py receiver | jq -r .address)
echo "   Create a multisig change address"
MULTISIG_ASSET_CHANGE=$(python create_multisig.py change)
MULTISIG_ASSET_CHANGE_ADDRESS=$(echo $MULTISIG_ASSET_CHANGE | jq -r .multisig)
echo "   Create the transaction (information available in the file TX_SEND.txt)"
TX_SEND=$(python send_assets.py $ASSET $RECEIVING_ADDRESS $AMOUNT $MULTISIG_ASSET_CHANGE_ADDRESS)
echo $TX_SEND > TX_SEND.txt
```
In this case I'm moving 1 asset token from my multisig (`wallet_1` and `wallet_2`) to a singlesig address controlled by `wallet_3`. The remaining assets are moved to a new multisig address. The asset id is found from the data saved from the previous step.

You can check the balance of `wallet_3` using `liquid-cli -rpcwallet=wallet_3.dat getbalance`.

## Reissuance assets from a multisig address
If we want to issue more assets we can use the reissuance token, the reissuance.py script shows how we can reissue assets using tokens held in a multisig wallet.

`Usage: python reissuance.py AMOUNT ASSET_ADDRESS ENTROPY REISSUANCE_TOKEN REISSUANCE_TOKEN_ADDRESS REISSUANCE_TOKEN_CHANGE_ADDRESS`

Like before we can use some scripts in order to calculate new multisig addresses for change outputs and new assets.

```
echo "Reissue and asset using a reissunce token present in a multisig wallet"
AMOUNT="0.00000300"
echo "   Create a multisig address for the asset"
MULTISIG_ASSET_REISSUANCE=$(python create_multisig.py "asset reissuance")
MULTISIG_ASSET_REISSUANCE_ADDRESS=$(echo $MULTISIG_ASSET_REISSUANCE | jq -r .multisig)
echo "   Get asset and token information"
ASSET_ENTROPY=$(echo $TX_ISSUANCE | jq -r .decoded_raw_transaction.vin[0].issuance.assetEntropy)
REISSUANCE_TOKEN=$(echo $TX_ISSUANCE | jq -r .decoded_raw_transaction.vin[0].issuance.token)
echo "   Create a multisig address for the reissuance token"
REISSUANCE_TOKEN_MULTISIG=$(python create_multisig.py "token reissuance")
REISSUANCE_TOKEN_ADDRESS=$(echo $REISSUANCE_TOKEN_MULTISIG | jq -r .multisig)
echo "   Create a multisig change address for the reissuance token"
REISSUANCE_TOKEN_CHANGE=$(python create_multisig.py "token reissuance change")
REISSUANCE_TOKEN_CHANGE_ADDRESS=$(echo $REISSUANCE_TOKEN_CHANGE | jq -r .multisig)
echo "   Create the reissuance transaction (information available in the file TX_REISSUANCE.txt)"
TX_REISSUANCE=$(python reissuance.py $AMOUNT $MULTISIG_ASSET_REISSUANCE_ADDRESS $ASSET_ENTROPY $REISSUANCE_TOKEN $REISSUANCE_TOKEN_ADDRESS $REISSUANCE_TOKEN_CHANGE_ADDRESS)
echo $TX_REISSUANCE > TX_REISSUANCE.txt
```
In this case we are creating 300 new assets, the reissuance token will be moved in a new multisig address.

As already discussed in the case of the `issue.py` script, if the fees are too low, the value of the variable `feerate` in the `reissuance.py` script can be increased.
