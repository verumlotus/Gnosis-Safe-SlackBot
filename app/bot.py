import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Python will raise KeyError is env vars are not set
SAFE_ADDRESS = os.environ['GNOSIS_SAFE_ADDRESS']
ETHERSCAN_API_KEY = os.environ['ETHERSCAN_API_KEY']
SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']

# Limit the number of transactions that we query for
TX_LIMIT = 100

# Custom Exceptions
class FetchTransactionsException(Exception):
    pass

class FetchEtherScanException(Exception):
    pass

def fetch_queued_transactions() -> list:
    # Get the latest nonce of this safe
    url = f'https://safe-transaction.gnosis.io/api/v1/safes/{SAFE_ADDRESS}/'
    response = requests.get(url=url)
    if not response.status_code == 200:
        raise FetchTransactionsException
    json_respose = response.json()
    current_nonce = json_respose['nonce']
    threshold = json_respose['threshold']

    # Fetch transactions 
    url = f'https://safe-transaction.gnosis.io/api/v1/safes/{SAFE_ADDRESS}/all-transactions/'
    params = {
        'limit': str(TX_LIMIT), 
        'executed': 'false', 
        'queued': 'true',
        'trusted': 'true'
    }
    response = requests.get(url=url, params=params)
    if not response.status_code == 200:
        raise FetchTransactionsException
    
    raw_transactions = response.json()['results']
    # Filter for only the queued transactions
    queued_transactions = [tx for tx in raw_transactions if tx['executionDate'] is None and tx['nonce'] >= current_nonce]
    parsed_transactions = list()
    for tx in queued_transactions:
        confirmations = tx.get('confirmations')
        signatures_remaining = threshold - len(confirmations) if confirmations else 'unknown'
        parsed_tx = {
            'safe': tx.get('safe'),
            'to': tx.get('to'),
            'data': tx.get('data'),
            'submissionDate': tx.get('submissionDate'),
            'dataDecoded': tx.get('dataDecoded'),
            'signaturesRemaining': signatures_remaining,
            'transfers': tx.get('transfers')
        }
        parsed_transactions.append(parsed_tx)
    print(parsed_transactions)
    return parsed_transactions

def augment_info_txs(parsed_txs: list[dict]) -> None:
    """Modifies the passed in list of dictionaries with additiona info for each tx"""
    # Add the contract name if it is verified and available on Etherscan
    url = f'https://api.etherscan.io/api/'
    for tx in parsed_txs:
        params = {
            'module': 'contract', 
            'action': 'getsourcecode', 
            'address': tx.get('to'),
            'apikey': ETHERSCAN_API_KEY
        }
        response = requests.get(url=url, params=params)
        if response.status_code != 200:
            raise FetchEtherScanException
        json_response = response.json()
        tx['contractName'] = "Unknown"
        if json_response.get('result'):
           tx['contractName'] = json_response.get("ContractName", "Unknown")

def get_parsed_queued_transactions() -> list[dict]:
    parsed_transactions = fetch_queued_transactions();
    augment_info_txs(parsed_txs=parsed_transactions)
    return parsed_transactions

def post_slack_message():
    queued_txs = get_parsed_queued_transactions()
    text_to_send = f'There are {len(queued_txs)} total queued transactions\n\n'

    for i in range(0, len(queued_txs)):
        tx = queued_txs[i]
        text_to_send += '-' * 5 + f'Transaction #{i}' + '-' * 5 + "\n"
        fields = json.dumps(tx, indent=4).split(',')
        text_to_send += "\n".join(fields)
        text_to_send += "\n" + '-' * 10
        
    requests.post(url=SLACK_WEBHOOK_URL, json={'text': text_to_send})

post_slack_message()