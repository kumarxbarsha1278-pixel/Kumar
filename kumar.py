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
        "👋 Bot is online and ready.\n\nUse `/run <arguments>` to execute.", 
        parse_mode="Markdown"
    )

async def run_binary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Execute the binary with arguments supplied by the user."""
    if not context.args:
        await update.message.reply_text("❌ Missing arguments. Usage: `/run 12 34 56`")
        return

    user_args = context.args
    await update.message.reply_text("🔄 Running process...")

    try:
        # Check if binary file is present
        if not os.path.exists(BINARY_PATH):
            await update.message.reply_text(f"❌ Error: `{BINARY_PATH}` file is missing from repository.")
            return
            
        # Ensure correct execution permissions on Linux host
        os.chmod(BINARY_PATH, 0o755)

        # Build execution array
        command = [BINARY_PATH] + user_args

        # Execute system process
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            timeout=30  
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
        await update.message.reply_text("❌ Error: Process execution exceeded maximum timeout.")
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
