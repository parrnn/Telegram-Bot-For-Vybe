from typing import Optional
import os
import requests
from telegram import Update, InputFile
from telegram.ext import ContextTypes
import globals.urls as urls
import globals.preferences as preferences
import functions.functions as functions
import functions.evaluates as evaluates
import constants.messages as messages
from functions.datetime import *
import matplotlib.pyplot as plt
import re

def draw_chart(x, y, title, xlabel, ylabel, filename,
               chart_type="line", color="steelblue", rotation=45,
               marker=None, fill=False):
    plt.figure(figsize=(10, 5))
    if chart_type == "bar":
        plt.bar(x, y, color=color)
    else:
        plt.plot(x, y, color=color, marker=marker)
        if fill:
            plt.fill_between(x, y, color=color, alpha=0.3)

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=rotation)

    if chart_type == "bar":
        plt.grid(visible=True, axis='y')
    else:
        plt.grid(visible=True)

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

async def generate_chart_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                  x: list, y: list, title: str, xlabel: str, ylabel: str,
                                  filename: str, chart_type: str = "line", color: str = "steelblue",
                                  rotation: int = 45, marker: Optional[str] = None, fill: bool = False,
                                  caption: Optional[str] = None):
    draw_chart(x, y, title, xlabel, ylabel, filename, chart_type, color, rotation, marker, fill)
    with open(filename, "rb") as photo:
        await update.message.reply_photo(photo=InputFile(photo), caption=caption or title, parse_mode="Markdown")
    os.remove(filename)

async def send_program_dau_chart(update: Update, context: ContextTypes.DEFAULT_TYPE, program_address: str, time_range: str):
    if not evaluates.is_valid_address(program_address):
        await update.message.reply_text(messages.INVALID_PROGRAM_ADDRESS)
        return

    if not evaluates.is_valid_range(time_range):
        await update.message.reply_text(messages.INVALID_TIME_RANGE)
        return

    program_name = functions.retrieve_program_name(program_address)
    if not program_name:
        await update.message.reply_text(messages.PROGRAM_NOT_FOUND)
        return

    url = urls.PROGRAM_ACTIVE_USERS_URL.format(program_address, time_range)

    try:
        response = requests.get(url, headers=preferences.headers, timeout=350)
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

        lines = [messages.ACTIVE_USERS_HEADER.format(time_range, program_name)]
        lines += [f"🕒 {dt} → 👥 {count}" for dt, count in zip(time_labels, user_counts)]
        lines.append("──────────────────────────────")
        lines.append(f"✅ *Total Active Users:* {total_active_users:,}")

        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

        match = re.match(r"(\d+)([hd])", time_range)
        if match:
            num, unit = int(match.group(1)), match.group(2)
            if (unit == "h" and num <= 2) or (unit == "d" and num <= 2):
                return

        filename = f"{program_name.replace(' ', '_')}_active_users_{time_range}.png"

        await generate_chart_and_send(
            update, context,
            x=time_labels,
            y=user_counts,
            title=f"Active Users Over {time_range} | {program_name}",
            xlabel="Time",
            ylabel="Active Users",
            filename=filename,
            chart_type="bar",
            color="steelblue",
            caption=f"📊 Active Users Chart | {program_name}"
        )

    except requests.exceptions.ReadTimeout:
        await update.message.reply_text(messages.TIMEOUT_ERROR)
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(messages.NETWORK_ERROR.format(e))
    except Exception as e:
        await update.message.reply_text(messages.UNEXPECTED_ERROR.format(e))

async def send_program_tx_chart(update: Update, context: ContextTypes.DEFAULT_TYPE, program_address: str, range_value: str):
    if not evaluates.is_valid_address(program_address):
        await update.message.reply_text(messages.INVALID_FORMAT)
        return

    if not evaluates.is_valid_range(range_value):
        await update.message.reply_text(messages.INVALID_TIME_RANGE)
        return

    program_name = functions.retrieve_program_name(program_address)
    if not program_name:
        await update.message.reply_text(messages.PROGRAM_NOT_FOUND)
        return

    url = urls.PROGRAM_TXS_URL.format(program_address, range_value)

    try:
        response = requests.get(url, headers=preferences.headers, timeout=350)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            await update.message.reply_text("⚠️ No transaction data found for this range.")
            return

        timestamps, tx_counts = [], []
        summary = [messages.TRANSACTIONS_HEADER.format(range_value, program_name)]

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
            if unit == "h" and value <= 2:
                return

        labels = [datetime.utcfromtimestamp(entry["blockTime"]).strftime('%Y-%m-%d %H:%M') for entry in data]
        filename = f"{program_name.replace(' ', '_')}_txns_{range_value}.png"

        await generate_chart_and_send(update, context,
            x=labels,
            y=tx_counts,
            title=f"Transactions Over {range_value} | {program_name}",
            xlabel="Time",
            ylabel="Transaction Count",
            filename=filename,
            chart_type="bar",
            color="yellow",
            caption=f"📈 Transaction Chart | {program_name} ({range_value})"
        )

    except requests.exceptions.ReadTimeout:
        await update.message.reply_text(messages.TIMEOUT_ERROR)
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(messages.NETWORK_ERROR.format(e))
    except Exception as e:
        await update.message.reply_text(messages.UNEXPECTED_ERROR.format(e))

async def send_tvl_chart(update: Update, context: ContextTypes.DEFAULT_TYPE, program_address: str, resolution: str):
    if not evaluates.is_valid_address(program_address):
        await update.message.reply_text(messages.INVALID_PROGRAM_ADDRESS)
        return

    if not evaluates.is_valid_resolution(resolution):
        await update.message.reply_text(messages.INVALID_RESOLUTION)
        return

    program_name = functions.retrieve_program_info(program_address)
    if not program_name:
        await update.message.reply_text(messages.PROGRAM_NOT_FOUND)
        return

    data = functions.fetch_tvl_data(program_address, resolution)
    if not data:
        await update.message.reply_text(messages.NO_TVL_DATA)
        return

    time_labels, tvl_values, summary_lines = [], [], []
    summary_lines.append(f"📊 *TVL Data for* `{program_name}` ({resolution})")
    summary_lines.append("──────────────────────────────")

    for item in data:
        tvl = float(item.get("tvl", 0))
        ts = item.get("time", "")
        readable = datetime.fromisoformat(ts.replace("Z", "")).strftime('%Y-%m-%d %H:%M:%S')
        time_labels.append(readable)
        tvl_values.append(tvl)
        summary_lines.append(f"🕒 {readable} → 💰 ${tvl:,.2f}")

    await update.message.reply_text("\n".join(summary_lines), parse_mode="Markdown")

    filename = f"{program_name.replace(' ', '_')}_TVL_{resolution}.png"
    await generate_chart_and_send(update, context,
        x=time_labels,
        y=tvl_values,
        title=f"TVL Over Time • {program_name} • {resolution}",
        xlabel="Time",
        ylabel="TVL (USD)",
        filename=filename,
        chart_type="line",
        color="blue",
        marker="o",
        caption=f"📈 TVL Chart | {program_name}"
    )

async def send_token_balance_chart(update: Update, context: ContextTypes.DEFAULT_TYPE, wallet_address: str, days: int):
    if not evaluates.is_valid_address(wallet_address):
        await update.message.reply_text(messages.INVALID_WALLET_FORMAT)
        return

    url = urls.TOKEN_BALANCE_CHART_URL.format(wallet_address, days)

    try:
        response = requests.get(url, headers=preferences.headers, timeout=350)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            await update.message.reply_text(messages.NO_TOKEN_BALANCE_FOUND)
            return

        dates, values, lines = [], [], [messages.TOKEN_BALANCE_HEADER_TEMPLATE.format(days, wallet_address)]

        for item in data:
            readable = datetime.utcfromtimestamp(item["blockTime"]).strftime('%Y-%m-%d')
            token_val = float(item.get("tokenValue", 0))
            stake_val = float(item.get("stakeValue", 0))
            sys_val = float(item.get("systemValue", 0))
            stake_sol = float(item.get("stakeValueSol", 0))
            lines.append(messages.TOKEN_BALANCE_HISTORY_ENTRY.format(readable, token_val, stake_val, sys_val, stake_sol))
            dates.append(readable)
            values.append(token_val)

        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

        filename = f"{wallet_address[:6]}_token_chart.png"
        await generate_chart_and_send(update, context,
            x=dates,
            y=values,
            title=f"Token Value Over Time • {wallet_address[:6]}...",
            xlabel="Date",
            ylabel="Token Value (USD)",
            filename=filename,
            chart_type="bar",
            color="skyblue",
            caption="📈 Token Balance Chart"
        )

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(messages.NETWORK_ERROR.format(e))
    except Exception as e:
        await update.message.reply_text(messages.UNEXPECTED_ERROR.format(e))
def retrieve_daily_top_holders_chart(mint_address: str, start_date: str, end_date: str) -> tuple[str, Optional[str]]:
    """
    Fetch and format the daily holder count for a token over a date range.
    Returns text summary and filename of generated chart (if applicable).
    """
    if not evaluates.is_valid_mint(mint_address):
        return messages.INVALID_MINT_ADDRESS, None

    start_unix = full_datetime_to_unix(start_date)
    end_unix = full_datetime_to_unix(end_date)

    if start_unix is None or end_unix is None or end_unix <= start_unix:
        return messages.INVALID_DATE_RANGE, None

    url = urls.DAILY_TOP_TOKEN_HOLDERS_URL.format(mint_address, start_unix, end_unix)

    try:
        response = requests.get(url, headers=preferences.headers, timeout=350)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            return messages.NO_DATA_FOUND, None

        labels = []
        counts = []
        lines = [messages.DAILY_HOLDERS_HEADER.format(mint_address, start_date, end_date), ""]

        for item in data:
            date_str = datetime.utcfromtimestamp(item["holdersTimestamp"]).strftime('%Y-%m-%d')
            count = item["nHolders"]
            labels.append(date_str)
            counts.append(count)
            lines.append(f"🗓️ {date_str} → 👥 {count:,}")

        latest_total = counts[-1] if counts else 0
        lines.append("")
        lines.append(f"✅ *Latest Total Holders:* {latest_total:,}")

        # Only generate chart if range > 2 days
        if (end_unix - start_unix) <= 2 * 86400:
            return "\n".join(lines), None

        filename = f"{mint_address}_holders_{start_date}_to_{end_date}.png"
        draw_chart(
            x=labels,
            y=counts,
            title=f"Holders Count | {mint_address} ({start_date} → {end_date})",
            xlabel="Date",
            ylabel="Holders",
            filename=filename,
            chart_type="bar",
            color="lightgreen"
        )

        return "\n".join(lines), filename

    except requests.exceptions.RequestException as e:
        return messages.NETWORK_ERROR.format(e), None
    except Exception as e:
        return messages.UNEXPECTED_ERROR.format(e), None
def retrieve_transfer_volume_chart(mint_address: str, start_date: str, end_date: str, interval: str) -> tuple[str, Optional[str]]:
    """
    Fetch transfer volume for a token over a range and optionally generate a volume chart.
    Returns text summary + filename of chart (if applicable).
    """
    if not evaluates.is_valid_mint(mint_address):
        return messages.INVALID_MINT_ADDRESS, None

    start_ts = full_datetime_to_unix(start_date)
    end_ts = full_datetime_to_unix(end_date)

    if not start_ts or not end_ts or end_ts <= start_ts:
        return messages.INVALID_DATE_RANGE, None

    if interval.lower() not in ['hour', 'day']:
        return messages.INVALID_INTERVAL, None

    url = urls.TOKEN_VOLUME_URL.format(mint_address, start_ts, end_ts, interval)

    try:
        response = requests.get(url, headers=preferences.headers, timeout=350)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            return messages.NO_VOLUME_DATA_FOUND, None

        dates = [timestamp_to_date(entry["timeBucketStart"]) for entry in data]
        volumes = [float(entry.get("volume", 0)) for entry in data]

        lines = [messages.TRANSFER_VOLUME_HEADER.format(interval, mint_address, start_date, end_date), ""]

        for dt, vol in zip(dates, volumes):
            lines.append(f"🕒 {dt} → 📦 {vol:,.2f}")

        lines.append("────────────────────────────")

        filename = f"{mint_address}_volume_{start_date}_to_{end_date}_{interval}.png"
        draw_chart(
            x=dates,
            y=volumes,
            title=f"Transfer Volume | {mint_address} ({start_date} → {end_date})",
            xlabel="Date",
            ylabel="Volume",
            filename=filename,
            chart_type="line",
            color="skyblue",
            fill=True
        )

        return "\n".join(lines), filename

    except requests.exceptions.RequestException as e:
        return messages.NETWORK_ERROR.format(e), None
    except Exception as e:
        return messages.UNEXPECTED_ERROR.format(e), None
