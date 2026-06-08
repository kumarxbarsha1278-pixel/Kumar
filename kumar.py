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

# HARDCODED FIX: Putting the token directly in the code
TOKEN = "8142270559:AAFOdVQ46Rf2icAxOoYa1S_K7IKlPC3w5N8"

# Setting your exact binary name
BINARY_PATH = "./ARK"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Hi! Use the command followed by your parameters.\n\nExample:\n`/run 12 34 56`", 
        parse_mode="Markdown"
    )

async def run_binary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Execute the ARK binary with user arguments."""
    if not context.args:
        await update.message.reply_text("❌ Please provide parameters. Example: `/run 12 34 56`")
        return

    user_args = context.args
    await update.message.reply_text("🔄 Processing your request...")

    try:
        # Check if ARK exists
        if not os.path.exists(BINARY_PATH):
            await update.message.reply_text(f"❌ Error: `{BINARY_PATH}` file not found in repository.")
            return
            
        # Give execution permissions to ARK inside Railway
        os.chmod(BINARY_PATH, 0o755)

        # Combines into: ['./ARK', '12', '34', '56']
        command = [BINARY_PATH] + user_args

        # Execute the binary safely
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            timeout=45  
        )

        output = result.stdout.strip() if result.stdout else "Execution finished with no standard output."
        errors = result.stderr.strip()

        # Build response message
        response = f"✅ **Output:**\n```\n{output}\n```"
        if errors:
            response += f"\n⚠️ **Stderr/Logs:**\n```\n{errors}\n```"

        if len(response) > 4000:
            response = response[:3900] + "\n...[Truncated due to length]"

        await update.message.reply_text(response, parse_mode="Markdown")

    except subprocess.TimeoutExpired:
        await update.message.reply_text("❌ Error: Command execution timed out.")
    except Exception as e:
        logger.error(f"Error executing binary: {e}")
        await update.message.reply_text(f"❌ System Error: {str(e)}")

def main() -> None:
    # Build the application directly with the hardcoded token
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("run", run_binary))
    
    logger.info("Bot is polling successfully with hardcoded token...")
    application.run_polling()

if __name__ == "__main__":
    main()
