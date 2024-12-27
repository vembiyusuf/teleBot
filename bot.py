import os
import logging
from dotenv import load_dotenv
import telebot
from groq import Groq

# Memuat variabel lingkungan
load_dotenv()

# Ambil BOT_TOKEN dan GROQ_API_KEY dari .env
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Validasi BOT_TOKEN dan GROQ_API_KEY
if not BOT_TOKEN or not GROQ_API_KEY:
    raise ValueError("Pastikan BOT_TOKEN dan GROQ_API_KEY sudah disetel di file .env")

# Inisialisasi bot Telegram
bot = telebot.TeleBot(BOT_TOKEN)

# Set up logging untuk melacak kesalahan dan aktivitas
logging.basicConfig(level=logging.INFO)

# Fungsi untuk log aktivitas
def log_message(message):
    logging.info(f"Pesan diterima dari {message.chat.first_name}: {message.text}")

# Inisialisasi klien Groq API
client = Groq(
    api_key=GROQ_API_KEY
)

# Fungsi untuk memanggil API Groq dan mendapatkan respons
def get_groq_response(prompt):
    """
    Mengirim permintaan ke API Groq untuk mendapatkan respons.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192"  # Model terbaru
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Error saat memanggil API Groq: {e}")
        return "Maaf, terjadi kesalahan saat memproses permintaan ke Groq AI."

# Command /start dan /hello
@bot.message_handler(commands=['start', 'hello'])
def kirim_sambutan(message):
    log_message(message)
    bot.reply_to(message, f"Halo {message.chat.first_name}, bagaimana kabarmu?")

# Command /help untuk panduan
@bot.message_handler(commands=['help'])
def kirim_bantuan(message):
    log_message(message)
    bantuan_text = """
Saya adalah bot yang bisa melakukan beberapa tugas sederhana:
- /start: Mulai percakapan dengan bot.
- /hello: Sapa bot dan lihat responsnya.
- /help: Lihat panduan ini.
- /about: Info tentang bot.
- /mabar: Mengajak bermain game (ML, FF, E-Football).
- /aibot: Tanyakan saya sesuatu dan saya akan menjawabnya dengan AI.
    """
    bot.reply_to(message, bantuan_text)

# Command /mabar
@bot.message_handler(commands=['mabar'])
def kirim_mabar(message):
    log_message(message)
    bot.reply_to(message, "Baik, silahkan invite saya. Ini ID saya: 9398489263.")

# Command /about
@bot.message_handler(commands=['about'])
def kirim_tentang(message):
    log_message(message)
    bot.reply_to(message, "Saya adalah ucup_bot, dibuat untuk membantu Anda belajar membuat bot Telegram!")

# Command /aibot untuk berinteraksi dengan AI
@bot.message_handler(commands=['aibot'])
def aibot_response(message):
    log_message(message)
    bot.reply_to(message, "Silakan tulis pertanyaan Anda untuk AI.")
    bot.register_next_step_handler(message, process_aibot_query)

def process_aibot_query(message):
    log_message(message)
    # Memanggil Groq AI untuk mendapatkan respons
    response = get_groq_response(message.text)
    bot.reply_to(message, response)

# Penanganan semua pesan lainnya
@bot.message_handler(func=lambda msg: True)
def echo_semua(message):
    log_message(message)
    try:
        # Balas pesan yang dikirim oleh pengguna
        bot.reply_to(message, message.text)
    except Exception as e:
        # Log error jika terjadi masalah
        logging.error(f"Error saat merespons: {e}")
        bot.reply_to(message, "Maaf, terjadi kesalahan saat memproses pesanmu.")

# Menjalankan bot dengan polling() biasa untuk mencegah konflik
try:
    logging.info("Bot sedang berjalan...")
    bot.polling(none_stop=True)
except Exception as e:
    logging.error(f"Bot gagal berjalan: {e}")
