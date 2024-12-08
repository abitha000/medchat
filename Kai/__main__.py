import logging
import pymongo
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram.ext import CallbackContext
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# MongoDB Connection Setup
client = MongoClient(os.getenv('MONGO_URI', 'mongodb+srv://avianandh004:TeamHdt009@cluster0.hdvf3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'))
db = client['faq_bot']
faq_collection = db['faq']

# Telegram Bot Setup
updater = Updater(token=os.getenv('TELEGRAM_TOKEN', '7548088682:AAFL08f6rTFBErJhbDK3uMMC7n_ZJDe3_QM'), use_context=True)
dispatcher = updater.dispatcher

# Logging Setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Language support
translations = {
    'en': {
        "start": "Welcome! I am your FAQ bot. How can I assist you today?",
        "help": "You can ask questions or request new ones. Use /request to submit a question.",
        "add_question": "To add a new question, use the command: /add_question followed by your question.",
        "edit_question": "To edit a question, use the command: /edit_question followed by the question you want to edit.",
        "delete_question": "To delete a question, use the command: /delete_question followed by the question you want to delete.",
        "not_found": "Sorry, I couldn't find an answer to that.",
        "faq_available": "Here are the available questions and answers."
    },
    'ta': {
        "start": "வணக்கம்! நான் உங்கள் கேள்வி பதில் பார்வையாளர். எப்படி உதவ முடியும்?",
        "help": "நீங்கள் கேள்விகள் கேட்க அல்லது புதிய கேள்வி கேட்டுக் கொள்ளலாம். /request ஐப் பயன்படுத்தி கேள்வி கேட்க.",
        "add_question": "புதிய கேள்வி சேர்க்க: /add_question உங்கள் கேள்வியுடன்.",
        "edit_question": "ஒரு கேள்வியை திருத்த: /edit_question உங்கள் கேள்வியை திருத்தவும்.",
        "delete_question": "ஒரு கேள்வியை நீக்க: /delete_question உங்கள் கேள்வியை நீக்கவும்.",
        "not_found": "மன்னிக்கவும், இந்த கேள்விக்கு பதில் எதுவும் இல்லை.",
        "faq_available": "இதுவரை உள்ள கேள்விகள் மற்றும் பதில்கள்."
    }
}

# Helper Functions
def get_answer_from_db(question, language='en'):
    query = {"question": question}
    result = faq_collection.find_one(query)
    if result:
        return result['answer'].get(language, "Answer not available in this language.")
    return None

def add_question_to_db(question, answer, language='en'):
    faq_collection.insert_one({
        "question": question,
        "answer": {
            'en': answer,
            'ta': answer
        }
    })

def edit_question_in_db(old_question, new_question, answer, language='en'):
    faq_collection.update_one(
        {"question": old_question},
        {"$set": {"question": new_question, "answer": {'en': answer, 'ta': answer}}}
    )

def delete_question_from_db(question):
    faq_collection.delete_one({"question": question})

def send_welcome(update: Update, context: CallbackContext):
    user_language = 'ta' if update.message.from_user.language_code == 'ta' else 'en'
    update.message.reply_text(
        translations[user_language]['start'],
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

def start(update: Update, context: CallbackContext):
    send_welcome(update, context)

def help_command(update: Update, context: CallbackContext):
    user_language = 'ta' if update.message.from_user.language_code == 'ta' else 'en'
    update.message.reply_text(translations[user_language]['help'])

def request_question(update: Update, context: CallbackContext):
    update.message.reply_text("Please type your question, and we will add it to the FAQ.")

def add_question(update: Update, context: CallbackContext):
    user_message = ' '.join(context.args)
    if not user_message:
        update.message.reply_text("Please provide the question.")
        return

    answer = "This is the placeholder answer."  # You can modify this to accept answers as well.
    add_question_to_db(user_message, answer)
    update.message.reply_text(f"Question '{user_message}' added successfully.")

def edit_question(update: Update, context: CallbackContext):
    old_question = context.args[0]
    new_question = context.args[1]
    answer = ' '.join(context.args[2:])
    
    if not old_question or not new_question or not answer:
        update.message.reply_text("Please provide old question, new question and answer.")
        return

    edit_question_in_db(old_question, new_question, answer)
    update.message.reply_text(f"Question '{old_question}' has been updated to '{new_question}'.")

def delete_question(update: Update, context: CallbackContext):
    question = ' '.join(context.args)
    if not question:
        update.message.reply_text("Please provide the question to delete.")
        return

    delete_question_from_db(question)
    update.message.reply_text(f"Question '{question}' has been deleted.")

def handle_message(update: Update, context: CallbackContext):
    question = update.message.text
    user_language = 'ta' if update.message.from_user.language_code == 'ta' else 'en'

    # Simulate typing animation
    context.bot.send_chat_action(chat_id=update.message.chat_id, action="typing")
    time.sleep(1.5)  # Simulate a delay like typing

    # Try to get an answer from the database
    answer = get_answer_from_db(question, user_language)

    if answer:
        update.message.reply_text(answer)
    else:
        update.message.reply_text(translations[user_language]['not_found'])

def request_for_new_answer(update: Update, context: CallbackContext):
    update.message.reply_text("Your question will be submitted for review and will be added if appropriate.")

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Add me to the group", url="https://t.me/YourGroupLink")],
        [InlineKeyboardButton("Support", callback_data='support')],
        [InlineKeyboardButton("Help", callback_data='help')]
    ]
    return InlineKeyboardMarkup(keyboard)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "help":
        help_command(update, context)
    elif query.data == "support":
        query.edit_message_text("For support, please contact @YourSupportUsername.")

def error(update: Update, context: CallbackContext):
    logger.warning(f"Update {update} caused error {context.error}")

def run():
    # Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("add_question", add_question))
    dispatcher.add_handler(CommandHandler("edit_question", edit_question))
    dispatcher.add_handler(CommandHandler("delete_question", delete_question))
    dispatcher.add_handler(CommandHandler("request", request_question))

    # Message Handler for Questions
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Button Handler
    dispatcher.add_handler(CallbackQueryHandler(button))

    # Error Handler
    dispatcher.add_error_handler(error)

    # Start Polling
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    run()
    
