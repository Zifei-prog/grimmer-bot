import os
import re
import time
import random
import telebot
from telebot import types
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ── state per user ──────────────────────────────
state = {}   # {chat_id: {"nomor": str, "bug": str}}

BUG_TYPES = {
    "bug_fc":       ("Android FC",      "Target akan crash total dalam 5 detik."),
    "bug_freeze":   ("WA Freeze",       "Aplikasi target akan freeze, tidak bisa dibuka."),
    "bug_ghost":    ("Ghost Bug",       "Pesan error tersembunyi, target tidak sadar WA-nya rusak."),
    "bug_infinity": ("Infinity Crash",  "Loop crash berulang, HP target harus restart manual."),
}

# ── helpers ─────────────────────────────────────
def valid_nomor(text: str) -> str | None:
    """Normalisasi nomor WA Indonesia. Return None kalau gak valid."""
    digits = re.sub(r"\D", "", text)
    if digits.startswith("0"):
        digits = "62" + digits[1:]
    elif digits.startswith("8"):
        digits = "62" + digits
    if not digits.startswith("62"):
        return None
    if not (10 <= len(digits) <= 15):
        return None
    return digits

def fmt_nomor(n: str) -> str:
    return f"+{n[:2]} {n[2:5]}-{n[5:9]}-{n[9:]}"

def main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("💀 Sender Bug"),
        types.KeyboardButton("ℹ️ Cara Kerja"),
        types.KeyboardButton("📊 Status Tool"),
    )
    bot.send_message(
        chat_id,
        "Pilih menu di bawah 👇",
        reply_markup=markup,
    )

def bug_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("💀 Android FC",    callback_data="bug_fc"),
        types.InlineKeyboardButton("❄️ WA Freeze",     callback_data="bug_freeze"),
        types.InlineKeyboardButton("👻 Ghost Bug",     callback_data="bug_ghost"),
        types.InlineKeyboardButton("💥 Infinity Crash", callback_data="bug_infinity"),
    )
    return kb

# ── command /start ──────────────────────────────
@bot.message_handler(commands=["start"])
def cmd_start(message):
    state.pop(message.chat.id, None)
    nama = message.from_user.first_name or "bro"
    bot.send_message(
        message.chat.id,
        f"👋 Halo *{nama}*, selamat datang di *GRIMMER SENDER*.\n\n"
        "Tool pengirim bug WhatsApp paling stabil di Indonesia.\n"
        "100% anonim · tanpa login · tanpa jejak.\n\n"
        "Klik *💀 Sender Bug* buat mulai.",
        parse_mode="Markdown",
    )
    main_menu(message.chat.id)

# ── menu: cara kerja ────────────────────────────
@bot.message_handler(func=lambda m: m.text == "ℹ️ Cara Kerja")
def cara_kerja(message):
    bot.send_message(
        message.chat.id,
        "🧠 *CARA KERJA GRIMMER SENDER*\n\n"
        "1. Masukkan nomor WA target (format 08xx atau 62xx).\n"
        "2. Pilih tipe bug yang mau dikirim.\n"
        "3. Bot akan inject payload ke server WhatsApp target.\n"
        "4. Target otomatis crash / freeze dalam hitungan detik.\n\n"
        "⚠️ *PENTING:*\n"
        "Bug ini paling efektif kalau target pakai *WhatsApp Bisnis*.\n"
        "Bug nembak celah enkripsi khusus WA Bisnis — kalau target pakai WA biasa, "
        "efeknya lebih lemah tapi tetap kena.\n\n"
        "🔒 *Aman?*\n"
        "Ya. Bot gak nyimpen nomor lu, gak nyimpen nomor target, gak ada log. "
        "Semua proses jalan di server anonim.",
        parse_mode="Markdown",
    )

# ── menu: status tool ───────────────────────────
@bot.message_handler(func=lambda m: m.text == "📊 Status Tool")
def status_tool(message):
    users = random.randint(1200, 1350)
    sent  = random.randint(89000, 91000)
    bot.send_message(
        message.chat.id,
        f"📊 *STATUS GRIMMER SENDER*\n\n"
        f"🟢 Server: Online\n"
        f"👥 User online: {users:,}\n"
        f"💀 Bug terkirim hari ini: {sent:,}\n"
        f"⚡ Success rate: 99%\n"
        f"🔧 Versi: v4.2.1\n\n"
        f"Semua sistem normal. Siap kirim.",
        parse_mode="Markdown",
    )

# ── menu: sender bug ────────────────────────────
@bot.message_handler(func=lambda m: m.text == "💀 Sender Bug")
def ask_number(message):
    state[message.chat.id] = {}
    msg = bot.send_message(
        message.chat.id,
        "📱 Masukkan nomor WA target.\n\n"
        "Contoh: `08123456789` atau `6281234567890`",
        parse_mode="Markdown",
    )
    bot.register_next_step_handler(msg, step_number)

def step_number(message):
    nomor = valid_nomor(message.text or "")
    if not nomor:
        bot.send_message(
            message.chat.id,
            "❌ Format nomor gak valid.\n"
            "Harus nomor Indonesia, contoh: `08123456789` atau `6281234567890`.",
            parse_mode="Markdown",
        )
        main_menu(message.chat.id)
        return

    state[message.chat.id] = {"nomor": nomor}
    bot.send_message(
        message.chat.id,
        f"✅ Target: *{fmt_nomor(nomor)}*\n\n"
        f"Sekarang pilih tipe bug:",
        parse_mode="Markdown",
        reply_markup=bug_keyboard(),
    )

# ── callback: pilih bug ─────────────────────────
@bot.callback_query_handler(func=lambda c: c.data.startswith("bug_"))
def process_bug(call):
    data = state.get(call.message.chat.id)
    if not data or "nomor" not in data:
        bot.answer_callback_query(call.id, "Sesi habis, mulai ulang dari menu.")
        return

    bug_key = call.data
    bug_name, bug_effect = BUG_TYPES[bug_key]
    nomor = data["nomor"]
    data["bug"] = bug_key

    bot.answer_callback_query(call.id, f"{bug_name} dipilih")
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"⏳ *Mengirim payload ke server WhatsApp target...*\n\n"
             f"📞 Target: `{fmt_nomor(nomor)}`\n"
             f"💀 Bug: *{bug_name}*\n"
             f"📡 Status: connecting...",
        parse_mode="Markdown",
    )

    # fake progress realistis
    steps = [
        "🔍 Memindai server target...",
        "🔓 Membuka celah enkripsi...",
        "📦 Menyiapkan payload...",
        "🚀 Mengirim payload...",
        "📡 Menunggu konfirmasi server...",
    ]
    for s in steps:
        time.sleep(random.uniform(0.8, 1.4))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"⏳ *Mengirim payload...*\n\n"
                 f"📞 Target: `{fmt_nomor(nomor)}`\n"
                 f"💀 Bug: *{bug_name}*\n\n"
                 f"{s}",
            parse_mode="Markdown",
        )

    # fake deteksi tipe WA — random, biar keliatan "beneran ngecek"
    wa_type = random.choice(["WhatsApp Bisnis", "WhatsApp Bisnis", "WhatsApp Biasa"])
    if wa_type == "WhatsApp Bisnis":
        work_note = "Bug 100% work di WA Bisnis. Target dijamin FC."
    else:
        work_note = "Target pakai WA biasa. Efek lebih lemah, tapi tetap kena freeze."

    time.sleep(random.uniform(1.0, 1.8))
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"✅ *PAYLOAD BERHASIL TERKIRIM!*\n\n"
             f"📞 Target: `{fmt_nomor(nomor)}`\n"
             f"💀 Bug: *{bug_name}*\n"
             f"📱 Tipe WA target: *{wa_type}*\n"
             f"📡 Status: Delivered ✓\n"
             f"🔥 Efek: {bug_effect}\n\n"
             f"ℹ️ {work_note}\n\n"
             f"_Payload sudah diterima server target. "
             f"Efek muncul dalam 5 detik._",
        parse_mode="Markdown",
    )

    state.pop(call.message.chat.id, None)
    time.sleep(1.5)
    main_menu(call.message.chat.id)

# ── fallback ────────────────────────────────────
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(
        message.chat.id,
        "Ketik /start buat mulai, atau pilih menu di bawah 👇",
    )
    main_menu(message.chat.id)

# ── run ─────────────────────────────────────────
if __name__ == "__main__":
    print("Grimmer Sender bot running...")
    bot.infinity_polling(timeout=30, long_polling_timeout=20)