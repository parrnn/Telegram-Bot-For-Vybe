from telegram import Update, InputFile
from telegram.ext import ContextTypes
import requests
import re
import json
from datetime import timezone, datetime
import matplotlib.pyplot as plt
import os
import pandas as pd
from typing import Union, Tuple

# API request headers
headers = {
    "accept": "application/json",
    "X-API-KEY": "YOUR_API_KEY"
}

def is_valid_range(r: str) -> bool:
    """
    Check if the given range string is valid (e.g., '1h', '7d').

    Args:
        r (str): Range string to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    return bool(re.fullmatch(r"\d+(h|d)", r))

def is_valid_address(address: str) -> bool:
    """
    Validate if the provided address is alphanumeric and 42 to 46 characters long.

    Args:
        address (str): Wallet or program address.

    Returns:
        bool: True if valid, False otherwise.
    """
    return bool(re.fullmatch(r"[a-zA-Z0-9]{42,46}", address))

def is_valid_limit(value: str) -> bool:
    """
    Validate if the input value is a positive integer.

    Args:
        value (str): Value to validate.

    Returns:
        bool: True if valid positive integer, False otherwise.
    """
    return value.isdigit() and int(value) > 0

def is_valid_days(value: str) -> bool:
    """
    Check if the number of days is between 1 and 30.

    Args:
        value (str): Days value as a string.

    Returns:
        bool: True if between 1 and 30, False otherwise.
    """
    return value.isdigit() and 1 <= int(value) <= 30

def is_valid_mint(address: str) -> bool:
    """
    Validate if the given mint address is alphanumeric and between 42-46 characters.

    Args:
        address (str): Mint address to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    return bool(re.fullmatch(r"[a-zA-Z0-9]{42,46}", address))

def is_valid_resolution(res: str) -> bool:
    """
    Validate if the resolution string is one of the allowed formats.

    Args:
        res (str): Resolution string (e.g., '1h', '1d', '1mo').

    Returns:
        bool: True if valid, False otherwise.
    """
    return bool(re.fullmatch(r"\d+(s|m|h|d|w|mo|y)", res))

def human_format(num: Union[int, float]) -> str:
    """
    Convert a large number into a human-readable format (e.g., 1.2K, 3.4M).

    Args:
        num (int or float): Number to format.

    Returns:
        str: Human-readable string representation.
    """
    try:
        num = float(num)
        for unit in ["", "K", "M", "B", "T"]:
            if abs(num) < 1000.0:
                return f"{num:.2f}{unit}"
            num /= 1000.0
        return f"{num:.2f}P"
    except (ValueError, TypeError):
        return "N/A"

def to_unix_from_full_datetime(human_time_str: str) -> Union[int, None]:
    """
    Convert a date string (YYYY-MM-DD) into a Unix timestamp in UTC.

    Args:
        human_time_str (str): Date string in 'YYYY-MM-DD' format.

    Returns:
        int | None: Unix timestamp if valid, otherwise None.
    """
    try:
        dt = datetime.strptime(human_time_str, '%Y-%m-%d')
        return int(dt.replace(tzinfo=timezone.utc).timestamp())
    except ValueError:
        return None

def convert_to_date(timestamp: int) -> str:
    """
    Convert a Unix timestamp to a human-readable date string (UTC).

    Args:
        timestamp (int): Unix timestamp.

    Returns:
        str: Date string in 'YYYY-MM-DD HH:MM' format.
    """
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')

def get_nft_collection_owners(collection_address: str) -> Union[str, list]:
    """
    Fetch the top NFT owners of a given NFT collection from Vybe Network API.

    Retrieves and formats the top 10 owners using numbered emojis (1️⃣ to 🔟),
    and shortens addresses for readability. Handles splitting long messages
    into chunks if needed.

    Args:
        collection_address (str):
            The address of the NFT collection (must be alphanumeric).

    Returns:
        Union[str, list]:
            - A single formatted string if the result fits under 4000 characters.
            - A list of string chunks if the result exceeds Telegram's message size limit.
            - A string containing an error message if validation or API request fails.

    Raises:
        requests.exceptions.RequestException:
            If there is a network-related error during the API call.
        ValueError:
            If the API response cannot be parsed as JSON.
        Exception:
            For any unexpected error during execution.

    Example:
        >>> get_nft_collection_owners('8fj3h5u...')
        📦 *Top Owners of:* 8fj3h5...4hf9
        1️⃣
        👤 *Owner:* 5B28C3...4Fd9
        🎁 *NFTs:* 12
        ...
    """
    if not re.fullmatch(r"[a-zA-Z0-9]+", collection_address):
        return "❌ Invalid collection address! Only alphanumeric characters are allowed."

    url = f"https://api.vybenetwork.xyz/nft/collection-owners/{collection_address}"

    try:
        response = requests.get(url, headers=headers, timeout=250)

        if response.status_code == 403:
            return "🚫 Forbidden (403): This collection is not accessible."
        elif response.status_code == 404:
            return "🔍 Not Found (404): No such collection found."

        response.raise_for_status()
        data = response.json()

        owners = data.get("data", [])
        if not owners:
            return "⚠️ No owners found for this collection."

        top_owners = owners[:10]

        emoji_numbers = {
            1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣",
            6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"
        }

        short_address = f"{collection_address[:6]}...{collection_address[-4:]}"
        result = [f"📦 *Top Owners of:* {short_address}\n"]

        for idx, item in enumerate(top_owners, start=1):
            emoji = emoji_numbers.get(idx, f"*{idx}.*")
            owner = item.get("owner", "N/A")
            amount = item.get("amount", 0)
            owner_short = f"{owner[:6]}...{owner[-4:]}"
            result.append(f"{emoji}\n👤 *Owner:* {owner_short}\n🎁 *NFTs:* {amount}\n")

        # Split if message is too long
        chunks = []
        chunk = ""
        for line in result:
            if len(chunk) + len(line) < 4000:
                chunk += line + "\n"
            else:
                chunks.append(chunk)
                chunk = line + "\n"
        if chunk:
            chunks.append(chunk)

        return chunks if len(chunks) > 1 else chunks[0]

    except requests.exceptions.RequestException as e:
        return f"❌ Network error occurred:\n{e}"
    except ValueError:
        return "❌ Failed to parse JSON response."
    except Exception as e:
        return f"⚠️ Unexpected error:\n{e}"
def get_program_details(program_address: str) -> Tuple[str, str]:
    """
    Fetch and format the details of a specific program from Vybe Network API.

    Retrieves metadata such as program name, entity, labels, daily stats (active users,
    new users, transactions), and description. Returns a formatted message and the logo URL.

    Args:
        program_address (str):
            The program's public address (must be a valid alphanumeric 42–46 characters long).

    Returns:
        Tuple[str, str]:
            - First element: A formatted message string containing program overview details.
            - Second element: The URL string to the program's logo.
            - If an error occurs, returns a single error message string instead of a tuple.

    Raises:
        requests.exceptions.RequestException:
            If there is a network error during the API call.
        json.JSONDecodeError:
            If the API response is not valid JSON.
        Exception:
            For any unexpected error during data retrieval or formatting.

    Example:
        >>> get_program_details('9AefkXv83z...')
        (
            \"📌 *Program Overview*\\n\\n🏛️ *Entity:* Orca\\n📛 *Name:* Orca\\n...\",
            \"https://storage.googleapis.com/.../orca_logo.png\"
        )
    """

    if not is_valid_address(program_address):
        return "❌ Invalid address! Only alphanumeric characters are allowed."

    url = f"https://api.vybenetwork.xyz/program/{program_address}"

    try:
        response = requests.get(url, headers=headers, timeout=250)

        if response.status_code in [400, 403, 404]:
            return "❌ Invalid or inaccessible program address."

        response.raise_for_status()
        data = response.json()

        entity_name = data.get("entityName", "N/A")
        friendly_name = data.get("friendlyName", "N/A")
        dau = data.get("dau", "N/A")
        new_users = data.get("newUsersChange1d", "N/A")
        txns = data.get("transactions1d", "N/A")
        labels = data.get("labels", [])
        logo_url = data.get("logoUrl", "N/A")
        description = data.get("programDescription", "N/A")

        labels_text = ", ".join(labels) if labels else "None"

        message = (
            f"📌 *Program Overview*\n\n"
            f"🏛️ *Entity:* {entity_name}\n"
            f"📛 *Name:* {friendly_name}\n"
            f"🏷️ *Labels:* {labels_text}\n\n"
            f"📊 *Stats (24h)*\n"
            f"👥 Active Users: {dau:,}\n"
            f"🆕 New Users: {new_users:,}\n"
            f"🔁 Transactions: {txns:,}\n\n"
            f"📖 *Description:*\n{description or 'N/A'}"
        )

        return message, logo_url

    except Exception:
        return "❌ Something went wrong. Please try again."
def get_program_name(program_address: str) -> Union[str, None]:
    """
    Retrieve the display name of a program from Vybe Network API.

    Attempts to fetch a friendly name, fallback name, or entity name
    associated with a given program address. Returns the address itself
    if no name is found.

    Args:
        program_address (str):
            The public address of the program to query (42–46 alphanumeric characters).

    Returns:
        Union[str, None]:
            - The program's friendly name, name, entity name, or the address itself if found.
            - None if the program is invalid, inaccessible, or if an error occurs.

    Raises:
        requests.exceptions.RequestException:
            If there is a network error during the API call.
        json.JSONDecodeError:
            If the response is not valid JSON.
        Exception:
            For any unexpected errors during fetching.

    Example:
        >>> get_program_name('9AefkXv83z...')
        'Orca'
    """
    url = f"https://api.vybenetwork.xyz/program/{program_address}"
    try:
        response = requests.get(url, headers=headers, timeout=250)
        if response.status_code in [400, 403, 404]:
            return None
        response.raise_for_status()
        info = response.json()
        return (
            info.get("friendlyName")
            or info.get("name")
            or info.get("entityName")
            or program_address
        )
    except Exception:
        return None

def get_top_active_wallets(program_address: str, days: int = 1, limit: int = 10) -> str:
    """
    Retrieve and format a list of the top active wallets for a given program over a specified time period.

    Fetches the most active wallets (based on transaction counts) from Vybe Network API, formats the list
    with emojis and short wallet addresses for display.

    Args:
        program_address (str):
            The public address of the program (must be 42–46 alphanumeric characters).
        days (int, optional):
            Number of past days to analyze (between 1 and 30). Defaults to 1.
        limit (int, optional):
            Maximum number of top wallets to retrieve. Defaults to 10.

    Returns:
        str:
            A formatted text block listing the top active wallets, or an error message if validation fails
            or the API call encounters an error.

    Raises:
        requests.exceptions.RequestException:
            If a network-related error occurs during the API call.
        Exception:
            For any unexpected error during data processing or response formatting.

    Example:
        >>> get_top_active_wallets('9AefkXv83z...', days=7, limit=5)
        📊 *Top 5 Active Wallets*
        🧾 *Program:* Orca
        📆 *Last 7 Days*
        1️⃣ 6T25g2...deF9 — 🔁 *1,203*
        2️⃣ D5gP12...A0F8 — 🔁 *1,045*
        ...
    """

    if not is_valid_address(program_address):
        return "❌ Invalid format! Only alphanumeric characters are allowed."

    if not is_valid_days(str(days)):
        return "❌ Days must be between 1 and 30."

    if not is_valid_limit(str(limit)):
        return "❌ Limit must be a positive number."

    program_name = get_program_name(program_address)
    if not program_name:
        return "🚫 Program not found or invalid."

    url = f"https://api.vybenetwork.xyz/program/{program_address}/active-users?days={days}&limit={limit}"

    try:
        response = requests.get(url, headers=headers, timeout=250)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            return "⚠️ No active user data found."

        emoji_numbers = {
            1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣",
            6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"
        }

        output = [
            f"📊 *Top {limit} Active Wallets*",
            f"🧾 *Program:* {program_name}",
            f"📆 *Last {days} Days*",
        ]

        for i, user in enumerate(data, 1):
            emoji = emoji_numbers.get(i, f"*{i}.*")
            wallet = user.get("wallet", "N/A")
            txs = f"{user.get('transactions', 0):,}"
            short_wallet = f"{wallet[:6]}...{wallet[-4:]}"
            output.append(f"{emoji} {short_wallet} — 🔁 *{txs}*")

        return "\n".join(output)

    except requests.exceptions.RequestException as e:
        return f"❌ Network error:\n{e}"
    except Exception as e:
        return f"⚠️ Unexpected error:\n{e}"

def to_float_safe(val, default: float = 0.0) -> float:
    """
    Safely convert a value to a float.

    Attempts to cast the input to a float. If the conversion fails
    due to a ValueError or TypeError, returns a provided default value.

    Args:
        val:
            The value to convert to float (can be any type).
        default (float, optional):
            Value to return if conversion fails. Defaults to 0.0.

    Returns:
        float:
            The successfully converted float value, or the default if conversion fails.

    Example:
        >>> to_float_safe("3.14")
        3.14
        >>> to_float_safe(None)
        0.0
        >>> to_float_safe("abc", default=1.0)
        1.0
    """
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def get_nft_portfolio(wallet_address: str) -> str:
    """
    Fetch and format the NFT portfolio of a given wallet from Vybe Network API.

    Retrieves overall wallet stats such as total SOL and USD value,
    along with a breakdown of NFT collections held, their item counts,
    and valuation in SOL and USD.

    Args:
        wallet_address (str):
            The public address of the wallet (42–46 alphanumeric characters).

    Returns:
        str:
            A formatted string summarizing the wallet's NFT portfolio.
            If the wallet has no NFTs, network errors occur, or the address is invalid,
            a corresponding error message is returned.

    Raises:
        requests.exceptions.RequestException:
            If there is a network-related error during the API call.
        json.JSONDecodeError:
            If the API response is not valid JSON.
        Exception:
            For any unexpected error during the API call or data processing.

    Example:
        >>> get_nft_portfolio('9xjT3kghPz...')
        \"💥 *NFT Portfolio*\\n👛 *Wallet:* 9xjT3k...Pz\\n🪙 *Total SOL Value:* 3.12 ◎ ...\"

    Notes:
        - If the output text exceeds typical message size limits (like Telegram 4096 chars),
          you may need to split the output manually before sending.
    """
    if not is_valid_address(wallet_address):
        return "❌ Invalid wallet address! Only alphanumeric characters allowed."

    url = f"https://api.vybenetwork.xyz/account/nft-balance/{wallet_address}"

    try:
        response = requests.get(url, headers=headers, timeout=250)

        if response.status_code == 404:
            return "🚫 Wallet not found or has no NFT data."

        response.raise_for_status()
        data = response.json()

        output = [
            "💥 *NFT Portfolio*",
            f"👛 *Wallet:* {data.get('ownerAddress', 'N/A')}",
            f"🪙 *Total SOL Value:* {to_float_safe(data.get('totalSol')):.2f} ◎",
            f"💵 *Total USD Value:* ${to_float_safe(data.get('totalUsd')):,.2f}",
            f"📚 *NFT Collections:* {data.get('totalNftCollectionCount', 0)}"
        ]

        collections = data.get("data", [])
        if not collections:
            output.append("\n⚠️ No NFT collections found.")
        else:
            output.append("\n🧾 *Collections:*")
            for nft in collections:
                name = nft.get("name", "N/A")
                collection = nft.get("collectionAddress", "N/A")
                items = nft.get("totalItems", 0)
                val_sol = to_float_safe(nft.get("valueSol"))
                val_usd = to_float_safe(nft.get("valueUsd"))
                price_sol = to_float_safe(nft.get("priceSol"))
                price_usd = to_float_safe(nft.get("priceUsd"))

                output.append(
                    f"\n🎭 *{name}*"
                    f"\n🔗 Collection: {collection}"
                    f"\n📦 Items: {items}"
                    f"\n💰 Value: {val_sol:.2f} ◎ / ${val_usd:,.2f}"
                    f"\n🏷️ Price: {price_sol:.2f} ◎ / ${price_usd:,.2f}"
                )

        return "\n".join(output)

    except requests.exceptions.RequestException as e:
        return f"❌ Network error:\n{e}"
    except json.JSONDecodeError:
        return "❌ Failed to parse JSON response."
    except Exception as e:
        return f"⚠️ Unexpected error:\n{e}"
def get_wallet_pnl_summary(wallet_address: str, days: int) -> list[str] | str:
    """
    Fetch and format the profit and loss (PnL) summary for a given wallet over a specified time period.

    Retrieves realized and unrealized PnL, trade volume, total trades, win rate, and per-token trading metrics
    from Vybe Network API. Returns a formatted string or a list of string chunks if the output is too large.

    Args:
        wallet_address (str):
            The wallet's public address (42–46 alphanumeric characters).
        days (int):
            Number of past days to calculate the PnL summary (e.g., 1, 7, or 30).

    Returns:
        Union[list[str], str]:
            - A list of message chunks if the result exceeds 4000 characters (Telegram's message limit).
            - A single formatted string if the result fits in one message.
            - An error message string if validation or data retrieval fails.

    Raises:
        requests.exceptions.RequestException:
            If there is a network-related error during the API call.
        json.JSONDecodeError:
            If the API response is not valid JSON.
        Exception:
            For any unexpected error during data formatting or processing.

    Example:
        >>> get_wallet_pnl_summary('9xjT3kghPz...', days=7)
        [
            \"💥 *PnL Summary (7d)*\\n👛 Wallet: `9xjT3kghPz...`\\n💵 *Realized PnL:* $1234.56\\n...\",
            \"🪙 *SOL*\\n💰 Realized: $500.00\\n...\\n\"
        ]

    Notes:
        - If multiple tokens are involved, token metrics are appended after the PnL summary.
        - The function automatically splits long outputs into multiple chunks.
    """

    if not is_valid_address(wallet_address):
        return "❌ Invalid wallet address format."

    url = f"https://api.vybenetwork.xyz/account/pnl/{wallet_address}?resolution={days}d"

    try:
        response = requests.get(url, headers=headers, timeout=1250)
        if response.status_code == 404:
            return "❌ Wallet not found or has no trading data."

        response.raise_for_status()
        data = response.json()

        summary = data.get("summary", {})
        output = [
            f"💥 *PnL Summary ({days}d)*",
            f"👛 Wallet: `{wallet_address}`",
            f"💵 *Realized PnL:* ${float(summary.get('realizedPnlUsd', 0)):.2f}",
            f"📉 *Unrealized PnL:* ${float(summary.get('unrealizedPnlUsd', 0)):.2f}",
            f"🔁 *Trade Volume:* ${float(summary.get('tradesVolumeUsd', 0)):.2f}",
            f"📊 *Total Trades:* {summary.get('tradesCount', 0)}",
            f"📦 *Avg. Trade Size:* ${float(summary.get('averageTradeUsd', 0)):.2f}",
            f"🏆 *Win Rate:* {float(summary.get('winRate', 0)) * 100:.2f}%",
        ]

        tokens = data.get("tokenMetrics", [])
        if tokens:
            output.append("\n📌 *Token Metrics:*")
            for token in tokens:
                symbol = token.get("tokenSymbol", "N/A")
                realized = float(token.get("realizedPnlUsd", 0))
                unrealized = float(token.get("unrealizedPnlUsd", 0))
                buys = token.get("buys", {})
                sells = token.get("sells", {})

                output.extend([
                    f"\n🪙 *{symbol}*",
                    f"💰 Realized: ${realized:.2f}",
                    f"📉 Unrealized: ${unrealized:.2f}",
                    f"🛒 Buys: ${float(buys.get('volumeUsd', 0)):.2f} | {buys.get('transactionCount', 0)} txs",
                    f"🏷️ Sells: ${float(sells.get('volumeUsd', 0)):.2f} | {sells.get('transactionCount', 0)} txs"
                ])

        result = "\n".join(output)

        chunks = []
        while len(result) > 4000:
            split_index = result.rfind("\n", 0, 4000)
            if split_index == -1:
                split_index = 4000
            chunks.append(result[:split_index])
            result = result[split_index:].lstrip()
        chunks.append(result)

        return chunks

    except requests.exceptions.RequestException as e:
        return f"❌ Network error: {e}"
    except Exception as e:
        return f"⚠️ Unexpected error: {e}"


def get_wallet_portfolio_summary(wallet_address: str) -> str:
    """
    Fetch and format the total portfolio summary for a given wallet, including token and NFT values.

    Aggregates the total USD value of tokens and NFTs held by the wallet,
    and returns a formatted summary displaying token value, NFT value, and the combined portfolio total.

    Args:
        wallet_address (str):
            The public address of the wallet (42–46 alphanumeric characters).

    Returns:
        str:
            A formatted summary of the wallet's portfolio in USD, or an error message
            if the wallet is invalid, not found, or has no recorded portfolio activity.

    Raises:
        requests.exceptions.RequestException:
            If a network error occurs during the API call.
        json.JSONDecodeError:
            If the API response is not valid JSON.
        Exception:
            For unexpected errors during portfolio aggregation.

    Example:
        >>> get_wallet_portfolio_summary('9xjT3kghPz...')
        📊 *Portfolio Summary*
        👛 Wallet: `9xjT3kghPz...`

        💼 *Token Value:* $3,254.32
        🎨 *NFT Value:* $1,204.50
        🧾 *Total Portfolio:* 💵 $4,458.82

    Notes:
        - If no valid portfolio data is found for the wallet, an error message is returned instead of a summary.
        - Internally makes three API calls: portfolio check, token balance, and NFT balance.
    """
    if not is_valid_address(wallet_address):
        return "❌ Invalid wallet address! Only letters and numbers are allowed."

    def fetch_json(url: str) -> dict | None:
        try:
            response = requests.get(url, headers=headers, timeout=250)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            return None

    check_url = f"https://api.vybenetwork.xyz/account/pnl/{wallet_address}?resolution=1d"
    check_data = fetch_json(check_url)

    if not check_data or (not check_data.get("summary") and not check_data.get("tokenMetrics")):
        return "❌ Wallet not found or has no portfolio activity."

    token_data = fetch_json(f"https://api.vybenetwork.xyz/account/token-balance/{wallet_address}")
    nft_data = fetch_json(f"https://api.vybenetwork.xyz/account/nft-balance/{wallet_address}")

    token_usd = float(token_data.get("totalTokenValueUsd", 0)) if token_data else 0.0
    nft_usd = float(nft_data.get("totalUsd", 0)) if nft_data else 0.0
    total = token_usd + nft_usd

    return (
        f"📊 *Portfolio Summary*\n"
        f"👛 Wallet: `{wallet_address}`\n\n"
        f"💼 *Token Value:* ${token_usd:,.2f}\n"
        f"🎨 *NFT Value:* ${nft_usd:,.2f}\n"
        f"🧾 *Total Portfolio:* 💵 ${total:,.2f}"
    )


def get_wallet_token_summary(wallet_address: str) -> str | list[str]:
    """
    Fetch and format the token balance summary for a given wallet.

    Retrieves all token holdings associated with the wallet from Vybe Network API,
    including 24h price changes, value changes, amounts, and verification status.
    Returns a formatted string or splits into multiple chunks if necessary.

    Args:
        wallet_address (str):
            The public address of the wallet (42–46 alphanumeric characters).

    Returns:
        Union[str, list[str]]:
            - A single formatted string if the output size is within platform limits.
            - A list of strings (chunks) if the output exceeds 4000 characters (e.g., Telegram limit).
            - An error message string if the wallet is invalid, not found, or if a network error occurs.

    Raises:
        requests.exceptions.RequestException:
            If there is a network error during the API call.
        json.JSONDecodeError:
            If the API response is not a valid JSON.
        Exception:
            For unexpected errors during token formatting or data parsing.

    Example:
        >>> get_wallet_token_summary('9xjT3kghPz...')
        \"🧾 *Wallet Token Summary*\\n👛 Wallet: `9xjT3kghPz...`\\n💰 Total Token Value (USD): $4,321.00\\n...\"

    Notes:
        - The function uses `🟢`, `🔴`, and `⚪️` emojis to visually indicate positive, negative, or neutral value changes.
        - If token count is large, output is split automatically to avoid exceeding message size limits.
    """

    def to_float_safe(value, default=0.0):
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def to_int_safe(value, default=0):
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    if not is_valid_address(wallet_address):
        return "❌ Invalid wallet address! It must only contain letters and numbers."

    url = f"https://api.vybenetwork.xyz/account/token-balance/{wallet_address}"

    try:
        response = requests.get(url, headers=headers, timeout=250)
        if response.status_code == 404:
            return "❌ Wallet not found or has no token data."
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return f"❌ Network error:\n{e}"
    except json.JSONDecodeError:
        return "❌ Failed to parse JSON response."

    if not data.get("data"):
        return "⚠️ This wallet has no token balances."

    output = [
        "🧾 *Wallet Token Summary*",
        f"👛 Wallet: `{data.get('ownerAddress', 'N/A')}`",
        f"💰 Total Token Value (USD): ${to_float_safe(data.get('totalTokenValueUsd')):,.2f}",
        f"🔒 Staked SOL (USD): ${to_float_safe(data.get('stakedSolBalanceUsd')):,.2f}",
        f"🪙 Token Count: {to_int_safe(data.get('totalTokenCount'))}",
        "\n📊 *Tokens:*"
    ]

    for token in data.get("data", []):
        symbol = token.get("symbol", "N/A")
        name = token.get("name", "N/A")
        mint = token.get("mintAddress", "N/A")
        price_change = to_float_safe(token.get("priceUsd1dChange"))
        value_change = to_float_safe(token.get("valueUsd1dChange"))
        amount = to_float_safe(token.get("amount"))
        value_usd = to_float_safe(token.get("valueUsd"))
        verified = "✅" if token.get("verified", False) else "❌"
        emoji = "🟢" if value_change > 0 else "🔴" if value_change < 0 else "⚪️"

        output.append(
            f"\n{emoji} *{symbol}* ({name})\n"
            f"🔗 Mint: `{mint}`\n"
            f"📈 24h Price Change: {price_change:.2f}%\n"
            f"💸 24h Value Change: ${value_change:.2f}\n"
            f"📦 Amount: {amount}\n"
            f"💵 Value: ${value_usd:,.2f}\n"
            f"✔️ Verified: {verified}"
        )

    result = "\n".join(output)
    if len(result) <= 4000:
        return result

    chunks = []
    while len(result) > 4000:
        split_at = result.rfind("\n", 0, 4000)
        if split_at == -1:
            split_at = 4000
        chunks.append(result[:split_at])
        result = result[split_at:].lstrip()
    chunks.append(result)
    return chunks
def get_token_info(mint_address: str) -> tuple[str, str] | str:
    """
    Fetch and format detailed information about a token given its mint address.

    Retrieves pricing, supply, category, verification status, market cap, and 24h volume
    from Vybe Network API. Returns the full formatted info as a string along with the logo URL.

    Args:
        mint_address (str):
            The public mint address of the token (42–46 alphanumeric characters).

    Returns:
        Union[Tuple[str, str], str]:
            - A tuple (formatted info string, logo URL string) if successful.
            - A string containing an error message if the token is not found,
              the address is invalid, or an error occurs during the request.

    Raises:
        requests.exceptions.RequestException:
            If a network-related error occurs during the API call.
        json.JSONDecodeError:
            If the API response is not valid JSON.
        Exception:
            For any unexpected error during data parsing or formatting.

    Example:
        >>> get_token_info('So11111111111111111111111111111111111111112')
        (
            \"📄 *Full Token Info*\\n🔘 *Symbol:* SOL\\n🏷️ *Name:* Solana\\n...\",
            \"https://vybe.network/storage/solana/logo.png\"
        )

    Notes:
        - If `updateTime` is provided in the API, it is converted to a readable UTC datetime string.
        - Output includes price history (current, 1-day ago, 7-days ago), category/subcategory,
          supply details, and volume information.
        - All numerical values are safely formatted with fallback defaults.
    """
    if not is_valid_mint(mint_address):
        return "❌ Invalid mint address! Only letters and digits are allowed."

    url = f"https://api.vybenetwork.xyz/token/{mint_address}"

    try:
        response = requests.get(url, headers=headers, timeout=250)
        if response.status_code == 404:
            return "❌ Token not found! Please check the mint address."
        response.raise_for_status()
        data = response.json()

        update_time = data.get("updateTime")
        update_str = datetime.utcfromtimestamp(update_time).strftime('%Y-%m-%d %H:%M:%S') if update_time else "N/A"

        output = [
            "📄 *Full Token Info*\n",
            f"🔘 *Symbol:* {data.get('symbol', 'N/A')}",
            f"🏷️ *Name:* {data.get('name', 'N/A')}",
            f"🔑 *Mint:* `{data.get('mintAddress', 'N/A')}`",

            "\n💵 *Price Info*",
            f"💰 *Current Price:* ${float(data.get('price', 0)):.4f}",
            f"📅 *1d Ago:* ${float(data.get('price1d', 0)):.4f}",
            f"🗓️ *7d Ago:* ${float(data.get('price7d', 0)):.4f}",

            "\n🔍 *Details*",
            f"🧬 *Decimals:* {data.get('decimal', 'N/A')}",
            f"✅ *Verified:* {data.get('verified', False)}",
            f"📂 *Category:* {data.get('category', 'N/A')}",
            f"📁 *Subcategory:* {data.get('subcategory') or '—'}",

            "\n⏱️ *Last Updated:*",
            f"{update_str}",

            "\n📦 *Supply & Market*",
            f"📦 *Supply:* {float(data.get('currentSupply', 0)):.4f}",
            f"💰 *Market Cap:* ${human_format(data.get('marketCap', 0))}",

            "\n📊 *24h Volume*",
            f"🔄 *Token:* {human_format(data.get('tokenAmountVolume24h', 0))}",
            f"💸 *USD:* ${human_format(data.get('usdValueVolume24h', 0))}"
        ]

        return "\n".join(output), data.get("logoUrl")

    except requests.exceptions.RequestException as e:
        return f"❌ Network error:\n{e}"
    except Exception as e:
        return f"⚠️ Unexpected error:\n{e}"

def get_token_ohlcv_data(mint_address: str, resolution: str, start_date: str, end_date: str) -> str:
    """
    Fetch and format OHLCV (Open, High, Low, Close, Volume) candlestick data for a given token over a date range.

    Queries Vybe Network API for OHLCV data at the specified resolution (e.g., 1m, 1h, 1d)
    between the provided start and end dates. Returns a formatted summary of the first 10 data points.

    Args:
        mint_address (str):
            The public mint address of the token (42–46 alphanumeric characters).
        resolution (str):
            The desired candle resolution (must be one of: '1m', '5m', '1h', '1d', etc.).
        start_date (str):
            Start date in 'YYYY-MM-DD' format.
        end_date (str):
            End date in 'YYYY-MM-DD' format (must be after start_date).

    Returns:
        str:
            - A formatted string summarizing OHLCV data.
            - An error message if validation fails, data is unavailable, or a request error occurs.

    Raises:
        requests.exceptions.RequestException:
            If a network-related error occurs during the API call.
        json.JSONDecodeError:
            If the API response is not valid JSON.
        Exception:
            For any unexpected error during data processing.

    Example:
        >>> get_token_ohlcv_data('So11111111111111111111111111111111111111112', '1d', '2025-01-01', '2025-01-10')
        📈 *Token OHLCV Data* (1d candles)
        🗓️ *Range:* 2025-01-01 → 2025-01-10
        🕒 *Time:* 2025-01-01 00:00:00
        🔓 Open: 95.23
        📈 High: 96.50
        📉 Low: 94.80
        🔒 Close: 95.90
        📦 Volume: 1234
        💵 Volume (USD): 117000
        🧾 Count: 430
        ────────────────────────────

    Notes:
        - Only the first 10 OHLCV entries are shown to avoid overly large messages.
        - If start or end date formats are invalid, meaningful error messages are returned.
    """

    valid_resolutions = ['1s', '1m', '3m', '5m', '15m', '30m', '1h', '2h', '3h', '4h', '1d', '1w', '1mo', '1y']

    if not is_valid_mint(mint_address):
        return "❌ Invalid mint address! Only letters and digits allowed."
    if resolution not in valid_resolutions:
        return "❌ Invalid resolution! Choose from: " + ", ".join(valid_resolutions)

    start_ts = to_unix_from_full_datetime(start_date)
    end_ts = to_unix_from_full_datetime(end_date)

    if not start_ts:
        return "❌ Invalid start date. Use format: YYYY-MM-DD"
    if not end_ts or end_ts <= start_ts:
        return "❌ End date must be after start date and correctly formatted."

    url = f"https://api.vybenetwork.xyz/price/{mint_address}/token-ohlcv?resolution={resolution}&timeStart={start_ts}&timeEnd={end_ts}"

    try:
        response = requests.get(url, headers=headers, timeout=250)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            return "⚠️ No OHLCV data found in the selected range."

        output = [
            f"📈 *Token OHLCV Data* ({resolution} candles)\n"
            f"🗓️ *Range:* {start_date} → {end_date}\n"
        ]

        for item in data[:10]:
            time_str = datetime.utcfromtimestamp(item["time"]).strftime('%Y-%m-%d %H:%M:%S')
            output.append(
                f"🕒 *Time:* {time_str}\n"
                f"🔓 Open: {item['open']}\n"
                f"📈 High: {item['high']}\n"
                f"📉 Low: {item['low']}\n"
                f"🔒 Close: {item['close']}\n"
                f"📦 Volume: {item['volume']}\n"
                f"💵 Volume (USD): {item['volumeUsd']}\n"
                f"🧾 Count: {item['count']}\n"
                f"────────────────────────────"
            )

        return "\n".join(output)

    except requests.exceptions.RequestException as e:
        return f"❌ Network error:\n{e}"
    except Exception as e:
        return f"⚠️ Unexpected error:\n{e}"

async def generate_and_send_chart(update: Update, context: ContextTypes.DEFAULT_TYPE, program_address: str, time_range: str):
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
        await update.message.reply_text("❌ Invalid program address format!")
        return

    if not is_valid_range(time_range):
        await update.message.reply_text("❌ Invalid range format! Use like: 1h, 1d, 7d")
        return

    program_name = get_program_name(program_address)
    if not program_name:
        await update.message.reply_text("🚫 Program not found or invalid.")
        return

    url = f"https://api.vybenetwork.xyz/program/{program_address}/active-users-ts?range={time_range}"

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

        lines = [
            f"📊 *Active Users Over `{time_range}`*",
            f"🧾 *Program:* {program_name}",
            "──────────────────────────────"
        ]
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
        await update.message.reply_text("⏱️ Timeout. Try again later.")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"❌ Network error:\n{e}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Unexpected error:\n{e}")
async def generate_and_send_tx_chart(update: Update, context: ContextTypes.DEFAULT_TYPE, program_address: str, range_value: str):
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
        await update.message.reply_text("❌ Invalid address format! Only alphanumeric characters allowed.")
        return

    if not is_valid_range(range_value):
        await update.message.reply_text("❌ Invalid range format! Use formats like '1h', '7d'.")
        return

    program_name = get_program_name(program_address)
    if not program_name:
        await update.message.reply_text("🚫 Program not found or unavailable.")
        return

    url = f"https://api.vybenetwork.xyz/program/{program_address}/transactions-count-ts?range={range_value}"

    try:
        response = requests.get(url, headers=headers, timeout=350)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            await update.message.reply_text("⚠️ No transaction data found for this range.")
            return

        timestamps = []
        tx_counts = []
        summary = [
            f"📊 *Transactions Over `{range_value}`*",
            f"🧾 *Program:* {program_name}",
            "──────────────────────────────"
        ]

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
                hourly_url = f"https://api.vybenetwork.xyz/program/{program_address}/transactions-count-ts?range=24h"
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
        await update.message.reply_text("⏱️ Timeout: Server took too long to respond.")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"❌ Network error:\n{e}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Unexpected error:\n{e}")

def get_daily_top_holders_chart(mint_address: str, start_date: str, end_date: str) -> tuple[str, str | None]:
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
        >>> get_daily_top_holders_chart('So11111111111111111111111111111111111111112', '2025-01-01', '2025-01-10')
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
        return "❌ Invalid mint address! Only alphanumeric characters are allowed.", None

    start_unix = to_unix_from_full_datetime(start_date)
    end_unix = to_unix_from_full_datetime(end_date)

    if start_unix is None or end_unix is None:
        return "❌ Invalid date format! Please use YYYY-MM-DD.", None

    url = f"https://api.vybenetwork.xyz/token/{mint_address}/holders-ts?startTime={start_unix}&endTime={end_unix}"

    try:
        response = requests.get(url, headers=headers, timeout=350)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            return "⚠️ No holder data found in the selected date range.", None

        time_labels = []
        holders = []
        lines = [
            f"📊 *Daily Holders Count*",
            f"🔑 *Mint:* `{mint_address}`",
            f"📆 *Range:* {start_date} → {end_date}",
            ""
        ]

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
            plt.bar(time_labels, holders, color='purple')
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
        return f"❌ Network error occurred:\n{e}", None
    except Exception as e:
        return f"⚠️ Unexpected error:\n{e}", None
def get_top_token_holders(mint_address: str, sort_criteria: str, sort_order: str, limit: int) -> str:
    """
    Fetch and format a ranked list of the top token holders for a given mint address.

    Retrieves the largest token holders from Vybe Network API, sorted based on user-specified criteria
    such as rank, balance, or value in USD. Returns a formatted summary suitable for Telegram messaging.

    Args:
        mint_address (str):
            The public mint address of the token (42–46 alphanumeric characters).
        sort_criteria (str):
            Field to sort by ('rank', 'ownerName', 'ownerAddress', 'valueUsd', 'balance', or 'percentageOfSupplyHeld').
        sort_order (str):
            Sort order, either 'asc' for ascending or 'desc' for descending.
        limit (int):
            Maximum number of top holders to retrieve (must be positive).

    Returns:
        str:
            A formatted text block listing top token holders, or an error message if validation fails,
            no data is found, or a network error occurs.

    Raises:
        requests.exceptions.RequestException:
            If a network-related error occurs during the API call.
        json.JSONDecodeError:
            If the API response cannot be parsed as valid JSON.
        Exception:
            For any unexpected error during processing or formatting.

    Example:
        >>> get_top_token_holders('So11111111111111111111111111111111111111112', 'balance', 'desc', 5)
        📋 *Top 5 Token Holders* (Sorted by *balance*, `DESC`):
        🏅 *Rank:* 1
        👤 *Owner:* whales1 (`9xjT3kghPz...`)
        📦 *Balance:* 12,500
        💵 *Value (USD):* $450,000.00
        📈 *Supply Held:* 8.45%
        🔘 *Token Symbol:* SOL

    Notes:
        - Valid sort criteria: rank, ownerName, ownerAddress, valueUsd, balance, percentageOfSupplyHeld.
        - Valid sort orders: 'asc' (ascending) or 'desc' (descending).
        - Sorting and limit are validated before making the API request.
        - If no holders are found, a warning message is returned.
    """

    valid_criteria = ['rank', 'ownerName', 'ownerAddress', 'valueUsd', 'balance', 'percentageOfSupplyHeld']
    valid_order = ['asc', 'desc']

    if not is_valid_mint(mint_address):
        return "❌ Invalid mint address! Only alphanumeric characters are allowed."

    if sort_criteria not in valid_criteria:
        return "❌ Invalid sort criteria! Choose from: rank, ownerName, ownerAddress, valueUsd, balance, percentageOfSupplyHeld."

    if sort_order.lower() not in valid_order:
        return "❌ Invalid sort order! Must be 'asc' or 'desc'."

    if limit <= 0:
        return "❌ Limit must be a positive number."

    url = (
        f"https://api.vybenetwork.xyz/token/{mint_address}/top-holders"
        f"?limit={limit}&sortBy={sort_criteria}&sortDirection={sort_order.capitalize()}"
    )

    try:
        response = requests.get(url, headers=headers, timeout=250)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            return "⚠️ No holders data found for this token."

        output = [f"📋 *Top {limit} Token Holders* (Sorted by *{sort_criteria}*, `{sort_order.upper()}`):"]
        for holder in data:
            output.append(
                f"\n🏅 *Rank:* {holder.get('rank')}\n"
                f"👤 *Owner:* {holder.get('ownerName', 'N/A')} (`{holder.get('ownerAddress')}`)\n"
                f"📦 *Balance:* {holder.get('balance')}\n"
                f"💵 *Value (USD):* ${float(holder.get('valueUsd', 0)):.2f}\n"
                f"📈 *Supply Held:* {holder.get('percentageOfSupplyHeld', 0) * 100:.2f}%\n"
                f"🔘 *Token Symbol:* {holder.get('tokenSymbol', 'N/A')}"
            )

        return "\n".join(output)

    except requests.exceptions.RequestException as e:
        return f"❌ Network error occurred:\n{e}"
    except json.JSONDecodeError:
        return "❌ Failed to parse response JSON."
    except Exception as e:
        return f"⚠️ Unexpected error:\n{e}"

def get_transfer_volume_chart(mint_address: str, start_date: str, end_date: str, interval: str):
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
        >>> get_transfer_volume_chart('So11111111111111111111111111111111111111112', '2025-01-01', '2025-01-10', 'day')
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
        return "❌ Invalid mint address! Only alphanumeric characters are allowed.", None

    start_timestamp = to_unix_from_full_datetime(start_date)
    end_timestamp = to_unix_from_full_datetime(end_date)

    if not start_timestamp or not end_timestamp or end_timestamp <= start_timestamp:
        return "❌ Invalid date range. Ensure correct format (YYYY-MM-DD) and that end date is after start date.", None

    if interval.lower() not in ['hour', 'day']:
        return "❌ Invalid interval! Please enter 'hour' or 'day'.", None

    url = (
        f"https://api.vybenetwork.xyz/token/{mint_address}/transfer-volume"
        f"?startTime={start_timestamp}&endTime={end_timestamp}&interval={interval}"
    )

    try:
        response = requests.get(url, headers=headers, timeout=350)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            return "⚠️ No transfer volume data found for this range.", None

        time_stamps = [convert_to_date(item["timeBucketStart"]) for item in data]
        volumes = [float(item.get("volume", 0)) for item in data]

        df = pd.DataFrame({'Date': time_stamps, 'Volume': volumes})

        summary_lines = [
            f"📋 *Transfer Volume Data* ({interval})",
            f"🪙 *Mint:* {mint_address}",
            f"📆 *Range:* {start_date} ➡ {end_date}",
            "────────────────────────────"
        ]

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
        return f"❌ Network error occurred:\n{e}", None
    except Exception as e:
        return f"⚠️ Unexpected error:\n{e}", None

def get_program_info(address: str) -> str | None:
    """
    Retrieve the friendly or entity name of a program given its address.

    Queries the Vybe Network API to fetch program metadata.
    Returns the program's friendly name if available, otherwise falls back
    to the entity name or returns the address itself. Returns None if an error occurs.

    Args:
        address (str):
            The public program address (42–46 alphanumeric characters).

    Returns:
        Union[str, None]:
            - The friendly name, entity name, or the address itself if available.
            - None if the request fails or if an unexpected error occurs.

    Raises:
        requests.exceptions.RequestException:
            If a network-related error occurs during the API call.
        Exception:
            For any unexpected errors during API communication.

    Example:
        >>> get_program_info('9xjT3kghPz...')
        'Orca'

    Notes:
        - If the program metadata contains a 'friendlyName', it will be prioritized.
        - If not, 'entityName' is used.
        - If neither exists, the address itself is returned as fallback.
        - Safe to call even if the program does not exist (returns None on error).
    """

    try:
        res = requests.get(
            f"https://api.vybenetwork.xyz/program/{address}",
            headers=headers,
            timeout=250
        )
        if res.ok:
            data = res.json()
            return data.get("friendlyName") or data.get("entityName") or address
    except Exception:
        return None
def fetch_tvl_data(address: str, resolution: str) -> list:
    """
    Fetch Total Value Locked (TVL) time-series data for a given program address.

    Queries the Vybe Network API to retrieve historical TVL measurements
    based on the specified resolution (e.g., hourly, daily).
    Returns a list of TVL data points, or an empty list if the request fails.

    Args:
        address (str):
            The public address of the program (42–46 alphanumeric characters).
        resolution (str):
            Time resolution for the data points (e.g., '1h', '1d', '7d').

    Returns:
        list:
            A list of TVL data points (each item typically contains timestamp and TVL values),
            or an empty list if an error occurs during the request.

    Raises:
        requests.exceptions.RequestException:
            If a network-related error occurs during the API call.
        json.JSONDecodeError:
            If the API response is not valid JSON.
        Exception:
            For any unexpected errors during data parsing.

    Example:
        >>> fetch_tvl_data('9xjT3kghPz...', '1d')
        [{'blockTime': 1740307200, 'tvlUsd': 350000.0}, ...]

    Notes:
        - If the program is invalid or there is no available data, the function returns an empty list.
        - Resolution must match supported intervals by Vybe Network ('1h', '1d', etc.).
    """
    try:
        res = requests.get(
            f"https://api.vybenetwork.xyz/program/{address}/tvl?resolution={resolution}",
            headers=headers,
            timeout=250
        )
        res.raise_for_status()
        return res.json().get("data", [])
    except Exception:
        return []


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
        await update.message.reply_text("❌ Invalid program address.")
        return

    if not is_valid_resolution(resolution):
        await update.message.reply_text("❌ Invalid resolution. Use values like `1h`, `1d`, `1w`, etc.")
        return

    program_name = get_program_info(program_address)
    if not program_name:
        await update.message.reply_text("🚫 Program not found or inaccessible.")
        return

    data = fetch_tvl_data(program_address, resolution)
    if not data:
        await update.message.reply_text("⚠️ No TVL data found for this program.")
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
            await update.message.reply_photo(photo=InputFile(photo), caption=f"📈 TVL Chart | {program_name}", parse_mode="Markdown")

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error while generating or sending chart:\n{e}")
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
        await update.message.reply_text("❌ Invalid wallet address format.")
        return

    url = f"https://api.vybenetwork.xyz/account/token-balance-ts/{wallet_address}?days={days}"

    try:
        response = requests.get(url, headers=headers, timeout=350)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            await update.message.reply_text("⚠️ No token balance data found for this wallet.")
            return

        dates, values, lines = [], [], [
            f"📊 *Token Balance History* (`{days}d`)",
            f"👛 *Wallet:* `{wallet_address}`",
            "────────────────────────────"
        ]

        for item in data:
            readable = datetime.utcfromtimestamp(item["blockTime"]).strftime('%Y-%m-%d')
            token_val = float(item.get("tokenValue", 0))
            stake_val = float(item.get("stakeValue", 0))
            sys_val = float(item.get("systemValue", 0))
            stake_sol = float(item.get("stakeValueSol", 0))

            lines.extend([
                f"📅 {readable}",
                f"💰 Token Value: ${token_val:,.2f}",
                f"🔒 Stake Value: ${stake_val:,.2f}",
                f"🛠️ System Value: ${sys_val:,.2f}",
                f"🧊 Stake (SOL): {stake_sol:.2f}",
                "────────────────────────────"
            ])
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
        await update.message.reply_text(f"❌ Network error:\n{e}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Unexpected error:\n{e}")