"""
VybeBot Core Bot Logic
=======================

This module defines the main functionality and user interaction flow for VybeBot —
a Telegram bot delivering on-chain analytics for NFTs, tokens, wallets, and programs, powered by the Vybe Network API.

Key Features:
--------------
- Fully dynamic multi-step input handling (awaiting address, dates, limits, etc.)
- Robust validation at every input step.
- Human-readable outputs with emoji-enhanced formatting.
- Automated chart generation with Matplotlib.
- AlphaVybe link integration for additional insights.

Usage Flow:
------------
1. User starts bot with /start.
2. Bot displays main menu.
3. User selects feature and follows prompts.
4. Bot fetches data, validates, formats, and responds.
5. Users can return or reset state via 🔙 Back or 🏠 Main Menu.
"""

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from constants.messages import *
from telegram.ext import ContextTypes
from constants.menu import *
from handlers import (
    handle_back_button, handle_collection_owners_awaiting, handle_program_details_awaiting,
    handle_top_wallets_awaiting, handle_wallet_pnl_awaiting, handle_wallet_portfolio_awaiting,
    handle_wallet_spl_awaiting, handle_token_info_awaiting, handle_ohlcv_awaiting,
    handle_active_users_awaiting, handle_transactions_awaiting, handle_daily_top_holders_awaiting,
    handle_top_token_holders_awaiting, handle_volume_awaiting, handle_tvl_awaiting,
    handle_token_balances_awaiting, handle_wallet_nft_awaiting
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    context.user_data["last_menu"] = "main"
    await update.message.reply_text(
        WELCOME_TEXT.format(user.first_name),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(main_menu_buttons, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Menus
    if text == "🎨 NFT":
        await update.message.reply_text("🎨 *NFT Menu*", parse_mode="Markdown",
                                        reply_markup=ReplyKeyboardMarkup(nft_menu, resize_keyboard=True)); return
    if text == "📦 Programs":
        context.user_data["last_menu"] = "main"
        await update.message.reply_text("📦 *Programs Menu*", parse_mode="Markdown",
                                        reply_markup=ReplyKeyboardMarkup(programs_menu, resize_keyboard=True)); return
    if text == "📊 Token Analysis":
        context.user_data["last_menu"] = "token"
        await update.message.reply_text("📊 *Token Analysis Menu*", parse_mode="Markdown",
                                        reply_markup=ReplyKeyboardMarkup(token_menu, resize_keyboard=True)); return
    if text == "👤 Holders":
        context.user_data["last_menu"] = "holders"
        await update.message.reply_text("👤 *Holders Submenu*", parse_mode="Markdown",
                                        reply_markup=ReplyKeyboardMarkup(holders_submenu, resize_keyboard=True)); return
    if text == "🧾 Wallet Tracking":
        context.user_data["last_menu"] = "main"
        await update.message.reply_text("🧾 *Wallet Tracking Menu*", parse_mode="Markdown",
                                        reply_markup=ReplyKeyboardMarkup(wallet_menu, resize_keyboard=True)); return
    if text == "🅰️ Alpha Vybe":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Open AlphaVybe", url="https://vybe.fyi/")]])
        await update.message.reply_text(ALPHA, parse_mode="Markdown", disable_web_page_preview=True,
                                        reply_markup=keyboard); return
    if text == "❓ Help":
        await update.message.reply_text(HELP, parse_mode="Markdown", disable_web_page_preview=True,
                                        reply_markup=ReplyKeyboardMarkup(main_menu_buttons, resize_keyboard=True)); return
    if text == "🏠 Main Menu":
        context.user_data.clear()
        context.user_data["last_menu"] = "main"
        await update.message.reply_text("🏠 *Main Menu*", parse_mode="Markdown",
                                        reply_markup=ReplyKeyboardMarkup(main_menu_buttons, resize_keyboard=True)); return
    if text == "🔙 Back":
        await handle_back_button(context, update); return

    awaiting_starters = {
        "👑 NFT Collection Owners": ("awaiting_collection_address", ENTER_COLLECTION_ADDRESS),
        "📄 Details": ("awaiting_program_address", ENTER_PROGRAM_ADDRESS),
        "💰 Top Wallets": ("awaiting_top_wallets_address", ENTER_PROGRAM_ADDRESS),
        "💥 NFT": ("awaiting_wallet_nft", ENTER_WALLET_ADDRESS),
        "📈 PnL": ("awaiting_wallet_pnl", ENTER_WALLET_ADDRESS),
        "💼 Portfolio": ("awaiting_wallet_portfolio", ENTER_WALLET_ADDRESS),
        "🪙 SPL": ("awaiting_wallet_spl", ENTER_WALLET_ADDRESS),
        "📋 Info": ("awaiting_token_mint", ENTER_MINT_ADDRESS),
        "🕰 OHLCV": ("awaiting_ohlcv_mint", ENTER_MINT_ADDRESS),
        "👥 Active Users": ("awaiting_active_users_address", ENTER_PROGRAM_ADDRESS),
        "🔁 Transactions": ("awaiting_tx_address", ENTER_PROGRAM_ADDRESS),
        "📅 Daily Top Holders": ("awaiting_daily_holder_mint", ENTER_MINT_ADDRESS),
        "🏆 Top Token Holders": ("awaiting_holder_mint", ENTER_MINT_ADDRESS),
        "📊 Volume": ("awaiting_volume_mint", ENTER_MINT_ADDRESS),
        "📈 TVL": ("awaiting_tvl_address", ENTER_PROGRAM_ADDRESS),
        "💼 Balances": ("awaiting_balances_wallet", ENTER_WALLET_ADDRESS),
    }

    if text in awaiting_starters:
        key, prompt = awaiting_starters[text]

        context.user_data.clear()

        if text in ["📈 PnL", "💼 Portfolio", "🪙 SPL", "💼 Balances"]:
            context.user_data["last_menu"] = "wallet"
        elif text == "🏆 Top Token Holders":
            context.user_data["last_menu"] = "holders"
        else:
            context.user_data["last_menu"] = "main"

        context.user_data[key] = True

        await update.message.reply_text(prompt, parse_mode="Markdown", disable_web_page_preview=True)
        return

    handlers = [
        handle_collection_owners_awaiting, handle_program_details_awaiting, handle_top_wallets_awaiting,
        handle_wallet_nft_awaiting, handle_wallet_pnl_awaiting, handle_wallet_portfolio_awaiting,
        handle_wallet_spl_awaiting, handle_token_info_awaiting, handle_ohlcv_awaiting,
        handle_active_users_awaiting, handle_transactions_awaiting, handle_daily_top_holders_awaiting,
        handle_top_token_holders_awaiting, handle_volume_awaiting, handle_tvl_awaiting,
        handle_token_balances_awaiting
    ]

    for handler in handlers:
        if await handler(text, context, update):
            return

    await update.message.reply_text(WRONG_INPUT, parse_mode="Markdown",
                                    disable_web_page_preview=True)
def main():
    app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot is running... Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
