# Import the necessary libraries
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import os, time
from molecules import *

# Replace 'YOUR_TELEGRAM_TOKEN' with your Telegram bot token
TOKEN = '6390084746:AAEthJcuJx8X_SMrZmjvZa_7sD7pRlMc5RY'
PHOTO_DIR = 'test'
Flag = 0 # 0 - start, 1 - scanner, 2 - levels

# Create the photo directory if it doesn't exist
if not os.path.isdir(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)

def start(update, context):
    """Handler function for the /start command"""
    # Define the first layer of buttons
    keyboard = [[InlineKeyboardButton("Scan Model", callback_data='scan_model'),
                 InlineKeyboardButton("Pass Levels", callback_data='pass_levels'),
                 InlineKeyboardButton("Go to website", url='http://atomkit.tilda.ws/')]]

    # Create the first layer inline keyboard markup
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send a message to the user with the first layer inline keyboard
    update.message.reply_text('Please select an option:', reply_markup=reply_markup)
    
    # buttons = [
    #     InlineKeyboardButton(text='Hydrogen (H2)', callback_data="hydrogen"),
    #     InlineKeyboardButton(text='Oxygen (O2)', callback_data="oxygen"),
    #     InlineKeyboardButton(text='Water (H2O)', callback_data="water")
    # ]
    # reply_markup = InlineKeyboardMarkup.from_column(buttons)
    # update.message.reply_text('Choose an element:', reply_markup=reply_markup)

def pass_levels_callback(update, context):
    """Callback function for the Pass Levels button"""
    # Define the second layer of buttons
    keyboard = [[InlineKeyboardButton("Level 1", callback_data='hydrogen'),
                 InlineKeyboardButton("Level 2", callback_data='oxygen'),
                 InlineKeyboardButton("Level 3", callback_data='water')]]

    # Create the second layer inline keyboard markup
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Edit the message to replace the first layer inline keyboard with the second layer inline keyboard
    query = update.callback_query
    query.edit_message_text(text="Please select a difficulty level:", reply_markup=reply_markup)

def help_command(update, context):
    """Handler function for the /help command"""
    # Send a message to the user with a list of available commands
    message = "Here are the available commands:\n\n" \
              "/start - Start the bot\n" \
              "/help - Show this help message\n" \
              "/info - Show information about the bot\n" \
              "/restart - Restart the bot\n"
    update.message.reply_text(message)
    
def info_command(update, context):
    """Handler function for the /info command"""
    message = "Scan AtomKit bot allows to:\n\n" \
              "- Scan the built crystal model\n" \
              "- Pass the levels to learn crystals\n" \
              "- Get website link to buy the product\n"
    update.message.reply_text(message)

def button_callback(update, context):
    global Flag
    Flag = 2
    
    query = update.callback_query
    element = query.data
    query.message.reply_text(f'Please send a photo of {element}.')

    context.user_data['element'] = element
    
    print(element)
    
def scan_model_callback(update, context):
    global Flag
    Flag = 1
    
    query = update.callback_query
    query.message.reply_text('Please send a photo of a model to scan.')

def photo_callback(update, context):
    if Flag == 1:
        # Save the photo to a file
        photo_file = update.message.photo[-1].get_file()
        namely = f'{update.message.message_id}'
        filename = f'{PHOTO_DIR}/{namely}.jpg'
        photo_file.download(filename)
        
        # отправка фото в функцию scan_model() в файле molecules.py, которая сканирует модель
        res = scan_model(namely)
        print(res)
        
        elements = [
            "wrong",
            'hydrogen',
            'oxygen',
            'water',
        ]
        
        if (res == 0):
            update.message.reply_text('No such model exists in our database.\n\n' \
                '/restart to try again!')
        else:
            update.message.reply_text(f'Hooray! I guess it is {elements[res]}!\n\n' \
                '/restart to try again!')
        
        os.remove(filename)
    if Flag == 2:
        # Retrieve the element from user_data
        element = context.user_data.get('element')
        
        print(element)

        # Save the photo to a file
        photo_file = update.message.photo[-1].get_file()
        namely = f'{element}_{update.message.message_id}'
        filename = f'{PHOTO_DIR}/{namely}.jpg'
        photo_file.download(filename)
        
        # отправка фото в функцию scan_model() в файле molecules.py, которая сканирует модель
        res = scan_model(namely)
        print(res)
        
        elements = [
            "wrong",
            'hydrogen',
            'oxygen',
            'water',
        ]
        
        if (elements[res] == element):
            update.message.reply_text(f'Hooray, it is {element}, great job!\n\n' \
                '/restart to try again!')
        else:
            print(f'{elements[res]} != {element}')
            update.message.reply_text("Please, try again. Third time's a charm, they say!\n\n" \
                "/restart to try again!")
        
        os.remove(filename)

def main():
    # Create the Telegram updater and dispatcher
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler(frozenset(['start', 'restart', 'menu']), start))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('info', info_command))
    
    # Add button callback handler
    dispatcher.add_handler(CallbackQueryHandler(pass_levels_callback, pattern='pass_levels'))
    dispatcher.add_handler(CallbackQueryHandler(scan_model_callback, pattern='scan_model'))
    
    # Add button callback handler
    dispatcher.add_handler(CallbackQueryHandler(button_callback, pattern=r'hydrogen|oxygen|water'))

    # Add photo callback handler
    dispatcher.add_handler(MessageHandler(Filters.photo, photo_callback))

    # Start the bot
    updater.start_polling()

if __name__ == '__main__':
    main()