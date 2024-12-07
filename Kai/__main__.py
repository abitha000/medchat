import time
import logging
from telegram import Update, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext, Application
import pymongo
from bson.objectid import ObjectId

# MongoDB setup
client = pymongo.MongoClient("mongodb+srv://avianandh004:TeamHdt009@cluster0.hdvf3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # MongoDB URI
db = client["medbot"]
faq_collection = db["faq"]

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to simulate typing effect
def send_typing_effect(update: Update, text: str):
    for char in text:
        update.message.reply_text(char, disable_notification=True)
        time.sleep(0.1)

# Start function
def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s started the bot.", user.first_name)
    start_image = "https://example.com/start_image.jpg"  # Replace with your start image URL
    update.message.reply_photo(start_image, caption="Welcome to MedBot! How can I assist you today? Type /help for more options.")

# Help command
def help_command(update: Update, context: CallbackContext):
    help_text = """
    Available Commands:
    /help - Get help information
    /support - Contact support
    /request <question> - Request an answer for a question not in the bot's knowledge base
    """
    send_typing_effect(update, help_text)

# Support command
def support_command(update: Update, context: CallbackContext):
    support_text = """
    If you need further assistance, please reach out to our support team at support@medbot.com
    """
    send_typing_effect(update, support_text)

# Request command
def request_answer(update: Update, context: CallbackContext):
    if context.args:
        question = ' '.join(context.args)
        # You can add logic to save requests to MongoDB for future response
        request_text = f"Your request for the question '{question}' has been received. Our team will get back to you shortly."
        send_typing_effect(update, request_text)
    else:
        send_typing_effect(update, "Please provide a question after /request command.")

# Add FAQ command (admin only)
def add_faq(update: Update, context: CallbackContext):
    if update.message.from_user.id == 1556830659:  # Replace with your admin user ID
        if len(context.args) >= 2:
            question = context.args[0]
            answer = ' '.join(context.args[1:])
            faq_collection.insert_one({"question": question, "answer": answer})
            send_typing_effect(update, "FAQ added successfully!")
        else:
            send_typing_effect(update, "Please provide both question and answer after the /addfaq command.")
    else:
        send_typing_effect(update, "You are not authorized to use this command.")

# Function to handle user messages and provide answers from MongoDB
def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text.lower()

    # Check if the question exists in the FAQ collection
    faq = faq_collection.find_one({"question": {"$regex": user_message, "$options": "i"}})

    if faq:
        send_typing_effect(update, faq["answer"])
    else:
        send_typing_effect(update, "Sorry, I don't have an answer for that. Type /request to ask for assistance.")

# Main function to set up the bot
def main():
    # Your Telegram Bot API Token
    API_TOKEN = "6819381670:AAGVK-B6hceOQqOkFcVNeIIZG-cxcI-h_XA"  # Replace with your Telegram Bot API token

    application = Application.builder().token('API_TOKEN').build()

    # Dispatcher to handle commands and messages
    dispatcher = application.dispatcher

    # Command Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("support", support_command))
    dispatcher.add_handler(CommandHandler("request", request_answer))
    dispatcher.add_handler(CommandHandler("addfaq", add_faq))

    # Message Handler for handling questions
    dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.command, handle_message))

    # Start polling
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
  
