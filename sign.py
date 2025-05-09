from bitcoinlib.transactions import Transaction
from bitcoinlib.keys import Key
from conf import COIN_CONFIG
import common, json, questionary

# this script should be deployed on offline device for signing the transaction with your private key
# make sure a file named "tx" has been put in the same folder which includes the transaction data created in online devices

tx_file = "tx"
signed_tx = "signed_tx"
coin_name: str

def sign():
    network = COIN_CONFIG[coin_name]["network"] 
    witness_type = COIN_CONFIG[coin_name]["witness_type"]

    with open(tx_file, 'r') as file:
        content = json.load(file)    

    # loop all input and get all addresses
    addresses = []
    for inp in content["inputs"]:
        addresses.append(inp["address"])

    # remove duplicate
    new_addresses = list(set(addresses))

    # collect pk and associated to address
    pk_obj = {}
    for idx, address in enumerate(new_addresses):
        pk = questionary.text("Type WIF private key for address [" + address + "]: ", validate=lambda text: len(text) > 0).ask()
        k = Key.from_wif(pk, network=network)
        pk_obj[address] = k

    t = Transaction(fee_per_kb=content["fee"] * 1000, network=network, witness_type=witness_type)

    for inp in content["inputs"]:
        t.add_input(prev_txid=inp["txid"], output_n=inp["output_n"], address=inp["address"], value=inp["value"],
            witness_type=witness_type, sequence=4294967293)

    for otp in content["outputs"]:
        if otp["change"]:
            print("transaction size:", t.estimate_size())
            fee = t.calculate_fee()
            print("total fee (sats):", fee)
            t.add_output(otp["amount"] - fee, otp["address"])
        else:
            t.add_output(otp["amount"], otp["address"])   
        
    # sign with pk for each input   
    for idx, address in enumerate(addresses):
        k = pk_obj[address]
        t.sign(keys=[k], index_n=idx)

    with open(signed_tx, 'w') as file:
        file.write(t.raw_hex())
        print(t.raw_hex())


if __name__ == "__main__":
    coin_name = common.choose_coin()
    sign()