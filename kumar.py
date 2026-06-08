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

TOKEN = os.getenv("8142270559:AAE0NSXI4vyA2RyTBAu3KY9EY8qjSQaGwpI")
# Changed from "./binary" to "./kumar"
BINARY_PATH = "./ARK"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome! Use the run command followed by your parameters.\n\nExample:\n`/run 12 34 56`", 
        parse_mode="Markdown"
    )

async def run_binary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("❌ Please provide parameters. Example: `/run 12 34 56`")
        return

    user_args = context.args
    await update.message.reply_text("🔄 Processing your request...")

    try:
        # Check if the renamed binary exists
        if not os.path.exists(BINARY_PATH):
            await update.message.reply_text(f"❌ Error: `{BINARY_PATH}` not found in Railway environment.")
            return
            
        # Give execution permissions to 'kumar'
        os.chmod(BINARY_PATH, 0o755)

        # Combines into: ['./kumar', '12', '34', '56']
        command = [BINARY_PATH] + user_args

        # Execute the binary
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            timeout=45
        )

        output = result.stdout.strip() if result.stdout else "Execution finished with no standard output."
        errors = result.stderr.strip()

        response = f"✅ **Output:**\n```\n{output}\n```"
        if errors:
            response += f"\n⚠️ **Stderr/Logs:**\n```\n{errors}\n```"

        if len(response) > 4000:
            response = response[:3900] + "\n...[Truncated]"

        await update.message.reply_text(response, parse_mode="Markdown")

    except subprocess.TimeoutExpired:
        await update.message.reply_text("❌ Error: Command execution timed out.")
    except Exception as e:
        logger.error(f"Error executing binary: {e}")
        await update.message.reply_text(f"❌ System Error: {str(e)}")

def main() -> None:
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN variable is missing!")
        return

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("run", run_binary))
    
    logger.info("Bot is polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
