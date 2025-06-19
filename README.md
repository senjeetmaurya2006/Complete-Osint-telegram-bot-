
# Telegram OSINT Bot 🔍

A powerful Telegram bot that can perform:

- 📞 Phone number lookup (NumVerify + MongoDB leak data)
- 🌐 IP address lookup (IP-API)
- 📧 Email domain info (DNS/IP resolution)
- 🔍 Google Dorking for numbers
- 🧾 Whois lookup for domains

## 🧠 Features

- Inline keyboard buttons for easy use
- Integrated with MongoDB for leaked data
- External APIs: NumVerify, IP-API, WHOIS

## 🔧 Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/osint-telegram-bot.git
   cd osint-telegram-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Edit `main.py` to replace:
   - `TOKEN` with your actual Telegram Bot token
   - `MONGO_URI` with your MongoDB URI
   - `NUMVERIFY_API` with your NumVerify API key

4. Run the bot:
   ```bash
   python main.py
   ```
