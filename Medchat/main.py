from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Your API Token here
TOKEN = 'YOUR_API_TOKEN'

# Dictionary to store questions and answers in Tamil and English
qa_pairs = {
    "How are you?": "I am doing well!",
    "எப்படி இருக்கிறீர்கள்?": "நான் நன்றாக இருக்கிறேன்!",
    "What is your name?": "My name is Bot.",
    "உங்கள் பெயர் என்ன?": "என் பெயர் Bot."
}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome! Ask me anything in Tamil or English.')

def answer(update: Update, context: CallbackContext) -> None:
    question = update.message.text
    response = qa_pairs.get(question, "Sorry, I don't have an answer for that.")
    update.message.reply_text(response)

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, answer))

    updater.start_polling()
    updater.idle()

if name == 'main':
    main()
