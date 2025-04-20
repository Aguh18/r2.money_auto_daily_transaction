import utils
import appearance
import data
from web3 import Web3
from dotenv import load_dotenv
import os
import time
import random

load_dotenv()

if __name__ == "__main__":
    
    print(appearance.ASCII_ART)
    print(appearance.CREDIT)
  
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    swap_total= os.getenv("USDC_SPENDING_AMOUNT")
    swap_count = 150
    swap_amount = int(swap_total) / swap_count
    stake_count = 12
    stake_amount = (int(swap_total)-10) / stake_count 
    is_loop = False
    
    while True:
        answer = input(
            "do you want the transaction to run only once, or should it be automated to run every day? (automation requires a vps) [once/auto]: "
        ).strip().lower()

        if answer == 'auto':
            is_loop = True
            break  # Exit the loop after valid input
        elif answer == 'once':
            is_loop = False
            break  # Exit the loop after valid input
        else:
            print("invalid input. please enter 'once' or 'auto'.")




    while True:
        
  
        if not utils.is_valid_private_key(PRIVATE_KEY) :
            print(f"{appearance.EMOJI['ERROR']} {appearance.color_text('Invalid private key.', appearance.COLORS['RED'])}")
            exit(1)
        
        w3 = Web3(Web3.HTTPProvider(data.RPC_URL))
        
        
        if not w3.is_connected():
            print(f"{appearance.EMOJI['ERROR']} {appearance.color_text('Failed to connect to Sepolia Testnet', appearance.COLORS['RED'])}")
            continue
        print(f"{appearance.EMOJI['SUCCESS']} {appearance.color_text(f'Connected to Sepolia Testnet: {data.RPC_URL}', appearance.COLORS['GREEN'])}")
        
    # Inisialisasi wallet
        account = w3.eth.account.from_key(PRIVATE_KEY)
        wallet_address = account.address
        print(f"\n{appearance.EMOJI['WALLET']}  {appearance.color_text(f'Wallet: {wallet_address}', appearance.COLORS['CYAN'])}")
        

        # Cek saldo
        eth_balance = utils.check_eth_balance(w3, wallet_address)
        usdc_balance = utils.check_token_balance(w3, wallet_address, data.USDC_ADDRESS)
        r2usd_balance = utils.check_token_balance(w3, wallet_address, data.R2USD_ADDRESS)
        sr2usd_balance = utils.check_token_balance(w3, wallet_address, data.SR2USD_ADDRESS)
        
        # tampilkan saldo
        print(f"{appearance.EMOJI['WALLET']} {appearance.color_text(f'ETH Balance: {eth_balance} ETH', appearance.COLORS['YELLOW'])}")
        print(f"{appearance.EMOJI['WALLET']} {appearance.color_text(f'USDC Balance: {usdc_balance} USDC', appearance.COLORS['YELLOW'])}")
        print(f"{appearance.EMOJI['WALLET']} {appearance.color_text(f'R2USD Balance: {r2usd_balance} R2USD', appearance.COLORS['YELLOW'])}")
        print(f"{appearance.EMOJI['WALLET']} {appearance.color_text(f'SR2USD Balance: {sr2usd_balance} SR2USD', appearance.COLORS['YELLOW'])}")
        print(f"{appearance.EMOJI['SUCCESS']} {appearance.color_text('Wallet balance check completed successfully.', appearance.COLORS['GREEN'])}")
        # print a line
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
        # swap usdc to r2usd
        success_count = 0
        fail_count = 0
        for i in range(swap_count):
            persen = random.uniform(1, 10)
            swap_amount_sementara = swap_amount - swap_amount * persen / 100
            print(f"{appearance.EMOJIS.LOADING} {appearance.color_text(f'Executing USDC to R2USD swap transaction {i+1} of {swap_count} (Amount: {swap_amount_sementara}USDC)', appearance.COLORSS.YELLOW)}")
            success = utils.swap_usdc_to_r2usd(w3, account, swap_amount_sementara)
            if success:
                print(f"{appearance.EMOJIS.SUCCESS} {appearance.color_text(f'Swap transaction {i+1} completed successfully!', appearance.COLORSS.GREEN)}")
                success_count += 1
            else:
                print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Swap transaction {i+1} failed. Continuing to next transaction.', appearance.COLORSS.RED)}")
                fail_count += 1
            
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
        # tampilkan succes count dan fail count
        print(f"{appearance.EMOJIS.SUCCESS} {appearance.color_text(f'Successful transactions: {success_count}', appearance.COLORSS.GREEN)}")
        print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Failed transactions: {fail_count}', appearance.COLORSS.RED)}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        message = (
        "<b>✅ Swap USDC to R2USD Completed</b>\n"
        f"<b>🟢 Success:</b> {success_count} transactions\n"
        f"<b>🔴 Failed:</b> {fail_count} transactions"
    )
        utils.send_telegram_message(message, parse_mode="HTML")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
       
        
        
        # swap r2usd to usdc
        success_count = 0
        fail_count = 0
        for i in range(swap_count):
            swap_amount_sementara = swap_amount - swap_amount * persen / 100
            print(f"{appearance.EMOJIS.LOADING} {appearance.color_text(f'Executing R2USD to USDC swap transaction {i+1} of {swap_count} (Amount: {swap_amount_sementara} R2USD)', appearance.COLORSS.YELLOW)}")
            success = utils.swap_r2usd_to_usdc(w3, account,  swap_amount_sementara)
            if success:
                print(f"{appearance.EMOJIS.SUCCESS} {appearance.color_text(f'Swap transaction {i+1} completed successfully!', appearance.COLORSS.GREEN)}")
                success_count += 1
            else:
                print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Swap transaction {i+1} failed. Continuing to next transaction.', appearance.COLORSS.RED)}")
                fail_count += 1
            
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
        # tampilkan succes count dan fail count
        print(f"{appearance.EMOJIS.SUCCESS} {appearance.color_text(f'Successful transactions: {success_count}', appearance.COLORSS.GREEN)}")
        print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Failed transactions: {fail_count}', appearance.COLORSS.RED)}")
        print(f"{appearance.EMOJIS.SUCCESS} {appearance.color_text('All transactions completed.', appearance.COLORSS.GREEN)}")  
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        message = (
        "<b>✅ Swap R2USD to USDC Completed</b>\n"
        f"<b>🟢 Success:</b> {success_count} transactions\n"
        f"<b>🔴 Failed:</b> {fail_count} transactions"
    )

        utils.send_telegram_message(message, parse_mode="HTML")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        
        
        
        success_count = 0
        fail_count = 0
        attempt = 1 

        amount_to_swap = int(swap_total) - 2
        print(f"{appearance.EMOJIS.LOADING} {appearance.color_text(f'Executing USDC to R2USD swap transaction (Amount: {amount_to_swap} USDC)', appearance.COLORSS.YELLOW)}")

        while True:
            print(f"{appearance.EMOJIS.LOADING} {appearance.color_text(f'Attempt {attempt}: Swapping {amount_to_swap} USDC...', appearance.COLORSS.YELLOW)}")
            
            success = utils.swap_usdc_to_r2usd(w3, account, amount_to_swap)
            if success:
                print(f"{appearance.EMOJIS.SUCCESS} {appearance.color_text(f'Swap transaction succeeded on attempt {attempt}!', appearance.COLORSS.GREEN)}")
                success_count += 1
                break
            else:
                print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Swap transaction attempt {attempt} failed. Retrying...', appearance.COLORSS.RED)}")
                fail_count += 1
                attempt += 1
                time.sleep(5)  # Tunggu 5 detik sebelum mencoba lagi

        print(f"{appearance.EMOJIS.INFO} {appearance.color_text(f'Waiting for 5 seconds before proceeding...', appearance.COLORSS.GRAY)}")
        time.sleep(5)
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # Kirim notifikasi telegram
        message = (
            "<b>✅ Swap USDC to R2USD Completed</b>\n"
            f"<b>💸 Amount Sent:</b> {amount_to_swap} USDC\n"
            f"<b>🔁 Attempts:</b> {attempt}\n"
            "Transaction has been processed successfully."
        )
        utils.send_telegram_message(message, parse_mode="HTML")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


                
    # Loop untuk menjalankan transaksi staking R2USD
    
        success_count = 0
        fail_count = 0
        for i in range(stake_count):
            print(f"{appearance.EMOJIS.LOADING} {appearance.color_text(f'Executing R2USD stake transaction {i+1} of {stake_count} (Amount: {stake_amount} R2USD)', appearance.COLORSS.YELLOW)}")
            success = utils.stake_r2usd(w3, account, stake_amount)
            if success:
                print(f"{appearance.EMOJIS.SUCCESS} {appearance.color_text(f'Stake transaction {i+1} completed successfully!', appearance.COLORSS.GREEN)}")
                success_count += 1
            else:
                print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Stake transaction {i+1} failed. Continuing to next transaction.', appearance.COLORSS.RED)}")
                fail_count += 1
            
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
        # tampilkan succes count dan fail count
        print(f"{appearance.EMOJIS.SUCCESS} {appearance.color_text(f'Successful transactions: {success_count}', appearance.COLORSS.GREEN)}")
        print(f"{appearance.EMOJIS.ERROR} {appearance.color_text(f'Failed transactions: {fail_count}', appearance.COLORSS.RED)}")
        print(f"{appearance.EMOJIS.SUCCESS} {appearance.color_text('All transactions completed.', appearance.COLORSS.GREEN)}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        message = (
        "<b>✅ Stake R2USD Completed</b>\n"
        f"<b>🟢 Success:</b> {success_count} transactions\n"
        f"<b>🔴 Failed:</b> {fail_count} transactions"
    )

        utils.send_telegram_message(message, parse_mode="HTML")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        if is_loop:
            utils.wait_until_next_day()  
        else:
            print(f"{appearance.EMOJIS.INFO} {appearance.color_text('Exiting the program...', appearance.COLORSS.GRAY)}")
            break
        
        

        
        

            
     



       