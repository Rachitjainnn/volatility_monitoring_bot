import math
import asyncio
from datetime import datetime
import pandas as pd
from logzero import logger

async def monitor_ltp(chat_id, context, smartApi, token_df, exch_seg, options_exch_seg, symbol, name, token, rounding_logic):
    previous_average = None
    total = []
    monitoring = True

    while monitoring:
        print(f"Fetch time: {datetime.now().strftime('%H:%M:%S')}")
        current_ltp = getLTP(smartApi, exch_seg,symbol,token,rounding_logic)
        temp = float(current_ltp * 100)

        ce_symbol, ce_token, pe_symbol, pe_token, strike = getCEandPe(token_df, temp,name)

        if ce_symbol and pe_symbol:
            try:
                optionCE = smartApi.ltpData(options_exch_seg, ce_symbol, ce_token)
                optionPE = smartApi.ltpData(options_exch_seg, pe_symbol, pe_token)
            except Exception as e:
                logger.error(f"Error fetching LTP data for options: {e}")
                print(f"Error fetching LTP data for options: {e}")
        
            ltp_value_CE = optionCE['data']['ltp']
            ltp_value_PE = optionPE['data']['ltp']
            total_ltp = round(ltp_value_CE + ltp_value_PE, 2)
            total.append(total_ltp)
            print(total)

            if len(total) == 3:
                current_average = (sum(total)) / 3
                print(f"Average LTP for the last 3 minutes: {current_average:.2f}")
                percentage_change = ((current_average - previous_average) / previous_average) * 100 if previous_average else None

                if previous_average is not None:
                    percentage_change = ((current_average - previous_average) / previous_average) * 100
                    print(f"Percentage change: {percentage_change:.2f}%")
                    if percentage_change >= -2:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=f"LTP of option in {name} has changed by {percentage_change:.2f}% in the last 4 minutes. Prices are {total}"
                    )
                            
                    else:
                        print("No significant change, no message sent.")


                previous_average = current_average
                total.clear()
            await asyncio.sleep(120)

def getLTP(smartApi, exch_seg,symbol,token,rounding_logic):
    try:
        response = smartApi.ltpData(exch_seg, symbol, token)
    except Exception as e:
        logger.error(f"Error fetching LTP data: {e}")
        print(f"Error fetching LTP data: {e}")
    ltp_value = response['data']['ltp']
    print(ltp_value)
    floored_ltp = rounding_logic(ltp_value)
    print(floored_ltp)
    return floored_ltp

def logic_100(ltp_value):
    if ltp_value % 100 >= 50:
        return math.ceil(ltp_value / 100.0) * 100
    else:
        return math.floor(ltp_value / 100.0) * 100

def logic_25(ltp_value):
    if ltp_value % 25 >= 12.5:
        return math.ceil(ltp_value / 25.0) * 25
    else:
        return math.floor(ltp_value / 25.0) * 25
    
def logic_50(ltp_value):
    if ltp_value % 50 >= 25:
        return math.ceil(ltp_value / 50.0) * 50
    else:
        return math.floor(ltp_value / 50.0) * 50

def getCEandPe(token_df, temp,name):
    tolerance = 0.01
    try:
        sensex_data = token_df[(token_df['name'] == name) & (abs(token_df['strike'] - temp) < tolerance)]
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        future_data = sensex_data[sensex_data['expiry'] >= current_date]
        filtered_data = future_data[future_data['symbol'].str.contains('CE|PE', regex=True)]
    except Exception as e:
        logger.error(f"Error filtering data of options: {e}")
        print(f"Error filtering data of options: {e}")

    if not filtered_data.empty:
        min_expiry_date = filtered_data['expiry'].min()
        closest_date_rows = filtered_data[filtered_data['expiry'] == min_expiry_date]
        ce_row = closest_date_rows[closest_date_rows['symbol'].str.contains('CE')]
        pe_row = closest_date_rows[closest_date_rows['symbol'].str.contains('PE')]
        ce_symbol, ce_token, pe_symbol, pe_token = ce_row['symbol'].values[0], ce_row['token'].values[0], pe_row['symbol'].values[0], pe_row['token'].values[0]
        strike = ce_row['strike'].values[0]
        return ce_symbol, ce_token, pe_symbol, pe_token, strike
    else:
        return None, None, None, None, None
    
def get_index_data(name):
    config = {
         "midcap": {
             "exch_seg": "NSE",
             "options_exch_seg": "NFO",
             "symbol": "NIFTY MID SELECT",
             "name": "MIDCPNIFTY",
             "token": 99926074,
             "rounding_logic": logic_25  
         },
         "bankex": {
             "exch_seg": "BSE",
             "options_exch_seg": "BFO",
             "symbol": "BANKEX",
            "name": "BANKEX",
             "token": 99919012,
             "rounding_logic": logic_100
         },
         "finnifty": {
            "exch_seg": "NSE",
             "options_exch_seg": "NFO",
             "symbol": "Nifty Fin Service",
             "name": "FINNIFTY",
             "token": 99926037,
             "rounding_logic": logic_50
         },
         "nifty": {
             "exch_seg": "NSE",
             "options_exch_seg": "NFO",
             "symbol": "Nifty 50",
             "name": "NIFTY",
             "token": 99926000,
             "rounding_logic": logic_50
         },
         "banknifty": {
             "exch_seg": "NSE",
             "options_exch_seg": "NFO",
             "symbol": "Nifty Bank",
             "name": "BANKNIFTY",
             "token": 99926009,
             "rounding_logic": logic_100
         },
         "sensex": {
             "exch_seg": "BSE",
             "options_exch_seg": "BFO",
             "symbol": "SENSEX",
             "name": "SENSEX",
             "token": 99919000,
             "rounding_logic": logic_100
         }
     }
    return config.get(name)
