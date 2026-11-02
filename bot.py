import os
import random
import difflib
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

SOAL_BANK = [
    {"jp": "あしたプールでおよいだあとスーパーでフルーツをかいます。", "benar": "ashita puuru de oyoida ato suupaa de furuutsu o kaimasu", "arti": "besok setelah renang di kolam beli buah di supermarket"},
    {"jp": "きょうはともだちとあたらしいレストランにいきました。テーブルはとてもきれいでした。", "benar": "kyou wa tomodachi to atarashii resutoran ni ikimashita. teeburu wa totemo kirei deshita", "arti": "hari ini pergi ke restoran baru sama temen. mejanya indah banget"},
    {"jp": "スーパーでセールがありました。ブルーのタオルとレモンティーをかいました。", "benar": "suupaa de seeru ga arimashita. buruu no taoru to remon tii o kaimashita", "arti": "di supermarket ada diskon. beli handuk biru dan teh lemon"},
    {"jp": "よるはテレビでサッカーをみます。サッカーのルールはむずかしいですがたのしいです。", "benar": "yoru wa terebi de sakkaa o mimasu. sakkaa no ruuru wa muzukashii desu ga tanoshii desu", "arti": "malam nonton bola di tv. aturan bola susah tapi seru"},
    {"jp": "あしたのニュースはセブンニュースです。", "benar": "ashita no nyuusu wa sebun nyuusu desu", "arti": "berita besok adalah seven news"},
    {"jp": "コーヒーとケーキをテーブルにおきました。", "benar": "koohii to keeki o teeburu ni okimashita", "arti": "naruh kopi dan kue di meja"},
    {"jp": "きょうはバーベキューをしました。", "benar": "kyou wa baabekyuu o shimashita", "arti": "hari ini barbekyu"},
]

# simpen soal per user biar gak rebutan
soal_per_user = {}

async def kirim_soal_ke_user(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.chat_id
    soal = random.choice(SOAL_BANK)
    soal_per_user[chat_id] = soal
    await context.bot.send_message(chat_id=chat_id, text=f"⏰ SOAL OTOMATIS (1 JAM)\n\n{soal['jp']}\n\nAyo romajiin! /soal buat ganti")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    soal = random.choice(SOAL_BANK)
    soal_per_user[chat_id] = soal
    
    # hapus jadwal lama biar gak dobel
    for job in context.job_queue.get_jobs_by_name(str(chat_id)):
        job.schedule_removal()
    
    context.job_queue.run_repeating(kirim_soal_ke_user, interval=3600, first=3600, chat_id=chat_id, name=str(chat_id))
    
    await update.message.reply_text(f"Bot aktif bre! Soal lu beda sama orang lain.\n\nSOAL PERTAMA:\n\n{soal['jp']}\n\nAyo romajiin!\n\n/soal - soal baru\n/stop - berhentiin bot per jam")

async def soal_baru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    soal = random.choice(SOAL_BANK)
    soal_per_user[chat_id] = soal
    await update.message.reply_text(f"SOAL BARU BRE!\n\n{soal['jp']}\n\nAyo romajiin!")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    for job in context.job_queue.get_jobs_by_name(str(chat_id)):
        job.schedule_removal()
    await update.message.reply_text("Oke bot per jam gw stop. Ketik /start lagi kalo mau aktifin lagi.")

async def koreksi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    soal = soal_per_user.get(chat_id)
    
    if not soal:
        await update.message.reply_text("Ketik /start dulu bre!")
        return
    
    user = update.message.text.lower().strip()
    benar = soal['benar']
    
    ratio = difflib.SequenceMatcher(None, user, benar).ratio()
    nilai = int(ratio * 100)
    
    if nilai >= 95:
        await update.message.reply_text(f"NILAI {nilai}/100 - RAJA KATAKANA! 👑🔥\n\nKunci: {benar}\nArti: {soal['arti']}\n\nKetik /soal buat lanjut!")
    elif nilai >= 70:
        await update.message.reply_text(f"NILAI {nilai}/100 - LUMAYAN BRE!\n\nLu: {user}\nKunci: {benar}\nArti: {soal['arti']}\n\nCek vokal panjang: suupaa bukan supa, seeru bukan seru, teeburu bukan teberu")
    else:
        await update.message.reply_text(f"NILAI {nilai}/100 - AYO LAGI!\n\nLu: {user}\nKunci: {benar}\nArti: {soal['arti']}")

# TOKEN ngambil dari Environment Render, bukan ditulis langsung
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    print("ERROR: BOT_TOKEN belum di-set!")
    print("Set di Render -> Environment Variables")
else:
    print("Bot multi-user jalan bre...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("soal", soal_baru))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, koreksi))
    app.run_polling()
