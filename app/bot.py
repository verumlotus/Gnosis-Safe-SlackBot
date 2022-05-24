import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Python will raise KeyError is env vars are not set
safe_address = os.environ['GNOSIS_SAFE_ADDRESS']

# Limit the number of transactions that we query for
TX_LIMIT = 100

# Custom Exceptions
class FetchTransactionsException(Exception):
    pass

def fetch_queued_transactions() -> list:
    # Get the latest nonce of this safe
    url = f'https://safe-transaction.gnosis.io/api/v1/safes/{safe_address}/'
    response = requests.get(url=url)
    if not response.status_code == 200:
        raise FetchTransactionsException
    json_respose = response.json()
    current_nonce = json_respose['nonce']
    threshold = json_respose['threshold']

    # Fetch transactions 
    url = f'https://safe-transaction.gnosis.io/api/v1/safes/{safe_address}/all-transactions/'
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
        signatures_remaining = threshold - confirmations if confirmations else 'unknown'
        parsed_tx = {
            'safe': tx.get('safe'),
            'to': tx.get('to'),
            'data': tx.get('data'),
            'submissionDate': tx.get('submissionDate'),
            'dataDecoded': tx.get('dataDecoded'),
            'signaturesRemaining': signatures_remaining
        }
        parsed_transactions.append(parsed_tx)
    print(parsed_transactions)
    return parsed_transactions



fetch_queued_transactions()