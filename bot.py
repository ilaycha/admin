import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")


# Фиктивный HTTP-сервер для Render
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running')
    
    def log_message(self, format, *args):
        pass

def run_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"Fake HTTP server running on port {port}")
    server.serve_forever()

# Запускаем сервер в отдельном потоке
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()


async def delete_system_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаляет системные сообщения о входе/выходе участников"""
    
    # Проверяем, есть ли сообщение
    if not update.message:
        return
    
    # Проверяем, является ли сообщение системным (вход/выход участника)
    if update.message.new_chat_members or update.message.left_chat_member:
        try:
            # Удаляем сообщение
            await update.message.delete()
            print(f"Удалено системное сообщение в чате {update.message.chat.title}")
        except Exception as e:
            print(f"Не удалось удалить сообщение: {e}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Обрабатываем все сообщения, но только те, что содержат системную информацию
    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.StatusUpdate.LEFT_CHAT_MEMBER,
            delete_system_messages,
        )
    )

    print("Bot started... Monitoring for system messages...")

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()