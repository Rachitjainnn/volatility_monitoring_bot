# volatility_monitoring_bot
This project is a real-time market volatility monitoring bot designed to track stock indices and their straddle prices. The bot continuously fetches market data every few minutes, calculates averages, and monitors significant changes over time. If the volatility remains stable or within a set threshold, it sends alerts via Telegram.

# Features

1) Monitors multiple stock indices concurrently.
2) Calculates the average LTP over a 3-5 minute interval and compares it with the previous average.
3) Sends a Telegram message if the percentage change in LTP is greater than or equal to -2% over a 5-minute window.
4) Handles dynamic index monitoring through /start and /stop commands.
5) Supports multiple index configurations, including Nifty, BankNifty, Sensex, and more.

# Installation

Clone the repository:

git clone https://github.com/Rachitjainnn/volatility_monitoring_bot.git

cd volatility_monitoring_bot

Install the required dependencies:

pip install -r requirements.txt

Set up environment variables by creating a .env file in the project root directory:

TELEGRAM_TOKEN=your_telegram_bot_token

API_KEY=your_smart_api_key

USERNAME=your_smart_api_username

PASSWORD=your_smart_api_password

TOTP_TOKEN=your_totp_token

# Usage

To start monitoring an index, use the /start command followed by the index name. For example:

/start nifty

This will start monitoring the Nifty index.

To stop monitoring an index, use the /stop command followed by the index name. For example:

/stop nifty

This will stop monitoring the Nifty index.

# Supported Indices

The bot currently supports the following indices:

nifty (Nifty 50)

banknifty (Nifty Bank)

sensex (Sensex)

midcap (Nifty Midcap)

bankex (BSE Bankex)

finnifty (Nifty Financial Services)

Each index has its own configuration for LTP rounding and monitoring logic.

# Concurrent Monitoring

The bot is capable of monitoring multiple indices concurrently. You can start monitoring different indices at the same time, and the bot will handle them independently.

Example Usage

Start monitoring Nifty and BankNifty:

/start nifty

/start banknifty

Stop monitoring Nifty:

/stop nifty

# Logging and Error Handling

The bot uses logzero for logging errors and important events. If any error occurs during the monitoring process (such as failure to fetch data from the API), it is logged for debugging purposes.

