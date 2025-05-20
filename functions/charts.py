from typing import Tuple
import matplotlib.pyplot as plt
import os
import pandas as pd
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from globals.urls import *
from functions.functions import *
from functions.datetime import *

async def send_program_dau_chart(update: Update, context: ContextTypes.DEFAULT_TYPE, program_address: str, time_range: str):
    """
    Generate and send a bar chart showing active users over time for a given program.

    Fetches time-series data of daily active users (DAU) from Vybe Network API for a program
    over a specified time range (e.g., 1h, 1d, 7d). If the dataset is large enough,
    generates and sends a bar chart image. For smaller datasets, sends a formatted text summary.

    Args:
        update (Update):
            Telegram Update object representing the incoming message.
        context (ContextTypes.DEFAULT_TYPE):
            Telegram context containing user data and bot state.
        program_address (str):
            The public address of the program (42–46 alphanumeric characters).
        time_range (str):
            Time range string like '12h', '1d', '7d', specifying how far back to retrieve data.

    Returns:
        None
            (Sends one or more messages or a chart image back to the user directly.)

    Raises:
        requests.exceptions.ReadTimeout:
            If the network request to the API exceeds the timeout.
        requests.exceptions.RequestException:
            If a general network error occurs during API fetching.
        Exception:
            For any unexpected error during chart creation, file handling, or sending.

    Example:
        >>> generate_and_send_chart(update, context, '9xjT3kghPz...', '7d')
        (Call this function with 'await' inside an async context.)
        (Sends a Telegram message with text summary + chart image)

    Notes:
        - Automatically detects small time ranges (<=2h or <=2d) and skips chart generation for them.
        - Saves the chart locally as a PNG file temporarily and deletes it after sending.
        - Uses Matplotlib to create professional bar charts with labeled axes and gridlines.
        - Applies Telegram Markdown formatting for better text readability.
    """
    if not is_valid_address(program_address):
        await update.message.reply_text(INVALID_PROGRAM_ADDRESS)
        return

    if not is_valid_range(time_range):
        await update.message.reply_text(INVALID_TIME_RANGE)
        return

    program_name = retrieve_program_name(program_address)
    if not program_name:
        await update.message.reply_text(PROGRAM_NOT_FOUND)
        return

    url = PROGRAM_ACTIVE_USERS_URL.format(program_address,time_range)

    try:
        response = requests.get(url, headers=headers, timeout=350)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            await update.message.reply_text("⚠️ No data available.")
            return

        time_labels = [
            datetime.utcfromtimestamp(item["blockTime"]).strftime('%Y-%m-%d %H:%M' if 'h' in time_range else '%Y-%m-%d')
            for item in data
        ]
        user_counts = [item["dau"] for item in data]
        total_active_users = sum(user_counts)

        lines = [ACTIVE_USERS_HEADER.format(time_range, program_name)]

        lines += [f"🕒 {dt} → 👥 {count}" for dt, count in zip(time_labels, user_counts)]
        lines.append("──────────────────────────────")
        lines.append(f"✅ *Total Active Users:* {total_active_users:,}")

        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

        match = re.match(r"(\d+)([hd])", time_range)
        if match:
            num, unit = int(match.group(1)), match.group(2)
            if (unit == "h" and num <= 2) or (unit == "d" and num <= 2):
                return

        plt.figure(figsize=(14, 6))
        plt.bar(time_labels, user_counts, color='steelblue')
        plt.xticks(rotation=45)
        plt.xlabel("Time")
        plt.ylabel("Active Users")
        plt.title(f"Active Users Over {time_range} | {program_name}")
        plt.tight_layout()
        plt.grid(axis='y')

        filename = f"{program_name.replace(' ', '_')}_active_users_{time_range}.png"
        plt.savefig(filename, dpi=300)
        plt.close()

        with open(filename, "rb") as photo:
            await update.message.reply_photo(photo=InputFile(photo), caption=f"📊 Active Users Chart | {program_name}", parse_mode="Markdown")

        os.remove(filename)

    except requests.exceptions.ReadTimeout:
        await update.message.reply_text(TIMEOUT_ERROR)
    except requests.exceptions.RequestException as e:
        await update.message.reply_text((NETWORK_ERROR.format(e)))
    except Exception as e:
        await update.message.reply_text((UNEXPECTED.format(e)))

async def send_program_tx_chart(update: Update, context: ContextTypes.DEFAULT_TYPE, program_address: str, range_value: str):
    """
    Generate and send a chart showing transaction counts over time for a given program.

    Fetches time-series transaction data from Vybe Network API for a program over a specified range
    (e.g., 1h, 7d). Displays a text summary and, depending on the range size, generates and sends
    a bar chart image showing transaction activity trends.

    Args:
        update (Update):
            Telegram Update object representing the incoming user message.
        context (ContextTypes.DEFAULT_TYPE):
            Telegram context containing conversation state and user data.
        program_address (str):
            The public address of the program (42–46 alphanumeric characters).
        range_value (str):
            Time range string (e.g., '1h', '12h', '7d') specifying how far back to fetch data.

    Returns:
        None
            (The function sends the output directly to the Telegram chat.)

    Raises:
        requests.exceptions.ReadTimeout:
            If the API request exceeds the allowed timeout.
        requests.exceptions.RequestException:
            For general network errors encountered during the API call.
        Exception:
            For any unexpected error during data processing, chart creation, or file handling.

    Example:
        >>>  generate_and_send_tx_chart(update, context, '9xjT3kghPz...', '1d')
        (Call this function with 'await' inside an async context.)
        (Sends a Telegram text summary + chart of transactions.)

    Notes:
        - For small ranges (1h, 2h), sends only text summaries without generating a chart.
        - For hourly breakdowns (e.g., 1d range), fetches additional 24h granular data for better charting.
        - Saves bar charts temporarily as PNG files and deletes them after sending.
        - Applies Telegram Markdown formatting for enhanced readability.
    """
    if not is_valid_address(program_address):
        await update.message.reply_text(INVALID_FORMAT)
        return

    if not is_valid_range(range_value):
        await update.message.reply_text(INVALID_TIME_RANGE)
        return

    program_name = retrieve_program_name(program_address)
    if not program_name:
        await update.message.reply_text(PROGRAM_NOT_FOUND)
        return
    url = PROGRAM_TXS_URL.format(program_address,range_value)

    try:
        response = requests.get(url, headers=headers, timeout=350)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            await update.message.reply_text("⚠️ No transaction data found for this range.")
            return

        timestamps = []
        tx_counts = []
        summary = [TRANSACTIONS_HEADER.format(range_value, program_name)]

        for entry in data:
            count = entry.get("transactionsCount", 0)
            ts = entry.get("blockTime", 0)
            readable = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            summary.append(f"🕒 {readable} → 🔁 {count:,}")
            timestamps.append(readable)
            tx_counts.append(count)

        summary.append("──────────────────────────────")
        summary.append(f"✅ *Total Transactions:* {sum(tx_counts):,}")

        await update.message.reply_text("\n".join(summary), parse_mode="Markdown")

        match = re.match(r"(\d+)([hd])", range_value)
        if match:
            value, unit = int(match.group(1)), match.group(2)

            if unit == "h" and value == 1:
                return

            if unit == "h" and 2 <= value < 24:
                time_labels = [
                    datetime.utcfromtimestamp(entry["blockTime"]).strftime('%Y-%m-%d %H:%M')
                    for entry in data
                ]
                tx_counts = [entry["transactionsCount"] for entry in data]

                plt.figure(figsize=(14, 6))
                plt.bar(time_labels, tx_counts, color='yellow')
                plt.xticks(rotation=90)
                plt.xlabel("Hour")
                plt.ylabel("Transaction Count")
                plt.title(f"Hourly Transactions ({range_value}) | {program_name}")
                plt.tight_layout()
                plt.grid(axis='y')

                filename = f"{program_name.replace(' ', '_')}_hourly_txns_{range_value}.png"
                plt.savefig(filename, dpi=300)
                plt.close()

                with open(filename, "rb") as photo:
                    await update.message.reply_photo(
                        photo=InputFile(photo),
                        caption=f"📈 Hourly Chart | {program_name} ({range_value})",
                        parse_mode="Markdown"
                    )
                os.remove(filename)
                return

            if (unit == "h" and value == 24) or (unit == "d" and value == 1):
                hourly_url = PROGRAM_TXS_URL.format(program_address,"24h")
                hourly_response = requests.get(hourly_url, headers=headers, timeout=350)
                hourly_response.raise_for_status()
                hourly_data = hourly_response.json().get("data", [])

                if not hourly_data:
                    await update.message.reply_text("⚠️ No 24-hour hourly data found.")
                    return

                hourly_labels = [
                    datetime.utcfromtimestamp(entry["blockTime"]).strftime('%Y-%m-%d %H:%M')
                    for entry in hourly_data
                ]
                hourly_counts = [entry["transactionsCount"] for entry in hourly_data]

                plt.figure(figsize=(14, 6))
                plt.bar(hourly_labels, hourly_counts, color='yellow')
                plt.xticks(rotation=90)
                plt.xlabel("Hour")
                plt.ylabel("Transaction Count")
                plt.title(f"Hourly Transactions (1d) | {program_name}")
                plt.tight_layout()
                plt.grid(axis='y')

                filename = f"{program_name.replace(' ', '_')}_hourly_txns_1d.png"
                plt.savefig(filename, dpi=300)
                plt.close()

                with open(filename, "rb") as photo:
                    await update.message.reply_photo(
                        photo=InputFile(photo),
                        caption=f"📈 Hourly Chart | {program_name} (1d)",
                        parse_mode="Markdown"
                    )
                os.remove(filename)
                return

        daily_labels = [
            datetime.utcfromtimestamp(entry["blockTime"]).strftime('%Y-%m-%d')
            for entry in data
        ]
        tx_counts = [entry["transactionsCount"] for entry in data]

        plt.figure(figsize=(14, 6))
        plt.bar(daily_labels, tx_counts, color='yellow')
        plt.xticks(rotation=45)
        plt.xlabel("Date")
        plt.ylabel("Transaction Count")
        plt.title(f"Transactions Over {range_value} | {program_name}")
        plt.tight_layout()
        plt.grid(axis='y')

        filename = f"{program_name.replace(' ', '_')}_txns_{range_value}.png"
        plt.savefig(filename, dpi=300)
        plt.close()

        with open(filename, "rb") as photo:
            await update.message.reply_photo(
                photo=InputFile(photo),
                caption=f"📈 Transaction Chart | {program_name} ({range_value})",
                parse_mode="Markdown"
            )
        os.remove(filename)

    except requests.exceptions.ReadTimeout:
        await update.message.reply_text(TIMEOUT_ERROR)
    except requests.exceptions.RequestException as e:
        await update.message.reply_text((NETWORK_ERROR.format(e)))
    except Exception as e:
        await update.message.reply_text((UNEXPECTED.format(e)))

def retrieve_daily_top_holders_chart(mint_address: str, start_date: str, end_date: str) -> tuple[str, str | None]:
    """
    Fetch and format the daily holder count for a given token mint over a specified date range.

    Retrieves historical holder counts from Vybe Network API and builds a text summary.
    If the range spans more than 2 days, also generates a bar chart image
    representing the daily number of holders.

    Args:
        mint_address (str):
            The public mint address of the token (42–46 alphanumeric characters).
        start_date (str):
            Start date in 'YYYY-MM-DD' format.
        end_date (str):
            End date in 'YYYY-MM-DD' format (must be after start_date).

    Returns:
        Tuple[str, Optional[str]]:
            - First element: A formatted text block summarizing the holder data.
            - Second element: The filename of the saved chart PNG if a chart was generated, otherwise None.
            - If validation fails or an error occurs, an error message string and None are returned.

    Raises:
        requests.exceptions.RequestException:
            If a network-related error occurs during the API call.
        json.JSONDecodeError:
            If the API response is not valid JSON.
        Exception:
            For unexpected errors during chart generation or data parsing.

    Example:
        >>> retrieve_daily_top_holders_chart('So11111111111111111111111111111111111111112', '2025-01-01', '2025-01-10')
        (
            \"📊 *Daily Holders Count*\\n🔑 *Mint:* `So111...`\\n...\",
            \"So11111111111111111111111111111111111111112_2025-01-01_to_2025-01-10_holders_chart.png\"
        )

    Notes:
        - If the date range is less than or equal to 2 days, no chart will be generated (only text summary).
        - Dates must be valid and properly formatted; otherwise, an error message will be returned.
        - The chart is saved locally with a filename derived from the mint address and date range.
    """

    if not is_valid_mint(mint_address):
        return INVALID_MINT_ADDRESS, None

    start_unix = full_datetime_to_unix(start_date)
    end_unix = full_datetime_to_unix(end_date)

    if start_unix is None or end_unix is None:
        return "❌ Invalid date format! Please use YYYY-MM-DD.", None

    url = DAILY_TOP_TOKEN_HOLDERS_URL.format(mint_address,start_unix,end_unix)

    try:
        response = requests.get(url, headers=headers, timeout=350)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            return "⚠️ No holder data found in the selected date range.", None

        time_labels = []
        holders = []
        lines = [DAILY_HOLDERS_HEADER.format(mint_address, start_date, end_date), ""]

        for item in data:
            readable_time = datetime.utcfromtimestamp(item["holdersTimestamp"]).strftime('%Y-%m-%d')
            count = item["nHolders"]
            time_labels.append(readable_time)
            holders.append(count)
            lines.append(f"🗓️ {readable_time} → 👥 {count:,}")

        total = holders[-1] if holders else 0
        lines.append("")
        lines.append(f"✅ *Latest Total Holders:* {total:,}")

        filename = f"{mint_address}_{start_date}_to_{end_date}_holders_chart.png".replace(":", "-")

        if (end_unix - start_unix) >= 2 * 86400:
            plt.figure(figsize=(14, 6))
            plt.bar(time_labels, holders, color='lightgreen')
            plt.xticks(rotation=45)
            plt.xlabel("Date")
            plt.ylabel("Holders")
            plt.title(f"Holders Count ({start_date} → {end_date})")
            plt.tight_layout()
            plt.grid(axis='y')
            plt.savefig(filename)
            plt.close()
            return "\n".join(lines), filename
        else:
            return "\n".join(lines), None

    except requests.exceptions.RequestException as e:
        return (NETWORK_ERROR.format(e)), None
    except Exception as e:
        return (UNEXPECTED.format(e)), None
def retrieve_transfer_volume_chart(mint_address: str, start_date: str, end_date: str, interval: str):
    """
    Fetch and format the transfer volume data for a given token mint over a specified time range.

    Retrieves historical transfer volumes from Vybe Network API based on the given interval
    ('hour' or 'day'). Returns a formatted text summary of the transfer volume data and generates
    a line chart image representing volume trends over time.

    Args:
        mint_address (str):
            The public mint address of the token (42–46 alphanumeric characters).
        start_date (str):
            Start date in 'YYYY-MM-DD' format.
        end_date (str):
            End date in 'YYYY-MM-DD' format (must be after start_date).
        interval (str):
            Data interval aggregation ('hour' or 'day').

    Returns:
        Tuple[str, Optional[str]]:
            - A formatted string summarizing the transfer volume data.
            - The filename of the saved chart PNG if chart generation succeeds, otherwise None.
            - An error message string and None if validation fails or an API error occurs.

    Raises:
        requests.exceptions.RequestException:
            If a network-related error occurs during the API call.
        json.JSONDecodeError:
            If the API response is not valid JSON.
        Exception:
            For any unexpected errors during data processing or plotting.

    Example:
        >>> retrieve_transfer_volume_chart('So11111111111111111111111111111111111111112', '2025-01-01', '2025-01-10', 'day')
        (
            \"📋 *Transfer Volume Data* (day)\\n🪙 *Mint:* So111...\\n📆 *Range:* 2025-01-01 ➡ 2025-01-10\\n...\",
            \"So11111111111111111111111111111111111111112_volume_2025-01-01_to_2025-01-10_day.png\"
        )

    Notes:
        - Dates must be correctly formatted and end date must be after start date.
        - Supported intervals are 'hour' and 'day' only.
        - The transfer volume chart is saved locally as a PNG file with a filename based on mint and date range.
        - Chart combines a filled area (volume under curve) and a line plot for better visualization.
    """

    if not is_valid_mint(mint_address):
        return INVALID_MINT_ADDRESS, None

    start_timestamp = full_datetime_to_unix(start_date)
    end_timestamp = full_datetime_to_unix(end_date)

    if not start_timestamp or not end_timestamp or end_timestamp <= start_timestamp:
        return INVALID_DATE_RANGE, None

    if interval.lower() not in ['hour', 'day']:
        return INVALID_INTERVAL, None

    url = TOKEN_VOLUME_URL.format(mint_address,start_timestamp,end_timestamp,interval)

    try:
        response = requests.get(url, headers=headers, timeout=350)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            return NO_VOLUME_DATA_FOUND, None

        time_stamps = [timestamp_to_date(item["timeBucketStart"]) for item in data]
        volumes = [float(item.get("volume", 0)) for item in data]

        df = pd.DataFrame({'Date': time_stamps, 'Volume': volumes})

        summary_lines = [TRANSFER_VOLUME_HEADER.format(interval, mint_address, start_date, end_date)]


        for ts, vol in zip(time_stamps, volumes):
            summary_lines.append(f"🕒 {ts} → 📦 {vol:,.2f}")

        summary_lines.append("────────────────────────────")

        filename = f"{mint_address}_volume_{start_date}_to_{end_date}_{interval}.png"

        plt.figure(figsize=(12, 6))
        plt.fill_between(df['Date'], df['Volume'], color='skyblue', alpha=0.4)
        plt.plot(df['Date'], df['Volume'], color='steelblue', linewidth=2)
        plt.xticks(rotation=45)
        plt.xlabel('Date')
        plt.ylabel('Volume')
        plt.title(f"Transfer Volume | {mint_address} ({start_date} ➡ {end_date}, {interval})")
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()

        return "\n".join(summary_lines), filename

    except requests.exceptions.RequestException as e:
        return (NETWORK_ERROR.format(e)), None
    except Exception as e:
        return (UNEXPECTED.format(e)), None

async def send_tvl_chart(update: Update, context: ContextTypes.DEFAULT_TYPE, program_address: str, resolution: str):
    """
    Generate and send a TVL (Total Value Locked) chart and summary for a given program over time.

    Fetches TVL data from Vybe Network API based on the provided program address and resolution.
    Sends a text summary showing TVL changes over time and, if enough data points exist,
    generates and sends a TVL line chart image.

    Args:
        update (Update):
            Telegram Update object representing the incoming user message.
        context (ContextTypes.DEFAULT_TYPE):
            Telegram context containing conversation state and user data.
        program_address (str):
            The public address of the program (42–46 alphanumeric characters).
        resolution (str):
            Time resolution for TVL aggregation (e.g., '1h', '1d', '1w').

    Returns:
        None
            (Sends a text message and optionally a chart image directly to the Telegram chat.)

    Raises:
        requests.exceptions.RequestException:
            If a network-related error occurs during the API call.
        json.JSONDecodeError:
            If the API response is not valid JSON.
        Exception:
            For any unexpected error during TVL plotting or file handling.

    Example:
        >>> send_tvl_chart(update, context, '9xjT3kghPz...', '1d')
        (Call this function with 'await' inside an async context.)
        (Sends a text summary of TVL changes + a line chart image showing TVL trend.)

    Notes:
        - Validates the program address and resolution format before making API requests.
        - If TVL data is missing or the program is invalid, sends a corresponding error message.
        - Chart is generated using Matplotlib and temporarily saved as a PNG file.
        - The PNG file is automatically deleted after sending to keep the server clean.
    """
    if not is_valid_address(program_address):
        await update.message.reply_text(INVALID_PROGRAM_ADDRESS)
        return

    if not is_valid_resolution(resolution):
        await update.message.reply_text(INVALID_RESOLUTION)
        return

    program_name = retrieve_program_info(program_address)
    if not program_name:
        await update.message.reply_text(PROGRAM_NOT_FOUND)
        return

    data = fetch_tvl_data(program_address, resolution)
    if not data:
        await update.message.reply_text(NO_TVL_DATA)
        return

    time_labels, tvl_values, summary_lines = [], [], []
    summary_lines.append(f"📊 *TVL Data for* `{program_name}` ({resolution})")
    summary_lines.append("──────────────────────────────")

    for item in data:
        tvl = float(item.get("tvl", 0))
        ts = item.get("time", "")
        try:
            readable = datetime.fromisoformat(ts.replace("Z", "")).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            readable = "N/A"

        time_labels.append(readable)
        tvl_values.append(tvl)
        summary_lines.append(f"🕒 {readable} → 💰 ${tvl:,.2f}")

    summary_text = "\n".join(summary_lines)
    await update.message.reply_text(summary_text, parse_mode="Markdown")

    try:
        plt.figure(figsize=(14, 6))
        plt.plot(time_labels, tvl_values, marker='o', color='blue')
        plt.xticks(rotation=45)
        plt.xlabel("Time")
        plt.ylabel("TVL (USD)")
        plt.title(f"TVL Over Time • {program_name} • {resolution}")
        plt.tight_layout()
        plt.grid(True)

        filename = f"{program_name.replace(' ', '_')}_TVL_{resolution}.png"
        plt.savefig(filename, dpi=300)
        plt.close()

        with open(filename, "rb") as photo:
            await update.message.reply_photo(photo=InputFile(photo), caption=f"📈 TVL Chart | {program_name}",
                                             parse_mode="Markdown")

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(GENERATE_ERROR)
async def send_token_balance_chart(update: Update, context: ContextTypes.DEFAULT_TYPE, wallet_address: str, days: int):
    """
    Generate and send the historical token balance chart and summary for a given wallet address.

    Fetches token balance time-series data from Vybe Network API over the past specified number of days.
    Sends a detailed text summary showing token, stake, system values, and generates a bar chart
    visualizing the token value trend over time.

    Args:
        update (Update):
            Telegram Update object representing the incoming user message.
        context (ContextTypes.DEFAULT_TYPE):
            Telegram context containing conversation state and user data.
        wallet_address (str):
            The public wallet address (42–46 alphanumeric characters).
        days (int):
            Number of past days to retrieve token balance history for.

    Returns:
        None
            (The function sends the output directly to the Telegram chat.)

    Raises:
        requests.exceptions.RequestException:
            If a network-related error occurs during the API call.
        json.JSONDecodeError:
            If the API response is not valid JSON.
        Exception:
            For any unexpected error during plotting, file handling, or API communication.

    Example:
        >>> send_token_balance_chart(update, context, '9xjT3kghPz...', 7)
        (Call this function with 'await' inside an async context.)
        (Sends a Telegram text summary + token balance bar chart image.)

    Notes:
        - Early validation checks the wallet address format before querying.
        - If no data is found, an informative warning message is sent instead of a chart.
        - The generated chart is saved temporarily as a PNG file and deleted after sending.
        - Dates are displayed in 'YYYY-MM-DD' format for better readability.
    """
    if not is_valid_address(wallet_address):
        await update.message.reply_text(INVALID_WALLET_FORMAT)
        return

    url = TOKEN_BALANCE_CHART_URL.format(wallet_address,days)

    try:
        response = requests.get(url, headers=headers, timeout=350)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            await update.message.reply_text(NO_TOKEN_BALANCE_FOUND)
            return

        dates, values = [], []
        lines = [TOKEN_BALANCE_HISTORY_HEADER.format(days, wallet_address)]

        for item in data:
            readable = datetime.utcfromtimestamp(item["blockTime"]).strftime('%Y-%m-%d')
            token_val = float(item.get("tokenValue", 0))
            stake_val = float(item.get("stakeValue", 0))
            sys_val = float(item.get("systemValue", 0))
            stake_sol = float(item.get("stakeValueSol", 0))

            lines.append(
                TOKEN_BALANCE_HISTORY_ENTRY.format(
                    readable,
                    token_val,
                    stake_val,
                    sys_val,
                    stake_sol
                )
            )

            dates.append(readable)
            values.append(token_val)

        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
        plt.figure(figsize=(14, 6))
        plt.bar(dates, values, color='skyblue')
        plt.xticks(rotation=45)
        plt.title(f" Token Value Over Time • {wallet_address[:6]}...")
        plt.xlabel("Date")
        plt.ylabel("Token Value (USD)")
        plt.tight_layout()
        plt.grid(axis='y')

        filename = f"{wallet_address[:6]}_token_chart.png"
        plt.savefig(filename)
        plt.close()

        with open(filename, "rb") as photo:
            await update.message.reply_photo(photo=InputFile(photo), caption="📈 Token Balance Chart")
        os.remove(filename)

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(NETWORK_ERROR.format(e))
    except Exception as e:
        await update.message.reply_text((UNEXPECTED.format(e)))