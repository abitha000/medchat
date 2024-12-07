import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import pymongo

# Setup logging to get detailed logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB Setup (replace with your MongoDB URI if using MongoDB Atlas)
client = pymongo.MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB URI
db = client["faq_db"]
faq_collection = db["faq_collection"]

# Telegram Bot Token from BotFather
TOKEN = "6819381670:AAGVK-B6hceOQqOkFcVNeIIZG-cxcI-h_XA"  # Replace with your actual bot token

# Command: /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hello! I am your FAQ bot. Ask me anything in Tamil or English.")

# Command: /help
def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "I can answer your questions in Tamil or English. "
        "To add a question and answer (admin only), use the command:\n"
        "/addfaq <question> - <answer>"
    )

# Command to add a FAQ to the database (Admin only)
def add_faq(update: Update, context: CallbackContext) -> None:
    # Check if the user is an admin (replace with your admin ID)
    admin_id = 1556830659  # Replace with your actual Telegram user ID

    if update.message.from_user.id != admin_id:
        update.message.reply_text("You are not authorized to add questions.")
        return
    
    # Ensure the command is in the format "/addfaq question - answer"
    if len(context.args) < 2:
        update.message.reply_text("Please provide the question and answer in the format: question - answer")
        return

    # Get the question and answer from the command
    question_answer = ' '.join(context.args)
    try:
        question, answer = question_answer.split(" - ", 1)
        # Insert into MongoDB (default language is English)
        faq_collection.insert_one({"question": question.lower(), "answer": answer, "language": "en"})
        update.message.reply_text(f"FAQ added successfully:\nQuestion: {question}\nAnswer: {answer}")
    except ValueError:
        update.message.reply_text("Invalid format. Please use: /addfaq <question> - <answer>")

# Handle incoming questions from users (in PM or groups)
def answer_question(update: Update, context: CallbackContext) -> None:
    user_question = update.message.text.lower()

    # Search for the question in the MongoDB
    faq = faq_collection.find_one({"question": user_question})

    if faq:
        update.message.reply_text(faq["answer"])
    else:
        update.message.reply_text("Sorry, I don't have an answer for that. Try asking something else.")

# Handle errors
def error(update: Update, context: CallbackContext) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# Sample FAQ entries to prepopulate the database
def add_sample_faqs():
    sample_faqs = [
        {"question": "what is python?", "answer": "Python is a high-level programming language.", "language": "en"},
        {"question": "இது பைதான் பற்றி என்ன?", "answer": "பைதான் ஒரு உயர் நிலை நிரலாக்க மொழி.", "language": "ta"},
        {"question": "what is your name?", "answer": "I am an FAQ bot created to answer your questions.", "language": "en"},
        {"question": "உன் பெயர் என்ன?", "answer": "நான் ஒரு கேள்வி பதில் படிகொள்.", "language": "ta"}
    ]
    
    # Insert sample FAQs into MongoDB
    for faq in sample_faqs:
        if not faq_collection.find_one({"question": faq["question"]}):
            faq_collection.insert_one(faq)

# Main function to start the bot
def main() -> None:
    add_sample_faqs()  # Add sample FAQs to the database

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add handlers for different commands and messages
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("addfaq", add_faq, pass_args=True))  # Command to add FAQ (Admin only)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, answer_question))  # Handle user questions
    
    # Handle errors
    dp.add_error_handler(error)

    # Start polling to get updates
    updater.start_polling()

    # Run the bot until you press Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
    
