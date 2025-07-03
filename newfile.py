import pandas as pd
import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

BOT_TOKEN = "7670129820:AAEMiK22t-_MAv4n4lvLOr5GKVvh_ujmNeY"  # <-- الصق التوكن من BotFather

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا! أرسل لي ملف صفقاتك بصيغة CSV وسأحلله لك 📈")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    file_path = f"{update.message.document.file_name}"
    await file.download_to_drive(file_path)

    try:
        df = pd.read_csv(file_path)
        df['الربح_الصافي'] = df['العائد'] - df['المبلغ']
        total_trades = len(df)
        wins = df[df['النتيجة'] == 'Win']
        losses = df[df['النتيجة'] == 'Loss']
        net_profit = df['الربح_الصافي'].sum()
        win_rate = (len(wins) / total_trades) * 100

        summary = (
            f"📊 تحليل صفقاتك:\n"
            f"- عدد الصفقات: {total_trades}\n"
            f"- صفقات رابحة: {len(wins)}\n"
            f"- صفقات خاسرة: {len(losses)}\n"
            f"- نسبة النجاح: {win_rate:.2f}%\n"
            f"- الربح/الخسارة الصافية: {net_profit:.2f} $\n"
        )

        await update.message.reply_text(summary)

    except Exception as e:
        await update.message.reply_text("حدث خطأ أثناء التحليل. تأكد من أن الملف بصيغة CSV ويحتوي على الأعمدة المطلوبة.")
        print("خطأ:", e)

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# تشغيل البوت
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Document.FileExtension("csv"), handle_document))

print("🤖 البوت يعمل الآن...")
app.run_polling()