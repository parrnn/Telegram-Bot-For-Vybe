"""
VybeBot Core Bot Logic
=======================

This module defines the main functionality and user interaction flow for VybeBot —
a Telegram bot delivering on-chain analytics for NFTs, tokens, wallets, and programs, powered by the Vybe Network API.

Imports:
---------
- Telegram Bot Framework:
    - `ReplyKeyboardMarkup`, `KeyboardButton`, `InlineKeyboardMarkup`, `InlineKeyboardButton`
    - `ApplicationBuilder`, `CommandHandler`, `MessageHandler`, `filters`
- Local Functions:
    - Imported from `functions.py`, including Vybe API calls, validation, and chart generation.

Menus and Layouts:
-------------------
- `main_menu_buttons`: Main navigation — NFTs, Programs, Token Analysis, Wallet Tracking, Alpha Vybe, Help.
- `nft_menu`: NFT analytics actions, such as Collection Owners.
- `programs_menu`: Program-level analytics like Details, Top Wallets, Transactions, Active Users, TVL.
- `token_menu`: Token actions — Holders, Token Info, Balances, OHLCV, Volume.
- `holders_submenu`: Sub-menu under Token Analysis for holder-related data.
- `wallet_menu`: Wallet-level analytics including NFT Portfolio, PnL, Portfolio Summary, SPL Tokens.
- `sort_criteria_buttons`, `sort_order_buttons`: Sorting options for token holder analytics.

Functions:
-----------
- `start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None`:
    - Greets the user and displays the main menu on `/start` command.

- `handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None`:
    - Processes all incoming text messages.
    - Handles menu navigation, feature selection, multi-step user inputs, validations, and analytics generation.
    - Interacts with local `functions.py` to fetch data, generate charts, and respond to users.

- `main() -> None`:
    - Initializes the Telegram bot.
    - Registers command and message handlers.
    - Starts polling to continuously receive updates from users.

Usage Flow:
------------
1. User starts bot with `/start`.
2. User navigates menus via buttons.
3. For certain actions, bot asks for inputs (e.g., wallet address, mint address, date range).
4. Bot fetches, formats, and sends analytics data or charts to user.
5. User can return to previous menus using "🔙 Back" or go to "🏠 Main Menu".

Key Features:
--------------
- Fully dynamic multi-step input handling (awaiting address, dates, limits, etc.)
- Robust validation at every input step.
- Human-readable outputs with emoji-enhanced formatting.
- Automated chart generation with Matplotlib for TVL, active users, transactions, balances, holders, and volumes.
- AlphaVybe link integration for additional insights.

Notes:
-------
- All responses are optimized for Telegram's messaging limits.
- Supports error handling for invalid inputs, API failures, and unexpected issues.
- Designed to be scalable — adding new menu options or analytics is straightforward.

"""


from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from functions import *


main_menu_buttons = [
    [KeyboardButton("🎨 NFT"), KeyboardButton("📦 Programs")],
    [KeyboardButton("📊 Token Analysis"), KeyboardButton("🧾 Wallet Tracking")],
    [KeyboardButton("🅰️ Alpha Vybe"), KeyboardButton("❓ Help")]
]

nft_menu = [
    [KeyboardButton("👑 NFT Collection Owners")],
    [KeyboardButton("🔙 Back"), KeyboardButton("🏠 Main Menu")]
]

programs_menu = [
    [KeyboardButton("📄 Details"), KeyboardButton("💰 Top Wallets")],
    [KeyboardButton("🔁 Transactions"), KeyboardButton("👥 Active Users")],
    [KeyboardButton("📈 TVL")],
    [KeyboardButton("🔙 Back"), KeyboardButton("🏠 Main Menu")]
]

token_menu = [
    [KeyboardButton("👤 Holders"), KeyboardButton("📋 Info")],
    [KeyboardButton("💼 Balances"), KeyboardButton("🕰 OHLCV")],
    [KeyboardButton("📊 Volume")],
    [KeyboardButton("🔙 Back"), KeyboardButton("🏠 Main Menu")]
]

holders_submenu = [
    [KeyboardButton("📅 Daily Top Holders")],
    [KeyboardButton("🏆 Top Token Holders")],
    [KeyboardButton("🔙 Back"), KeyboardButton("🏠 Main Menu")]
]

wallet_menu = [
    [KeyboardButton("💥 NFT"), KeyboardButton("📈 PnL")],
    [KeyboardButton("💼 Portfolio"), KeyboardButton("🪙 SPL")],
    [KeyboardButton("🔙 Back"), KeyboardButton("🏠 Main Menu")]
]

sort_criteria_buttons = ReplyKeyboardMarkup(
    [
        [KeyboardButton("rank"), KeyboardButton("ownerName"), KeyboardButton("ownerAddress")],
        [KeyboardButton("valueUsd"), KeyboardButton("balance"), KeyboardButton("percentageOfSupplyHeld")],
        [KeyboardButton("🔙 Back")]
    ],
    resize_keyboard=True
)

sort_order_buttons = ReplyKeyboardMarkup(
    [
        [KeyboardButton("asc"), KeyboardButton("desc")],
        [KeyboardButton("🔙 Back")]
    ],
    resize_keyboard=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    context.user_data["last_menu"] = "main"

    welcome_text = (
        f"👋 Hello {user.first_name}!\n\n"
        "Welcome to *VybeBot* – your on-chain insights assistant.\n"
        "Use the keyboard buttons below to explore analytics across NFTs, programs, tokens, and wallets.\n\n"
        "📌 Press ❓ *Help* at any time to view the full feature guide."
    )

    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(main_menu_buttons, resize_keyboard=True)
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🎨 NFT":
        await update.message.reply_text("🎨 *NFT Menu*", parse_mode="Markdown",
                                        reply_markup=ReplyKeyboardMarkup(nft_menu, resize_keyboard=True))
        return

    elif text == "📦 Programs":
        context.user_data["last_menu"] = "main"
        await update.message.reply_text("📦 *Programs Menu*", parse_mode="Markdown",
                                        reply_markup=ReplyKeyboardMarkup(programs_menu, resize_keyboard=True))
        return

    elif text == "📊 Token Analysis":
        context.user_data["last_menu"] = "token"
        await update.message.reply_text("📊 *Token Analysis Menu*", parse_mode="Markdown",
                                        reply_markup=ReplyKeyboardMarkup(token_menu, resize_keyboard=True))
        return

    elif text == "👤 Holders":
        context.user_data["last_menu"] = "holders"
        await update.message.reply_text("👤 *Holders Submenu*", parse_mode="Markdown",
                                        reply_markup=ReplyKeyboardMarkup(holders_submenu, resize_keyboard=True))
        return

    elif text == "🧾 Wallet Tracking":
        context.user_data["last_menu"] = "main"
        await update.message.reply_text("🧾 *Wallet Tracking Menu*", parse_mode="Markdown",
                                        reply_markup=ReplyKeyboardMarkup(wallet_menu, resize_keyboard=True))
        return

    elif text == "🅰️ Alpha Vybe":
        alpha_text = (
            "🔍 *Want more alpha?*\n\n"
            "Dive into powerful token analytics, wallet insights, and real-time market data on AlphaVybe:\n\n"
            "🌐 https://vybe.fyi/\n\n"
            "📊 Track trending tokens\n"
            "🐋 Follow whales and top wallets\n"
            "📈 Monitor live price action\n"
            "💼 Break down PnL and portfolio flows\n\n"
            "_Alpha starts here._"
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Open AlphaVybe", url="https://vybe.fyi/")]])
        await update.message.reply_text(alpha_text, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=keyboard)
        return

    elif text == "❓ Help":
        help_text = (
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
            "Happy analyzing with VybeBot! 🚀📊"
        )
        await update.message.reply_text(help_text, parse_mode="Markdown", disable_web_page_preview=True,
                                        reply_markup=ReplyKeyboardMarkup(main_menu_buttons, resize_keyboard=True))
        return

    elif text == "🏠 Main Menu":
        context.user_data["last_menu"] = "main"
        for key in list(context.user_data.keys()):
            if key.startswith("awaiting_") or key.startswith("ohlcv_") or key.startswith("volume_"):
                del context.user_data[key]

        await update.message.reply_text("🏠 *Main Menu*", parse_mode="Markdown",
                                        reply_markup=ReplyKeyboardMarkup(main_menu_buttons, resize_keyboard=True))
        return

    elif text == "🔙 Back":
        for key in list(context.user_data.keys()):
            if key.startswith("awaiting_") or key.startswith("ohlcv_") or key.startswith("volume_"):
                del context.user_data[key]

        last_menu = context.user_data.get("last_menu", "main")

        if last_menu == "holders":
            context.user_data["last_menu"] = "token"
            await update.message.reply_text("📊 *Token Analysis Menu*", parse_mode="Markdown",
                                            reply_markup=ReplyKeyboardMarkup(token_menu, resize_keyboard=True))
        elif last_menu == "token":
            context.user_data["last_menu"] = "main"
            await update.message.reply_text("🏠 *Main Menu*", parse_mode="Markdown",
                                            reply_markup=ReplyKeyboardMarkup(main_menu_buttons, resize_keyboard=True))
        else:
            await update.message.reply_text("🏠 *Main Menu*", parse_mode="Markdown",
                                            reply_markup=ReplyKeyboardMarkup(main_menu_buttons, resize_keyboard=True))
        return

    elif text == "👑 NFT Collection Owners":
        await update.message.reply_text(
            "📥 Please enter the *collection address* (alphanumeric only):",
            parse_mode="Markdown"
        )
        context.user_data["awaiting_collection_address"] = True


    elif context.user_data.get("awaiting_collection_address"):

        collection_address = text.strip()

        if not is_valid_address(collection_address):
            await update.message.reply_text(

                "❌ Invalid collection address! It must be alphanumeric and 42_46 characters long.\nPlease try again:"

            )

            return

        response = get_nft_collection_owners(collection_address)

        if response == "🔍 Not Found (404): No such collection found.":
            await update.message.reply_text(

                "🔍 Collection not found! Please double-check the address and try again:",

                parse_mode="Markdown"

            )

            return

        context.user_data["awaiting_collection_address"] = False

        if isinstance(response, list):
            for chunk in response:
                await update.message.reply_text(chunk, parse_mode="Markdown")
        else:
            await update.message.reply_text(response, parse_mode="Markdown")
    elif text == "📄 Details":
        await update.message.reply_text("📥 Send the *program address* to get details:", parse_mode="Markdown")
        context.user_data["awaiting_program_address"] = True

    elif context.user_data.get("awaiting_program_address"):
        program_address = text.strip()
        response = get_program_details(program_address)
        if isinstance(response, tuple):
            context.user_data["awaiting_program_address"] = False
            text, logo_url = response
            keyboard = InlineKeyboardMarkup([

                [InlineKeyboardButton("🖼️ View Logo", url=logo_url)]

            ])

            await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)
        else:
            await update.message.reply_text("❌ Invalid program address. Please try again:")

    elif text == "💰 Top Wallets":
        await update.message.reply_text("📮 Send the *program address*:", parse_mode="Markdown")
        context.user_data["awaiting_top_wallets_address"] = True

    elif context.user_data.get("awaiting_days"):
        days = text.strip()
        if not is_valid_days(days):
            await update.message.reply_text("❌ Please enter a number between 1 and 30.")
            return

        context.user_data["awaiting_days"] = False
        program_address = context.user_data.get("program_address")
        program_name = context.user_data.get("program_name")

        response = get_top_active_wallets(program_address, days=int(days), limit=10)
        await update.message.reply_text(response, parse_mode="Markdown")

    elif context.user_data.get("awaiting_top_wallets_address"):
        program_address = text.strip()
        if not is_valid_address(program_address):
            await update.message.reply_text("❌ Invalid format! Only alphanumeric characters are allowed.")
            return

        program_name = get_program_name(program_address)

        if not program_name:
            await update.message.reply_text("🚫 Program not found or invalid. Please try again.")

            return

        context.user_data["program_address"] = program_address

        context.user_data["program_name"] = program_name

        context.user_data["awaiting_top_wallets_address"] = False

        context.user_data["awaiting_days"] = True

        await update.message.reply_text("📆 How many *previous days*? (1–30)", parse_mode="Markdown")
    elif text == "💥 NFT":
        await update.message.reply_text(
            "📥 Send the *wallet address* to fetch NFT portfolio:",
            parse_mode="Markdown"
        )
        context.user_data["awaiting_wallet_nft"] = True

    elif context.user_data.get("awaiting_wallet_nft"):
        wallet = text.strip()
        if not is_valid_address(wallet) or len(wallet) < 42 or len(wallet) > 46:
            await update.message.reply_text(
                "❌ Invalid wallet address! It must be alphanumeric and 42-46 characters long.\nPlease try again:"
            )
            return

        context.user_data["awaiting_wallet_nft"] = False
        response = get_nft_portfolio(wallet)
        await update.message.reply_text(response, parse_mode="Markdown")

    elif context.user_data.get("awaiting_nft_wallet"):
        context.user_data["awaiting_nft_wallet"] = False
        wallet = text.strip()
        response = get_nft_portfolio(wallet)
        await update.message.reply_text(response, parse_mode="Markdown")

    elif text == "📈 PnL":
        context.user_data["last_menu"] = "wallet"
        context.user_data["awaiting_wallet_pnl"] = True
        await update.message.reply_text("👛 Send the *wallet address* to get PnL summary:", parse_mode="Markdown")

    elif context.user_data.get("awaiting_wallet_pnl"):
        wallet = text.strip()
        if not is_valid_address(wallet) or len(wallet) < 42 or len(wallet) > 46:
            await update.message.reply_text(
                "❌ Invalid wallet address! It must be alphanumeric and 42-46 characters long.\nPlease try again:"
            )
            return

        context.user_data["awaiting_wallet_pnl"] = False
        context.user_data["awaiting_pnl_days"] = True
        context.user_data["wallet_for_pnl"] = wallet
        await update.message.reply_text("📆 Choose number of days: `1`, `7`, or `30`", parse_mode="Markdown")

    elif context.user_data.get("awaiting_pnl_days"):
        days = text.strip()
        if not days.isdigit() or int(days) not in [1, 7, 30]:
            await update.message.reply_text("❌ Invalid input. Please enter 1, 7, or 30 only.")
            return

        context.user_data["awaiting_pnl_days"] = False
        wallet = context.user_data.get("wallet_for_pnl")
        response = get_wallet_pnl_summary(wallet, int(days))

        if isinstance(response, list):
            for chunk in response:
                await update.message.reply_text(chunk, parse_mode="Markdown")
        else:
            await update.message.reply_text(response, parse_mode="Markdown")

    elif text == "💼 Portfolio":
        context.user_data["last_menu"] = "wallet"
        context.user_data["awaiting_wallet_portfolio"] = True
        await update.message.reply_text("👛 Send the *wallet address* to get portfolio summary:", parse_mode="Markdown")

    elif context.user_data.get("awaiting_wallet_portfolio"):
        wallet = text.strip()
        if not is_valid_address(wallet) or len(wallet) < 42 or len(wallet) > 46:
            await update.message.reply_text(
                "❌ Invalid wallet address! It must be alphanumeric and 42-46 characters long.\nPlease try again:"
            )
            return

        context.user_data["awaiting_wallet_portfolio"] = False
        response = get_wallet_portfolio_summary(wallet)

        if isinstance(response, list):
            for chunk in response:
                await update.message.reply_text(chunk, parse_mode="Markdown")
        else:
            await update.message.reply_text(response, parse_mode="Markdown")

    elif text == "🪙 SPL":
        context.user_data["last_menu"] = "wallet"
        context.user_data["awaiting_wallet_spl"] = True
        await update.message.reply_text("👛 Send the *wallet address* to get SPL token summary:", parse_mode="Markdown")

    elif context.user_data.get("awaiting_wallet_spl"):
        wallet = text.strip()
        if not is_valid_address(wallet) or len(wallet) < 42 or len(wallet) > 46:
            await update.message.reply_text(
                "❌ Invalid wallet address! It must be alphanumeric and 42-46 characters long.\nPlease try again:"
            )
            return

        context.user_data["awaiting_wallet_spl"] = False
        response = get_wallet_token_summary(wallet)

        if isinstance(response, list):
            for chunk in response:
                await update.message.reply_text(chunk, parse_mode="Markdown")
        else:
            await update.message.reply_text(response, parse_mode="Markdown")

    elif text == "📋 Info":
        context.user_data["awaiting_token_mint"] = True
        await update.message.reply_text(
            "🔑 Send the *mint address* to get token info:",
            parse_mode="Markdown"

        )
    elif context.user_data.get("awaiting_token_mint"):
        context.user_data["awaiting_token_mint"] = False
        mint = text.strip()

        if not is_valid_mint(mint):
            context.user_data["awaiting_token_mint"] = True
            await update.message.reply_text(
                "❌ Invalid mint address! Only letters and digits allowed.\nPlease try again:",
                parse_mode="Markdown"
            )
            return

        response = get_token_info(mint)

        if isinstance(response, tuple):
            text, logo_url = response
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🖼️ View Logo", url=logo_url)]
            ])
            await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)
        else:
            await update.message.reply_text(response, parse_mode="Markdown")
    elif text == "🕰 OHLCV":
        context.user_data["awaiting_ohlcv_mint"] = True
        await update.message.reply_text("🔑 Send the *mint address* for OHLCV data:", parse_mode="Markdown")


    elif context.user_data.get("awaiting_ohlcv_mint"):

        mint = text.strip()

        if not is_valid_mint(mint) or not (42 <= len(mint) <= 46):
            await update.message.reply_text(

                "❌ Invalid mint address! It must be alphanumeric and 42_46 characters long.\nPlease try again:"

            )

            return
        context.user_data["ohlcv_mint"] = mint

        context.user_data["awaiting_ohlcv_mint"] = False

        context.user_data["awaiting_ohlcv_resolution"] = True

        await update.message.reply_text(

            "🕒 Send the resolution (e.g. 1d, 1mo, 1h):\n  Possible values: 1s, 1m, 3m, 5m, 15m, 30m, 1h, 2h, 3h, 4h, 1d, 1w, 1mo, 1y.",

            parse_mode="Markdown"

        )


    elif context.user_data.get("awaiting_ohlcv_resolution"):
        resolution = text.strip()
        valid_resolutions = ['1s', '1m', '3m', '5m', '15m', '30m', '1h', '2h', '3h', '4h', '1d', '1w', '1mo', '1y']
        if resolution not in valid_resolutions:
            await update.message.reply_text("❌ Invalid resolution. Try again (e.g. `1d`, `1mo`):")
            return
        context.user_data["ohlcv_resolution"] = resolution
        context.user_data["awaiting_ohlcv_resolution"] = False
        context.user_data["awaiting_ohlcv_start"] = True
        await update.message.reply_text("📅 Enter *start date* (YYYY-MM-DD):", parse_mode="Markdown")

    elif context.user_data.get("awaiting_ohlcv_start"):
        start_date = text.strip()
        if not to_unix_from_full_datetime(start_date):
            await update.message.reply_text("❌ Invalid start date format. Use YYYY-MM-DD like (2025-01-01):")
            return
        context.user_data["ohlcv_start"] = start_date
        context.user_data["awaiting_ohlcv_start"] = False
        context.user_data["awaiting_ohlcv_end"] = True
        await update.message.reply_text("📅 Enter *end date* (YYYY-MM-DD):", parse_mode="Markdown")

    elif context.user_data.get("awaiting_ohlcv_end"):
        end_date = text.strip()
        mint = context.user_data.get("ohlcv_mint")
        resolution = context.user_data.get("ohlcv_resolution")
        start = context.user_data.get("ohlcv_start")

        if not to_unix_from_full_datetime(end_date) or to_unix_from_full_datetime(
                end_date) <= to_unix_from_full_datetime(start):
            await update.message.reply_text(
                "❌ Invalid end date. It must be after the start date and in correct format (YYYY-MM-DD):")
            return

        for key in list(context.user_data.keys()):
            if key.startswith("awaiting_ohlcv") or key.startswith("ohlcv_"):
                del context.user_data[key]

        response = get_token_ohlcv_data(
            mint_address=mint,
            resolution=resolution,
            start_date=start,
            end_date=end_date
        )

        if isinstance(response, list):
            for chunk in response:
                await update.message.reply_text(chunk, parse_mode="Markdown")
        else:
            await update.message.reply_text(response, parse_mode="Markdown")


    elif text == "👥 Active Users":

        await update.message.reply_text(

            "📥 Send the *program address* to analyze active users:",

            parse_mode="Markdown"

        )

        context.user_data["awaiting_active_users_address"] = True


    elif context.user_data.get("awaiting_active_users_address"):

        program_address = text.strip()

        if not is_valid_address(program_address):
            await update.message.reply_text(

                "❌ Invalid address! It must be alphanumeric and 42_46 characters long.\nPlease try again:"

            )

            return

        context.user_data["chart_program_address"] = program_address

        context.user_data["awaiting_active_users_address"] = False

        context.user_data["awaiting_active_users_range"] = True

        await update.message.reply_text(

            "⏱️ Enter time range like `12h`, `1d`, or `7d`:",

            parse_mode="Markdown"

        )


    elif context.user_data.get("awaiting_active_users_range"):

        time_range = text.strip()

        if not is_valid_range(time_range):
            await update.message.reply_text(

                "❌ Invalid range! Use formats like `1h`, `12h`, or `3d`.\nPlease try again:"

            )

            return

        context.user_data["awaiting_active_users_range"] = False

        program_address = context.user_data.get("chart_program_address")

        await generate_and_send_chart(update, context, program_address, time_range)


    elif text == "🔁 Transactions":

        await update.message.reply_text(

            "🔗 Send the *program address* for transactions summary:", parse_mode="Markdown"

        )

        context.user_data["awaiting_tx_address"] = True


    elif context.user_data.get("awaiting_tx_address"):

        program_address = text.strip()

        if not is_valid_address(program_address):
            await update.message.reply_text(

                "❌ Invalid address format! Only alphanumeric characters are allowed.\nPlease try again:"

            )

            return

        context.user_data["awaiting_tx_address"] = False

        context.user_data["tx_program_address"] = program_address

        context.user_data["awaiting_tx_range"] = True

        await update.message.reply_text(

            "⏱️ How much historical data would you like to see? (e.g., past 24 hours: 24h , 7 days: 7d , etc.)",

            parse_mode="Markdown"

        )

    elif context.user_data.get("awaiting_tx_range"):
        time_range = text.strip()

        if not is_valid_range(time_range):
            await update.message.reply_text(
                "❌ Invalid range format. Use values like `1h`, `12h`, `3d` etc.\nPlease try again:")
            return

        context.user_data["awaiting_tx_range"] = False
        program_address = context.user_data.get("tx_program_address")

        await generate_and_send_tx_chart(update, context, program_address, time_range)

    elif text == "📅 Daily Top Holders":
        context.user_data["awaiting_daily_holder_mint"] = True
        await update.message.reply_text("🔑 Send the *mint address* to get daily holders chart:", parse_mode="Markdown")
    elif context.user_data.get("awaiting_daily_holder_mint"):
        mint = text.strip()
        if not is_valid_mint(mint):
            await update.message.reply_text("❌ Invalid mint address! Please enter a valid alphanumeric address:")
            return
        context.user_data["daily_holder_mint"] = mint
        context.user_data["awaiting_daily_holder_mint"] = False
        context.user_data["awaiting_daily_holder_start"] = True
        await update.message.reply_text("📅 Send the *start date* (YYYY-MM-DD):", parse_mode="Markdown")


    elif context.user_data.get("awaiting_daily_holder_start"):

        start_date = text.strip()

        if not to_unix_from_full_datetime(start_date):
            await update.message.reply_text("❌ Invalid start date format! Use YYYY-MM-DD:")

            return

        context.user_data["daily_holder_start"] = start_date

        context.user_data["awaiting_daily_holder_start"] = False

        context.user_data["awaiting_daily_holder_end"] = True

        await update.message.reply_text("📅 Send the *end date* (YYYY-MM-DD):", parse_mode="Markdown")




    elif context.user_data.get("awaiting_daily_holder_end"):

        end_date = text.strip()

        start = context.user_data.get("daily_holder_start")

        if not to_unix_from_full_datetime(end_date) or to_unix_from_full_datetime(
                end_date) <= to_unix_from_full_datetime(start):
            await update.message.reply_text("❌ Invalid end date! Must be in YYYY-MM-DD format and after start date.")

            return

        context.user_data["awaiting_daily_holder_end"] = False

        mint = context.user_data["daily_holder_mint"]

        message, chart_path = get_daily_top_holders_chart(mint, start, end_date)

        await update.message.reply_text(message, parse_mode="Markdown")

        if chart_path and os.path.exists(chart_path):
            with open(chart_path, "rb") as photo:
                await update.message.reply_photo(photo=InputFile(photo), caption="🖼️ Holders Chart",
                                                 parse_mode="Markdown")

            os.remove(chart_path)



    elif text == "🏆 Top Token Holders":

        context.user_data.clear()

        context.user_data["last_menu"] = "holders"

        context.user_data["awaiting_holder_mint"] = True

        await update.message.reply_text(

            "🔑 Send the *mint address* to fetch top token holders:",

            parse_mode="Markdown"

        )


    elif context.user_data.get("awaiting_holder_mint"):

        mint = text.strip()

        if not is_valid_mint(mint) or not (42 <= len(mint) <= 46):
            await update.message.reply_text(

                "❌ Invalid mint address! Please enter a valid alphanumeric address (42_46 characters)."

            )

            return

        context.user_data["holder_mint"] = mint

        context.user_data["awaiting_holder_mint"] = False

        context.user_data["awaiting_sort_criteria"] = True

        await update.message.reply_text(

            "📊 Choose a *sort criteria*:",

            parse_mode="Markdown",

            reply_markup=sort_criteria_buttons

        )


    elif context.user_data.get("awaiting_sort_criteria"):

        sort = text.strip()

        valid_criteria = ['rank', 'ownerName', 'ownerAddress', 'valueUsd', 'balance', 'percentageOfSupplyHeld']

        if sort not in valid_criteria:
            await update.message.reply_text("❌ Invalid sort criteria. Please select from the keyboard.")

            return

        context.user_data["sort_criteria"] = sort

        context.user_data["awaiting_sort_criteria"] = False

        context.user_data["awaiting_sort_order"] = True

        await update.message.reply_text(

            "⬆️⬇️ Choose sort order:",

            parse_mode="Markdown",

            reply_markup=sort_order_buttons

        )


    elif context.user_data.get("awaiting_sort_order"):

        order = text.strip().lower()

        if order not in ['asc', 'desc']:
            await update.message.reply_text("❌ Invalid sort order. Please use the buttons provided.")

            return

        context.user_data["sort_order"] = order

        context.user_data["awaiting_sort_order"] = False

        context.user_data["awaiting_holder_limit"] = True

        await update.message.reply_text(

            "🔢 How many top holders? (e.g., 10):",

            parse_mode="Markdown"

        )


    elif context.user_data.get("awaiting_holder_limit"):

        if not text.strip().isdigit() or int(text.strip()) <= 0:
            await update.message.reply_text("❌ Invalid number. Please enter a *positive integer*.")

            return

        limit = int(text.strip())

        mint = context.user_data["holder_mint"]

        sort = context.user_data["sort_criteria"]

        order = context.user_data["sort_order"]

        context.user_data["awaiting_holder_limit"] = False

        result = get_top_token_holders(mint, sort, order, limit)

        await update.message.reply_text(result, parse_mode="Markdown")

        context.user_data["last_menu"] = "token"
        await update.message.reply_text(
            "📊 *Token Analysis Menu*",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(token_menu, resize_keyboard=True)
        )




    elif text == "📊 Volume":

        context.user_data["awaiting_volume_mint"] = True

        await update.message.reply_text("🔑 Send the *mint address* for transfer volume:", parse_mode="Markdown")




    elif context.user_data.get("awaiting_volume_mint"):

        mint = text.strip()

        if not is_valid_mint(mint) or not (42 <= len(mint) <= 46):
            await update.message.reply_text(

                "❌ Invalid mint address! It must be alphanumeric and 42_46 characters long.\nPlease try again:",

                parse_mode="Markdown"

            )

            return

        context.user_data["volume_mint"] = mint

        context.user_data["awaiting_volume_mint"] = False

        context.user_data["awaiting_volume_start"] = True

        await update.message.reply_text("📅 Enter the *start date* (YYYY-MM-DD):", parse_mode="Markdown")




    elif context.user_data.get("awaiting_volume_start"):

        start_date = text.strip()

        if not to_unix_from_full_datetime(start_date):
            await update.message.reply_text("❌ Invalid start date format! Use YYYY-MM-DD (e.g., 2025-01-01):")

            return

        context.user_data["volume_start"] = start_date

        context.user_data["awaiting_volume_start"] = False

        context.user_data["awaiting_volume_end"] = True

        await update.message.reply_text("📅 Enter the *end date* (YYYY-MM-DD):", parse_mode="Markdown")



    elif context.user_data.get("awaiting_volume_end"):

        end_date = text.strip()

        start = context.user_data["volume_start"]

        if not to_unix_from_full_datetime(end_date) or to_unix_from_full_datetime(

                end_date) <= to_unix_from_full_datetime(start):
            await update.message.reply_text(

                "❌ Invalid end date! It must be after the start date and in YYYY-MM-DD format:")

            return

        context.user_data["volume_end"] = end_date

        context.user_data["awaiting_volume_end"] = False

        context.user_data["awaiting_volume_interval"] = True

        await update.message.reply_text("⏱️ Choose interval: `hour` or `day`", parse_mode="Markdown")




    elif context.user_data.get("awaiting_volume_interval"):

        interval = text.strip().lower()

        if interval not in ["hour", "day"]:
            await update.message.reply_text("❌ Invalid interval! Please enter `hour` or `day`:")

            return

        mint = context.user_data.get("volume_mint")

        start = context.user_data.get("volume_start")

        end = context.user_data.get("volume_end")

        summary, filename = get_transfer_volume_chart(mint, start, end, interval)

        for key in list(context.user_data.keys()):

            if key.startswith("volume_") or key.startswith("awaiting_volume_"):
                del context.user_data[key]

        await update.message.reply_text(summary, parse_mode="Markdown")

        if filename and os.path.exists(filename):
            with open(filename, "rb") as photo:
                await update.message.reply_photo(

                    photo=InputFile(photo),

                    caption="📈 Transfer Volume Chart",

                    parse_mode="Markdown"

                )

            os.remove(filename)



    elif text == "📈 TVL":

        await update.message.reply_text(

            "📥 Send the *program address* for TVL:",

            parse_mode="Markdown"

        )

        context.user_data["awaiting_tvl_address"] = True


    elif context.user_data.get("awaiting_tvl_address"):

        address = text.strip()

        if not is_valid_address(address):
            await update.message.reply_text(

                "❌ Invalid address! It must be alphanumeric and 42_46 characters long.\nPlease try again:"

            )

            return

        context.user_data["awaiting_tvl_address"] = False

        context.user_data["tvl_address"] = address

        context.user_data["awaiting_tvl_resolution"] = True

        await update.message.reply_text(

            "⏱️ Enter resolution (e.g., 1h, 1d, 1w):",

            parse_mode="Markdown"

        )


    elif context.user_data.get("awaiting_tvl_resolution"):

        resolution = text.strip()

        if not re.fullmatch(r"\d+(s|h|d|w)", resolution):
            await update.message.reply_text(

                "❌ Invalid resolution format! Use values like `1h`, `1d`, `1w`.\nPlease try again:"

            )

            return

        context.user_data["awaiting_tvl_resolution"] = False

        address = context.user_data.get("tvl_address")

        await send_tvl_chart(update, context, address, resolution)

    elif text == "💼 Balances":
        context.user_data["last_menu"] = "token"
        context.user_data["awaiting_balances_wallet"] = True
        await update.message.reply_text(
            "🔑 Send the *wallet address* to fetch token balances:",
            parse_mode="Markdown"
        )



    elif context.user_data.get("awaiting_balances_wallet"):

        wallet = text.strip()

        if not is_valid_address(wallet) or len(wallet) < 42 or len(wallet) > 46:
            await update.message.reply_text(

                "❌ Invalid wallet address! It must be alphanumeric and 42_46 characters long.\nPlease try again:"

            )

            return

        context.user_data["balances_wallet"] = wallet

        context.user_data["awaiting_balances_wallet"] = False

        context.user_data["awaiting_balances_days"] = True

        await update.message.reply_text(

            "📅 How many days of history? (Enter a number between 1 and 30):",

            parse_mode="Markdown"

        )



    elif context.user_data.get("awaiting_balances_days"):
        try:
            days = int(text.strip())
            if not (1 <= days <= 30):
                raise ValueError()
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid number! Please enter a value between 1 and 30:",
                parse_mode="Markdown"
            )
            return

        context.user_data["awaiting_balances_days"] = False
        wallet = context.user_data.get("balances_wallet")
        await send_token_balance_chart(update, context, wallet, days)
    else:
        await update.message.reply_text(
            "❌ I didn't understand that. Please use the menu below to navigate.",
            reply_markup=ReplyKeyboardMarkup(main_menu_buttons, resize_keyboard=True)
        )
def main():
    bot_token = "YOUR_BOT_TOKEN_HERE"
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running... Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
