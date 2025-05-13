WELCOME_TEXT = (
    f"👋 Hello %s !\n\n"
    "Welcome to *VybeBot* – your on-chain insights assistant.\n"
    "Use the keyboard buttons below to explore analytics across NFTs, programs, tokens, and wallets.\n\n"
    "📌 Press ❓ *Help* at any time to view the full feature guide."
)
ALPHA =     (
            "🔍 *Want more alpha?*\n\n"
            "Dive into powerful token analytics, wallet insights, and real-time market data on AlphaVybe:\n\n"
            "🌐 https://vybe.fyi/\n\n"
            "📊 Track trending tokens\n"
            "🐋 Follow whales and top wallets\n"
            "📈 Monitor live price action\n"
            "💼 Break down PnL and portfolio flows\n\n"
            "_Alpha starts here._")
HELP = (
    "🆘 *VybeBot Help Menu*\n\n"
    "Welcome to *VybeBot* – your all-in-one assistant for on-chain analytics and insights across NFTs, tokens, wallets, and programs!\n\n"
    "👇 Use the keyboard buttons or commands to explore features:\n\n"
    "*🎨 NFT*\n"
    "• 👑 Collection Owners – See top holders of any NFT collection (up to 🔟).\n"
    "• 💥 NFT (in Wallet Tracking) – View a wallet’s full NFT portfolio.\n\n"
    "*📦 Programs*\n"
    "• 📄 Details – Get stats, description & logo of any program.\n"
    "• 💰 Top Wallets – View most active wallets in the past X days.\n"
    "• 🔁 Transactions – Chart transaction counts over time.\n"
    "• 👥 Active Users – Visualize DAU trends with charts.\n"
    "• 📈 TVL – View historical Total Value Locked.\n\n"
    "*📊 Token Analysis*\n"
    "• 📋 Info – Fetch full token details by mint.\n"
    "• 🕰 OHLCV – Get open/high/low/close/volume data with resolution options.\n"
    "• 📊 Volume – Analyze transfer volumes (hour/day).\n\n"
    "*👤 Holders*\n"
    "• 📅 Daily Top Holders – Chart holder count growth.\n"
    "• 🏆 Top Token Holders – Rank by balance, value, or supply %.\n"
    "• 💼 Balances – View wallet token balances over time.\n\n"
    "*🧾 Wallet Tracking*\n"
    "• 💼 Portfolio – View total token + NFT value in a wallet.\n"
    "• 📈 PnL – Track wallet profit/loss over 1, 7, or 30 days.\n"
    "• 🪙 SPL – See token holdings, prices, and value changes.\n\n"
    "*🅰️ Alpha Vybe*\n"
    "🔗 Dashboards: [vybe.fyi](https://vybe.fyi)\n"
    "Live market metrics, whale activity & token insights.\n\n"
    "*🔙 Back / 🏠 Main Menu*\n"
    "Use these to navigate between menus.\n\n"
    "💡 *Need Help?* Just press ❓ Help anytime.\n\n"
    "Happy analyzing with VybeBot! 🚀📊")

ENTER_COLLECTION_ADDRESS= ("📥 Please enter the *collection address* (alphanumeric only):")
INVALID_COLLECTION_ADDRESS= ("❌ Invalid collection address! It must be alphanumeric and 42_46 characters long.\nPlease try again:")
COLLECTION_NOT_FOUND=("🔍 Collection not found! Please double-check the address and try again:")
ENTER_PROGRAM_ADDRESS=("📥 Send the *program address* :")
INVALID_ADDRESS=("❌ Invalid address! It must be alphanumeric and 42_46 characters long.\nPlease try again:")
INVALID_PROGRAM_ADDRESS=("🚫 Program not found or invalid. Please try again.")
TIMESPAN_1D_30D=("📆 How many *previous days*? (1–30)")
INVALID_TIMESPAN_1D_30D=("❌ Please enter a number between 1 and 30.")
INVALID_FORMAT=("❌ Invalid format! Only alphanumeric characters are allowed.")
ENTER_WALLET_ADDRESS=("📥 Send the *wallet address* :")
INVALID_WALLET_ADDRESS=("❌ Invalid wallet address! It must be alphanumeric and 42-46 characters long.\nPlease try again:")
TIMESPAN_1D_7D_30D=("📆 Choose number of days: `1`, `7`, or `30`")
INVALID_TIMESPAN_1D_7D_30D=("❌ Invalid input. Please enter 1, 7, or 30 only.")
ENTER_MINT_ADDRESS=("🔑 Send the *mint address* :")
INVALID_MINT_ADDRESS=("❌ Invalid mint address! Only letters and digits allowed.\nPlease try again:")
ENTER_RESOLUTION=("🕒 Send the resolution (e.g. 1d, 1mo, 1h):\n  Possible values: 1s, 1m, 3m, 5m, 15m, 30m, 1h, 2h, 3h, 4h, 1d, 1w, 1mo, 1y.")
INVALID_RESOLUTION=("❌ Invalid resolution. Try again (e.g. `1d`, `1mo`):")
ENTER_START_DATE=("📅 Enter *start date* (YYYY-MM-DD):")
INVALID_START_DATE=("❌ Invalid start date format. Use YYYY-MM-DD like (2025-01-01):")
ENTER_END_DATE=("📅 Enter *end date* (YYYY-MM-DD):")
INVALID_END_DATE=("❌ Invalid end date. It must be after the start date and in correct format (YYYY-MM-DD):")
ENTER_TIME_RANGE=("⏱️ Enter time range like `12h`, `1d`, or `7d`:")
INVALID_TIME_RANGE=("❌ Invalid range! Use formats like `1h`, `12h`, or `3d`.\nPlease try again:")
ENTER_TRANSACTION_RESOLUTION=("⏱️ How much historical data would you like to see? (e.g., past 24 hours: 24h , 7 days: 7d , etc.)")
INVALID_TRANSACTION_RESOLUTION=("❌ Invalid range format. Use values like `1h`, `12h`, `3d` etc.\nPlease try again:")
SORT_CRITERIA=("📊 Choose a *sort criteria*:")
INVALID_SORT_CRITERIA=("❌ Invalid sort criteria. Please select from the keyboard.")
SORT_ORDER=("⬆️⬇️ Choose sort order:")
INVALID_SORT_ORDER=("❌ Invalid sort order. Please use the buttons provided.")
TOP_HOLDERS_COUNT=("🔢 How many top holders? (e.g., 10):")
INVALID_HOLDERS_COUNT=("❌ Invalid number. Please enter a *positive integer*.")
ENTER_INTERVAL=("⏱️ Choose interval: `hour` or `day`")
INVALID_INTERVAL=("❌ Invalid interval! Please enter `hour` or `day`:")
ENTER_TVL_RESOLUTION=("⏱️ Enter resolution (e.g., 1h, 1d, 1w):")
INVALID_TVL_RESOLUTION=("❌ Invalid resolution format! Use values like `1h`, `1d`, `1w`.\nPlease try again:")
ENTER_BALANCE_DAYS=("📅 How many days of history? (Enter a number between 1 and 30):")
WRONG_INPUT=("❌ I didn't understand that. Please use the menu below to navigate.")