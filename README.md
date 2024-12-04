
# Crypto Portfolio Telegram Bot

A Telegram bot that helps users manage and track their cryptocurrency portfolios. Users can add coins, view their holdings, calculate profits/losses, and receive daily updates about their portfolio.

---

## Features

- **Add Coins**: Users can add cryptocurrency coins to their portfolio by providing the symbol, amount, and purchase price.
- **Portfolio Overview**: View a summary of all holdings, including:
  - Current value
  - Average purchase price
  - Profit/Loss calculations
- **Delete Coins**: Remove coins or specific transactions from the portfolio.
- **Daily Updates**: Automatically sends a daily update message at 7:07 AM and 7:07 PM with portfolio insights.
- **Real-Time Prices**: Fetches live cryptocurrency prices using the [CoinMarketCap API](https://coinmarketcap.com/api/).

---

## Installation

### Prerequisites

- Python 3.9 or higher
- Telegram bot token (get it via [BotFather](https://core.telegram.org/bots#botfather))
- CoinMarketCap API key (sign up [here](https://coinmarketcap.com/api/))
- SQLite3 (pre-installed with Python)

### Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/crypto-portfolio-telegram-bot.git
   cd crypto-portfolio-telegram-bot
   ```

2. Install the required Python libraries:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure your bot:

   - Create a `config.py` file in the project directory:
     ```python
     TELEGRAM_TOKEN = "your-telegram-bot-token"
     COINMARKETCAP_API_KEY = "your-coinmarketcap-api-key"
     ```

4. Run the bot:

   ```bash
   python bot.py
   ```

---

## Usage

### Commands

- **`/start`**: Start the bot and view the introduction.
- **`/portfolio`**: View your current portfolio summary.
- **`/add`**: Add a new cryptocurrency to your portfolio.
- **`/delete`**: Remove a coin or specific transaction from your portfolio.

### Example Commands

- To add a coin:  
  `BTC 0.5 30000`  
  Adds **0.5 BTC** at **$30,000** purchase price.

- To delete a coin, follow the prompts after typing `/delete`.

---

## Database Structure

### Tables

1. **`users`**
   - `user_id` (Primary Key)
   - `username`
   - `name`
   - `surname`

2. **`portfolio`**
   - `id` (Primary Key)
   - `user_id` (Foreign Key)
   - `symbol`
   - `amount`
   - `purchase_price`

---

## API Integration

### CoinMarketCap API
The bot uses the CoinMarketCap API to fetch real-time cryptocurrency prices. Ensure your API key is valid and has sufficient request limits.

---

## Scheduler

The bot uses the `schedule` module to send daily portfolio updates to all users at:
- **7:07 AM**  
- **7:07 PM**  

This runs in a separate thread to avoid interfering with the bot's main polling thread.

---

## Keyboard Layouts

The bot provides custom inline and reply keyboards for user-friendly interaction. These are implemented in the `keyboards` module.

---

## Known Issues & Future Improvements

- **Error Handling**: Improve error messages for invalid inputs.
- **Multi-Currency Support**: Add support for other fiat currencies besides USD.
- **Advanced Analytics**: Display charts and historical data for coins.

---

## Contributing

Contributions are welcome! Feel free to fork the project, create a branch, and submit a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

- Telegram: [@your-username](https://t.me/your-username)
- GitHub: [your-username](https://github.com/your-username)

---
