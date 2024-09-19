from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.request import HTTPXRequest
from monitor import monitor_ltp, get_index_data
from smart_api_utils import initialize_api, initialize_symbol_token_map
import asyncio
import os
from dotenv import load_dotenv
from logzero import logger


load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
try:
    bot = Bot(token=TELEGRAM_TOKEN)
    request = HTTPXRequest(connection_pool_size=8, connect_timeout=5.0, read_timeout=20.0)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).request(request).build()
except Exception as e:
    logger.error(f"Error initializing bot: {e}")
    print(f"Error initializing bot: {e}")

monitoring_tasks = {}  
token_df = initialize_symbol_token_map()
smartApi = initialize_api()

async def start(update: Update, context):
    try:
        global monitoring_tasks
        chat_id = update.effective_chat.id
        index_name = update.message.text.split(' ')[1]  
        await update.message.reply_text(f"Monitoring started for {index_name}!")
        index_config = get_index_data(index_name)
        if index_config:
            if index_name in monitoring_tasks:
                await update.message.reply_text(f"Monitoring for {index_name} is already running.")
            else:
                task = asyncio.create_task(monitor_ltp(
                    chat_id, 
                    context, 
                    smartApi, 
                    token_df, 
                    index_config['exch_seg'], 
                    index_config['options_exch_seg'], 
                    index_config['symbol'], 
                    index_config['name'], 
                    index_config['token'], 
                    index_config['rounding_logic']
                ))
                monitoring_tasks[index_name] = task
                print(monitoring_tasks)
        else:
            await update.message.reply_text(f"No configuration found for index: {index_name}")
    except Exception as e:
        logger.error(f"Error starting monitoring task: {e}")
        print(f"Error starting monitoring task: {e}")

async def stop(update: Update,context):
    try:
        global monitoring_tasks
        index_name = update.message.text.split(' ')[1]
        if index_name in monitoring_tasks:
            monitoring_tasks[index_name].cancel()
            del monitoring_tasks[index_name]
            await update.message.reply_text(f"Monitoring stopped for {index_name}!")
        else:
            await update.message.reply_text(f"No monitoring task found for {index_name}!")
    except Exception as e:
        logger.error(f"Error stopping monitoring task: {e}")
        print(f"Error stopping monitoring task: {e}")

try:
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('stop', stop))
    app.run_polling()

except Exception as e:
    logger.error(f"Error running bot: {e}")
    print(f"Error running bot: {e}")
