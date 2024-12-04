import sqlite3
from telebot import types
import telebot
import requests
import sqlite3
import schedule
import time
import threading



from keyboards import portfolio_keyboard, cancel_keyboard, portfolio_and_add_keyboard, add_keyboard, \
    delete_and_add_keyboard, all_keyboard
from texts import description
from config import COINMARKETCAP_API_KEY, TELEGRAM_TOKEN

conn = sqlite3.connect('portfolio.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    name TEXT,
                    surname TEXT
                 )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    symbol TEXT,
                    amount REAL,
                    purchase_price REAL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                 )''')
conn.commit()

bot = telebot.TeleBot(TELEGRAM_TOKEN)

conn = sqlite3.connect('portfolio.db', check_same_thread=False)
cursor = conn.cursor()

def get_current_price(crypto_symbol, convert_currency="USD"):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY
    }
    params = {
        "symbol": crypto_symbol,
        "convert": convert_currency
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if response.status_code == 200:
        return data["data"][crypto_symbol]["quote"][convert_currency]["price"]
    return None

def add_user_if_not_exists(user_id, username, name, surname):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (user_id, username, name, surname) VALUES (?, ?, ?, ?)",
                       (user_id, username, name, surname))
        conn.commit()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    add_button = types.InlineKeyboardButton("Add Coins", callback_data="add")
    markup.add(add_button)

    bot.send_message(
        message.chat.id,
        description,
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(commands=['portfolio'])
def show_portfolio(message):
    user_id = message.chat.id
    cursor.execute("SELECT symbol, amount, purchase_price FROM portfolio WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()

    if not rows:
        bot.reply_to(message, "Your portfolio is empty. Add coins by sending SYMBOL AMOUNT PURCHASE_PRICE.")
        return

    merged_coins = {}

    for symbol, amount, purchase_price in rows:
        if symbol in merged_coins:
            merged_coins[symbol]['amount'] += amount
            merged_coins[symbol]['total_purchase_price'] += amount * purchase_price
        else:
            merged_coins[symbol] = {'amount': amount, 'total_purchase_price': amount * purchase_price}

    for symbol, data in merged_coins.items():
        average_purchase_price = data['total_purchase_price'] / data['amount']
        merged_coins[symbol]['average_purchase_price'] = average_purchase_price

    response = "Your Portfolio:\n"
    total_value = 0
    total_profit_loss = 0
    for symbol, data in merged_coins.items():
        current_price = get_current_price(symbol)
        if current_price is None:
            bot.reply_to(message, f"Could not retrieve current price for {symbol}.")
            return

        value = current_price * data['amount']
        profit_or_loss = (current_price - data['average_purchase_price']) * data['amount']
        response += (
            f"\nCoin: {symbol}\n"
            f"Amount: {data['amount']}\n"
            f"Average Purchase Price: {data['average_purchase_price']:.2f} USD\n"
            f"Current Price: {current_price:.2f} USD\n"
            f"Holdings Value: {value:.2f} USD\n"
            f"Profit/Loss: {profit_or_loss:.2f} USD\n"

            "--------------------"
        )
        total_value += value
        total_profit_loss += profit_or_loss

    response += (
        f"\nTotal Portfolio Value: {total_value:.2f} USD\n"
        f"Total Profit/Loss: {total_profit_loss:.2f} USD"
    )
    bot.reply_to(message, response, reply_markup=delete_and_add_keyboard())


@bot.message_handler(commands=['add'])
def initiate_add_to_portfolio(message):
    bot.send_message(message.chat.id, "Please send the coin symbol, amount, and purchase price in the format: SYMBOL AMOUNT PURCHASE_PRICE (e.g., BTC 0.5 30000)", reply_markup=cancel_keyboard())
    bot.register_next_step_handler(message, add_to_portfolio)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "portfolio":
        show_portfolio(call.message)
        bot.answer_callback_query(call.id, text="Portfolio displayed")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=call.message.text)
    elif call.data == "add":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Please send the coin symbol, amount, and purchase price in the format: SYMBOL AMOUNT PURCHASE_PRICE (e.g., BTC 0.5 30000)", reply_markup=cancel_keyboard())
        bot.register_next_step_handler(call.message, add_to_portfolio)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=call.message.text)
    elif call.data == "cancel":
        print("cancel")
        bot.answer_callback_query(call.id, "Adding Coin are canceled")
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        bot.send_message(call.message.chat.id, "Adding Coin are canceled", reply_markup=all_keyboard())
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=call.message.text)
    elif call.data == "delete":
        initiate_delete(call.message)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=call.message.text)
def add_to_portfolio(message):
    if message.text.lower() == 'cancel':
        bot.reply_to(message, "Adding Coin are cancelled", reply_markup=portfolio_keyboard())
        return

    try:
        text = message.text.split()
        if len(text) != 3:
            bot.reply_to(message, "Please enter in the format: SYMBOL AMOUNT PURCHASE_PRICE (e.g., BTC 0.5 30000)")
            bot.register_next_step_handler(message, add_to_portfolio)  # Call add_to_portfolio again
            return

        symbol = text[0].upper()
        amount = float(text[1])
        purchase_price = float(text[2])
        user_id = message.from_user.id
        username = message.from_user.username
        name = message.from_user.first_name
        surname = message.from_user.last_name

        add_user_if_not_exists(user_id, username, name, surname)

        cursor.execute("INSERT INTO portfolio (user_id, symbol, amount, purchase_price) VALUES (?, ?, ?, ?)",
                       (user_id, symbol, amount, purchase_price))
        conn.commit()
        bot.reply_to(message, f"Added {amount} of {symbol} to your portfolio at {purchase_price} USD each.",
                     reply_markup=portfolio_keyboard())
    except ValueError:
        bot.reply_to(message, "Invalid input. Make sure to follow the format: SYMBOL AMOUNT PURCHASE_PRICE.", reply_markup=cancel_keyboard())

def send_symbol_list(chat_id, symbols):
    response = "Please choose which coin to delete:\n"
    for symbol in symbols:
        response += f"{symbol}\n"
    bot.send_message(chat_id, response, reply_markup=cancel_keyboard())
@bot.message_handler(commands=['delete'])
def initiate_delete(message):
    if isinstance(message, types.CallbackQuery):
        message = message.message
    user_id = message.chat.id
    cursor.execute("SELECT symbol FROM portfolio WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()

    if not rows:
        bot.send_message(message.chat.id, "You have no coins in your portfolio. Add coins using the /add command.")
        return

    symbols = set(row[0] for row in rows)

    send_symbol_list(message.chat.id, symbols)

    bot.register_next_step_handler(message, delete_coin)

def delete_coin(message):
    if message.text.lower() == 'cancel':
        bot.reply_to(message, "Deleting Coin are cancelled", reply_markup=portfolio_keyboard())
        return

    symbol = message.text.upper()
    user_id = message.from_user.id

    cursor.execute("SELECT id, symbol, amount, purchase_price FROM portfolio WHERE user_id = ? AND symbol = ?", (user_id, symbol))
    rows = cursor.fetchall()

    if not rows:
        bot.reply_to(message, "You don't have any transactions of this coin in your portfolio.", reply_markup=portfolio_keyboard())
        return

    if len(rows) == 1:
        confirm_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        confirm_keyboard.add(types.KeyboardButton("Confirm", request_location=False))
        confirm_keyboard.add(types.KeyboardButton("Cancel", request_location=False))

        bot.send_message(message.chat.id, f"Are you sure you want to delete {rows[0][2]} of {rows[0][1]} at {rows[0][3]} USD from your portfolio?", reply_markup=confirm_keyboard)
        bot.register_next_step_handler(message, confirm_delete, rows[0])
    else:
        response = "You have multiple transactions of this coin. Please choose which one to delete:\n"
        for i, row in enumerate(rows):
            response += f"{i+1}. {row[2]} of {row[1]} at {row[3]} USD\n"
        bot.send_message(message.chat.id, response, reply_markup=cancel_keyboard())
        bot.register_next_step_handler(message, select_transaction, rows)

def confirm_delete(message, row, confirm_keyboard=None):
    if message.text.lower() == 'cancel':
        bot.reply_to(message, "Deleting Coin are cancelled", reply_markup=portfolio_keyboard())
        return

    if message.text.lower() == 'confirm':
        id = row[0]
        cursor.execute("DELETE FROM portfolio WHERE id = ?", (id,))
        conn.commit()
        bot.reply_to(message, f"Deleted {row[2]} of {row[1]} at {row[3]} USD", reply_markup=portfolio_keyboard())
    else:
        bot.reply_to(message, "Invalid input. Please try again.", reply_markup=confirm_keyboard)

def delete_specific_coin(message, rows):
    coins = []
    for i, row in enumerate(rows):
        coins.append(f"{i+1}. {row[2]} of {row[1]} at {row[3]} USD")

    bot.send_message(message.chat.id, "Select the transaction you want to delete:\n" + "\n".join(coins), reply_markup=cancel_keyboard())


def select_transaction(message, rows):
    try:
        choice = int(message.text) - 1
        if choice < 0 or choice >= len(rows):
            bot.send_message(message.chat.id, "Invalid choice. Please try again.", reply_markup=cancel_keyboard())
            return
    except ValueError:
        bot.send_message(message.chat.id, "Invalid input. Please try again.", reply_markup=cancel_keyboard())
        return

    confirm_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    confirm_keyboard.add(types.KeyboardButton("Confirm", request_location=False))
    confirm_keyboard.add(types.KeyboardButton("Cancel", request_location=False))

    bot.send_message(message.chat.id, f"Are you sure you want to delete {rows[choice][2]} of {rows[choice][1]} at {rows[choice][3]} USD?", reply_markup=confirm_keyboard)
    bot.register_next_step_handler(message, lambda msg: confirm_delete(msg, rows[choice]))



def send_daily_message():
    # Get all user IDs from the database
    cursor.execute("SELECT user_id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]

    # Send a message to each user
    for user_id in user_ids:
        bot.send_message(user_id, "Good morning/Good evening! Here's your daily update.")

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def run_bot():
    bot.polling()

# Schedule the message to be sent at 7am and 7pm every day
schedule.every().day.at("07:07").do(send_daily_message)  # 7am
schedule.every().day.at("19:07").do(send_daily_message)  # 7pm

# Create threads for the scheduler and the bot
scheduler_thread = threading.Thread(target=run_scheduler)
bot_thread = threading.Thread(target=run_bot)

# Start the threads
scheduler_thread.start()
bot_thread.start()


