
"""
Handles multi-step input logic for VybeBot command flows.
Each handler processes Telegram user input for specific actions
like token OHLCV, TVL, NFT portfolios, volume charts, and more.
"""

from messages import *
from functions import *
from menu import *

async def handle_back_button(context, update):
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

async def handle_collection_owners_awaiting(text, context, update):
    if context.user_data.get("awaiting_collection_address"):
        collection_address = text.strip()

        if not is_valid_address(collection_address):
            await update.message.reply_text(INVALID_COLLECTION_ADDRESS)
            return True

        response = get_nft_collection_owners(collection_address)

        if response == "🔍 Not Found (404): No such collection found.":
            await update.message.reply_text(COLLECTION_NOT_FOUND)
            return True

        context.user_data["awaiting_collection_address"] = False

        if isinstance(response, list):
            for chunk in response:
                await update.message.reply_text(chunk)  # no parse_mode
        else:
            await update.message.reply_text(response)  # no parse_mode

        return True

    return False

async def handle_program_details_awaiting(text, context, update):
    if context.user_data.get("awaiting_program_address"):
        program_address = text.strip()
        response = get_program_details(program_address)

        if isinstance(response, tuple):
            context.user_data["awaiting_program_address"] = False
            message, logo_url = response
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🖼️ View Logo", url=logo_url)]
            ])
            await update.message.reply_text(message, parse_mode="Markdown", reply_markup=keyboard)
        else:
            await update.message.reply_text(INVALID_PROGRAM_ADDRESS, disable_web_page_preview=True)
        return True

    return False

async def handle_top_wallets_awaiting(text, context, update):
    if context.user_data.get("awaiting_top_wallets_address"):
        program_address = text.strip()

        if not is_valid_address(program_address):
            await update.message.reply_text((INVALID_ADDRESS), disable_web_page_preview=True)
            return True

        program_name = get_program_name(program_address)

        if not program_name:
            await update.message.reply_text((INVALID_PROGRAM_ADDRESS),  disable_web_page_preview=True)
            return True

        context.user_data["program_address"] = program_address
        context.user_data["program_name"] = program_name
        context.user_data["awaiting_top_wallets_address"] = False
        context.user_data["awaiting_days"] = True

        await update.message.reply_text((TIMESPAN_1D_30D), parse_mode="Markdown", disable_web_page_preview=True)
        return True

    elif context.user_data.get("awaiting_days"):
        days = text.strip()
        if not is_valid_days(days):
            await update.message.reply_text((INVALID_TIMESPAN_1D_30D), disable_web_page_preview=True)
            return True

        context.user_data["awaiting_days"] = False
        program_address = context.user_data.get("program_address")
        program_name = context.user_data.get("program_name")

        response = get_top_active_wallets(program_address, days=int(days), limit=10)
        await update.message.reply_text((response), parse_mode="Markdown")
        return True

    return False

async def handle_wallet_nft_awaiting(text, context, update):
    if context.user_data.get("awaiting_wallet_nft") or context.user_data.get("awaiting_nft_wallet"):
        wallet = text.strip()

        if not is_valid_address(wallet) or not (42 <= len(wallet) <= 46):
            await update.message.reply_text(INVALID_WALLET_ADDRESS, disable_web_page_preview=True)
            return True

        context.user_data["awaiting_wallet_nft"] = False
        context.user_data["awaiting_nft_wallet"] = False

        response = get_nft_portfolio(wallet)
        await update.message.reply_text(response, parse_mode="Markdown")
        return True

    return False
async def handle_wallet_pnl_awaiting(text, context, update):
    if context.user_data.get("awaiting_wallet_pnl"):
        wallet = text.strip()

        if not is_valid_address(wallet) or not (42 <= len(wallet) <= 46):
            await update.message.reply_text(INVALID_WALLET_ADDRESS, disable_web_page_preview=True)
            return True

        context.user_data["wallet_for_pnl"] = wallet
        context.user_data["awaiting_wallet_pnl"] = False
        context.user_data["awaiting_pnl_days"] = True

        await update.message.reply_text(TIMESPAN_1D_7D_30D, parse_mode="Markdown", disable_web_page_preview=True)
        return True

    elif context.user_data.get("awaiting_pnl_days"):
        days = text.strip()

        if not days.isdigit() or int(days) not in [1, 7, 30]:
            await update.message.reply_text(INVALID_TIMESPAN_1D_7D_30D,disable_web_page_preview=True)
            return True

        context.user_data["awaiting_pnl_days"] = False
        wallet = context.user_data.get("wallet_for_pnl")
        response = get_wallet_pnl_summary(wallet, int(days))

        if isinstance(response, list):
            for chunk in response:
                await update.message.reply_text(chunk, parse_mode="Markdown")
        else:
            await update.message.reply_text(response, parse_mode="Markdown")

        return True

    return False

async def handle_wallet_portfolio_awaiting(text, context, update):
    if context.user_data.get("awaiting_wallet_portfolio"):
        wallet = text.strip()

        if not is_valid_address(wallet) or not (42 <= len(wallet) <= 46):
            await update.message.reply_text(INVALID_WALLET_ADDRESS, disable_web_page_preview=True)
            return True

        context.user_data["awaiting_wallet_portfolio"] = False
        response = get_wallet_portfolio_summary(wallet)

        if isinstance(response, list):
            for chunk in response:
                await update.message.reply_text(chunk, parse_mode="Markdown")
        else:
            await update.message.reply_text(response, parse_mode="Markdown")

        return True

    return False

async def handle_wallet_spl_awaiting(text, context, update):
    if context.user_data.get("awaiting_wallet_spl"):
        wallet = text.strip()

        if not is_valid_address(wallet) or not (42 <= len(wallet) <= 46):
            await update.message.reply_text(INVALID_WALLET_ADDRESS, disable_web_page_preview=True)
            return True

        context.user_data["awaiting_wallet_spl"] = False
        response = get_wallet_token_summary(wallet)

        if isinstance(response, list):
            for chunk in response:
                await update.message.reply_text(chunk, parse_mode="Markdown")
        else:
            await update.message.reply_text(response, parse_mode="Markdown")

        return True

    return False

async def handle_token_info_awaiting(text, context, update):
    if context.user_data.get("awaiting_token_mint"):
        mint = text.strip()

        if not is_valid_mint(mint):
            await update.message.reply_text(INVALID_MINT_ADDRESS, disable_web_page_preview=True)
            return True

        context.user_data["awaiting_token_mint"] = False
        response = get_token_info(mint)

        if isinstance(response, tuple):
            message, logo_url = response
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🖼️ View Logo", url=logo_url)]
            ])
            await update.message.reply_text(message, parse_mode="Markdown", reply_markup=keyboard)
        else:
            await update.message.reply_text(response, parse_mode="Markdown")

        return True

    return False

valid_resolutions = ['1s', '1m', '3m', '5m', '15m', '30m', '1h', '2h', '3h', '4h', '1d', '1w', '1mo', '1y']

async def handle_ohlcv_awaiting(text, context, update):
    if context.user_data.get("awaiting_ohlcv_mint"):
        mint = text.strip()
        if not is_valid_mint(mint) or not (42 <= len(mint) <= 46):
            await update.message.reply_text(INVALID_MINT_ADDRESS, disable_web_page_preview=True)
            return True
        context.user_data["ohlcv_mint"] = mint
        context.user_data["awaiting_ohlcv_mint"] = False
        context.user_data["awaiting_ohlcv_resolution"] = True
        await update.message.reply_text(ENTER_RESOLUTION, parse_mode="Markdown", disable_web_page_preview=True)
        return True

    elif context.user_data.get("awaiting_ohlcv_resolution"):
        resolution = text.strip()
        if resolution not in valid_resolutions:
            await update.message.reply_text(INVALID_RESOLUTION, disable_web_page_preview=True)
            return True
        context.user_data["ohlcv_resolution"] = resolution
        context.user_data["awaiting_ohlcv_resolution"] = False
        context.user_data["awaiting_ohlcv_start"] = True
        await update.message.reply_text(ENTER_START_DATE, parse_mode="Markdown", disable_web_page_preview=True)
        return True

    elif context.user_data.get("awaiting_ohlcv_start"):
        start = text.strip()
        if not to_unix_from_full_datetime(start):
            await update.message.reply_text(INVALID_START_DATE,  disable_web_page_preview=True)
            return True
        context.user_data["ohlcv_start"] = start
        context.user_data["awaiting_ohlcv_start"] = False
        context.user_data["awaiting_ohlcv_end"] = True
        await update.message.reply_text(ENTER_END_DATE, parse_mode="Markdown", disable_web_page_preview=True)
        return True

    elif context.user_data.get("awaiting_ohlcv_end"):
        end = text.strip()
        mint = context.user_data.get("ohlcv_mint")
        resolution = context.user_data.get("ohlcv_resolution")
        start = context.user_data.get("ohlcv_start")

        if not to_unix_from_full_datetime(end) or to_unix_from_full_datetime(end) <= to_unix_from_full_datetime(start):
            await update.message.reply_text(INVALID_END_DATE, disable_web_page_preview=True)
            return True

        for key in list(context.user_data.keys()):
            if key.startswith("awaiting_ohlcv") or key.startswith("ohlcv_"):
                del context.user_data[key]

        response = get_token_ohlcv_data(
            mint_address=mint,
            resolution=resolution,
            start_date=start,
            end_date=end
        )

        if isinstance(response, list):
            for chunk in response:
                await update.message.reply_text(chunk, parse_mode="Markdown")
        else:
            await update.message.reply_text(response, parse_mode="Markdown")

        return True

    return False

async def handle_active_users_awaiting(text, context, update):
    if context.user_data.get("awaiting_active_users_address"):
        program_address = text.strip()

        if not is_valid_address(program_address):
            await update.message.reply_text(INVALID_ADDRESS, disable_web_page_preview=True)
            return True

        program_name = get_program_name(program_address)
        if not program_name:
            await update.message.reply_text(INVALID_PROGRAM_ADDRESS, disable_web_page_preview=True)
            return True

        context.user_data["chart_program_address"] = program_address
        context.user_data["awaiting_active_users_address"] = False
        context.user_data["awaiting_active_users_range"] = True

        await update.message.reply_text(ENTER_TIME_RANGE, parse_mode="Markdown", disable_web_page_preview=True)
        return True

    elif context.user_data.get("awaiting_active_users_range"):
        time_range = text.strip()

        if not is_valid_range(time_range):
            await update.message.reply_text(INVALID_TIME_RANGE, disable_web_page_preview=True)
            return True

        context.user_data["awaiting_active_users_range"] = False
        program_address = context.user_data.get("chart_program_address")

        await generate_and_send_chart(update, context, program_address, time_range)
        return True

    return False

async def handle_transactions_awaiting(text, context, update):
    if context.user_data.get("awaiting_tx_address"):
        program_address = text.strip()

        if not is_valid_address(program_address):
            await update.message.reply_text(INVALID_FORMAT, disable_web_page_preview=True)
            return True

        context.user_data["tx_program_address"] = program_address
        context.user_data["awaiting_tx_address"] = False
        context.user_data["awaiting_tx_range"] = True

        await update.message.reply_text(ENTER_TRANSACTION_RESOLUTION, parse_mode="Markdown", disable_web_page_preview=True)
        return True

    elif context.user_data.get("awaiting_tx_range"):
        time_range = text.strip()

        if not is_valid_range(time_range):
            await update.message.reply_text(INVALID_TRANSACTION_RESOLUTION, disable_web_page_preview=True)
            return True

        context.user_data["awaiting_tx_range"] = False
        program_address = context.user_data.get("tx_program_address")

        await generate_and_send_tx_chart(update, context, program_address, time_range)
        return True

    return False

async def handle_daily_top_holders_awaiting(text, context, update):
    if context.user_data.get("awaiting_daily_holder_mint"):
        mint = text.strip()
        if not is_valid_mint(mint):
            await update.message.reply_text(INVALID_MINT_ADDRESS,
                                            disable_web_page_preview=True,)
            return True

        context.user_data["daily_holder_mint"] = mint
        context.user_data["awaiting_daily_holder_mint"] = False
        context.user_data["awaiting_daily_holder_start"] = True

        await update.message.reply_text(ENTER_START_DATE, parse_mode="Markdown",
                                        disable_web_page_preview=True)
        return True

    elif context.user_data.get("awaiting_daily_holder_start"):
        start_date = text.strip()
        if not to_unix_from_full_datetime(start_date):
            await update.message.reply_text(INVALID_START_DATE,
                                            disable_web_page_preview=True)
            return True

        context.user_data["daily_holder_start"] = start_date
        context.user_data["awaiting_daily_holder_start"] = False
        context.user_data["awaiting_daily_holder_end"] = True

        await update.message.reply_text(ENTER_END_DATE, parse_mode="Markdown",
                                        disable_web_page_preview=True)
        return True

    elif context.user_data.get("awaiting_daily_holder_end"):
        end_date = text.strip()
        start = context.user_data.get("daily_holder_start")

        if not to_unix_from_full_datetime(end_date) or to_unix_from_full_datetime(end_date) <= to_unix_from_full_datetime(start):
            await update.message.reply_text(INVALID_END_DATE,
                                            disable_web_page_preview=True)
            return True

        context.user_data["awaiting_daily_holder_end"] = False
        mint = context.user_data["daily_holder_mint"]

        message, chart_path = get_daily_top_holders_chart(mint, start, end_date)

        await update.message.reply_text(message, parse_mode="Markdown")

        if chart_path and os.path.exists(chart_path):
            with open(chart_path, "rb") as photo:
                await update.message.reply_photo(photo=InputFile(photo), caption="🖼️ Holders Chart", parse_mode="Markdown")
            os.remove(chart_path)

        return True

    return False

async def handle_top_token_holders_awaiting(text, context, update):
    if context.user_data.get("awaiting_holder_mint"):
        mint = text.strip()
        if not is_valid_mint(mint) or not (42 <= len(mint) <= 46):
            await update.message.reply_text(INVALID_MINT_ADDRESS,
                                            disable_web_page_preview=True)
            return True

        context.user_data["holder_mint"] = mint
        context.user_data["awaiting_holder_mint"] = False
        context.user_data["awaiting_sort_criteria"] = True

        await update.message.reply_text(SORT_CRITERIA, parse_mode="Markdown", reply_markup=sort_criteria_buttons)
        return True

    elif context.user_data.get("awaiting_sort_criteria"):
        sort = text.strip()
        valid_criteria = ['rank', 'ownerName', 'ownerAddress', 'valueUsd', 'balance', 'percentageOfSupplyHeld']

        if sort not in valid_criteria:
            await update.message.reply_text(INVALID_SORT_CRITERIA,
                                            disable_web_page_preview=True)
            return True

        context.user_data["sort_criteria"] = sort
        context.user_data["awaiting_sort_criteria"] = False
        context.user_data["awaiting_sort_order"] = True

        await update.message.reply_text(SORT_ORDER, parse_mode="Markdown", reply_markup=sort_order_buttons)
        return True

    elif context.user_data.get("awaiting_sort_order"):
        order = text.strip().lower()
        if order not in ['asc', 'desc']:
            await update.message.reply_text(INVALID_SORT_ORDER,
                                            disable_web_page_preview=True)
            return True

        context.user_data["sort_order"] = order
        context.user_data["awaiting_sort_order"] = False
        context.user_data["awaiting_holder_limit"] = True

        await update.message.reply_text(TOP_HOLDERS_COUNT, parse_mode="Markdown",
                                        disable_web_page_preview=True)
        return True

    elif context.user_data.get("awaiting_holder_limit"):
        if not text.strip().isdigit() or int(text.strip()) <= 0:
            await update.message.reply_text(INVALID_HOLDERS_COUNT,
                                            disable_web_page_preview=True)
            return True

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
        return True

    return False

async def handle_volume_awaiting(text, context, update):
    if context.user_data.get("awaiting_volume_mint"):
        mint = text.strip()

        if not is_valid_mint(mint) or not (42 <= len(mint) <= 46):
            await update.message.reply_text(INVALID_MINT_ADDRESS,
                                            disable_web_page_preview=True,)
            return True

        context.user_data["volume_mint"] = mint
        context.user_data["awaiting_volume_mint"] = False
        context.user_data["awaiting_volume_start"] = True

        await update.message.reply_text(ENTER_START_DATE, parse_mode="Markdown",
                                        disable_web_page_preview=True)
        return True

    elif context.user_data.get("awaiting_volume_start"):
        start_date = text.strip()

        if not to_unix_from_full_datetime(start_date):
            await update.message.reply_text(INVALID_START_DATE,
                                            disable_web_page_preview=True)
            return True

        context.user_data["volume_start"] = start_date
        context.user_data["awaiting_volume_start"] = False
        context.user_data["awaiting_volume_end"] = True

        await update.message.reply_text(ENTER_END_DATE, parse_mode="Markdown",
                                        disable_web_page_preview=True)
        return True

    elif context.user_data.get("awaiting_volume_end"):
        end_date = text.strip()
        start = context.user_data["volume_start"]

        if not to_unix_from_full_datetime(end_date) or to_unix_from_full_datetime(end_date) <= to_unix_from_full_datetime(start):
            await update.message.reply_text(INVALID_END_DATE,
                                            disable_web_page_preview=True)
            return True

        context.user_data["volume_end"] = end_date
        context.user_data["awaiting_volume_end"] = False
        context.user_data["awaiting_volume_interval"] = True

        await update.message.reply_text(ENTER_INTERVAL, parse_mode="Markdown",
                                        disable_web_page_preview=True)
        return True

    elif context.user_data.get("awaiting_volume_interval"):
        interval = text.strip().lower()

        if interval not in ["hour", "day"]:
            await update.message.reply_text(INVALID_INTERVAL,
                                            disable_web_page_preview=True)
            return True

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

        return True

    return False

async def handle_tvl_awaiting(text, context, update):
    if context.user_data.get("awaiting_tvl_address"):
        address = text.strip()

        if not is_valid_address(address):
            await update.message.reply_text(INVALID_ADDRESS,
                                            disable_web_page_preview=True)
            return True

        context.user_data["tvl_address"] = address
        context.user_data["awaiting_tvl_address"] = False
        context.user_data["awaiting_tvl_resolution"] = True

        await update.message.reply_text(ENTER_TVL_RESOLUTION, parse_mode="Markdown",
                                        disable_web_page_preview=True)
        return True

    elif context.user_data.get("awaiting_tvl_resolution"):
        resolution = text.strip()

        if not re.fullmatch(r"\d+(s|h|d|w)", resolution):
            await update.message.reply_text(INVALID_TVL_RESOLUTION,
                                            disable_web_page_preview=True)
            return True

        context.user_data["awaiting_tvl_resolution"] = False
        address = context.user_data.get("tvl_address")

        await send_tvl_chart(update, context, address, resolution)
        return True

    return False

async def handle_token_balances_awaiting(text, context, update):
    if context.user_data.get("awaiting_balances_wallet"):
        wallet = text.strip()

        if not is_valid_address(wallet) or not (42 <= len(wallet) <= 46):
            await update.message.reply_text(INVALID_WALLET_ADDRESS,
                                            disable_web_page_preview=True)
            return True

        context.user_data["balances_wallet"] = wallet
        context.user_data["awaiting_balances_wallet"] = False
        context.user_data["awaiting_balances_days"] = True

        await update.message.reply_text(ENTER_BALANCE_DAYS, parse_mode="Markdown",
                                        disable_web_page_preview=True)
        return True

    elif context.user_data.get("awaiting_balances_days"):
        try:
            days = int(text.strip())
            if not (1 <= days <= 30):
                raise ValueError()
        except ValueError:
            await update.message.reply_text(INVALID_TIMESPAN_1D_30D,
                                            disable_web_page_preview=True)
            return True

        context.user_data["awaiting_balances_days"] = False
        wallet = context.user_data.get("balances_wallet")
        await send_token_balance_chart(update, context, wallet, days)
        return True

    return False

