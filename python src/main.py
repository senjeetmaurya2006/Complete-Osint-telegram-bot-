# === main.py ===

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
from pymongo import MongoClient
import requests
import socket
from datetime import datetime
import logging
import whois

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Bot Config ---
TOKEN = "8052328802:AAF6jf7aj6JyqaxeyMieJsUHb3rDxP3oLIU"
MONGO_URI = "mongodb://user:password@host:port/database"
NUMVERIFY_API = "YOUR_NUMVERIFY_API_KEY"

client = MongoClient(MONGO_URI)
db = client.get_database()
collection = db.get_collection("leaked_data")
log_collection = db.get_collection("query_logs")

# --- /start ---
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📞 Phone Lookup", callback_data='/details')],
        [InlineKeyboardButton("🌐 IP Lookup", callback_data='/iplookup')],
        [InlineKeyboardButton("📧 Email Info", callback_data='/emailinfo')],
        [InlineKeyboardButton("🔍 Whois", callback_data='/whois')],
        [InlineKeyboardButton("🧠 Dork", callback_data='/dork')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        f"👋 Welcome {user.first_name}!

Use the buttons or type commands:
"
        "/details <number>\n/iplookup <ip>\n/emailinfo <email>\n/whois <domain>\n/dork <number>",
        reply_markup=reply_markup
    )

# --- NumVerify API ---
def get_external_info(number):
    try:
        url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API}&number={number}&format=1"
        data = requests.get(url).json()
        if data.get("valid"):
            return {
                "Country": data.get("country_name", "N/A"),
                "Carrier": data.get("carrier", "N/A"),
                "Line Type": data.get("line_type", "N/A"),
                "Location": data.get("location", "N/A")
            }
    except Exception as e:
        logger.warning(f"API error: {e}")
    return {}

# --- /details ---
def details(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("❌ Use: /details <phone>")
        return
    number = context.args[0]
    result = collection.find_one({'phone': number})
    name = result.get('name', 'N/A') if result else 'N/A'
    address = result.get('address', 'N/A') if result else 'N/A'
    location = result.get('location', 'N/A') if result else 'N/A'

    extra = get_external_info(number)
    msg = f"📞 Number: `{number}`\n👤 Name: {name}\n🏠 Address: {address}\n📍 Location: {location}"
    if extra:
        msg += "\n\n🌐 Extra Info:\n" + "\n".join([f"{k}: {v}" for k, v in extra.items()])
    update.message.reply_text(msg, parse_mode='Markdown')

# --- /iplookup ---
def iplookup(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("❌ Use: /iplookup <ip>")
        return
    ip = context.args[0]
    try:
        data = requests.get(f"http://ip-api.com/json/{ip}").json()
        if data["status"] == "success":
            msg = f"🌐 IP: `{ip}`\nCountry: {data['country']}\nCity: {data['city']}\nISP: {data['isp']}\nOrg: {data['org']}"
        else:
            msg = "❌ Invalid IP"
        update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {e}")

# --- /emailinfo ---
def emailinfo(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("❌ Use: /emailinfo <email>")
        return
    email = context.args[0]
    try:
        domain = email.split("@")[1]
        ip_list = socket.gethostbyname_ex(domain)[2]
        update.message.reply_text(f"📧 Domain: `{domain}`\n🔹 IPs: {', '.join(ip_list)}", parse_mode='Markdown')
    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {e}")

# --- /dork ---
def dork(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("❌ Use: /dork <number>")
        return
    num = context.args[0]
    links = [
        f'https://www.google.com/search?q="{num}"',
        f'https://www.google.com/search?q=site:pastebin.com+{num}',
        f'https://www.google.com/search?q=intitle:"{num}"',
        f'https://www.google.com/search?q=intext:"{num}"'
    ]
    update.message.reply_text("🔎 Dork Links:\n" + "\n".join(links))

# --- /whois ---
def whois_lookup(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("❌ Use: /whois <domain>")
        return
    domain = context.args[0]
    try:
        w = whois.whois(domain)
        msg = f"📄 Whois for `{domain}`:\n\n" + "\n".join([f"{k}: {v}" for k, v in w.items() if v])
        update.message.reply_text(msg[:4000], parse_mode='Markdown')  # limit msg size
    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {e}")

# --- Main ---
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("details", details))
    dp.add_handler(CommandHandler("iplookup", iplookup))
    dp.add_handler(CommandHandler("emailinfo", emailinfo))
    dp.add_handler(CommandHandler("dork", dork))
    dp.add_handler(CommandHandler("whois", whois_lookup))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

