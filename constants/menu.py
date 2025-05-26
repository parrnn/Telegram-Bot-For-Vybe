from telegram import ReplyKeyboardMarkup, KeyboardButton

main_menu_buttons = [
    [KeyboardButton("🎨 NFT"), KeyboardButton("📦 Programs")],
    [KeyboardButton("📊 Token Analysis"), KeyboardButton("🧾 Wallet Tracking")],
    [KeyboardButton("🅰️ Alpha Vybe"), KeyboardButton("❓ Help")]
]

nft_menu = [
    [KeyboardButton("👑 NFT Collection Owners")],
    [KeyboardButton("🔙 Back"), KeyboardButton("🏠 Main menu")]
]

programs_menu = [
    [KeyboardButton("📄 Details"), KeyboardButton("💰 Top Wallets")],
    [KeyboardButton("🔁 Transactions"), KeyboardButton("👥 Active Users")],
    [KeyboardButton("📈 TVL")],
    [KeyboardButton("🔙 Back"), KeyboardButton("🏠 Main menu")]
]

token_menu = [
    [KeyboardButton("👤 Holders"), KeyboardButton("📋 Info")],
    [KeyboardButton("💼 Balances"), KeyboardButton("🕰 OHLCV")],
    [KeyboardButton("📊 Volume")],
    [KeyboardButton("🔙 Back"), KeyboardButton("🏠 Main menu")]
]

holders_submenu = [
    [KeyboardButton("📅 Daily Top Holders")],
    [KeyboardButton("🏆 Top Token Holders")],
    [KeyboardButton("🔙 Back"), KeyboardButton("🏠 Main menu")]
]

wallet_menu = [
    [KeyboardButton("💥 NFT"), KeyboardButton("📈 PnL")],
    [KeyboardButton("💼 Portfolio"), KeyboardButton("🪙 SPL")],
    [KeyboardButton("🔙 Back"), KeyboardButton("🏠 Main menu")]
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

