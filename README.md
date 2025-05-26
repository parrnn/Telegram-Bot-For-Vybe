# VybeBot – On-Chain Analytics Telegram Bot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version" />
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT" />
  <img src="https://img.shields.io/badge/Powered%20By-Vybe%20Network-purple.svg" alt="Vybe Network" />
</p>

VybeBot is a feature-rich Telegram bot that delivers real-time on-chain analytics for NFTs, programs, tokens, and wallet activity using the [Vybe Network API](https://docs.vybenetwork.com).  
Perfect for data analysts, crypto researchers, and DeFi enthusiasts.

---

## 🚀 Features

- Detailed analytics for NFTs, Programs, Tokens, Wallets
- Real-time OHLCV, TVL, Transfer Volume charts
- Top wallet/token holders tracking
- Portfolio summary and PnL reporting
- Chart generation and Telegram delivery

---
- [Features](#-features)
- [Quick Overview](#quick-overview)
- [Setup Instructions](#-setup-instructions)
- [Usage Examples](#-usage-examples)
- [Project Structure](#-project-structure)
- [Demo](#-demo-coming-soon)
- [License](#-license)
- [Contact](#-contact)
## Quick Overview
| Category | Metrics Available |
|:---------|:------------------|
| NFTs     | Portfolio, Collection Owners |
| Programs | Details, Top Wallets, TVL, Active Users, Tx Count |
| Tokens   | Info, OHLCV, Holders, Transfer Volume, Balances |
| Wallets  | SPL, Portfolio, PnL |

## 🧰 Setup Instructions

1. **Clone the Repo**
   ```bash
   git clone https://github.com/parrnn/Telegram-Bot-For-Vybe.git
   cd Telegram-Bot-For-Vybe
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Bot**
 
- Open `main.py` and insert your Telegram Bot Token:

```python
bot_token = "YOUR_BOT_TOKEN_HERE"
```

- Open `globals`/`preferences.py` and insert your Vybe API Key inside the `headers` dictionary.


```python
headers = {
      "accept": "application/json",
      "X-API-KEY": "YOUR_API_KEY"
  }
```

4. **Run the Bot**
   ```bash
   python main.py
   ```

---

## 📖 Usage Examples

**Example 1: Getting the Details of a Specific Program**
- Type `/start`
- Choose `📦 Programs`
- Select `📄 Details`
- Enter the program ID when prompted
- Receive the full program overview and details directly in Telegram

**Example 2: Viewing a Wallet's NFT Portfolio**
- Press `/start` to launch the bot (if you haven't already).
- Choose `🧾 Wallet Tracking`.
- Select `💥 NFT`.
- Enter the wallet address when prompted.
- Instantly receive a full breakdown of the wallet's NFT portfolio and collection details!


---

## 📂 Project Structure

```
vybebot/
├── main.py                  # Main entry point for the Telegram bot (message routing)
├── handlers.py              # Awaiting handlers and user input flows
├── functions/               # Core logic split into functional modules
│   ├── charts.py            # Chart generation (TVL, Txs, OHLCV, etc.)
│   ├── converts.py          # Safe type conversion helpers (e.g. to_float_safe)
│   ├── datetime.py          # Unix timestamp to readable time conversions
│   ├── evaluates.py         # Input validation (address format, limits, dates)
│   └── functions.py         # API calls and data-fetching functions
├── constants/               # Reusable constants and layouts
│   ├── menu.py              # ReplyKeyboard layout for menus and submenus
│   └── messages.py          # Reusable message templates and error strings
├── globals/
│   ├── preferences.py       # API headers (Vybe API key, request config)
│   └── urls.py              # Vybe API endpoint templates
├── tutorial/
│   └── vybe.gif             # GIF demo of the bot in action
├── requirements.txt         # Python dependency list
├── LICENSE                  # Project license
└── README.md                # Documentation and usage instructions

```

---

## 📸 Demo

Here’s a quick demo of VybeBot in action! 🚀

<p align="center">
  <img src="https://github.com/parrnn/Telegram-Bot-For-Vybe/blob/main/Tutorial/VYBE.gif?raw=true" alt="VybeBot Demo" width="250"/>
</p>
---

## 🛡 License

This project is licensed under the **MIT License**.

---

## 📬 Contact

- [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/parrnn)
- [![Twitter](https://img.shields.io/badge/-Twitter-1DA1F2?logo=twitter&logoColor=white)](https://twitter.com/par_rnn)

---
