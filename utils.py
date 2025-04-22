# Standard library imports
import os
import re
import time
import random
from datetime import datetime, timedelta


# Third-party imports
import asyncio
import requests
from eth_account import Account
from web3 import AsyncWeb3, Web3
from web3.exceptions import ContractLogicError, TransactionNotFound

# Local imports
import appearance
import data

def wait_until_next_day():
    now = datetime.now()

    # Random waktu antara jam 14:00 sampai 17:00
    random_hour = random.randint(14, 17)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)

    next_run_time = datetime(now.year, now.month, now.day, random_hour, random_minute, random_second)

    # Cek apakah waktu sekarang > next_run_time atau selisihnya < 8 jam
    if now > next_run_time or (next_run_time - now).total_seconds() < 8 * 60 * 60:
        next_run_time += timedelta(days=1)

    print(f"{appearance.EMOJIS.INFO} {appearance.color_text('Next run scheduled at ' + next_run_time.strftime('%Y-%m-%d %H:%M:%S'), appearance.COLORSS.GRAY)}")

    while True:
        now = datetime.now()
        time_remaining = next_run_time - now

        if time_remaining.total_seconds() <= 0:
            break

        # Tampilkan countdown (format: jam:menit:detik)
        countdown = str(time_remaining).split('.')[0]
        print(f"{appearance.EMOJIS.LOADING} {appearance.color_text('Countdown: ' + countdown, appearance.COLORSS.GRAY)}", end='\r')

        time.sleep(1)

    print()  # newline setelah countdown selesai
    print(f"{appearance.EMOJIS.INFO} {appearance.color_text('It is now time to run the next transaction!', appearance.COLORSS.GRAY)}")



def send_telegram_message(message, parse_mode="Markdown"):
    telegram_url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
    payload = {
        "chat_id": os.getenv('TELEGRAM_CHAT_ID'),
        "text": message,
        "parse_mode": parse_mode  # Menambahkan parameter parse_mode
    }
    try:
        response = requests.post(telegram_url, json=payload)
        if response.status_code == 200:
            print("Telegram notification sent to private chat")
        else:
            print("Failed to send Telegram notification:")
    except Exception as e:
        print("Failed to send Telegram notification")

def is_valid_private_key(key):
    clean_key = key[2:] if key.startswith('0x') else key
    return bool(re.match(r'^[0-9a-fA-F]{64}$', clean_key))


def check_eth_balance(w3, wallet_address):
    try:
        balance = w3.eth.get_balance(wallet_address)
        return w3.from_wei(balance, 'ether')
    except Exception as e:
        print(f"{appearance.EMOJI['ERROR']} {appearance.color_text(f'Failed to check ETH balance: {e}', appearance.COLORS['RED'])}")
        return 0

# Fungsi untuk memeriksa saldo token ERC20
def check_token_balance(w3, wallet_address, token_address):
    try:
        # Konversi alamat kontrak ke format checksum
        checksum_address = w3.to_checksum_address(token_address)
        token_contract = w3.eth.contract(address=checksum_address, abi=data.ERC20_ABI)
        balance = token_contract.functions.balanceOf(wallet_address).call()
        decimals = token_contract.functions.decimals().call()
        return balance / (10 ** decimals)
    except Exception as e:
        print(f"{appearance.EMOJI['ERROR']}  {appearance.color_text(f'Failed to check balance for token {token_address}: {e}', appearance.COLORS['RED'])}")
        return 0


def approve_token(w3, account, token_address, spender_address, amount):
    try:
        checksum_token = w3.to_checksum_address(token_address)
        checksum_spender = w3.to_checksum_address(spender_address)
        token_contract = w3.eth.contract(address=checksum_token, abi=data.ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_wei = int(amount * (10 ** decimals))
        current_allowance = token_contract.functions.allowance(account.address, checksum_spender).call()
        
        if current_allowance >= amount_wei:
            print(f"{appearance.EMOJIS.INFO} {appearance.color_text('Sufficient allowance already exists', appearance.COLORSS.GRAY)}")
            return True
        
        print(f"{appearance.EMOJIS.LOADING} {appearance.color_text(f'Approving {amount} tokens for spending...', appearance.COLORSS.YELLOW)}")
        
        # Transaction parameters
        base_gas_price = w3.eth.gas_price
        max_retries = 3
        retry_delay = 30  # seconds
        gas_multiplier = 1.2  # Increase gas price by 20% each retry
        
        for attempt in range(max_retries):
            gas_price = int(base_gas_price * (gas_multiplier ** attempt))
            tx = token_contract.functions.approve(checksum_spender, amount_wei).build_transaction({
                'from': account.address,
                'gas': 100000,
                'nonce': w3.eth.get_transaction_count(account.address),
                'gasPrice': gas_price,
                'chainId': data.SEPOLIA_CHAIN_ID
            })
            signed_tx = account.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Approval transaction sent (attempt {attempt + 1}): {tx_hash.hex()}', appearance.COLORSS.WHITE)}")
            print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Check on Sepolia Explorer: https://sepolia.etherscan.io/tx/{tx_hash.hex()}', appearance.COLORSS.GRAY)}")
            
            # Wait for confirmation with timeout
            start_time = time.time()
            while time.time() - start_time < retry_delay:
                try:
                    receipt = w3.eth.get_transaction_receipt(tx_hash)
                    if receipt:
                        if receipt.status == 0:
                            raise Exception("Approval transaction failed")
                        print(f"{appearance.EMOJIS.SUCCESS} {appearance.color_text('Approval confirmed', appearance.COLORSS.GREEN)}")
                        return True
                except TransactionNotFound:
                    pass
                time.sleep(5)  # Check every 5 seconds
            
            print(f"{appearance.EMOJIS.WARNING} {appearance.color_text(f'Transaction not confirmed after {retry_delay} seconds, increasing gas price...', appearance.COLORSS.YELLOW)}")
        
        raise Exception(f"Approval transaction not confirmed after {max_retries} attempts")
    
    except Exception as e:
        print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Failed to approve token: {e}', appearance.COLORSS.RED)}")
        return False
    try:
        checksum_token = w3.to_checksum_address(token_address)
        checksum_spender = w3.to_checksum_address(spender_address)
        token_contract = w3.eth.contract(address=checksum_token, abi=data.ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_wei = int(amount * (10 ** decimals))
        current_allowance = token_contract.functions.allowance(account.address, checksum_spender).call()
        
        if current_allowance >= amount_wei:
            print(f"{appearance.EMOJIS.INFO} {appearance.color_text('Sufficient allowance already exists', appearance.COLORSS.GRAY)}")
            return True
        
        print(f"{appearance.EMOJIS.LOADING} {appearance.color_text(f'Approving {amount} tokens for spending...', appearance.COLORSS.YELLOW)}")
        tx = token_contract.functions.approve(checksum_spender, amount_wei).build_transaction({
            'from': account.address,
            'gas': 100000,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gasPrice': w3.eth.gas_price,
            'chainId': data.SEPOLIA_CHAIN_ID
        })
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Approval transaction sent: {tx_hash.hex()}', appearance.COLORSS.WHITE)}")
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Check on Sepolia Explorer: https://sepolia.etherscan.io/tx/{tx_hash.hex()}', appearance.COLORSS.GRAY)}")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 0:
            raise Exception("Approval transaction failed")
        print(f"{appearance.EMOJIS.SUCCESS} {appearance.color_text('Approval confirmed', appearance.COLORSS.GREEN)}")
        return True
    except Exception as e:
        print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Failed to approve token: {e}', appearance.COLORSS.RED)}")
        return False
    
# Fungsi untuk swap USDC ke R2USD
def swap_usdc_to_r2usd(w3, account, amount):
    try:
        
        usdc_balance = check_token_balance(w3, account.address, data.USDC_ADDRESS)
        print(f"{appearance.EMOJIS.MONEY} {appearance.color_text(f'Current USDC balance: {usdc_balance:.6f}', appearance.COLORSS.WHITE)}")
        if usdc_balance < amount:
            print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Insufficient USDC balance. You have {usdc_balance:.6f} USDC but trying to swap {amount} USDC.', appearance.COLORSS.RED)}")
            return False
        
        if not approve_token(w3, account, data.USDC_ADDRESS, data.USDC_TO_R2USD_CONTRACT , amount):
            return False
        
        checksum_contract = w3.to_checksum_address(data.USDC_TO_R2USD_CONTRACT)
        token_contract = w3.eth.contract(address=w3.to_checksum_address(data.USDC_ADDRESS), abi=data.ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_wei = int(amount * (10 ** decimals))
        
        dat = (
            data.USDC_TO_R2USD_METHOD_ID +
            w3.to_bytes(hexstr=account.address).rjust(32, b'\0').hex() +
            w3.to_bytes(amount_wei).rjust(32, b'\0').hex() +
            '0' * 64 * 5  # Placeholder untuk parameter lain
        )
        
        print(f"{appearance.EMOJIS.SWAP} {appearance.color_text(f'Swapping {amount} USDC to R2USD...', appearance.COLORSS.YELLOW)}")
        tx = {
            'to': checksum_contract,
            'data':dat,
            'gas': 500000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
            'chainId': data.SEPOLIA_CHAIN_ID
        }
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Transaction sent: {tx_hash.hex()}', appearance.COLORSS.WHITE)}")
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Check on Sepolia Explorer: https://sepolia.etherscan.io/tx/{tx_hash.hex()}', appearance.COLORSS.GRAY)}")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 0:
            raise Exception("Swap transaction failed")
        
        print(f"{appearance.EMOJIS.SUCCESS} {appearance.color_text('Swap confirmed!', appearance.COLORSS.GREEN)}")
        new_usdc_balance = check_token_balance(w3, account.address, data.USDC_ADDRESS)
        new_r2usd_balance = check_token_balance(w3, account.address, data.R2USD_ADDRESS)  
        print(f"{appearance.EMOJIS.MONEY} {appearance.color_text(f'New USDC balance: {new_usdc_balance:.6f}', appearance.COLORSS.WHITE)}")
        print(f"{appearance.EMOJIS.MONEY} {appearance.color_text(f'New R2USD balance: {new_r2usd_balance:.6f}', appearance.COLORSS.WHITE)}")
        return True
    except Exception as e:
        print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Failed to swap USDC to R2USD: {e}', appearance.COLORSS.RED)}")
        return False
    
    
# Fungsi untuk swap R2USD ke USDC
def swap_r2usd_to_usdc(w3, account, amount):
    try:
        r2usd_balance = check_token_balance(w3, account.address, data.R2USD_ADDRESS )
        print(f"{appearance.EMOJIS.MONEY} {appearance.color_text(f'Current R2USD balance: {r2usd_balance:.6f}', appearance.COLORSS.WHITE)}")
        if r2usd_balance < amount:
            print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Insufficient R2USD balance. You have {r2usd_balance:.6f} R2USD but trying to swap {amount} R2USD.', appearance.COLORSS.RED)}")
            return False
        
        if not  approve_token(w3, account, data.R2USD_ADDRESS, data.R2USD_TO_USDC_CONTRACT , amount):
            return False
        
        token_contract = w3.eth.contract(address=w3.to_checksum_address(data.R2USD_ADDRESS), abi=data.ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_wei = int(amount * (10 ** decimals))
        min_output = int(amount_wei * 0.97)  # 97% dari jumlah input
        
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Swapping {amount} R2USD, expecting at least {min_output / (10 ** decimals):.6f} USDC', appearance.COLORSS.GRAY)}")
        dat = (
            data.R2USD_TO_USDC_METHOD_ID +
            '0000000000000000000000000000000000000000000000000000000000000000' +
            '0000000000000000000000000000000000000000000000000000000000000001' +
            w3.to_bytes(amount_wei).rjust(32, b'\0').hex() +
            w3.to_bytes(min_output).rjust(32, b'\0').hex()
        )
        
        print(f"{appearance.EMOJIS.SWAP} {appearance.color_text(f'Swapping {amount} R2USD to USDC...', appearance.COLORSS.YELLOW)}")
        tx = {
            'to': w3.to_checksum_address(data.R2USD_TO_USDC_CONTRACT),
            'data': dat,
            'gas': 500000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
            'chainId': data.SEPOLIA_CHAIN_ID
        }
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Transaction sent: {tx_hash.hex()}', appearance.COLORSS.WHITE)}")
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Check on Sepolia Explorer: https://sepolia.etherscan.io/tx/{tx_hash.hex()}', appearance.COLORSS.GRAY)}")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 0:
            raise Exception("Swap transaction failed")
        
        print(f"{appearance.EMOJIS.SUCCESS} {appearance.color_text('Swap confirmed!', appearance.COLORSS.GREEN)}")
        new_usdc_balance = check_token_balance(w3, account.address, data.USDC_ADDRESS)
        new_r2usd_balance = check_token_balance(w3, account.address, data.R2USD_ADDRESS)  
        print(f"{appearance.EMOJIS.MONEY} {appearance.color_text(f'New USDC balance: {new_usdc_balance:.6f}', appearance.COLORSS.WHITE)}")
        print(f"{appearance.EMOJIS.MONEY} {appearance.color_text(f'New R2USD balance: {new_r2usd_balance:.6f}', appearance.COLORSS.WHITE)}")
        return True
    except Exception as e:
        print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Failed to swap R2USD to USDC: {e}', appearance.COLORSS.RED)}")
        return False


# Fungsi untuk stake R2USD



def stake_r2usd(w3, account, amount):
    try:
        # Validasi alamat kontrak
        if w3.eth.get_code(w3.to_checksum_address(data.R2USD_ADDRESS)) == b'':
            raise ValueError("R2USD_ADDRESS is not a valid contract")
        if w3.eth.get_code(w3.to_checksum_address(data.STAKE_R2USD_CONTRACT)) == b'':
            raise ValueError("STAKE_R2USD_CONTRACT is not a valid contract")
        if w3.eth.get_code(w3.to_checksum_address(data.SR2USD_ADDRESS)) == b'':
            raise ValueError("SR2USD_ADDRESS is not a valid contract")

        # Log kode kontrak untuk debugging
        contract_code = w3.eth.get_code(w3.to_checksum_address(data.STAKE_R2USD_CONTRACT))
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Staking contract code length: {len(contract_code)} bytes', appearance.COLORSS.GRAY)}")

        r2usd_balance = check_token_balance(w3, account.address, data.R2USD_ADDRESS)
        print(f"{appearance.EMOJIS.MONEY} {appearance.color_text(f'Current R2USD balance: {r2usd_balance:.6f}', appearance.COLORSS.WHITE)}")
        if r2usd_balance < amount:
            print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Insufficient R2USD balance. You have {r2usd_balance:.6f} R2USD but trying to stake {amount} R2USD.', appearance.COLORSS.RED)}")
            return False
        
        if not approve_token(w3, account, data.R2USD_ADDRESS, data.STAKE_R2USD_CONTRACT, amount):
            return False
        
        token_contract = w3.eth.contract(address=w3.to_checksum_address(data.R2USD_ADDRESS), abi=data.ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_wei = int(amount * (10 ** decimals))
        
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Staking {amount} R2USD...', appearance.COLORSS.GRAY)}")
        tx_data = (
            data.STAKE_R2USD_METHOD_ID +
            w3.to_bytes(amount_wei).rjust(32, b'\0').hex() +
            '0' * 576  # Padding seperti di JavaScript
        )
        
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Executing stake of {amount} R2USD...', appearance.COLORSS.YELLOW)}")
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Prepared tx_data: {tx_data}', appearance.COLORSS.GRAY)}")
        gas_estimate = w3.eth.estimate_gas({
            'to': w3.to_checksum_address(data.STAKE_R2USD_CONTRACT),
            'from': account.address,
            'data': tx_data
        })
        tx = {
            'to': w3.to_checksum_address(data.STAKE_R2USD_CONTRACT),
            'data': tx_data,
            'gas': int(gas_estimate * 1.2),
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address, 'pending'),
            'chainId': data.SEPOLIA_CHAIN_ID
        }
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Transaction sent: {tx_hash.hex()}', appearance.COLORSS.WHITE)}")
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Check on Sepolia Explorer: https://sepolia.etherscan.io/tx/{tx_hash.hex()}', appearance.COLORSS.GRAY)}")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 0:
            raise Exception("Stake transaction failed")
        
        print(f"{appearance.EMOJIS.SUCCESS} {appearance.color_text('Stake confirmed!', appearance.COLORSS.GREEN)}")
        new_r2usd_balance = check_token_balance(w3, account.address, data.R2USD_ADDRESS)
        new_sr2usd_balance = check_token_balance(w3, account.address, data.SR2USD_ADDRESS)
        print(f"{appearance.EMOJIS.MONEY} {appearance.color_text(f'New R2USD balance: {new_r2usd_balance:.6f}', appearance.COLORSS.WHITE)}")
        print(f"{appearance.EMOJIS.MONEY} {appearance.color_text(f'New sR2USD balance: {new_sr2usd_balance:.6f}', appearance.COLORSS.WHITE)}")
        return True
    except ValueError as ve:
        print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Invalid input or contract error: {ve}', appearance.COLORSS.RED)}")
        return False
    except ContractLogicError as cle:
        print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Contract logic error: {cle}. Check contract address, method ID, or contract state.', appearance.COLORSS.RED)}")
        return False
    except Exception as e:
        print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Unexpected error: {e}', appearance.COLORSS.RED)}")
        return False

    