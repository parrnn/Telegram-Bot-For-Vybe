import requests
import json
from typing import Union, Tuple
import re
import constants.messages as messages
import globals.preferences as preferences
import functions.evaluates as evaluates
import functions.converts as converts
import functions.datetime as datetime
import globals.urls as urls

emoji_numbers = {
            1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣",
            6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"
        }

def retrieve_nft_collection_owners(collection_address: str) -> Union[str, list]:
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
        >>> retrieve_nft_collection_owners('8fj3h5u...')
        📦 *Top Owners of:* 8fj3h5...4hf9
        1️⃣
        👤 *Owner:* 5B28C3...4Fd9
        🎁 *NFTs:* 12
        ...
    """
    if not re.fullmatch(r"[a-zA-Z0-9]+", collection_address):
        return messages.INVALID_COLLECTION_ADDRESS
    url = str.format(urls.COLLECTION_URL, collection_address)

    try:
        response = requests.get(url, headers=preferences.headers, timeout=250)

        if response.status_code == 403:
            return messages.STATUS_CODE_403
        elif response.status_code == 404:
            return messages.STATUS_CODE_404

        response.raise_for_status()
        data = response.json()

        owners = data.get("data", [])
        if not owners:
            return messages.NO_OWNERS_FOUND

        top_owners = owners[:10]



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
        return (str.format(messages.NETWORK_ERROR,e))
    except ValueError:
        return messages.VALUE_ERROR
    except Exception as e:
        return (str.format(messages.NETWORK_ERROR,e))

def retrieve_program_details(program_address: str) -> Tuple[str, str]:
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

    Example:
        >>> retrieve_program_details('9AefkXv83z...')
        (
            "📌 *Program Overview*\n\n🏛️ *Entity:* Orca\n📛 *Name:* Orca\n...",
            "https://storage.googleapis.com/.../orca_logo.png"
        )
    """
    if not evaluates.is_valid_address(program_address):
        return messages.INVALID_ADDRESS

    url = str.format(urls.PROGRAM_DETAILS_URL, program_address)

    try:
        response = requests.get(url, headers=preferences.headers, timeout=250)

        if response.status_code == 400:
            return messages.INACCESSIBLE_PROGRAM_ADDRESS
        elif response.status_code == 403:
            return messages.INACCESSIBLE_PROGRAM_ADDRESS
        elif response.status_code == 404:
            return messages.INACCESSIBLE_PROGRAM_ADDRESS

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

        dau_formatted = f"{dau:,}" if isinstance(dau, int) else dau
        new_users_formatted = f"{new_users:,}" if isinstance(new_users, int) else new_users
        txns_formatted = f"{txns:,}" if isinstance(txns, int) else txns

        formatted_message = f"📌 *Program Overview*\n\n" \
                            f"🏛️ *Entity:* {entity_name}\n" \
                            f"📛 *Name:* {friendly_name}\n" \
                            f"🏷️ *Labels:* {labels_text}\n\n" \
                            f"📊 *Stats (24h)*\n" \
                            f"👥 Active Users: {dau_formatted}\n" \
                            f"🆕 New Users: {new_users_formatted}\n" \
                            f"🔁 Transactions: {txns_formatted}\n\n" \
                            f"📖 *Description:*\n{description or 'N/A'}"

        return formatted_message, logo_url

    except requests.exceptions.RequestException as e:
        return messages.SOMETHING_WENT_WRONG
    except json.JSONDecodeError as e:
        return messages.JSON_ERROR
    except Exception as e:
        return messages.SOMETHING_WENT_WRONG
def retrieve_program_name(program_address: str) -> Union[str, None]:
    """
    Retrieve the display name of a program from Vybe Network API.

    Attempts to fetch a friendly name, fallback name, or entity name
    associated with a given program address. Returns the address itself
    if no name is found but the program is accessible.

    Args:
        program_address (str):
            The public address of the program to query (typically 32–44 characters).

    Returns:
        Union[str, None]:
            - The program's friendly name, name, entity name, or the address itself.
            - None if the program is invalid, inaccessible (status 400, 403, 404), or if an error occurs.

    Raises:
        requests.exceptions.RequestException:
            If there is a network error during the API call.
        json.JSONDecodeError:
            If the response is not valid JSON.
        Exception:
            For any unexpected errors during fetching or parsing.

    Example:
        >>> retrieve_program_name('9AefkXv83z...')
        'Orca'
    """

    url = str.format(urls.PROGRAM_DETAILS_URL, program_address)

    try:
        response = requests.get(url, headers=preferences.headers, timeout=250)
        if response.status_code in [400, 403, 404]:
            return None
        response.raise_for_status()
        info = response.json()

        name = (
            info.get("friendlyName")
            or info.get("name")
            or info.get("entityName")
        )

        return name if name else program_address

    except Exception:
        return None


def retrieve_top_active_wallets(program_address: str, days: int = 1, limit: int = 10) -> str:
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
        >>> retrieve_top_active_wallets('9AefkXv83z...', days=7, limit=5)
        📊 *Top 5 Active Wallets*
        🧾 *Program:* Orca
        📆 *Last 7 Days*
        1️⃣ 6T25g2...deF9 — 🔁 *1,203*
        2️⃣ D5gP12...A0F8 — 🔁 *1,045*
        ...
    """

    if not evaluates.is_valid_address(program_address):
        return messages.INVALID_FORMAT

    if not evaluates.is_valid_days(str(days)):
        return messages.INVALID_TIMESPAN_1D_30D

    if not evaluates.is_valid_limit(str(limit)):
        return messages.INVALID_LIMIT

    program_name = retrieve_program_name(program_address)
    if not program_name:
        return messages.PROGRAM_NOT_FOUND

    url = str.format( urls.TOP_ACTIVE_WALLETS_URL, program_address,days,limit)

    try:
        response = requests.get(url, headers=preferences.headers, timeout=250)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            return messages.NO_DATA_FOUND

        output_lines = [str.format(messages.TOP_ACTIVE_WALLETS_TEMPLATE,limit, program_name, days)]

        for i, user in enumerate(data, 1):
            emoji = emoji_numbers.get(i, f"*{i}.*")
            wallet = user.get("wallet", "N/A")
            txs = f"{user.get('transactions', 0):,}"
            short_wallet = f"{wallet[:6]}...{wallet[-4:]}"
            output_lines.append(f"{emoji} {short_wallet} — 🔁 *{txs}*")

        return "\n".join(output_lines)


    except requests.exceptions.RequestException as e:
        return (str.format(messages.NETWORK_ERROR,e))
    except Exception as e:
        return (str.format(messages.UNEXPECTED_ERROR,e))


def retrieve_nft_portfolio(wallet_address: str) -> str:
    """
    Fetch and format the NFT portfolio of a given wallet from Vybe Network API.

    Retrieves overall wallet stats such as total SOL and USD value,
    along with a breakdown of NFT collections held, their item counts,
    and valuation in SOL and USD.

    Args:
        wallet_address (str): The public address of the wallet.

    Returns:
        str: A formatted string summarizing the wallet's NFT portfolio.

    Raises:
        requests.exceptions.RequestException: If a network error occurs.
        json.JSONDecodeError: If the API response is not valid JSON.
        Exception: For any unexpected error during data processing.
    """
    if not evaluates.is_valid_address(wallet_address):
        return "❌ Invalid wallet address! Only alphanumeric characters allowed."

    url = str.format(urls.NFT_PORTFOLIO_URL, wallet_address)

    try:
        response = requests.get(url, headers=preferences.headers, timeout=20)

        if response.status_code == 404:
            return "🚫 Wallet not found or has no NFT data."

        response.raise_for_status()
        data = response.json()

        output_lines = [str.format(messages.NFT_PORTFOLIO_TEMPLATE,
            data.get('ownerAddress', 'N/A'),
            converts.to_float_safe(data.get('totalSol')),
            converts.to_float_safe(data.get('totalUsd')),
            data.get('totalNftCollectionCount', 0)
        )]

        collections = data.get("data", [])
        if not collections:
            output_lines.append("\n⚠️ No NFT collections found.")
        else:
            output_lines.append("\n🧾 *Collections:*")
            for nft in collections:
                name = nft.get("name", "N/A")
                collection = nft.get("collectionAddress", "N/A")
                items = nft.get("totalItems", 0)
                val_sol = converts.to_float_safe(nft.get("valueSol"))
                val_usd = converts.to_float_safe(nft.get("valueUsd"))
                price_sol = converts.to_float_safe(nft.get("priceSol"))
                price_usd = converts.to_float_safe(nft.get("priceUsd"))

                output_lines.append(
                    str.format(messages.NFT_PORTFOLIO_COLLECTION_MESSAGE,
                        name,
                        collection,
                        items,
                        val_sol,
                        val_usd,
                        price_sol,
                        price_usd
                    )
                )

        return "\n".join(output_lines)

    except requests.exceptions.RequestException as e:
        return str.format(messages.NETWORK_ERROR,e)
    except json.JSONDecodeError:
        return messages.JSON_ERROR
    except Exception as e:
        return str.format(messages.UNEXPECTED_ERROR,e)

def retrieve_wallet_pnl_summary(wallet_address: str, days: int) -> list[str] | str:
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
        >>> retrieve_wallet_pnl_summary('9xjT3kghPz...', days=7)
        [
            \"💥 *PnL Summary (7d)*\\n👛 Wallet: `9xjT3kghPz...`\\n💵 *Realized PnL:* $1234.56\\n...\",
            \"🪙 *SOL*\\n💰 Realized: $500.00\\n...\\n\"
        ]

    Notes:
        - If multiple tokens are involved, token metrics are appended after the PnL summary.
        - The function automatically splits long outputs into multiple chunks.
    """

    if not evaluates.is_valid_address(wallet_address):
        return messages.INVALID_WALLET_FORMAT

    url = str.format(urls.WALLET_PNL_URL, wallet_address,days)

    try:
        response = requests.get(url, headers=preferences.headers, timeout=1250)
        if response.status_code == 404:
            return messages.WALLET_NOT_FOUND

        response.raise_for_status()
        data = response.json()

        summary = data.get("summary", {})
        output = [
            str.format(messages.PNL_SUMMARY_HEADER,days),
            str.format(messages.PNL_SUMMARY_TEMPLATE,
                wallet_address,
                float(summary.get('realizedPnlUsd', 0)),
                float(summary.get('unrealizedPnlUsd', 0)),
                float(summary.get('tradesVolumeUsd', 0)),
                summary.get('tradesCount', 0),
                float(summary.get('averageTradeUsd', 0)),
                float(summary.get('winRate', 0)) * 100
            )
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

                output.append(
                    str.format(messages.PNL_TOKEN_ENTRY,
                        symbol,
                        realized,
                        unrealized,
                        float(buys.get("volumeUsd", 0)),
                        buys.get("transactionCount", 0),
                        float(sells.get("volumeUsd", 0)),
                        sells.get("transactionCount", 0),
                    )
                )

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
        return (str.format(messages.NETWORK_ERROR,e))
    except Exception as e:
        return (str.format(messages.UNEXPECTED_ERROR,e))


def retrieve_wallet_portfolio_summary(wallet_address: str) -> str:
    if not evaluates.is_valid_address(wallet_address):
        return messages.INVALID_WALLET_ADDRESS

    def fetch_json(url: str) -> dict | None:
        try:
            response = requests.get(url, headers=preferences.headers, timeout=20)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            return None

    check_url = str.format(urls.WALLET_PNL_URL, wallet_address, 1)
    token_url = str.format(urls.WALLET_TOKEN_BALANCE_URL, wallet_address)
    nft_url   = str.format(urls.NFT_PORTFOLIO_URL, wallet_address)

    check_data = fetch_json(check_url)
    if not check_data or (not check_data.get("summary") and not check_data.get("tokenMetrics")):
        return messages.WALLET_NOT_FOUND_FOR_PORTFOLIO

    token_data = fetch_json(token_url)
    nft_data   = fetch_json(nft_url)

    token_usd = float(token_data.get("totalTokenValueUsd", 0)) if isinstance(token_data, dict) else 0.0
    nft_usd= float(nft_data.get("totalUsd", 0)) if isinstance(nft_data, dict) else 0.0
    total= token_usd + nft_usd

    return str.format(messages.PORTFOLIO_SUMMARY_MESSAGE, wallet_address, token_usd, nft_usd, total)

def retrieve_wallet_token_summary(wallet_address: str) -> str | list[str]:
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
        >>> retrieve_wallet_token_summary('9xjT3kghPz...')
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

    if not evaluates.is_valid_address(wallet_address):
        return messages.INVALID_WALLET_ADDRESS
    url = str.format(urls.WALLET_TOKEN_BALANCE_URL, wallet_address)

    try:
        response = requests.get(url, headers=preferences.headers, timeout=250)
        if response.status_code == 404:
            return messages.ERROR_NO_WALLET_TOKEN_DATA
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return (str.format(messages.NETWORK_ERROR,e))
    except json.JSONDecodeError:
        return messages.JSON_ERROR

    if not data.get("data"):
        return messages.WARN_NO_TOKEN_BALANCES

    output = []
    output.append(
        str.format(messages.WALLET_TOKEN_SUMMARY,
            data.get('ownerAddress', 'N/A'),
            to_float_safe(data.get('totalTokenValueUsd')),
            to_float_safe(data.get('stakedSolBalanceUsd')),
            to_int_safe(data.get('totalTokenCount')),
        )
    )

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
            str.format(messages.TOKEN_DETAIL_TEMPLATE,
                emoji=emoji,
                symbol=symbol,
                name=name,
                mint=mint,
                price_change=price_change,
                value_change=value_change,
                amount=amount,
                value_usd=value_usd,
                verified=verified
            )
        )

    result = "\n".join(output)

    # Telegram messages have a length limit (approx 4096 chars)
    if len(result) <= 4000:
        return result

    # Split into chunks if too long
    chunks = []
    while len(result) > 4000:
        split_at = result.rfind("\n", 0, 4000)
        if split_at == -1:
            split_at = 4000
        chunks.append(result[:split_at])
        result = result[split_at:].lstrip()
    chunks.append(result)
    return chunks
def retrieve_token_info(mint_address: str) -> tuple[str, str] | str:
    """
    Fetch and format detailed information about a token given its mint address.

    Retrieves pricing, supply, category, verification status, market cap, and 24h volume
    from Vybe Network API. Returns the full formatted info as a string along with the logo URL.

    Args:
        mint_address (str):
            The public mint address of the token.

    Returns:
        Union[Tuple[str, str], str]:
            - A tuple (formatted info string, logo URL string) if successful.
            - A string error message if the token is invalid or an error occurs.

    Example:
        >>> retrieve_token_info('So11111111111111111111111111111111111111112')
    """
    if not evaluates.is_valid_mint(mint_address):
        return messages.INVALID_MINT_ADDRESS

    url = str.format(urls.TOKEN_INFO_URL, mint_address)

    try:
        response = requests.get(url, headers=preferences.headers, timeout=20)

        if response.status_code == 404:
            return messages.TOKEN_NOT_FOUND

        response.raise_for_status()
        data = response.json()

        update_time = data.get("updatetime")
        update_str = datetime.datetime.utcfromtimestamp(update_time).strftime('%Y-%m-%d %H:%M:%S') if update_time else "N/A"

        final_message = str.format(messages.TOKEN_INFO_TEMPLATE,
            symbol=data.get('symbol', 'N/A'),
            name=data.get('name', 'N/A'),
            mint=data.get('mintAddress', 'N/A'),
            price=float(data.get('price', 0)),
            price_1d=float(data.get('price1d', 0)),
            price_7d=float(data.get('price7d', 0)),
            decimals=data.get('decimal', 'N/A'),
            verified='✅' if data.get('verified', False) else '❌',
            category=data.get('category', 'N/A'),
            subcategory=data.get('subcategory') or '—',
            last_updated=update_str,
            supply=float(data.get('currentSupply', 0)),
            market_cap=datetime.format_number_human_readable(data.get('marketCap', 0)),
            volume_token=datetime.format_number_human_readable(data.get('tokenAmountVolume24h', 0)),
            volume_usd=datetime.format_number_human_readable(data.get('usdValueVolume24h', 0))
        )

        return final_message, data.get("logoUrl")

    except requests.exceptions.RequestException as e:
        return (str.format(messages.NETWORK_ERROR,e))
    except Exception as e:
        return (str.format(messages.UNEXPECTED_ERROR,e))


def retrieve_token_ohlcv_data(mint_address: str, resolution: str, start_date: str, end_date: str) -> str:
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
        >>> retrieve_token_ohlcv_data('So11111111111111111111111111111111111111112', '1d', '2025-01-01', '2025-01-10')
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

    if not evaluates.is_valid_mint(mint_address):
        return messages.INVALID_MINT_ADDRESS
    if resolution not in valid_resolutions:
        return "❌ Invalid resolution! Choose from: " + ", ".join(valid_resolutions)

    start_ts = datetime.full_datetime_to_unix(start_date)
    end_ts = datetime.full_datetime_to_unix(end_date)

    if not start_ts:
        return messages.INVALID_START_DATE
    if not end_ts or end_ts <= start_ts:
        return messages.INVALID_END_DATE

    url = str.format(urls.TOKEN_OHLCV_URL, mint_address,resolution,start_ts,end_ts)

    try:
        response = requests.get(url, headers=preferences.headers, timeout=250)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            return messages.NO_OHLCV_FOUND

        output = [
            str.format(messages.TOKEN_OHLCV_HEADER,resolution, start_date, end_date)
        ]

        for item in data[:10]:
            time_str = datetime.datetime.utcfromtimestamp(item["time"]).strftime('%Y-%m-%d %H:%M:%S')
            output.append(
                str.format(messages.TOKEN_OHLCV_ITEM,
                    time_str,
                    item['open'],
                    item['high'],
                    item['low'],
                    item['close'],
                    item['volume'],
                    item['volumeUsd'],
                    item['count']
                )
            )

        return "\n".join(output)

    except requests.exceptions.RequestException as e:
        return (str.format(messages.NETWORK_ERROR,e))
    except Exception as e:
        return (str.format(messages.UNEXPECTED_ERROR,e))

def retrieve_top_token_holders(mint_address: str, sort_criteria: str, sort_order: str, limit: int) -> str:
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
        >>> retrieve_top_token_holders('So11111111111111111111111111111111111111112', 'balance', 'desc', 5)
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

    if not evaluates.is_valid_mint(mint_address):
        return messages.INVALID_MINT_ADDRESS

    if sort_criteria not in valid_criteria:
        return messages.INVALID_SORT_CRITERIA

    if sort_order.lower() not in valid_order:
        return messages.INVALID_SORT_ORDER

    if limit <= 0:
        return messages.INVALID_LIMIT
    url = str.format(urls.TOP_TOKEN_HOLDERS_URL, mint_address,limit,sort_criteria,sort_order.capitalize())

    try:
        response = requests.get(url, headers=preferences.headers, timeout=250)
        response.raise_for_status()
        data = response.json().get("data", [])

        if not data:
            return "⚠️ No holders data found for this token."

        output = [f"📋 *Top {limit} Token Holders* (Sorted by *{sort_criteria}*, `{sort_order.upper()}`):"]
        for holder in data:
            output.append(
                str.format(messages.TOKEN_HOLDER_DETAIL,
                    rank=holder.get('rank'),
                    owner_name=holder.get('ownerName', 'N/A'),
                    owner_address=holder.get('ownerAddress'),
                    balance=holder.get('balance'),
                    value_usd=float(holder.get('valueUsd', 0)),
                    supply_held=holder.get('percentageOfSupplyHeld', 0) * 100,
                    symbol=holder.get('tokenSymbol', 'N/A')
                )
            )

        return "\n".join(output)

    except requests.exceptions.RequestException as e:
        return (str.format(messages.NETWORK_ERROR,e))
    except json.JSONDecodeError:
        return messages.JSON_ERROR
    except Exception as e:
        return (str.format(messages.UNEXPECTED_ERROR,e))

def retrieve_program_info(address: str) -> str | None:
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
        >>> retrieve_program_info('9xjT3kghPz...')
        'Orca'

    Notes:
        - If the program metadata contains a 'friendlyName', it will be prioritized.
        - If not, 'entityName' is used.
        - If neither exists, the address itself is returned as fallback.
        - Safe to call even if the program does not exist (returns None on error).
    """
    url = str.format(urls.PROGRAM_DETAILS_URL,address)
    try:
        res = requests.get(
            url,
            headers=preferences.headers,
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
    url = str.format(urls.PROGRAM_TVL, address, resolution)

    try:
        res = requests.get(
            url,
            headers=preferences.headers,
            timeout=250
        )
        res.raise_for_status()
        return res.json().get("data", [])
    except Exception:
        return []