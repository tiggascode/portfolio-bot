from telebot import types

def portfolio_keyboard():
    markup = types.InlineKeyboardMarkup()
    portfolio_button = types.InlineKeyboardButton("Portfolio", callback_data="portfolio")
    markup.add(portfolio_button)
    return markup

def cancel_keyboard():
    cancel_button = types.InlineKeyboardButton("Cancel", callback_data="cancel")
    markup = types.InlineKeyboardMarkup([[cancel_button]])
    return markup

def add_keyboard():
    markup = types.InlineKeyboardMarkup()
    add_button = types.InlineKeyboardButton("Add Coins", callback_data="add")
    markup.add( add_button)
    return markup

def portfolio_and_add_keyboard():
    markup = types.InlineKeyboardMarkup()
    portfolio_button = types.InlineKeyboardButton("Portfolio", callback_data="portfolio")
    add_button = types.InlineKeyboardButton("Add Coin", callback_data="add")
    markup.add(portfolio_button,add_button)
    return markup

def delete_and_add_keyboard():
    markup = types.InlineKeyboardMarkup()
    delete_button = types.InlineKeyboardButton("Delete Coin", callback_data="delete")
    add_button = types.InlineKeyboardButton("Add Coin", callback_data="add")
    markup.add(add_button,delete_button)
    return markup


def all_keyboard():
    markup = types.InlineKeyboardMarkup()
    portfolio_button = types.InlineKeyboardButton("Portfolio", callback_data="portfolio")
    add_button = types.InlineKeyboardButton("Add Coin", callback_data="add")
    delete_button = types.InlineKeyboardButton("Delete Coin", callback_data="delete")
    markup.add(portfolio_button,add_button,delete_button)
    return markup