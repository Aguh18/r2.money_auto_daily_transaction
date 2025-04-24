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
    
        # Konversi alamat ke checksum
        checksum_token = w3.to_checksum_address(token_address)
        checksum_spender = w3.to_checksum_address(spender_address)
      
        
        # Inisialisasi kontrak token
        token_contract = w3.eth.contract(address=checksum_token, abi=data.ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_wei = int(amount * (10 ** decimals))
        
        # Periksa allowance saat ini
        current_allowance = token_contract.functions.allowance(account.address, checksum_spender).call()
        if current_allowance >= amount_wei:
            print(f"{appearance.EMOJIS.INFO} {appearance.color_text('Sufficient allowance already exists', appearance.COLORSS.GRAY)}")
            return True
    except Exception as e:
        print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Failed to check allowance: {e}', appearance.COLORSS.RED)}")
        return False
    
        
        
# Fungsi untuk swap USDC ke R2USD

def swap_usdc_to_r2usd(w3, account, amount):
    try:
        # Periksa saldo USDC
        usdc_balance = check_token_balance(w3, account.address, data.USDC_ADDRESS)
        print(f"{appearance.EMOJIS.MONEY} {appearance.color_text(f'Current USDC balance: {usdc_balance:.6f}', appearance.COLORSS.WHITE)}")
        if usdc_balance < amount:
            print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Insufficient USDC balance. You have {usdc_balance:.6f} USDC but trying to swap {amount} USDC.', appearance.COLORSS.RED)}")
            return False
        
        # Pastikan approval token
        if not approve_token(w3, account, data.USDC_ADDRESS, data.USDC_TO_R2USD_CONTRACT, amount):
            print(f"{appearance.EMOJIS.ERROR} {appearance.color_text('Failed to approve USDC for swap', appearance.COLORSS.RED)}")
            return False
        
        # Siapkan kontrak dan data transaksi
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
        
        # Periksa gas price hingga cukup rendah
        MAX_GAS_PRICE_WEI = 12_000_000_000  # 0.00000001 ETH
        while True:
            gas_price = w3.eth.gas_price
            print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Current gas price: {gas_price} wei ({gas_price / 10**18:.12f} ETH)', appearance.COLORSS.GRAY)}")
            if gas_price > MAX_GAS_PRICE_WEI:
                print(f"{appearance.EMOJIS.WARNING} {appearance.color_text(f'Gas price too high: {gas_price / 10**18:.12f} ETH is above maximum 0.00000001 ETH. Waiting for lower gas price...', appearance.COLORSS.YELLOW)}")
                time.sleep(15)  # Tunggu 15 detik sebelum cek ulang
                continue
            break  # Gas price cukup rendah, lanjutkan
        
        # Lanjutkan pembuatan transaksi
        print(f"{appearance.EMOJIS.SWAP} {appearance.color_text(f'Swapping {amount} USDC to R2USD...', appearance.COLORSS.YELLOW)}")
        tx = {
            'to': checksum_contract,
            'data': dat,
            'gas': 500000,
            'gasPrice': gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
            'chainId': data.SEPOLIA_CHAIN_ID
        }
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Transaction sent: {tx_hash.hex()}', appearance.COLORSS.WHITE)}")
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Check on Sepolia Explorer: https://sepolia.etherscan.io/tx/{tx_hash.hex()}', appearance.COLORSS.GRAY)}")
        
        # Tunggu konfirmasi tanpa batas waktu
        description = "Swap USDC to R2USD"
        print(f"{appearance.EMOJIS.LOADING} {appearance.color_text(f'Waiting for {description} confirmation...', appearance.COLORSS.YELLOW)}")
        
        is_success = False
        retries_count= 0
        max_retries = 5
        while retries_count < max_retries:
            retries_count += 1
            try:
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                if receipt:
                    if receipt.status == 0:
                        raise Exception(f"{description} failed (reverted)")
                    is_success = True
                    break  # Keluar dari loop jika dikonfirmasi
            except TransactionNotFound:
                print(f"{appearance.EMOJIS.LOADING} {appearance.color_text(f'{description} still pending, continuing to wait...', appearance.COLORSS.YELLOW)}")
            except Exception as e:
                print(f"{appearance.EMOJIS.WARNING} {appearance.color_text(f'Error while checking {description}: {e}, continuing to wait...', appearance.COLORSS.YELLOW)}")
            time.sleep(15)  # Cek setiap 15 detik
            
        if not is_success:
            print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'{description} failed after {max_retries} retries', appearance.COLORSS.RED)}")
            return False
        
        # Log hasil setelah konfirmasi
        print(f"{appearance.EMOJIS.SUCCESS} {appearance.color_text('Swap confirmed!', appearance.COLORSS.GREEN)}")
        new_usdc_balance = check_token_balance(w3, account.address, data.USDC_ADDRESS)
        new_r2usd_balance = check_token_balance(w3, account.address, data.R2USD_ADDRESS)
        print(f"{appearance.EMOJIS.MONEY} {appearance.color_text(f'New USDC balance: {new_usdc_balance:.6f}', appearance.COLORSS.WHITE)}")
        print(f"{appearance.EMOJIS.MONEY} {appearance.color_text(f'New R2USD balance: {new_r2usd_balance:.6f}', appearance.COLORSS.WHITE)}")
        return True
    
    except Exception as e:
        print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Failed to swap USDC to R2USD: {e}', appearance.COLORSS.RED)}")
        return False
    
def swap_r2usd_to_usdc(w3, account, amount):
    try:
        # Periksa saldo R2USD
        r2usd_balance = check_token_balance(w3, account.address, data.R2USD_ADDRESS)
        print(f"{appearance.EMOJIS.MONEY} {appearance.color_text(f'Current R2USD balance: {r2usd_balance:.6f}', appearance.COLORSS.WHITE)}")
        if r2usd_balance < amount:
            print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Insufficient R2USD balance. You have {r2usd_balance:.6f} R2USD but trying to swap {amount} R2USD.', appearance.COLORSS.RED)}")
            return False
        
        # Pastikan approval token
        if not approve_token(w3, account, data.R2USD_ADDRESS, data.R2USD_TO_USDC_CONTRACT, amount):
            print(f"{appearance.EMOJIS.ERROR} {appearance.color_text('Failed to approve R2USD for swap', appearance.COLORSS.RED)}")
            return False
        
        # Siapkan kontrak dan data transaksi
        token_contract = w3.eth.contract(address=w3.to_checksum_address(data.R2USD_ADDRESS), abi=data.ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_wei = int(amount * (10 ** decimals))
        min_output = int(amount_wei * 0.97)  # 97% dari jumlah input
        
        # Periksa gas price hingga cukup rendah
        MAX_GAS_PRICE_WEI = 12_000_000_000  # 0.00000001 ETH
        while True:
            gas_price = w3.eth.gas_price
            print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Current gas price: {gas_price} wei ({gas_price / 10**18:.12f} ETH)', appearance.COLORSS.GRAY)}")
            if gas_price > MAX_GAS_PRICE_WEI:
                print(f"{appearance.EMOJIS.WARNING} {appearance.color_text(f'Gas price too high: {gas_price / 10**18:.12f} ETH is above maximum 0.00000001 ETH. Waiting for lower gas price...', appearance.COLORSS.YELLOW)}")
                time.sleep(15)  # Tunggu 15 detik sebelum cek ulang
                continue
            break  # Gas price cukup rendah, lanjutkan
        
        # Siapkan data transaksi
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Swapping {amount} R2USD, expecting at least {min_output / (10 ** decimals):.6f} USDC', appearance.COLORSS.GRAY)}")
        dat = (
            data.R2USD_TO_USDC_METHOD_ID +
            '0000000000000000000000000000000000000000000000000000000000000000' +
            '0000000000000000000000000000000000000000000000000000000000000001' +
            w3.to_bytes(amount_wei).rjust(32, b'\0').hex() +
            w3.to_bytes(min_output).rjust(32, b'\0').hex()
        )
        
        # Lanjutkan pembuatan transaksi
        print(f"{appearance.EMOJIS.SWAP} {appearance.color_text(f'Swapping {amount} R2USD to USDC...', appearance.COLORSS.YELLOW)}")
        tx = {
            'to': w3.to_checksum_address(data.R2USD_TO_USDC_CONTRACT),
            'data': dat,
            'gas': 500000,
            'gasPrice': gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
            'chainId': data.SEPOLIA_CHAIN_ID
        }
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Transaction sent: {tx_hash.hex()}', appearance.COLORSS.WHITE)}")
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Check on Sepolia Explorer: https://sepolia.etherscan.io/tx/{tx_hash.hex()}', appearance.COLORSS.GRAY)}")
        
        # Tunggu konfirmasi tanpa batas waktu
        description = "Swap R2USD to USDC"
        print(f"{appearance.EMOJIS.LOADING} {appearance.color_text(f'Waiting for {description} confirmation...', appearance.COLORSS.YELLOW)}")
        
        # ulaingi 5 kali
        is_success = False
        rertry_count = 0
        max_retries = 5
        while rertry_count < max_retries:
            rertry_count += 1
            try:
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                if receipt:
                    if receipt.status == 0:
                        raise Exception(f"{description} failed (reverted)")
                    is_success = True
                    break  # Keluar dari loop jika dikonfirmasi
            except TransactionNotFound:
                print(f"{appearance.EMOJIS.LOADING} {appearance.color_text(f'{description} still pending, continuing to wait...', appearance.COLORSS.YELLOW)}")
            except Exception as e:
                print(f"{appearance.EMOJIS.WARNING} {appearance.color_text(f'Error while checking {description}: {e}, continuing to wait...', appearance.COLORSS.YELLOW)}")
            time.sleep(15)  # Cek setiap 15 detik
        
        if not is_success:
            print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'{description} failed after {max_retries} retries', appearance.COLORSS.RED)}")
            return False
        
        # Log hasil setelah konfirmasi
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

        # Periksa saldo R2USD
        r2usd_balance = check_token_balance(w3, account.address, data.R2USD_ADDRESS)
        print(f"{appearance.EMOJIS.MONEY} {appearance.color_text(f'Current R2USD balance: {r2usd_balance:.6f}', appearance.COLORSS.WHITE)}")
        if r2usd_balance < amount:
            print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Insufficient R2USD balance. You have {r2usd_balance:.6f} R2USD but trying to stake {amount} R2USD.', appearance.COLORSS.RED)}")
            return False
        
        # Pastikan approval token
        if not approve_token(w3, account, data.R2USD_ADDRESS, data.STAKE_R2USD_CONTRACT, amount):
            print(f"{appearance.EMOJIS.ERROR} {appearance.color_text('Failed to approve R2USD for staking', appearance.COLORSS.RED)}")
            return False
        
        # Siapkan kontrak dan data transaksi
        token_contract = w3.eth.contract(address=w3.to_checksum_address(data.R2USD_ADDRESS), abi=data.ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_wei = int(amount * (10 ** decimals))
        
        # Siapkan data transaksi
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Staking {amount} R2USD...', appearance.COLORSS.GRAY)}")
        tx_data = (
            data.STAKE_R2USD_METHOD_ID +
            w3.to_bytes(amount_wei).rjust(32, b'\0').hex() +
            '0' * 576  # Padding seperti di JavaScript
        )
        
        # Periksa gas price hingga cukup rendah
        MAX_GAS_PRICE_WEI = 12_000_000_000  # 0.00000001 ETH
        while True:
            gas_price = w3.eth.gas_price
            print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Current gas price: {gas_price} wei ({gas_price / 10**18:.12f} ETH)', appearance.COLORSS.GRAY)}")
            if gas_price > MAX_GAS_PRICE_WEI:
                print(f"{appearance.EMOJIS.WARNING} {appearance.color_text(f'Gas price too high: {gas_price / 10**18:.12f} ETH is above maximum 0.00000001 ETH. Waiting for lower gas price...', appearance.COLORSS.YELLOW)}")
                time.sleep(15)  # Tunggu 15 detik sebelum cek ulang
                continue
            break  # Gas price cukup rendah, lanjutkan
        
        # Lanjutkan pembuatan transaksi
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
            'gasPrice': gas_price,
            'nonce': w3.eth.get_transaction_count(account.address, 'pending'),
            'chainId': data.SEPOLIA_CHAIN_ID
        }
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Transaction sent: {tx_hash.hex()}', appearance.COLORSS.WHITE)}")
        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Check on Sepolia Explorer: https://sepolia.etherscan.io/tx/{tx_hash.hex()}', appearance.COLORSS.GRAY)}")
        
        # Tunggu konfirmasi tanpa batas waktu
        description = "Stake R2USD"
        print(f"{appearance.EMOJIS.LOADING} {appearance.color_text(f'Waiting for {description} confirmation...', appearance.COLORSS.YELLOW)}")
        max_retries = 5
        retry_count = 0
        is_success = False
        while retry_count < max_retries:
            
            retry_count += 1
            try:
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                if receipt:
                    if receipt.status == 0:
                        raise Exception(f"{description} failed (reverted)")
                    is_success = True
                    break  # Keluar dari loop jika dikonfirmasi
            except TransactionNotFound:
                print(f"{appearance.EMOJIS.LOADING} {appearance.color_text(f'{description} still pending, continuing to wait...', appearance.COLORSS.YELLOW)}")
            except Exception as e:
                print(f"{appearance.EMOJIS.WARNING} {appearance.color_text(f'Error while checking {description}: {e}, continuing to wait...', appearance.COLORSS.YELLOW)}")
            time.sleep(15)  # Cek setiap 15 detik
        if not is_success:
            print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Failed to confirm transaction after {max_retries} retries.', appearance.COLORSS.RED)}")
            return False
        
        
        # Log hasil setelah konfirmasi
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
    