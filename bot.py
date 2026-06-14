import os
import threading
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")


# HTTP-сервер для Render + UptimeRobot
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._send_ok()

    def do_HEAD(self):
        """HEAD-запрос от Uptime Robot — отвечаем без тела."""
        self._send_ok()

    def _send_ok(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        if self.command == "GET":
            self.wfile.write(b"Bot is running")

    def log_message(self, format, *args):
        pass


def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    print(f"🌐 HTTP Server running on port {port}")
    server.serve_forever()


# Запускаем сервер в отдельном потоке
threading.Thread(target=run_server, daemon=True).start()


async def delete_system_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаляет системные сообщения о входе/выходе участников"""

    if not update.message:
        return

    # Проверяем, является ли сообщение системным (вход/выход участника)
    if update.message.new_chat_members or update.message.left_chat_member:
        try:
            await update.message.delete()
            print(f"Удалено системное сообщение в чате {update.message.chat.title}")
        except Exception as e:
            print(f"Не удалось удалить сообщение: {e}")


def main():
    # Явно создаём цикл событий для Python 3.14
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.StatusUpdate.LEFT_CHAT_MEMBER,
            delete_system_messages,
        )
    )

    print("✅ Бот запущен... Мониторинг системных сообщений...")

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()