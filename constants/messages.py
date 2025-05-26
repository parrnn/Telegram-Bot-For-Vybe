WELCOME_TEXT ="""👋 Hello {}
Welcome to *VybeBot* – your on-chain insights assistant.
Use the keyboard buttons below to explore analytics across NFTs, programs, tokens, and wallets.
📌 Press ❓ *Help* at any time to view the full feature guide."""
ALPHA = """
🔍 *Want more alpha?*
Dive into powerful token analytics, wallet insights, and real-time market data on AlphaVybe:
🌐 https://vybe.fyi/
📊 Track trending tokens
🐋 Follow whales and top wallets
📈 Monitor live price action
💼 Break down PnL and portfolio flows
_Alpha starts here._
"""
HELP = """
*VybeBot Help menu*
Welcome to *VybeBot* – your all-in-one assistant for on-chain analytics and insights across NFTs, tokens, wallets, and programs!
👇 Use the keyboard buttons or commands to explore features:
*🎨 NFT*
• 👑 Collection Owners – See top holders of any NFT collection (up to 🔟).
• 💥 NFT (in Wallet Tracking) – View a wallet’s full NFT portfolio.
*📦 Programs*
• 📄 Details – Get stats, description & logo of any program.
• 💰 Top Wallets – View most active wallets in the past X days.
• 🔁 Transactions – Chart transaction counts over time.
• 👥 Active Users – Visualize DAU trends with charts.
• 📈 TVL – View historical Total Value Locked.
*📊 Token Analysis*
• 📋 Info – Fetch full token details by mint.
• 🕰 OHLCV – Get open/high/low/close/volume data with resolution options.
• 📊 Volume – Analyze transfer volumes (hour/day).
*👤 Holders*
• 📅 Daily Top Holders – Chart holder count growth.
• 🏆 Top Token Holders – Rank by balance, value, or supply %.
• 💼 Balances – View wallet token balances over time.
*🧾 Wallet Tracking*
• 💼 Portfolio – View total token + NFT value in a wallet.
• 📈 PnL – Track wallet profit/loss over 1, 7, or 30 days.
• 🪙 SPL – See token holdings, prices, and value changes.
*🅰️ Alpha Vybe*
🔗 Dashboards: [vybe.fyi](https://vybe.fyi)
Live market metrics, whale activity & token insights.
*🔙 Back / 🏠 Main menu*
Use these to navigate between menus.
💡 *Need Help?* Just press ❓ Help anytime.
Happy analyzing with VybeBot! 🚀📊"""

ENTER_COLLECTION_ADDRESS= "📥 Please enter the *collection address* (alphanumeric only):"
ENTER_PROGRAM_ADDRESS="📥 Send the *program address* :"
ENTER_WALLET_ADDRESS="📥 Send the *wallet address* :"
ENTER_MINT_ADDRESS="🔑 Send the *mint address* :"
ENTER_RESOLUTION="🕒 Send the resolution (e.g. 1d, 1mo, 1h):  Possible values: 1s, 1m, 3m, 5m, 15m, 30m, 1h, 2h, 3h, 4h, 1d, 1w, 1mo, 1y."
ENTER_START_DATE="📅 Enter *start date* (YYYY-MM-DD):"
ENTER_END_DATE="📅 Enter *end date* (YYYY-MM-DD):"
ENTER_TIME_RANGE="⏱️ Enter time range like `12h`, `1d`, or `7d`:"
ENTER_TRANSACTION_RESOLUTION="⏱️ How much historical data would you like to see? (e.g., past 24 hours: 24h , 7 days: 7d , etc.)"
ENTER_INTERVAL="⏱️ Choose interval: `hour` or `day`"
ENTER_TVL_RESOLUTION="⏱️ Enter resolution (e.g., 1h, 1d, 1w):"
ENTER_BALANCE_DAYS="📅 How many days of history? (Enter a number between 1 and 30):"

COLLECTION_NOT_FOUND="🔍 Collection not found! Please double-check the address and try again:"
PROGRAM_NOT_FOUND="🚫 Program not found or invalid."
NO_OWNERS_FOUND="⚠️ No owners found for this collection."
NO_DATA_FOUND="⚠️ No active user data found."
WALLET_NOT_FOUND="❌ Wallet not found or has no trading data."
WALLET_NOT_FOUND_FOR_PORTFOLIO="❌ Wallet not found or has no portfolio activity."
TOKEN_NOT_FOUND="❌ Token not found! Please check the mint address."
NO_OHLCV_FOUND="⚠️ No OHLCV data found in the selected range."
NO_VOLUME_DATA_FOUND="⚠️ No transfer volume data found for this range."
NO_TOKEN_BALANCE_FOUND="⚠️ No token balance data found for this wallet."
NO_TVL_DATA="⚠️ No TVL data found for this program."

TIMESPAN_1D_30D="📆 How many *previous days*? (1–30)"
TIMESPAN_1D_7D_30D="📆 Choose number of days: `1`, `7`, or `30`"

SORT_CRITERIA="📊 Choose a *sort criteria*:"
SORT_ORDER="⬆️⬇️ Choose sort order:"
TOP_HOLDERS_COUNT="🔢 How many top holders? (e.g., 10):"

WARN_NO_TOKEN_BALANCES = "⚠️ This wallet has no token balances."
GENERATE_ERROR=("⚠️ Error while generating or sending chart:"
"{e}")
UNRECOGNIZED_INPUT="❌ I didn't understand that. Please use the menu below to navigate."
STATUS_CODE_403="🚫 Forbidden (403): This collection is not accessible."
STATUS_CODE_404="🔍 Not Found (404): No such collection found."
NETWORK_ERROR = """❌ Network error occurred: 
{}"""
VALUE_ERROR="❌ Failed to parse JSON response."
UNEXPECTED_ERROR="""⚠️ Unexpected error:"
{}"""
INACCESSIBLE_PROGRAM_ADDRESS="❌ Invalid or inaccessible program address."
SOMETHING_WENT_WRONG="❌ Something went wrong. Please try again."
JSON_ERROR="❌ Failed to parse JSON response."
ERROR_NO_WALLET_TOKEN_DATA = "❌ Wallet not found or has no token data."

PROGRAM_DETAILS_TEMPLATE = """
📌 *Program Overview*
🏛️ *Entity:* 
📛 *Name:* {}
🏷️ *Labels:* {}
📊 *Stats (24h)*
👥 Active Users: {:,}
🆕 New Users: {:,}
🔁 Transactions: {:,}
📖 *Description:*{}
"""
TOP_ACTIVE_WALLETS_TEMPLATE = """
📊 *Top {} Active Wallets*
🧾 *Program:* {}
📆 *Last {} Days*"""

NFT_PORTFOLIO_TEMPLATE = """    
💥 *NFT Portfolio*
👛 *Wallet:* {}
🪙 *Total SOL Value:* {:.2f} 
💵 *Total USD Value:* ${:,.2f}
📚 *NFT Collections:* {}"""

NFT_PORTFOLIO_COLLECTION_MESSAGE =""" 
🎭 *{}*
🔗 Collection: {}
📦 Items: {}
💰 Value: {:.2f} ◎ / ${:,.2f}
🏷️ Price: {:.2f} ◎ / ${:,.2f}"""

PNL_SUMMARY_HEADER = "💥 *PnL Summary ({}d)*"
PNL_SUMMARY_TEMPLATE =""" 
👛 Wallet: `{}`
💵 *Realized PnL:* ${:.2f}
📉 *Unrealized PnL:* ${:.2f}
🔁 *Trade Volume:* ${:.2f}
📊 *Total Trades:* {}
📦 *Avg. Trade Size:* ${:.2f}
🏆 *Win Rate:* {:.2f}%"""

PNL_TOKEN_ENTRY = """
🪙 *{}*
💰 Realized: ${:.2f}
📉 Unrealized: ${:.2f}
🛒 Buys: ${:.2f} | {} txs
🏷️ Sells: ${:.2f} | {} txs"""

PORTFOLIO_SUMMARY_MESSAGE =""" 
📊 *Portfolio Summary*
👛 Wallet: `{}`
💼 *Token Value:* ${:,.2f}
🎨 *NFT Value:* ${:,.2f}
🧾 *Total Portfolio:* 💵 ${:,.2f}"""

WALLET_TOKEN_SUMMARY =""" 
🧾 *Wallet Token Summary*
👛 Wallet Address: `{}`
💰 Total Token Value (USD): ${:,.2f}
🔒 Staked SOL Value (USD): ${:,.2f}
🪙 Number of Tokens Held: {}
📊 *Tokens List:*"""

TOKEN_DETAIL_TEMPLATE =""" 
{emoji} *{symbol}* ({name})
🔗 Mint: `{mint}`
📈 24h Price Change: {price_change:.2f}%
💸 24h Value Change: ${value_change:.2f}
📦 Amount: {amount}\n
💵 Value: ${value_usd:,.2f}
✔️ Verified: {verified}"""

TOKEN_INFO_TEMPLATE = """
📄 *Full Token Info*
🔘 *Symbol:* {symbol}
🏷️ *Name:* {name}
🔑 *Mint:* `{mint}`

💵 *Price Info*
💰 *Current Price:* ${price:.4f}
📅 *1d Ago:* ${price_1d:.4f}
🗓️ *7d Ago:* ${price_7d:.4f}

🔍 *Details*
🧬 *Decimals:* {decimals}
✅ *Verified:* {verified}
📂 *Category:* {category}
📁 *Subcategory:* {subcategory}

⏱️ *Last Updated:*
{last_updated}

📦 *Supply & Market*
📦 *Supply:* {supply:.4f}
💰 *Market Cap:* ${market_cap}

📊 *24h Volume*
🔄 *Token:* {volume_token}
💸 *USD:* ${volume_usd}"""

TOKEN_OHLCV_HEADER = """
📈 *Token OHLCV Data* ({} candles)
🗓️ *Range:* {} → {}"""

TOKEN_OHLCV_ITEM =""" 
🕒 *Time:* {}
🔓 Open: {}
📈 High: {}
📉 Low: {}
🔒 Close: {}
📦 Volume: {}
💵 Volume (USD): {}
🧾 Count: {}
────────────────────────────"""

ACTIVE_USERS_HEADER =""" 
📊 *Active Users Over `{}`*
🧾 *Program:* {}
──────────────────────────────"""

TRANSACTIONS_HEADER = """
📊 *Transactions Over `{}`*
🧾 *Program:* {}
──────────────────────────────"""

TIMEOUT_ERROR="⏱️ Timeout: Server took too long to respond."
DAILY_HOLDERS_HEADER = """
📊 *Daily Holders Count*
🔑 *Mint:* `{}`
📆 *Range:* {} → {}"""

TOKEN_HOLDER_DETAIL = """
🏅 *Rank:* {rank}
👤 *Owner:* {owner_name} (`{owner_address}`)
📦 *Balance:* {balance}
💵 *Value (USD):* ${value_usd:.2f}
📈 *Supply Held:* {supply_held:.2f}%
🔘 *Token Symbol:* {symbol}"""

TRANSFER_VOLUME_HEADER = """
📋 *Transfer Volume Data* ({})
🪙 *Mint:* {}
📆 *Range:* {} ➡ {}
────────────────────────────"""

TOKEN_BALANCE_HEADER_TEMPLATE = """
📊 *Token Balance History* (`{}d`)
👛 *Wallet:* `{}`
────────────────────────────"""

TOKEN_BALANCE_HISTORY_ENTRY = """
📅 {}
💰 Token Value: ${:,.2f}
🔒 Stake Value: ${:,.2f}
🛠️ System Value: ${:,.2f}
🧊 Stake (SOL): {:.2f}
────────────────────────────"""

INVALID_COLLECTION_ADDRESS= """❌ Invalid collection address! It must be alphanumeric and 42–46 characters long. Please try again:"""
INVALID_ADDRESS="❌ Invalid address! It must be alphanumeric and 42–46 characters long. Please try again:"
INVALID_PROGRAM_ADDRESS="🚫 Program not found or invalid. Please try again."
INVALID_TIMESPAN_1D_30D="❌ Please enter a number between 1 and 30."
INVALID_FORMAT="❌ Invalid format! Only alphanumeric characters are allowed."
INVALID_WALLET_ADDRESS="❌ Invalid wallet address! It must be alphanumeric and 42-46 characters long. Please try again:"
INVALID_TIMESPAN_1D_7D_30D="❌ Invalid input. Please enter 1, 7, or 30 only."
INVALID_MINT_ADDRESS="❌ Invalid mint address! Only letters and digits allowed. Please try again:"
INVALID_RESOLUTION="❌ Invalid resolution. Try again (e.g. `1d`, `1mo`):"
INVALID_START_DATE="❌ Invalid start date format. Use YYYY-MM-DD like (2025-01-01):"
INVALID_END_DATE="❌ Invalid end date. It must be after the start date and in correct format (YYYY-MM-DD):"
INVALID_TIME_RANGE="❌ Invalid range! Use formats like `1h`, `12h`, or `3d`. Please try again:"
INVALID_TRANSACTION_RESOLUTION="❌ Invalid range format. Use values like `1h`, `12h`, `3d` etc. Please try again:"
INVALID_SORT_CRITERIA="❌ Invalid sort criteria. Please select from the keyboard."
INVALID_SORT_ORDER="❌ Invalid sort order. Please use the buttons provided."
INVALID_HOLDERS_COUNT="❌ Invalid number. Please enter a *positive integer*."
INVALID_INTERVAL="❌ Invalid interval! Please enter `hour` or `day`:"
INVALID_TVL_RESOLUTION="❌ Invalid resolution format! Use values like `1h`, `1d`, `1w`. Please try again:"
INVALID_LIMIT="❌ Limit must be a positive number."
INVALID_WALLET_FORMAT="❌ Invalid wallet address format."
INVALID_DATE_RANGE="❌ Invalid date range. Ensure correct format (YYYY-MM-DD) and that end date is after start date."









