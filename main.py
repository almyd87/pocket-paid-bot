
import telebot
import json
import os

TOKEN = "7869769364:AAGWDK4orRgxQDcjfEHScbfExgIt_Ti8ARs"
ADMIN_ID = 1125130202

bot = telebot.TeleBot(TOKEN)
USERS_FILE = "users.json"
CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_user(user_id, username):
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
    if str(user_id) not in users:
        users[str(user_id)] = {"username": username, "status": "pending"}
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

def get_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def update_user_status(user_id, status):
    users = get_users()
    if str(user_id) in users:
        users[str(user_id)]["status"] = status
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or "لا يوجد"
    save_user(user_id, username)

    users = get_users()
    if users[str(user_id)]["status"] != "accepted":
        config = load_config()
        text = f"""
🔒 لا يمكنك استخدام البوت حتى يتم تفعيل اشتراكك.

💵 قيمة الاشتراك: {config['price']} دولار أمريكي
🏦 الدفع عبر Binance

📍 عنوان المحفظة:
{config['wallet']}

📸 بعد الدفع، أرسل صورة إثبات التحويل هنا.
"""
        with open("payment_guide.png", "rb") as img:
            bot.send_photo(message.chat.id, img, caption=text)
    else:
        bot.send_message(message.chat.id, "✅ مرحبًا بك! اشتراكك مفعل.")

@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    users = get_users()
    pending = [uid for uid, data in users.items() if data["status"] == "pending"]
    if not pending:
        bot.send_message(message.chat.id, "✅ لا يوجد طلبات اشتراك حالياً.")
        return

    for uid in pending:
        data = users[uid]
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("✅ قبول", callback_data=f"accept_{uid}"),
            telebot.types.InlineKeyboardButton("❌ رفض", callback_data=f"reject_{uid}")
        )
        bot.send_message(message.chat.id, f"طلب اشتراك جديد:
@{data['username']} (ID: {uid})", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("accept_") or call.data.startswith("reject_"))
def handle_decision(call):
    if call.from_user.id != ADMIN_ID:
        return
    action, uid = call.data.split("_")
    if action == "accept":
        update_user_status(uid, "accepted")
        bot.send_message(int(uid), "✅ تم تفعيل اشتراكك. يمكنك الآن استخدام البوت.")
        bot.edit_message_text("✅ تم قبول الاشتراك.", call.message.chat.id, call.message.message_id)
    elif action == "reject":
        update_user_status(uid, "rejected")
        bot.send_message(int(uid), "❌ تم رفض اشتراكك. تواصل مع الإدارة.")
        bot.edit_message_text("❌ تم رفض الاشتراك.", call.message.chat.id, call.message.message_id)

@bot.message_handler(content_types=['photo'])
def handle_payment_proof(message):
    user_id = message.from_user.id
    username = message.from_user.username or "لا يوجد"
    caption = f"🧾 إثبات دفع جديد
👤 المستخدم: @{username}
🆔 ID: {user_id}"
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption)
    bot.send_message(message.chat.id, "✅ تم استلام صورة الدفع. سيتم مراجعتها قريبًا.")

print("✅ Bot is running...")
bot.infinity_polling()
