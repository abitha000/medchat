import time
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown  # for version 20+
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
from pymongo import MongoClient

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB setup
client = MongoClient("mongodb+srv://avianandh004:TeamHdt009@cluster0.hdvf3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['telegram_bot_db']
collection = db['qna']

# Define function to simulate typing animation
async def simulate_typing(update, context, text):
    """Simulate typing animation for the bot"""
    chat_id = update.message.chat_id
    for i in range(len(text) + 1):
        time.sleep(0.1)  # Simulating typing delay
        await context.bot.send_message(chat_id, text[:i], parse_mode=ParseMode.MARKDOWN)
        await context.bot.send_message(chat_id, text, parse_mode=ParseMode.MARKDOWN)

# Define function to start the bot
async def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message and inline buttons on /start"""
    chat_id = update.message.chat_id

    # Send start image
    start_image_url = "https://envs.sh/LaP.jpg"  # Replace with your actual image URL
    await context.bot.send_photo(chat_id, start_image_url)

    # Inline buttons
    keyboard = [
        [InlineKeyboardButton("Add me to the group", url="https://t.me/Medichat_ro_bot?startgroup=true")],
        [InlineKeyboardButton("Support", url="https://t.me/lochakpochak")],
        [InlineKeyboardButton("Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Welcome message with inline buttons
    simulate_typing(update, context, "Welcome! I'm here to answer your questions in Tamil and English. How can I assist you today?")
    await context.bot.send_message(chat_id, "Welcome! I'm here to assist you with Siddha medicine queries. You can ask in Tamil or English.", reply_markup=reply_markup)

# Command to add a question-answer pair
async def add_qna(update: Update, context: CallbackContext) -> None:
    """Allow admins to add question and answer to the database"""
    if update.message.from_user.id != YOUR_ADMIN_USER_ID:  # Replace with your admin user ID
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add_qna <question> <answer>")
        return

    question = context.args[0]
    answer = " ".join(context.args[1:])
    
    # Store in MongoDB
    collection.insert_one({"question": question, "answer": answer})
    
    simulate_typing(update, context, "The question and answer pair has been added successfully!")
    await update.message.reply_text(f"Added Q: {question}\nA: {answer}")

# Command to edit a question-answer pair
async def edit_qna(update: Update, context: CallbackContext) -> None:
    """Allow admins to edit an existing QnA"""
    if update.message.from_user.id != YOUR_ADMIN_USER_ID:
        return

    if len(context.args) < 3:
        await update.message.reply_text("Usage: /edit_qna <old_question> <new_answer>")
        return

    old_question = context.args[0]
    new_answer = " ".join(context.args[1:])
    
    # Update the answer in MongoDB
    result = collection.update_one({"question": old_question}, {"$set": {"answer": new_answer}})
    if result.modified_count > 0:
        simulate_typing(update, context, "The question has been updated successfully!")
        await update.message.reply_text(f"Updated Q: {old_question}\nNew A: {new_answer}")
    else:
        await update.message.reply_text(f"Could not find the question: {old_question}")

# Command to delete a question-answer pair
async def delete_qna(update: Update, context: CallbackContext) -> None:
    """Allow admins to delete a question-answer pair"""
    if update.message.from_user.id != YOUR_ADMIN_USER_ID:
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /delete_qna <question>")
        return

    question = context.args[0]
    
    # Delete from MongoDB
    result = collection.delete_one({"question": question})
    if result.deleted_count > 0:
        simulate_typing(update, context, "The question has been deleted successfully!")
        await update.message.reply_text(f"Deleted Q: {question}")
    else:
        await update.message.reply_text(f"Could not find the question: {question}")

# Command to get answers from the database
async def get_answer(update: Update, context: CallbackContext) -> None:
    """Handle user queries and return stored answers"""
    question = update.message.text.strip()
    
    # Look for the question in the database
    qna = collection.find_one({"question": question})
    
    if qna:
        answer = qna["answer"]
        simulate_typing(update, context, f"Answer: {answer}")
        await update.message.reply_text(answer)
    else:
        simulate_typing(update, context, "Sorry, I don't have an answer for that. You can request more information!")
        await update.message.reply_text("Sorry, I don't have an answer for that. You can request more information!")

# Command for requesting new QnA
async def request_qna(update: Update, context: CallbackContext) -> None:
    """Allow users to request a new question-answer pair"""
    user_request = update.message.text.strip()
    
    simulate_typing(update, context, "Your request has been sent to the admins.")
    await update.message.reply_text(f"Request for new Q&A received: {user_request}\nAdmins will review and respond shortly.")

# Command for help
async def help(update: Update, context: CallbackContext) -> None:
    """Send help information"""
    help_text = "Here are the commands you can use:\n\n"
    help_text += "/add_qna <question> <answer> - Add a new question-answer pair (Admin only)\n"
    help_text += "/edit_qna <old_question> <new_answer> - Edit an existing QnA (Admin only)\n"
    help_text += "/delete_qna <question> - Delete a question-answer pair (Admin only)\n"
    help_text += "/request_qna <question> - Request a new question-answer pair if not available\n"
    help_text += "Feel free to ask any question related to Siddha medicine in Tamil or English."

    simulate_typing(update, context, help_text)
    await update.message.reply_text(help_text)

# Main function to start the bot
def main():
    # Replace with your bot's token
    TOKEN = "7548088682:AAFL08f6rTFBErJhbDK3uMMC7n_ZJDe3_QM"
    
    application = Application.builder().token(TOKEN).build()

    # Handlers for commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_qna", add_qna))
    application.add_handler(CommandHandler("edit_qna", edit_qna))
    application.add_handler(CommandHandler("delete_qna", delete_qna))
    application.add_handler(CommandHandler("request_qna", request_qna))
    application.add_handler(CommandHandler("help", help))

    # Handler for user queries
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_answer))

    # Inline button handler (Help button)
    application.add_handler(CallbackQueryHandler(help, pattern='^help$'))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
