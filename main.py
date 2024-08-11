import logging
import time
from datetime import datetime, timedelta
from threading import Timer
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your bot token
BOT_TOKEN = '6823753494:AAHa41WZgXEJswYiZHMYaUhlfCyn4MhG1so'

# Dictionary to store message IDs and their deletion times
message_schedule = {}

# Function to delete a message
def delete_message(context: CallbackContext):
    chat_id, message_id = context.job.context
    try:
        context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"Deleted message {message_id} from chat {chat_id}")
    except Exception as e:
        logger.error(f"Failed to delete message {message_id} from chat {chat_id}: {e}")

# Function to schedule message deletion
def schedule_deletion(update: Update, context: CallbackContext, message_id: int):
    chat_id = update.message.chat_id
    delete_time = datetime.now() + timedelta(minutes=1)
    job = context.job_queue.run_once(delete_message, when=delete_time, context=(chat_id, message_id))
    message_schedule[message_id] = job
    logger.info(f"Scheduled message {message_id} for deletion at {delete_time}")

# Function to handle incoming messages
def handle_message(update: Update, context: CallbackContext):
    message_id = update.message.message_id
    schedule_deletion(update, context, message_id)

# Function to start the bot
def start(update: Update, context: CallbackContext):
    sent_message = update.message.reply_text('Hello! I will delete your messages after one minute.')
    schedule_deletion(update, context, sent_message.message_id)

def main():
    # Create the Updater and pass it your bot's token
    updater = Updater(BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register the start handler
    dp.add_handler(CommandHandler("start", start))

    # Register the message handler
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()