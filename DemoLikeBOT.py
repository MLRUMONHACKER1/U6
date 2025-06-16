from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
from datetime import datetime, timedelta
import threading

# ✅ Bot Token
API_TOKEN = "7586858250:AAHSiIM812OwSELLQZCQJa_xoS4-ClilRVE"
ALLOWED_GROUP_ID = -1002828129907
VIP_USER_ID = 8073890761.6118026850  # float id দেওয়া যাবে না এখানে

user_usage = {}
like_usage = {"BD": 0, "IND": 0}

# ✅ কীবোর্ড
def join_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/jexarofficial")]
    ])

def vip_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/jexarofficial")],
        [InlineKeyboardButton("💎 Buy VIP", url="https://t.me/GODJEXAR")]
    ])

def verify_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Verify For Extra Likes", url="https://shortxlinks.in/RTubx")]
    ])

# ✅ লিমিট রিসেট ফাংশন
def reset_daily_limits():
    global user_usage, like_usage
    user_usage = {}
    like_usage = {"BD": 0, "IND": 0}
    print("✅ Daily limits reset.")

def schedule_reset():
    while True:
        now = datetime.now()
        next_reset = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        wait_seconds = (next_reset - now).total_seconds()
        threading.Timer(wait_seconds, reset_daily_limits).start()
        break

# ✅ মূল লাইক কমান্ড
async def like_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg.chat.id != ALLOWED_GROUP_ID:
        return

    parts = msg.text.split()
    if len(parts) != 3:
        await msg.reply_text("❗ Format: /like bd uid", reply_markup=join_keyboard())
        return

    region, uid = parts[1].upper(), parts[2]
    if region not in ["BD", "IND"]:
        await msg.reply_text("❗ Only BD or IND supported!", reply_markup=join_keyboard())
        return

    user_id = msg.from_user.id
    if user_id != VIP_USER_ID:
        if user_usage.get(user_id, 0) >= 1:
            await msg.reply_text("🚫 You already used your like today!", reply_markup=verify_keyboard())
            return
        if like_usage[region] >= 30:
            await msg.reply_text(f"⚠️ Daily like limit reached for {region}. Try again tomorrow.", reply_markup=join_keyboard())
            return

    wait = await msg.reply_text("⏳ Sending Likes, Please Wait.....")
    url = f"https://anish-likes.vercel.app/like?server_name={region.lower()}&uid={uid}&key=jex4rrr"

    try:
        r = requests.get(url)
        data = r.json()
    except:
        await wait.edit_text("❌ Failed to fetch data. Try again later.", reply_markup=join_keyboard())
        return

    if data.get("status") == 2:
        await wait.edit_text(
            f"🚫 Max Likes Reached\n\n"
            f"👤 Name: {data.get('PlayerNickname', 'N/A')}\n"
            f"🆔 UID: {uid}\n"
            f"🌍 Region: {region}\n"
            f"❤️ Current Likes: {data.get('LikesNow', 'N/A')}",
            reply_markup=vip_keyboard()
        )
        return

    await wait.edit_text(
        f"✅ Likes Sent Successfully!\n\n"
        f"👤 Name: {data.get('PlayerNickname', 'N/A')}\n"
        f"🆔 UID: {uid}\n"
        f"❤️ Before Likes: {data.get('LikesbeforeCommand', 'N/A')}\n"
        f"👍 Current Likes: {data.get('LikesafterCommand', 'N/A')}\n"
        f"🎯 Likes Sent: {data.get('LikesGivenByAPI', 'N/A')}",
        reply_markup=join_keyboard()
    )

    if user_id != VIP_USER_ID:
        user_usage[user_id] = 1
        like_usage[region] += 1

# ✅ মেইন ফাংশন
if __name__ == "__main__":
    schedule_reset()

    app = ApplicationBuilder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("like", like_handler))

    print("🤖 Bot is Running...")
    app.run_polling()
