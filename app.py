import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- CONFIGURATION ---
BINARY_PATH = "./ARK"
# Your token is placed here directly, but it will still check Environment Variables first.
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8142270559:AAFOdVQ46Rf2icAxOoYa1S_K7IKlPC3w5N8")
# ---------------------

def execute_binary_worker(ip, port, time_arg):
    """Background worker that handles the execution of the ARK binary."""
    print(f"--> [EXEC] Running: {BINARY_PATH} {ip} {port} {time_arg}")
    try:
        os.chmod(BINARY_PATH, 0o755)  # Ensure execution permissions on Render
        process = subprocess.Popen(
            [BINARY_PATH, ip, port, time_arg],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        print(f"--> [EXEC FINISHED] Exit Code: {process.returncode}")
        if process.returncode != 0:
            print(f"--> [EXEC ERROR]: {stderr}")
            
    except Exception as e:
        print(f"--> [EXEC CRITICAL EXCEPTION]: {e}")

async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /run command. 
    Usage: /run <IP> <PORT> <TIME>
    """
    if len(context.args) < 3:
        await update.message.reply_text(
            "❌ **Invalid Format.**\n\nUse: `/run <IP> <PORT> <TIME>`\nExample: `/run 1.1.1.1 80 60`"
        )
        return

    ip = context.args[0]
    port = context.args[1]
    time_arg = context.args[2]

    await update.message.reply_text(
        f"🚀 **Launching Binary Process...**\n\n🌐 **IP:** {ip}\n🔌 **Port:** {port}\n⏱️ **Time:** {time_arg} seconds"
    )

    # Launch process in background thread to keep the Telegram bot responsive
    threading.Thread(target=execute_binary_worker, args=(ip, port, time_arg), daemon=True).start()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    await update.message.reply_text(
        "🤖 **ARK Binary Runner Bot is Online!**\n\nTo execute a command, type:\n`/run <IP> <PORT> <TIME>`"
    )

# --- RENDER HEALTH WEB SERVER ---
class HealthServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Telegram Bot & Health Check Server Running.")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthServer)
    server.serve_forever()

# --- MAIN INITIATOR ---
def main():
    # Start Render health check server in background
    threading.Thread(target=run_health_server, daemon=True).start()

    # Build and start Telegram Bot Polling
    print("--> Starting Telegram Bot Application...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("run", run_command))

    application.run_polling()

if __name__ == "__main__":
    main()
