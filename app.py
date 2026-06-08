import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- CONFIGURATION ---
BINARY_PATH = "./ARK"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8142270559:AAFOdVQ46Rf2icAxOoYa1S_K7IKlPC3w5N8")
# ---------------------

def execute_binary_worker(ip, port, time_arg):
    """Background worker that handles the execution of the ARK binary."""
    print(f"--> [EXEC] Running: {BINARY_PATH} {ip} {port} {time_arg}")
    try:
        # Give executable permissions just in case
        os.chmod(BINARY_PATH, 0o755)  
        
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
        f"🚀 **Launching Process...**\n\n🌐 **IP:** {ip}\n🔌 **Port:** {port}\n⏱️ **Time:** {time_arg} seconds"
    )

    # Launch binary process in background thread to avoid freezing the Telegram Bot polling loop
    threading.Thread(target=execute_binary_worker, args=(ip, port, time_arg), daemon=True).start()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    await update.message.reply_text(
        "🤖 **ARK Binary Runner Bot is Online!**\n\nTo execute a command, type:\n`/run <IP> <PORT> <TIME>`"
    )

# --- RENDER HEALTH CHECK WEB SERVER ---
class HealthServer(BaseHTTPRequestHandler):
    def do_GET(self):
        """Responds to standard web pings"""
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot and Health Check servers are running.")

    def do_HEAD(self):
        """FIXES THE CRASH: Responds to Render's internal HEAD status requests"""
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

    def log_message(self, format, *args):
        """Silences standard HTTP logs to keep your Render console completely clean"""
        return

def run_health_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(("0.0.0.0", port), HealthServer)
        print(f"--> Internal health check web server active on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"--> [SERVER CRASH]: {e}")

# --- MAIN RUNNER ---
def main():
    # 1. Spin up the Render-required web server in a background thread
    server_thread = threading.Thread(target=run_health_server, daemon=True)
    server_thread.start()

    # 2. Setup and launch Telegram Bot on the Main Thread
    print("--> Starting Telegram Bot Application...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("run", run_command))

    # Keep bot alive and listening for polling updates
    application.run_polling()

if __name__ == "__main__":
    main()
