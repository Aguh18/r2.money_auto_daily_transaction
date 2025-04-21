# R2 Money Auto Transaction Bot

A Python-based bot designed to automate interactions with the R2 Money protocol on the Sepolia testnet. It supports swapping between USDC and R2USD, staking R2USD for sR2USD, and checking wallet balances. The bot can run once or automate daily transactions with optional Telegram notifications.

## Features

- Swap USDC to R2USD and vice versa
- Stake R2USD to earn sR2USD
- Monitor balances for ETH, USDC, R2USD, and sR2USD
- Single wallet support
- Customizable USDC spending amount via `.env`
- Telegram notifications for transaction updates(Optional)
- One-time or daily automated execution (VPS required for automation)

## Prerequisites

- **Python** 3.8 or higher
- **pip** (Python package manager)
- **Git** for cloning the repository
- An **Ethereum wallet** containing:
  - Sepolia testnet ETH for gas fees
  - Sepolia USDC tokens for swaps
- (Optional) **Telegram Bot** for notifications:
  - Telegram bot token
  - Telegram chat ID

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Aguh18/r2.money_auto_daily_transaction_bot.git
   cd r2.money_auto_daily_transaction_bot
   ```

2. **Create a Virtual Environment** (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   Install required packages listed in `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

  

4. **Configure Environment File**:

   Create a `.env` file in the project root and add your wallet private key, USDC spending amount, and optional Telegram settings. Example:

   ```
   PRIVATE_KEY=your_private_key
   USDC_SPENDING_AMOUNT=150
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHAT_ID=your_telegram_chat_id
   ```

   - `PRIVATE_KEY`: Ethereum private key for Sepolia testnet wallet.
   - `USDC_SPENDING_AMOUNT`: Total USDC to use for swaps and staking (e.g., `150` for 150 USDC). This is split into 150 swaps and 12 staking transactions.
   - `TELEGRAM_BOT_TOKEN`: (Optional) Token for Telegram bot notifications.
   - `TELEGRAM_CHAT_ID`: (Optional) Chat ID for receiving notifications.

   **Warning**: Keep your `.env` file private and add it to `.gitignore` to prevent accidental exposure.

## Setting Up Telegram Notifications (Optional)

To enable Telegram notifications, you need a bot token and chat ID.

### Get a Telegram Bot Token

1. Open Telegram and search for <span style="color: blue;">@BotFather</span>.
2. Start a chat and send the command <span style="color: gray;">/newbot</span>.
3. Follow the prompts to create a bot and receive a token.
4. Copy the token and add it to `TELEGRAM_BOT_TOKEN` in `.env`.

### Get a Telegram Chat ID

1. Send a message to your newly created bot in Telegram.
2. In a browser, visit:

   ```
   https://api.telegram.org/bot<your-bot-token>/getUpdates
   ```

   Replace `<your-bot-token>` with your bot token.

3. Find the `chat.id` in the response (e.g., `123456789`).
4. Add this ID to `TELEGRAM_CHAT_ID` in `.env`.

## Usage

1. **Prepare Funds**:

   - Ensure your wallet has Sepolia testnet ETH for gas fees.
   - Acquire at least the USDC amount specified in `USDC_SPENDING_AMOUNT` (e.g., 150 USDC) via testnet faucets or project resources.

2. **Start the Bot**:

   Run the bot with:

   ```bash
   python main.py
   ```

3. **Interact with Prompts**:

   - Select execution mode:
     - `once`: Run transactions once and exit.
     - `auto`: Run transactions daily (requires a VPS).
   - The bot will execute:
     - 150 USDC to R2USD swaps with randomized amounts (`USDC_SPENDING_AMOUNT / 150`).
     - 150 R2USD to USDC swaps with randomized amounts.
     - One large USDC to R2USD swap (`USDC_SPENDING_AMOUNT - 2`).
     - 12 R2USD to sR2USD staking transactions (`(USDC_SPENDING_AMOUNT - 10) / 12`).
     - Telegram notifications for each transaction batch (if configured).

4. **Track Progress**:

   - View real-time balance updates, transaction statuses, and success/failure counts.
   - Receive Telegram summaries for transaction results (if enabled).

## Example Output

```
==========================================
 R2 MONEY AUTO BOT - AIRDROP INSIDERS
==========================================
✅ Connected to Sepolia Testnet: <rpc_url>
💳 Wallet: 0x1234...5678
💰 ETH Balance: 0.5 ETH
💰 USDC Balance: 150 USDC
💰 R2USD Balance: 0 R2USD
💰 SR2USD Balance: 0 SR2USD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏳ Executing USDC to R2USD swap 1/150 (Amount: 0.95 USDC)
✅ Swap 1 completed successfully!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Successful transactions: 145
❌ Failed transactions: 5
```

## Token Addresses (Sepolia)

- **USDC**: `0xef84994ef411c4981328ffce5fda41cd3803fae4`
- **R2USD**: `0x20c54c5f742f123abb49a982bfe0af47edb38756`
- **sR2USD**: `0xbd6b25c4132f09369c354bee0f7be777d7d434fa`

## Security Notes

- **Protect Private Keys**: Never use mainnet wallets for testnet operations and keep keys secure.
- **Verify Contracts**: Confirm all contract addresses against official sources to avoid malicious interactions.
- **Testnet Only**: This bot is for Sepolia testnet use. Do not adapt for mainnet without thorough review.
- **Review Code**: Inspect the code before running with sensitive data like private keys.

## Disclaimer

This bot is intended for educational purposes. Use it at your own risk. The developers are not liable for any financial losses.

## License

MIT License

## Community

Join us on Telegram: [AutoDropz](https://t.me/+V_JQTTMVZVU3YTM9)

## Credits

This project was inspired by the R2Money-Auto-Bot by [Airdrop Insiders](https://github.com/airdropinsiders) The developers have adapted and rewritten the original code in Python to meet specific requirements, enhancing it with additional features and optimizations. Special thanks to Airdrop Insiders for providing the foundational reference.